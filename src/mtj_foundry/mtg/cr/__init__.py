"""The Comprehensive Rules substrate — the lower half of an acyclic pair.

This package derives facts from the Comprehensive Rules only. It never imports,
calls or references `mtj_foundry.mtg.shapes/**` -- including inside a function
body -- so the CR substrate remains the lower half of an acyclic pair
(`shapes -> cr -> edition -> infra`). Enforced by B10.

`find_home` and `keyword_homes()` deliberately do NOT live here: they consume
delivery parsing, so they belong with `mtg/shapes/delivery.py`. Placing them
here is exactly the cycle R6 was written to remove.

Not a re-export surface — import the owning module directly.
"""
