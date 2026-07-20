from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoldoverSample:
    profile: str
    elapsed_seconds: int
    phase_error_ns: float


def phase_error_ns(fractional_error: float, elapsed_seconds: int, *, initial_phase_ns: float = 0.0) -> float:
    return initial_phase_ns + fractional_error * elapsed_seconds * 1_000_000_000


def simulate_holdover() -> list[HoldoverSample]:
    profiles = (("xo", 2e-8), ("ocxo", 1e-11))
    checkpoints = (1, 60, 3600)
    return [
        HoldoverSample(profile, elapsed_seconds, phase_error_ns(fractional_error, elapsed_seconds))
        for profile, fractional_error in profiles
        for elapsed_seconds in checkpoints
    ]


def main() -> int:
    print("perte de référence -> holdover local")
    for sample in simulate_holdover():
        value = sample.phase_error_ns
        unit = "ns"
        if abs(value) >= 1_000:
            value /= 1_000
            unit = "us"
        print(f"{sample.profile:>4}  t={sample.elapsed_seconds:>4}s  erreur={value:>7.3f} {unit}")
    print("assertion : le budget d'incertitude doit couper le service avant la zone invalide.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())