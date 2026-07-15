"""Tests for the public aggregate activity dashboard."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "activity" / "generate_dashboard.py"
SPEC = importlib.util.spec_from_file_location("activity_dashboard", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load activity dashboard module")
dashboard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dashboard)


class ActivityDashboardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
            "profile": {"display_name": "Test", "github": "test"},
            "snapshot": {
                "captured_at": "2026-07-16",
                "lifetime_tokens": 1000,
                "peak_task_tokens": 500,
                "longest_task_minutes": 90,
                "current_streak_days": 2,
                "longest_streak_days": 4,
                "total_tasks": 5,
            },
            "daily": [],
        }

    def test_record_and_render_exact_daily_tokens(self) -> None:
        dashboard.record_daily_entry(
            self.data, "2026-07-16", 1200, 2, 1, 3, "Implemented dashboard"
        )
        svg = dashboard.render_svg(self.data)

        self.assertIn("2026-07-16: 1,200 tokens", svg)
        self.assertIn("1 exact day recorded", svg)
        self.assertNotIn("Implemented dashboard", svg)

    def test_duplicate_date_is_updated_not_appended(self) -> None:
        dashboard.record_daily_entry(
            self.data, "2026-07-16", 100, None, None, None, None
        )
        dashboard.record_daily_entry(
            self.data, "2026-07-16", 200, None, None, None, None
        )

        self.assertEqual(len(self.data["daily"]), 1)
        self.assertEqual(self.data["daily"][0]["tokens"], 200)

    def test_negative_or_duplicate_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dashboard.record_daily_entry(
                self.data, "2026-07-16", -1, None, None, None, None
            )

        self.data["daily"] = [
            {"date": "2026-07-16", "tokens": 1},
            {"date": "2026-07-16", "tokens": 2},
        ]
        with self.assertRaises(ValueError):
            dashboard.validate_data(self.data)

    def test_json_round_trip_is_reviewable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "usage.json"
            dashboard.write_json(path, self.data)
            loaded = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(loaded, self.data)


if __name__ == "__main__":
    unittest.main()
