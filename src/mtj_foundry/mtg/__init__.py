"""L2 — the shared MTG/card semantic substrate.

Knows what a card, an ability and the Comprehensive Rules are; knows nothing
about the codebook, axes, membership, evidence, the thesaurus or any operator
tool. Imports may only go down: `mtg` may reach `infra`, never the reverse, and
never upward into `codebook`, `evidence`, `thesaurus`, `products` or `ops`.

Not a re-export surface — import the owning module directly.
"""
