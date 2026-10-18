"""Headless rendering checks for the GUI's two timelapse datawall modules."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageDraw


MODULES = Path(__file__).resolve().parents[1] / "datawall_modules"
sys.path.insert(0, str(MODULES))
import datawall_timelapse_detailed as detailed
import datawall_timelapse_fast as fast
import timelapse_tools as tools


def sample_report():
    points = [
        {"path": "/captures/frame_{}.jpg".format(index), "timestamp": 1700000000 + index * 600,
         "mtime": 1700000000 + index * 600, "size": 20000 + index * 1000,
         "time_label": "2023-11-14 22:{:02d}:00".format(index * 10)}
        for index in range(6)
    ]
    return {
        "version": 1, "detail": "detailed", "path": "/captures/test camera",
        "generated_at": 1700003000, "generated_label": "2023-11-14 23:03:20 UTC",
        "timezone": "UTC", "latest": points[-1], "points": points,
        "summary": {
            "image_count": 6, "total_bytes": 135000, "actual_count": 6,
            "expected_count": 7, "missing_count": 1, "extra_count": 0,
            "completion_percent": 600 / 7, "first_timestamp": points[0]["timestamp"],
            "last_timestamp": points[-1]["timestamp"], "first_label": points[0]["time_label"],
            "last_label": points[-1]["time_label"], "latest_age_seconds": 0,
            "window_start": points[0]["timestamp"], "start_source": "first image",
            "interval_seconds": 600, "schedule_description": "Every ten minutes",
            "status": "behind", "warnings": [], "selection": "recent",
        },
        "datawall_images": dict(
            [("timelapse_latest", points[-1])]
            + [("timelapse_{}".format(index + 1), point) for index, point in enumerate(points[-5:])]
        ),
        "selections": [
            dict(point, key="timelapse_{}".format(index + 1), label="Recent {}".format(index + 1))
            for index, point in enumerate(points[-5:])
        ],
    }


class TimelapseDatawallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.report = sample_report()
        self.data = {
            "info": {"boxname": "Test Pigrow", "timelapse detail=detailed path='/captures/test camera'":
                     json.dumps(self.report)},
            "settings": {"gallery_mode": "recent"}, "images": {},
        }

    def output(self, name):
        return str(self.directory / name)

    def test_module_requests_keep_fast_metadata_only_and_offer_gallery_modes(self):
        fast_options, fast_request = fast.read_datawall_options()
        detail_options, detail_request = detailed.read_datawall_options()
        self.assertIn("output", fast_options)
        self.assertIn("output", detail_options)
        self.assertIn("detail=fast", fast_request["info_read"][-1])
        self.assertNotIn("gallery_mode", fast_request["settings"])
        self.assertNotIn("pictures", fast_request)
        self.assertEqual(detail_request["settings"]["gallery_mode"], ["recent", "hourly", "daily"])
        self.assertIn("selection={gallery_mode}", detail_request["info_read"][-1])
        self.assertEqual(detail_request["settings"]["daily_time"], "1700")

    def test_fast_does_not_open_photographs_or_build_graphs(self):
        output = self.output("fast.png")
        with mock.patch.object(tools, "photo_box") as photos, mock.patch.object(tools, "graph_image") as graphs:
            self.assertEqual(fast.make_datawall(self.data, {"output": output}), output)
            photos.assert_not_called()
            graphs.assert_not_called()
        with Image.open(output) as image:
            self.assertEqual(image.width, 1200)
            self.assertEqual(image.mode, "RGB")
            self.assertGreater(image.height, 550)

    def test_detailed_renders_latest_five_slots_and_graph_without_pyplot(self):
        colors = ["red", "green", "blue", "orange", "purple", "cyan"]
        for index, key in enumerate(["timelapse_latest"] + ["timelapse_{}".format(i) for i in range(1, 6)]):
            path = self.directory / (key + ".png")
            Image.new("RGB", (640, 480), colors[index]).save(path)
            self.data["images"][key] = str(path)
        output = self.output("detailed.png")
        with mock.patch.dict(sys.modules, {"matplotlib.pyplot": None}), \
                mock.patch.object(tools, "photo_box", wraps=tools.photo_box) as photos:
            self.assertEqual(detailed.make_datawall(self.data, {"output": output}), output)
        self.assertEqual(len(photos.call_args_list), 6)
        self.assertEqual(photos.call_args_list[0].args[1], self.data["images"]["timelapse_latest"])
        self.assertEqual([call.args[1] for call in photos.call_args_list[1:]],
                         [self.data["images"]["timelapse_{}".format(i)] for i in range(1, 6)])
        with Image.open(output) as image:
            self.assertEqual(image.width, 1200)
            self.assertGreater(image.height, 1700)
            red_pixels = sum(amount for amount, color in image.getcolors(image.width * image.height)
                             if color == (255, 0, 0))
            self.assertGreater(red_pixels, 300000)

    def test_detailed_handles_missing_period_and_corrupt_photos(self):
        corrupt = self.directory / "broken.jpg"
        corrupt.write_bytes(b"not a photograph")
        self.data["images"] = {"timelapse_latest": str(corrupt), "timelapse_2": "None"}
        self.data["image_errors"] = {"timelapse_latest": "Download failed"}
        self.report["summary"]["selection"] = "daily"
        self.report["summary"]["daily_time"] = "1700"
        self.report["selections"][0].update(path=None, time_label=None, label="2023-11-14 at 17:00")
        self.data["info"]["timelapse detail=detailed path='/captures/test camera'"] = json.dumps(self.report)
        output = detailed.make_datawall(self.data, {"output": self.output("missing.png")})
        with Image.open(output) as image:
            self.assertGreater(image.height, 1700)

    def test_missing_empty_and_invalid_report_all_render(self):
        cases = [{}, {"info": {"timelapse detail=fast": "not JSON"}},
                 {"info": {"timelapse detail=fast": "[]"}},
                 {"info": {"timelapse detail=fast": json.dumps({"summary": {"status": "empty"}})}}]
        for index, data in enumerate(cases):
            for module in (fast, detailed):
                output = self.output("empty_{}_{}.png".format(index, module.__name__))
                with self.subTest(index=index, module=module.__name__):
                    self.assertEqual(module.make_datawall(data, {"output": output}), output)
                    self.assertTrue(Path(output).is_file())

    def test_options_override_saved_settings_but_empty_options_preserve_them(self):
        self.data["settings"]["output"] = self.output("saved.png")
        self.assertEqual(fast.make_datawall(self.data, {}), self.data["settings"]["output"])
        selected = self.output("override.png")
        self.assertEqual(fast.make_datawall(self.data, {"output": selected}), selected)

    def test_missing_metrics_are_unavailable_and_path_wraps_within_width(self):
        self.assertEqual(tools.count(None), "Unavailable")
        self.assertEqual(tools.byte_size(None), "Unavailable")
        self.assertEqual(tools.duration(None), "Unavailable")
        self.assertEqual(tools.count(0), "0")
        rows = dict(tools.summary_rows({"summary": {}}))
        self.assertIn("Unavailable images", rows["Folder totals"])
        draw = ImageDraw.Draw(Image.new("RGB", (300, 100)))
        face = tools.font(18)
        lines = tools.text_lines(draw, "/verylongfoldername" * 20, face, 220, 3)
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(draw.textlength(line, font=face) <= 220 for line in lines))

    def test_graph_accepts_one_point_and_skips_invalid_file_metadata(self):
        report = copy.deepcopy(self.report)
        report["points"] = report["points"][:1] + [None, {}, {"timestamp": "nan", "size": 100},
                                                 {"timestamp": 1e100, "size": 100}]
        with mock.patch.dict(sys.modules, {"matplotlib.pyplot": None}):
            graph = tools.graph_image(report)
        self.assertEqual(graph.size, (1144, 340))
        self.assertEqual(graph.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
