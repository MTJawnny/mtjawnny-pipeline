"""The bounded wave: a set of pre-authorized work units with explicit order.

A wave is the unit that replaces the one-microtask-per-review cadence. One
selected `T` may authorize many units; the Worker may cross unit boundaries
without asking, and may not cross the WAVE boundary -- that is where independent
Manager review happens, and finishing a unit is explicitly not a STOP.

The order this module derives is DETERMINISTIC: the same plan always yields the
same sequence, on any machine, so a resumed session executes the remainder of
the same order rather than a plausible one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError


@dataclass(frozen=True)
class Unit:
    id: str
    objective: str
    depends_on: tuple[str, ...]
    allow_paths: tuple[str, ...]
    validation: tuple[str, ...]
    mutating: bool
    deny_paths: tuple[str, ...] = ()
    negative_controls: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    commit_boundary: bool = True
    concurrency: str = "SERIAL"
    note: str = ""

    @classmethod
    def from_body(cls, raw: Mapping[str, Any]) -> "Unit":
        return cls(
            id=raw["id"],
            objective=raw["objective"],
            depends_on=tuple(raw["depends_on"]),
            allow_paths=tuple(raw["allow_paths"]),
            validation=tuple(raw["validation"]),
            mutating=bool(raw["mutating"]),
            deny_paths=tuple(raw.get("deny_paths", ())),
            negative_controls=tuple(raw.get("negative_controls", ())),
            stop_conditions=tuple(raw.get("stop_conditions", ())),
            commit_boundary=bool(raw.get("commit_boundary", True)),
            concurrency=raw.get("concurrency", "SERIAL"),
            note=raw.get("note", ""),
        )


@dataclass(frozen=True)
class WavePlan:
    wave: str
    branch: str
    review_boundary: str
    units: tuple[Unit, ...]
    stop_conditions: tuple[str, ...] = ()
    order: tuple[str, ...] = field(default=())

    def unit(self, unit_id: str) -> Unit:
        for u in self.units:
            if u.id == unit_id:
                return u
        raise KeyError(unit_id)


def plan_from_command(wave: str, body: Mapping[str, Any]) -> WavePlan:
    """Build and fully validate a wave plan from a WAVE_COMMAND body."""
    units = tuple(Unit.from_body(u) for u in body["units"])
    if not units:
        raise BusError(E.EMPTY_WAVE, f"wave {wave} authorizes no units")

    seen: set[str] = set()
    for unit in units:
        if unit.id in seen:
            raise BusError(E.DUPLICATE_UNIT_ID, f"unit {unit.id} declared twice")
        seen.add(unit.id)

    for unit in units:
        for dep in unit.depends_on:
            if dep not in seen:
                raise BusError(E.UNKNOWN_DEPENDENCY, f"unit {unit.id} depends on unknown {dep}")
            if dep == unit.id:
                raise BusError(E.DEPENDENCY_CYCLE, f"unit {unit.id} depends on itself")

    return WavePlan(
        wave=wave,
        branch=body["branch"],
        review_boundary=body["review_boundary"],
        units=units,
        stop_conditions=tuple(body.get("stop_conditions", ())),
        order=execution_order(units),
    )


def execution_order(units: Sequence[Unit]) -> tuple[str, ...]:
    """Topological order, ties broken by declared position.

    Declared position -- not id, not insertion into a set -- is the tiebreak, so
    the Manager's own ordering survives into execution and two machines agree.
    """
    position = {unit.id: index for index, unit in enumerate(units)}
    remaining = {unit.id: set(unit.depends_on) for unit in units}
    ordered: list[str] = []
    while remaining:
        ready = sorted((uid for uid, deps in remaining.items() if not deps), key=position.__getitem__)
        if not ready:
            stuck = ", ".join(sorted(remaining))
            raise BusError(E.DEPENDENCY_CYCLE, f"cycle among: {stuck}")
        for uid in ready:
            ordered.append(uid)
            del remaining[uid]
        for deps in remaining.values():
            deps.difference_update(ready)
    return tuple(ordered)


def remaining_after(plan: WavePlan, completed: Iterable[str], failed: Iterable[str] = ()) -> dict:
    """Resume arithmetic: what is left, what is blocked, and why.

    `completed` and `failed` come from DURABLE evidence -- posted progress
    messages and commit trailers -- never from a session's memory of what it
    thinks it did.
    """
    done = set(completed)
    bad = set(failed)
    unknown = sorted((done | bad) - {u.id for u in plan.units})
    if unknown:
        raise BusError(E.UNKNOWN_DEPENDENCY, f"not units of wave {plan.wave}: {', '.join(unknown)}")

    blocked: dict[str, list[str]] = {}
    runnable: list[str] = []
    for uid in plan.order:
        if uid in done or uid in bad:
            continue
        unit = plan.unit(uid)
        reasons = sorted(dep for dep in unit.depends_on if dep in bad or dep in blocked)
        if reasons:
            blocked[uid] = reasons
        else:
            runnable.append(uid)
    return {
        "wave": plan.wave,
        "order": list(plan.order),
        "completed": sorted(done),
        "failed": sorted(bad),
        "runnable": runnable,
        "blocked": {k: blocked[k] for k in sorted(blocked)},
        "next": runnable[0] if runnable else None,
        "wave_complete": not runnable and not blocked,
    }
