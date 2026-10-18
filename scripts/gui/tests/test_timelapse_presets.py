"""Exercise shipped presets through the real importer and renderer without a Pi."""

import datetime as dt
import importlib
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
sys.path.insert(0, str(GUI / "info_modules"))
sys.path.insert(0, str(GUI / "datawall_modules"))

try:
    import wx
except ImportError:
    wx = None

from PIL import Image
from info_timelapse import collect_info

if wx is not None:
    from panels.datawall_pnl import ctrl_pnl


@unittest.skipIf(wx is None, "wxPython required to import the GUI datawall importer")
class TimelapsePresetTests(unittest.TestCase):
    def setUp(self):
        scratch = GUI.parents[1] / "work"
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix="timelapse-presets-", dir=scratch)
        self.root = Path(self.folder.name)
        self.captures = self.root / "camera with spaces"
        self.captures.mkdir()
        self.local = self.root / "downloads"
        self.local.mkdir()
        self.now = dt.datetime(2026, 10, 17, 18, 15).timestamp()
        self.first = dt.datetime(2026, 10, 11, 0, 2).timestamp()
        timestamp = self.first
        index = 0
        while timestamp <= self.now:
            filename = self.captures / ("cap_{}.jpg".format(int(timestamp)))
            Image.new("RGB", (48, 32), (index % 255, 90, 130)).save(filename)
            timestamp += 3600
            index += 1
        self.downloads = []
        self.commands = []

        def download(remote_path, relative_path):
            self.downloads.append(remote_path)
            destination = self.local / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(remote_path, destination)
            return str(destination)

        def read_info(command):
            self.commands.append(command)
            if command == "boxname":
                return "Test Pigrow"
            if command == "datetime":
                return "2026-10-17 18:15:00"
            tokens = shlex.split(command)
            self.assertEqual(tokens.pop(0), "timelapse")
            options = dict(token.split("=", 1) for token in tokens)
            return json.dumps(collect_info(**options, now=self.now, cron_text=""))

        # No wx window is needed for the collection path used by the start panel.
        class Importer:
            create_datawall_data = ctrl_pnl.create_datawall_data
            _import_info_images = ctrl_pnl._import_info_images
            _download_manifest_image = ctrl_pnl._download_manifest_image

        self.importer = Importer()
        self.importer.shared_data = SimpleNamespace(frompi_path=str(self.local))
        self.importer.parent = SimpleNamespace(link_pnl=SimpleNamespace(
            download_file_to_folder=download))
        self.importer.read_info_module = read_info

    def tearDown(self):
        self.folder.cleanup()

    def test_every_shipped_preset_imports_and_renders_for_start_panel(self):
        presets = sorted((GUI / "datawall_presets").glob("datawall_timelapse_*.txt"))
        self.assertEqual(len(presets), 4)
        for preset in presets:
            with self.subTest(preset=preset.name):
                self.commands.clear()
                self.downloads.clear()
                lines = preset.read_text().splitlines()
                lines = ["setting:capture_path=" + str(self.captures)
                         if line.startswith("setting:capture_path=") else
                         "setting:interval=3600" if line.startswith("setting:interval=") else
                         "setting:start=" + str(self.first) if line.startswith("setting:start=") else line
                         for line in lines]
                data = self.importer.create_datawall_data(
                    lines, show_dialog=False, error_collector=[])
                report = next(json.loads(value) for key, value in data["info"].items()
                              if key.startswith("timelapse "))
                self.assertEqual(report["summary"]["missing_count"], 0)
                self.assertEqual(report["summary"]["actual_count"],
                                 report["summary"]["expected_count"])
                self.assertEqual(sum(command.startswith("timelapse ")
                                     for command in self.commands), 1)
                self.assertEqual(data["settings"]["capture_path"], str(self.captures))
                module_name = next(line.split("=", 1)[1] for line in lines
                                   if line.startswith("module="))
                module = importlib.import_module("datawall_" + module_name)
                before = os.getcwd()
                try:
                    os.chdir(self.root)
                    # Automatic creation calls make_datawall with empty opts.
                    output = module.make_datawall(data, opts={})
                finally:
                    os.chdir(before)
                with Image.open(self.root / output) as wall:
                    self.assertEqual(wall.width, 1200)
                    self.assertGreater(wall.height, 500)
                if module_name.endswith("fast"):
                    self.assertEqual(self.downloads, [])
                    self.assertEqual(data["images"], {})
                    self.assertNotIn("points", report)
                else:
                    self.assertEqual(set(data["images"]), {
                        "timelapse_latest", *["timelapse_{}".format(i) for i in range(1, 6)]})
                    self.assertTrue(all(Path(path).is_file() for path in data["images"].values()))
                    self.assertLessEqual(len(self.downloads), 6)
                    self.assertEqual(len(self.downloads), len(set(self.downloads)))
                    self.assertEqual(report["summary"]["selection"], data["settings"]["gallery_mode"])


if __name__ == "__main__":
    unittest.main()
