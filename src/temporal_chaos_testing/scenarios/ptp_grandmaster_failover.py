from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrandmasterSnapshot:
    name: str
    priority1: int
    clock_class: int
    offset_ns: int


@dataclass(frozen=True)
class FailoverOutcome:
    previous: str
    replacement: str
    holdover_ns: int
    phase_step_ns: int
    degraded: bool


def choose_best_master(candidates: list[GrandmasterSnapshot]) -> GrandmasterSnapshot:
    return min(candidates, key=lambda item: (item.priority1, item.clock_class, abs(item.offset_ns), item.name))


def simulate_failover() -> FailoverOutcome:
    primary = GrandmasterSnapshot(name="gm-a", priority1=128, clock_class=6, offset_ns=50)
    backup = GrandmasterSnapshot(name="gm-b", priority1=128, clock_class=7, offset_ns=820)
    selected_before = choose_best_master([primary, backup])
    selected_after = choose_best_master([backup])
    holdover_ns = 300
    phase_step_ns = selected_after.offset_ns - selected_before.offset_ns
    degraded = abs(phase_step_ns) > 500
    return FailoverOutcome(
        previous=selected_before.name,
        replacement=selected_after.name,
        holdover_ns=holdover_ns,
        phase_step_ns=phase_step_ns,
        degraded=degraded,
    )


def main() -> int:
    outcome = simulate_failover()
    print(f"grandmaster initial   : {outcome.previous}")
    print(f"grandmaster de secours: {outcome.replacement}")
    print(f"holdover intermédiaire: {outcome.holdover_ns} ns")
    print(f"saut de phase         : {outcome.phase_step_ns} ns")
    print(f"qualité dégradée      : {outcome.degraded}")
    print("assertion : un failover PTP doit propager une métrique de qualité, pas un faux temps parfait.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())