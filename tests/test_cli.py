from __future__ import annotations

import unittest

from temporal_chaos_testing.cli import build_scenarios, project_root


class ChaosCliTests(unittest.TestCase):
    def test_scenario_registry_contains_expected_entries(self) -> None:
        scenarios = build_scenarios()

        self.assertEqual(sorted(scenarios), ["controlled-clock", "faketime", "space"])

    def test_scenario_paths_are_local_to_repository(self) -> None:
        root = project_root()
        scenarios = build_scenarios()

        for scenario in scenarios.values():
            target = scenario.command[-1]
            self.assertTrue(str(root) in target)


if __name__ == "__main__":
    unittest.main()