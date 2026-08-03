# DELIVERY GAP CENSUS — 2026-08-03

> ## ⚠ CORRECTED 2026-08-03 PM — the numbers below were overstated
>
> Re-measured against a fixed extractor. **Self-vs-other was 1,921; it is
> 1,558** (−18.9%). Three defects, none of them in the data:
>
> | defect | cards |
> |---|--:|
> | this table summed **per-family** counts; 51 cards sit in two families | −52 |
> | self-triggers read as other-triggers (`this Equipment`, `Sharuum`, `A-` cards) | −265 |
> | phase triggers read as event triggers (Legion Warboss's *"create a Goblin **that attacks**"*) | −45 |
>
> **End-step and begin-combat went UP**, because those 45 came home to them.
> The table below has been corrected in place; corrected figures are **bold**.
>
> Full derivation, the generator fixes, and the ruling questions that follow
> from it: **`docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md`** §2.
>
> **✅ AND THE FIVE SELF-VS-OTHER ROWS ARE NO LONGER GAPS.** Captain ratified
> the `other-` / `any-` subject prefix on 2026-08-03 (**grammar §2a**), so
> `other-permanent enters`, `another creature dies`, `another creature
> attacks`, `other creature deals combat damage to a player` and `other
> permanent leaves the battlefield` now compose onto ratified DELIVERY tokens
> (`other-etb`, `any-etb`, `other-death-trigger`, …) and have been **removed
> from the table below**. 1,558 cards unblocked. Re-run `--gaps` to see the
> current state — this document is a dated snapshot, not live state.
>
> Seventh instance of the standing lesson — §8 of the PM handoff.
>
> **And the ground-truth set did NOT catch it.** The 116 hand-verified Clue
> routings are **byte-identical before and after** all three fixes, so §"Validation
> — 116 of 116" below still holds and always did. What surfaced the defects was
> measuring a *new* dimension (SUBJECT × CONTROLLER), whose residual bucket
> exposed `this Equipment` and `at the beginning of…` clauses sitting in the
> wrong families. A ground-truth set only validates the shapes it contains —
> here, no Clue card is an Equipment, a Siege, or a legendary short-name
> self-reference. Keep the set, and keep widening it.

Corpus-wide, **zero tokens**. Produced by `experiments/foundry_shape_extractor.py`,
built this session at Captain's direction: *"language is so hardcoded we can
seemingly build a python script that can run corpus wide with no tokens spent."*

That is correct, and grammar §6b already licensed it — **SHAPE has no ambiguity
and belongs in a script; JOB is interpretive and belongs to a model.** The Clue
pass spent model tokens on the shape half and then threw the classifier away.
This tool is that classifier, made permanent and made to run on all 32,557
gate-passing cards at once.

## What it is

- Decomposes every card into ability lines, all faces, reminder text excluded (§6a).
- Names each line's DELIVERY slot **structurally** (§2: delivery is determined by
  ability STRUCTURE, never by effect words).
- **Does not hardcode the vocabulary.** The 19 ratified DELIVERY tokens are
  parsed out of §2's table at run time and the tool halts if it can't read them.
  Ratify a token and the tool picks it up; retire one and it stops emitting it.
- Reports an unnamed shape as `UNRATIFIED:<descriptor>` and **never approximates
  it onto the nearest ratified token** — the exact error the Clue pass had to undo.
- Judges nothing, writes nothing to the codebook.

## Validation — 116 of 116

Checked against the 116 hand-verified Clue routings from earlier today, which
were read card by card against full oracle text. **The tool reproduces every
one, including all four compound-trigger cards** that earn two memberships under
§1's multi-axis rule (Duggan, Raven Eagle, Obsessive Pursuit, Tivit).

It took four bug fixes to get there, and the bugs are worth recording because
they are the same class the arc keeps hitting:

| bug | cost |
|---|---|
| `\b~\b` can never match — `~` is not a word character | every self-reference invisible; 792 cards misfiled as "another permanent enters" |
| self/other decided over the whole line, not the trigger clause | "Parley — Whenever **this creature** attacks, **each** player reveals…" read as an other-creature trigger |
| compound split fired on `or` inside object phrases | "whenever you cast an instant **or** sorcery spell" lost as a cast-trigger — 1,044 cards |
| self-name check case-sensitive | "When **A**lquist Proft enters" read as another permanent |

Same lesson as §S4 (154→90→44), C4f, and Roles (85%): **the cards are
unambiguous; the encoding of them is not.** A tool does not escape that — but a
tool gets fixed once, and it can be regression-checked against a hand-verified
set, which a session's throwaway classifier cannot.

## The census — delivery shapes with NO ratified §2 token

~~63,019~~ **61,804** ability lines scanned.

| unratified delivery shape | lines | cards |
|---|--:|--:|
| `unclassified-trigger` (residual — see below) | **1,245** | **1,203** |
| **end step** | **657** | **652** — of which 333 are `delayed` triggers (CR 603.7), already buildable; **536 need vocabulary** per `END-STEP-TRIGGER-RULING-2026-08-03.md` §1 |
| Saga / Class chapter | 576 | 221 |
| ~~other-permanent enters~~ | — | **RATIFIED §2a** → `other-etb` 242 / `any-etb` 315 |
| ~~another creature dies~~ | — | **RATIFIED §2a** → `other-death-trigger` 117 / `any-death-trigger` 319 |
| ~~another creature attacks~~ | — | **RATIFIED §2a** → `other-attack-trigger` 34 / `any-attack-trigger` 311 |
| beginning of combat | **333** | **331** |
| to graveyard from anywhere | **224** | **224** |
| ~~other creature deals combat damage to a player~~ | — | **RATIFIED §2a** → `other-combat-damage-to-player` 1 / `any-` 201 |
| sacrifice trigger | 178 | 176 |
| player attacks ("whenever you attack") | 159 | 158 |
| discard trigger | 140 | 132 |
| turned face up | 116 | 116 |
| damage **received** ("is dealt N damage") | **109** | **108** |
| lifegain trigger | **98** | **96** |
| ~~other permanent leaves the battlefield~~ | — | **RATIFIED §2a** → `other-leaves-battlefield-trigger` 14 / `any-` 29 |
| is attacked | **38** | **37** |
| counter placed on the source | 37 | 37 |
| draw step | **31** | **30** |
| to graveyard from non-battlefield | 8 | 8 |

`experiments/out/foundry/delivery_gaps.json` carries the full card lists.

### What this changes

The Clue pass found `end-step-trigger`, self-vs-other, and chapter triggers by
hand, one mechanic at a time, and it cost 47 of 163 cards sent to a decision
packet. **Those same gaps block thousands of cards corpus-wide, and none of them
are about Clues.** Ruling them once unblocks all 40 CR keyword actions
simultaneously.

The two biggest are not exotic:

1. **Self vs other is unnamed across the whole corpus.** §2's rows read "when
   **~** enters", "whenever **~** attacks", "when **~** dies". Read literally —
   and §6a says read it literally — every trigger keyed on *another* permanent
   has no name. That is ~~1,921~~ **1,558 distinct cards** across five families
   (the per-family counts above sum to 1,582 and double-count 51 cards that sit
   in two). Still the single largest vocabulary gap in the codebook.

   **⚠ It is not one ruling if the question is "self vs other".** Re-measured,
   **75% of the population prints "a", not "another"** — and §6a rule 3 makes
   those different shapes, because bare "a" *includes* the source. The real
   question is a SUBJECT × CONTROLLER matrix; see
   `DELIVERY-VOCABULARY-BATCH-2026-08-03.md` §3.
2. **`end-step-trigger` does not exist.** §2 ratifies `upkeep-trigger` and not
   its mirror. **536 cards need vocabulary**, wholly regular templating.
   (`end-step-trigger` was also **killed as an axis** in `TRIAGE-BATCH-1.md`
   §1c — that kill governs the axis, not this vocabulary; batch §1.)

### The residual, stated honestly

`unclassified-trigger` is 1,203 cards the tool can see are triggered abilities
but cannot name. It is a genuine "I don't know", not a silent bucket. Sampling
shows real recurring shapes inside it — cycling (48), draw-a-card (42), first
main phase (44), becomes-tapped (30), mutates (26), unlock-a-door (26),
exploit (18), commit-a-crime (16), scry (13), end-of-combat (13). Each is
nameable; none is named yet.

## CR 701 keyword actions, ranked by what is buildable today

`--rank`, single corpus pass. "ready" = ability lines whose delivery already has
a ratified token; "blocked" = lines needing vocabulary.

**Re-measured 2026-08-03 PM** against the fixed extractor; every `ready`/`blocked`
split below has been updated, and one row (`manifest dread`) was missing.

| action | CR | cards | ready | blocked | % ready | has an axis? |
|---|---|--:|--:|--:|--:|---|
| counter | 701.6 | 4,450 | 3,113 | 2,556 | 54.9% | yes |
| create | 701.7 | 3,378 | 1,857 | 1,773 | 51.2% | yes |
| sacrifice | 701.21 | 3,114 | 2,474 | 834 | 74.8% | yes |
| exile | 701.13 | 2,711 | 1,728 | 1,457 | 54.3% | yes |
| cast | 701.5 | 2,604 | 968 | 1,808 | 34.9% | yes |
| destroy | 701.8 | 1,722 | 623 | 1,186 | 34.4% | yes |
| discard | 701.9 | 1,642 | 987 | 721 | 57.8% | yes |
| **regenerate** | 701.19 | 397 | 296 | 113 | **72.4%** | **NO AXIS** |
| **transform** | 701.27 | 281 | 219 | 122 | **64.2%** | **NO AXIS** |
| investigate | 701.16 | 135 | 73 | 67 | 52.1% | built today |
| **goad** | 701.15 | 77 | 43 | 39 | 52.4% | **NO AXIS** |
| **manifest** | 701.40 | 68 | 37 | 32 | 53.6% | **NO AXIS** |
| **venture into the dungeon** | 701.49 | 45 | 31 | 16 | **66.0%** | **NO AXIS** |
| **amass** | 701.47 | 57 | 28 | 33 | 45.9% | **NO AXIS** |
| **manifest dread** | 701.62 | 33 | 19 | 15 | 55.9% | **NO AXIS** |

`activate` (701.2, 86.5%) is correctly excluded per the CR-coverage packet — it
duplicates the `activated-` delivery marker.

**Next action to run: `regenerate` — 397 cards, 72.4% buildable, no axis.** It
outranks every action the CR-coverage packet listed, and nothing found it because
nothing was counting.

## Cost

Zero tokens per run, ~40 seconds for `--gaps`, ~4 minutes for `--rank`. It is
re-runnable after every ratification, so the census never goes stale by
recall — which is Gate 2's whole point.
