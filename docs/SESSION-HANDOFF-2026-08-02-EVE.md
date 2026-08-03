# SESSION HANDOFF — 2026-08-02 (EVE)

> ⚠ **SUPERSEDED — this is NOT current state.**
> The current handoff is **`docs/SESSION-HANDOFF-2026-08-03.md`**.
> Start at **`docs/SESSION-START-PROCEDURE.md`**.

Supersedes `SESSION-HANDOFF-2026-08-02-PM.md` for current state. That file
remains the accurate record of the CDR-09 walk and the tier-1/2 re-audits.

**Zero API calls. Cumulative arc spend unchanged at $90.51 / $140.**

---

## 0. START HERE

**`docs/SESSION-START-PROCEDURE.md`** — five gates, short by design. It is new
this session and it exists because "read more docs" was not working as an
instruction. Gate 3 is now mechanical:

```
python3 experiments/foundry_slug_dossier.py <slug>
```

Run it **before** calling anything defective. Measured this session: **291 of
328 active axes (88%) carry a ruling**, and **77 (23%) have those rulings filed
under a former name**, where a grep of the live slug returns nothing.

---

## 1. Live state — measured at session end

| | |
|---|---|
| codebook | `foundry-codebook/2` · **497 axes** · **328 active** · 7,875 members |
| sha256 | `c184e76eb2109535114647545ee6e2ba7c79964e5ccd41a829bbb9f83d376e18` |
| lint | clean |
| family sweep | **6 blocking** (unchanged all day) |
| definition drift | **25 findings** (C1a 1, C1b 1, C2 16, C3 7) — down from 27 |
| spend | $90.51 / $140 |

`codebook.json` is gitignored. `experiments/out/foundry/backups/` is the ONLY
rollback path — and it is **local-only**; the push this session covered code
and docs, not the codebook.

---

## 2. What happened this session

1. **Tier-3 re-audit executed** (D1–D12 + M, Captain-ratified). 23 axes / 69
   member-reads → 14 axes with findings. 6 new axes, 2 renames, 12 member
   moves, 2 drops, 8 definition edits, 4 quotes.
   Record: `docs/TIER-3-DECISION-PACKET-2026-08-02.md`.
2. **D3f ruled GENERAL** — *"D3f stands as written, general."* A `{T}` in an
   activated cost is axis identity on **every** `activated-` axis, not just the
   haste case. This will keep firing as the re-audit descends.
3. **Grammar §7 gained** `sacrificed-creature-toughness`, and the
   `attacker-count` vs `creature-count` split is now recorded as load-bearing.
4. **Tier-4 audited, NOT executed.** 20 axes / 80 member-reads → 12 axes with
   findings. Awaiting rulings.
5. **The slug dossier built** (§0) and the session-start procedure written.
6. Pushed to `origin/main` — 70 commits, the whole foundry arc's first push.

---

## 3. WHAT IS WAITING ON YOU

### 3a. Tier 4 — six calls, ready to rule

**`docs/TIER-4-DECISION-SHEET-2026-08-02.md`** is the decision surface: six
questions, each with a default. Answer format is `"all defaults"` or
`"all defaults except 4 — do X"`. Evidence for every line is in
`docs/TIER-4-DECISION-PACKET-2026-08-02.md` under the same E-numbers.

| call | what it is |
|---|---|
| 1 | move 5 members to axes that already exist |
| 2 | drop 4 members that belong nowhere, ledger them |
| 3 | correct 4 definitions that contradict their members |
| 4 | four new axis names — the only call creating vocabulary |
| 5 | two evidence quotes (mechanical) |
| 6 | **§S4** — does the created-ability rule bind DET patterns? |

**Call 6 is the one with consequences.** 44 DET memberships were written off
text belonging to **tokens the card creates**. Tireless Provisioner is filed as
producing mana and gaining life; it does neither — the Food and Treasure
*tokens* say that. 37 more sit on "activate only as a sorcery" because a Map
token they create says so, while having no activated ability at all. All are
`class=rule-derived`, full weight, nothing downstream discounts them.

Root cause is known: the F2 walk fix widened those patterns to paragraph scope
(`[^\n]*`), and reminder text lives on the same line. The fix belongs in the
**producer** (G4), and it must **preserve keyword reminder text** — Unearth and
Encore genuinely do carry "Activate only as a sorcery" as their own ability
(CR 702.140). That boundary is why the number is 44 and not 154.

### 3b. Carried, still unruled

- **Tier-3 D13** — `evasion-vs-high/low-power-blockers` vs Q8's ratified
  `cant-be-blocked-<restriction>` grammar. Still one of the 6 sweep blockers,
  and it collides with ADD-01's session-4 DET plan. It is a merge-or-extend
  vocabulary call, not a rename.
- **Tier-3 §S** — 88 Alchemy-variant memberships, 48 with the paper twin
  already on the same axis. Step 1 is whether the paper-preference binds
  codebook membership at all.
- **Tier-3 D14** (A-Social Climber) — subsumed by §S.
- **`combat-trigger` / `begin-combat-trigger`** — not in §2's closed DELIVERY
  vocabulary, exposed by tier-3 D2, never carried a recommendation.
- **CDR-01** — n=1 → `deferred`. Still unruled, and it would retroactively
  touch the six axes created today (all entered `active`, matching the tier-2
  precedent).
- 6 sweep blockers · 6 family rulings · S1–S7 · CDR-02/04/06.

---

## 4. Known defects in our own tooling

- **`renames` carries the old scope forward.** `foundry_membership_move.py`'s
  rename op accepts a `definition` override but **not** a `scope` one. It bit
  this session — tier-3 D7's rename kept `scope: opponent-stuff`, the exact
  claim D7 ruled false, and needed a follow-up spec. **Fix before the next
  tier.** (`scope_edits` was added this session and works; the gap is
  rename-specific.)
- **`foundry_reaudit.py` has no repeatability test**, contrary to what the PM
  handoff claimed. Three auto-flags only: NO QUOTE, QUOTE NOT VERBATIM,
  CREATED-ABILITY RISK. The D3f `{T}` test is judgment-only — and now that D3f
  is general, that is a real gap worth closing.
- **`foundry_review.html` dark since 2026-07-17.** Unchanged, and today
  restated the case: two sessions produced more findings than could be ruled.
  **Ratification throughput is the bottleneck, not finding-generation.**

---

## 5. Next work item

**Tier 5** — `python3 experiments/foundry_reaudit.py --min-members 5 --max-members 5`.

Do not start it before tier 4 is ruled. Tier 4's findings are still uncommitted
to the codebook, and tier 5 will re-derive against a codebook that is about to
change.

Trend across four tiers, which is the argument for continuing:

| tier | axes | member-reads | axes with findings |
|---|--:|--:|--:|
| 1 (0–1 members) | 23 | 19 | 11 of 19 reads |
| 2 (2) | 68 | 136 | 10 (15%) |
| 3 (3) | 23 | 69 | 14 (61%) |
| 4 (4) | 20 | 80 | 12 (60%) |

Per-member defect rate is falling (tier 3: 30% → tier 4: 19%) while the axis
rate holds — more members means more evidence keeping a definition honest.
**Three tier-4 axes came back clean specifically because of earlier rulings**
(`etb-surveil`, the tier-2 D2 merge, batch-6 D3's dropped clause). That is the
first evidence the walk is converging rather than only accumulating.
