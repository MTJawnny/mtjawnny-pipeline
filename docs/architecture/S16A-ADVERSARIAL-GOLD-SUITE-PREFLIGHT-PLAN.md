# S16A Adversarial Gold-Suite Preflight Plan

Status: **PLANNED / NON-EXECUTING**  
Objective: **2 of 5**  
Fresh Claude session: **REQUIRED**  
Candidate phase: **S16A**  
Implementation authorization: **NONE**

## Mission

Design and populate an implementation-independent adversarial benchmark for **card-reading precision** before S16A parser implementation begins.

The benchmark must answer a stricter question than “did we preserve all Oracle characters?” It must test whether Foundry preserves the semantic relationships that make a Magic card executable: ownership, costs, modes, targets, conditions, sequencing, dependency, cardinality, zones, timing, and provenance.

This plan operationalizes `docs/architecture/CARD-READING-PRECISION-ACCEPTANCE.md` without changing parser code.

## Benchmark independence rule

Gold cases must not be selected primarily because the current parser already handles them. The suite should intentionally contain:

- known difficult historical shapes;
- newly discovered corpus shapes;
- official-rules edge cases;
- cards whose English looks deceptively simple but whose rules structure is not;
- hard negatives that differ by one semantic relationship.

The current implementation may be measured against the suite later, but it must not define the suite.

## Seed witnesses

The suite begins with, but is not limited to:

- **Cryptic Command** — exact modal cardinality, distinct mode selection, mode-local targeting, combined resolution without flattening all four effects.
- **Zuko, Conflicted** — triggered parent, parent-level life loss, stateful mode availability, chooser/control implications, sequenced exile/return/control transfer.
- **Monument to Endurance** — discard trigger, per-turn mode memory, exhaustion of legal choices.

These are seed witnesses, not acceptance by anecdote.

## Required structural-family census

Before choosing the final suite, mechanically census the accepted corpus for at least these families:

- `choose one/two/three/...` modal instructions;
- `choose up to N`, `choose any number`, variable/X selection;
- “same mode more than once” permissions;
- “hasn't been chosen” / “not chosen this turn/game” restrictions;
- opponent/other-player mode choice;
- pawprint modes and cost-before-effect modes;
- modal headers whose governing instruction continues after the numeric choice phrase;
- nonmodal bullet structures, die tables, station/level/class structures;
- activated abilities with multi-part costs;
- casting/additional/alternative cost language;
- payment or choice made during resolution;
- `if you do`, `when you do`, reflexive triggers, delayed triggers, linked abilities;
- replacement and prevention effects;
- multiple targets and target-sharing relationships;
- multiple independent instructions versus sequential instructions;
- variable quantities and “for each” relations;
- source/destination zone distinctions;
- quoted/granted abilities containing punctuation;
- nested reminder text;
- multi-face, split, Adventure, Room, Saga, Class, level/tier and other structured layouts present in the corpus;
- repeated identical text fragments in different abilities on one card;
- punctuation-bearing structures involving colons, semicolons, periods, em/en dashes, bullets, parentheses, quotations, question/exclamation marks and ellipses where present.

Record measured population sizes. If a requested family does not exist in the accepted corpus, say so rather than inventing a fixture population.

## Gold-case selection method

For each structural family:

1. identify the population mechanically;
2. stratify meaningful subfamilies before sampling;
3. choose representative and adversarial witnesses independently of current parser success;
4. prefer more than one witness where the family contains materially different templates;
5. include at least one hard negative or mutation target when a relationship could plausibly be flattened;
6. record why each selected card is in the suite.

There is no magic final card count. Coverage of semantic relationship classes matters more than hitting an arbitrary number. The result must nevertheless be large enough that no major structural family is represented by one boutique example if multiple materially different forms exist.

## Required gold annotation

Each card/witness should carry a machine-readable annotation with at least:

- Oracle ID / stable card identifier;
- card name for human readability;
- Oracle-text hash or corpus-version anchor;
- structural family tags;
- relevant face and paragraph coordinates;
- parent ability identity;
- expected ability delivery/type where needed;
- modal group identity and selection cardinality where needed;
- mode boundaries;
- costs/payment timing;
- actor/controller/chooser;
- target relationships;
- conditions/restrictions;
- sequential/dependent relationship edges;
- source and destination zones where relevant;
- exact/source-relative quantity constraints;
- expected provenance spans;
- explicit “must not flatten into” statements;
- rules/source evidence supporting the annotation;
- confidence / unresolved ambiguity marker.

The benchmark annotation should describe semantic truth, not implementation-specific AST field names.

## Source hierarchy

Use evidence in this order when practical:

1. Oracle text from the accepted corpus;
2. Comprehensive Rules applicable to the template;
3. official Wizards release notes/rulings for card-specific interaction details;
4. only then carefully qualified secondary/community explanation where official material is insufficient.

Community claims must not silently become canonical card-reading truth.

## Mutation-based negative controls

For selected witnesses, define deliberate corruptions that a correct semantic representation must detect. Required classes include:

- remove a cost while preserving payload;
- change `choose two` to `choose one`;
- remove “different modes” restriction;
- remove “same mode more than once” permission;
- remove stateful “hasn't been chosen” restriction;
- move a target between modes;
- convert a mode group into cumulative sentences;
- split a linked/reflexive effect into unrelated effects;
- merge independent effects;
- move a condition from parent to child or child to parent;
- change source/destination zone;
- change resolution payment into casting/activation cost;
- delete a continuation sentence;
- delete one card face;
- corrupt punctuation inside a quoted ability;
- flatten nested reminder parentheses.

A benchmark item is stronger when it includes both positive truth and a falsifiable corruption.

## Required deliverables

1. **Structural-family census** with measured populations and search method.
2. **Gold-suite manifest** in machine-readable form.
3. **Human-readable benchmark guide** explaining each family and witness.
4. **Negative-control catalog** linked to witnesses/families.
5. **Coverage matrix**: semantic relationship class × witness set.
6. **Unrepresented/unsupported-shape register**.
7. **Provenance register** for CR/release-note evidence.
8. **Draft S16A benchmark acceptance contract**, clearly NOT AUTHORIZED.

## Anti-overfitting requirements

The preflight must independently search for additional witnesses beyond the three named seeds. It should also include cards not previously discussed in Issue #1 so the future parser cannot succeed merely by acquiring card-specific exceptions.

Where possible, reserve a subset of suitable witnesses as a future holdout. Holdout selection and any random/deterministic seed should be committed before parser implementation observes labels.

## Non-goals

This preflight does not:

- implement a parser;
- change `oracle_text.py`, delivery, locality, or other source;
- declare current parser failures as automatically wrong without rules evidence;
- implement S16B similarity;
- import strategic/community judgments into Oracle truth;
- alter S10–S15 migration order;
- merge or publish anything.

## STOP conditions

STOP and report if:

- a gold annotation cannot be supported by Oracle/CR/official evidence and would require guessing;
- the accepted corpus representation is missing source material needed to specify the case;
- two official sources conflict materially and the conflict cannot be resolved from rules authority;
- selecting the benchmark requires inspecting/tuning against a future S16A implementation not yet authorized;
- a family cannot be mechanically identified and would require card-name handlisting as the primary census mechanism.

## Completion bar

Objective 2 is complete when S16A can begin with a precommitted, provenance-bearing adversarial suite that tests semantic conservation rather than raw text retention, includes falsifiable negative controls, covers the measured structural families of the corpus, and is sufficiently independent of the implementation to serve as a real acceptance benchmark.
