"""Compat wrapper for the packaged deterministic rollback scenario."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from temporal_chaos_testing.scenarios.controlled_clock import ControlledClock, main, simulate_step_back


if __name__ == "__main__":
    raise SystemExit(main())
