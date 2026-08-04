# D5 — THE REPLACEMENT WINDOW WAS A GUESSED NUMBER (2026-08-04)

**155 gap lines closed, and 9 lines CORRECTED off a token they never should
have held.** Fourth item of the work order. **Zero API calls.**

---

## 1. The defect, and why widening it would have been the same defect

```python
\bwould\b.{0,60}\binstead\b|\bskips?\b|\benters? with\b|\benters? tapped\b
```

`{0,60}` is a hand-chosen number with **no CR behind it**. Measured gap between
the two words on the lines it lost: **min 61 · median 89 · max 173**.

> **CR 614.1a** — *"Effects that use the word **'instead'** are replacement
> effects."*
> **CR 614.1b** — *"Effects that use the word **'skip'** are replacement
> effects."*

**The CR states no distance at all**, so the window is **removed**, not widened.
Widening it to 200 would be the same defect with a later expiry date — which is
exactly what `ed252a6`'s locked rule predicts about every hand-written stand-in
for a CR-published rule.

## 2. But 614.1a read at its WIDEST is wrong, and the measurement says so

A bare `\binstead\b` is the literal reading of 614.1a. Measured on the unrouted
population, face-aware:

| pattern | permanent-side | spell-side |
|---|--:|--:|
| `would … instead`, **unbounded** | **128** | 25 |
| bare `instead` | 148 | **298** |

The bare word sweeps in every instant whose effect merely contains it —
*"Counter target creature or enchantment spell. If that spell is countered this
way, exile it **instead** of putting it into its owner's graveyard."* **CR 614.1a
describes the EFFECT; §1 governs the DELIVERY**, and an instant's delivery is the
unmarked default no matter what its effect does. The `would` → `instead`
**template**, not the bare word, is what identifies a replacement *ability*.

**The `would` → `instead` order is kept, and it is the whole safety margin.**
`.` does not match a newline and an ability line is one line, so the unbounded
form cannot leave its ability.

**The 25 spell-side additions are not a new policy:** 98 spell-side lines were
already on `replacement` before this pass (Yawgmoth's Will, Harm's Way, Kor Dirge
are the class). Removing the window did not change which side of the
spell/permanent line this token sits on; it only stopped the cut-off from being
arbitrary.

## 3. Removing the window EXPOSED a missing guard — the more important half

The very first run moved **Bewitching Leechcraft** `static` → `replacement`:

> `Enchanted creature has "If this creature would untap during your untap step,
> remove a +1/+1 counter from it instead. If you do, untap it."`

The Aura's own delivery is `static`; the replacement belongs to the **enchanted
creature**. §2's created-ability rule (Captain-ratified 2026-08-02) is explicit —
*"an ability **granted to another permanent** … the delivery belongs to the
creating ability, never to the created one."*

**The old window had missed it by one character.** The gap is **61**. The guard
was never needed only because a guessed number happened to fall in the right
place, which is not a property anyone could have relied on.

**The replacement test now reads the line with quoted spans blanked**, the same
discipline the trigger clause already uses (*"a trigger clause must never cross
into a quoted created ability"*).

### 3a. That guard then corrected 9 lines the census had never reported

The harness **halted loudly** — *"8 line(s) LOST a ratified delivery token. That
is the one direction no census in this toolchain reports."* Every one was read.
All nine are a **granted ability inside quotes**, and all nine were wrong before:

| card | type | was | now | correct because |
|---|---|---|---|---|
| Brokers' Safeguard · Brittle Blast · Arcane Archery | Instant | `replacement` | unmarked | §1 — a spell ability's delivery is the unmarked default |
| Can't Stay Away · March Toward Perfection | Sorcery | `replacement` | unmarked | §1 |
| Summoner's Grimoire | Artifact — Equipment | `replacement` | **`static`** | the Equipment's own ability is static |
| The Eighth Doctor | Legendary Creature | `replacement` | unmarked | permanent-side; belongs on `static`, see below |
| Scion of Halaster · Master Chef | Legendary Enchantment — Background | `replacement` | unmarked | same |

**Five are now exactly right.** Summoner's Grimoire landed on `static` correctly.
**Three are UNDER-marked, not wrong** — they are permanents whose delivery is
`static`, but the static branch only matches `^(enchant|equipped creature|
enchanted )`, so *"Commander creatures you own have …"* falls through. That is
**step 2's** population, not D5's, and under-marking is reportable while a wrong
ratified token is not.

## 4. RESULT

| | |
|---|--:|
| gap lines closed | **155** |
| lines corrected OFF a wrong token | **9** |
| lines appeared / vanished | 0 / 0 |
| `replacement` | 2,152 → **2,298** |
| `static` | 12,135 → 12,136 |
| unrouted | 18,745 → **18,598** |
| `routed_lines` · `keyword_homes` | 61,900 · 144 **UNCHANGED** |

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |

## 6. What this item proves

**The harness's REGRESSION arm is the one that earned its keep.** It is the only
check in the toolchain that reports a line *losing* a token, it halted the pass,
and behind it were nine memberships the codebook should never have asserted.
Every other census in this project reports what it classified.

**A guessed constant does not just lose lines — it hides missing logic.** The
60-character window was concealing an absent created-ability guard, and no
amount of widening would have revealed it. Only deleting it did.
