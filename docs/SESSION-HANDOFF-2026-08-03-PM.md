# SESSION HANDOFF — 2026-08-03 PM

Supersedes `SESSION-HANDOFF-2026-08-03.md`. **Zero API calls all session.
Cumulative arc spend unchanged at $90.51 / $140.** Captain has **$37** in the
Claude Console, deliberately unspent — see §7.

## 0. START HERE

**`docs/SESSION-START-PROCEDURE.md`** — five gates. Gate 3 is mechanical:
`python3 experiments/foundry_slug_dossier.py <slug>` **before** calling anything
defective.

---

## 1. Live state — measured at handoff time, not recalled

| | |
|---|---|
| codebook | **545 axes** · **359 active** · **8,571 members** |
| sha256 | `48e36cc794940082357f2bc2458591e63993983d7d6a2ebcbf14652a445db4c1` |
| lint | clean |
| family sweep | **6 blocking** (unchanged four days) |
| definition drift | **35 findings** — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 |
| backups | 25 in `experiments/out/foundry/backups/` |
| commits this session | 2 (`03e557c`, `784d665`) |

`codebook.json` is gitignored; backups are the ONLY rollback path and are
**local-only**. Three mutations this session, each backed up and readback-verified.

---

## 2. READING MANIFEST

**The 2026-08-03 AM handoff shipped without one, and Gate 1 depends on it.**
That gap sent the next session to a two-day-old manifest. Fixed here; keep it.

### 2a. Mandatory before ANY foundry work

| doc | why |
|---|---|
| `CLAUDE.md` (repo root) | the contract |
| **`docs/CODEBOOK-NAMING-GRAMMAR.md`** | **read WHOLE.** All slug law. §6a/§6b/§6c/§8.4a are the newest and the most load-bearing |
| `docs/RATIFIED-RULINGS-REGISTRY.md` | generated index; grep before calling anything defective |
| this file | current state |

### 2b. New this session — read before touching delivery vocabulary

| doc | what it holds |
|---|---|
| **`docs/DELIVERY-GAP-CENSUS-2026-08-03.md`** | corpus-wide census of delivery shapes with no ratified token. **The single highest-value document on the board.** Carries a ⚠ correction in its end-step row |
| `docs/CYCLING-RULING-2026-08-03.md` | Captain-ratified; `cycling` + `typecycling` vocabulary, `dodges-counterspells` parent |
| `docs/BECOMES-TAPPED-RULING-2026-08-03.md` | CR 603.2e; becomes-tapped ≠ is-tapped ≠ enters-tapped |
| `docs/END-STEP-TRIGGER-RULING-2026-08-03.md` | corrects this session's own census 601 → 536 |
| `docs/CLUE-INSTANTIATION-2026-08-03.md` | the CR-action template; §4 is 47 cards awaiting rulings |

### 2c. Before touching the codebook
`docs/T3-AXIS-FOUNDRY-v3.md` + `docs/T3-BUILDOUT-PLAYBOOK.md` ·
`docs/DERIVED-TAG-LAYER-SPEC.md` · `docs/CORPUS-PASS-PLAN.md`

### 2d. Batch record — Captain's annotations are AUTHORITATIVE
`docs/TRIAGE-BATCH-1.md` · `-2` · `-3` · `-5` · `-7` ·
`docs/archive/TRIAGE-BATCH-4.md` · `docs/archive/TRIAGE-BATCH-6.md` ·
`docs/RATIFIED-DIRECTIVES-BATCH-4-6.md` ·
`docs/archive/CORPUS-PASS-WALK-RATIFICATION.md`

---

## 3. THE ONE THING THAT CHANGED — shape work is now a script

Captain, this session: *"language is so hard coded we can seemingly build a
python script that can run corpus wide with no tokens spent… then put back into
you to audit then parent build."*

Correct, and §6b already licensed it: **SHAPE is decidable and belongs in a
script; JOB is interpretive and belongs to a model.**

**`experiments/foundry_shape_extractor.py`** — corpus-wide DET delivery parser,
**zero tokens per run**.

- Parses its 19 ratified DELIVERY tokens **out of grammar §2 at run time**; halts
  rather than falling back to a remembered vocabulary.
- Reports unnamed shapes as `UNRATIFIED:<descriptor>`, **never** approximating
  onto the nearest ratified token.
- **Validated 116/116** against hand-verified Clue routings, compound triggers
  included.
- `--gaps` (~40s) · `--action <cr-term>` · `--rank` (~4min)

**Re-run `--gaps` after every vocabulary ratification.** The census must never be
recalled — that is Gate 2's whole point.

Four bugs it took to get there, all worth knowing: `\b~\b` can never match (`~`
is not a word character, so every self-reference was invisible); self/other read
over the whole line instead of the trigger clause; the compound split fired on
`or` inside object phrases; the self-name check was case-sensitive.

---

## 4. Built this session

| axis family | axes | members |
|---|--:|--:|
| Clue / CR 701.16 `investigate` | 10 | 120 |
| `rule:cycling` | 1 | 304 |
| `rule:typecycling` | 1 | 91 |

Clue population measured at **163 creators, not the packet's 132** — 26 cards
create Clue tokens without printing the keyword, and §6a makes the printed
instruction the claim regardless.

---

## 5. NEXT WORK ITEM — one ruling, ~2,700 cards

**The delivery-vocabulary batch.** Every ruling this session ended at the same
wall. Ratify the *vocabulary* and nodes self-instantiate per §11 — the same
argument the CR-coverage packet made for the 701 action names.

| pending token | cards |
|---|--:|
| **self-vs-other convention** — 5 trigger families at once | **1,921** |
| `end-step-trigger` + scope (your 405 / each 81 / active-player 50) | **536** |
| `becomes-tapped-trigger` | 111 |
| `cycled-trigger` · `cycles-a-card-trigger` · `cycle-or-discard-trigger` | 89 |
| `tapped-for-mana-trigger` · `becomes-untapped-trigger` | 66 |

**Self-vs-other is the big one and it is ONE ruling, not five.** §2's rows read
"when **~** enters / whenever **~** attacks / when **~** dies" — the tilde is the
source. Read literally, as §6a demands, every trigger keyed on *another*
permanent has no name. If the answer is a scope-slot convention it resolves all
five families at once.

Two open naming questions inside it, flagged not assumed:
- the active-player end step has **no §6 scope token** (`own`/`each` don't fit) —
  new scope vocabulary, not just a delivery token
- `rule:create-token-clue` keeps its bare name only until the opponent-creates
  siblings are built; §1 then makes the SCOPE slot mandatory

---

## 6. WAITING ON CAPTAIN — carried

- **Clue §4** — 47 cards: 15 blocked on missing vocabulary, 17 on self-vs-other,
  7 on another-player-creates, plus the `-conditional` question (§4f) where **I
  assumed the answer** and listed the 9 affected members
- **Provenance (`CLUE-INSTANTIATION` §5)** — seeds carry `class: human` /
  `captain-cli-*` per the role-shapes precedent, but these assignments are
  model-derived and `human` is the full-weight class. The convention may be
  mislabelling model work
- **Typecycling split** — ruled a separate axis from cycling; CR 702.29f is the
  honest counter-argument, reversible in one move spec
- Tier-4 calls 3a/3c/4 · Tier-4 call 6 / §S4 preprocessor (44 DET memberships) ·
  token-type gaps (Incubator, Army, face-down 2/2) · D13 · §S (88 Alchemy) ·
  CDR-01 · `begin-combat-trigger` + Saga-chapter vocabulary

---

## 7. On the $37

**Recommend holding it.** The documented bottleneck is **ratification
throughput, not generation** — 2026-08-02 generated more findings than could be
ruled on, and this session added ~2,700 cards' worth. Spending to generate more
findings makes it worse.

The correct home for model spend is the **PARENT/JOB layer**, which §6b says is
the genuinely interpretive half — The One Ring vs Grand Abolisher is a call no
script can make. That layer needs the shape layer under it first.

The free lever on the actual bottleneck is unchanged: **`experiments/foundry_review.html`
has been dark since 2026-07-17** and reviving it remains the highest-leverage
unstarted work.

---

## 8. The numbers to carry forward

**Three first-measurements were wrong this session, in both directions:**
investigate 132 → **163**; end-step 601 → **536**; and the extractor's own
first-run gap census was inflated by the `~` bug until ground truth caught it.

Standing lesson, now on its fifth instance (§S4 154→90→44 · C4f · Roles 85% ·
investigate · end-step): **the cards are unambiguous; the encoding of them is
not.** A tool does not exempt itself — but a tool gets fixed once and can be
regression-checked against a hand-verified set, which a session's throwaway
classifier cannot. **Always keep a hand-verified ground-truth set to check a new
tool against.**

**CR 702 has never been censused.** Cycling is the first 702 keyword *ability* to
get an axis this arc; everything prior was 701 keyword *actions*. `--rank` shows
flying (4,452), trample (1,597), vigilance (1,096), first strike (780), flash
(696), lifelink (692), equip (632) — all with no axis. **A larger uncovered
population than the 40 keyword actions**, and the natural next census.
