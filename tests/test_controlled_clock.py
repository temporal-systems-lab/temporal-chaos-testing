from __future__ import annotations

import importlib.util
import pathlib
import unittest

from temporal_chaos_testing.scenarios.certificate_expiry import simulate_certificate_checks
from temporal_chaos_testing.scenarios.holdover import phase_error_ns, simulate_holdover
from temporal_chaos_testing.scenarios.jwt_totp_skew import simulate_auth_skew
from temporal_chaos_testing.scenarios.leap_smear_mismatch import linear_smear_offset_ms, simulate_mismatch
from temporal_chaos_testing.scenarios.lease_pause import simulate_lease_pause
from temporal_chaos_testing.scenarios.ptp_grandmaster_failover import GrandmasterSnapshot, choose_best_master, simulate_failover


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

    def test_holdover_ocxo_matches_order_of_magnitude(self) -> None:
        self.assertAlmostEqual(phase_error_ns(1e-11, 3600), 36.0)
        samples = simulate_holdover()
        self.assertEqual(samples[0].profile, "xo")
        self.assertEqual(samples[-1].profile, "ocxo")

    def test_leap_smear_midpoint_can_reject_a_short_validity_window(self) -> None:
        self.assertEqual(linear_smear_offset_ms(43_200), 500)
        outcome = simulate_mismatch()
        self.assertTrue(outcome.strict_accepts)
        self.assertFalse(outcome.smeared_accepts)

    def test_certificate_status_changes_when_clock_skews(self) -> None:
        outcome = simulate_certificate_checks()
        self.assertEqual(outcome.correct_status, "valid")
        self.assertEqual(outcome.ahead_status, "expired")
        self.assertEqual(outcome.behind_status, "not-yet-valid")

    def test_lease_pause_requires_fencing(self) -> None:
        outcome = simulate_lease_pause()
        self.assertTrue(outcome.stale_write_without_fencing)
        self.assertFalse(outcome.stale_write_with_fencing)

    def test_auth_skew_breaks_jwt_and_totp_windows(self) -> None:
        outcome = simulate_auth_skew()
        self.assertFalse(outcome.jwt_valid)
        self.assertFalse(outcome.totp_valid)

    def test_ptp_failover_selects_backup_and_marks_quality_degraded(self) -> None:
        best = choose_best_master(
            [
                GrandmasterSnapshot(name="gm-a", priority1=128, clock_class=6, offset_ns=50),
                GrandmasterSnapshot(name="gm-b", priority1=128, clock_class=7, offset_ns=820),
            ]
        )
        self.assertEqual(best.name, "gm-a")
        outcome = simulate_failover()
        self.assertEqual(outcome.replacement, "gm-b")
        self.assertTrue(outcome.degraded)


if __name__ == "__main__":
    unittest.main()