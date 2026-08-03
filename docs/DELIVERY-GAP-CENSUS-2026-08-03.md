# DELIVERY GAP CENSUS — 2026-08-03

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

63,019 ability lines scanned.

| unratified delivery shape | lines | cards |
|---|--:|--:|
| `unclassified-trigger` (residual — see below) | 1,243 | 1,201 |
| **other-permanent enters** | 799 | **792** |
| **end step** | 606 | **601** |
| Saga / Class chapter | 576 | 221 |
| **another creature dies** | 451 | **448** |
| **another creature attacks** | 416 | **413** |
| beginning of combat | 279 | 277 |
| to graveyard from anywhere | 233 | 233 |
| other creature deals combat damage to a player | 221 | 220 |
| sacrifice trigger | 178 | 176 |
| player attacks ("whenever you attack") | 159 | 158 |
| discard trigger | 140 | 132 |
| turned face up | 116 | 116 |
| damage **received** ("is dealt N damage") | 107 | 106 |
| lifegain trigger | 104 | 102 |
| other permanent leaves the battlefield | 48 | 48 |
| is attacked | 43 | 42 |
| counter placed on the source | 37 | 37 |
| draw step | 28 | 27 |
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
   has no name. That is **792 + 448 + 413 + 220 + 48 = 1,921 cards** across five
   families. This is the single largest vocabulary gap in the codebook and it is
   one ruling, not five, if the answer is a scope-slot convention.
2. **`end-step-trigger` does not exist.** §2 ratifies `upkeep-trigger` and not
   its mirror. 601 cards, wholly regular templating.

### The residual, stated honestly

`unclassified-trigger` is 1,201 cards the tool can see are triggered abilities
but cannot name. It is a genuine "I don't know", not a silent bucket. Sampling
shows real recurring shapes inside it — cycling (48), draw-a-card (42), first
main phase (44), becomes-tapped (30), mutates (26), unlock-a-door (26),
exploit (18), commit-a-crime (16), scry (13), end-of-combat (13). Each is
nameable; none is named yet.

## CR 701 keyword actions, ranked by what is buildable today

`--rank`, single corpus pass. "ready" = ability lines whose delivery already has
a ratified token; "blocked" = lines needing vocabulary.

| action | CR | cards | ready | blocked | % ready | has an axis? |
|---|---|--:|--:|--:|--:|---|
| counter | 701.6 | 4,450 | 3,105 | 2,563 | 54.8% | yes |
| create | 701.7 | 3,378 | 1,801 | 1,827 | 49.6% | yes |
| sacrifice | 701.21 | 3,114 | 2,466 | 841 | 74.6% | yes |
| exile | 701.13 | 2,711 | 1,725 | 1,460 | 54.2% | yes |
| cast | 701.5 | 2,604 | 999 | 1,777 | 36.0% | yes |
| destroy | 701.8 | 1,722 | 616 | 1,193 | 34.1% | yes |
| discard | 701.9 | 1,642 | 974 | 734 | 57.0% | yes |
| **regenerate** | 701.19 | 397 | 296 | 113 | **72.4%** | **NO AXIS** |
| **transform** | 701.27 | 281 | 220 | 121 | **64.5%** | **NO AXIS** |
| investigate | 701.16 | 135 | 73 | 67 | 52.1% | built today |
| **goad** | 701.15 | 77 | 43 | 39 | 52.4% | **NO AXIS** |
| **manifest** | 701.40 | 68 | 33 | 36 | 47.8% | **NO AXIS** |
| **amass** | 701.47 | 57 | 28 | 33 | 45.9% | **NO AXIS** |
| **venture into the dungeon** | 701.49 | 45 | 24 | 23 | 51.1% | **NO AXIS** |

`activate` (701.2, 86.5%) is correctly excluded per the CR-coverage packet — it
duplicates the `activated-` delivery marker.

**Next action to run: `regenerate` — 397 cards, 72.4% buildable, no axis.** It
outranks every action the CR-coverage packet listed, and nothing found it because
nothing was counting.

## Cost

Zero tokens per run, ~40 seconds for `--gaps`, ~4 minutes for `--rank`. It is
re-runnable after every ratification, so the census never goes stale by
recall — which is Gate 2's whole point.
