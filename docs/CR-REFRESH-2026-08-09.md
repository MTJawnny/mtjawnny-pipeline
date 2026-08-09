# CR REFRESH — DONE. 2026-06-19 → 2026-08-07, by normalization.

**Landed 2026-08-09.** `docs/NEXT-SESSION-CR-NORMALIZATION.md` is the spec this
executes; this is the record of what happened, what moved, and the two things
that need Captain.

Commits: `2733326` (the loader + the fidelity diff) · `675a58b` (every parser
pointed at the new edition).

---

## THE HEADLINE

**Zero lines of routing moved.** 61,383 ability lines compared, 0 moved, 0
appeared, 0 vanished. Gate 2 green. The refresh was the safest change this
project has made, and the reason is measurable rather than lucky: of the 3,144
rules the two editions share, **3,130 are byte-identical**, and of the 14 that
were reworded, **none is a rule any parser here reads.**

Two numbers moved, both real rules changes, both named:

| | before | after | why |
|---|--:|--:|---|
| CR 702 keyword names | 193 | **194** | CR 702.195 **Storied**, added by WotC |
| keyword homes | 150 | **151** | Storied → `static`, from 702.195a's own sentence |

Everything else on the pinned acceptance test reproduced **exactly**: card
types 15 · subtypes 550 · supertypes 5 · ability words 61 · zones 7 · damage
recipients 4 · self-reference nouns 568 · §2 tokens 64 · ability lines 61,383 ·
deliveries 61,960 · `unclassified-trigger` 481 · active axes 403 · members
8,810.

---

## HOW IT WAS BUILT — one loader, and the file untouched

`experiments/foundry_cr.py` is the only place that knows how a CR file is
formatted. The 2026-08-07 edition writes `**205.2a.**` where every parser here
keys on `205.2a`; the loader strips that at read time and the file stays
pristine, exactly as ratified 2026-08-09. Five read sites now go through it
(`foundry_cr702_classes`, `foundry_cr_checks`, `foundry_family_sweep`,
`foundry_keyword_buckets`, `foundry_shape_extractor`).

**Every transformation is a PURE DELETION of markup characters**, which is what
makes the conservation law statable: the normalized line must be a subsequence
of the raw line whose only dropped characters come from `*#>. `. It is asserted
per line, so one damaged line halts the run, and it is negative-controlled
against substitution, insertion, reordering and a greedy span — the class of
damage a reassembly check cannot see.

The content guard names **nine rule-line openings the parsers actually depend
on** rather than counting lines. It earned its keep immediately: it caught
three of my own wrong anchors on the first run (`120.1 ` and `400.1 ` are
written `120.1.` and `400.1.`; `113.3a` opens *"Spell abilities are"*, not
*"A spell ability"*). A count guard would have passed all three.

**The CR is now tracked in THIS repo** rather than reached across into the site
repo's gitignored `docs/`. That is the durable win: the next refresh is a diff.

---

## HOW THE ZERO WAS VERIFIED — because a zero is the easiest wrong answer

Three separate things had to be true, and each was checked rather than assumed.

**1. The loader is a no-op on the PRIOR edition.** New code + the June CR
reproduces 61,960 routed lines / 150 keyword homes / 15,430 unrouted rows,
exactly. That isolates the rules change from my edit — without it, "0 moved"
could mean the two errors cancelled. `MTJ_CR_PATH=<file>` is what makes this
possible and is the reason it exists.

**2. THE FIRST DIFF WAS BLIND, AND THE SECOND ONE WAS NOT.**
`cr_action_terms()` reads `docs/cr-checks.json` — a **generated artifact**, not
the CR — so the first routing diff never exercised the CR 701 change at all and
its zero was meaningless. Regenerated: 262 → 264 terms, exactly `recruit`
(701.70) and `storied` (702.195), nothing renumbered. Then the diff was re-run.

> Same family as *"a derived map is not the list it was derived from"*. The
> tell was that the map is keyed on CR rule numbers, so it reads like the CR.

**3. `recruit` really did enter `TRIGGER_VERB`** — asserted, not inferred from
the zero. It moves nothing because all **3** corpus lines printing the word
carry it inside a **card name** (Recruit Instructor ×2, Freedom Fighter
Recruit), never as a trigger-condition verb, and all three were already routed
correctly. `enduring story`: **0** lines. `storied` appears on 1 line, also a
card name, and correctly does not enter `TRIGGER_VERB` because CR 702.195a
makes it a keyword ABILITY, not a CR 701 keyword ACTION.

The standing `family_sweep` failure was compared **finding by finding** against
the old CR, not by count: 249 findings / 6 blocking, and the sets are identical.

---

## THE MANA CHANGE — found, and narrower than the blast radius feared

Captain, 2026-08-09: *"there's a new CR that changes how mana abilities work."*
It is **CR 605.1a**, and here it is:

> **prior (2026-06-19)** — An activated ability is a mana ability if it meets
> all of the following criteria: it doesn't require a target (see rule 115.6),
> it could add mana to a player's mana pool when it resolves, and it's not a
> loyalty ability.
>
> **new (2026-08-07)** — …it's not a loyalty ability (see rule 606, "Loyalty
> Abilities"), **and its cost and effect don't move any card to or from a
> library. Do not take into account replacement effects that may apply, other
> than self-replacement effects, when evaluating these criteria.**

**IT HAS NO CODE PATH IN THIS REPO TODAY, AND THAT IS THE FINDING.** Nothing
parses CR 605.1a. Grammar §2 cites it to *explain* a §1 qualifier on
`ability-activated-trigger`, and that qualifier is matched as printed card text
(*"that isn't a mana ability"*) — cards still print those words, so the routing
is unchanged. What moved is the game's definition of which abilities qualify,
which this pipeline does not model.

The rest of the measured blast radius stands, **re-verified by the edition diff
rather than asserted**: CR 106.4, 106.6 and 106.12 are all byte-identical
across the two editions, so `tapped-for-mana-trigger` (58 lines),
`add-mana` (1,746) and `restricted-purpose-mana` (217 members) are untouched —
including the two ratified hours before Captain's notice. `CR-REFRESH-MANA-
ABILITIES.md` measured the right rules; the answer is simply "nothing moved".

---

## THE CR-LAG REGISTER DID NOT SHRINK — and both entries were lying about why

`chorus` and `N or less` both said *"the real fix is to refresh the CR
snapshot."* **The refresh happened and fixed neither.**

* CR 205.3k, byte-identical: *"The spell types are Adventure, Arcane, Lesson,
  Omen, and Trap."* `Chorus` is still absent while the corpus prints it.
* CR 706.3a, byte-identical: still the three forms, still no `N or less`.

So the lag was never a stale snapshot — **the CR itself is behind the printed
cards**, and both entries are permanent until WotC catches up. Both comments
are corrected in place, because a register entry naming a fix nobody has done
reads as unstarted work.

**And the direction has now inverted too.** CR 702.195 Storied and CR 701.70
Recruit exist in the rules with **0 attested corpus lines** — the corpus
snapshot is older than the CR. Not a defect either way; worth knowing that both
sources can lead.

---

## THE OTHER RULES CHANGES, for the record

Reworded 14 · added 18 · removed 9. Beyond 605.1a, nothing touches a rule this
pipeline parses:

| area | what changed |
|---|---|
| **310 / 704.5v–aa** | battle protector rules restructured and renumbered; 310.8 split so non-Siege battles get their own defense-0 rule; 704.5 shifted one letter along, adding **704.5aa** |
| **506.4** | a permanent is now removed from combat if its *"controller **or protector**"* changes |
| **701.70** | **Recruit**, a new keyword action |
| **702.195** | **Storied**, a new static keyword ability, plus the *"enduring story"* designation |
| **122.1j** | hone counters on Equipment |
| **206.3a** | see the finding below — this one is not a rules change |
| **722.3a** | a comma became a period |

---

## ⚠ DECISION SHEET — two items, and neither blocks anything

### D-CR-1 · The new file is a DERIVATIVE and it has measured encoding damage

The `_LLM.md` filename was flagged in the spec as *"possibly a derivative"*.
Its own front matter settles it — `format: "LLM-optimized Markdown"`,
`source_fidelity: "content preserved; formatting normalized"` — so it is a
reformatting, not WotC's raw release. The spec said to diff it against the
official text first. That was done the only way available offline, and the
result is mostly reassuring and partly not:

**Reassuring:** 3,130 of 3,144 shared rules are **byte-identical** to a
WotC-derived plain-text edition, including every curly apostrophe. **Zero**
rules differ by whitespace or quote characters alone — the signature of a
reformatter touching content.

**Not reassuring:** **CR 206.3a carries 7 mojibake characters** — UTF-8 bytes
decoded as Latin-1 — in City in a Bottle's Arabian Nights name list:

```
Dandân -> DandÃ¢n     El-Hajjâj -> El-HajjÃ¢j    Ghazbán -> GhazbÃ¡n
Junún  -> JunÃºn      Juzám     -> JuzÃ¡m        Khabál  -> KhabÃ¡l
Ring of Ma’rûf -> Ma’rÃ»f
```

Measured, not sampled: `á â ú û` occur in the entire CR **only** inside 206.3a,
all four are gone from the new file, and the prior edition has **zero**
mojibake anywhere. A second, unrelated non-uniformity: **704.5aa is unbolded**
in the new file — the reformatter's own pattern misses two-letter subrules.

**Handled the way CLAUDE.md already handles a vendored-CR discrepancy:** a
declared register naming its evidence, and **anything outside it HALTS**
(`foundry_cr._KNOWN_ENCODING_DAMAGE`, negative-controlled four ways). Nothing
here parses CR 206, so the damage is inert today.

**Not repaired, on purpose.** The mojibake is mechanically reversible and the
prior edition holds the correct text — but repairing it is a **content**
mutation at read time, and what was ratified 2026-08-09 was a **formatting**
one. Captain's call:

| | |
|---|---|
| **a. Leave it** | current state. Declared, guarded, inert. Costs nothing until something reads CR 206 — and the resolver (3.11) exact-matches card names, so `Juzám Djinn` is a name it will eventually meet. |
| **b. Repair the 7 at read time** (recommended) | a declared table of 7 characters, each verified against the 2026-06-19 edition, applied by the loader. Small, evidenced, and it makes the CR trustworthy as ground truth for names. |
| **c. Replace the file** | fetch WotC's official 2026-08-07 release and re-run the edition diff against it. Strictly the best answer, and the only one that also catches damage in the 14 rules this diff cannot adjudicate. Needs a download. |

**My read:** (c) is right if a download is easy, (b) if not. But this is a
one-rule cosmetic defect in a file that is otherwise 99.6% verified, so it
should not hold anything up.

### D-CR-2 · CR 605.1a — do we model "is a mana ability" at all?

Today: no, and nothing needs it. The new clause changes which real abilities
are mana abilities; every mana-related token here is matched from printed text.

**Recommendation: no action, record and move on.** Raising it because the
CR-REFRESH doc predicted this rule would move a *premise*, and the honest
answer is that the premise it names is not encoded anywhere — which is itself
worth knowing before someone builds on the assumption that it is.

---

## ONE CORRECTION TO THE SPEC

`NEXT-SESSION-CR-NORMALIZATION.md` FACT 2 states the vendored edition has
**2,167** rule-numbered lines. Measured: **3,153**. The new edition has 3,162,
not 3,161 — the missing one is the unbolded 704.5aa. The 3,161 was a count of
*bold markers*, which is not the same question.

A carried-forward count in a spec, in the document written to prevent exactly
that. It changed nothing — the acceptance test is content-based — which is the
point of building the guard that way.
