"""Timelapse reports use metadata only and need neither wx nor a connected Pi."""

import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock


MODULE = Path(__file__).resolve().parents[1] / "info_modules" / "info_timelapse.py"
SPEC = importlib.util.spec_from_file_location("info_timelapse", MODULE)
info = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(info)


@contextlib.contextmanager
def london_timezone():
    try:
        with mock.patch.dict(os.environ, {"TZ": "Europe/London"}):
            time.tzset()
            yield
    finally:
        # patch.dict restores the previous TZ, including its absence, before
        # resetting the process timezone used by subsequent tests.
        time.tzset()


class TimelapseInfoTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="timelapse-info-")
        self.path = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def image(self, timestamp, name=None, size=16, mtime=None):
        path = self.path / (name or "cap_{}.jpg".format(timestamp))
        # Deliberately invalid image bytes: collection must not decode images.
        path.write_bytes(b"x" * size)
        os.utime(path, (timestamp if mtime is None else mtime,) * 2)
        return path

    def report(self, **kwargs):
        kwargs.setdefault("now", 1600)
        kwargs.setdefault("cron_text", "")
        return info.collect_info(path=str(self.path), **kwargs)

    def cron(self, expression="*/5 * * * *", path=None, script="camcap.py"):
        return '{} /home/pi/Pigrow/scripts/cron/{} caps="{}"'.format(expression, script, path or self.path)

    def test_count_runs_through_now_and_only_compares_same_window(self):
        self.image(900)
        self.image(1000)
        self.image(1100)
        report = self.report(interval="100", start="1000")
        summary = report["summary"]
        self.assertEqual(summary["image_count"], 3)
        self.assertEqual(summary["actual_count"], 2)
        self.assertEqual(summary["expected_count"], 7)
        self.assertEqual(summary["missing_count"], 5)
        self.assertEqual(summary["status"], "behind")
        self.assertEqual(summary["interval_source"], "explicit")
        self.assertEqual(summary["start_source"], "explicit")
        self.assertNotIn("points", report)
        self.assertNotIn("datawall_images", report)

    def test_expected_interval_boundaries_are_inclusive(self):
        self.image(1000)
        for now, expected in ((1000, 1), (1099.999, 1), (1100, 2), (1100.001, 2)):
            with self.subTest(now=now):
                self.assertEqual(self.report(interval="100", now=now)["summary"]["expected_count"], expected)
        for now, expected in ((1000.299999, 3), (1000.3, 4), (1000.300001, 4)):
            with self.subTest(fractional_now=now):
                self.assertEqual(self.report(interval="0.1", now=now)["summary"]["expected_count"], expected)

    def test_filename_timestamp_preferred_over_mtime_and_supported_images(self):
        self.image(1000.125, mtime=9000)
        self.image(1300, "custom.PNG", size=20)
        self.image(1400, "other.webp", size=30)
        self.image(1500, "not-a-photo.txt", size=100)
        (self.path / "directory.jpg").mkdir()
        report = self.report(detail="detailed", interval=100)
        self.assertEqual([point["timestamp"] for point in report["points"]], [1000.125, 1300, 1400])
        self.assertEqual(report["summary"]["total_bytes"], 66)
        self.assertEqual(report["latest"]["timestamp"], 1400)
        self.assertEqual(report["datawall_images"]["timelapse_latest"]["path"], str(self.path / "other.webp"))
        self.assertEqual(report["points"][0]["mtime"], 9000)

    def test_auto_interval_does_not_guess_from_file_gaps(self):
        for timestamp in (1000, 1100, 1200):
            self.image(timestamp)
        summary = self.report()["summary"]
        self.assertIsNone(summary["expected_count"])
        self.assertIsNone(summary["interval_seconds"])
        self.assertEqual(summary["interval_source"], "unknown")
        self.assertEqual(summary["status"], "unknown")
        self.assertTrue(summary["warnings"])

    def test_cron_count_includes_first_observed_minute_and_stopped_period(self):
        start = dt.datetime(2025, 1, 2, 12).timestamp()
        self.image(start + 2)
        self.image(start + 302)
        summary = self.report(cron_text=self.cron(), now=start + 1800)["summary"]
        self.assertEqual(summary["window_start"], start)
        self.assertEqual(summary["expected_count"], 7)
        self.assertEqual(summary["actual_count"], 2)
        self.assertEqual(summary["missing_count"], 5)
        self.assertEqual(summary["interval_seconds"], 300)
        self.assertEqual(summary["interval_source"], "cron")

    def test_cron_matches_capture_folder_and_ignores_disabled_jobs(self):
        start = dt.datetime(2025, 1, 2, 12).timestamp()
        self.image(start + 2)
        cron = "\n".join((self.cron("* * * * *", path="/other/camera"),
                          "# " + self.cron("* * * * *"),
                          self.cron("0 * * * *", script="libcam_cap.py")))
        summary = self.report(cron_text=cron, now=start + 3600)["summary"]
        self.assertEqual(summary["expected_count"], 2)
        self.assertEqual(summary["interval_seconds"], 3600)

    def test_cron_general_lists_ranges_steps_names_and_dom_dow_rule(self):
        schedule = info._CronSchedule("0,30 8-10 * JAN MON-FRI".split())
        begin = dt.datetime(2025, 1, 1).timestamp()  # Wednesday.
        end = dt.datetime(2025, 1, 6, 23, 59).timestamp()  # Monday.
        self.assertEqual(schedule.count(begin, end), 4 * 6)
        self.assertIsNone(schedule.regular_interval())
        # Both day selectors restricted means day-of-month OR weekday in cron.
        schedule = info._CronSchedule("0 12 1 * MON".split())
        self.assertEqual(schedule.count(begin, end), 2)
        schedule = info._CronSchedule("*/15 */2 * * *".split())
        self.assertEqual(schedule.count(begin, begin + 86400 - 1), 48)
        self.assertIsNone(schedule.regular_interval())  # Overnight gaps are longer.

    def test_cron_unknown_for_multiple_jobs_wrappers_and_extended_syntax(self):
        self.image(1000)
        jobs = (self.cron() + "\n" + self.cron("0 * * * *"),
                self.cron().replace("/home/pi/Pigrow/scripts/", "sudo /home/pi/Pigrow/scripts/"),
                self.cron("0 0 L * *"),
                "CRON_TZ=UTC\n" + self.cron(),
                self.cron("@reboot"))
        for cron in jobs:
            with self.subTest(cron=cron):
                summary = self.report(cron_text=cron)["summary"]
                self.assertIsNone(summary["expected_count"])
                self.assertEqual(summary["interval_source"], "unknown")

    def test_cron_hourly_macro_and_no_shell_subprocess(self):
        self.image(dt.datetime(2025, 1, 2, 12, 0, 2).timestamp())
        completed = mock.Mock(returncode=0, stdout=self.cron("@hourly"))
        with mock.patch.object(info.subprocess, "run", return_value=completed) as run:
            summary = self.report(cron_text=None, now=dt.datetime(2025, 1, 2, 14).timestamp())["summary"]
        self.assertEqual(summary["expected_count"], 3)
        self.assertEqual(run.call_args.args[0], ["crontab", "-l"])
        self.assertNotIn("shell", run.call_args.kwargs)

    def test_empty_and_unreadable_directories_are_reports(self):
        report = self.report(detail="detailed")
        self.assertEqual(report["summary"]["status"], "empty")
        self.assertIsNone(report["summary"]["expected_count"])
        self.assertEqual(len(report["selections"]), 5)
        self.assertTrue(all(value is None for value in report["datawall_images"].values()))
        explicit = self.report(interval=100, start=1000)["summary"]
        self.assertEqual(explicit["expected_count"], 7)
        self.assertEqual(explicit["missing_count"], 7)
        with mock.patch.object(info.os, "scandir", side_effect=PermissionError("denied")):
            failed = self.report(interval=100, start=1000)["summary"]
        self.assertEqual(failed["status"], "error")
        self.assertIsNone(failed["expected_count"])
        self.assertTrue(any("denied" in warning for warning in failed["warnings"]))

    def test_recent_selection_latest_first_and_five_keys(self):
        for timestamp in range(1000, 1600, 100):
            self.image(timestamp)
        report = self.report(detail="detailed")
        self.assertEqual([slot["timestamp"] for slot in report["selections"]], [1500, 1400, 1300, 1200, 1100])
        self.assertEqual(set(report["datawall_images"]), {"timelapse_latest"} | {"timelapse_{}".format(i) for i in range(1, 6)})

    def test_hourly_selection_never_fills_a_missing_hour_with_old_image(self):
        now = dt.datetime(2025, 1, 2, 15, 30).timestamp()
        t15 = dt.datetime(2025, 1, 2, 15, 1).timestamp()
        t13 = dt.datetime(2025, 1, 2, 13, 2).timestamp()
        t11 = dt.datetime(2025, 1, 2, 11, 10).timestamp()
        for timestamp in (t15, t15 + 60, t13, t11):
            self.image(timestamp)
        slots = self.report(now=now, detail="detailed", selection="hourly")["selections"]
        self.assertEqual([slot["timestamp"] for slot in slots], [t15, None, t13, None, t11])
        self.assertEqual(slots[0]["target"], dt.datetime(2025, 1, 2, 15).timestamp())

    def test_hourly_selection_chooses_nearest_on_either_side_without_reuse(self):
        now = dt.datetime(2025, 1, 2, 13, 25).timestamp()
        before = dt.datetime(2025, 1, 2, 12, 59).timestamp()
        self.image(before)
        self.image(dt.datetime(2025, 1, 2, 13, 20).timestamp())
        # At the midpoint a capture belongs to the later hour's centered window.
        midpoint = dt.datetime(2025, 1, 2, 11, 30).timestamp()
        self.image(midpoint)
        slots = self.report(now=now, detail="detailed", selection="hourly")["selections"]
        self.assertEqual([slot["timestamp"] for slot in slots], [before, midpoint, None, None, None])
        selected = [slot["path"] for slot in slots if slot["path"]]
        self.assertEqual(len(selected), len(set(selected)))

    @unittest.skipUnless(hasattr(time, "tzset"), "requires process timezone support")
    def test_hourly_fall_back_preserves_both_repeated_hours(self):
        with london_timezone():
            now = dt.datetime(2026, 10, 25, 1, 10, tzinfo=dt.timezone.utc).timestamp()
            latest_hour = now - 600
            expected = [latest_hour - index * 3600 for index in range(5)]
            for timestamp in expected:
                self.image(timestamp)
            slots = self.report(now=now, detail="detailed", selection="hourly")["selections"]
            self.assertEqual([slot["target"] for slot in slots], expected)
            self.assertEqual([slot["timestamp"] for slot in slots], expected)
            self.assertIn("01:00 GMT", slots[0]["label"])
            self.assertIn("01:00 BST", slots[1]["label"])

    @unittest.skipUnless(hasattr(time, "tzset"), "requires process timezone support")
    def test_hourly_spring_forward_skips_the_nonexistent_hour(self):
        with london_timezone():
            now = dt.datetime(2026, 3, 29, 1, 10, tzinfo=dt.timezone.utc).timestamp()
            latest_hour = now - 600
            expected = [latest_hour - index * 3600 for index in range(5)]
            for timestamp in expected:
                self.image(timestamp)
            slots = self.report(now=now, detail="detailed", selection="hourly")["selections"]
            self.assertEqual([slot["target"] for slot in slots], expected)
            self.assertEqual([slot["timestamp"] for slot in slots], expected)
            self.assertIn("02:00 BST", slots[0]["label"])
            self.assertIn("00:00 GMT", slots[1]["label"])

    def test_daily_selection_closest_to_1700_in_each_elapsed_day(self):
        now = dt.datetime(2025, 1, 6, 16).timestamp()
        nearest = dt.datetime(2025, 1, 5, 16, 59).timestamp()
        self.image(nearest)
        self.image(dt.datetime(2025, 1, 5, 17, 10).timestamp())
        old = dt.datetime(2025, 1, 3, 17, 1).timestamp()
        self.image(old)
        # Today's 17:00 target has not elapsed yet.
        self.image(dt.datetime(2025, 1, 6, 15).timestamp())
        for clock in ("1700", "17:00"):
            slots = self.report(now=now, detail="detailed", selection="daily", daily_time=clock)["selections"]
            self.assertEqual([slot["timestamp"] for slot in slots], [nearest, None, old, None, None])
            self.assertEqual(slots[0]["target"], dt.datetime(2025, 1, 5, 17).timestamp())

    def test_daily_target_becomes_available_at_exact_time(self):
        now = dt.datetime(2025, 1, 6, 17).timestamp()
        self.image(now)
        slots = self.report(now=now, detail="detailed", selection="daily")["selections"]
        self.assertEqual(slots[0]["target"], now)
        self.assertEqual(slots[0]["timestamp"], now)

    def test_future_captures_excluded_from_comparison_and_gallery(self):
        self.image(1000)
        self.image(2000)
        report = self.report(detail="detailed", interval=100)
        self.assertEqual(report["summary"]["image_count"], 2)
        self.assertEqual(report["summary"]["actual_count"], 1)
        self.assertEqual(report["latest"]["timestamp"], 1000)
        self.assertEqual(len(report["points"]), 1)

    def test_auto_path_reads_dirlocs_and_falls_back_to_home(self):
        config = self.path / "dirlocs.txt"
        config.write_text("path=/ignored\ncaps_path={}\n".format(self.path))
        report = info.collect_info(config_path=config, now=1600, cron_text="")
        self.assertEqual(report["path"], str(self.path))
        with mock.patch.dict(os.environ, {"HOME": str(self.path)}):
            report = info.collect_info(config_path=self.path / "missing", now=1600, cron_text="")
        self.assertEqual(report["path"], str(self.path / "Pigrow" / "caps"))

    def test_naive_and_offset_iso_start(self):
        start = dt.datetime(2025, 1, 2, 12)
        self.image(start.timestamp())
        report = self.report(interval=60, start=start.isoformat(), now=start.timestamp() + 60)
        self.assertEqual(report["summary"]["expected_count"], 2)
        offset_start = dt.datetime(2025, 1, 2, 12, tzinfo=dt.timezone(dt.timedelta(hours=2)))
        self.assertEqual(info._timestamp(offset_start.isoformat()), offset_start.timestamp())

    def test_cli_is_one_json_document_and_flags_are_key_value(self):
        for args in (["detail=detailed", "path={}".format(self.path), "interval=invalid"],
                     ["unknown=value"], ["nonsense"], ["daily_time=2500"]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(info.main(args), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["summary"]["status"], "error")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            info.main(["-flags"])
        self.assertIn("daily_time=1700", output.getvalue())

    def test_invalid_arguments_are_rejected_without_nonfinite_json(self):
        for kwargs in ({"interval": 0}, {"interval": "nan"}, {"interval": "inf"},
                       {"daily_time": "9:30"}, {"daily_time": "2360"},
                       {"detail": "other"}, {"selection": "other"},
                       {"start": 2000}, {"start": "nan"}, {"now": "inf"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.report(**kwargs)


if __name__ == "__main__":
    unittest.main()
