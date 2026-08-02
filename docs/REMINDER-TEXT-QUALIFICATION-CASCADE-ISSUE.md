# Reminder Text — Full State & the Qualification-Cascade Shadowing Issue

**Written:** 2026-07-10, end of a long session (`mtjawnny-pipeline` repo,
`experiments/tier_engine.py`). **Purpose:** Captain asked for a full rescan
of the engine's reminder-text handling, a comprehensive writeup of state +
history, and wants a second model (Fable 5) to propose ratification ideas
for one specific, newly-found issue below. This doc is investigation +
options, not a decision — nothing here is authorized to ship without an
explicit ruling, same house rule as everything else in this repo.

Captain's own framing, verbatim, worth preserving: *"reminder text is such
a problem... other reminder text cards are still too high. unless of
course its just a bug with the viewer and the current entries have
reminder text PLUS something in common with swift foot boots... I might
have been chasing a ghost based on the viewers text output."*

**Short answer up front: not a ghost, not a viewer bug.** The viewer is
rendering exactly what the engine computes. The engine itself has a real,
newly-confirmed defect: a generic, near-universal reminder-text match can
"claim" a candidate pair and permanently prevent a much more specific,
more meaningful match (a shared granted keyword) from ever being checked
at all. Section 4 below has the receipts.

---

## 1. How to verify this doc against the repo

```bash
cd ~/Projects/mtjawnny-pipeline
git log --oneline -10
git status --porcelain
```

Everything below describes repo state as of commit `6f81a9c` on `main`,
with a clean working tree (nothing uncommitted at time of writing). If
`git log` shows commits past `6f81a9c`, the repo has moved — trust the
repo over this doc, especially for anything in Section 4 (numbers were
measured live against this exact commit and will drift with any further
scoring change).

---

## 2. This session's reminder-text history, in order

All of this landed in four commits, all today, all on top of `190e8fa`
(the last commit before this session):

### 2a. Entry #5 — cumulative fragment scoring (commit `5166ddd`, shared commit with #4)
Not reminder-specific, but touches the same qualification code
(`find_shared_fragment` → `find_shared_fragments`). `find_shared_fragment`
now credits every qualifying non-overlapping run in the best-matching
paragraph pair, not just the longest, with diminishing rank weight.

### 2b. Entry #4 — granted-keyword-SET kinship (commit `5166ddd`)
New Tier 2 mechanism (`mechanism="keyword_grant"`) for the Equipment/Aura
"Equipped/Enchanted creature has X" idiom (Swiftfoot Boots ↔ Lightning
Greaves motivating case). Along the way, found and fixed a real
pre-existing bug: `is_keyword_only_paragraph()`'s keyword-prefix check
wasn't word-boundary safe — "equipped" silently prefix-matched an
Equipment card's own "Equip" keyword, wrongly excluding the ENTIRE grant
clause from `matchable_paragraphs` before ANY mechanism (including
ordinary text matching) could ever see it. This is Entry #4's own
motivating case's root cause — Swiftfoot Boots/Lightning Greaves had
**zero** searchable text before the fix.

### 2c. Entry #6 — reminder-fragment text-comparison bug (commit `e150243`)
Found live-reviewing Swiftfoot Boots' viewer output: equip-cost boilerplate
(`{1}: attach to target creature you control. equip only as a sorcery.`)
was cluttering its Tier 2 list. Root cause: `text_injected_on_side()` /
`find_reminder_attribution()` compared a `find_shared_fragment(s)`-
reconstructed fragment (every token's trailing period stripped, the CO-C
tokenization convention) against the RAW injected-reminder paragraph text
(periods intact) — a comparison that can never succeed across an internal
sentence boundary within a multi-sentence paragraph. This silently
disabled `fragment_both_sides_injected()`'s hard discount
(`PROVENANCE_DISCOUNT_WEIGHT`) for exactly the case it exists to catch.
Same bug, third location: two hardcoded gate constants
(`SWIFTFOOT_EQUIP_TEXT`, `FAITHLESS_FLASHBACK_TEXT`) used the same
period-bearing raw text for exact-equality checks, making two named gates
(`check_gb_swiftfoot_boots_gate`, `check_gc_faithless_looting_gate`) a
structural always-PASS regardless of real state, for who knows how long.

Fixing it surfaced two things that had never actually been verified true:
- `check_gb_swiftfoot_boots_gate`: even with the discount now firing
  correctly, 1 equip-reminder row still sat in Swiftfoot Boots' displayed
  top 10 — a **hard floor**, not further reducible by the discount
  constant alone, coming from a SEPARATE already-ratified mechanism
  (Phase 3's frame-affinity restoration — any same-type match restores
  `effective_weight` toward 1.0 independent of the provenance discount;
  measured directly: `PROVENANCE_DISCOUNT_WEIGHT=0.0` still floors
  `effective_weight` at `restored_fraction=0.375` for an Equipment-vs-
  Equipment pair). `PROVENANCE_DISCOUNT_WEIGHT` lowered `0.05 → 0.01`,
  gate's expected floor updated `0 → 1`.
- `check_gc_faithless_looting_gate`: the flashback reminder's corpus DF
  has drifted `173 → 172` (ordinary corpus growth, unrelated to this
  session) — now exactly at the rescue-band ceiling, so 171 rows now
  legitimately qualify under the already-ratified DF-banding rule. Gate's
  expected count updated `0 → 171`.

### 2d. Entry #7 — mechanism sort priority + P/T modifier, then corrected (commit `d8e488e`, then `6f81a9c`)
Two asks from live-reviewing Zurgo's Tier 2 table:

1. **`mechanism="keyword"` must always outrank `mechanism="reminder"`.**
   Confirmed live: Hanweir Garrison (reminder) was outranking Zurgo
   Stormrender (keyword). Implemented as a hard categorical sort key
   (`keyword_over_reminder_priority()`), not a scalar bonus, so no future
   DF/corpus drift can silently undo it. Scoped to keyword-vs-reminder
   only — text/mana/keyword_grant rows are unaffected, still competing
   purely on rank score.
2. **Equipment/Aura P/T stat modifiers ("+N/+N")** were being discarded
   entirely by Entry #4's extraction. First pass: added as a scalar
   mismatch penalty. Captain's correction: a penalty blended into the same
   score as tag_score/affinity/CI isn't real priority — wanted "exact buff
   beats near buff beats far buff" as a hard, fully-graduated guarantee.
   Rebuilt as `pt_exactness_priority()`, a second categorical sort-key
   dimension, same shape as (1). Documented explicitly at the time: a
   single global sort **cannot** make "exact beats near" absolute for
   `keyword_grant` rows while leaving every other mechanism's ordering
   completely untouched — pragmatic resolution keeps exact matches (P/T
   distance 0) in the normal competitive pool, only demotes non-exact
   matches into a graduated lower tier.

Each of (2c) and (2d) individually shifted Swiftfoot Boots' relative
rankings enough to let more equip-reminder-boilerplate rows back into its
fixed top-10 display window by pure relative displacement (not new bugs) —
`check_gb_swiftfoot_boots_gate`'s measured floor moved **three times** in
one session: `0 → 1 → 2 → 4`. This is flagged in the constant's own code
comment as an expected, ongoing consequence of unrelated precision
improvements elsewhere, not a regression signal by itself. It is also the
direct reason Captain went back to look at the viewer again and found the
issue in Section 4.

---

## 3. Current architecture: the qualification cascade

`assign_tier(anchor_doc, candidate_doc, ...)` (`tier_engine.py:2183`)
decides ONE tier + ONE mechanism per anchor/candidate pair, in this exact
order, each step gated on nothing having claimed the pair yet:

```
1. Tier 0 check (byte-identical full text + frame match)
2. Tier 1 check (byte-identical whole paragraph, or demoted from failed
   frame match) — sets base=0 or base=1
3. ELSE: text/reminder Tier 2 fragment path (find_shared_fragments(),
   DF-banded, rescue ceiling 172) — sets base=2, mechanism="text" or
   "reminder" (relabeled if the winning fragment came from an M2-injected
   paragraph)
4. Mechanism 1 (keyword_kinship) override — line 2338:
   `if best_kinship is not None and (base is None or
    best_kinship["tier"] < base): ... mechanism = "keyword"`
   Only overrides on a STRICTLY BETTER tier. A tie leaves step 3's
   mechanism standing.
5. keyword_grant (Entry #4) — line 2380: `if base is None:` ONLY.
   Never runs at all if step 3 already set base to anything, no matter
   how weak.
6. mana kinship (Phase 4, R6) — line 2422: `if base is None:` ONLY.
   Same gating as step 5, runs after it.
7. `if base is None: return None` → Tier 3 (tag-based) territory.
```

Steps 5 and 6 share the exact same shape: **"only fires if literally
nothing else found anything."** This was an explicit, ratified design
choice for mana kinship (R6, Phase 4): *"Fires ONLY when text/keyword
matching found nothing at all for the pair... mana kinship is Tier-2-only,
so it can never override an already-better tier."* Mana kinship is
deliberately the broadest, weakest-evidence, last-resort net — losing to
literally anything more specific is the intended behavior, not a defect.

**keyword_grant inherited this exact same gating by copying the code
shape mana kinship already used** (see `tier_engine.py:2380`, `if base is
None:`, immediately followed by the near-identical mana block at line
2422). Nobody explicitly ruled on whether "only fires if nothing else
found anything" was the RIGHT precedence for keyword_grant specifically —
it was inherited, not decided. Section 4 shows why that inherited choice
produces a worse outcome for this mechanism than it does for mana.

---

## 4. The finding: reminder text is "shadowing" real keyword_grant matches

### 4a. Concrete cases, verified against real oracle text

| Candidate | Oracle text (grant clause) | Shared keyword with Swiftfoot Boots | Currently shows as |
|---|---|---|---|
| Crystal Slipper | "Equipped creature gets +1/+0 and has **haste**." | haste | `mechanism=reminder`, evidence = generic equip-cost boilerplate (DF≈64) |
| Ring of Valkas | "Equipped creature has **haste**." | haste | same |
| Skateboard | "Equipped creature gets +1/+0 and has **haste**." | haste | same |
| Boots of Speed | "Equipped creature gets +1/+0 and has **haste**." | haste | same |
| Strider Harness | "Equipped creature gets +1/+1 and has **haste**." | haste | same |

All five grant "haste" via a plain, well-formed `Equipped creature
[gets +N/+N and] has X` clause — exactly the idiom `GRANT_CLAUSE_RE`
already parses correctly (confirmed: `granted_keyword_kinship_match()`
independently returns a real, qualifying match for every one of these
when called directly, outside the cascade). Swiftfoot Boots' own grant is
"hexproof and haste" — haste is a genuine, real, shared keyword. This is
NOT a false positive; it's a real similarity signal that never gets
evaluated, because all five candidates' equip cost also happens to be
`{1}` (same as Swiftfoot Boots), so their generic Equip-reminder
boilerplate ALSO text-matches at DF≈64 — and because step 3 in the
cascade runs before step 5, that boilerplate match claims `base=2` first
and keyword_grant (step 5) never even runs for these five pairs.

### 4b. How big is this, exactly? (measured, not estimated)

Script: iterate Swiftfoot Boots' full candidate pool (via
`gather_candidate_pool()`, unmodified); for every candidate that currently
resolves to `mechanism in ("text", "reminder")` at Tier 2, independently
call `granted_keyword_kinship_match()` on the same pair (bypassing the
cascade) and check whether it ALSO returns a qualifying match.

```
total text/reminder Tier2 rows for Swiftfoot Boots: 65
of those, SHADOWED by a qualifying keyword_grant match that never got checked: 5
  Crystal Slipper: currently mechanism=reminder DF=64, shadowed match: ['haste'] penalty=0.45
  Ring of Valkas:  currently mechanism=reminder DF=64, shadowed match: ['haste'] penalty=0.30
  Skateboard:      currently mechanism=reminder DF=64, shadowed match: ['haste'] penalty=0.45
  Boots of Speed:  currently mechanism=reminder DF=64, shadowed match: ['haste'] penalty=0.45
  Strider Harness: currently mechanism=reminder DF=64, shadowed match: ['haste'] penalty=0.60
```

**5 of 65 (7.7%)** of Swiftfoot Boots' text/reminder Tier 2 rows have a
real, hidden keyword_grant match that the cascade never lets run. This is
ONLY the "equip cost happens to also be {1}" subset — the true
denominator of "candidates that share a real granted keyword with
Swiftfoot Boots but got claimed by boilerplate text first" could not be
larger than this (a shared keyword with a DIFFERENT equip cost wouldn't
generate matching boilerplate text in the first place, so it wouldn't be
shadowed — it would already correctly reach keyword_grant). This 5-row
number is a precise, not approximate, count for this one anchor.

**Not yet measured, flagged explicitly rather than assumed:** whether this
shadowing pattern is similarly sized for OTHER Equipment/Aura anchors
beyond Swiftfoot Boots (Lightning Greaves, Mask of Avacyn, Cobbled Wings,
etc., all of which now have their own `keyword_grant` rows per Entry #4).
A full corpus-wide sweep (every card with a `granted_keyword_facts` entry,
same shadowing check) was not run this session — sizing that is the
natural first step before choosing a fix, not guessed at here.

### 4c. Checked, and NOT the same issue: mana kinship

Ran the identical shadowing check for Sol Ring (mana kinship instead of
keyword_grant):

```
Sol Ring: total text/reminder Tier2 rows: 8, shadowed by a qualifying mana match: 8
```

8/8 looks alarming at first glance but is expected and NOT a bug: `Sol
Ring` is itself a mana-producing card, so nearly ANY other mana-producing
candidate in its pool will trivially share SOME pip via
`mana_pip_kinship_match()`'s broad "any shared pip qualifies" rule (R6) —
this is mana kinship correctly acting as the deliberately-broad,
deliberately-last-resort net it was ratified to be. The distinction from
Section 4a/4b: keyword_grant's shadowed matches are NARROW, SPECIFIC,
high-confidence signals (an exact shared named keyword) losing to
boilerplate; mana kinship's "shadowed" matches are themselves broad,
low-confidence signals that are SUPPOSED to lose to anything more
specific. Don't conflate the two when scoping a fix.

### 4d. Checked, and clean: Mechanism 1 (keyword_kinship) shadowing

Ran the same style of check across all 9 calibration anchors + Zurgo +
Delney (does a real Mechanism-1 keyword match exist for any candidate
currently resolving to text/reminder, at a tier the keyword match doesn't
strictly beat, and therefore never gets to override per line 2338's `<`
comparison?):

```
(no output — zero shadowed rows found on any of the 11 anchors checked)
```

Mechanism 1 does not currently exhibit this problem anywhere in the
calibration panel. (This is a DIFFERENT question from the "keyword must
sort above reminder" ranking fix already shipped in Entry #7 part 1 —
that fix addressed cross-row ranking after both mechanisms are already
correctly assigned; this check is about whether the mechanism ASSIGNMENT
itself ever gets suppressed. It doesn't, today, on this panel.)

---

## 5. What is and isn't a "viewer bug"

Captain's instinct to double-check whether this was a viewer rendering
issue was reasonable and worth ruling out explicitly: **it is not.**
`viewer.html` and `emit_viewer.py` render exactly what
`build_row_export()` receives from `assign_tier()`'s own return dict —
there is no separate viewer-side scoring, re-ranking, or re-labeling
logic anywhere in `emit_viewer.py` or `viewer.html` that could produce a
mismatch between "what the engine decided" and "what's on screen." Every
number and mechanism label shown live via `/api/anchor` this session was
independently reproduced by calling `assign_tier()` directly in a
standalone script, byte-for-byte. The defect is upstream, in
`assign_tier()`'s qualification cascade itself (Section 3), not in
anything downstream of it.

---

## 6. Options for ratification (sketched, not decided — for Fable 5 / Captain to weigh)

None of these are authorized. Sketched here to give a second model
(Fable 5) real starting material rather than a blank slate.

**Option A — Reorder the cascade: run keyword_grant before text/reminder.**
Move step 5 ahead of step 3, so an exact shared granted keyword always
wins over generic boilerplate text, mirroring how Mechanism 1 (keyword_
kinship) already effectively gets first crack via its own override logic.
Simplest change, smallest diff. Risk: keyword_grant would now ALSO
preempt genuinely meaningful (non-boilerplate) text matches for Equipment/
Aura pairs that happen to also share a keyword — untested whether that
tradeoff is ever actually worse in practice; needs corpus measurement
before/after, same discipline as every other change this session.

**Option B — "best evidence wins" instead of "first found wins."**
Run all four paths (text/reminder, keyword_kinship, keyword_grant, mana)
unconditionally for every pair, then pick the winner by some cross-
mechanism comparable quality measure (e.g. rarity/DF-equivalent, or a
fixed mechanism-quality ranking table) rather than sequential gating.
Mechanism 1 already partially does this (line 2338's tier-comparison
override) — this option generalizes that pattern to keyword_grant and
mana too. More principled, more even-handed, meaningfully larger change
— touches the FROZEN tier-assignment core more broadly than Option A,
needs its own full impact measurement and gate re-verification.

**Option C — Narrow fix: only let keyword_grant be shadowed by a
GENUINELY competitive text match, not by boilerplate specifically.**
Keep the "first found wins" cascade shape, but add a check before step 3
claims the pair: if the winning text/reminder fragment is BOTH-SIDES-
INJECTED reminder boilerplate (the exact `fragment_both_sides_injected()`
check Entry #6 already fixed and uses for rank discounting), let
keyword_grant run anyway and compare the two, keeping the better one.
Smaller, more surgical than Option B; doesn't touch mana kinship's already
-ratified behavior at all; needs its own decision about what "compare and
keep the better one" means (by penalty magnitude? by DF? by a fixed
mechanism preference?).

**Option D — Do nothing to the cascade; treat this as evidence-labeling.**
Leave qualification order as-is (text/reminder still "wins" the pair,
same tier), but when the winning match IS both-sides-injected boilerplate
AND a keyword_grant match also exists, blend it into the DISPLAYED
evidence/rank rather than the QUALIFICATION decision (e.g. "reminder-
boilerplate match; also shares granted keyword 'haste'" as a combined
evidence string, similar in spirit to Entry #5's cumulative-fragment-
scoring pattern). Avoids re-touching the qualification cascade at all;
purely additive/display-layer; likely the least corpus-disruptive option,
but doesn't actually change the RANK the row gets, only what it says —
worth Fable 5's read on whether that satisfies the actual complaint or
just documents it more clearly.

Common next steps for whichever direction gets picked: corpus-wide
shadowing count (not just Swiftfoot Boots — see the open item in 4b),
full gate suite, determinism ×2, before/after reorder count, viewer
regen, report header note. Same ritual as every other change this
session — no exceptions for this one.

---

## 7. House rules, repeated because this is a FROZEN-core question

Halt-loudly. Never commit without explicit ask (this doc itself commits
nothing — it's pure investigation). Measure corpus impact before
ratifying, not after. Snapshot after any ruling-affecting change.
Regenerate the viewer cache and restart `serve_viewer.py` after any engine
change. Determinism verified twice before calling anything done. See
`TIER-ENGINE-STATE-AND-V2.11-HANDOFF.md` for the full standing list.

---

## 8. Fable 5's ratification recommendation (2026-07-10, same session)

Asked to review this doc and propose ratification ideas. Verified the
repo state independently (confirmed `6f81a9c`, clean tree, doc's
measurements current) before answering. Recommendation, verbatim:

> **Ratify Option C, with a precise categorical rule and one element of D
> folded in.**
>
> **The rule:** at step 3, if *every* qualifying run in the winning
> paragraph pair is both-sides-injected boilerplate (`runs[0]` AND all
> `extra_fragments` — the per-run `both_injected` flags are already
> computed, costs nothing new) AND `granted_keyword_kinship_match()`
> qualifies, keyword_grant claims the pair outright. No scalar comparison.
> If even one run is genuine non-boilerplate text, text/reminder keeps the
> pair exactly as today.
>
> **Why categorical, not "compare and keep the better":** the engine has
> already ruled on the value of both-injected boilerplate —
> `PROVENANCE_DISCOUNT_WEIGHT = 0.01`, i.e. near-worthless evidence. Any
> qualifying grant match is categorically stronger; inventing a scalar
> comparison between DF and grant-penalty just to confirm 0.01-weight
> evidence loses would be a cross-mechanism metric nobody needs. This also
> matches the Entry #7 precedent: hard categorical priority, immune to DF
> drift, not a blendable bonus.
>
> **Fold in D's evidence idea:** when keyword_grant takes the pair, append
> the displaced boilerplate as a note (`[also matched equip-reminder
> boilerplate, DF=64]`). Maximal information shown, self-explaining diffs.
>
> **Why this is the R6-faithful answer, not A or B:** the current bug
> means the pair still qualifies, but on the WEAKEST evidence available,
> buried at weight 0.01 despite carrying a real shared-keyword signal —
> that's rank burying the wrong thing, exactly what R6 exists to prevent.
> C restores the strongest evidence without excluding anyone. It's also
> the overdue ruling on keyword_grant's inherited-not-decided gating
> (Section 3's key finding), scoped to exactly the mechanism that was
> never actually ruled on.
>
> **Against A:** preempts genuine, rare text matches for any Equipment/
> Aura pair that also shares a keyword — a real regression risk the doc
> itself flags, buys nothing C doesn't.
>
> **Against B:** its generality solves problems that don't exist (4d shows
> Mechanism 1 has zero shadowing; 4c shows mana must stay last-resort).
> Subtract those and B's effective scope collapses to keyword_grant-vs-
> text — which is C, minus the FROZEN-core surgery and minus inventing a
> cross-mechanism quality metric that doesn't exist.
>
> **Against D alone:** the complaint is substantive, not cosmetic — the
> label is wrong AND the rank comes from the wrong pathway (boilerplate
> discount + frame-affinity floor, instead of grant penalty + P/T
> priority). D documents the defect; C fixes it.
>
> **Mana kinship:** untouched by construction — its `if base is None` gate
> is unmodified; C only changes which mechanism sets `base` upstream.
>
> **Measurement ritual before ratifying:**
> 1. Corpus-wide shadowing sweep (the open 4b item) — specifically count
>    shadowed pairs having a non-boilerplate extra run. That number is
>    exactly the behavioral gap between A and C; if zero today, C is still
>    the safer invariant going forward.
> 2. Two known interactions to verify, not guess: (a)
>    `check_gb_swiftfoot_boots_gate`'s floor of 4 will move again — the
>    five rows relabel reminder→keyword_grant; (b) those five now enter
>    Entry #7's `pt_exactness_priority` regime (Crystal Slipper's +1/+0 vs
>    Boots' no-mod means pt_distance > 0 → graduated demotion). Both are
>    probably correct outcomes, but measure them.
> 3. Then the standard ritual: full gate suite, determinism ×2, viewer
>    regen, report header note.

**Not yet ruled on by Captain.** This is Fable 5's recommendation, logged
for the record — implementation requires an explicit go-ahead, same as
everything else in this doc.

---

## 9. RATIFIED and IMPLEMENTED, 2026-07-10 (same session)

Captain: "run measurment pass and implement option C." Both done.

**Measurement pass (the open item from Section 4b and Fable 5's
recommendation):** corpus-wide, not just Swiftfoot Boots. Of 9,059 pairs
that qualify via `granted_keyword_kinship_match()`, **587 are correctly
claimed by genuine, strong text matches today** (e.g. Behemoth Sledge vs
Unflinching Courage, DF≈2 — a near-verbatim match) and **71 are shadowed
by pure both-sides-injected boilerplate** with nothing else backing the
win. This directly confirms Fable 5's core argument against Option A: a
blanket cascade reorder would have wrongly preempted all 587 genuine
matches to fix only 71 real problems.

**Implementation:** exactly Option C as recommended — categorical, not a
scalar comparison, folds in Option D's "keep the displaced evidence"
idea. One implementation bug caught during the post-fix corpus
re-measurement (not shipped): the new check's guard needed `base == 2`
explicitly, not just "not None" — an earlier draft wrongly fired for
Tier 0 matches (which never set `fragment`) and crashed. Fixed before
verification passed.

**Post-fix verification:** re-ran the identical corpus-wide measurement.
0 pairs still shadowed by pure boilerplate (was 71) — all now correctly
resolve to `mechanism=keyword_grant`. All 587 genuine-text matches
confirmed byte-for-byte unchanged. Full gate suite 73/73 green
(`check_gb_swiftfoot_boots_gate`'s floor moved `4 → 3` — a genuine
reduction, not relative displacement this time), determinism confirmed
twice, viewer regenerated and confirmed live via `/api/anchor` — all five
motivating cards (Crystal Slipper, Ring of Valkas, Boots of Speed,
Skateboard, Strider Harness) now show `keyword_grant` with the boilerplate
preserved as a `[also matched: ...]` note.

Full details, including the exact code and report-header note text: see
`experiments/POKE-PUNCH-LIST.md` Entry #8 in the `mtjawnny-pipeline` repo.
Committed there; this doc is left uncommitted in this repo, same as
before — Captain's call whether to track it.
