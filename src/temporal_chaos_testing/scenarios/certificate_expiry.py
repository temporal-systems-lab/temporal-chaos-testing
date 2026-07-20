from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CertificateWindow:
    not_before_s: int
    not_after_s: int


@dataclass(frozen=True)
class CertificateCheckOutcome:
    correct_status: str
    ahead_status: str
    behind_status: str


def certificate_status(now_s: int, certificate: CertificateWindow) -> str:
    if now_s < certificate.not_before_s:
        return "not-yet-valid"
    if now_s > certificate.not_after_s:
        return "expired"
    return "valid"


def simulate_certificate_checks() -> CertificateCheckOutcome:
    certificate = CertificateWindow(not_before_s=1_700_000_000, not_after_s=1_700_003_600)
    accurate_now = 1_700_003_500
    ahead_now = accurate_now + 180
    behind_now = certificate.not_before_s - 120
    return CertificateCheckOutcome(
        correct_status=certificate_status(accurate_now, certificate),
        ahead_status=certificate_status(ahead_now, certificate),
        behind_status=certificate_status(behind_now, certificate),
    )


def main() -> int:
    outcome = simulate_certificate_checks()
    print(f"horloge correcte : {outcome.correct_status}")
    print(f"horloge en avance : {outcome.ahead_status}")
    print(f"horloge en retard : {outcome.behind_status}")
    print("assertion : les champs notBefore/notAfter supposent une heure civile bornée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())