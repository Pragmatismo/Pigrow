"""Pixel and lifecycle regressions for the shared, headless stylized-set engine."""

from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageChops

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
import stylized_sets as sets


class StylizedSetTests(unittest.TestCase):
    def setUp(self):
        scratch = GUI.parents[1] / "work"
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix="stylized-engine-", dir=scratch)
        self.root = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def image(self, name, color, size=(3, 2), mode="RGB", exif=None):
        path = self.root / (name + ".png")
        with Image.new(mode, size, color) as image:
            image.save(path, **({"exif": exif} if exif is not None else {}))
        return path

    def settings(self, base="black", **layer):
        settings = sets.default_settings()
        settings["base"] = base
        settings["layers"][0].update(layer)
        return settings

    def pixels(self, renderer, paths):
        values = []
        for path in paths:
            with renderer.process(path) as output:
                self.assertEqual(output.mode, "RGB")
                values.append(output.getpixel((0, 0)))
        return values

    def test_defaults_and_validation_are_independent(self):
        first = sets.default_settings()
        second = sets.default_settings()
        first["layers"][0]["name"] = "changed"
        self.assertEqual(second["layers"][0]["name"], "Layer 1")
        original = {"layers": [{"tint": "#FFaA00"}]}
        normalized = sets.validate_settings(original)
        self.assertEqual(normalized["layers"][0]["tint"], "#ffaa00")
        normalized["layers"][0]["name"] = "new"
        self.assertEqual(original, {"layers": [{"tint": "#FFaA00"}]})
        self.assertEqual(normalized["version"], 1)

    def test_strict_validation_rejects_unknown_types_ranges_and_nonfinite(self):
        invalid = [None, [], {"version": True}, {"version": 2}, {"base": "video"},
                   {"max_size": True}, {"max_size": 127}, {"max_size": 4097},
                   {"max_size": 128.0}, {"layers": {}}, {"unknown": 0},
                   {"layers": [sets.default_layer()] * 17}]
        invalid_layers = [{"source": "unknown"}, {"persistence": "forever"},
                          {"blend": "overlay"}, {"enabled": 1}, {"invert": 0},
                          {"opacity": float("nan")}, {"decay": float("inf")},
                          {"gain": -1}, {"gain": True}, {"opacity": "0.5"},
                          {"threshold": 256}, {"threshold": 1.0},
                          {"trail_frames": 0}, {"trail_frames": 101},
                          {"tint": "red"}, {"tint": "#fff"},
                          {"name": " "}, {"name": "x" * 81}, {"typo": 2}]
        invalid += [{"layers": [layer]} for layer in invalid_layers]
        for settings in invalid:
            with self.subTest(settings=settings):
                with self.assertRaises(ValueError):
                    sets.validate_settings(settings)

    def test_zero_layers_base_modes_and_owned_outputs_survive_close(self):
        first = self.image("first", (10, 20, 30))
        second = self.image("second", (40, 50, 60))
        for base, expected in (("current", (40, 50, 60)), ("first", (10, 20, 30)),
                               ("black", (0, 0, 0)), ("white", (255, 255, 255))):
            with self.subTest(base=base):
                settings = sets.default_settings()
                settings.update(base=base, layers=[])
                renderer = sets.StylizedRenderer(settings)
                with renderer.process(first):
                    pass
                result = renderer.process(second)
                renderer.close()
                renderer.close()
                self.assertEqual(result.getpixel((0, 0)), expected)
                result.close()
                with self.assertRaises(RuntimeError):
                    renderer.process(first)

    def test_difference_references_original_inputs_and_first_output_exists(self):
        paths = [self.image(str(index), (value, 0, 0)) for index, value in enumerate((10, 40, 50))]
        for source, expected in (("difference_previous", [0, 30, 10]),
                                  ("difference_first", [0, 30, 40])):
            with self.subTest(source=source):
                with sets.StylizedRenderer(self.settings(source=source, blend="normal")) as renderer:
                    values = self.pixels(renderer, paths)
                self.assertEqual([value[0] for value in values], expected)

    def test_mutating_returned_image_cannot_change_reference_history(self):
        first = self.image("first", (10, 0, 0))
        second = self.image("second", (40, 0, 0))
        with sets.StylizedRenderer(self.settings(source="difference_previous", blend="normal")) as renderer:
            with renderer.process(first) as output:
                output.putpixel((0, 0), (255, 255, 255))
            with renderer.process(second) as output:
                self.assertEqual(output.getpixel((0, 0)), (30, 0, 0))

    def test_unchanged_regions_remain_transparent_after_inversion_and_tint(self):
        frame = self.image("frame", (100, 80, 60))
        settings = self.settings(base="white", source="difference_previous", blend="normal",
                                 invert=True, tint="#ff0000", gain=3)
        with sets.StylizedRenderer(settings) as renderer:
            self.assertEqual(self.pixels(renderer, [frame, frame]), [(255, 255, 255)] * 2)

    def test_changed_pixels_use_current_colors_and_strict_threshold(self):
        paths = [self.image("first", (10, 0, 0)), self.image("second", (40, 0, 0))]
        for threshold, expected in ((29, (40, 0, 0)), (30, (0, 0, 0))):
            with self.subTest(threshold=threshold):
                settings = self.settings(source="changed_pixels", blend="normal", threshold=threshold)
                with sets.StylizedRenderer(settings) as renderer:
                    values = self.pixels(renderer, paths)
                self.assertEqual(values[-1], expected)

    def test_all_blends_and_opacity_have_expected_pixel_results(self):
        first = self.image("first", (100, 100, 100))
        second = self.image("second", (200, 200, 200))
        expected = {"normal": 200, "add": 255, "add_modulo": 44, "screen": 222,
                    "lighten": 200, "multiply": 78, "difference": 100}
        for blend, value in expected.items():
            with self.subTest(blend=blend):
                with sets.StylizedRenderer(self.settings(base="first", source="copy", blend=blend)) as renderer:
                    result = self.pixels(renderer, [first, second])[-1]
                self.assertEqual(result, (value,) * 3)
        with sets.StylizedRenderer(self.settings(source="copy", blend="normal", opacity=0.5)) as renderer:
            self.assertEqual(self.pixels(renderer, [second]), [(100, 100, 100)])

    def test_legacy_modulo_accumulation_matches_previous_module_frames_two_onward(self):
        values = [(10, 240, 30), (40, 20, 200), (200, 220, 10), (70, 0, 255)]
        paths = [self.image(str(index), color) for index, color in enumerate(values)]
        settings = self.settings(base="first", source="difference_previous",
                                 persistence="permanent", blend="add_modulo")
        carry = Image.new("RGB", (3, 2), values[0])
        with sets.StylizedRenderer(settings) as renderer:
            for index, path in enumerate(paths):
                if index:
                    with Image.new("RGB", (3, 2), values[index - 1]) as previous:
                        with Image.new("RGB", (3, 2), values[index]) as current:
                            with ImageChops.difference(previous, current) as difference:
                                next_carry = ImageChops.add_modulo(carry, difference)
                    carry.close()
                    carry = next_carry
                with renderer.process(path) as output:
                    self.assertEqual(output.tobytes(), carry.tobytes())
        carry.close()

    def test_trail_decays_then_expires_at_exact_frame_count(self):
        paths = [self.image("black", (0, 0, 0)), self.image("bright", (80, 0, 0))]
        paths += [paths[0], paths[0], paths[0]]
        settings = self.settings(source="changed_pixels", persistence="trail", blend="add",
                                 trail_frames=2, decay=0.5)
        with sets.StylizedRenderer(settings) as renderer:
            values = self.pixels(renderer, paths)
        self.assertEqual([value[0] for value in values], [0, 80, 40, 0, 0])

    def test_translucent_copy_trail_reveals_older_patches_then_expires(self):
        paths = []
        for index in range(4):
            path = self.root / ("moving-copy-{}.png".format(index))
            with Image.new("RGB", (3, 1), "black") as image:
                if index < 3:
                    image.putpixel((index, 0), (255, 0, 0))
                image.save(path)
            paths.append(path)
        settings = self.settings(source="copy", persistence="trail", blend="normal",
                                 opacity=0.5, trail_frames=3, decay=1)
        with sets.StylizedRenderer(settings) as renderer:
            values = self.pixels(renderer, paths)
        # Later black backgrounds reduce the earlier red patch; they must not
        # erase it completely until that input position leaves the finite trail.
        self.assertEqual([value[0] for value in values], [128, 64, 32, 0])

    def test_changed_pixel_normal_trail_retains_prior_object_colors(self):
        paths = []
        for index in range(5):
            path = self.root / ("moving-change-{}.png".format(index))
            with Image.new("RGB", (3, 1), "black") as image:
                if index < 3:
                    image.putpixel((index, 0), (0, 255, 0))
                image.save(path)
            paths.append(path)
        settings = self.settings(source="changed_pixels", persistence="trail", blend="normal",
                                 opacity=0.6, trail_frames=3, decay=1)
        greens = []
        with sets.StylizedRenderer(settings) as renderer:
            for path in paths:
                with renderer.process(path) as output:
                    greens.append(output.getpixel((1, 0))[1])
        self.assertEqual(greens, [0, 153, 61, 61, 0])

    def test_single_frame_or_zero_decay_trail_equals_frame_opacity_for_all_blends(self):
        paths = [self.image("opacity-{}".format(index), color)
                 for index, color in enumerate(((80, 110, 60), (30, 140, 220), (150, 10, 80)))]
        for blend, _ in sets.BLEND_CHOICES:
            for source in ("copy", "changed_pixels"):
                settings = self.settings(base="first", source=source, blend=blend, opacity=0.35)
                expected = []
                with sets.StylizedRenderer(settings) as renderer:
                    for path in paths:
                        with renderer.process(path) as output:
                            expected.append(output.tobytes())
                for trail_frames, decay in ((1, 0.8), (5, 0)):
                    with self.subTest(blend=blend, source=source, trail_frames=trail_frames, decay=decay):
                        settings["layers"][0].update(persistence="trail", trail_frames=trail_frames, decay=decay)
                        with sets.StylizedRenderer(settings) as renderer:
                            for path, expected_bytes in zip(paths, expected):
                                with renderer.process(path) as output:
                                    self.assertEqual(output.tobytes(), expected_bytes)

    def test_zero_opacity_returns_the_custom_base_for_all_blends_and_persistence(self):
        first = self.image("opacity-first", (80, 110, 60))
        second = self.image("opacity-second", (30, 140, 220))
        for blend, _ in sets.BLEND_CHOICES:
            for persistence, _ in sets.PERSISTENCE_CHOICES:
                with self.subTest(blend=blend, persistence=persistence):
                    settings = self.settings(base="first", source="copy", blend=blend,
                                             persistence=persistence, opacity=0)
                    with sets.StylizedRenderer(settings) as renderer:
                        self.assertEqual(self.pixels(renderer, [first, second]), [(80, 110, 60)] * 2)

    def test_one_frame_trail_matches_frame_mode_and_permanent_never_fades(self):
        paths = [self.image("black", (0, 0, 0)), self.image("bright", (80, 0, 0))]
        paths += [paths[0], paths[0], paths[0]]
        settings = self.settings(source="changed_pixels", blend="add", decay=0)
        expected = None
        for persistence in ("frame", "trail"):
            settings["layers"][0].update(persistence=persistence, trail_frames=1)
            with sets.StylizedRenderer(settings) as renderer:
                values = self.pixels(renderer, paths)
            if expected is None:
                expected = values
            self.assertEqual(values, expected)
        settings["layers"][0]["persistence"] = "permanent"
        with sets.StylizedRenderer(settings) as renderer:
            values = self.pixels(renderer, paths)
        self.assertEqual([value[0] for value in values], [0, 80, 80, 80, 80])

    def test_layer_order_changes_output_and_disabled_layer_does_nothing(self):
        frame = self.image("white", (255, 255, 255))
        settings = self.settings(source="copy", blend="normal", tint="#ff0000")
        blue = sets.default_layer()
        blue.update(source="copy", blend="normal", tint="#0000ff")
        settings["layers"].append(blue)
        with sets.StylizedRenderer(settings) as renderer:
            self.assertEqual(self.pixels(renderer, [frame]), [(0, 0, 255)])
        settings["layers"].reverse()
        with sets.StylizedRenderer(settings) as renderer:
            self.assertEqual(self.pixels(renderer, [frame]), [(255, 0, 0)])
        settings["layers"][-1]["enabled"] = False
        with sets.StylizedRenderer(settings) as renderer:
            self.assertEqual(self.pixels(renderer, [frame]), [(0, 0, 255)])

    def test_grayscale_rgba_dimensions_and_exif_orientation_are_normalized(self):
        exif = Image.Exif()
        exif[274] = 6
        first = self.image("oriented", (20, 30, 40), size=(2, 3), exif=exif)
        second = self.image("grey", 80, size=(8, 8), mode="L")
        third = self.image("rgba", (40, 50, 60, 30), size=(1, 10), mode="RGBA")
        settings = sets.default_settings()
        settings["layers"] = []
        with sets.StylizedRenderer(settings) as renderer:
            for path in (first, second, third):
                with renderer.process(path) as output:
                    self.assertEqual(output.mode, "RGB")
                    self.assertEqual(output.size, (3, 2))
        with sets.StylizedRenderer(settings, max_size=2) as renderer:
            with renderer.process(first) as output:
                self.assertEqual(output.size, (2, 1))

    def test_edges_remove_unfiltered_border_and_threshold_is_applied(self):
        white = self.image("white", "white", size=(5, 5))
        settings = self.settings(source="edges", blend="normal")
        with sets.StylizedRenderer(settings) as renderer:
            with renderer.process(white) as output:
                self.assertEqual(output.getbbox(), None)

    def test_bad_input_leaves_previous_original_and_trail_state_usable(self):
        first = self.image("first", (10, 0, 0))
        second = self.image("second", (40, 0, 0))
        bad = self.root / "bad.png"
        bad.write_text("not an image")
        settings = self.settings(source="difference_previous", persistence="trail", trail_frames=2, blend="add")
        with sets.StylizedRenderer(settings) as renderer:
            with renderer.process(first):
                pass
            with self.assertRaises(OSError):
                renderer.process(bad)
            with renderer.process(second) as output:
                self.assertEqual(output.getpixel((0, 0)), (30, 0, 0))

    def test_memory_check_happens_before_pixels_are_decoded(self):
        source = mock.MagicMock()
        source.size = (20000, 20000)
        source.getexif.return_value = {}
        source.__enter__.return_value = source
        with sets.StylizedRenderer(sets.default_settings()) as renderer:
            with mock.patch.object(sets.Image, "open", return_value=source):
                with self.assertRaisesRegex(ValueError, "memory|renderer limit"):
                    renderer.process("huge.png")
        source.thumbnail.assert_not_called()

    def test_size_override_reduces_history_memory_and_disabled_layers_do_not_count(self):
        frame = self.image("large", (20, 40, 60), size=(200, 100))
        settings = self.settings(source="copy", persistence="trail", trail_frames=100)
        original_estimate = sets.estimate_memory_bytes(settings, (200, 100))
        with mock.patch.object(sets, "MAX_MEMORY_BYTES", 5 * 1024 * 1024):
            with sets.StylizedRenderer(settings) as renderer:
                with self.assertRaises(ValueError):
                    renderer.process(frame)
            with sets.StylizedRenderer(settings, max_size=128) as renderer:
                with renderer.process(frame) as output:
                    self.assertEqual(output.size, (128, 64))
        settings["layers"][0]["enabled"] = False
        self.assertLess(sets.estimate_memory_bytes(settings, (200, 100)), original_estimate)

    def test_failed_later_layer_does_not_commit_partial_history(self):
        first = self.image("first", (10, 0, 0))
        second = self.image("second", (40, 0, 0))
        settings = self.settings(source="difference_previous", persistence="trail", trail_frames=2, blend="add")
        settings["layers"].append(deepcopy(settings["layers"][0]))
        with sets.StylizedRenderer(settings) as renderer:
            with renderer.process(first):
                pass
            original = renderer._source
            calls = 0
            def fail_second(current, layer):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise ValueError("simulated layer failure")
                return original(current, layer)
            with mock.patch.object(renderer, "_source", side_effect=fail_second):
                with self.assertRaisesRegex(ValueError, "simulated"):
                    renderer.process(second)
            with renderer.process(second) as output:
                self.assertEqual(output.getpixel((0, 0)), (60, 0, 0))


if __name__ == "__main__":
    unittest.main()
