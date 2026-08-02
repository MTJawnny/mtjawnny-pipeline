# CDR-09 §12a rename walk — derivation result, 2026-08-02

**Status: WALK HALTED BEFORE MUTATION. `codebook.json` is untouched**
(sha256 `61af1a1d7f81504f422feb4d…`, identical to session start).

Precondition 4 of the walk says: *"Re-derive the 16 renames from live state
rather than pasting §12a's list. If the live set disagrees with §12a, halt —
do not reconcile silently."*

**The live set disagrees.** This document is the halt.

Derivation script: `experiments/foundry_cdr09_derive.py` (writes nothing).
Machine output: `experiments/out/foundry/cdr09_derivation.json`.

---

## 1. Preconditions 1–3 all passed

| gate | result |
|---|---|
| `foundry_codebook.py lint` | clean — 455 axes, 7,699 members, 7,699 assertions |
| `foundry_family_sweep.py --strict` | 196 findings, **6 blocking** — matches handoff exactly |
| backup | `backups/codebook.v0.7.pre-cdr09-rename-walk.20260802-132352.json`, verified by readback (hash-identical **and** parsed deep-equal, 455 records) |

## 2. What agrees with §12a

**The axis count is exactly right: 33 active axes carry a counter token.**
All **16** renames §12a lists were independently re-derived and every one is
confirmed non-conforming for the reason §12a gives. Nothing in §12a's list is
wrong.

## 3. What disagrees — §12a's list is SHORT BY 3, plus 1 contradiction

§12a's arithmetic gate is *16 renames + 17 already-conforming = 33*. Live
derivation gives **16 + 3 + 1 + 13 = 33**. The count reconciles exactly; the
partition does not. §12a counted these 4 axes as "already conforming". They
are not.

### 3a. Three axes non-conforming under §8 rule 1 — the `with`-plus-qualifier class

§8a rule 2 admits `with` as a left binder with the example `etb-with-counters`,
where `with` is the *immediate* left neighbour. In all three below a qualifier
sits between `with` and `counters`, so nothing binds the counter token
directly. **Two of the three are additionally clear §8 rule 1 violations**
("noun sense is always TYPED") — their own definitions name the counter type
while their slugs do not. That is not an artifact of a strict reading.

| axis | mem | why non-conforming | proposed |
|---|--:|---|---|
| `rule:etb-with-negative-counters` | 3 | definition says **-1/-1**; `negative` is not ratified type vocabulary (`minus1` is) | `rule:etb-with-minus1-counters` |
| `rule:create-token-with-x-counters` | 2 | definition says **+1/+1**; slug is untyped | `rule:create-token-with-x-plus1-counters` |
| `rule:cost-reduction-scales-with-own-counters` | 1 | genuinely type-agnostic ("the number of counters accumulated on the source permanent") → the `any-` case, but no phrasing is obvious | **needs a ruling** — `-scales-with-own-any-counters` is the mechanical answer and reads badly |

The first two I'd ratify as written. The third is a real naming question, not a
typo.

Note `create-token-with-x-counters` also sits under §8 rule 3 pressure (a
counter is not a token): the slug names both, legitimately here, since the
definition describes a token that *receives* counters.

### 3b. One axis whose definition contradicts its own name AND its members

`rule:draw-second-card-trigger-plus1-counter` (4 members) — **this is not a
naming problem and it is not in scope for the walk.**

- **Slug** says: draw-second-card trigger → +1/+1 counter.
- **Definition** says: draw-second-card trigger → *"producing a **creature
  token** as a reward."*
- **Members** say: all four disagree with each other.

| member evidence (human-class quotes) | delivery | payoff |
|---|---|---|
| "Whenever you draw your second card each turn, put a +1/+1 counter on this creature." | draw-second | counter |
| "When this creature enters, if it was the second spell you cast this turn, put a +1/+1 counter on target creature." | **etb / cast-second** | counter |
| "Whenever you cast your second spell each turn, draw a card, then create a 0/3 white Wall creature token…" | **cast-second** | **token** |
| "Whenever you draw your second card each turn, create a 1/1 colorless Thopter artifact creature token with flying." | draw-second | **token** |

So the axis mixes two deliveries (draw-second vs cast-second) **and** two
payoffs (counter vs token) — a live §8 rule 3 violation at the *membership*
level, which the name-only walk cannot touch. Only one of the four members
matches the slug.

**This is a split, not a rename.** It needs a Captain ruling before the walk
can classify the axis at all, because its sense cannot be derived from its
definition (the definition mentions no counter).

## 4. Why the walk did not proceed with the undisputed 16

Executing the 16 in isolation was considered and rejected. All 16 are safe on
their own, but:

1. §12a's stated post-walk gate (*16 + 17 = 33*) would not describe the
   resulting codebook, so the walk could not be verified against its own
   ratified check.
2. **CDR-13's Homograph Form Ledger rests on a "zero new churn" claim.** Three
   axes needing a second rename later is precisely new churn, and it would be
   discovered *after* the ledger was built on the assumption it could not
   happen.
3. `draw-second-card-trigger-plus1-counter` would keep a name asserting a
   counter payoff that its definition and 3 of its 4 members contradict.

Ratifying §3a and §3b turns this into a **19-rename walk plus one split**, done
once.

## 5. What is needed to unblock

1. **Ratify or reject the three §3a renames** (two are straightforward; the
   third needs a name).
2. **Rule on `draw-second-card-trigger-plus1-counter`** — split by payoff, split
   by delivery, or both.
3. Then the walk re-derives, the arithmetic gate becomes *19 + 13 + (split
   outcome) = 33*, and executes in one pass under the backup law.

## 6. Unchanged by this session

`codebook.json` sha256 `61af1a1d7f81504f422feb4d…` — no mutation. ADD-08 /
Tier-0 bug 4 remains blocked on the walk, as does CDR-13.
