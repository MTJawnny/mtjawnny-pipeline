# TRIGGER-CONDITION VERB SET — DERIVATION RULING (2026-08-04)

Found while ratifying `discard-trigger`, at Captain's standing direction to
*"reference the CR each time"*. **Zero API calls.**

This is the **ninth** instance of the CR 113.3c bug class, and the first one
whose root cause is the *mechanism the previous eight fixes relied on*.

---

## 1. The defect

`trigger_clause()` decides where a trigger CONDITION ends. CR 113.3c:

> *"Triggered abilities have a **trigger condition** and an **effect**. They are
> written as '[Trigger condition], [effect]'."*

A comma does not always end the condition — "Whenever a Mutant**,** Ninja, or
Turtle you control enters" has commas inside the object phrase. So the function
walks the comma cuts and returns the first prefix that carries a trigger verb.

Its verb list was hand-curated, and carried this comment:

> *"a verb missing here only makes the clause end earlier, which is the
> conservative direction."*

**That is backwards, and it is why the defect survived.** The loop returns the
first prefix carrying a *listed* verb. When the real event verb is **absent**,
the loop walks **past** the condition and returns a prefix whose verb came from
the **effect**. A missing verb makes the clause end **later**.

### 1a. Measured

| | |
|---|--:|
| curated verb list | 24 verbs |
| `when`/`whenever` lines in corpus | 13,028 |
| lines whose first comma-prefix carried **no** listed verb | **488** |

Worked cases, each a real misfile into `discard-trigger` because "discard"
appeared in the effect half and *was* a listed verb:

| card | printed trigger condition | CR |
|---|---|---|
| Illuna, Apex of Wishes | "Whenever this creature **mutates**" | 702.140 |
| Ulrich of the Krallenhorde | "Whenever this creature **transforms**" | 701.27 |
| Fell Stinger | "When this creature **exploits** a creature" | 702.110 |
| Sauron, the Dark Lord | "Whenever the Ring **tempts** you" | 701.54d |
| Battlefield Scavenger | "Whenever you **exert** a creature" | 701.39 |

## 2. RULING — the verb set is DERIVED, not curated

Same principle that already parses the DELIVERY tokens out of grammar §2 at run
time: **a curated list is only ever as good as the last failure someone
noticed.** The set is now built from the CR's own keyword-action list in
`docs/cr-checks.json`, plus an explicitly CR-cited supplement.

### 2a. Only `kind == "keyword-action"` is bulk-derived

CR 702 **keywords** are deliberately NOT bulk-derived. They are ability
**names**, not event verbs, and folding in words like `flying` or `absorb` would
match inside a **subject** phrase and cut the clause **too early** — "Whenever
Flying Men, Goblin King, or a Bird enters" would stop at "whenever flying men"
and lose the event entirely. The CR 702 keywords that genuinely print as trigger
events are listed individually: `mutate` 702.140, `exploit` 702.110,
`crew` 702.122, `saddle` 702.171.

### 2b. Two verbs the CR list does not supply — found by regression, not by review

**`cycle` is filed by the CR as a KEYWORD (702.29), not a keyword-action**, so
deriving from the action list alone silently dropped it. Measured consequence
before the fix: Radiant Smite fell off `cycled-trigger` and Crystalline Resonance
flipped `any-` → `other-`, because their clauses ran on into the effect and
picked up "the starting player" / "another target permanent".

**Past participles are unreachable** by the `(es|s)?` inflection — `tapped` /
`untapped` (CR 603.2e) must be listed outright.

Both are now in the halt-guard, so losing them again stops the run.

## 3. Two further defects the fix exposed

1. **`at least` is a quantifier, not a timing clause.** The multi-delivery
   splitter treated any part opening `at` as a trigger, so Kytheon's *"if Kytheon
   and **at least** two other creatures attacked"* produced a bogus second
   delivery.
2. **`or`/`and` inside the SUBJECT phrase broke the split.** "Whenever Giott
   **or** another Dwarf you control enters" split to part 0 = "whenever ~",
   which carries no event, so its clause ran into the effect and Giott was filed
   as a `discard-trigger` off "you may discard a card". Leading segments are now
   re-joined until part 0 actually carries an event.

## 4. Impact — 59 lines, every one audited by hand

| transition | n | verdict |
|---|--:|---|
| `unclassified`+`other-attack-trigger` → `attack-trigger` | 26 | **fix** — the battalion family |
| `GAP:discard-trigger` → `unclassified` | 5 | **fix** — effect-half reads |
| `unclassified`+phase token → phase token | 8 | **fix** — spurious second delivery |
| `sacrifice-trigger` → `unclassified` | 3 | **fix** — Dark Depths / Plague Boiler class |
| recovered a real delivery from `unclassified` | 6 | **fix** — the "~ or another X" shape |
| others | 11 | **fix**, individually inspected |

### 4a. The battalion 26 — CR 207.2c decides it

Battalion is an **ability word**: *"they have **no special rules meaning** and no
individual entries in the Comprehensive Rules"* (CR 207.2c). So §2b's
keyword-derivation does **not** apply and the axis takes the **printed** trigger,
exactly as `becomes-untapped-trigger` does for Inspired.

Printed: *"Whenever this creature **and** at least two other creatures attack"* —
**the source must attack**, so unmarked `attack-trigger` is correct and the old
`other-attack-trigger` asserted something false. Glimmer Lens correctly **keeps**
`other-`: its source is an Equipment, which can never attack.

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| known-good routings | 9/9 (Willie Lumpkin is absent from the gated corpus — the expectation was wrong, not the code) |
| Clue/investigate ground truth | **0 of 139 changed** |
| every changed line | read individually, all 59 |

**The ground-truth set caught none of it — again.** 139 investigate routings were
byte-identical through a fix that moved 59 lines. A ground-truth set validates
only the shapes it contains; no Clue card is a battalion creature, a mutate
creature, or a Saga. Third consecutive session where this held.

## 6. OPEN — logged, not ruled

**§2a does not name the `~ or another X` compound.** "Whenever Giott **or**
another Dwarf you control enters" includes the source *and* others. Today it
resolves to unmarked (the `^when ~` override forces `other=False`), but §2a's
three-way table names only *the source* / *another* / *a*. Six cards sit on this
shape (Giott, Millicent, Psychomancer, Slagstone Refinery, Fear of Sleep
Paralysis, Projektor Inspector). **Captain ruling needed**; `any-` is the
defensible reading, since the source is included.
