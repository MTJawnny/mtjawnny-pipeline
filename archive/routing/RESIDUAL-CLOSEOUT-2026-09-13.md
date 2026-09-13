# Residual routing closeout provenance — 2026-09-13

This is evidence, not task authority. Current task selection remains GitHub Issue #1 latest `K` -> active `T`.

Base cleanup evidence head: `7aa321d656c211a7dd54103ed9b4e45950bd2b08`.

This closeout integrates the separately reviewed R8.3 and AG-CLI-01 conservation work into the cleanup lineage and retires the remaining unbannered routing hazards identified by `archive/routing/FINAL-VERIFICATION-2026-09-13.md`. It does not advance accepted h, merge a branch, resume AQ4, or authorize S10–S16.

## Sole-home law conservation

| law | historical live home | canonical live home | byte-exact archive | original Git blob |
|---|---|---|---|---|
| `R8.3` | `docs/B-CONSOLIDATION-REAUDIT-PACKET.md` | `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md` | `archive/routing/docs/B-CONSOLIDATION-REAUDIT-PACKET.md` | `3f57d5cd9909aed5e8d9de6a8fbfa9c096f0ab44` |
| `AG-CLI-01` | `docs/B-MIGRATION-DIRECTIVE.md` | `docs/MEMBER-ADD-MUTATION-LAW.md` | `archive/routing/docs/B-MIGRATION-DIRECTIVE.md` | `213206b6560d9f097ae86af1673b4630a1c1a64a` |

The historical re-audit generator is also preserved byte-exact at `archive/routing/experiments/foundry_build_reaudit_packet.py`, blob `3a1fd7019c8c4d9f37054f5f1fc91e2b13bc41d0`. Its old live path is a halt-loudly tombstone so it cannot silently regenerate stale routing.

## Residual stale-routing retirement

| former live path | byte-exact archive | original Git blob | live disposition |
|---|---|---|---|
| `docs/T3-BUILDOUT-PLAYBOOK.md` | `archive/routing/docs/T3-BUILDOUT-PLAYBOOK.md` | `d4cffd89edddc15deb9a13c875365c4e019c492b` | inert compatibility stub; mechanically preserves registry references |
| `docs/T3-AXIS-FOUNDRY-v3.md` | `archive/routing/docs/T3-AXIS-FOUNDRY-v3.md` | `2b89ea43fa371945ee9f8b487758d4dddb2d60cc` | inert compatibility stub; mechanically preserves registry references |
| `docs/WORK-PACKETS-2026-08-07.md` | `archive/routing/docs/WORK-PACKETS-2026-08-07.md` | `e1bab565d6da493016d65fdef298eb4412f96e4a` | inert compatibility stub; mechanically preserves registry references |

## AQ4 classification

`docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md` no longer presents itself as current task routing. Its exact prior bytes are frozen at `archive/routing/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`, original blob `92e254b222c76f4570d0870b371bfd371093a4c0`.

The live compatibility path states only that AQ4 is PAUSED and points to the frozen contract. Archival does not withdraw or amend its pre-registered benchmark commitments; they remain evidence/input if the Captain later reauthorizes AQ4. It grants no current AQ4 execution authority.

## Verification boundary

`tests/refoundation/test_residual_routing_closeout.py` pins every archived original by Git blob identity, requires the live direct paths to be inert, verifies the two canonical law statements, checks the retired re-audit generator fails loudly, and includes a reactivation negative control.

Full canonical Gate 2 remains a separate executable acceptance requirement. This evidence file does not claim that execution has occurred on the residual closeout head.
