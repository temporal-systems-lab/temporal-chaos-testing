from __future__ import annotations

import argparse
from dataclasses import dataclass
from importlib import resources
import os
import shlex
import shutil
import subprocess
import sys

from . import __version__


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    risk: str
    command: tuple[str, ...]
    environment: dict[str, str] | None = None


def packaged_scenario_path(name: str) -> str:
    return str(resources.files("temporal_chaos_testing.scenarios").joinpath(name))


def build_scenarios() -> dict[str, Scenario]:
    python = sys.executable or "python3"
    return {
        "certificate-expiry": Scenario(
            name="certificate-expiry",
            description="simulate certificate validity windows under skewed civil clocks",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.certificate_expiry")
        ),
        "controlled-clock": Scenario(
            name="controlled-clock",
            description="inject a deterministic wall-clock rollback without mutating the host clock",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.controlled_clock")
        ),
        "faketime": Scenario(
            name="faketime",
            description="run the libfaketime demonstration in an isolated lab environment",
            risk="lab-only",
            command=("bash", packaged_scenario_path("faketime_demo.sh")),
            environment={"TEMPORAL_CHAOS_PYTHON": python}
        ),
        "holdover": Scenario(
            name="holdover",
            description="model source loss and holdover drift on local oscillators",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.holdover")
        ),
        "jwt-totp-skew": Scenario(
            name="jwt-totp-skew",
            description="show how skew breaks JWT leeway and TOTP validation windows",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.jwt_totp_skew")
        ),
        "leap-smear-mismatch": Scenario(
            name="leap-smear-mismatch",
            description="compare smeared and unsmeared UTC around an incompatible leap-second policy",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.leap_smear_mismatch")
        ),
        "lease-pause": Scenario(
            name="lease-pause",
            description="show why stale lease holders need fencing tokens after process pauses",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.lease_pause")
        ),
        "ptp-grandmaster-failover": Scenario(
            name="ptp-grandmaster-failover",
            description="simulate grandmaster loss, holdover, and phase step on PTP failover",
            risk="safe-lab",
            command=(python, "-m", "temporal_chaos_testing.scenarios.ptp_grandmaster_failover")
        ),
        "space": Scenario(
            name="space",
            description="run the SPICE time conversion demo with optional kernel download",
            risk="lab-download",
            command=(python, "-m", "temporal_chaos_testing.scenarios.spice_time_demo")
        )
    }


def add_dry_run_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true", help="print the underlying command without executing it")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="temporal-chaos", description="Temporal chaos testing launcher")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list available scenarios")
    certificate_expiry = subparsers.add_parser("certificate-expiry", help="simulate certificate notBefore/notAfter failures")
    add_dry_run_argument(certificate_expiry)
    controlled_clock = subparsers.add_parser("controlled-clock", help="run the deterministic rollback scenario")
    add_dry_run_argument(controlled_clock)
    faketime = subparsers.add_parser("faketime", help="run the libfaketime lab scenario")
    faketime.add_argument("--ack-lab-risk", action="store_true", help="acknowledge that this scenario is for isolated lab use only")
    add_dry_run_argument(faketime)
    holdover = subparsers.add_parser("holdover", help="model holdover drift after source loss")
    add_dry_run_argument(holdover)
    jwt_totp_skew = subparsers.add_parser("jwt-totp-skew", help="simulate JWT and TOTP failures under clock skew")
    add_dry_run_argument(jwt_totp_skew)
    leap_smear = subparsers.add_parser("leap-smear-mismatch", help="simulate incompatible leap smear policies")
    add_dry_run_argument(leap_smear)
    lease_pause = subparsers.add_parser("lease-pause", help="simulate stale lease holders after long pauses")
    add_dry_run_argument(lease_pause)
    ptp_failover = subparsers.add_parser("ptp-grandmaster-failover", help="simulate holdover and PTP grandmaster failover")
    add_dry_run_argument(ptp_failover)
    space = subparsers.add_parser("space", help="run the SPICE scenario")
    space.add_argument("--download", action="store_true", help="download missing kernels before running")
    space.add_argument("--ack-network-download", action="store_true", help="acknowledge that kernel download uses the network and should happen only in an isolated lab context")
    add_dry_run_argument(space)
    return parser


def run_scenario(scenario: Scenario, extra_args: list[str] | None = None, *, dry_run: bool = False) -> int:
    command = list(scenario.command)
    if extra_args:
        command.extend(extra_args)
    if dry_run:
        print(" ".join(shlex.quote(part) for part in command))
        return 0
    env = os.environ.copy()
    if scenario.environment:
        env.update(scenario.environment)
    completed = subprocess.run(command, check=False, env=env)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    scenarios = build_scenarios()

    if args.command == "list":
        for scenario in scenarios.values():
            print(f"{scenario.name}: {scenario.description} [{scenario.risk}]")
        return 0
    if args.command == "certificate-expiry":
        return run_scenario(scenarios["certificate-expiry"], dry_run=args.dry_run)
    if args.command == "controlled-clock":
        return run_scenario(scenarios["controlled-clock"], dry_run=args.dry_run)
    if args.command == "faketime":
        if not args.ack_lab_risk:
            parser.error("faketime requires --ack-lab-risk because it is reserved for isolated laboratory environments")
        if shutil.which("faketime") is None and not args.dry_run:
            print("faketime binary not found; install libfaketime before running this scenario")
            return 1
        return run_scenario(scenarios["faketime"], dry_run=args.dry_run)
    if args.command == "holdover":
        return run_scenario(scenarios["holdover"], dry_run=args.dry_run)
    if args.command == "jwt-totp-skew":
        return run_scenario(scenarios["jwt-totp-skew"], dry_run=args.dry_run)
    if args.command == "leap-smear-mismatch":
        return run_scenario(scenarios["leap-smear-mismatch"], dry_run=args.dry_run)
    if args.command == "lease-pause":
        return run_scenario(scenarios["lease-pause"], dry_run=args.dry_run)
    if args.command == "ptp-grandmaster-failover":
        return run_scenario(scenarios["ptp-grandmaster-failover"], dry_run=args.dry_run)
    if args.command == "space":
        if args.download and not args.ack_network_download:
            parser.error("space --download requires --ack-network-download")
        extra_args = ["--download"] if args.download else []
        return run_scenario(scenarios["space"], extra_args, dry_run=args.dry_run)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())