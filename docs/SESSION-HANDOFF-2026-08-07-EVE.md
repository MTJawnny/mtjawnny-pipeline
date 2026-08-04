# SESSION HANDOFF — 2026-08-07 EVE

Supersedes `SESSION-HANDOFF-2026-08-07.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Nine commits, `ff17cbf` .. `fb5051a`.

**The session in one line: an audit of the AUDITS. Nine structural escapes were
named, measured and closed — and closing them turned up two live data
corruptions, one unrouted keyword family, and 167 memberships that contradict a
ratified law. Gate 2 goes from six commands to eight, and both older audits now
fail on DEGRADATION instead of only on breakage.**

**NEXT SESSION'S JOB IS STILL THE TRAP SWEEP. It is §4 of the superseded
handoff and it is now §5 here. Start there.**

---

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — five gates, **Gate 2 is now EIGHT
commands.** If no task was given, §5's NEXT WORK ITEM is your instruction.
Only two things need Captain's explicit word: **ratifying new vocabulary** and
**mutating the codebook**.

---

## 1. WHAT PROMPTED THIS

Captain asked what could still escape the audit suite. Nine escapes were
found; all nine are closed or reported. The finding that generalises:

> **Every mechanism in this repo asked "did it CHANGE" or "did it get LOST".
> Not one asked "is it RIGHT".** Conservation, invariance and the routing diff
> are all relative or structural. A token wrong since before the first snapshot
> was permanently invisible, and `diff --strict` scored `None → ratified` as
> pure profit.

---

## 2. GATE 2 — now EIGHT commands

```
python3 experiments/foundry_codebook.py lint
python3 experiments/foundry_family_sweep.py --strict
python3 experiments/foundry_definition_drift.py
python3 experiments/foundry_ruling_registry.py
python3 experiments/foundry_punctuation_audit.py      # conservation + baseline
python3 experiments/foundry_visibility_audit.py       # visibility + baseline
python3 experiments/foundry_ground_truth.py           # NEW — is the token RIGHT
python3 experiments/foundry_gate_audit.py             # NEW — what Gate #0 hides
```

Plus one **reporter that is deliberately not a gate**:

```
python3 experiments/foundry_reminder_conformance.py   # §6a, exits 0 until ratified
```

**The two audits now compare against a pinned baseline**
(`experiments/out/foundry/audit-baseline.json`, 65 metrics). Movement in the
worse direction is fatal; movement in the better direction is reported; either
is accepted only by an explicit `--update-baseline`. It is a RATCHET, not a
tolerance — a percentage band would be exactly the tuning knob the engine rules
forbid.

---

## 3. LIVE STATE — measured at handoff, not recalled

| | |
|---|---|
| codebook | **565 axes · 8,740 members — UNCHANGED, no mutation this session** |
| lint · definition drift · ruling registry | clean · clean · clean |
| family sweep | **6 blocking** (the same 6) |
| conservation audit | **0 violations** / 61,383 lines · 43 metrics pinned |
| visibility audit | **0 dropped · 0 unscanned · 33 uncontexted · 0 face spans** · 22 metrics pinned |
| **ground truth** | **488 graded, 488 pass, 0 unanchored, 0 mismatch** |
| gate audit | 5,676 out · 114 CR members attested only outside · **0 crashes** |
| reminder conformance | **167 memberships** (reported, blocked on Captain) |
| invariance | **0** (was **1** at the previous handoff, unreported) |
| deliveries emitted | 61,952 |
| **unrouted** | **15,993 rows / 15,902 lines** (was 16,082 / 15,991) |
| `spell-or-static` | **14,898** — and see §4, it is not 14,898 gaps |
| DET expansions | **2,104** (was 1,930) |
| keyword homes | 150 (unchanged) |
| working tree | clean |

---

## 4. THE NUMBER THAT WAS WRONG ALL ARC

`--gaps` excludes `spell-or-static` by construction — correctly, it is not
missing vocabulary — but excluded had become **unreportable**, and 93.7% of all
unrouted lines live there. CR 113.3a splits it with no new vocabulary at all:

| | | |
|---|--:|--:|
| undecidable — card HAS an instant/sorcery face (grammar §1 default) | 10,413 | **69.9%** |
| CR 113.3a closes: decidably STATIC | 4,485 | 30.1% |

**So "unrouted" has been overstating the remaining work by roughly 3×.** Most
of it is the unmarked default for a spell ability, which is correct and
finished. The decidably-static 4,485 is the real queue, and its top shapes are
exactly what §5 already names: `creatures you control` 167 · `other creatures
you` 72 · `each creature you` 59.

---

## 5. NEXT WORK ITEM — the TRAP SWEEP, unchanged. Proceeds WITHOUT asking.

Carried forward verbatim from the superseded handoff §4. Two AUDIT-5 findings
remain open (`\b` after `as ` in the CR 614.1c branch, 25 lines; `\benters?\b`
in the etb trigger test, 43 lines), **and the sweep is the job, not those two
lines**: grep every branch for `\b` adjacent to `~`, and for singular/plural or
inflected tests — widened to separators and symbol variants, not just verbs.

**One thing to carry into it that is new:** the ground-truth fixture now exists,
so run it after every sweep step. It is the only check that would notice the
sweep handing out a *wrong* ratified token, and improving recall is exactly
when that happens.

Then, in order: CR 706.3b die-row ROUTING · the anthem group · `escapes with`.

---

## 6. WHAT CHANGED — nine commits

**`ff17cbf` conservation reaches the reminder strip (E1/E2/E2b).** Test A
measured from `ability_lines()` OUTPUT, and `ability_lines()` IS the reminder
strip plus a split — so 19.2% of every oracle character was mutated upstream of
the boundary. A0 closes it against CR 207.2a. **And it found a live corruption:**
CR 201.5c's shortened-name heuristic was ungated by supertype, erasing CR 205
TYPE words from oracle text on 26 non-legendary cards — `Destroy the Evidence`
scanned as `~ target land`. All 118 legendary hits were correct. This also
fixed the one invariance failure standing at HEAD.

**`f93fbed` ground truth (E3).** 534 Captain-ratified `class: human` seeds
already existed in `experiments/moves/*.json` — 4.4× the 116 Clue routings I
went looking for. Expected values are derived at run time from the axis slug
against §2 / CR 702; nothing is hand-written. **Found 91 unrouted
`rule:typecycling` lines on its first run** — CR 702.29f, *"typecycling
abilities ARE cycling abilities"*, form derived from CR 205 like landwalk. 88
lines moved, all correct.

**`b40a3a5` gate audit (E4).** All eight checks share one gate, so it is one
blind spot, not eight. 114 CR 205 members attested only outside it — including
the same six card types that caused the original self-reference defect. All
5,676 gated-out cards parse: the gate is a POPULATION decision, not a
capability limit.

**`191c9b3` striations (E5).** The visibility audit covered 5 of 11 census
constructs, including *not* the leveler it was built to protect. CR 711.2 and
716.2 put the marker on its own line with the abilities BELOW it — 174 content
lines, **none joined**. Both rules print the same sentence the CR 706.3b join
was built on. 0 lines moved, 0 memberships changed.

**`7d235f1` baseline + floor (E6/E7).** Degradation exited 0 on both audits.
65 metrics pinned as a ratchet. The recall table now prints z and FLOOR: `digit`
reads ratio 1.04 and carries z = 2.9, and `comma` needs **+4,169** broken lines
before the ratio flag says anything.

**`27bbf43` read inside `spell-or-static` (E8).** §4 above.

**`11b7498` face isolation (E9).** The joins that reveal an option could also
fuse a DFC's two faces (CR 712.8 / 709.3b). Zero today, because proximity
scoping is `[^\n]*` — and nothing asserted it, while this session added two
joins that build strings across lines.

**`7ea092c` labels (E10).** CLAUDE.md's trap quoted 237 uncontexted; live is
33, stale one commit after it was written. The snapshot's "unrouted" counts
ROWS and the audit's counts LINES; both now say which. **11 new traps.**

**`5d66813` §6a conformance (E1b).** See §7.

**`fb5051a` registry regenerate.** It was stale before this session started —
nothing in Gate 2 notices a generated artifact drifting from its generator.

---

## 7. BLOCKED ON CAPTAIN — one NEW item, plus the standing sheet

### NEW — `docs/REMINDER-TEXT-DET-CONFORMANCE-2026-08-07.md`

Grammar §6a and the ratified CR-action batch's **own note** both say reminder
text is stripped before DET matching. `det_scan_texts()` does not strip it.
**167 live memberships (3.97% of all DET assignments, 13 axes) exist only
because a pattern matched inside a parenthetical.**

| class | n | verdict |
|---|--:|---|
| **A** token-definition reminders (Clue/Map/Powerstone/Treasure) | 122 | §6a decides outright — remove |
| **B** the reminder describes a DIFFERENT mechanic — `innate-unblockable` collected 13 cards off **protection** reminder text | 26 | wrong on the merits — remove |
| **C** the fact is TRUE, the evidence is not admissible | 19 | **Captain's call.** Recommend C1 (remove; one law, no exceptions) over C2 (keep, widen the patterns) |

Logged, not executed — it is a codebook mutation. Ratification takes four
steps, listed in §5 of the ruling doc.

### Standing sheet — carried forward unchanged

All eight items from the superseded handoff §5 remain open: CR refresh ·
`main-phase-unqualified` (n=1) · `to-graveyard-zone-unstated` (n=11) · five
logged migrations · `rule:postcombat-main-phase-trigger` under-populated ·
§2a prefix-stripping anchor · `start your engines!` / the 43 homeless keywords.

---

## 8. WHAT THIS SESSION PROVES

**An audit's boundary is upstream of something.** Ask what runs BEFORE the
first thing your audit reads. The largest text mutation in the pipeline sat one
stage outside the conservation boundary for its whole life.

**Conservation is structural and cannot see content.** Interleave conservation
passes a greedy `\(.*\)` that eats real rules text between two parentheticals.
Only the span's own CR definition catches it. Negative-control every guard
against a deliberately broken version of the thing it guards — that is how four
of this session's guards were confirmed to work at all.

**Zero movement was the correct result three times, and each was still a real
fix.** The whitespace repair (156 lines, 0 tokens moved), the striation join
(174 joins, 0 lines moved), face isolation (0 spans found). A fix whose effect
is invisible to the routing layer is not a no-op; it is a hazard removed before
it fired.

**A PROBE DEFECT IS THE DEFAULT OUTCOME, NOT THE EXCEPTION.** Six more this
session on top of the previous four, and every single one was the same mistake
in a different costume — **asking the question again instead of consuming what
the classifier already emitted.** `parse_deliveries` instead of
`deliveries_for_lines`; `kw in [(tok, desc), …]` against tuples, which scored a
correct 304-member family 0/304; grading a family axis by string equality
against a printed variant; splitting type lines on whitespace, which called 28
multiword and curly-apostrophe CR subtypes unattested; a band boundary that
stopped at any `roll … dice` line, which was Barbarian Class's own level-2
ability; and `_direction` reading only a dotted key's leaf, so every nested
pinned metric silently resolved to neutral and a negative control passed.

Ten probe defects across two sessions is not bad luck. **Budget for it: write
the probe, then run the system map's question on the probe.**
