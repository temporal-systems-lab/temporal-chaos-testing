from __future__ import annotations

import unittest

from temporal_chaos_testing.cli import build_scenarios, packaged_scenario_path


class ChaosCliTests(unittest.TestCase):
    def test_scenario_registry_contains_expected_entries(self) -> None:
        scenarios = build_scenarios()

        self.assertEqual(sorted(scenarios), ["controlled-clock", "faketime", "space"])

    def test_python_scenarios_use_module_invocation(self) -> None:
        scenarios = build_scenarios()

        self.assertEqual(
            scenarios["controlled-clock"].command[1:],
            ("-m", "temporal_chaos_testing.scenarios.controlled_clock"),
        )
        self.assertEqual(
            scenarios["space"].command[1:],
            ("-m", "temporal_chaos_testing.scenarios.spice_time_demo"),
        )

    def test_faketime_scenario_uses_packaged_shell_script(self) -> None:
        scenarios = build_scenarios()

        self.assertEqual(scenarios["faketime"].command[0], "bash")
        self.assertEqual(scenarios["faketime"].command[1], packaged_scenario_path("faketime_demo.sh"))


if __name__ == "__main__":
    unittest.main()