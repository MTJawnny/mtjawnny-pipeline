# S7's "ZERO-COST NEXT STEP" IS NOT RUNNABLE AS WRITTEN (2026-08-05)

**STATUS: FINDING, with a proposal. Nothing was built and nothing was changed.**
Raised because `SESSION-HANDOFF-2026-08-04-EVE.md` §0 instructs: *"If something
this handoff promises is missing, say so out loud rather than proceeding past
it."* This is that.

---

## 1. The item, carried unexamined across three handoffs

> **`PARENT-LAYER-OPENING-PACKET-2026-08-04.md` §6** — *"Run
> `experiments/measure/family_tree_evidence.py` against the five populated
> candidates. **It already implements the substitute lens, the Tagger
> cross-reference and exemplar panels**, it is fixed-seed and
> determinism-verified, and it is the **S7 gate those candidates have never been
> through.** … it costs nothing but CPU."*

Repeated as a ready-to-run, zero-token work item in
`SESSION-HANDOFF-2026-08-04.md` §8a.4, `SESSION-HANDOFF-2026-08-04-EVE.md` §5.5,
and — before this finding — `SESSION-HANDOFF-2026-08-05.md` §4.2. **I copied it
forward myself without checking it, which is the same failure it documents.**

## 2. It cannot be run. Three independent reasons, all measured

### 2a. The tool is hardcoded to a DIFFERENT population

`family_tree_evidence.py` measures the **v1 derivation patterns** of
`DERIVED-TAG-LAYER-SPEC.md` (`restricts-cast`, the Grand Abolisher family). Its
own docstring says so: *"Implements DERIVED-TAG-LAYER-SPEC.md's v1 derivation
patterns as a THROWAWAY script."*

| checked | result |
|---|---|
| takes command-line arguments | **no** — `main()` takes none, there is no `argparse` |
| references `parent`, `candidate`, `payoff` | **zero** occurrences |
| reads `codebook.json` | **zero** occurrences |

So *"running it per candidate"* is **not an operation the tool supports.** It
would run and produce its usual output about `restricts-cast`, which says nothing
about `sacrifice-payoff`.

### 2b. "Deck co-play" — the FIRST named component — has no data source

The packet defines the lens at §2: *"the **substitute lens** — **deck co-play**,
Tagger cross-reference, exemplar panels."* And the only gloss the term has
anywhere else is `PARENT-TREE-CANDIDATES.md`:69/78 — *"Substitute family (**decks
run** Stasis **OR** stun packages)"*, i.e. cards a deck chooses *between*.

**This repo has no deck-level data at all.**

```
data/raw/  ->  oracle-cards.jsonl.gz   oracle-tags.jsonl.gz   rulings.jsonl.gz
```

No decklists, no EDHREC, no co-play matrix, and nothing in `pipeline/` fetches
any. Deck co-play is **not currently measurable**, by this tool or any other.

### 2c. "Substitute lens" is defined in one parenthetical and implemented nowhere

`grep -rn "substitute lens" docs/` returns **6 lines across 4 documents**, all of
which *invoke* it; none defines the measurement. Every `substitute` match in the
code is `self-name-**substituted**` — the string-replacement sense, not the lens.

**There is no implementation of S7's check anywhere in the repository.**

## 3. What IS true, and it is two thirds of the lens

The packet's claim is not empty — it is **2 of 3 right**, and both halves are
genuinely reusable:

| component | status |
|---|---|
| **Tagger cross-reference** | **AVAILABLE.** `experiments/out/card-tags.json.gz`, **35,550 cards** tagged; `te.load_card_tags` / `build_tag_index` / `compute_tag_stats` all work over any population |
| **exemplar / near-miss panels** | **AVAILABLE.** `family_tree_evidence.py` PART 4 already produces named match lists; the technique is population-agnostic |
| **deck co-play** | **UNAVAILABLE** — no data source (§2b) |

## 4. PROPOSAL — run S7 in the form the data permits, and say which third is missing

**Not built here.** This is a measurement, so it needs no ratification and a
future session may simply do it — but the *design* question in §5 should be
answered first, because getting it wrong is how this project manufactures false
findings.

1. **A new script**, `experiments/measure/parent_candidate_evidence.py`, taking
   the candidate parents and reading their children's member sets from
   `codebook.json` — the parameterization `family_tree_evidence.py` lacks.
2. **Tagger cross-reference per candidate**: which Tagger tags blanket the
   candidate's union-of-children population, with idf. This is the redundancy
   signal, and `FAMILY-TREE-EVIDENCE.md`'s anti-laundering guard applies
   unchanged — *corpus behaviour and exemplar cards outrank tag co-occurrence
   wherever they disagree.*
3. **Exemplar / near-miss panels per candidate**, fixed-seed.
4. **Deck co-play reported as UNMEASURED**, never silently omitted. A gate that
   quietly drops a third of its own definition is the failure this document is
   about.

## 5. THE DESIGN QUESTION THAT MUST BE ANSWERED FIRST — for Captain

**What replaces deck co-play?** It is the only component that speaks to
*substitution*, and CLAUDE.md forbids the obvious stand-in outright:

> **"Same-card co-occurrence is the WRONG test for substitute families."**

and the packet's own §2 explains why in this exact context:

> *"Near-zero overlap means the children are cleanly **disjoint** … it is
> precisely **why** a parent earns its keep. S6's whole promise is **'Same Job,
> Different Words'**: the parent groups cards that share **no** child."*

So the two candidate answers are:

| option | consequence |
|---|---|
| **A. Accept a 2/3 lens** — Tagger + exemplars only, deck co-play reported unmeasured | S7 becomes satisfiable today at zero cost. It measures *shared job by taxonomy*, which is weaker than substitution but is real evidence |
| **B. Acquire deck data** | The only thing that measures actual substitution. **A Captain decision**: it is a new external data source, an outward-facing fetch, and it interacts with the locked rule *"no card data in git, ever."* |

**Recommendation: A now, B logged.** Option A is measurable, costs nothing, and
gives the five candidates real evidence they have never had. Option B is the only
path to the lens as originally conceived and should not be improvised into
existence by a session at 2am.

## 6. What this proves

**A work item can rot exactly like a ratified standard with no caller.** This one
named a real file, a real gate, and a real cost estimate — every surface signal
said "ready to run" — and it had never been executed even once, so nothing ever
contradicted it. It survived three handoffs, including one I wrote.

**Gate 3b greps for prior art on a topic. Nothing greps a work item for
feasibility.** The cheapest possible check would have caught it:
`python3 <the named script> --help`, or `grep -c parent <the named script>`.

**Standing suggestion:** when a handoff promises a command, the next session
should run it *first* — before planning around it. A command that cannot run is
found in one second and costs a session otherwise.
