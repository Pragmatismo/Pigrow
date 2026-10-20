"""Calendar rendering regressions using tiny local photographs only."""

from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageDraw

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
from timelapse_modules import analyse_daygrid as grid


class DayGridTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="daygrid-")
        self.root = Path(self.folder.name)
        self.output = self.root / "grid.png"

    def tearDown(self):
        self.folder.cleanup()

    def frame(self, moment, color=(23, 141, 69), name=None):
        path = self.root / (name or "cap_{}.png".format(moment.strftime("%Y%m%d%H%M%S")))
        with Image.new("RGB", (40, 30), color) as image:
            image.save(path)
        return str(path)

    def test_partial_day_keeps_midnight_alignment_and_neutral_missing_periods(self):
        frames = [self.frame(datetime(2026, 10, 1, hour)) for hour in (12, 13)]
        self.assertTrue(grid.analyse_set(frames, self.output))
        _, _, body_height, width, height = grid._layout(1)
        with Image.open(self.output) as result:
            self.assertEqual(result.size, (width, height))
            middle = (grid.LEFT + width - grid.RIGHT) // 2
            plot_y = grid.TOP + grid.LABEL_HEIGHT
            self.assertIn(result.getpixel((middle, plot_y + body_height // 4 + 2)),
                          (grid.MISSING, grid.MISSING_ALT))
            self.assertEqual(result.getpixel((middle, plot_y + body_height // 2 + 2)), (23, 141, 69))
            self.assertIn(result.getpixel((middle, plot_y + body_height * 3 // 4 + 1)),
                          (grid.MISSING, grid.MISSING_ALT))

    def test_sparse_captures_do_not_fill_a_large_gap(self):
        times = [datetime(2026, 10, 1, hour) for hour in (2, 14, 15)]
        windows = grid.get_image_windows(times)
        self.assertTrue(all(end - start <= 60 for start, end in windows))
        images = list(zip(times, ("a", "b", "c")))
        rows = grid._render_rows(images, 720)
        self.assertIsNone(rows[300])  # 10:00 lies in the missing twelve-hour period.
        self.assertEqual(rows[60], 0)
        self.assertEqual(rows[420], 1)

    def test_timing_jitter_remains_contiguous_and_single_capture_has_small_window(self):
        start = datetime(2026, 10, 1, 10)
        times = [start + timedelta(seconds=value) for value in (0, 600, 1201)]
        windows = grid.get_image_windows(times)
        self.assertLessEqual(windows[1][0], windows[0][1])
        self.assertLessEqual(windows[2][0], windows[1][1])
        self.assertEqual(grid.get_image_windows([start]), [(585, 615)])
        self.assertEqual(grid.get_image_windows([]), [])

    def test_corrupt_images_are_marked_without_aborting_other_days(self):
        frames = [self.frame(datetime(2026, 10, 1, 12))]
        corrupt = self.root / "cap_20261002120000.png"
        corrupt.write_text("broken image")
        frames.append(str(corrupt))
        self.assertTrue(grid.analyse_set(frames, self.output))
        column_width, _, body_height, _, _ = grid._layout(2)
        with Image.open(self.output) as result:
            self.assertEqual(result.getpixel((grid.LEFT + column_width + column_width // 2,
                                             grid.TOP + grid.LABEL_HEIGHT + body_height // 2 + 2)),
                             grid.UNREADABLE)

    def test_undated_files_are_omitted_but_all_undated_or_all_corrupt_is_explained(self):
        undated = self.frame(datetime(2026, 10, 1, 12), name="unknown.png")
        with self.assertRaisesRegex(ValueError, "No capture dates"):
            grid.analyse_set([undated], self.output)
        good = self.frame(datetime(2026, 10, 1, 12))
        self.assertTrue(grid.analyse_set([undated, good], self.output))
        Path(good).write_text("broken")
        with self.assertRaisesRegex(ValueError, "None of the dated images could be read"):
            grid.analyse_set([good], self.output)

    def test_dense_frames_decode_no_more_images_than_rendered_rows(self):
        start = datetime(2026, 10, 1, 10)
        images = [(start + timedelta(milliseconds=index), "cap-{}.png".format(index))
                  for index in range(10000)]
        rows = grid._render_rows(images, 720)
        self.assertLessEqual(len({index for index in rows if index is not None}), 720)
        self.assertIsNotNone(rows[300])
        self.assertIsNone(rows[400])

    def test_many_days_wrap_without_unbounded_canvas(self):
        for count in (1, 2, 10, 120, 365, 1000, 3000):
            with self.subTest(days=count):
                column_width, columns, body_height, width, height = grid._layout(count)
                self.assertLessEqual(width, grid.MAX_WIDTH)
                self.assertLessEqual(height, grid.MAX_HEIGHT)
                self.assertLessEqual(width * height, grid.MAX_PIXELS)
                self.assertGreaterEqual(column_width, 12)
        with self.assertRaisesRegex(ValueError, "shorter date range"):
            grid._layout(100000)

    def test_large_frame_counts_fit_actual_horizontal_and_rotated_draw_bounds(self):
        original_text = ImageDraw.ImageDraw.text
        for count in (100_000, 1_000_000, 123_456_789):
            for width in (12, 32, 48, 72, 96, 120):
                with self.subTest(count=count, column_width=width):
                    with Image.new("RGB", (200, 140), grid.BACKGROUND) as canvas:
                        draw = ImageDraw.Draw(canvas)
                        draws = []

                        def record_text(target, xy, text, *args, **kwargs):
                            bounds = target.textbbox(xy, text, font=kwargs["font"])
                            draws.append((target is draw, bounds, target._image.size, text))
                            return original_text(target, xy, text, *args, **kwargs)

                        with mock.patch.object(ImageDraw.ImageDraw, "text", side_effect=record_text, autospec=True):
                            grid._date_label(canvas, draw, datetime(2026, 1, 2).date(),
                                             count, 40, width, 0)
                        self.assertTrue(draws)
                        for is_main, bounds, image_size, text in draws:
                            left, top, right, bottom = bounds
                            self.assertGreaterEqual(left, 40 if is_main else 0, text)
                            self.assertLessEqual(right, 40 + width if is_main else image_size[0], text)
                            self.assertGreaterEqual(top, 0, text)
                            self.assertLessEqual(bottom, image_size[1], text)

    def test_more_than_one_panel_and_chronological_order(self):
        start = datetime(2026, 1, 1, 12)
        frames = [self.frame(start + timedelta(days=index)) for index in range(20)]
        self.assertTrue(grid.analyse_set(list(reversed(frames)), self.output))
        _, columns, body_height, _, _ = grid._layout(len(frames))
        self.assertLess(columns, len(frames))
        with Image.open(self.output) as result:
            second_panel_y = grid.TOP + grid.LABEL_HEIGHT + body_height + grid.PANEL_GAP + grid.LABEL_HEIGHT
            self.assertEqual(result.getpixel((grid.LEFT + 30, second_panel_y + body_height // 2 + 2)),
                             (23, 141, 69))


if __name__ == "__main__":
    unittest.main()
