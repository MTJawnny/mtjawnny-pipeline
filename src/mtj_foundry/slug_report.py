"""Slug validation report — the operator CLI over the slug grammar.

## What this is

The CLI S11 left in the legacy `validate_slug` shell: with slugs as arguments,
print each validation result as JSON; with `--batch`, validate every active axis
slug of the codebook, summarise, and write the batch report; with nothing,
print the usage text and exit 1. S13 moved it here. Output bytes, the report
document and the exit status are the shell's.

## What this is NOT

* **Not the slug grammar.** The six checks, every vocabulary and the collision
  law are `mtj_foundry.codebook_slug`; the shell's `validate_slug` facade hands
  them its closed vocabulary at call time, and that facade is what is called.
* **Not a reader, writer or process boundary.** The codebook read, the report
  location and its writer, the usage text and the process exit belong to the
  composition boundary. `run` returns the exit status; it never exits.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Callable

__all__ = ["SlugReportContext", "batch_summary", "run"]


@dataclasses.dataclass(frozen=True)
class SlugReportContext:
    usage: str
    read_codebook: Callable[[], dict]
    validate_slug: Callable[..., dict]
    report_path: Path
    write_json: Callable[[Path, dict], None]


def batch_summary(results: list) -> dict:
    n_fail = sum(1 for r in results if not r["ok"])
    n_warn_only = sum(1 for r in results if r["ok"] and r["warnings"])
    n_clean = len(results) - n_fail - n_warn_only
    return {"total": len(results), "clean": n_clean, "warned": n_warn_only,
            "flagged": n_fail, "results": results}


def run(args: list, ctx: SlugReportContext) -> int:
    if not args:
        print(ctx.usage)
        return 1

    if args[0] == "--batch":
        codebook = ctx.read_codebook()
        axes = codebook["axes"]
        active_slugs = sorted(s for s, e in axes.items() if e.get("status") == "active")
        results = []
        for slug in active_slugs:
            defn = axes[slug].get("definition")
            results.append(ctx.validate_slug(slug, definition=defn, all_slugs=active_slugs))
        report = batch_summary(results)
        print(f"validated {report['total']} active slugs: {report['clean']} clean, "
              f"{report['warned']} warned (non-blocking), {report['flagged']} flagged")
        ctx.write_json(ctx.report_path, report)
        print(f"wrote {ctx.report_path}")
    else:
        for slug in args:
            print(json.dumps(ctx.validate_slug(slug), indent=2))
    return 0
