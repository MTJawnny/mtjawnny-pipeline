# mtj-bridge v0 — architecture and state machine

## 1. Module map

| Module | Responsibility | Talks to |
|---|---|---|
| `yamlite.py` | strict YAML-subset parse/emit; halts on anything it cannot represent | — |
| `protocol.py` | typed `Task` / `Result` / `Review` / `Claim` + validation | `yamlite` |
| `policy.py` | **the safety boundary**: deterministic verdict → action | `protocol` |
| `state.py` | durable ledger reconstruction, claim/lock | `protocol` |
| `redact.py` | secret scrubbing for every outbound string | — |
| `logging_setup.py` | structured JSON logs, redacted at the handler | `redact` |
| `adapters.py` | `gh` CLI, git, `claude -p`, OpenAI Responses | `redact` |
| `fakes.py` | in-memory GitHub / Claude / OpenAI for offline tests | — |
| `worker.py` | `mtj-worker`: execute one task | all |
| `manager.py` | `mtj-manager`: review one result | all |
| `cycle.py` | `mtj-cycle`: exactly one Worker→Manager cycle | `worker`, `manager` |

Dependency direction is one-way: `policy` never imports an adapter, so the
safety layer cannot acquire a network or model dependency by accident.

## 2. State machine

Phase is **derived from GitHub comments**, never held in memory.
`state.IssueLedger.next_phase()` is the whole definition:

```
                    ┌─────────────────────────────────────────┐
                    │  no mtj-result/1 on the issue           │
                    │            WORKER_EXECUTE               │
                    └───────────────────┬─────────────────────┘
                                        │ worker posts mtj-result/1
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │  results > reviews                      │
                    │            MANAGER_REVIEW               │
                    └───────────────────┬─────────────────────┘
                                        │ manager posts mtj-review/1
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
              verdict halts automation          verdict is PASS/REPAIR
                   HALTED                            COMPLETE
              (Captain or STOP)               (or next bounded task)
```

Restarting the process at any point re-derives the same phase, because the
comments are the state. This is what makes both sessions disposable.

## 3. Worker sequence

```
1. fetch origin/<base_branch>                     ← read-only
2. measured = rev-parse origin/<base_branch>
   measured != task.base  →  STOP, and the model is NEVER invoked
3. git worktree add -b mtj/<task>-<ts> ~/.mtj-bridge/worktrees/…  <base>
4. read refoundation/*.md from the ref (git show, no checkout)
5. build prompt = bootstrap + measured state + issue contract
6. claude -p --output-format json --session-id <fresh uuid> …   ← FRESH session
7. changed = git status --porcelain -uall            ← MEASURED, not claimed
8. enforce task allow/deny globs        → violation  →  STOP, no PR
9. classify against CAPTAIN_PATHS       → hit        →  STOP, no PR, packet
10. git add -A; git commit; git push                 ← wrapper owns git
11. gh pr create --draft                             ← never merged
12. post mtj-result/1
```

Step 2 before step 6 is deliberate: a stale base costs zero model spend.
Steps 7–9 before step 10 are deliberate: a Captain-reserved change never
reaches a pull request at all.

## 4. Manager sequence

```
1. reconstruct ledger from GitHub
2. read PR diff paths (measured) — falls back to result.mutations
3. build prompt = bootstrap + task + result + diff paths
4. model.review(prompt)                    ← FRESH call, no tools, text only
5. parse_review(text)   → invalid → STOP   ← a chatty model halts, never crashes
6. policy.decide(...)                      ← deterministic, no model
7. post exactly one comment for the decision
```

The model is a **reviewer**, not an actor. It has no shell, no git, no GitHub,
and its output is data that `decide()` may ignore.

## 5. Trust model

| Component | Trusted for | NOT trusted for |
|---|---|---|
| Claude Worker | editing files inside its worktree | git, GitHub, scope enforcement |
| OpenAI Manager | judgement expressed as a verdict | authorizing anything |
| `policy.decide()` | every authorization | — |
| Captain | semantic truth, ratification, authority | — |

Both models are treated as untrusted inputs to a deterministic gate. The gate is
`policy.decide()`, it is 100% covered by `tests/test_policy.py`, and its central
invariant has a negative control (`test_negative_control_clean_case_really_does_pass`)
so the restrictive assertions cannot pass for the wrong reason.

## 6. Known limitations

1. **Repair tasks are not auto-created.** `policy.decide()` returns
   `CREATE_REPAIR_TASK` and the manager logs it, but v0 does not open the issue.
   Deliberate: issuing tasks is Manager authority, and Captain should watch the
   first few before it writes.
2. **Polling/daemon mode is not built.** `--once` semantics only.
3. **`next_task` creation is gated twice** — on the task authorizing a successor
   *and* on the review naming one. Issue #3 sets `next.authorized: NONE`, so no
   successor can be created from this task under any verdict.
4. **Path scope is only enforced when the task supplies globs.** Issue #3 supplies
   none. The bridge reports "NOT machine-checked" rather than assuming permission;
   future tasks should carry `scope.allow_paths` / `scope.deny_paths`.
5. **`CAPTAIN_PATHS` is a heuristic list, not a derived one.** It is a floor. It
   cannot know that an ordinary-looking path carries semantic weight, which is why
   the Worker-declared `decision_required` channel exists alongside it.
6. **Two deliberate YAML deviations** (`tests/test_yamlite.py::TestDeliberateDeviations`):
   - a 40-zero SHA and `007` stay **strings** (PyYAML makes the first `int 0`);
   - `2026-08-28` stays a **string** (PyYAML makes it a `datetime.date`).
   Both coercions would corrupt an identifier the state machine compares as text.
7. **The live control plane is not strict YAML.** Issue #3's body contains plain
   scalars beginning with a backtick (`` - `--once` and `--dry-run` … ``), which
   **PyYAML refuses to scan**. `yamlite` accepts them, so the bridge can read the
   traffic the Manager actually writes. Recommendation: quote such values in
   future task bodies. Verified: `yamlite` and PyYAML agree structurally on Issue
   #3 once those lines are quoted, on the Issue #1 result, and on
   `BOOTSTRAP-STATE.yaml`.
8. **Issue #1's task block predates the schema** — it has no `base_branch`, so it
   does not validate as `mtj-task/1`. Discovery logs a warning and skips it. Not
   repaired here: Issue #1 is pending Captain review and the bridge must not
   silently rewrite a durable authority record.
