"""L1 — domain-free infrastructure.

The lowest permanent layer: determinism, digests, ratchets and byte-format
ownership. Nothing here knows what a card, an axis, a codebook or the
Comprehensive Rules is, and nothing here may import upward.

DELIBERATELY NOT A RE-EXPORT SURFACE. The repository's package law keeps public
names in the module that owns them and leaves `mtj_foundry.__init__` carrying a
version and nothing else; a convenience façade here would create a second place
a symbol appears to live. Import `mtj_foundry.infra.conservation`,
`.conservation_contract`, `.ratchet` or `.artifact` directly.
"""
