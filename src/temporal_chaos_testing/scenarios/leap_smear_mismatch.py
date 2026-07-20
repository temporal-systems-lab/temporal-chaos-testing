from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LeapSmearOutcome:
    smear_offset_ms: int
    validity_ms: int
    strict_accepts: bool
    smeared_accepts: bool


def linear_smear_offset_ms(seconds_into_window: int, *, window_seconds: int = 86_400) -> int:
    if not 0 <= seconds_into_window <= window_seconds:
        raise ValueError("seconds_into_window must stay within the smear window")
    return round(1_000 * seconds_into_window / window_seconds)


def simulate_mismatch(*, validity_ms: int = 300, seconds_into_window: int = 43_200) -> LeapSmearOutcome:
    strict_now_ms = 1_000_000
    smear_offset_ms = linear_smear_offset_ms(seconds_into_window)
    deadline_ms = strict_now_ms + validity_ms
    smeared_now_ms = strict_now_ms + smear_offset_ms
    return LeapSmearOutcome(
        smear_offset_ms=smear_offset_ms,
        validity_ms=validity_ms,
        strict_accepts=strict_now_ms <= deadline_ms,
        smeared_accepts=smeared_now_ms <= deadline_ms,
    )


def main() -> int:
    outcome = simulate_mismatch()
    print(f"écart smear/UTC strict : {outcome.smear_offset_ms} ms")
    print(f"fenêtre de validité     : {outcome.validity_ms} ms")
    print(f"service UTC strict      : {'accepte' if outcome.strict_accepts else 'rejette'}")
    print(f"service lissé           : {'accepte' if outcome.smeared_accepts else 'rejette'}")
    print("assertion : un leap smear incompatible casse les TTL et fenêtres trop étroites.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())