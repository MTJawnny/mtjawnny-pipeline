"""The installed Foundry command — argument parsing and process exit, nothing else.

## Why this file is thin

`mtj_foundry.runtime` raises; this decides what a raised failure means to a
shell. That split is the whole point: a library that calls `sys.exit` cannot be
composed, and a library that swallows a failure to return a tidy value turns a
stop into a result. The rule the refoundation already ratified for the corpus and
codebook capabilities applies unchanged here -- the library raises, the CLI
handles the process.

## The two exit statuses

* **1 — a declared input did not hold, or an input could not be read.** Every
  typed failure this boundary or the capabilities beneath it raise lands here:
  a missing selector, a digest or size mismatch, a schema rejection, a lint
  failure, an unreadable corpus. Nothing is printed to stdout on this path, so a
  redirected report file is never left holding a success-shaped document that
  describes a failed run.
* **2 — the command was invoked wrongly.** argparse's own status, untouched.

Anything else propagates with its traceback. An unexpected exception is not a
category of result; it is a defect, and hiding it behind a friendly message and
exit 1 would make it indistinguishable from an input that legitimately failed
verification.

## The command writes nothing

It opens no file for writing, creates no directory and caches nothing. The report
goes to stdout. An operator may redirect that stream wherever they like; where it
lands is the operator's decision and not a side effect of this command.
"""

from __future__ import annotations

import argparse
import sys

from mtj_foundry import __version__, codebook, codebook_store, corpus, runtime

__all__ = ["build_parser", "main"]

_EPILOG = """\
examples:
  mtj-foundry-report --root /path/to/repo \\
      --input-lock /path/to/repo/refoundation/path-e/input-lock.json

  mtj-foundry-report --root /path/to/repo \\
      --corpus data/raw/oracle-cards.jsonl.gz \\
      --corpus-sha256 <hex> --corpus-provenance "<where these bytes came from>"

The codebook is selected by the tracked authority selector and verified against
it; the corpus has no tracked selector, so its expected sha256 and provenance are
REQUIRED. A run that cannot state which corpus bytes it measured does not run.
"""


def build_parser() -> argparse.ArgumentParser:
    """The command's declared surface.

    `--root` is EXPLICIT and required. Discovering it from the working directory
    would make the command's inputs depend on where it was invoked, which is the
    cwd coupling the permanent layout owner exists to remove -- and this command
    must be runnable from an unrelated directory with nothing on the path.
    """
    parser = argparse.ArgumentParser(
        prog="mtj-foundry-report",
        description=("Verify the selected codebook and an explicitly pinned corpus, "
                     "load both through the permanent capabilities, and emit one "
                     "deterministic input/population/coverage report on stdout. "
                     "Read-only: it infers nothing, assigns nothing, and writes "
                     "nothing. The report is derived evidence, not authority."),
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"mtj-foundry-report (mtj_foundry {__version__})")
    parser.add_argument("--root", required=True,
                        help="repository root. explicit on purpose: the command "
                             "never derives it from the working directory")
    parser.add_argument("--authority", default=None,
                        help="override the tracked codebook authority selector "
                             "(default: the layout owner's selector path)")
    parser.add_argument("--codebook", default=None,
                        help="override the codebook path (default: the layout "
                             "owner's operational codebook path)")
    parser.add_argument("--corpus", default=None,
                        help="corpus path; relative values resolve against --root")
    parser.add_argument("--input-lock", default=None,
                        help="input-lock document declaring the corpus identity "
                             "and provenance")
    parser.add_argument("--corpus-sha256", default=None,
                        help="expected sha256 of the corpus file's exact bytes")
    parser.add_argument("--corpus-content-sha256", default=None,
                        help="expected sha256 of the corpus DECOMPRESSED content; "
                             "measured and compared only when given")
    parser.add_argument("--corpus-provenance", default=None,
                        help="one statement of where the corpus bytes came from")
    return parser


def main(argv=None) -> int:
    """Run one report. Returns a process exit status; never raises for input state."""
    args = build_parser().parse_args(argv)
    try:
        report = runtime.run(
            args.root,
            authority_path=args.authority,
            codebook_path=args.codebook,
            corpus_path=args.corpus,
            lock_path=args.input_lock,
            expected_corpus_sha256=args.corpus_sha256,
            expected_corpus_content_sha256=args.corpus_content_sha256,
            corpus_provenance=args.corpus_provenance,
        )
    except (runtime.FoundryRuntimeError, codebook_store.CodebookReadError,
            codebook_store.CodebookStoreError, codebook.LintError,
            corpus.CorpusLoadError) as error:
        # HOUSE STYLE, AT THE ONE PLACE IT BELONGS. A plain-English line naming
        # the exact problem, on stderr, and nothing on stdout.
        print(f"STOP — {error}", file=sys.stderr)
        return 1
    sys.stdout.write(runtime.render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
