"""Deterministic wall-clock rollback scenario packaged for CLI and wheel use."""

from __future__ import annotations


class ControlledClock:
    def __init__(self, value_ms: int):
        self.value_ms = value_ms

    def now_ms(self) -> int:
        return self.value_ms

    def advance_ms(self, delta_ms: int) -> None:
        self.value_ms += delta_ms


def simulate_step_back() -> tuple[int, int]:
    wall = ControlledClock(10_000)
    monotonic = ControlledClock(500)

    wall_start = wall.now_ms()
    mono_start = monotonic.now_ms()

    monotonic.advance_ms(150)
    wall.advance_ms(-2_000)

    wall_elapsed = wall.now_ms() - wall_start
    mono_elapsed = monotonic.now_ms() - mono_start
    return wall_elapsed, mono_elapsed


def main() -> int:
    wall_elapsed, mono_elapsed = simulate_step_back()
    print(f"durée wall-clock injectée : {wall_elapsed} ms")
    print(f"durée monotone injectée   : {mono_elapsed} ms")
    print("assertion : la durée métier doit venir de l'horloge monotone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())