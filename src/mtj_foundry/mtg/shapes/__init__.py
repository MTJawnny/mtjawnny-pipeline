"""The MTG ability-shape substrate — the upper half of an acyclic pair.

`shapes -> cr -> edition -> infra`. A shapes module may consume the CR
substrate; the CR substrate may never consume this one, including through a
function-local import. Enforced by B10.

`find_home` and `keyword_homes()` live here, in `delivery.py`, because they
consume delivery parsing. That placement IS the R6 repair: putting them in the
CR half is the cycle, and the legacy `_twin` cross-instance state sync existed
only to survive it.

Not a re-export surface — import the owning module directly.
"""
