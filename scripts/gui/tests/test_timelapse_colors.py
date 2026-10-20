"""Color analyses retain image order, handle mixed formats, and bound outputs."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
from timelapse_modules import analyse_brightness as brightness
from timelapse_modules import analyse_colorgraph as colorgraph
from timelapse_modules import analyse_colourswatch as swatch


class TimelapseColorTests(unittest.TestCase):
    def setUp(self):
        scratch = GUI.parents[1] / "work"
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix="timelapse-colors-", dir=scratch)
        self.root = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def image(self, name, color, mode="RGB", size=(48, 32)):
        path = self.root / (name + ".png")
        with Image.new(mode, size, color) as image:
            image.save(path)
        return str(path)

    def test_statistics_keep_set_order_and_failed_positions(self):
        frames = [self.image("red", (255, 0, 0)), str(self.root / "missing.png"),
                  self.image("blue", (0, 0, 255)), self.image("green", (0, 255, 0))]
        means, lows, highs, luminance, failed = colorgraph.collect_statistics(frames)
        np.testing.assert_allclose(means[[0, 2, 3]], ((100, 0, 0), (0, 0, 100), (0, 100, 0)), atol=0.001)
        self.assertTrue(np.isnan(means[1]).all())
        self.assertTrue(np.isnan(luminance[1]).all())
        self.assertEqual(failed, 1)
        self.assertGreater(luminance[3, 0], luminance[0, 0])
        self.assertGreater(luminance[0, 0], luminance[2, 0])

    def test_no_unsigned_channel_wraparound(self):
        red = self.image("red", (255, 0, 0), size=(12, 8))
        red_counts, green_counts, blue_counts = colorgraph.color_intensity_ranges(red)
        self.assertEqual(sum(red_counts), 12 * 8)
        self.assertEqual(sum(green_counts), 0)
        self.assertEqual(sum(blue_counts), 0)

    def test_mixed_modes_dimensions_and_exposure_limits(self):
        frames = [self.image("black", 0, "L", (13, 19)),
                  self.image("white", (255, 255, 255, 255), "RGBA", (600, 20)),
                  self.image("grey", 128, "L", (20, 600))]
        means, _, _, luminance, failed = colorgraph.collect_statistics(frames)
        self.assertEqual(failed, 0)
        np.testing.assert_allclose(means[0], 0, atol=0.001)
        np.testing.assert_allclose(means[1], 100, atol=0.001)
        self.assertAlmostEqual(luminance[0, 1], 100)
        self.assertAlmostEqual(luminance[1, 2], 100)
        self.assertAlmostEqual(luminance[2, 0], 128 / 2.55, places=3)

    def test_each_tool_renders_a_single_image_and_mixed_corrupt_set(self):
        frame = self.image("red", "red")
        bad = self.root / "bad.png"
        bad.write_text("not an image")
        for module in (colorgraph, brightness, swatch):
            for frames in ([frame], [frame, str(bad)]):
                with self.subTest(module=module.__name__, count=len(frames)):
                    output = self.root / (module.__name__.rsplit(".", 1)[1] + ".png")
                    self.assertTrue(module.analyse_set(frames, output))
                    with Image.open(output) as image:
                        self.assertEqual(image.width, 1600)
                        self.assertLessEqual(image.height, 1300)
                        image.load()

    def test_empty_and_all_bad_fail_without_overwriting_existing_result(self):
        output = self.root / "result.png"
        output.write_bytes(b"previous result")
        for module in (colorgraph, brightness, swatch):
            for frames in ([], [str(self.root / "missing.png")]):
                with self.subTest(module=module.__name__, frames=frames):
                    with self.assertRaisesRegex(ValueError, "[Nn]o"):
                        module.analyse_set(frames, output)
                    self.assertEqual(output.read_bytes(), b"previous result")

    def test_swatch_uses_full_frame_not_only_center_crop(self):
        source = self.root / "split.png"
        with Image.new("RGB", (100, 40), "red") as image:
            image.paste((0, 0, 255), (50, 0, 100, 40))
            image.save(source)
        output = self.root / "swatch.png"
        swatch.analyse_set([str(source)], output)
        with Image.open(output) as image:
            red, green, blue = image.getpixel((800, swatch.TOP + 100))
        self.assertAlmostEqual(red, blue, delta=2)
        self.assertLess(green, 2)

    def test_swatch_marks_unreadable_frame_without_shifting_later_images(self):
        red = self.image("red", "red")
        blue = self.image("blue", "blue")
        output = self.root / "swatch.png"
        swatch.analyse_set([red, str(self.root / "missing.png"), blue], output)
        with Image.open(output) as image:
            self.assertEqual(image.getpixel((300, swatch.TOP + 100)), (255, 0, 0))
            self.assertEqual(image.getpixel((800, swatch.TOP + 100)), swatch.MISSING)
            self.assertEqual(image.getpixel((1300, swatch.TOP + 100)), (0, 0, 255))
            self.assertEqual(image.getpixel((800, swatch.TOP + swatch.STRIP_HEIGHT - 3)), swatch.ERROR_COLOR)

    def test_large_swatch_averages_all_frames_without_unbounded_output(self):
        # Each dense column contains two frames, so a red/blue alternating set
        # must be purple. Representative sampling would incorrectly be red.
        red = self.image("red", "red", size=(1, 1))
        blue = self.image("blue", "blue", size=(1, 1))
        frames = [red, blue] * (swatch.RIGHT - swatch.LEFT)
        output = self.root / "large-swatch.png"
        swatch.analyse_set(frames, output)
        with Image.open(output) as image:
            self.assertEqual(image.size, (1600, 680))
            self.assertEqual(image.getpixel((800, swatch.TOP + 100)), (127, 0, 127))

    def test_large_colorgraph_and_brightness_have_fixed_canvas(self):
        result = (np.array([10, 20, 30]), np.array([5, 10, 15]),
                  np.array([15, 30, 45]), 20, 0, 0)
        frames = ["valid.png"] * 10001
        with mock.patch.object(colorgraph, "image_statistics", return_value=result):
            for module in (colorgraph, brightness):
                output = self.root / (module.__name__.rsplit(".", 1)[1] + ".png")
                self.assertTrue(module.analyse_set(frames, output))
                with Image.open(output) as image:
                    self.assertEqual(image.width, 1600)
                    self.assertLessEqual(image.height, 1300)


if __name__ == "__main__":
    unittest.main()
