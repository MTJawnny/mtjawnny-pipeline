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
0. mutating task with no allow/deny globs  →  STOP, model NEVER invoked
0b. raw validation.commands in the task body  →  STOP, model NEVER invoked
0c. mutating task with zero validation.ids   →  STOP, model NEVER invoked
0d. validation id not in VALIDATION_REGISTRY →  STOP, model NEVER invoked
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
10. claude is_error                     → FAIL       →  no validation, no commit,
                                                        no push, no PR (7-9 still
                                                        recorded as evidence)
11. run VALIDATION_REGISTRY argv for each declared id ← wrapper owns validation
    non-zero rc                         → FAIL       →  no PR
    empty evidence on a mutating task   → STOP       →  no PR
12. git add -A; git commit; git push                 ← wrapper owns git
13. gh pr create --draft                             ← never merged
14. post mtj-result/1 (including `evidence:`)
```

Discovery (step 0, before all of this) requires **both** `status: READY` in the
issue body **and** ledger phase `WORKER_EXECUTE`. `READY` is a static string that
nobody rewrites when work completes, so it stays true forever; the ledger is what
knows the task is done.

Step 2 before step 6 is deliberate: a stale base costs zero model spend.
Steps 7–9 before step 12 are deliberate: a Captain-reserved change never reaches a
pull request at all. Step 10 after 7–9 is also deliberate: a failed execution still
has to leave its changed-path and Captain classification in durable state, because a
failed run that touched reserved territory is exactly what the record must show —
only PUBLICATION is withheld, never the evidence.

## 4. Manager sequence

```
1. reconstruct ledger from GitHub
2. read PR changed paths AND the actual patch (`gh pr diff`, bounded + redacted)
   a PR whose diff cannot be fetched  →  STOP, the model is not asked to review blind
   a PR whose diff came back TRUNCATED →  STOP, before the model is invoked
3. build prompt = bootstrap + task + result + patch + wrapper-captured evidence
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
| Claude Worker | editing files inside its worktree | git, GitHub, scope enforcement, its own validation |
| OpenAI Manager | judgement expressed as a verdict | authorizing anything |
| `policy.decide()` | every authorization | — |
| Captain | semantic truth, ratification, authority | — |

Both models are treated as untrusted inputs to a deterministic gate. The gate is
`policy.decide()`, its central invariant has a negative control
(`test_negative_control_clean_case_really_does_pass`) so the restrictive assertions
cannot pass for the wrong reason, and the Worker's git prohibition is enforced by
the invocation's tool-deny rather than by its prompt.

**The task body is also an untrusted input.** It is authored by a model, so it may
not supply argv at all: it names `validation.ids`, and trusted code owns what each
one resolves to. Constraining the *executable* was not enough — `python3` belongs on
any allowlist and `python3 -c <payload>` is arbitrary execution with an allowlisted
`argv[0]`. Raw `validation.commands` in a task body is now a STOP. Without this,
"the Manager may specify acceptance criteria" reads as "the Manager may run anything
on the operator's host".

**Only a complete diff may reach an automated PASS.** A truncated patch is refused
before the Manager model is invoked, and `build_review_prompt` raises if handed one,
so the guarantee does not depend on a caller remembering the check. Instructing the
model not to PASS on a partial diff was prompt wording standing in for a structural
gate — the exact inversion of "model output may only ever make the outcome more
restrictive".

## 6. Known limitations

0. **The live Manager canary passed once** (Captain-run, 2026-08-29, recorded on
   issue #3). It has not been re-run since the OpenAI error path changed, because
   `OPENAI_API_KEY` is not present in every operator environment; the failure path
   is covered offline against the shipped adapter with its client substituted.
1. **Repair tasks are not auto-created.** `policy.decide()` returns
   `CREATE_REPAIR_TASK` and the manager logs it, but v0 does not open the issue.
   Deliberate: issuing tasks is Manager authority, and Captain should watch the
   first few before it writes.
2. **Polling/daemon mode is not built.** `--once` semantics only.
3. **`next_task` creation is gated twice** — on the task authorizing a successor
   *and* on the review naming one. Issue #3 sets `next.authorized: NONE`, so no
   successor can be created from this task under any verdict.
4. **Path scope is now mandatory for mutating tasks** (Manager review, 2026-08-29).
   A mutating task with no globs STOPs before the model is invoked. Read-only tasks
   declare `scope.kind: read_only` and are exempt. Note that Issue #3's own body
   supplies no globs, so under the repaired rule that task would not execute
   unattended — which is the correct outcome, and is why the rule changed.
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
