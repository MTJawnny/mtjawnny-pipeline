# SESSION HANDOFF — 2026-08-03 EVE

Supersedes `SESSION-HANDOFF-2026-08-03-PM.md`. **Zero API calls all session.
Cumulative arc spend unchanged at $90.51 / $140.** Captain's $37 still unspent.

**The session in one line: the delivery-vocabulary batch was taken, ratified,
and built out — §2 went from 19 tokens to 30, and one codebook migration was
executed.**

## 0. START HERE

**`docs/SESSION-START-PROCEDURE.md`** — five gates. Gate 3 is mechanical:
`python3 experiments/foundry_slug_dossier.py <slug>` **before** calling anything
defective. **It earned its keep three times this session** (§6 below).

---

## 1. Live state — measured at handoff time, not recalled

| | |
|---|---|
| codebook | **565 axes** · **359 active** · **8,740 members** |
| sha256 | `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| lint | clean |
| family sweep | **6 blocking** (unchanged all session) |
| definition drift | **35 findings** — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 |
| backups | **26** in `experiments/out/foundry/backups/` |
| commits this session | **14** (`3589d0e` … `fa877b7`) |
| §2 DELIVERY vocabulary | **30 tokens** (was 19) |

**One codebook mutation this session** — the `own` → `you-control` migration,
backed up and readback-verified before execution. Axes 545 → 565, active 359 →
359, assertions 8,571 → 8,740 (+169 rename copies, CDR-09 tombstone model).

---

## 2. READING MANIFEST

### 2a. Mandatory before ANY foundry work

| doc | why |
|---|---|
| `CLAUDE.md` (repo root) | the contract |
| **`docs/CODEBOOK-NAMING-GRAMMAR.md`** | **read WHOLE.** It changed more today than on any prior day — **§2a, §2b, §2c, §2d and §6d are all new**, plus 11 new §2 table rows |
| `docs/RATIFIED-RULINGS-REGISTRY.md` | generated index; grep before calling anything defective |
| this file | current state |

### 2b. The new law, in dependency order

| doc / section | what it holds |
|---|---|
| **grammar §2a** | `other-` / `any-` **trigger-subject prefix**. The single most load-bearing ruling of the day — it composes with every trigger token and has already absorbed two proposals that would otherwise have been minted separately |
| **grammar §2b** | a CR 702 keyword's DELIVERY is **derived**, never ruled per keyword |
| **grammar §2c** | `cycles-a-card-trigger` **is** `any-cycled-trigger` — check §2a before minting |
| **grammar §2d** | **`delayed` is a QUALIFIER, not a DELIVERY** |
| **grammar §6d** | `you-control` / `you-own`; `own` RETIRED and migrated |
| `docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md` | the decision packet; Q1–Q7 all ratified |

### 2c. This session's rulings (each carries its CR anchors)

`SAGA-CHAPTER-RULING` · `BEGIN-COMBAT-RULING` · `PLAYER-ATTACK-RULING` ·
`IS-ATTACKED-RULING` · `SACRIFICE-TRIGGER-RULING` · `DISCARD-TRIGGER-RULING`
(all `-2026-08-03.md`). Earlier same-day: `CYCLING-` · `BECOMES-TAPPED-` ·
`END-STEP-TRIGGER-` · `CLUE-INSTANTIATION-`.

**`docs/DELIVERY-GAP-CENSUS-2026-08-03.md` carries a ⚠ correction banner and is
a dated snapshot — re-run `--gaps`, never cite it as live state.**

### 2d. Before touching the codebook
`docs/T3-AXIS-FOUNDRY-v3.md` + `docs/T3-BUILDOUT-PLAYBOOK.md` ·
`docs/DERIVED-TAG-LAYER-SPEC.md` · `docs/CORPUS-PASS-PLAN.md`

### 2e. Batch record — Captain's annotations are AUTHORITATIVE
`docs/TRIAGE-BATCH-1.md` · `-2` · `-3` · `-5` · `-7` ·
`docs/archive/TRIAGE-BATCH-4.md` · `docs/archive/TRIAGE-BATCH-6.md` ·
`docs/RATIFIED-DIRECTIVES-BATCH-4-6.md`

---

## 3. RATIFIED this session — 30 §2 tokens, from 19

`activated · any-damage-to-creature · any-damage-to-player · attack-trigger ·
becomes-tapped-trigger · becomes-targeted-trigger · becomes-untapped-trigger ·
begin-combat-trigger · blocks-or-becomes-blocked-trigger · cast-trigger ·
chapter-trigger · combat-damage-to-creature · combat-damage-to-player ·
cycle-or-discard-trigger · cycled-trigger · death-trigger · end-combat-trigger ·
end-step-trigger · etb · is-attacked-trigger · kicker · landfall ·
leaves-battlefield-trigger · loyalty · player-attack-trigger · replacement ·
sacrifice-trigger · static · tapped-for-mana-trigger · upkeep-trigger`

Plus **§6 scope**: `active-player`, `you-control`, `you-own`.
Minus **`delayed`**, moved to QUALIFIER by §2d.

---

## 4. NEXT WORK ITEM

**`discard-trigger` is ruled but NOT ratified** —
`docs/DISCARD-TRIGGER-RULING-2026-08-03.md`, 96 lines / 88 cards, CR 701.9a/b,
§2a applies (83 `any-` / 12 source / 1 `other-`). Ratifying it is one grammar
row plus one `msub()` call.

Then the remaining named gaps, largest first:

| shape | cards | note |
|---|--:|---|
| `unclassified-trigger` | 1,003 | genuine residual, many shapes |
| `turned-face-up` | 121 | CR 701.34 / morph family |
| `damage-received` | 109 | "is dealt N damage" |
| **`main-phase`** | **86** | **newly visible** — was hidden inside other buckets until this session's phase fix |
| `lifegain-trigger` | 86 | |
| `to-graveyard-from-anywhere` | 60 | |
| `counter-placed` | 44 | |
| `draw-step` | 30 | |
| `phase-trigger-unnamed` | 10 | residual phase shapes |

**Two candidates logged but not ruled:** "caused to discard" (11 lines — fires
only on an opponent's effect, CR 701.9b) and the token-creation half of
Mirkwood Bats' compound.

---

## 5. MIGRATIONS LOGGED, NOT EXECUTED

Each is a codebook mutation and rides its own step under the backup law.

| what | size | source |
|---|--:|---|
| `rule:gains-life-on-other-creature-etb`, `rule:death-of-other-permanents-grows-this-creature` → §2a forms | 2 axes / 6 mem | grammar §2a |
| `rule:combat-trigger-auto-attach-equipment` → `rule:begin-combat-trigger-…` | 1 axis / 2 mem | BEGIN-COMBAT §4 |
| the three `delayed-` axes → §1 slot order (QUALIFIER last) | 3 axes / 10 mem | grammar §2d |
| §7 `own-counters` → `self-counters` | 1 axis | grammar §6d |

---

## 6. WHAT THIS SESSION PROVES — read this before trusting a number

**Gate 3 caught three killed axes that a session was about to re-mint**, each
already ruled in `TRIAGE-BATCH-1.md` §1c's "templating boilerplate" bucket:
`end-step-trigger`, `saga-chapter-progression`, and the near-miss on
`combat-trigger`. In every case the kill governed the **axis** and not the
**vocabulary**, and in two of them **the CR gave a better reason than batch-1
had** (CR 714.3c makes Saga progression a turn-based action; CR 513 is the end
step, not the 500.7 that ruling cited).

**Every single family was over-counted on first measurement.** The cause was one
bug, seven times: the event test read the whole ability line instead of the
trigger condition. **CR 113.3c** settles it — *"Triggered abilities have a
trigger condition and an effect. They are written as '[Trigger condition],
[effect]'."* All 18 event tests now read the condition.

| family | first number | measured |
|---|--:|--:|
| self-vs-other | 1,921 | **1,558** |
| sacrifice | 181 | **110** |
| end-of-combat | 111 | **17** |
| tapped-for-mana | 33 | **23** |
| discard | 120 | **96** |

**The ground-truth set did not catch any of it.** The 116 hand-verified Clue
routings were byte-identical before and after every fix. A ground-truth set
validates only the shapes it contains — no Clue card is an Equipment, a Siege,
or a legendary short-name self-reference. **Keep it, and keep widening it.**

**Ask the CR first.** Captain's *"if any of them would benefit from a CR query,
do that first"* corrected two citations I had already written down, and every
subsequent ruling found something the measurement alone would have missed.

---

## 7. On the $37 — unchanged recommendation

**Hold it.** The bottleneck was never generation. This session ratified
11 delivery tokens, 3 scope tokens and 5 grammar sections at zero token cost,
because SHAPE is decidable and belongs in a script (§6b). The correct home for
model spend is still the **PARENT/JOB layer** — every ruling this session logged
a parent candidate (`rule:sacrifice-payoff`, `rule:discard-payoff`,
`rule:precombat-setup`, `rule:attack-payoff`, `rule:punishes-attacking-you`,
`rule:saga-payoff`, `rule:end-step-payoff`, `rule:dodges-counterspells`) and
**not one has been authored**. That backlog is now the most valuable thing on
the board, and it is genuinely interpretive.

The free lever is unchanged: **`experiments/foundry_review.html` has been dark
since 2026-07-17.**
