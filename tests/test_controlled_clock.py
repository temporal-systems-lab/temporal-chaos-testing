from __future__ import annotations

import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).parents[1] / "chaos" / "controlled_clock_demo.py"
SPEC = importlib.util.spec_from_file_location("controlled_clock_demo", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ControlledClock = MODULE.ControlledClock
simulate_step_back = MODULE.simulate_step_back


class ControlledClockTests(unittest.TestCase):
    def test_controlled_clock_advances_by_delta(self) -> None:
        clock = ControlledClock(100)
        clock.advance_ms(25)
        self.assertEqual(clock.now_ms(), 125)

    def test_simulated_step_back_makes_wall_elapsed_negative_only_for_wall_clock(self) -> None:
        wall_elapsed, mono_elapsed = simulate_step_back()
        self.assertEqual(wall_elapsed, -2000)
        self.assertEqual(mono_elapsed, 150)


if __name__ == "__main__":
    unittest.main()