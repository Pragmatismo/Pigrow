"""Regression checks for shared timestamp, rendering and resource guarantees."""

import datetime as dt
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
from timelapse_modules import analysis_common as common


class AnalysisCommonTests(unittest.TestCase):
    def test_dates_are_utc_and_compact_dates_take_precedence(self):
        self.assertEqual(common.capture_datetime("cap_20260102123456.jpg"),
                         dt.datetime(2026, 1, 2, 12, 34, 56))
        self.assertEqual(common.capture_datetime("cap_1700000000.125.jpg"),
                         dt.datetime(2023, 11, 14, 22, 13, 20, 125000))
        for suffix in ("20260230123456", "9999999999999999999999", "nan", "unknown"):
            self.assertIsNone(common.capture_datetime("cap_" + suffix + ".jpg"))

    def test_thumbnail_is_rgb_and_releases_source(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "frame.png"
            with Image.new("L", (400, 200), 50) as image:
                image.save(path)
            with common.load_thumbnail(path) as thumbnail:
                self.assertEqual(thumbnail.mode, "RGB")
                self.assertEqual(thumbnail.size, (128, 64))
                path.unlink()  # The returned thumbnail owns its decoded pixels.
                self.assertEqual(thumbnail.getpixel((0, 0)), (50, 50, 50))

    def test_atomic_failure_retains_previous_image_and_removes_tempfile(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "output.png"
            with Image.new("RGB", (12, 12), "red") as image:
                common.save_image(image, path)
                before = path.read_bytes()
                with mock.patch.object(image, "save", side_effect=OSError("disk full")):
                    with self.assertRaisesRegex(OSError, "disk full"):
                        common.save_image(image, path)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_dense_plot_preserves_spike_and_breaks_at_missing_values(self):
        fig, axes = common.new_figure("Dense test")
        try:
            x = np.arange(1, 100001)
            y = np.ones(100000)
            y[50000] = 999
            y[20000:22000] = np.nan
            common.plot_series(axes[0], x, y)
            self.assertLessEqual(len(axes[0].lines[0].get_xdata()), 1600)
            self.assertTrue(np.isnan(axes[0].lines[0].get_ydata()).any())
            segments = axes[0].collections[0].get_segments()
            self.assertTrue(any(segment.size and segment[:, 1].max() == 999
                                for segment in segments))
        finally:
            fig.clear()

    def test_short_plot_does_not_connect_across_unknown_frame(self):
        fig, axes = common.new_figure("Short test")
        try:
            common.plot_series(axes[0], [1, 2, 3], [10, np.nan, 20])
            self.assertTrue(np.isnan(axes[0].lines[0].get_ydata()[1]))
        finally:
            fig.clear()


if __name__ == "__main__":
    unittest.main()
