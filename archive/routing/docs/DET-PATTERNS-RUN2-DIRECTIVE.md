# DET-PATTERNS-RUN2-DIRECTIVE — three new patterns via the standing flow (session 4 of 4)

ZERO API SPEND. PRECONDITION: session 3 complete. Governed by
B-MIGRATION-DISCOVERY.md §10 (A2, A8) and the standing DET pattern
discipline (ADDENDUM-4 §4: patterns versioned like scoring constants,
fixed-seed 20-hit sample sheets, any failure halts before provenance
writes).

## 1. Draft three patterns (proposal stage)

1. `rule:activated-regenerate-self` — "Regenerate [CARDNAME]"-shaped
   activated abilities (closes the b3 "kill, then decompose" debt;
   R8.3). All-faces, polarity, per-clause subject checks per DET
   preprocessing standard v1.
2. `rule:grants-team-trample` — static team-scope trample grants
   (revived-deferred axis, A2; analogue: grants-haste-to-your-creatures,
   det-patterns-v2:20).
3. `rule:grants-haste-to-reanimated-creature` — reanimation-context
   haste grants (revived-deferred axis, A2).

For each: measured corpus hit list (gate-passing cards only, Gate #0),
fixed-seed 20-hit sample sheet to files (names + quotes in the FILE,
never console), proposed as det-patterns-v3.json DRAFT entries
(det-patterns-v2 stays authoritative until ratification).

## 2. STOP for Captain pattern ratification

Sample sheets are the ratification instrument. No membership writes, no
status flips, until Captain rules per pattern.

## 3. On ratification (may be a continuation or a fresh trigger)

- det-patterns-v3.json finalized (v2 entries carried forward unchanged).
- DET apply per the migrated A8 semantics: rule-derived assertions
  merged (source_ref="det-patterns-v3:<index>", matched-clause quotes,
  corpus_ref); existing human/llm assertions untouched.
- The two revived axes flip deferred → active on their first landed
  membership (A2), history-logged.
- Gates: sample-sheet PASS precondition, backup law, lint,
  determinism ×2, exact-count report.

## 4. Report

Per-pattern hit counts, flips executed, codebook sha256, spend $0.00 /
cumulative $90.51 / headroom $49.49, commits. Punch item to carry
forward: future Scryfall-refresh DET passes now run v3.

## 4a. NEW-02 — `rule:forced-attack-each-combat` widening (measured 2026-08-02, NOT applied)

The F-C pattern bug, measured against the live gated corpus so session 4
ratifies against numbers rather than the prose estimate. **Nothing is
applied here — the pattern is ratified and rides the sample-sheet gate
like any other.**

Current (`det-patterns-v2.json`, index per file):

```
\bthis creature attacks each (?:combat|turn) if able\b
```

Proposed:

```
(?:\bthis creature|\~) attacks each (?:combat|turn) if able\b
```

Measured over 32,557 gate-passing cards, matching `det_scan_texts()` output:

| | hits |
|---|---:|
| current pattern | 59 |
| proposed pattern | 67 |
| **missed by current** | **8** |
| regressions (caught now, lost after) | **0** |

The 8 are all cards that self-reference by printed NAME, which
`canonicalize_self_reference()` rewrites to `~` before matching:
Alexios Deimos of Kosmos · Amarant Coral · Ares God of War · Hulk Always
Angry · Hulk Brutal Brawler · Ruric Thar the Unbowed · Toski Bearer of
Secrets · Xantcha Sleeper Agent. Disproportionately legendaries, which is
the tell — legendary oracle text self-references by name far more often
than by "this creature".

This is why F-C concluded the PATTERN was wrong and the model was right;
the 8 cards are a systematic false-negative class, not model noise.

**Standing guard now in place (no ruling needed, landed 2026-08-02):**
`foundry_common.pattern_misses_cardname_token()` flags any pattern
anchoring a self-reference form without also accepting `~`, and
`foundry_family_sweep` reports it BLOCKING. Only this one pattern trips it
today — `rule:innate-unblockable` already anchors `(?:this creature|\~)`.
Session-4 patterns must be authored against `det_scan_texts()` output or
the sweep will block them.

## 5. Standing discipline

Halt loudly · patterns are ratified rulings, never silently tuned ·
transcript hygiene · backups · determinism ×2 · one session, this work
item only.
