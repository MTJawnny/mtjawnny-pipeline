# SESSION HANDOFF — 2026-08-01 (B-migration arc)

> ⚠ **SUPERSEDED — this is NOT current state.**
> The current handoff is **`docs/SESSION-HANDOFF-2026-08-02-EVE.md`**.
> Start at **`docs/SESSION-START-PROCEDURE.md`**.
> (Filename sort is misleading: `-EVE` and `-PM` sort BEFORE the
> bare-date file, so "newest by name" picks the wrong one. Follow
> this pointer, not the sort.)

Written to be read COLD. If you are picking this up with no memory of the
session, this file plus `docs/CDR-PROPOSALS.md` is everything you need. Read
this first, then CDR-PROPOSALS, then stop and wait for Captain's rulings.

**Session spend: $0.00. Cumulative arc: $90.51. Headroom vs the $140 ceiling:
$49.49.** Zero API calls were made all session; every result is local compute.

---

## 1. Where the system is, in one paragraph

`codebook.json` migrated from schema `foundry-codebook/1` to `/2` and is
verified: membership provably unchanged, independent verifier clean, 19/19
negative tests, determinism ×2. Consolidation of the run-1 SYNTH output is
NOT done and is now blocked on a set of Captain rulings, not on code. Three
external/adversarial audits ran this session; the last returned
NO-GO-AS-WRITTEN on the consolidation decisions, and its blockers are real and
verified. The failure surface has moved twice: from the schema (fixed), to the
consolidation decisions (blocked), to the ratified-vocabulary layer (the
current front).

**Live state:** `codebook.json` schema `foundry-codebook/2`, v0.7, 455 records,
7,699 members, 7,699 assertions, sha256
`61af1a1d7f81504f422feb4d35aff14aee890dcc892338e882766def93e66522`,
3,385,604 B. Lint clean, verifier CLEAN, 19/19 negative tests — all re-run at
session end.

---

## 2. What shipped this session (6 commits, all on `main`)

| commit | what |
|---|---|
| `2378b1f` | codebook /1 → /2 migration executed; new accessor module, migration writer, independent verifier + negative tests; reconcile frozen as the /1 legacy producer with two hard guards |
| `32d4a73` | re-audit hardening pass; quote gate made a hard halt; lint gaps closed; two ratified corrections applied |
| `621382b` | session 2 split into 2a CLASSIFY / 2b ENUMERATE; both directives written; pre-execution review packet |
| `cfc26fa` | session 2a executed (zero mutation); classification artifact + A12 external re-audit packet |
| `3b668bd` | standing family-completeness + name-differentiation sweep |
| `9fe0e77` | sweep pass E — ratified vocabulary vs the Comprehensive Rules |

**Key files created:** `experiments/foundry_codebook.py` (the /2 accessor
boundary: load/lint/atomic-write/backup + `add-member` CLI),
`foundry_migrate_codebook_v2.py`, `foundry_verify_migration.py` (independent
verifier + 19 negative tests), `foundry_consolidate_run1_classify.py` (session
2a), `foundry_build_reaudit_packet.py`, `foundry_family_sweep.py` (the standing
gate), `foundry_axis_merge_pointer_correction.py`.

---

## 3. The one pattern that explains most of this session

**A hand-maintained MIRROR of a ratified record gets trusted as the record.**
Every store in this system except one is a hand copy of something else, and
every one of them has now been caught drifted:

| mirror | drifted from | how it showed up |
|---|---|---|
| `validate_slug.py` vocabularies | `CODEBOOK-NAMING-GRAMMAR.md` | rejects 45% of live axes; blocked 209 ratified promotion rows on a token the grammar had ratified |
| codebook `source=DET` | the DET pattern roster | 3 ratified patterns never applied |
| 2a's existence test | "what is ratified to exist" | would have created 2 duplicate axes |
| commit prose | the artifact beside it | fabricated "0 with differing quotes" (artifact says 42) |
| `grammars.json` vocabularies | the Comprehensive Rules | 13 of 21 CR token types missing → 114 cards with no valid slug |

**The Comprehensive Rules are the only non-mirror.** They are upstream of
everything and cannot drift. That is why pass E exists and why the CR is now
load-bearing for this project — see §5.

The convergence is real, not decorative: `by-power`, `except-by-count` and
`as-long-as-<state>` are the *same ratified family* in grammar Q8.5 **and** the
three orphaned DET patterns. Three independent mirrors each lost the same
ratified thing, and no single check could have caught it because each mirror
was internally consistent.

---

## 4. Audits run this session, and what each found

**External re-audit (different model family) —
`docs/B-CONSOLIDATION-REAUDIT-LLM-HANDOFF.md`, verdict NO-GO-AS-WRITTEN.**
Three blockers: (B-01) A15 presented a false three-way choice; (B-02) many of
the 93 proposed nodes are semantically incoherent — grammar-valid slug does not
imply coherent axis; (B-03) exact counts already wrong (a 94th axis uncounted,
a redirect row omitted). Plus H-01..H-05, M-01..M-02. **Every checkable claim
was verified true.** This is the ratified A12 checkpoint and it is DISCHARGED —
but its blockers are open.

**Fable 5, proposal check.** Found the three orphaned DET patterns (the
headline finding of the session), corrected the DET-contradiction count from 6
to 29, and refuted rev 1's `except` vocabulary claim.

**Fable 5, CR ingest.** Established the CR token-type gap, the CR keyword-action
gap, and resolved two questions I had wrongly treated as open — `destruction`
vs `destroy` and the `targeted-*` slot order are both settled by the project's
own grammar.

**Fable 5, counter homograph.** Confirmed CR 122.1 (game object) vs CR 701.6
(keyword action); grammar §8 already rules on it but the validator enforces
only final-token position. Demonstrated canonicalizer corruption. Found `exile`
as a second homograph.

**Fable 5, CR-vs-slug audit feasibility.** LANDED and filed —
`docs/CR-VOCABULARY-AUDIT.md`, verdict CR-AUDIT-PARTIAL. Headline numbers
re-verified (313 tokens, 131 coinage axes, 139 validator failures, all exact).
Recommends a Homograph Form Ledger generalizing the ratified §8 pattern, at
ZERO new churn beyond CDR-09's already-ruled renames. Became CDR-13; CDR-10
folds into it.

---

## 5. The strategic shift: predestined tags

Captain's insight, measured and confirmed: *once you understand the game, a
family's siblings are derivable.* Where the CR **closes** a set (token types,
counter types, keyword actions) an axis needs no discovery — it is enumerable,
its membership is regex-derivable, and it costs $0.00.

Measured support for the 13 missing CR token types: Incubator 35, Junk 15,
Map 13, Wicked Role 11, Monster Role 8, Cursed Role 6, and 4 more at 5.
**9 clear ≥5 cards; `Gold` is already ratified at 4, so 11 of 13 qualify on the
project's own precedent.**

This inverts the economics. `create-token-clue` was a $57.63 SYNTH discovery of
a fact sitting in CR 111.10b — and it is currently absorbing both unhoused Map
tokens and 137 `investigate` cards, which is exactly why an external auditor
read it as incoherent. **SYNTH should only ever be asked about "same job,
different words"**, the actual hard problem; everything CR-enumerable belongs
to the deterministic path.

Limit, stated so it is not over-applied: this works only where the CR closes
the set. `grants-<keyword>` ranges over ~190 keyword abilities; predestining
all of them yields ~190 mostly-empty axes.

---

## 6. Decisions waiting on Captain

All in `docs/CDR-PROPOSALS.md` (rev 2) with measurements and one recommendation
each. Thirteen numbered decisions plus standing-rule proposals:

- **CDR-01** singleton node activation · **CDR-02** A15 disposition ·
  **CDR-03** R5 revalidation · **CDR-04** duplicate-quote schema (an A1
  amendment) · **CDR-05** near-duplicate axes · **CDR-06** multi-keyword grant
  routing · **CDR-07** repaired-node status
- **CDR-08** rename the 4 slot-order violators · **CDR-09** the `counter`
  homograph (~15 renames; 3 need a wording ruling) · **CDR-10** the `exile`
  homograph · **CDR-11** predestined tags (and: 7 Role values or one `role`
  umbrella?) · **CDR-12** the CR keyword-action gap
- Standing rules **NEW-01/02** and **ADD-02..08**

**Already ruled, no action needed:** ADD-01 — the three orphaned DET patterns
take the DET path in session 4 (Option A).

---

## 7. Recommended order for tomorrow

1. **Rule CDR-01 through CDR-13.** Nothing downstream can move first.
2. **Vocabulary completion before node review** (ADD-02 + CDR-11). Reviewing
   the 93 nodes against an incomplete vocabulary means reviewing some of them
   twice — Map tokens and `investigate` cards would be re-litigated.
3. **Then** re-run session 2a against the completed vocabulary, and only then
   the B-02 semantic repair.

**Do NOT** run session 2b or session 3 until the above lands. 2b expands ~18,135
rows mechanically; doing that against unrepaired decisions bakes them in.

---

## 8. Known-open technical debt

- `foundry_det_pass.load_axis_patterns()` silently demotes a ratified pattern
  with no active axis instead of halting. **This is what hid the three orphans
  for weeks.** Bug fix, no ruling needed.
- `canonicalize_label`'s flat-set slot bucketing is not position-aware, so
  `counters` buckets as EFFECT even in noun slugs (ADD-08).
- `validate_slug`'s `bare_counter_noun` check fires only in final-token
  position.
- `det-patterns-v2.json` carries 35 stale `current_codebook_n_members` values —
  snapshots presented as current values. The sweep reports them.
- 2a directive §2 item 5 ordered a cross-lane canonical-overlap computation
  that the script never performed. The value was computed by hand afterwards
  (0, benign), but the artifact cannot evidence the check.
- `experiments/out/foundry/corpus_pass_run1_classification.json` (sha256
  `7f0a83c7…`) is 2a's output and is **stale** the moment any CDR is ruled —
  2a must be re-run.

---

## 9. Standing discipline for whoever picks this up

- **Halt loudly.** Never guess, never silently skip, never best-guess a data
  shape.
- **Measure, never recall.** Every audit round this session caught an
  arithmetic error, and the sub-mode was always a hand-written number drifting
  from a correct generated artifact sitting beside it. Paste numbers from
  generator output (ADD-06).
- **Nothing model-generated is load-bearing without Captain ratification.**
  That includes every recommendation in CDR-PROPOSALS.
- **`codebook.json` is gitignored.** Backups in
  `experiments/out/foundry/backups/` are the ONLY rollback path; the backup
  law and its readback verification are not optional.
- **Run `python3 experiments/foundry_family_sweep.py --strict` before and after
  any consolidation work.** It exits 1 on blocking findings. Current blocking
  count: 5 (3 orphaned patterns — ruled, awaiting session 4; 2 family-template
  contradictions — CDR-08 territory).
- The `/loop`-style temptation to keep auditing is real. Three audits found
  progressively deeper layers; a fourth may find a fifth. **The rulings are the
  bottleneck now, not the analysis.**
