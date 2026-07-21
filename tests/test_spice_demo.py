from __future__ import annotations

from pathlib import Path
import unittest

from temporal_chaos_testing.scenarios.spice_time_demo import (
    default_manifest_path,
    ensure_utc_within_window,
    load_manifest,
    render_meta_kernel,
)


class SpiceDemoTests(unittest.TestCase):
    def test_manifest_uses_historical_reference_case(self) -> None:
        manifest = load_manifest(default_manifest_path())

        self.assertEqual(manifest["reference_case"]["utc"], "1979-01-09T12:00:00")
        self.assertEqual(manifest["spacecraft"]["spacecraft_id"], -31)

    def test_meta_kernel_uses_spice_directives(self) -> None:
        rendered = render_meta_kernel(
            [Path("/tmp/naif0012.tls"), Path("/tmp/vg100051.tsc")],
            source_manifest=Path("manifest.json"),
        )

        self.assertIn("\\begindata", rendered)
        self.assertIn("\\begintext", rendered)
        self.assertNotIn("//", rendered)

    def test_defensible_window_rejects_modern_extrapolation(self) -> None:
        manifest = load_manifest(default_manifest_path())

        ensure_utc_within_window(manifest, "1979-01-09T12:00:00")
        with self.assertRaises(ValueError):
            ensure_utc_within_window(manifest, "2026-07-09T12:00:00")


if __name__ == "__main__":
    unittest.main()