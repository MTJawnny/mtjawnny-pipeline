# C4 — decision sheet

**7 calls.** 93 memberships across 22 active axes, from the first run of the
C4 check built for your ruling that *"the printed word is the claim"*
(grammar §6a).

Answer `all defaults`, or `all defaults except 3 — do X`.
Write `VERDICT: …` under a call; annotations here are authoritative.
Full per-axis evidence: `experiments/out/foundry/definition_drift_report.json`
and the generated `docs/DEFINITION-DRIFT-AUDIT-2026-08-02.md`.

**Everything below was hand-verified against printed oracle text before being
written here.** Two buckets looked like check artifacts from truncated quotes
and were checked card-by-card; both were real. One earlier false-positive class
(a bare `your` test matching "your choice") was found and removed before the
check shipped.

---

## The shape of it

93 memberships, but only **six failure shapes**, and one of them is 36 of the 93:

| shape | memberships | what the card actually prints |
|---|--:|---|
| affects **itself**, slug says target/other | 36 | "**this creature** gains double strike" |
| **targets**, but slug claims "other" | 25 | "**target** creature" where the slug says *another* |
| **ownership**-restricted on an `any-*` axis | 14 | "target creature **you control**" |
| **Aura**, affects what it enchants | 6 | "tap **enchanted** creature" — never targets |
| **choice**, not target | 6 | "a source of **your choice**", "**a** creature you control" |
| **mass**, not target | 6 | "each opponent", "for each creature you control" |

The choice-vs-target row is the subtlest and the one I'd have missed without
your ruling: CR treats *choosing* and *targeting* as different operations, so
Kayla's Command ("Put a +1/+1 counter on **a** creature you control") does not
belong on a `-target` axis even though it plainly affects one creature.

---

## 1. Drop the false `other` from 4 slug names

The slug claims the source is excluded; **all or most members print plain
"target"**, so they can affect themselves. The name is the false claim, not the
members.

| axis | flagged | rename to |
|---|---|---|
| `activated-animate-other-artifact` | **2 of 2** | `activated-animate-target-artifact` |
| `activated-plus1-counter-transfer-to-other-creature` | **2 of 2** | `activated-plus1-counter-transfer-to-target-creature` |
| `etb-bounce-other-creature` | 6 of 9 | `etb-bounce-target-creature` |
| `etb-plus1-counter-on-other-creature` | 15 of 42 target-but-not-other | `etb-plus1-counter-on-target-creature` |

Note the second one was renamed yesterday under tier-2 D1 — that fixed the
*direction* (`from-` → `to-`) and left the `-other-` claim, which Spike Hatcher
and Spike Rogue both contradict ("Put a +1/+1 counter on **target creature**").

**DEFAULT: yes, rename all four.**

VERDICT:

---

## 2. Split out 36 members that affect **themselves**

The largest class. These sit on `-target` / `-other` axes while printing "this
creature gains…" — they never touch another permanent.

| from | flagged | to |
|---|--:|---|
| `grants-double-strike-target` | 21 | **new** `rule:grants-self-double-strike` |
| `etb-plus1-counter-on-other-creature` | 12 | **new** `rule:etb-self-plus1-counter` |
| `etb-tap-and-stun-target` | 3 | **new** `rule:etb-self-tapped-with-stun-counters` |

`rule:etb-self-plus1-counter` slots into the existing self-counter family
(`self-plus1-counter-growth`, `attack-trigger-self-plus1-counter-growth`,
`draw-trigger-self-plus1-counter-growth`, …), so it is family extension rather
than new territory.

**DEFAULT: yes — 3 new axes, 36 moves.**

VERDICT:

---

## 3. Split out 6 Aura members that affect what they **enchant**

An Aura acting on "enchanted creature/land" does not target — the attachment
already fixed the object. Coherent class across three axes.

| from | member(s) |
|---|---|
| `activated-tap-target-creature` | Burden of Guilt, Castaway's Despair, Weakstone's Subjugation |
| `activated-destroy-target-land` | Pooling Venom, Steam Vines |
| `untaps-target-land` | Wellspring |

Precedent for the naming exists: `rule:aura-locks-enchanted-creature-tapped`.

**DEFAULT: three new siblings —** `rule:aura-taps-enchanted-permanent`,
`rule:aura-destroys-enchanted-land`, `rule:aura-untaps-enchanted-land`.
Alternative: one wide `rule:aura-affects-enchanted-permanent` and let the
effect be a facet. I recommend the three — your ruling says the effect verb is
also a printed claim.

VERDICT:

---

## 4. Split out 6 members where the card **chooses** rather than targets

CR distinguishes them; a "choice" cannot be responded to by changing targets,
and hexproof/ward do not stop it.

| from | member(s) | prints |
|---|---|---|
| `prevent-fixed-damage-any-target` | Kithkin Armor, Story Circle | "a source of **your choice**" |
| `prevent-fixed-damage-any-target` | Urza's Armor, **Opal-Eye** | "if a source would deal damage **to you**" / "to Opal-Eye" |
| `grants-double-strike-target` | Aradesh the Founder, Reyav Master Smith | "**a** creature you control" |

**Opal-Eye is my error from earlier today** — I moved it here under tier-4
call 1, before your ruling existed. It prevents damage to itself and targets
nothing. It belongs with the self-class in call 2 or on its own; flagging it
rather than quietly re-moving it.

**DEFAULT: yes — new `rule:prevent-fixed-damage-to-chosen-source` for the
choice pair, self-prevention members to a self axis, Opal-Eye corrected.**

VERDICT:

---

## 5. Split out 14 ownership-restricted members (your 3a ruling, generalised)

`any-*` scope asserts the axis can affect an opponent's permanents. These
members print "you control" and cannot.

| axis | flagged | n |
|---|--:|--:|
| `copy-creature-token` | 7 | 21 |
| `attack-trigger-pump-any-creature` | 2 | 3 |
| `etb-pump-target-creature` | 1 | 4 |
| `sets-base-power-or-toughness` | 1 | 19 |
| `attack-trigger-untap-attacker` | 1 | 3 |
| `activated-untap-another-permanent` | 1 | 2 |

**DEFAULT: yes — split each to an `-own-` sibling.** This is the reversal of
batch-6 D3 applied generally, already recorded in grammar §6a.

Note: after its split, `attack-trigger-pump-any-creature` holds **Mayhem Patrol
alone**, and `etb-pump-target-creature` — which I certified clean in tier 4 —
loses Herald of the Fair.

VERDICT:

---

## 6. Fix one scope field (no members move)

`activated-tap-grants-haste-other-creature-you-control` has scope
`any-creature` while its own ratified name says `you-control`. The name is
right — you ratified it under D3f. The field is wrong.

**DEFAULT: yes — scope → `your-stuff`.** Clears both a C4b and the single C4d.

VERDICT:

---

## 7. Four one-offs that each need their own answer

| axis | member | problem | my read |
|---|---|---|---|
| `direct-damage-any-target` | Unstable Amulet | "deals 1 damage to **each opponent**" — mass, not targeted | move to `rule:mass-damage-opponents` (**does not exist**; nearest is `mass-damage-opponent-creatures-only`, which is creatures) |
| `attack-trigger-buff-other-attacker-plus1-counters` | Sovereign Okinec Ahau | "**for each** creature you control…" — mass, no target, no "other" | ledger; no mass sibling exists |
| `etb-grants-connive-to-other-creature` | Mob Lookout | "target creature **you control** connives" — no "other", own-restricted | drop `-other-` from the slug (only 2 members, both alike) |
| `cast-trigger-draw-on-target-own-creature-spell` | The Great Henge | triggers on a creature **entering**, not on a cast; no "target". Axis already carries 3 open C3 findings | **this axis is multiply broken — I recommend a dedicated re-audit, not a patch** |

**DEFAULT: as read above, except the last — which I recommend you defer.**

VERDICT:

---

### If you say "all defaults"

~8 new axes · 4 renames · ~60 member moves · 1 scope fix · 1 axis deferred for
its own pass. One declared spec under the usual gates, but I would split it in
two — the renames and the self-class (calls 1–2, 60 of the 93) are mechanical
once ruled; calls 3–7 mint eight names and are worth landing separately so a
bad name is cheap to back out.

### What this does not cover

C1b/C2/C3 still carry 22 findings between them, unchanged by anything here.
And C4 only checks three printed words — `target`, `another`/`other`, and
ownership. Your ruling covers every templating word; `may` (optional vs
mandatory), `each` vs `all`, and `opponent` vs `player` vs `defending player`
are the obvious next ones and are not yet enforced by anything.
