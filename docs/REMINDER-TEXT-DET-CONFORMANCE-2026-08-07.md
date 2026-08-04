# REMINDER TEXT AND THE DET SCAN LAYER — 2026-08-07

**Status: RULING PROPOSED, NOT LOAD-BEARING. Blocked on Captain.**
Removing any of these memberships is a codebook mutation, so it is **logged,
not executed** — the same discipline as the five migrations in
`SESSION-HANDOFF-2026-08-07.md` §5 item 4.

---

## 1. The contradiction

Two ratified artifacts say reminder text is excluded from a card's claim.

> **Grammar §6a** (Captain-ratified 2026-08-02): *"A card's claim is its
> printed oracle text with reminder-text parentheticals **excluded** — a
> token-definition parenthetical states what the **token** does, which §2's
> created-ability rule assigns to the token, not the card."*

> **`docs/det-patterns-cr-actions-v1.json`**, the ratified CR-action batch,
> in its own note: *"**Reminder text is stripped before matching** (grammar
> §6a / tier-4 §S4): a Clue token's own reminder text is the TOKEN's ability."*

`foundry_common.det_scan_texts()` does not strip it.

```python
def det_scan_texts(card):
    canon = canonicalize_self_reference(full_oracle_text(card), card)
    return [canon] + expand_modal_bullets(canon)
```

`full_oracle_text()` returns the printed text with the parentheticals intact.
The extractor's `ability_lines()` **does** strip them (§6a), so the two halves
of the pipeline have disagreed since the DET standard was ratified.

CR 207.2 is the background: the text box *"may also contain italicized text
that has no game function"*, and CR 207.2a defines reminder text as *"italicized
text within parentheses that summarizes a rule that applies to that card."*

## 2. The measurement

Every ratified DET pattern (45, from the three batch files) against the
gate-passing corpus, comparing hits on `det_scan_texts()` output against hits
on the same output with `strip_reminder()` applied.

| | |
|---|--:|
| card→pattern assignments | 4,205 |
| **assignments that exist ONLY because of reminder text** | **167** |
| share | **3.97%** |
| axes affected | 13 |

All 167 are live memberships in `codebook.json` today.

## 3. The 167, in three classes

The classes matter because they do not all deserve the same answer.

### Class A — the token-definition case §6a names by name (122)

| axis | n | the parenthetical that did it |
|---|--:|---|
| `rule:activation-restricted-to-sorcery-speed` | 65 | `(It's an artifact with "{1}, {T}, Sacrifice this token: … Activate only as a sorcery.")` |
| `rule:restricted-purpose-mana` | 37 | `(It's an artifact with "{T}: Add {C}. This mana can't be spent to cast a nonartifact spell.")` |
| `rule:created-token-enters-tapped` | 20 | `(Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token…)` |

These are Clue, Map, Powerstone and Treasure reminder text. **The restriction
belongs to the TOKEN, not to the card that makes it** — which is the exact
sentence §6a already rules on. The card is not restricted to sorcery speed;
the Clue it creates is.

**Recommendation: remove. §6a decides these outright, no new ruling needed.**

### Class B — the reminder describes a DIFFERENT mechanic (26)

| axis | n | the parenthetical that did it |
|---|--:|---|
| `rule:innate-unblockable` | 13 | `(This creature can't be blocked, targeted, dealt damage, or enchanted by anything black.)` |
| `rule:enters-tapped` (unconditional) | 13 | `(You may cast this spell for {W} if you also return an unblocked attacker you control to hand…)` |

The first is **protection** (CR 702.16), whose reminder text happens to contain
"can't be blocked". Apostle of Purifying Light has protection from black; it is
not innately unblockable, and the axis asserts something false about it. The
second matches inside a ninjutsu-family reminder.

**These are wrong on the merits, not merely mis-sourced. Recommendation:
remove.**

### Class C — the fact is TRUE, the evidence is not admissible (19)

| axis | n |
|---|--:|
| `rule:activation-restricted-to-own-upkeep` | 11 |
| `rule:grants-trample-to-creatures-with-counters` | 2 |
| six singletons (`grants-creature-type`, `grants-extra-turn`, `grants-haste-to-created-tokens`, three `landfall-*`) | 6 |

`(Activate only during your upkeep and only once each turn.)` is a keyword's
reminder text, and for those 11 cards the restriction really does apply. The
membership states a true thing. But **evidence-quote-or-discard** requires the
quote to come from oracle text, and §6a puts reminder text outside it — so
these members are true assertions with no admissible evidence.

**This is the only part that is a genuine judgement call**, and it is Captain's:

- **C1** — remove them too. One law, no exceptions; if the fact matters, the
  pattern should find it in printed text, and the axis regains the member
  honestly on the next DET pass.
- **C2** — keep them, and widen the pattern so it matches the printed keyword
  rather than the reminder. More work, keeps 19 true memberships.

**Recommendation: C1.** It is the smaller change, it needs no new pattern
ratification, and a member that only a reminder can justify is exactly what
§6a was written to exclude. C2 can be done later per axis, on merit.

## 4. Why this was invisible

Nothing in the toolchain compares the DET layer's preprocessing against §6a.
The routing regression compares delivery tokens (a different layer entirely),
the family sweep checks pattern/axis correspondence, and definition drift's
check C4 reads scope, targeting and ownership from the *definition* — not the
*evidence*. The visibility audit's `align()` even documents the mismatch in
passing (*"`ability_lines` removes it (§6a) and `det_scan_texts` does not"*)
and compensates for it locally, without anything asking whether the mismatch
was intended.

`experiments/foundry_reminder_conformance.py` is now the standing reporter. It
exits 0 today, deliberately: **a ruling doc is not load-bearing until
ratified.** On ratification, `--strict` makes it a gate.

## 5. What ratification would take

1. Captain's word on Class C (C1 or C2). A and B need no ruling — §6a already
   decides them — but they are memberships, so they still need the mutation
   authorised.
2. `det_scan_texts()` calls `strip_reminder()`. One line; `strip_reminder` was
   extracted as a named function on 2026-08-07 for exactly this call site.
3. A declared spec in `experiments/moves/`, run through
   `foundry_membership_move.py` — member conservation, determinism ×2, atomic
   write, backup taken first. **Never hand-edit `codebook.json`.**
4. Re-run all eight gates; re-pin the audit baseline on purpose.

## 6. Boundaries stated

- **Gate-passing corpus only.** The 5,676 gated-out cards are not counted;
  `foundry_gate_audit.py` covers that population separately.
- **Ratified patterns only.** `rule:kicker-conditional-bonus-effect` carries a
  null pattern (retired in §2g) and is skipped.
- **This is about the SCAN layer, not the delivery layer.** No delivery token
  moves either way; `ability_lines()` has always stripped correctly.
- The count is assignments, not cards: a card hit by two affected patterns is
  two assignments. 167 assignments across 13 axes.
