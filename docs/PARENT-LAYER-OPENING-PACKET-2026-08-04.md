# PARENT LAYER — OPENING PACKET (2026-08-04)

Captain's instruction: *"then open the parent layer."* The handoff called this
*"the most valuable thing on the board… genuinely interpretive."*

**Zero API calls.** This packet is **raw material for a Captain ruling**, in the
`FAMILY-TREE-EVIDENCE.md` tradition — every open item is phrased as a decision,
not a recommendation to adopt. **Nothing here is load-bearing until ratified**,
per `PARENT-TREE-CANDIDATES.md`'s own discipline.

---

## 0. THE HEADLINE — 3 of the 8 logged candidates CANNOT be authored yet

Eight parents were logged across the 2026-08-03 shape rulings. Measured against
the live codebook (359 active axes), they do not have equal footing:

| logged candidate | existing child axes | union of members |
|---|--:|--:|
| `rule:sacrifice-payoff` | 16 | **132** |
| `rule:attack-payoff` | 23 | **153** |
| `rule:discard-payoff` | 7 | **56** |
| `rule:precombat-setup` | 5 | **64** |
| `rule:lifegain-payoff` (batch-1 Q2, pre-existing) | 12 | **171** |
| **`rule:punishes-attacking-you`** | **0** | **0** |
| **`rule:saga-payoff`** | **0** | **0** |
| **`rule:end-step-payoff`** | **0** | **0** |

**Why the three are empty, and it is not an oversight.** Their intended children
are `is-attacked-trigger`, `chapter-trigger` and `end-step-trigger` — all
**DELIVERY tokens ratified into grammar §2**, none of which is an **axis**. The
ratified parent decisions are explicit that this is by design: *"the bare axis
`rule:end-step-trigger` remains KILLED per TRIAGE-BATCH-1.md §1c — **delivery-only
slugs are parents, not axes**."*

So the shape pass produced **vocabulary**, not members. **A parent derived from a
delivery token has nothing to derive from** until either (a) leaf axes are minted
beneath the token, or (b) S1's *"explicit direct-member list for cards no child
captures"* is populated by hand.

**DECISION 1 for Captain.** For a delivery-only parent, do we
**(a)** author it now with a direct-member list built from the DET census
(`is-attacked-trigger` has 36 lines, `chapter-trigger` 576, `end-step-trigger`
637 — all measurable today at zero cost), or
**(b)** hold it until leaf axes exist? **(a) is cheap and available now**; (b) is
the more conservative reading of S1.

## 1. A TRAP HIT LIVE, recorded because it is the documented one

Building the candidate-children list for `rule:dodges-counterspells`, a name-match
returned 11 axes / 104 memberships — and **most of it was garbage**:

| matched | actually |
|---|---|
| `rule:plus1-counters-matter` (37) | **+1/+1 counters** — CR 122.1 NOUN |
| `rule:counters-target-spell` (13) | **countering spells** — CR 701.6 VERB |
| `rule:gives-energy-counters-immediately` (10) | energy counters — NOUN |
| `rule:spell-uncounterable` (26) | **the only real child** |

This is **exactly the CDR-09 homograph failure**, reproduced by me in one line:
sorting `counter`/`counters` by string rather than by **sense**. §8a exists
because that misfiled **17 of 33** counter axes. The real child set for this
parent is `rule:spell-uncounterable` (26) plus, arguably, hexproof/ward shapes —
which is a **different job** ("dodges interaction") and is Decision 4 below.

Recorded per Gate 4: *when your check disagrees with a ratified list, suspect the
check.* It did, and it was.

## 2. CHILD OVERLAP IS ~ZERO — and that is the RIGHT answer, not a problem

| candidate parent | children | sum of members | union | overlap |
|---|--:|--:|--:|--:|
| `sacrifice-payoff` | 16 | 134 | 132 | **2** |
| `attack-payoff` | 23 | 155 | 153 | **2** |
| `lifegain-payoff` | 12 | 172 | 171 | **1** |
| `discard-payoff` | 7 | 56 | 56 | **0** |
| `precombat-setup` | 5 | 64 | 64 | **0** |

**Do not read this as weak evidence.** CLAUDE.md states the trap outright:
**"Same-card co-occurrence is the WRONG test for substitute families."** Near-zero
overlap means the children are cleanly **disjoint** — no duplicate axes, which is
good hygiene — and it is precisely *why* a parent earns its keep. S6's whole
promise is **"Same Job, Different Words"**: the parent groups cards that share
**no** child. If the children overlapped heavily, the children would be redundant
and the fix would be a merge, not a parent.

**S7 as written cannot be satisfied by this measurement.** It calls for the
*substitute lens* — deck co-play, Tagger cross-reference, exemplar panels — which
is `experiments/measure/family_tree_evidence.py` (present, last run 2026-07-17).
**Running it per candidate is the correct next step and costs zero tokens.**

## 3. PROPOSED MERGERS — three pairs may be one parent each

§6b's rule is that a merge requires identical **printed shapes**, but a shared
**job** is exactly what a parent is for. These are the candidates where two logged
parents look like one job:

| A | B | argument | verdict sought |
|---|---|---|---|
| `punishes-attacking-you` | `damage-payoff` (Hornet Nest, Trapjaw Tyrant, logged 08-04) | both answer *"attacking me costs you"*; the printed events differ (`is-attacked-trigger` vs `is-dealt-damage-trigger`) which is why they are **not** one axis | **one parent or two?** |
| `discard-payoff` | `graveyard-fill-payoff` (logged 08-04) | both answer *"my graveyard is a resource"*; `discard-trigger`, `to-graveyard-from-library-trigger` and `mill` converge | **one parent or two?** |
| `lifegain-payoff` | `punishes-lifegain` (Kavu Predator, Punishing Fire) | **argued NOT to merge** — §6b rule 3: rewarding **your** lifegain and punishing **theirs** are *"completely different and have real in-game consequences"* | **confirm the split** |

**The third is the one I would defend hardest.** The first two are genuine
coin-flips and are Captain's call, not mine — they are the "spirit of the card"
judgment §6b reserves for a human.

## 4. NEW CANDIDATES from the 2026-08-04 pass — logged, not authored

| candidate | job | source |
|---|---|---|
| `rule:damage-payoff` | "being damaged pays me" | IS-DEALT-DAMAGE §6 |
| `rule:punishes-lifegain` | "your lifegain hurts you" | GAIN-LIFE §5 |
| `rule:graveyard-fill-payoff` | "my graveyard is a resource" | TO-GRAVEYARD §5 |
| `rule:postcombat-value` | "convert combat damage into value" (Neheb the Eternal) | MAIN-PHASE §5 |
| `rule:counters-matter` | already proposed batch-2; **now has 5 instantiated `<type>-counter-placed` nodes** feeding it | COUNTER-PLACED §2 |

**`rule:precombat-setup` and `rule:postcombat-value` are two parents, not one.**
CR 505.1a makes them different phases; §6b makes them different jobs — setup
*before* attacking versus converting *after*. The 2026-08-04 main-phase ruling
supplies both populations (63 and 10 lines).

## 5. WHAT I DID NOT DO, and why

**No parent was authored.** Authoring one is a codebook mutation, it is
interpretive by §6b's own definition, and `PARENT-TREE-CANDIDATES.md` says
nothing in it is load-bearing until the schema pass ratifies it. Captain's
standing rule — *"nothing model-generated is load-bearing without Captain
ratification"* — applies with full force to the layer whose entire content is
judgment.

**The four decisions above are the opening.** Each is a yes/no, each has its
measurement attached, and none of them needs an API call to resolve.

## 6. THE ZERO-COST NEXT STEP

Run `experiments/measure/family_tree_evidence.py` against the five populated
candidates. It already implements the substitute lens, the Tagger
cross-reference and exemplar panels, it is fixed-seed and determinism-verified,
and it is the **S7 gate those candidates have never been through**. That is the
evidence Captain asked for before ratifying a parent, and it costs nothing but
CPU.
