# Findings memo — DF-distribution measurement pass (Gate 0)

*Measurement-only, per THESAURUS-REFINEMENT-PASS-1-HANDOFF.md §5 work item 1. No
engine changes. Working tree verified clean at tag `tier-engine-v2.9e2-baseline`
(commit `8cb70df`) before any of this ran. Corpus: 38,233 cards, 2026-07-03 R2
snapshot (unchanged from the triage pass). Scripts: `experiments/measure/
df_distributions.py` (Deliverables 1–2) and `experiments/measure/
pip_normalization.py` (Deliverable 3), both run twice with byte-identical
output — see raw logs in `experiments/out/measurement/*.txt` / `*.json`
(gitignored, regenerate with the commands below).*

```
python3 experiments/measure/df_distributions.py
python3 experiments/measure/pip_normalization.py
```

---

## 1. Natural breakpoints

**T1 paragraph population (`para_exact_df`, n=3,603 qualifying texts) is
extremely right-skewed, dominated by pairs.** 52.6% of all currently-qualifying
T1 paragraphs are shared by exactly 2 cards; the distribution is basically flat
from p1 through p50 (raw DF=2 the whole way), then climbs slowly to p90=10,
p95=18, and only opens up in the last percentile: p99=52, p99.5=82, p99.9=172,
p100=451. There is no sharp single elbow — it's a smooth long tail — but the
p90–p99 band (DF 10–52) is where "probably fine" gives way to "probably
boilerplate," and that range brackets the existing T2 floor (50) reasonably
well. The T2 pooled population (n=58,012, already floor-capped at 50) shows the
same shape: p50=3, p90=13, p99=39 — most qualifying fragments sit far below the
floor; the floor is doing real work only against a thin tail.

**The single loudest breakpoint is a length breakpoint, not a DF breakpoint.**
The four largest T1 offenders by raw DF — `{t}: add {c}.` (451), `this land
enters tapped.` (440), `choose one —` (330), `draw a card.` (270) — are *all*
shorter than `NGRAM_MIN_LEN` (5 tokens: 3, 4, 3, 4 tokens respectively). None of
them has a defined `ngram_scale_df` at all. If DRAFT RULING 1's commonality
weight is implemented by reusing `ngram_df_estimate()` unchanged (the function
T2 already uses), **it cannot see the four worst T1 offenders in the entire
corpus** — the mechanism would be structurally blind to exactly the cases
motivating it. This is not a tuning question; it's a scope gap that has to be
closed before a DF floor can "close F1" as DRAFT RULING 1 claims.

## 2. Surprises

**Surprise 1 — Black Market Connections' "timing opener" complaint is not a
Lane-3 flooding case at all.** Its opener paragraph (`at the beginning of your
first main phase, choose one or more —`) has `exact_df=1` — it is *unique* in
the corpus. It cannot mint a single T1 row with anyone, let alone flood. This
contradicts the triage doc's own hedge ("very likely Black Market Connections'
timing-opener complaint too... worth a direct check, not yet run here") — the
direct check now says no. Whatever Black Market Connections' actual complaint
is, it is not F1/Lane 3; recommend striking it from CO-A's expected-resolution
list and re-diagnosing separately.

**Surprise 2 — the "wanted" and "unwanted" DF ranges overlap, so no single flat
threshold can separate them.** Vandalblast's overload reminder sits at DF=26 —
*below* Growth Spiral's DF=54, Garruk's Uprising's DF=57, Cultivate's DF=70,
Rhystic Study's DF=77, Rampant Growth's DF=119, and Deadly Dispute's DF=128.
Vandalblast is unwanted boilerplate (Lane 3); the Lane 1c six are wanted,
human-obvious, currently-rejected clauses. Any single ascending DF cutoff that
lets Growth Spiral (54) through necessarily lets Vandalblast (26) through too,
since 26 < 54. **A pure DF-magnitude band cannot do this job alone** — this is
presumably why DRAFT RULING 1 already specifies "a band structure, not a pure
curve," but the measurement shows the problem is sharper than a curve-vs-band
question: it's that DF alone doesn't correlate with wanted/unwanted here at
all. The measured difference between these two groups isn't magnitude, it's
**provenance** — Vandalblast/Swiftfoot/Mystic Remora/Faithless Looting are all
v2.9 Mechanism-2 reminder-injected text (near-canonical templated boilerplate
by construction); the Lane 1c six are native, hand-written oracle text that
happens to be moderately common. A provenance-aware discount (injected text
discounted harder, at any DF) may be the mechanism DF-magnitude alone can't be.
Flagged loudly per instructions — not resolved here.

**Surprise 3 — pip normalization's `<n>`/`<mana>` merge can flip a currently-
correct same-color-pair match into an excluded one.** The ten literal
two-color "`{T}: Add {B} or {G}.`"-shaped guild-pair clauses each sit at
DF 26–34 today (all comfortably under the floor — each pair *already*
correctly clusters same-pair sources via plain text matching, no normalization
needed). Pip-normalizing collapses all ten into one skeleton, `{t}: add <mana>
or <mana>.`, at DF=358 — 7× over the floor. If the eventual CO uses the
normalized skeleton's DF as a *replacement* qualification gate rather than a
*parallel, better-tier-wins* path (the v2.9 M1/M2 pattern), this would
regress an already-correct behavior: same-pair guild sources would stop
matching each other. This mirrors DRAFT RULING 2's own worry about Arcane
Signet surviving normalization-driven DF increase — Arcane Signet's own clause
does survive, untouched, ngram-scale DF=8 both pre- and post-normalization,
since its ability is written in English ("any color"), not mana symbols, so
the normalizer never touches it — but the guild-pair family shows the same
failure mode DOES materialize elsewhere, on real cards, not just
hypothetically.

**Surprise 4 (confirms rather than contradicts) — the equip-reminder
boilerplate cluster gets *worse*, not better, under generic-numeral
normalization alone.** Merging all numeral-cost equip reminders (`{1}:`,
`{2}:`, `{3}:`, ...) into `<n>: attach to target creature you control. equip
only as a sorcery.` raises the cluster from Swiftfoot's individual DF=63 to
DF=235 (ngram-scale 245). This is expected given DRAFT RULING 2's own
generic-equivalence goal, but it means CO-A (T1 rarity gate) and pip
normalization are not independent work items — sequencing pip normalization
*before* CO-A's floor is calibrated would inflate exactly the cluster CO-A is
trying to bury. Recommend CO-A calibration happen against **both** the
unnormalized and pip-normalized DF numbers, not just the former.

**Surprise 5 — the Sol Ring/Mind Stone colorless-mana family is already the
single worst T1 offender's near-neighbor, and pip normalization makes it
worse under a paragraph-exact-DF gate.** Pre-normalization, `{T}: Add {C}.`
alone is already DF=451 (the corpus's single largest T1-qualifying paragraph
by exact count). Pip-normalizing merges it with `{C}{C}`/`{C}{C}{C}`/etc.
variants (the `{C}{C} ≡ {2}` equivalence, working as specified) to DF=479 —
still a 3-token paragraph, still *undefined* on the ngram scale both before
and after, but now the clear #1 offender if para_exact_df (§4a below) becomes
part of the eventual short-paragraph gate. The two rulings compound here
rather than cancel: DRAFT RULING 2 makes an already-severe short-paragraph
case slightly more severe, not less.

## 3. Recommendation table (menu, not a ruling)

All values below are measured raw DF with percentile in parentheses, drawn
from the tables printed by the two scripts. This is a menu of candidate edges,
not a chosen threshold — Captain ratifies.

| Candidate band edge | Raw DF | T1 exact-df pctile | T1 ngram-scale pctile (len≥5) | T2 pooled pctile | Rationale |
|---|---|---|---|---|---|
| Full-weight ceiling | 10 | p89.81–91.29 | p75.02–77.41 | p84.84–86.51 | Below this, nearly everything is either a true pair-level match or clearly distinctive; almost no boilerplate landmark sits this low except Vandalblast (26, still above). |
| Discount-band start | 11 | — | — | — | Mirrors above; the discount band would begin exactly where full weight ends. |
| Discount-band end / evergreen ceiling | 50 | p98.89–98.92 | p97.30–97.39 | p99.94–100.0 (population pre-filtered to ≤50, so this is the top edge by construction) | Matches the existing, already-ratified `NGRAM_DF_FLOOR=50`. Keeping the ceiling unchanged preserves every existing T2 gate/report number; only WHERE the discount starts is new. |
| Existing evergreen kill-floor | unchanged (50) | — | — | — | No evidence in this pass to move the floor itself — see Lane 1c note below. |

*(Percentiles given as [bisect-left, bisect-right] ranges since these DF values recur many times in each population — a single-point percentile would understate how much mass sits exactly at that DF. Computed directly from `experiments/out/measurement/df_distributions_raw.json`, not hand-estimated from the printed table rows.)*

**Explicit non-recommendation:** raising the flat ceiling to let the Lane 1c
six through does not cleanly exclude the M2-injected boilerplate cluster —
the two groups' DF ranges interleave (see the full ladder below), which is
exactly Surprise 2. Recommend Captain treat "where do the Lane 1c six clear"
and "where does the boilerplate/M2-injected cluster get buried" as **two
separate ratification questions**, not one shared number:

```
Raw DF ladder, ascending (landmark : DF : provenance : verdict wanted):
  Vandalblast overload reminder      : 26  : M2-injected : UNWANTED (currently passes)
  Growth Spiral vs Eureka Moment      : 54  : native      : WANTED (currently rejected)
  Garruk's Uprising vs Elemental Bond : 57  : native      : WANTED (currently rejected)
  Mystic Remora cumulative upkeep     : 60  : M2-injected : UNWANTED (currently passes as T1)
  Swiftfoot Boots equip reminder      : 64  : M2-injected : UNWANTED (currently passes as T1)
  Cultivate vs Skyshroud Claim        : 70  : native      : WANTED (currently rejected)
  Rhystic Study vs Reparations        : 77  : native      : WANTED (currently rejected)
  Rampant Growth vs Natural Connection: 119 : native      : WANTED (currently rejected)
  Deadly Dispute vs Village Rites     : 128 : native      : WANTED (currently rejected)
  Faithless Looting flashback reminder: 173 : M2-injected : UNWANTED (currently passes as T1)
```

No flat cutoff produces the "wanted stays, unwanted buries" split this ladder
needs (Vandalblast/26 is below Growth Spiral/54; Mystic Remora/60 and
Swiftfoot/64 are between Garruk's Uprising/57 and Cultivate/70). A
provenance split (M2-injected discounted independent of DF magnitude, native
long clauses judged on DF alone) is the only structure in this data that
separates the two groups cleanly. This is a genuine ruling question, not a
number to pick.

**Short-paragraph population (< 5 tokens, cannot use `ngram_df_estimate` at
all) needs its own, separate ruling before CO-A can be written as "reuse
`ngram_df_estimate`."** Population: 305 distinct texts, 3,696 cards' worth of
exact-DF mass, headlined by the four items in §1. Recomputed this subset's OWN
`para_exact_df` percentile table directly (not reused from the all-qualifying
table above, which mixes short and long paragraphs and would understate this
population's skew): p50=3, p75=5, p90=18, p95=39, p99=270, p100=451. This
subset is MORE extreme than the len≥5 population, not comparably shaped —
p99 alone (270) already exceeds every Lane 1c landmark and every M2-injected
boilerplate landmark measured in Deliverable 1/2. A single shared band
structure across both metrics is NOT supported by this data; recommend
treating the short-paragraph population as needing its OWN, separately-
ratified thresholds, not a reuse of whatever edges get chosen for the len≥5
population.

## 4. Ambiguities requiring an explicit ruling (halting loudly, not choosing)

**(a) Which DF metric governs T1 qualification?** `para_exact_df` (defined for
every paragraph, literally what `find_shared_paragraph` already keys on) vs
`ngram_scale_df` (same scale/function as T2, but undefined below 5 tokens,
which is where the four worst offenders live). DRAFT RULING 1's "applies
uniformly to T1 paragraph qualification... and T2 fragment scoring" cannot
mean *literally* the same function call for both, given the length gap. This
needs an explicit two-metric ruling (or an explicit "short paragraphs get a
different rule") before CO-A is written.

**(b) Does pip normalization run as a replacement gate or a parallel path?**
Surprise 3's guild-pair regression only happens if the pip-normalized skeleton
*replaces* today's literal-text matching. If it runs in parallel (v2.9 M1/M2
pattern: better tier wins, original text path untouched), the regression
cannot occur — same-pair guild sources keep qualifying via their unchanged
literal text, and pip-normalization only ever *adds* possible cross-color
matches, which this data shows would correctly fail to qualify anyway (shape
DF=358, over any plausible floor). Recommend the parallel-path design
explicitly, but flagging it as a recommendation, not asserting it was already
decided — SNAPSHOT-SYSTEM-CHANGE-ORDER.md and the eventual pip-slot CO should
say so explicitly if ratified.

**(c) Unhandled mana-symbol contents** — `{A}`, `{CHAOS}`, `{D}`, `{E}`,
`{H}`, `{HR}`, `{P}`, `{Q}`, `{S}`, `{TK}`, `{½}`, `{∞}` were left literal by
the pip-normalizer rather than guessed at (Acorn/silver-border markers, energy
counters, snow mana, untap symbol, Planar chaos symbol, joke-set infinity/half
mana). Verified via direct grep against the raw corpus (each maps to a real,
rare, mostly non-Commander-legal card — Acornelia, Nissa Worldsoul Speaker,
Frostpeak Yeti, Puresight Merrow, Chaotic Aether, Urza's Fun House, Mox Lotus,
etc.). Zero impact on the measurement's real findings; flagged for
completeness per halt-loudly discipline, not because any of them are load-
bearing.

**(d) The T2 provenance segmentation came out 4-way, not 3-way.** 1,226 of
57,733 qualifying 5-grams (2.1%) occur in BOTH a native paragraph on one card
and an M2-injected paragraph on another — this is precisely the
Hero-of-Bladehold-class overlap the v2.9 erratum note already ratified as BY
DESIGN. Forcing it into "native" or "M2-injected" would misstate the
measurement; kept as its own `mixed` bucket (percentile table printed in the
raw report). Not asking for a ruling here — just noting the deviation from
the literal 3-bucket instruction, since it was a documented judgment call.

---

## Reproduction

```
python3 experiments/measure/df_distributions.py   # Deliverables 1-2, ~5s
python3 experiments/measure/pip_normalization.py  # Deliverable 3, ~15s
```

Both were run twice against the unchanged `data/raw/oracle-cards.jsonl.gz`
(2026-07-03 snapshot) with byte-identical stdout and raw JSON output on both
runs (diffed, zero lines). Full tables (histograms + percentile tables for
every population, not just the excerpts quoted above) are in
`experiments/out/measurement/df_distributions_report.txt` and
`experiments/out/measurement/pip_normalization_report.txt` (gitignored,
regenerate with the commands above — nothing here was imported into or
altered in `tier_engine.py`).
