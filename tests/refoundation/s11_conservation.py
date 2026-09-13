"""S11 membership-conservation instruments — stdlib only, no repository imports.

Kept apart from `test_s11_codebook_kernel.py` on purpose: the pins in that test
were MEASURED by running THIS source against the accepted base's LEGACY
callables (which predate every `mtj_foundry.codebook_*` S11 owner), so this file
may import nothing that the base does not have.

Why a FINGERPRINT and not a count. Member conservation that compares totals is
blind to substitution: replacing one member's oracle_id with another's keeps
every count and silently changes what the codebook says. The fingerprint is
over what membership MEANS -- per axis, the status, the ordered member ids, the
member tier, and every assertion's full content.
"""

from __future__ import annotations

import hashlib
import json

__all__ = ["harness_spec", "membership_fingerprint", "partition_digest",
           "text_sha256"]


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def membership_fingerprint(codebook: dict) -> str:
    """sha256 over every axis's status and exact membership, in slug order."""
    rows = []
    for slug in sorted(codebook["axes"]):
        axis = codebook["axes"][slug]
        members = [[m["oracle_id"], m.get("tier"),
                    [json.dumps(a, sort_keys=True, ensure_ascii=False)
                     for a in m.get("assertions", [])]]
                   for m in axis.get("members", [])]
        rows.append([slug, axis.get("status"), members])
    return text_sha256(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))


def partition_digest(axis_patterns, prefilter_patterns, lattice_rows) -> str:
    """sha256 of the resolution partition: which record went where, in order."""
    return text_sha256(json.dumps({
        "axis": [[p["pattern_index"], p["resolved_slug"]] for p in axis_patterns],
        "prefilter": [p["pattern_index"] for p in prefilter_patterns],
        "lattice": [p["pattern_index"] for p in lattice_rows],
    }, sort_keys=True))


def harness_spec(codebook: dict) -> dict:
    """A deterministic spec exercising every membership operation on `codebook`.

    Derived from the document itself, so the same spec is produced wherever the
    same selected codebook is present. The choices keep the result lint-clean:
    the multi-axis add copies a member carrying exactly one human assertion, and
    the seed is human-class.
    """
    axes = codebook["axes"]
    active = sorted(s for s, e in axes.items() if e.get("status") == "active"
                    and len(e.get("members", [])) >= 4)
    a, b, c, d = active[0], active[1], active[2], active[3]

    def ids(slug):
        return [m["oracle_id"] for m in axes[slug]["members"]]

    def one_human(slug, oid):
        m = next(m for m in axes[slug]["members"] if m["oracle_id"] == oid)
        return len(m["assertions"]) == 1 and m["assertions"][0]["class"] == "human"

    in_b_or_c = set(ids(b)) | set(ids(c))
    move_member = ids(a)[0]
    add_member = next(o for o in ids(a)[1:] if o not in in_b_or_c and one_human(a, o))
    scope_now = axes[a].get("scope")
    return {
        "batch": "s11-conservation", "ruling": "docs/S11-CONSERVATION.md",
        "source_ref": "captain-cli-2026-09-13",
        "new_axes": {"rule:s11-conservation-new-axis": {
            "definition": "conservation fixture", "scope": "self", "note": "fixture"}},
        "renames": {d: {"to": "rule:s11-conservation-renamed", "why": "fixture",
                        "definition": "renamed fixture"}},
        "merges": [{"from": c, "to": b, "why": "fixture merge"}],
        "moves": [{"from": a, "to": "rule:s11-conservation-new-axis",
                   "members": [move_member], "why": "fixture move"}],
        "adds": [{"from": a, "to": b, "member": add_member,
                  "quote": "conservation fixture quote", "why": "fixture add"}],
        "seeds": [{"to": "rule:s11-conservation-new-axis", "member": ids(d)[0],
                   "quote": "conservation seed quote", "class": "human",
                   "why": "fixture seed"}],
        "drops": [{"from": b, "member": ids(b)[0], "why": "fixture drop"}],
        "quote_edits": {b: {ids(b)[1]: "conservation edited quote"}},
        "definition_edits": {a: "conservation fixture definition"},
        "scope_edits": {a: "opponent" if scope_now != "opponent" else "self"},
    }
