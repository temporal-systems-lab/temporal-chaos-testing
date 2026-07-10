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
        "space": Scenario(
            name="space",
            description="run the SPICE time conversion demo with optional kernel download",
            risk="lab-download",
            command=(python, "-m", "temporal_chaos_testing.scenarios.spice_time_demo")
        )
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="temporal-chaos", description="Temporal chaos testing launcher")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list available scenarios")
    controlled_clock = subparsers.add_parser("controlled-clock", help="run the deterministic rollback scenario")
    controlled_clock.add_argument("--dry-run", action="store_true", help="print the underlying command without executing it")
    faketime = subparsers.add_parser("faketime", help="run the libfaketime lab scenario")
    faketime.add_argument("--ack-lab-risk", action="store_true", help="acknowledge that this scenario is for isolated lab use only")
    faketime.add_argument("--dry-run", action="store_true", help="print the underlying command without executing it")
    space = subparsers.add_parser("space", help="run the SPICE scenario")
    space.add_argument("--download", action="store_true", help="download missing kernels before running")
    space.add_argument("--ack-network-download", action="store_true", help="acknowledge that kernel download uses the network and should happen only in an isolated lab context")
    space.add_argument("--dry-run", action="store_true", help="print the underlying command without executing it")
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
    if args.command == "controlled-clock":
        return run_scenario(scenarios["controlled-clock"], dry_run=args.dry_run)
    if args.command == "faketime":
        if not args.ack_lab_risk:
            parser.error("faketime requires --ack-lab-risk because it is reserved for isolated laboratory environments")
        if shutil.which("faketime") is None and not args.dry_run:
            print("faketime binary not found; install libfaketime before running this scenario")
            return 1
        return run_scenario(scenarios["faketime"], dry_run=args.dry_run)
    if args.command == "space":
        if args.download and not args.ack_network_download:
            parser.error("space --download requires --ack-network-download")
        extra_args = ["--download"] if args.download else []
        return run_scenario(scenarios["space"], extra_args, dry_run=args.dry_run)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())