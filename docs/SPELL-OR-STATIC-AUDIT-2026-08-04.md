# `spell-or-static` AUDIT — THE BLIND SPOT (2026-08-04)

Item 2 of the 2026-08-04 handoff: *"the gap census cannot see anything that lands
in `spell-or-static`… it deserves its own audit — it is the one place the
tooling is blind by construction."* **Zero API calls. No ratification required,
so run unasked per Gate 1.**

---

## 1. Method — grammar §1 supplies a decidable cut

> **§1** — *"DELIVERY … **OMITTED for spell abilities** (CR 113.3a): an
> instant/sorcery's resolution effect is the unmarked default. **Everything
> non-spell is MARKED.**"*

So the test needs no judgement: an **unmarked** line on a card that is **not an
instant or sorcery** is a defect **by definition**. Partition the bucket by type
line and the defect population falls out.

## 2. THE HEADLINE

| | lines | verdict |
|---|--:|---|
| `spell-or-static` total | **20,559** | 33% of all 61,858 ability lines |
| …on **instants/sorceries** | **10,617** | **CORRECT** — §1's unmarked default |
| …on **PERMANENTS** | **9,942** | **every one must be MARKED per §1** |

**9,942 lines — 16% of the corpus — sit on permanents carrying no delivery
marking at all.** None of them has ever appeared in a gap census, because
`cmd_gaps` excludes `spell-or-static` explicitly.

## 3. The permanent-side population, partitioned

| | lines | what it should be | anchor |
|---|--:|---|---|
| **F. other** | **7,480** | overwhelmingly `static` | 113.3d |
| **E. keyword w/ cost** | **1,900** | per-keyword, §2b derives it | 702.Na |
| **B. "as long as"** | **432** | `static` | 113.3d |
| **C. additional cost** | **66** | casting modifier, not a permanent ability | 601.2b |
| **D. aura / equip text** | **64** | `static` | 113.3d |

Group F is not exotic — it is Marang River Prowler's *"This creature can't block
and can't be blocked"*, Weakstone's *"Attacking creatures get -1/-0"*, Providence
of Night's *"Protection from monocolored"*. **These are ordinary static abilities
(CR 113.3d) and `static` is a ratified §2 token.** The gap is that nothing routes
them to it: `static` is currently reached only via the keyword pass and the
aura-prefix branch.

## 4. THE CLEAN DEFECT INSIDE IT — §2b's keyword router drops CR-stated classes

Group E is not a vocabulary gap. §2b already ratified the answer — *"route a
CR 702 keyword to the §2 token its `702.Na` text resolves to"* — and the router
is losing keywords the CR states **explicitly**.

**The CR states 19 keywords as `activated`. Only 13 reach `KEYWORD_HOME`.**

| lost | CR | corpus lines |
|---|---|--:|
| **Equip** | **702.6a** | **567** |
| Ninjutsu | 702.49a | 44 |
| Level Up | 702.87a | 25 |
| Fortify | 702.67a *(corrected — 702.66 is Delve)* | 2 |
| Aura Swap | 702.65a | 1 |
| Forecast | 702.57a *(corrected — 702.56 is Replicate)* | (0 bare lines) |

**Equip is §2b's own worked example.** The section quotes CR 702.6a verbatim —
*"Equip is an ACTIVATED ability of Equipment cards"* — as the illustration of why
no per-keyword ruling is needed. It does not route. Every Equipment in the corpus
has been carrying an unmarked equip line.

### 4a. Landwalk variants are a second, separate miss

The CR files these under **Landwalk (702.14)**, but cards print the *variant*:

| printed | lines |
|---|--:|
| swampwalk / islandwalk / forestwalk / mountainwalk / plainswalk | **118** |

`landwalk` is in the static list; `swampwalk` is not, so the matcher misses all
118. CR 702.14 is explicit that these are landwalk, so this is derivable, not a
ruling.

**757 bare-keyword lines lost between the two causes** (639 CR-activated + 118
landwalk), across **754 cards**.

## 5. WHY NOTHING CAUGHT THIS

Three independent guards were all blind to it, and each for a structural reason
worth recording:

1. **The gap census excludes `spell-or-static`** — the bucket is the fallback, so
   anything reaching it is reported as "nothing to see".
2. **`--rank` measures *buildable* lines**, which counts a `spell-or-static` line
   as resolved rather than as missing.
3. **The Clue ground-truth set contains no Equipment**, no landwalk creature and
   no bare-keyword-with-cost line. Fourth consecutive session in which it
   validated only the shapes it contains.

**This is the strongest argument yet for the standing note in CLAUDE.md:** a
fallback bucket that is excluded from reporting is not a safe default, it is an
unmonitored sink. **20,559 lines were in it and half were wrong.**

## 6. RECOMMENDED, NOT DONE

> **STEP 1 IS DONE — 2026-08-04. `docs/KEYWORD-ROUTER-FIX-2026-08-04.md`.**
> **824 lines moved, not the 757 predicted here.** The cause was not six
> missing names: §2b's *"the class says which slot, the templated text says
> which token in that slot"* was implemented backwards, and the same defect had
> **misrouted Unearth (57 lines) onto `replacement`** — a wrong *ratified*
> token, which no gap census can report. Landwalk came to 128 rather than 118,
> because CR 702.14a states a **grammar**, not the five basic variants.
> Permanent-side `spell-or-static` is now **9,178**, and steps 2–4 below stand
> unchanged. Two CR citations in §4 above were wrong and are corrected in place.


Diagnosed but deliberately **not fixed in this pass** — `find_home` in
`foundry_cr702_classes.py` needs reading before I change it, and guessing at the
cause of a 6-keyword drop would be exactly the error this audit exists to catch.

Order of work, cheapest and safest first:

1. **Fix the §2b router** for the 6 CR-stated `activated` keywords and the 5
   landwalk variants. Pure derivation, no new vocabulary, ratified rule already
   in place. **757 lines.**
2. **Route bare static abilities on permanents to `static`** (groups B, D, F —
   7,976 lines). `static` is already a ratified §2 token; this is wiring, but it
   is large and should be measured with the same before/after line-diff
   discipline used on the trigger-verb fix.
3. **Rule group C** (66 lines): "As an additional cost to cast this spell" on a
   *permanent* card is a casting modifier, not an ability of the permanent.
   CR 601.2b. Genuinely needs a Captain call on which slot, if any.
4. **Stop excluding `spell-or-static` from the census** — or report it with the
   instant/sorcery split applied, so the permanent-side population is visible
   permanently rather than by audit.
