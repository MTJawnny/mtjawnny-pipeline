# PRODUCT REALITY AUDIT — 2026-08-09

**Captain's instruction: *"recontextualize yourself with the goals of the tool
and truly judge whether what has been done will do what the tool is set out to
do."***

This is that judgement. Every number below was **measured this session**, and
§8 gives the command that re-derives each one — because the finding of this
audit is precisely that a number nobody re-derives stops being true.

**Verdict: the T3 foundry is well-built and is not connected to the product.**

---

## 1. WHAT THE TOOL IS FOR

CLAUDE.md, line 1:

> The data pipeline for mtjawnny.com's corpus tools (**Magic Thesaurus,
> Similar Cards, Deck Finisher**).

The codebook, the axes and the delivery grammar are machinery for producing
`rule:` tags that make those three tools smarter than raw embeddings. That is
the whole reason any of it exists.

## 2. WHAT SHIPS TODAY

| | |
|---|---|
| Phase 2 (images) | **done** — 36,155 PNGs in R2 |
| Phase 3 pipeline, last **successful** build | **2026-07-05**. None since. |
| `tags/cards.yaml` — *"YOUR custom layer, the differentiator"* | **15 lines** |
| The three named corpus tools, on the site | **none exist** — 12 one-word card pages + a life-counter table |
| Cards carrying ≥1 derived tag | **6,275 of 32,557 — 19.3%** |
| Full-corpus pass | **`STOPPED_FOR_CAPTAIN` since 2026-08-02** |
| Review tool `foundry_review.html` | untouched since **2026-07-17** |

## 3. THE CENTRAL FINDING — THE FOUNDRY IS A CLOSED LOOP

**Nothing the foundry produces reaches a shipped card.**

* Every importer of `foundry_shape_extractor` — **13 of them** — is an audit,
  a census, a probe or a regression harness. `foundry_emit.py`,
  `foundry_det_pass.py`, `foundry_codebook.py`, `foundry_membership_move.py`
  and **every file in `pipeline/`**: zero references.
* **`tier_engine.py` reads no foundry output at all** — no `codebook.json`, no
  `det-patterns-v2.json`, no axes. It emits exactly **one** `rule:` tag,
  `rule:turn-scoped`, which it derives itself.
* So neither the **403-axis codebook (7,930 memberships)** nor the **45
  ratified DET patterns** are wired to anything a user can see.

The delivery classifier classifies, and its output is consumed only by tools
that check the classifier.

**This is a MISSING WIRE, not wasted work.** The inventory is real and mostly
good. But until the wire exists, every foundry session is speculative
inventory, and no audit in the repo can tell the difference.

## 4. WHERE THE EFFORT WENT

Since 2026-08-01: **204 commits.**

| touched | file-touches |
|---|--:|
| `docs/` | 429 |
| `experiments/` | 200 |
| `CLAUDE.md` | 43 |
| **`pipeline/`** | **0** |

**48 distinct `experiments/foundry_*` files edited. Zero `pipeline/` files.**

## 5. THE 2026-08-09 SESSION, JUDGED ON ITS OWN TERMS

**The CR refresh was worth doing.** Captain flagged it, the pipeline derives
from the CR at run time by design, it was cheap, and it found real encoding
damage in the new file. Keep it. `docs/CR-REFRESH-2026-08-09.md`.

**W4 does not survive this audit.** 1,012 lines routed to `static` in a
classifier nothing consumes — and `static` appears as a slug prefix on **1 of
403 active axes**, so even after the wire exists this slot value is nearly
unused.

**And the metric was the wrong direction of the right number.** `--gaps`
reports lines *needing vocabulary*. Routing a line to `static` **removes it
from that report without tagging a single card**. The decidably-static queue
went 4,370 → 3,358 because lines were labelled, not because coverage moved. For
a tool bottlenecked at 19.3% coverage, that makes the backlog *look* smaller.

**Every gate run answered "did I break anything?" None could answer "does this
reach a card?"** That is the gap this document exists to close.

## 6. WHAT IS GENUINELY SOLID — KEEP ALL OF IT

Gate 2's twelve negative-controlled checks · `foundry_probe` · the
conservation, visibility and ground-truth audits · `foundry_cr.py` and its
edition diff. These caught **four** defects in the 2026-08-09 session alone,
including one the routing diff by itself would have scored a clean pass.

This is good machinery pointed at the wrong altitude. It will pay for itself
the moment it is guarding something that ships.

## 7. ONE TENSION THAT NEEDS CAPTAIN

Grammar §1: *"DELIVERY … OMITTED for spell abilities … **Everything non-spell
is MARKED**."*

Measured: **233 of 403 active axes carry no delivery prefix at all, holding
6,911 of 7,930 members (87%)** — including `rule:enters-tapped` (686 members),
which is not a spell ability.

So either most of the live codebook is non-conformant with §1, or §1's marking
rule is not what the codebook actually practises. **Nobody would notice**,
because nothing validates the codebook against the delivery classifier — which
is finding §3 showing up as a second symptom.

## 8. RE-DERIVE EVERY NUMBER ABOVE

A carried-forward count is not a measurement, and that rule applies to this
page hardest of all. One paste:

```bash
# §2 coverage — the number that matters
python3 - <<'EOF'
import json, sys, collections; sys.path.insert(0,"experiments")
import foundry_common as fc
cb = json.load(open("experiments/out/foundry/codebook.json"))["axes"]
active = {k:v for k,v in cb.items() if v.get("status")=="active"}
cards,_,_ = fc.load_corpus_gated()
covered = {m.get("oracle_id") if isinstance(m,dict) else m
           for v in active.values() for m in (v.get("members") or [])}
print(f"cards {len(cards)}  tagged {len(covered)}  "
      f"{100*len(covered)/len(cards):.1f}%  axes {len(active)}")
EOF

# §3 the closed loop — expect ONLY audits/censuses/probes
grep -rn "import foundry_shape_extractor" --include="*.py" experiments/
grep -c "out/foundry\|codebook\|det-patterns" experiments/tier_engine.py   # expect 0
grep -on '"rule:[a-z-]*"' experiments/tier_engine.py | sort -u             # expect 1

# §4 where the effort went
git log --since=2026-08-01 --name-only --format="" | grep -v '^$' \
  | sort -u | grep -c "^pipeline/"                                         # expect 0

# §2 what ships
gh run list --limit 5 ; wc -l tags/cards.yaml
python3 -c "import json;print(json.load(open('experiments/out/foundry/corpus_pass_run1_classification.json'))['STOPPED_FOR_CAPTAIN'])"
```

## 9. RECOMMENDATION — ORDERED

**Stop W4.** The remaining 3,358 decidably-static lines are the same trade.

1. **WIRE THE CODEBOOK INTO `tier_engine`.** The missing link. Take this first
   if you take one thing: it converts existing inventory into product and
   immediately measures whether the 7,930 memberships improve neighbours at
   all. If they do not, that is the most valuable negative result available.
2. **Unblock `A15-VOCAB-01`** — ONE Captain decision, open since 2026-08-02,
   gating the full-corpus pass that takes coverage from 19.3% toward the whole
   corpus. 209 rows, 2 slugs; its own recommendation is option B (rename to
   existing ratified vocabulary, no vocabulary expansion).
3. **Revive `foundry_review.html`** — `SESSION-START-PROCEDURE.md` has named
   this *"the highest-leverage unstarted work"* since 2026-07-17, and names
   ratification throughput as **the** bottleneck. It has been dark for 23 days.
4. **Get a green pipeline build** — the last one was 2026-07-05.

## 10. THE DURABLE FIX — MAKE THIS A TOOL, NOT A PARAGRAPH

`docs/SYSTEM-SELF-TEST-2026-08-09.md` measured the house's own record:
**every defect class that got a TOOL stopped recurring; the one class that got
a paragraph reached 21 instances.**

This finding got a paragraph. It will decay the same way.

**The tool it wants is a REACHABILITY check** — from the `pipeline/` entry
points, trace what is actually read, and report which foundry artifacts reach a
shipped card and which do not. Wired into `foundry_gate2.py` as a reporter, it
would make "this work reaches nothing" a visible number every session instead
of a discovery someone makes once a month.

**Not built here on purpose** — it is new scope and it is the next session's
call, not this one's. But it is the highest-leverage item on this page after
§9.1, and §9.1 is what makes it measurable.
