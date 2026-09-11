#!/usr/bin/env python3
"""CR EDITION — the S9 test owner of the `_CASES` / `_selftest` guard.

R5 closed a debt, not a gap in coverage: these ten cases and their negative
controls have existed since the CR normalizer was written, and NOTHING RAN
THEM. `experiments/foundry_cr.py --selftest` was reachable only by a human
typing it, and no Gate-2 row, no test and no workflow ever did. A guard nobody
invokes is indistinguishable from a guard that passes.

This file is where they live now, and `tests/refoundation/test_cr_edition_guard.py`
is what makes the standing suite run them.

WHY THIS IS NOT A SEVENTEENTH GATE-2 ROW
----------------------------------------
K6 fixes normal Gate 2 at 16 checks over 15 scripts, and that contract is not a
count to be edged upward whenever something needs running. The CR-edition guard
is registered on the refoundation test surface instead, which executes on every
`python3 -m unittest discover -s tests/refoundation -t .`. It is standing and
red-capable; it is not a Gate-2 row.

WHAT IT OWNS
------------
The ten normalize cases, and the four control families the legacy `_selftest`
carried: the pure-deletion conservation law (rejects substitution/insertion/
greedy-span/reordering, accepts a legitimate markup deletion), the encoding
guard, the declared-damage repair, and -- added here, because R5 requires this
surface to be shown RED on a rigged input -- the BROKEN BOLD RULE control
aimed at `_assert_parseable`.

WHAT IT DELIBERATELY DOES NOT OWN
----------------------------------
`_report`, the legacy CLI and the `PRIOR_CR_PATH` operator presentation stay in
`experiments/foundry_cr.py` for their later operator disposition.

WHICH MODULE IS UNDER TEST
--------------------------
The permanent S6 semantics, `mtj_foundry.mtg.cr.edition`. The legacy shell is
imported too, and every name this guard uses is asserted to BE the permanent
module's -- so this cannot drift into testing a second implementation. The
shell is what re-establishes the `STOP — …` process boundary the encoding
controls catch as `SystemExit`, which is why the controls reach the law
through it rather than around it.

    python3 tests/guards/cr/test_cr_edition.py
"""
import sys
from pathlib import Path

# The legacy module directory: the shell is the halt boundary these controls
# were written against, and it is a bounded later-owner surface this guard is
# authorized to consume while that slice is outstanding.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "experiments"))
import foundry_cr as cr                              # noqa: E402

from mtj_foundry.mtg.cr import edition as _edition   # noqa: E402

# The permanent module is the thing under test. These bindings are the shell's,
# which is how the historic `SystemExit` contract is preserved; that they resolve
# to the permanent implementation and not a second copy is ASSERTED below rather
# than assumed.
normalize_line = cr.normalize_line
_pure_deletion = cr._pure_deletion
_assert_encoding = cr._assert_encoding
_demojibake = cr._demojibake
_repair_encoding = cr._repair_encoding
PRIOR_CR_PATH = cr.PRIOR_CR_PATH
_KNOWN_ENCODING_DAMAGE = cr._KNOWN_ENCODING_DAMAGE


def _assert_the_law_is_the_permanent_one() -> int:
    """The shell must be an alias, never a second implementation.

    Aimed at the failure this whole migration exists to prevent: a legacy file
    quietly keeping its own copy of a promoted semantic, so the guard passes
    while the shipped library drifts.
    """
    bad = 0
    aliased = {"_pure_deletion": _edition._pure_deletion,
               "_demojibake": _edition._demojibake,
               "_KNOWN_ENCODING_DAMAGE": _edition._KNOWN_ENCODING_DAMAGE,
               "PRIOR_CR_PATH": _edition.PRIOR_CR_PATH}
    for name, permanent in aliased.items():
        if getattr(cr, name) is permanent:
            print(f"  [ok] {name} IS mtj_foundry.mtg.cr.edition's")
        else:
            print(f"  [FAIL] {name} is a second implementation")
            bad += 1
    # The wrapped ones cannot be `is`-identical -- the wrapper is the halt
    # boundary -- so the check is that each one WRAPS the permanent function.
    for name in ("normalize_line", "normalize", "_assert_parseable",
                 "_assert_encoding", "_repair_encoding"):
        wrapper = getattr(cr, name)
        permanent = getattr(_edition, name)
        if wrapper is permanent or wrapper.__doc__ == permanent.__doc__:
            print(f"  [ok] {name} reaches the permanent module")
        else:
            print(f"  [FAIL] {name} does not reach the permanent module")
            bad += 1
    return bad


def _bolded_fragment() -> str:
    """A synthetic navigation-formatted CR fragment, DERIVED from the anchors.

    Every required anchor, re-bolded into the shape the navigation edition
    actually prints. Derived rather than typed: a hand-written fragment would
    be a second list of the rule lines the guard requires, and would go stale
    the moment `_REQUIRED_ANCHORS` moved.
    """
    import re
    out = []
    for anchor, _why in _edition._REQUIRED_ANCHORS:
        m = re.match(r"^(\d{3}\.\d+[a-z]{0,2})\.?(\s?)(.*)$", anchor)
        num, gap, rest = m.group(1), m.group(2), m.group(3)
        out.append(f"**{num}.**{gap}{rest}")
    return "\n".join(out) + "\n"


def _broken_bold_rule_control() -> int:
    """THE R5 CONTROL: rig the bold-rule handling and require a real RED.

    `_assert_parseable` has two arms and both are exercised, because a control
    that shows one arm red says nothing about the other:

      * rig `_BOLD_RULE` alone -> `_BOLD_LABEL` still strips the wrapper, so the
        SUBRULE lines keep the marker's period (`205.2a.` where the plain shape
        writes `205.2a`) and the required anchors go missing;
      * rig both -> the `**205.2a.**` marker survives literally and the
        surviving-marker arm fires.

    Aimed at the PATTERNS, which are the code path, not at the tool's name --
    three of eight controls on 2026-08-09 were mis-aimed and each first read as
    "this gate is broken".

    Run against a synthetic fragment. The real edition on disk is never read,
    normalized or written here.
    """
    import re
    bad = 0
    fragment = _bolded_fragment()

    # Control A, the POSITIVE half: unrigged, the fragment normalizes to a
    # parseable CR. Without this the controls below would also pass if the
    # fragment were simply malformed.
    try:
        _edition._assert_parseable(_edition.normalize(fragment), Path("<control>"))
        print("  [ok] the real normalizer leaves the fragment parseable")
    except _edition.CRError as exc:
        print(f"  [FAIL] the real normalizer produced unparseable text: {exc}")
        bad += 1

    # A pattern that matches nothing but still HAS a group, because
    # `normalize_line` substitutes `\\1` through `_BOLD_LABEL` and a groupless
    # rig would raise `re.PatternError` instead of exercising the guard -- a
    # control that dies on its own rigging proves nothing about the law.
    NEVER = re.compile(r"^(?!x)(x)")

    def rigged(source, *names) -> str:
        """Normalize + assert with the named patterns unable to match."""
        real = {n: getattr(_edition, n) for n in names}
        for n in names:
            setattr(_edition, n, NEVER)
        try:
            _edition._assert_parseable(_edition.normalize(source),
                                       Path("<control>"))
            return ""
        except _edition.CRError as exc:
            return str(exc)
        finally:
            for n, v in real.items():
                setattr(_edition, n, v)

    # The second arm needs its OWN input, and that is the point rather than a
    # convenience: `_assert_parseable` checks the anchors FIRST, so a fragment
    # that loses them can never reach the surviving-marker branch. Its input is
    # therefore anchors already in the PLAIN shape -- which the normalizer
    # leaves alone -- plus one bolded line that has nowhere to go once both
    # patterns are rigged.
    plain_plus_marker = ("\n".join(a for a, _ in _edition._REQUIRED_ANCHORS)
                         + "\n**205.2a.** The card types are artifact.\n")

    checks = [
        ("a broken _BOLD_RULE loses the required rule lines",
         fragment, ("_BOLD_RULE",), "does not normalize to a parseable CR"),
        ("a broken _BOLD_RULE and _BOLD_LABEL leave the marker standing",
         plain_plus_marker, ("_BOLD_RULE", "_BOLD_LABEL"),
         "bold rule markers survived normalization"),
    ]
    for label, source, names, want in checks:
        message = rigged(source, *names)
        if want in message:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label} -- went UNDETECTED "
                  f"(got {message[:70]!r})")
            bad += 1

    # Restored, or every later caller in this process tests the rig, not the law.
    for name in ("_BOLD_RULE", "_BOLD_LABEL"):
        if getattr(_edition, name) is not NEVER:
            print(f"  [ok] {name} restored")
        else:
            print(f"  [FAIL] {name} was not restored")
            bad += 1
    return bad


# ---------------------------------------------------------------------------
# SELF-TEST — a guard that has never been shown to fail is not known to be a
# guard (CLAUDE.md, 2026-08-09). Each case below is a NEGATIVE control aimed at
# the code path, not at the module's name.
# ---------------------------------------------------------------------------
_CASES = [
    # (label, raw, expected-or-None-if-must-halt)
    ("bold subrule drops its period",
     "**205.2a.** The card types are artifact, battle, and vanguard.",
     "205.2a The card types are artifact, battle, and vanguard."),
    ("bold numbered rule KEEPS its period",
     "**702.6.** Equip", "702.6. Equip"),
    ("two-letter subrule",
     "**704.5aa.** If a player controls a permanent",
     "704.5aa If a player controls a permanent"),
    ("plain line is untouched (the prior edition still loads)",
     "205.2a The card types are artifact.",
     "205.2a The card types are artifact."),
    ("blockquoted example becomes a plain Example: line",
     "> **Example:** Lost Order of Jarkeld has power 1+*.",
     "Example: Lost Order of Jarkeld has power 1+*."),
    ("heading dedents one level",
     "### 702. Keyword Abilities", "## 702. Keyword Abilities"),
    ("top-level heading is left alone",
     "# Magic: The Gathering Comprehensive Rules",
     "# Magic: The Gathering Comprehensive Rules"),
    ("navigation label loses only its wrapper",
     "**These rules are effective as of August 7, 2026.**",
     "These rules are effective as of August 7, 2026."),
    # CR 208.2 prints a literal asterisk. A blanket `\*\*` strip would survive
    # this line by luck; the test pins that it must not be attempted.
    ("a LITERAL CR asterisk survives",
     "**208.2.** Some creature cards have power and/or toughness of */*.",
     "208.2. Some creature cards have power and/or toughness of */*."),
    ("a rule number cited MID-SENTENCE is not a marker",
     "See rule 605.1a for mana abilities.",
     "See rule 605.1a for mana abilities."),
]

def _selftest() -> int:
    bad = 0
    for label, raw, want in _CASES:
        got = normalize_line(raw)
        ok = got == want and _pure_deletion(raw, got)
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            bad += 1
            print(f"        raw  {raw!r}\n        want {want!r}\n        got  {got!r}")

    # Guard D — the conservation law must REJECT a deliberately broken
    # normalizer. Without this the law is decoration.
    broken = [("substitution", "205.2a x", "205.2a y"),
              ("insertion", "205.2a x", "205.2a xy"),
              ("greedy span eaten", "205.2a (see 300) x", "205.2a x"),
              ("reordering", "205.2a ab", "205.2a ba")]
    for label, raw, fake in broken:
        if _pure_deletion(raw, fake):
            print(f"  [FAIL] conservation accepted a {label}")
            bad += 1
        else:
            print(f"  [ok] conservation rejects a {label}")

    # And it must ACCEPT a legitimate markup deletion, or it is merely strict.
    if not _pure_deletion("**205.2a.** x", "205.2a x"):
        print("  [FAIL] conservation rejects a legitimate markup deletion")
        bad += 1
    else:
        print("  [ok] conservation accepts a legitimate markup deletion")

    # The encoding guard, aimed at the CODE PATH rather than at the tool's
    # name: three of eight negative controls on 2026-08-09 were mis-aimed and
    # each first read as "this gate is broken".
    def halts(text):
        try:
            _assert_encoding(text, Path("<selftest>"))
            return False
        except SystemExit:
            return True

    declared = next(iter(_KNOWN_ENCODING_DAMAGE))
    checks = [
        ("encoding guard fires on an UNDECLARED corrupted rule",
         "702.6a Equip is an activated ability of JuzÃ¡m cards.", True),
        (f"encoding guard stays quiet on the declared rule ({declared})",
         f"{declared} Those names are DandÃ¢n, JuzÃ¡m Djinn.", False),
        ("encoding guard stays quiet on correct accented text",
         "206.3a Those names are Dandân, Juzám Djinn, Ring of Ma’rûf.", False),
        ("encoding guard stays quiet on the curly apostrophe alone",
         "205.3i The land types are Urza’s, Desert.", False),
    ]
    for label, line, want_halt in checks:
        got = halts(line)
        if got == want_halt:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label} (halted={got}, wanted {want_halt})")
            bad += 1

    # THE REPAIR (D-CR-1b). Every case is aimed at the code path, not at the
    # feature's name — the three mis-aimed negative controls of 2026-08-09 each
    # first read as "this gate is broken".
    if _demojibake("JuzÃ¡m Djinn") == "Juzám Djinn":
        print("  [ok] repair is DERIVED from the damage, not typed")
    else:
        print("  [FAIL] repair derivation is wrong")
        bad += 1

    def repairs(text_in):
        try:
            return _repair_encoding(text_in, PRIOR_CR_PATH)   # skips assert 2
        except SystemExit:
            return "<HALTED>"

    rule = declared
    repair_cases = [
        ("declared damage is repaired",
         f"{rule} Those names are DandÃ¢n, GhazbÃ¡n Ogre, JuzÃ¡m Djinn, "
         f"KhabÃ¡l Ghoul, JunÃºn Efreet, Ring of Ma’rÃ»f, El-HajjÃ¢j.",
         f"{rule} Those names are Dandân, Ghazbán Ogre, Juzám Djinn, "
         f"Khabál Ghoul, Junún Efreet, Ring of Ma’rûf, El-Hajjâj."),
        # A count that does not match the register means the damage MOVED.
        # Widening the repair to fit is how a register stops being evidence.
        ("a DIFFERENT amount of damage halts rather than being absorbed",
         f"{rule} Those names are DandÃ¢n and JuzÃ¡m Djinn.", "<HALTED>"),
        # Clean text must survive the pass untouched, or the repair is a
        # rewrite wearing a repair's name.
        ("already-correct text passes through unchanged",
         f"{rule} Those names are Dandân, Juzám Djinn.",
         f"{rule} Those names are Dandân, Juzám Djinn."),
    ]
    for label, src, want in repair_cases:
        got = repairs(src)
        if got == want:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label}\n        got  {got!r}\n        want {want!r}")
            bad += 1
    return bad


def main() -> int:
    print("CR EDITION SELF-TEST — every guard shown to both pass and fail.")
    print("Each negative control prints its guard's real STOP message to "
          "stderr. Those\nare the controls WORKING; the verdict is the "
          "[ok]/[FAIL] column below.")
    bad = _selftest()
    bad += _assert_the_law_is_the_permanent_one()
    bad += _broken_bold_rule_control()
    if bad:
        print(f"\n{bad} self-test failure(s)")
        return 1
    print("\nall guards behaved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
