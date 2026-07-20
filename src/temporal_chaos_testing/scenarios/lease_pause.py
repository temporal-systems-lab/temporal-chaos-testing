from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LeaseOutcome:
    original_token: int
    replacement_token: int
    pause_ms: int
    stale_write_without_fencing: bool
    stale_write_with_fencing: bool


def simulate_lease_pause(*, lease_ms: int = 5_000, pause_ms: int = 10_000) -> LeaseOutcome:
    original_token = 7
    replacement_token = 8 if pause_ms > lease_ms else 7
    return LeaseOutcome(
        original_token=original_token,
        replacement_token=replacement_token,
        pause_ms=pause_ms,
        stale_write_without_fencing=pause_ms > lease_ms,
        stale_write_with_fencing=original_token >= replacement_token,
    )


def main() -> int:
    outcome = simulate_lease_pause()
    print(f"pause injectée           : {outcome.pause_ms} ms")
    print(f"token initial            : {outcome.original_token}")
    print(f"token du nouveau leader  : {outcome.replacement_token}")
    print(f"sans fencing             : {'écriture stale acceptée' if outcome.stale_write_without_fencing else 'bloqué'}")
    print(f"avec fencing             : {'écriture stale acceptée' if outcome.stale_write_with_fencing else 'écriture stale rejetée'}")
    print("assertion : une lease expirée exige un fencing token monotone côté ressource.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())