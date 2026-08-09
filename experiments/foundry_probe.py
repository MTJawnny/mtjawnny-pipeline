#!/usr/bin/env python3
"""THE PROBE LIBRARY — make the RIGHT call shorter to write than the wrong one.

WHY THIS FILE EXISTS
--------------------
Twenty-one probe defects across five sessions. `docs/SYSTEM-SELF-TEST-2026-08-09.md`
measured why the standing cure never cured anything:

  · It was never ONE cure. The 21 have at least FOUR distinct causes, and a
    single slogan cannot prevent four things.
  · Every defect class that got a TOOL stopped recurring. Probe defects are the
    only class that never got one -- they got a paragraph in CLAUDE.md.
  · `foundry_prior_art.py --orphans` has reported "4 use the ratified
    preprocessing, 19 bypass it" since 2026-08-04. Re-run 2026-08-09: STILL
    4 and 19. A measurement nothing acts on is not a control.

A probe is written once, run once and thrown away. It never enters CI, gets no
baseline and gets no negative control. Every audit in this repo verifies the
PIPELINE; nothing verifies the INSTRUMENT. This file is that mechanism, and it
works the only way this has ever worked here: by being the path of least
resistance, not by being advice.

THE FOUR CAUSES AND THEIR GUARDS
--------------------------------
  A. RE-IMPLEMENTATION      `corpus()` / `rows()`  -- one canonical entry point.
  B. ASSUMED VOCABULARY     `domain()`             -- halts on a value the live
                                                      data does not contain.
  C. OVERLAPPING CLASSES    `assert_disjoint()`    -- halts when classes double-count.
  D. OVER-NARROW FILTER     `must_capture()`       -- halts when a known-positive
                                                      is missed.

USAGE -- the whole point is that this is shorter than doing it by hand:

    import foundry_probe as p

    ctx = p.corpus()                       # gated corpus + §2 + keyword homes
    for card, line, toks, descs in p.rows(ctx):
        ...

    st = p.domain(ctx.axes, "status", "active")      # halts on a typo'd value
    p.assert_disjoint({"em-dash": rx1, "bullet": rx2}, samples)
    p.must_capture(my_filter, p.KNOWN_TRIGGER_SHAPES)

Every guard HALTS rather than warns. A warned-about probe defect is the state
we have been in for five sessions.
"""
import sys
import re
import json
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc            # noqa: E402
import foundry_shape_extractor as fx   # noqa: E402

CODEBOOK = REPO_ROOT / "out" / "foundry" / "codebook.json"
GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"


class Ctx:
    """Everything a probe needs, built once, the same way the classifier does."""

    __slots__ = ("cards", "ratified", "keywords", "axes", "_cb")

    def __init__(self, cards, ratified, keywords, axes, cb):
        self.cards, self.ratified = cards, ratified
        self.keywords, self.axes, self._cb = keywords, axes, cb


_CTX = None


def corpus(force=False) -> Ctx:
    """GUARD A -- the one canonical way to stand up a probe.

    `build_self_noun_rx` and `build_keyword_homes` are ORDER-DEPENDENT module
    state. A probe that forgets either gets a subtly different classifier than
    the one it believes it is measuring, and nothing says so. Two of the 21
    were exactly this.
    """
    global _CTX
    if _CTX is not None and not force:
        return _CTX
    cards, _, _ = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)
    cb = json.loads(CODEBOOK.read_text(encoding="utf-8"))
    _CTX = Ctx(cards, ratified, set(fx.CR_KEYWORD_NAMES or ()), cb["axes"], cb)
    return _CTX


def rows(ctx: Ctx = None, gated_out=False):
    """GUARD A -- iterate (card, line, tokens, descriptors) the ONLY correct way.

    Uses `deliveries_for_lines`, never `parse_deliveries` on a bare line. The
    difference is D3 modal inheritance, and skipping it reported Charming
    Scoundrel as a MISMATCH on ground truth's first run: a CR 700.2 mode parses
    to None alone and inherits its header's `etb`.

    Yields TOKENS AS STRINGS. `parse_delivery` returns (token, descriptor)
    PAIRS, and `kw in [(tok, desc), ...]` is silently always False -- that
    scored a correct 304-member family 0/304.
    """
    ctx = ctx or corpus()
    for oid, card in sorted(ctx.cards.items(), key=lambda kv: kv[1]["name"]):
        for line, parsed in fx.deliveries_for_lines(card, ctx.ratified):
            yield (card, line,
                   [str(t) for t, _ in parsed],
                   [str(d) for _, d in parsed])


def domain(records, field, *values, allow_empty=False):
    """GUARD B -- halt if a value is not in the LIVE domain of `field`.

    The recorded case: a probe filtered axes on `status not in
    ("merged","retired","dropped")`. The live values are `active`, `renamed`,
    `killed`, `merged`, `deferred` -- so `retired`/`dropped` matched nothing,
    75 killed axes leaked in, and the active count read 436 against
    definition_drift's own 359. A count cannot see a substitution; only the
    domain can. Same family as "a halt-guard must assert CONTENT, not
    cardinality".

    Returns the set of requested values once they are proven to exist.
    """
    seq = records.values() if isinstance(records, dict) else records
    live = collections.Counter(
        (r.get(field) if isinstance(r, dict) else getattr(r, field, None))
        for r in seq)
    if not live and not allow_empty:
        fc.halt(f"field {field!r} is absent from every record. A probe "
                f"filtering on it would silently select nothing.")
    missing = [v for v in values if v not in live]
    if missing:
        fc.halt(
            f"value(s) {missing!r} do not occur in the live domain of "
            f"{field!r}.\n  live values: "
            f"{', '.join(f'{k!r}={n}' for k, n in live.most_common())}\n"
            f"  A filter on an absent value matches NOTHING and reads as a "
            f"clean result. This is the guessed-vocabulary defect.")
    return set(values)


def active_axes(ctx: Ctx = None):
    """GUARD B, applied -- the active set, with the domain proven first."""
    ctx = ctx or corpus()
    domain(ctx.axes, "status", "active")
    return {s: a for s, a in ctx.axes.items() if a.get("status") == "active"}


def assert_disjoint(classes: dict, samples, name="classes"):
    """GUARD C -- halt when two classification patterns claim the same sample.

    The recorded case: a `non-ASCII` class written `[^\\x00-\\x7f]` also matched
    the em-dash, the bullet and the curly apostrophe -- three classes already in
    the same table. It scored 6,342 lines at ratio 1.55 and was reported as a
    finding. Restricted to letters: 33 lines, ratio 0.81. A probe that overlaps
    another probe reports a correlation as a discovery.
    """
    overlaps = collections.Counter()
    example = {}
    for s in samples:
        hit = [k for k, rx in classes.items()
               if (rx.search(s) if hasattr(rx, "search") else rx(s))]
        for i, a in enumerate(hit):
            for b in hit[i + 1:]:
                overlaps[(a, b)] += 1
                example.setdefault((a, b), s)
    if overlaps:
        lines = "\n".join(
            f"    {a} ∩ {b}: {n} samples   e.g. {example[(a, b)][:70]!r}"
            for (a, b), n in overlaps.most_common(8))
        fc.halt(f"{name} are NOT disjoint -- each overlap is double-counted "
                f"and reads as an independent signal:\n{lines}")
    return True


def must_capture(predicate, cases, name="filter"):
    """GUARD D -- halt when a filter misses a known-positive.

    The recorded case: a probe required an ability line to start with `when`,
    and so lost `Burning Chains — When the chosen player loses the game` (a
    CR 207.2c ability-word prefix) and a compound `...AND whenever an opponent
    loses`. It reported 5 where the truth was 7 -- and the routing diff, not the
    probe, is what corrected it.

    `cases` is an iterable of (text, should_match) -- a fixture, inline, tiny.
    """
    bad = [(t, want) for t, want in cases if bool(predicate(t)) != bool(want)]
    if bad:
        lines = "\n".join(
            f"    expected {'MATCH' if w else 'NO match'}: {t[:78]!r}"
            for t, w in bad[:8])
        fc.halt(f"{name} disagrees with its own known-positive fixture on "
                f"{len(bad)} case(s):\n{lines}\n"
                f"  An over-narrow filter under-reports and reads as a clean "
                f"measurement.")
    return True


# A shared fixture of trigger shapes that have each broken a real probe.
# Every one is a printed corpus line, not an invention.
KNOWN_TRIGGER_SHAPES = [
    ("Burning Chains — When the chosen player loses the game, you win the game.", True),
    ("When this enchantment enters and whenever an opponent loses the game, "
     "exile the top card of each player's library.", True),
    ("Whenever you gain or lose life during your turn, this creature gets "
     "+1/+0 until end of turn.", True),
    ("Eerie — Whenever an enchantment you control enters and whenever you "
     "fully unlock a Room, draw a card.", True),
    ("Flying, vigilance", False),
    ("{T}: Add {C}.", False),
]


def vocab(section: str) -> set:
    """GUARD B, for grammar sections -- backticked identifiers, halt-guarded.

    A renamed heading returns an empty set, which scores every segment UNKNOWN
    and reads as a catastrophic finding rather than a broken probe.
    """
    text = GRAMMAR.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(section)}\..*?$(.*?)(?=^## \d)", text,
                  re.M | re.S)
    if not m:
        fc.halt(f"grammar section §{section} not found. A probe deriving "
                f"vocabulary from it would score everything UNKNOWN.")
    toks = {t.strip("`") for t in
            re.findall(r"`([a-z0-9][a-z0-9\-<>]*)`", m.group(1))}
    toks = {t for t in toks if t and not t.startswith("-")}
    if len(toks) < 5:
        fc.halt(f"grammar §{section} yielded only {len(toks)} identifiers; the "
                f"section shape changed. Refusing to return a vocabulary that "
                f"would silently under-match.")
    return toks


def longest_match(segments, vocabulary, window=4):
    """GUARD A -- greedy longest-first over a HYPHEN SEQUENCE.

    Ratified vocabulary CONTAINS hyphens (`you-control`, `create-token`,
    `plus1-counter`). Splitting on `-` and testing each piece shreds the
    vocabulary being measured against: that scored 24.1% coverage and listed
    `you`, `control`, `create` as unknown. Greedy: 42.9%.

    Yields (matched_term_or_None, n_segments_consumed).
    """
    i = 0
    while i < len(segments):
        for j in range(min(len(segments), i + window), i, -1):
            cand = "-".join(segments[i:j])
            if cand in vocabulary:
                yield cand, j - i
                i = j
                break
        else:
            yield None, 1
            i += 1


def selftest():
    """Negative-control the library itself. A guard that has never been shown
    to FAIL is not known to be a guard -- the finding of the 2026-08-09 gate
    audit, applied to this file before it is trusted by anything."""
    import subprocess
    ok, bad = [], []

    def expect_halt(label, fn):
        try:
            fn()
        except SystemExit:
            ok.append(label)
            return
        except Exception as e:
            ok.append(f"{label} (raised {type(e).__name__})")
            return
        bad.append(label)

    def expect_pass(label, fn):
        try:
            fn()
            ok.append(label)
        except BaseException as e:
            bad.append(f"{label} -- unexpectedly failed: {e!r}")

    recs = [{"status": "active"}, {"status": "killed"}, {"status": "renamed"}]
    expect_pass("B domain: real value passes", lambda: domain(recs, "status", "active"))
    expect_halt("B domain: guessed value halts", lambda: domain(recs, "status", "retired"))
    expect_halt("B domain: absent field halts", lambda: domain(recs, "nosuch", "x"))

    dis = {"em-dash": re.compile(r"—"), "non-ascii": re.compile(r"[^\x00-\x7f]")}
    expect_halt("C disjoint: overlapping classes halt",
                lambda: assert_disjoint(dis, ["a — b"]))
    good = {"em-dash": re.compile(r"—"), "bullet": re.compile(r"•")}
    expect_pass("C disjoint: disjoint classes pass",
                lambda: assert_disjoint(good, ["a — b", "x • y"]))

    narrow = lambda t: bool(re.match(r"^When(ever)?\b", t))
    expect_halt("D capture: over-narrow filter halts",
                lambda: must_capture(narrow, KNOWN_TRIGGER_SHAPES))
    wide = lambda t: bool(re.search(r"\bWhen(ever)?\b", t))
    expect_pass("D capture: correct filter passes",
                lambda: must_capture(wide, KNOWN_TRIGGER_SHAPES))

    expect_pass("B vocab: §4 parses", lambda: vocab("4"))
    expect_halt("B vocab: bogus section halts", lambda: vocab("999"))

    segs = "you-control-create-token".split("-")
    got = [m for m, _ in longest_match(segs, {"you-control", "create-token"})]
    (ok if got == ["you-control", "create-token"] else bad).append(
        f"A longest_match: multiword terms survive ({got})")

    print("=" * 74)
    print("PROBE LIBRARY SELF-TEST — every guard shown capable of FAILING")
    print("=" * 74)
    for o in ok:
        print(f"  ✓ {o}")
    for b in bad:
        print(f"  ✗ {b}")
    print(f"\n  {len(ok)} passed, {len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest())
