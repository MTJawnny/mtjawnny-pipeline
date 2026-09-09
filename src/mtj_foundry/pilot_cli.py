"""The installed milestone-3 command — `mtj-foundry-pilot`.

## Why a second console script and not a fourth `mtj-foundry-evidence` subcommand

The task allowed either, and the deciding fact is one line of the accepted
milestone-2 surface's own contract: *"The command writes no file and creates no
directory. Redirecting stdout is an operator choice, not a side effect."* Every
one of `index`, `query` and `evaluate` emits its document on stdout and opens
nothing for writing, and a reviewer can check that property of the whole command
in one sentence.

A bundle builder writes several hundred files into a directory. Folding it in
would falsify that sentence, and the repair would be to edit accepted prose in
an accepted module so a new subcommand could live under it — which is rewriting
an accepted contract for tidiness, the exact thing `evidence_cli` declined to do
to `mtj-foundry-report`. So milestone 2's command is untouched, and the
capability that writes gets its own name, where "this one writes, and only where
you tell it to" is the whole surface.

## The exit contract is milestone 1's, unchanged

* **0** — the bundle is written; a short human-readable summary is on stdout.
* **1** — a declared input did not hold: a missing or malformed artifact, a
  schema rejection, two artifacts built from different selected inputs, or an
  output directory this builder may not write into. One `STOP — …` line on
  stderr and **nothing on stdout**.
* **2** — argparse's own bad-usage status, untouched.

There is no `except Exception` here either. An unexpected exception is a defect,
not a category of result.

## What it reads and what it writes

It reads exactly two files — the emitted index artifact and the emitted
evaluation report — plus its own package-owned static assets. It reads no
repository, no codebook, no corpus, no authority selector and no network.

It writes only under the explicit `--output` directory, and only under the rule
`pilot._prepare_output` states: create a new path, use an empty one, replace one
whose `manifest.json` this builder wrote, and refuse everything else. It never
deletes a directory tree.
"""

from __future__ import annotations

import argparse
import sys

from mtj_foundry import __version__, pilot, runtime

__all__ = ["build_parser", "main"]

_EPILOG = """\
example:
  # emit the two accepted milestone-2 artifacts first
  mtj-foundry-evidence index --root /path/to/repo \\
      --input-lock /path/to/repo/refoundation/path-e/input-lock.json > index.json
  mtj-foundry-evidence evaluate --index index.json \\
      --panel /path/to/repo/refoundation/path-e/m2-evaluation.json > evaluation.json

  # then build the static bundle from those FILES -- no repository is read
  mtj-foundry-pilot --index index.json --evaluation evaluation.json \\
      --output /tmp/pilot-bundle

  # serve it with any plain static file server
  python3 -m http.server --directory /tmp/pilot-bundle 8000

The bundle is a DIAGNOSTIC over a selected historical corpus and codebook. It is
not a finished thesaurus, not a production Searcher B, and not a claim about
similarity. It shows the coverage and tie-block limits of the current evidence
rather than hiding them.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mtj-foundry-pilot",
        description=("Build a deterministic, self-contained static diagnostic "
                     "bundle from an emitted evidence index and its evaluation "
                     "report. Consumes artifacts only: once they exist, no "
                     "repository, codebook, corpus or backend is read, and the "
                     "emitted bundle needs none at runtime either."),
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"mtj-foundry-pilot (mtj_foundry {__version__})")
    parser.add_argument("--index", required=True,
                        help="path to an emitted mtj-foundry-evidence-index/1 artifact")
    parser.add_argument("--evaluation", required=True,
                        help="path to the emitted mtj-foundry-m2-evaluation/1 report "
                             "graded from that same index")
    parser.add_argument("--output", required=True,
                        help="explicit directory to write the bundle into. the ONLY "
                             "place this command writes. a new path is created, an "
                             "empty one is used, a directory holding this builder's "
                             "own manifest is replaced file by file, and anything "
                             "else is refused")
    parser.add_argument("--verify", action="store_true",
                        help="after writing, re-read the bundle from disk and check "
                             "it against the source artifact: manifest digests, full "
                             "corpus population, and every anchor's candidate order "
                             "and tie blocks against mtj_foundry.retrieval.query")
    return parser


def _summary(manifest: dict, verification: dict) -> str:
    """A short operator page on stdout. The bundle itself carries the detail.

    Deliberately not the bundle's numbers restated by hand — every value here is
    read back out of the manifest that was just written, so a summary can never
    describe a build that did not happen.
    """
    population = manifest["population"]
    discovery = manifest["frozen_evaluation"]["aggregate_candidate_discovery"]
    presentation = manifest["frozen_evaluation"]["aggregate_presentation"]
    lines = [
        f"{manifest['pilot_schema']}  status={manifest['status']}",
        f"  files      {manifest['file_count']:,} "
        f"({manifest['total_bytes']:,} bytes, excluding {manifest['self_excluded']})",
        f"  source     index {manifest['source_artifacts']['index']['sha256']} "
        f"({manifest['source_artifacts']['index']['byte_size']:,} bytes)",
        f"             eval  {manifest['source_artifacts']['evaluation']['sha256']} "
        f"({manifest['source_artifacts']['evaluation']['byte_size']:,} bytes)",
        f"  corpus     {population['corpus_ids_total']:,} cards, "
        f"{population['corpus_ids_covered']:,} with active evidence, "
        f"{population['corpus_ids_uncovered']:,} UNASSIGNED_NO_ACTIVE_EVIDENCE",
        f"  frozen     discovery {discovery['discoverable']}/"
        f"{discovery['named_correct_total']}; "
        f"{presentation['in_a_tie_block_larger_than_one']}/"
        f"{presentation['discoverable_total']} discoverable sat in a tie block "
        f"larger than one",
    ]
    for key, value in verification.items():
        lines.append(f"  verified   {key}: {value}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    """Build one bundle. Returns a process exit status; never raises for input state."""
    args = build_parser().parse_args(argv)
    try:
        manifest = pilot.build(args.index, args.evaluation, args.output)
        verification = {}
        if args.verify:
            index = pilot.retrieval.load_index(args.index)
            pilot.verify_manifest(args.output)
            verification["manifest"] = "every emitted file matches its recorded digest"
            population = pilot.verify_population(args.output, index)
            verification["population"] = (
                f"{population['cards']:,} cards present, faces byte-equal")
            equivalence = pilot.verify_retrieval_equivalence(args.output, index)
            verification["retrieval"] = (
                f"{equivalence['anchors_checked']:,} anchors / "
                f"{equivalence['candidates_checked']:,} candidates / "
                f"{equivalence['tie_blocks_checked']:,} tie blocks equal to "
                f"mtj_foundry.retrieval.query")
    except runtime.FoundryRuntimeError as error:
        # HOUSE STYLE, at the one place it belongs. `PilotError` and every
        # retrieval refusal are `FoundryRuntimeError` subclasses, so this one
        # name covers a bad artifact, a schema rejection, an input disagreement
        # and a refused output directory alike.
        print(f"STOP — {error}", file=sys.stderr)
        return 1
    sys.stdout.write(_summary(manifest, verification))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
