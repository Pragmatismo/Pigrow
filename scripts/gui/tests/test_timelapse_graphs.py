"""Regression checks for metadata graphs without wx or a connected camera."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))

from timelapse_modules import analyse_filesize as filesize
from timelapse_modules import analyse_filesizedistribution as distribution
from timelapse_modules import analyse_time as capture_time
from timelapse_modules import analyse_timediff as timediff


class TimelapseGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="analysis-graphs-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def path(self, suffix, size=256):
        path = self.root / ("cap_" + str(suffix) + ".jpg")
        path.write_bytes(b"x" * size)
        return str(path)

    def test_file_sizes_keep_missing_frame_position(self):
        paths = [self.path(1000, 21), str(self.root / "missing.jpg"), self.path(1001, 66)]
        values, missing = filesize.collect_file_sizes(paths)
        self.assertEqual(missing, 1)
        self.assertEqual(values[0], 21)
        self.assertTrue(np.isnan(values[1]))
        self.assertEqual(values[2], 66)

    def test_elapsed_times_preserve_order_and_unknown_positions(self):
        paths = ["cap_20260102120000.jpg", "unknown.jpg", "cap_20260102115900.jpg",
                 "cap_20260102120500.jpg"]
        dates, first, elapsed = capture_time.elapsed_capture_times(paths)
        self.assertEqual(first.year, 2026)
        self.assertEqual(first.month, 1)
        self.assertEqual(first.day, 2)
        self.assertTrue(np.isnan(elapsed[1]))
        self.assertEqual(elapsed[2], -60)
        self.assertEqual(elapsed[3], 300)

    def test_intervals_never_bridge_unknown_timestamp(self):
        paths = ["cap_1000.jpg", "bad.jpg", "cap_1500.jpg", "cap_1500.jpg",
                 "cap_1490.jpg", "cap_1600.jpg"]
        dates, values = timediff.capture_intervals(paths)
        self.assertTrue(np.isnan(values[:3]).all())
        np.testing.assert_array_equal(values[3:], [0, -10, 110])

    def test_all_graphs_render_one_and_many_frames_to_bounded_images(self):
        paths = [self.path(1700000000 + index * 60, 128 + index * 7) for index in range(6)]
        for module in (filesize, distribution, capture_time, timediff):
            for selected in (paths[:1], paths):
                with self.subTest(module=module.__name__, count=len(selected)):
                    output = self.root / (module.__name__.split(".")[-1] + ".png")
                    self.assertIs(module.analyse_set(selected, str(output)), True)
                    with Image.open(output) as image:
                        self.assertLessEqual(image.width, 2000)
                        self.assertLessEqual(image.height, 1600)
                        image.verify()

    def test_large_metadata_graphs_have_bounded_rendering(self):
        # A single real file can occupy many slots in a set. Avoid 30,000 fixture files.
        paths = [self.path(1700000000)] * 30000
        for module in (filesize, distribution, capture_time, timediff):
            captured = []

            def inspect(fig, path):
                fig.canvas.draw()
                captured.append((len(fig.axes[0].patches), len(fig.axes[0].lines)))
                self.assertLessEqual(fig.canvas.get_width_height()[0], 2000)
                for text in (fig.axes[0].xaxis.label, fig.axes[0].yaxis.label):
                    bounds = text.get_window_extent(fig.canvas.get_renderer())
                    width, height = fig.canvas.get_width_height()
                    self.assertGreaterEqual(bounds.x0, 0)
                    self.assertGreaterEqual(bounds.y0, 0)
                    self.assertLessEqual(bounds.x1, width)
                    self.assertLessEqual(bounds.y1, height)

            with self.subTest(module=module.__name__):
                with mock.patch.object(module, "save_figure", side_effect=inspect):
                    self.assertTrue(module.analyse_set(paths, str(self.root / "large.png")))
                self.assertTrue(captured)
                # Histogram <=100 rectangles; series uses collections/envelope, never per-image bars.
                self.assertLessEqual(captured[0][0], 100)
                self.assertLessEqual(captured[0][1], 12)

    def test_unusable_sets_raise_descriptive_errors(self):
        for module in (filesize, distribution, capture_time, timediff):
            with self.subTest(module=module.__name__):
                with self.assertRaises(ValueError):
                    module.analyse_set([], str(self.root / "empty.png"))
                with self.assertRaises(ValueError):
                    module.analyse_set([str(self.root / "unknown.jpg")] * 2,
                                       str(self.root / "invalid.png"))

    def test_mixed_invalid_metadata_is_explained_and_rendered(self):
        paths = [self.path(1000), str(self.root / "unknown.jpg"), self.path(1500), self.path(1600)]
        for module in (filesize, distribution, capture_time, timediff):
            with self.subTest(module=module.__name__):
                self.assertTrue(module.analyse_set(paths, str(self.root / "mixed.png")))


if __name__ == "__main__":
    unittest.main()
