# CR-derived checks — proposal, 2026-08-02

Captain: *"why aren't we building checks for all game logic components and
having them fire when they are spotted? the logic is so hardcoded. You almost
don't need to think. just sort."*

Measured answer: **we should, and the gap is bigger than the checks.**
Nothing here is executed.

---

## 1. "Mass" is not Magic wording — Captain is right, and it is measurable

> *"'Mass'. What does mass mean in Magic the Gathering? Mass is not game logic
> wording. Mass should only be used for the parent layer to relate two cards
> that affect all players and just your opponents."*

**The Comprehensive Rules never print the word "mass". Zero occurrences in
10,060 lines.** It is entirely our coinage. What the CR actually prints is
`each`, `all`, `any number of`, and `target`.

So under §6b, `mass-` is a **job** word sitting in the **child** layer, which
is precisely the confusion §6b was ratified to stop. And it is not harmless —
because "mass" papers over the symmetric/one-sided distinction, three axes
currently hold both:

| axis | symmetric members | one-sided members |
|---|--:|--:|
| `mass-damage-creatures-and-players` | 11 | 3 |
| `mass-damage-opponent-creatures-only` | 1 | 8 |
| `mass-plus1-counter-distribution` | 1 | 31 |

`mass-damage-opponent-creatures-only` is the clearest: its name says
*opponent creatures only*, and Wildfire Howl ("deals 2 damage to **each
creature**") hits yours too. A symmetric board sweeper and a one-sided sweeper
are different cards for deck-building, and the word "mass" is what let them
share an axis.

**Proposed (needs ratification — this amends ratified §6 vocabulary):**

1. **Retire `mass-` from axis names.** Replace with the printed CR scope:
   `each-<class>` for symmetric, and the ownership form for one-sided
   (`opponent-<class>` / `own-<class>`). 15 active axes carry `mass-`.
2. **Keep `mass` as a ratified PARENT word** — exactly the use Captain
   describes: a job-level umbrella relating "affects everyone" to "affects just
   your opponents". That relationship is real and belongs one layer up.
3. The three conflating axes **split** on the way through, since symmetric and
   one-sided become different printed names.

This is a §12-style rename walk, not a silent fix: `mass-` is currently
ratified vocabulary in §6, so retiring it is an explicit amendment.

## 2. Why the checks were reactive, and what "all of them" would mean

C1–C4 were each built after a specific failure. That is backwards, and the CR
makes a systematic set derivable.

**CR 701 enumerates 67 keyword actions** — a closed vocabulary with exact
printed wording and a rule number each. Measured against 344 live axes:

| | |
|---|--:|
| CR 701 keyword actions | **67** |
| with a matching token in any live slug | **21** |
| **with no token in any slug** | **46** |

Corpus pressure behind the uncovered ones (gate-passing cards printing the
action):

| cards | action | cards | action |
|--:|---|--:|---|
| 1,461 | Activate | 57 | Amass |
| 271 | Regenerate | 56 | Goad |
| 240 | Transform | 52 | Exchange |
| 134 | Investigate | 46 | Venture into the Dungeon |
| 64 | Manifest | 38 | Fight / Monstrosity |

**Caveat on that 46, stated because the matcher is crude:** it tests the
action's first word against slug tokens, so morphological near-misses count as
uncovered — `rule:prevents-regeneration` exists but carries `regeneration`, not
`regenerate`. The large ones are genuinely absent, and CDR-PROPOSALS' finding
F-F independently measured the same class (fight 152, investigate 137, manifest
68, amass 57, goad 56, explore 54).

**So the finding is not "we need more checks."** It is that ~46 CR keyword
actions have no axis at all, and `investigate` alone is 134 cards currently
landing wherever the nearest sibling absorbs them — F-E already traced Map
tokens into `create-token-clue` for exactly this reason.

## 3. Proposed architecture — a generated check registry

Replace hand-written C1–C4 with a registry derived from the CR, one row per
game-logic term:

```
docs/cr-checks.json          # GENERATED, never hand-edited (G4)
  { "term": "destroy", "cr": "701.8",
    "printed_forms": ["destroy", "destroys"],
    "era_variants": [],
    "kind": "effect" }
```

Generator: `experiments/foundry_cr_checks.py`, walking CR 701 (keyword
actions), 702 (keywords — already extracted to `keyword-buckets.json`), and the
scope/targeting terms in 109/115/506/601. The drift tool then **loops the
registry** instead of carrying hand-written checks, so adding a term is data,
not code.

Two properties this buys that the current set lacks:

- **Coverage becomes measurable.** "Which CR terms does the codebook not
  model?" becomes a generated report — the §2 table above, on every run.
- **Era variants live in one place.** C4g failed today because it knew
  "defending player" and not "the player or planeswalker it's attacking". In a
  registry that is one `era_variants` field, not a bug in each check.

## 4. The honest limit — why "just sort" is not quite the whole job

Captain: *"You almost don't need to think. Just sort."* True of the cards.
**Not yet true of the checks**, and today is the evidence:

| check | wrong how | caught by |
|---|---|---|
| §S4 reminder-text | 154 → 90 → **44** across three attempts | hand-verifying samples |
| ownership | 19 → **14** ("your choice" is not ownership) | reading the hits |
| C4f mass | flagged ~50 **correct** axes (tested `each\|all`, but modern templating writes a bare plural) | reading the hits |
| C4f again | whole-card text let a second ability's "target" condemn a mass ability | reading the hits |
| C4g | knew one templating era only | reading the hits |

Every one was a hard-logic question with an objectively correct answer, where
the *cards* were unambiguous and my *encoding* was not. The pattern is
identical each time: **a check that encodes one form of a law reports every
other form as a defect.**

So the sorting is mechanical; **deciding what to sort on is where the errors
live.** That is an argument for the registry (one place to fix a form, and
era-variants as data), not against the principle. It is also the reason the
proposed autonomy split keeps *"a check disagreeing with a ratified ruling"* on
Captain's side — that is the exact signature of a check being wrong, and it has
been wrong 4 of 4 times this session.

## 5. Recommended order

1. **Rule on `mass-`** (§1). It is the smallest item and it unblocks naming for
   everything that follows.
2. **Build the CR check registry + generator** (§3). DET, zero tokens.
3. **Run the coverage report** and bring the ~46 uncovered CR actions as a
   packet — this is axis *creation*, the largest untouched surface in the
   project, and per §6b those axes are mintable per-shape without ratification
   once their names compose from ratified vocabulary.
4. Resume the n≥5 re-audit under the new checks, which will have swept most of
   it mechanically first.

## Also fixed while measuring this

`CLAUDE.md` pointed at `~/Projects/mtjawnny.github.io/mtg-comprehensive-rules.md`
for the CR. **That file does not exist** — the real path is
`.../mtjawnny.github.io/docs/mtg-comprehensive-rules.md`. A load-bearing
reference named in the contract, pointing nowhere, for an unknown length of
time. Corrected.
