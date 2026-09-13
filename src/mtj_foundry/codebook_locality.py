"""Codebook-facing locality BINDING — the address law applied to live assertions.

## What this is

S7 owns the ratified address law itself (`mtj_foundry.mtg.shapes.locality`):
given a card and a quote it returns OWNER / SPAN / AMBIGUOUS / UNRESOLVED. That
module never reads a codebook. This one is the other half: it walks every
assertion on every ACTIVE axis of a codebook document and binds the law to it.

* `census` -- coverage over every live assertion with EXACT denominators,
  reporting owner coverage and evidence-location coverage SEPARATELY, plus the
  three STORED-address questions (`stored_owned`, `stored_mismatch`,
  `addressable_missing`) that a census computed from quotes alone cannot see.
* `unaddressed_rows` -- every live assertion the backfill will NOT address, with
  its reason, deterministically ordered.

## The resolver is INJECTED, and that is the S7 law, not a convenience

`resolve` is a parameter. The legacy shell passes its own module-level `resolve`
-- the S7 function behind the halt boundary, reading its card primitives through
`CardFaceRules` at call time -- and the Gate-2 locality guard's controls rig that
route. A binding that imported the resolver itself would bypass every rigged
route and turn those controls green without exercising them. This module also
never imports corpus storage: the cards arrive as an argument, so the pure
locality engine stays storage-agnostic and this binding stays reader-agnostic.

## What this is NOT

* No file reads: the shell loads the codebook (raw JSON, unchanged) and the
  gated corpus.
* No report rendering, no artifact writing, no determinism ×2 wrapper, no CLI
  (`render_unaddressed_md`, `cmd_report` stay operator-side, S13).
* It writes nothing and repairs nothing. An address is SNAPSHOT-RELATIVE; a
  disagreement is COUNTED, never reattached.

## Layer law

Stdlib plus the S7 status constants from `mtj_foundry.mtg.shapes.locality`.
"""

from __future__ import annotations

from typing import Callable

from mtj_foundry.mtg.shapes import locality as _locality

__all__ = ["census", "unaddressed_rows"]


def census(cards: dict, codebook_document: dict, resolve: Callable) -> dict:
    """Coverage over every live assertion, with EXACT denominators.

    Reports owner coverage and evidence-location coverage SEPARATELY. They are
    different questions and the pre-implementation check exists because
    substituting one for the other is how a broad quote comes to look owned.
    """
    OWNER, SPAN = _locality.OWNER, _locality.SPAN
    AMBIGUOUS, UNRESOLVED = _locality.AMBIGUOUS, _locality.UNRESOLVED
    m = {"assertions": 0, "quoted": 0, "quoteless": 0,
         "owned": 0, "span": 0, "ambiguous": 0, "unresolved": 0,
         # STORED coverage, added with the step-4 backfill. Everything above
         # measures what the resolver CAN address; these two measure what the
         # codebook actually CARRIES. Measured 2026-08-13, deleting all 7,808
         # stored addresses left every Gate 2 row green, because a census
         # computed from quotes reproduces itself perfectly on a file with the
         # field stripped out.
         #
         # Marker choice is deliberate and collision-checked against every
         # pinned section: `stored_owned` resolves WORSE_IF_DOWN through the
         # pre-existing "owned" marker and `stored_mismatch` resolves
         # WORSE_IF_UP through "mismatch".
         "stored_owned": 0, "stored_mismatch": 0,
         # THE THIRD QUESTION. An assertion the resolver addresses to exactly
         # one OWNER, whose stored `locality` is ABSENT. Correct value: 0. A
         # ratchet on a total cannot see a compensated loss; only a
         # per-assertion join of "is addressable" against "is addressed" can.
         #
         # EXCLUSIONS, all by ratification: AMBIGUOUS, SPAN, UNRESOLVED and
         # quoteless assertions are NOT missing -- the resolver declines to
         # address them, so an absent address is the correct state. Tombstone
         # (non-active) axes stay outside the active-axis locality contract.
         "addressable_missing": 0}
    for slug, axis in codebook_document["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            card = cards.get(member["oracle_id"])
            for a in member["assertions"]:
                m["assertions"] += 1
                q = a.get("quote")
                stored = a.get("locality")
                if stored is not None:
                    m["stored_owned"] += 1
                if not q:
                    m["quoteless"] += 1
                    # A stored address with no quote is unfalsifiable; lint
                    # already rejects it, so reaching here is a mismatch.
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                m["quoted"] += 1
                if card is None:
                    m["unresolved"] += 1
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                r = resolve(card, q)
                m[{OWNER: "owned", SPAN: "span", AMBIGUOUS: "ambiguous",
                   UNRESOLVED: "unresolved"}[r["status"]]] += 1
                # REPORTED, never silently reattached.
                if stored is not None and (
                        r["status"] != OWNER or list(r["owner"]) != list(stored)):
                    m["stored_mismatch"] += 1
                # Addressable but unaddressed. Keyed on OWNER only, so the four
                # unaddressed-by-rule statuses can never reach it.
                if r["status"] == OWNER and stored is None:
                    m["addressable_missing"] += 1
    return m


def unaddressed_rows(cards: dict, codebook_document: dict, resolve: Callable) -> list:
    """Every live assertion the backfill will NOT address, with its reason.

    Deterministically ordered: (reason, slug, oracle_id, class, source_ref).
    Nothing here reads a card name as a code path -- names are carried for the
    human reading the sheet.
    """
    OWNER = _locality.OWNER
    rows = []
    for slug, axis in codebook_document["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            oid = member["oracle_id"]
            card = cards.get(oid)
            for a in member["assertions"]:
                q = a.get("quote")
                if not q:
                    reason, detail, cands = "QUOTELESS", (
                        "assertion carries no evidence quote"), []
                elif card is None:
                    reason, detail, cands = "UNRESOLVED", (
                        "oracle_id is not in the gated corpus"), []
                else:
                    r = resolve(card, q)
                    if r["status"] == OWNER:
                        continue
                    reason = r["status"]
                    detail = r["reason"]
                    cands = [list(c) for c in r["candidates"]]
                rows.append({
                    "reason": reason,
                    "axis": slug,
                    "oracle_id": oid,
                    "card": (card or {}).get("name", "(not in corpus)"),
                    "class": a.get("class"),
                    "source_ref": a.get("source_ref"),
                    "quote": q or "",
                    "candidates": cands,
                    "detail": detail,
                })
    rows.sort(key=lambda r: (r["reason"], r["axis"], r["oracle_id"],
                             r["class"] or "", r["source_ref"] or ""))
    return rows
