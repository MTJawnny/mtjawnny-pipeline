# SESSION HANDOFF — 2026-08-03

Supersedes `SESSION-HANDOFF-2026-08-02-EVE.md`. **Zero API calls all session.
Cumulative arc spend unchanged at $90.51 / $140.**

## 0. START HERE

**`docs/SESSION-START-PROCEDURE.md`** — five gates. Gate 3 is mechanical:
`python3 experiments/foundry_slug_dossier.py <slug>` **before** calling
anything defective.

---

## 1. Live state

| | |
|---|---|
| codebook | **533 axes** · **347 active** · 8,056 members |
| sha256 | `999a9021f30789cd068e0f43ad47a959043480527d190bb7cbdf2c726c9ee9e5` |
| lint | clean |
| family sweep | **6 blocking** (unchanged for two days) |
| definition drift | **35 findings** — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 |

`codebook.json` is gitignored; `experiments/out/foundry/backups/` is the ONLY
rollback path and is **local-only**. Six backups written this session, each
readback-verified.

---

## 2. The through-line — five rulings that changed the model

Everything else this session is downstream of these.

1. **§6a — THE PRINTED WORD IS THE CLAIM.** *"Game logic is game logic. If
   something targets, it targets. If it does not target, it does not target."*
   Templating words are CR terms of art, hardcoded to their mechanic, and are
   **axis identity, never a facet**.
2. **§6b — SHAPE vs JOB.** Shape (printed text, zero ambiguity) is the child;
   job (play outcome, interpretive) is the parent. Per-shape axes are minted
   **freely, even at n=1**. Two axes merge only when printed shapes are
   *identical* — similar outcome is grounds for a shared parent, never a merge.
   Worked case: The One Ring vs Grand Abolisher — same job, different anchor.
3. **§6c — `mass-` RETIRED.** The CR prints "mass" **zero times in 10,060
   lines**. It was a job word in the child layer, and it was hiding the
   symmetric/one-sided distinction on three axes. 12 renamed; `mass` survives
   as *parent* vocabulary only.
4. **§8.4a — `role` is ONE umbrella.** No card conditions on Role type; CR
   205.3h makes Role a single subtype; CR 303.7a's state-based action is
   type-agnostic. Resolves **CDR-11**. Carries a standing reversal condition.
5. **S4a — PARENT EDGES ARE UNRANKED.** *"Neither one wins, they live both
   simultaneously."* No primary parent, no weighting. Monstrous Rage is a combat
   trick **and** an enchantment card. **"Parent tree" is a misnomer** — it is a
   lattice.

---

## 3. What was built

| thing | what it does |
|---|---|
| `foundry_slug_dossier.py` | slug → every ruling touching it, **following rename chains**. 88% of active axes carry a ruling; **23% have them filed under a former name**, where a live-slug grep finds nothing. |
| drift check **C4** (a/b/c/e/f/g/h) | enforces §6a. First run: **93 memberships across 22 axes**; now 11. |
| `foundry_cr_checks.py` → `cr-checks.json` | **262 CR terms** — the check set is now *derived*, not discovered after each failure. `era_variants` is the load-bearing field. |
| `cr-predefined-tokens.json` | all 21 CR 111.10 tokens with granted abilities parsed — makes composed effects **derivable** |
| `seeds` + `scope_edits` ops | seed members onto a newly modelled mechanic; correct a scope field |

Executed: tier-3 (D1–D12+M), tier-4 part 1, C4 parts 1–2, the mass walk, Role
shapes. **6 codebook mutations, all backed up and gate-verified.**

---

## 4. WAITING ON CAPTAIN

- **Tier-4 calls 3a/3c/4** — 6 new slug strings await naming ratification
  (`docs/TIER-4-DECISION-SHEET-2026-08-02.md` §7b), plus the ownership-split
  scope question (§7a) — **answered in principle by §6a, not yet executed**.
- **Tier-4 call 6 / §S4** — ruled YES; the **preprocessor fix is not built**.
  44 DET memberships still rest on token reminder text.
- **CR vocabulary batch** — ratified. `create-token-clue` (124 hits) is
  **patterned but not applied**; the §2.5 sample gate has not been run.
- **Token-type vocabulary gaps** — Incubator, Army, face-down 2/2 have no
  object vocabulary.
- Carried: **D13** (by-power family, still a sweep blocker) · **§S** (88
  Alchemy memberships) · **CDR-01** · `begin-combat-trigger` + Saga-chapter
  delivery vocabulary (now blocking 3 Role cards).

---

## 5. Next work item

**The 40 uncovered CR keyword actions** (`docs/CR-COVERAGE-PACKET-2026-08-02.md`).
Lead with `investigate` — 132 cards, and `create-token-clue` needs **no
ratification**: `clue` is ratified vocabulary, batch-5 D14 named the slug as a
future sibling, and §11 self-instantiates it.

Then **nested effects**, which Captain named as the core difficulty and which
is measured: **1,273 gate-passing cards carry a nested ability, only 23% on any
axis.** 768 are abilities *granted to another permanent* — the biggest bucket,
against `temporary-keyword-grant`'s 40 members. §2's created-ability rule is
already the law for this; it has never been applied at scale.

---

## 6. The number to carry forward

**Classifier accuracy on Roles: 33 of 39 (85%)** — on a closed set of 39 cards
with completely regular templating. Six were real distinct shapes a naive
reading flattens, two of them created-ability cases.

Third measured instance of the same thing: §S4 (154→90→**44**), C4f (flagged
~50 **correct** axes), Roles (85%). **The cards are unambiguous; the encoding
of them is not.** Hand-verify closed sets. When a check disagrees with a
ratified list, suspect the check — it has been wrong every time this arc.
