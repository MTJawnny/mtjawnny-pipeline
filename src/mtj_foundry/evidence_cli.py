"""The installed milestone-2 command — one script, three subcommands.

## Why one script and not three

`mtj-foundry-evidence index | query | evaluate`. Three console scripts would put
three entry points in the metadata for one capability, and an operator would
have to learn which of them shares which flags. One subcommand surface keeps the
shared input contract in one place and makes the pipeline obvious in the help
text: emit an artifact, then ask it questions, then grade it against the frozen
panel.

`mtj-foundry-report` is untouched. It is the accepted milestone-1 command with
its own accepted contract, and folding it in here would rewrite an accepted
surface for tidiness.

## The exit contract is milestone 1's, unchanged

* **0** — the requested document is on stdout.
* **1** — a declared input did not hold, or could not be read: a digest or size
  mismatch, a missing or malformed file, a schema rejection, a lint failure, an
  unknown anchor, an ambiguous name. One `STOP — …` line on stderr and **nothing
  on stdout**, so a redirected artifact file is never left holding a
  success-shaped document for a run that failed.
* **2** — argparse's own bad-usage status, untouched.

Anything else escapes with its traceback. An unexpected exception is a defect,
not a category of result, and there is no `except Exception` in this file.

## What each subcommand reads

`index` reads the repository inputs — the authority selector, the codebook, the
corpus, the input lock — through the milestone-1 boundary, and writes the
artifact to stdout. `query` and `evaluate` read **only** the emitted artifact
(and, for `evaluate`, the frozen panel fixture). That asymmetry is the milestone
property: once the artifact exists, answering a question about it needs no
repository, no codebook and no corpus.

The command writes no file and creates no directory. Redirecting stdout is an
operator choice, not a side effect.
"""

from __future__ import annotations

import argparse
import sys

from mtj_foundry import (__version__, codebook, codebook_store, corpus,
                         evaluation, evidence_index, retrieval, runtime)

__all__ = ["build_parser", "main"]

_EPILOG = """\
examples:
  # emit the artifact (reads the repository; stdout is the artifact)
  mtj-foundry-evidence index --root /path/to/repo \\
      --input-lock /path/to/repo/refoundation/path-e/input-lock.json > index.json

  # ask it a question (reads ONLY the artifact, from anywhere)
  mtj-foundry-evidence query --index index.json --name "Reanimate" --top 25

  # grade it against the frozen panel
  mtj-foundry-evidence evaluate --index index.json \\
      --panel /path/to/repo/refoundation/path-e/m2-evaluation.json \\
      --source-document /path/to/repo/docs/WIRE-PREDICTIONS-2026-08-09.md

An anchor is named by oracle_id or by name. A name matching more than one
oracle_id HALTS: oracle_id is the only card key, and 216 normalized names in the
selected corpus are shared by more than one card.
"""


def _add_input_arguments(parser: argparse.ArgumentParser) -> None:
    """The milestone-1 input surface, verbatim, on the one subcommand that reads
    repository inputs. Stated once so `index` cannot drift from `report`."""
    parser.add_argument("--root", required=True,
                        help="repository root. explicit on purpose: the command "
                             "never derives it from the working directory")
    parser.add_argument("--authority", default=None,
                        help="override the tracked codebook authority selector")
    parser.add_argument("--codebook", default=None, help="override the codebook path")
    parser.add_argument("--corpus", default=None,
                        help="corpus path; relative values resolve against --root")
    parser.add_argument("--input-lock", default=None,
                        help="input-lock document declaring the corpus identity "
                             "and provenance")
    parser.add_argument("--corpus-sha256", default=None,
                        help="expected sha256 of the corpus file's exact bytes")
    parser.add_argument("--corpus-content-sha256", default=None,
                        help="expected sha256 of the corpus DECOMPRESSED content")
    parser.add_argument("--corpus-provenance", default=None,
                        help="one statement of where the corpus bytes came from")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mtj-foundry-evidence",
        description=("Emit a deterministic full-population evidence index over the "
                     "selected codebook and corpus, query it, or grade it against "
                     "the frozen evaluation panel. Read-only: it infers nothing, "
                     "assigns nothing, and writes nothing. Every document it emits "
                     "is derived evidence, not authority."),
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"mtj-foundry-evidence (mtj_foundry {__version__})")
    sub = parser.add_subparsers(dest="command", required=True)

    index = sub.add_parser(
        "index", help="emit the evidence index artifact on stdout",
        description=("Verify the selected inputs through the accepted milestone-1 "
                     "boundary and emit one row per card of the ENTIRE selected "
                     "corpus. Eligibility and coverage are fields on a row, never "
                     "a filter over rows."))
    _add_input_arguments(index)

    query = sub.add_parser(
        "query", help="query an emitted index artifact",
        description=("Return the cards the selected evidence connects to an anchor, "
                     "with the positive evidence that caused each discovery. Reads "
                     "the artifact and nothing else."))
    query.add_argument("--index", required=True, help="path to an emitted index artifact")
    anchor = query.add_mutually_exclusive_group(required=True)
    anchor.add_argument("--oracle-id", default=None, help="anchor by oracle_id")
    anchor.add_argument("--name", default=None,
                        help="anchor by printed name; an ambiguous name HALTS")
    query.add_argument("--top", type=int, default=None,
                       help="print only the first N candidates. ranks and tie blocks "
                            "are computed over the whole set first")

    evaluate = sub.add_parser(
        "evaluate", help="grade the retrieval against the frozen panel",
        description=("Run the frozen named-correct panel and emit a deterministic "
                     "report separating candidate discovery from presentation. This "
                     "is a measurement; it authorises nothing."))
    evaluate.add_argument("--index", required=True,
                          help="path to an emitted index artifact")
    evaluate.add_argument("--panel", required=True,
                          help="path to the frozen evaluation panel fixture")
    evaluate.add_argument("--source-document", default=None,
                          help="path to the frozen source document, to verify the "
                               "panel's recorded git blob id against its bytes")
    return parser


def _run_index(args) -> str:
    index = evidence_index.generate(
        args.root,
        authority_path=args.authority,
        codebook_path=args.codebook,
        corpus_path=args.corpus,
        lock_path=args.input_lock,
        expected_corpus_sha256=args.corpus_sha256,
        expected_corpus_content_sha256=args.corpus_content_sha256,
        corpus_provenance=args.corpus_provenance)
    return evidence_index.render_index(index)


def _run_query(args) -> str:
    document = retrieval.load_index(args.index)
    result = retrieval.query(document, oracle_id=args.oracle_id, name=args.name,
                             top=args.top)
    return retrieval.render_result(result)


def _run_evaluate(args) -> str:
    document = retrieval.load_index(args.index)
    panel = evaluation.load_panel(args.panel)
    measured = verified = None
    if args.source_document is not None:
        try:
            measured = evaluation.git_blob_sha(args.source_document)
        except OSError as error:
            raise evaluation.PanelError(
                f"panel source document at {args.source_document}: "
                f"{type(error).__name__}: {error}") from error
        verified = measured == panel["source"]["git_blob_sha"]
        if not verified:
            raise evaluation.PanelError(
                f"the panel records source git blob "
                f"{panel['source']['git_blob_sha']!r} but "
                f"{args.source_document} measures {measured!r} — the frozen "
                f"document or the fixture changed; refusing to grade against a "
                f"panel whose source is not the one it was transcribed from")
    result = evaluation.evaluate(document, panel, panel_source_blob_sha=measured,
                                 panel_source_blob_sha_verified=verified)
    return evaluation.render_evaluation(result)


_COMMANDS = {"index": _run_index, "query": _run_query, "evaluate": _run_evaluate}


def main(argv=None) -> int:
    """Run one subcommand. Returns a process exit status; never raises for input state."""
    args = build_parser().parse_args(argv)
    try:
        payload = _COMMANDS[args.command](args)
    except (runtime.FoundryRuntimeError, codebook_store.CodebookReadError,
            codebook_store.CodebookStoreError, codebook.LintError,
            corpus.CorpusLoadError,
            evidence_index.EvidenceIndexConservationError) as error:
        # HOUSE STYLE, AT THE ONE PLACE IT BELONGS. A plain-English line naming
        # the exact problem, on stderr, and nothing on stdout. `RetrievalError`
        # and `PanelError` are `FoundryRuntimeError` subclasses and are caught by
        # the first name in this tuple.
        print(f"STOP — {error}", file=sys.stderr)
        return 1
    sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
