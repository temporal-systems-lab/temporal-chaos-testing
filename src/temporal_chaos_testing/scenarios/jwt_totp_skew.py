from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import struct


SECRET = b"temporal-chaos-secret"


@dataclass(frozen=True)
class AuthSkewOutcome:
    server_skew_s: int
    jwt_valid: bool
    totp_valid: bool


def validate_jwt(now_s: int, *, not_before_s: int, expires_at_s: int, leeway_s: int = 30) -> bool:
    return (not_before_s - leeway_s) <= now_s <= (expires_at_s + leeway_s)


def generate_totp(secret: bytes, unix_time_s: int, *, step_s: int = 30, digits: int = 6) -> str:
    counter = unix_time_s // step_s
    payload = struct.pack(">Q", counter)
    digest = hmac.new(secret, payload, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = int.from_bytes(digest[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(code % (10 ** digits)).zfill(digits)


def validate_totp(token: str, secret: bytes, unix_time_s: int, *, step_s: int = 30, window: int = 1) -> bool:
    for delta in range(-window, window + 1):
        candidate_time = unix_time_s + delta * step_s
        if generate_totp(secret, candidate_time, step_s=step_s) == token:
            return True
    return False


def simulate_auth_skew(*, server_skew_s: int = 95) -> AuthSkewOutcome:
    client_now_s = 1_700_000_000
    server_now_s = client_now_s + server_skew_s
    token = generate_totp(SECRET, client_now_s)
    return AuthSkewOutcome(
        server_skew_s=server_skew_s,
        jwt_valid=validate_jwt(server_now_s, not_before_s=client_now_s - 5, expires_at_s=client_now_s + 60),
        totp_valid=validate_totp(token, SECRET, server_now_s, window=1),
    )


def main() -> int:
    outcome = simulate_auth_skew()
    print(f"skew serveur : {outcome.server_skew_s} s")
    print(f"JWT accepté  : {outcome.jwt_valid}")
    print(f"TOTP accepté : {outcome.totp_valid}")
    print("assertion : JWT, TOTP et fenêtres anti-rejeu exigent un skew explicitement borné.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())