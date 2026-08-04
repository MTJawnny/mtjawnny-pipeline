# THINGS JAWNNY DOESN'T GIVE A DAMN ABOUT

**A DECLINE REGISTER.** Everything here was measured, understood, and
**deliberately not done**. This is not a backlog and not a list of open gaps.

## Why this file exists

The procedure's own diagnosis: *"ratification throughput is the bottleneck."*
Two sessions on 2026-08-02 generated more findings than could be ruled on. A
finding that is correct, cheap, and **worthless** still costs a decision, and
without a record of the decline it gets re-raised by the next session that
measures the corpus — which is exactly what a census is built to do.

**So: if it is here, do not re-raise it.** It is not an oversight, it is a
ruling. Report it as *declined*, never as *open*. If you think a decline is
wrong, say so in one line with what changed — do not re-derive it from scratch.

## The standing test

Captain's ratified criterion, and it is the one that decides every row here:

> **Judge candidates by DECK-BUILDING RELEVANCE, not textual frequency.**

The corpus tools — Magic Thesaurus, Similar Cards, Deck Finisher — exist to
answer *"what else does this job in my deck?"* A mechanic can be perfectly
real, perfectly parseable, and answer that question for nobody.

---

## 1. Attractions / the `Visit` keyword — declined 2026-08-06

| | |
|---|--:|
| cards | **22** |
| sets | **`unf` only** (Unfinity) |
| gate | passes on `{'commander': 'legal'}` alone |
| unrouted lines | 23 |
| CR | 702.159a / 702.159b, card type 717 |

**What it is.** Attractions are a separate deck; in your precombat main phase
you roll a d6 to "visit" them, and each Attraction whose lit-up numbers include
the result fires. CR 702.159a states the template outright — *"'Visit —
[Effect]' means 'Whenever you roll to visit your Attractions, if the result is
equal to a number that is lit up on this Attraction, [effect].'"* — so it is a
triggered ability with a CR-stated condition and **could** be closed with one
ratified §2 token.

**Why declined.** One novelty mechanic, one set, Commander-only. Nobody opens
the Thesaurus to find a substitute for Ferris Wheel. Captain, 2026-08-06:
*"yeah leave it. I don't care about it."*

**What it costs to decline:** 23 lines stay `spell-or-static`, which is an
honest report of a real, unnamed shape. That is what the bucket is for. Nothing
is corrupted and no other work is blocked.

## 2. Art tags — declined

**Out of scope by the derivation contract, not merely by preference.** The
standing rule is **evidence-quote-or-discard, and quotes come from ORACLE TEXT
ONLY.** Artwork, frame treatment and flavor text carry no rules meaning
(CR 207.2b makes flavor text explicitly non-functional), so nothing about them
is derivable inside this pipeline's evidence law. Tagging them would require a
second, non-oracle evidence source with its own provenance class.

Related and already settled: **Tag Grabber was deleted 2026-07-16** and must not
be referenced or revived; Similar Cards (4.3) supersedes it.

## 3. Prototype cards — declined

| | |
|---|--:|
| cards | **21** |
| sets | `bro` 18, `ybro` 2, `mh3` 1 |
| printed line | `Prototype {1}{B} — 1/1` |
| CR | 702.160, card type 718 |

**What it is.** An alternative casting cost that also changes the creature's
printed mana value, colour and P/T. The printed line is a **cost**, not a
delivery — `ability_word_prefix` already refuses it as such (CR 601.2b), so it
is handled correctly and simply has nothing to say.

**Why declined.** 21 cards, one block. Prototype changes *how you cast*, not
*what the card does in a deck slot*, so it answers the substitute question for
nobody.

---

## What is NOT on this list

Do not read this file as permission to skip a hard population. These are all
still live and none of them belong here:

- the **anthem group** (~15,181 lines in `spell-or-static`) — step 2's work
- **CR 706.3b die-roll rows** (101 lines) — needs no vocabulary at all
- the **43 CR 702 keywords with no `KEYWORD_HOME`** — includes `escape`,
  `flashback`, `evoke`, `partner`; real, deck-relevant mechanics
- **`start your engines!`** (46 lines) — CR 702.179a names its class outright
