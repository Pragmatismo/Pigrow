"""Datawall preset/import checks using a fake Pi and optional real wx controls.

Run with wxPython installed; widget checks also need a display, for example::

    xvfb-run -a /usr/bin/python3 scripts/gui/tests/test_datawall_import.py

The importer checks run without a display. Shell-wrapper checks also require
Paramiko to import the connection panel. No SSH connection or Pi is used.
"""

import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import patch

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
try:
    import wx
except ImportError:
    wx = None

if wx is not None:
    from panels import datawall_pnl

HAS_PARAMIKO = importlib.util.find_spec("paramiko") is not None
if wx is not None and HAS_PARAMIKO:
    from panels import link_pnl


class FakeLink:
    def __init__(self, local_folder):
        self.local_folder = Path(local_folder)
        self.commands = []
        self.downloads = []
        self.response = "plain info"
        self.files = {}
        self.failures = set()
        self.missing = set()

    def run_on_pi(self, command):
        self.commands.append(command)
        return self.response, ""

    def download_file_to_folder(self, remote_path, relative_path):
        self.downloads.append((remote_path, relative_path))
        destination = self.local_folder / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if remote_path in self.failures:
            destination.write_bytes(b"partial")
            raise OSError("Capture disappeared during download")
        if remote_path not in self.missing:
            destination.write_bytes(self.files.get(remote_path, b"test"))
        return str(destination)


class LocalShellSSH:
    """Execute the exact SSH command string through the remote shell boundary."""
    def __init__(self):
        self.commands = []

    def exec_command(self, command):
        self.commands.append(command)
        result = subprocess.run(["/bin/sh", "-c", command], capture_output=True,
                                timeout=5, check=False)
        return None, io.BytesIO(result.stdout), io.BytesIO(result.stderr)


@unittest.skipIf(wx is None or not HAS_PARAMIKO, "wxPython and Paramiko are required")
class DatawallCommandBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        remote_root = self.root / "Pigrow's timelapse tools; $HOME"
        module = remote_root / "scripts" / "gui" / "info_modules" / "info_timelapse.py"
        module.parent.mkdir(parents=True)
        module.write_text("#!" + sys.executable + "\n"
                          "import json, sys\nprint(json.dumps(sys.argv[1:]))\n")
        module.chmod(0o700)
        self.ssh = LocalShellSSH()
        link = SimpleNamespace(ssh=self.ssh)
        link.run_on_pi = MethodType(link_pnl.link_pnl.run_on_pi, link)
        self.panel = SimpleNamespace(
            shared_data=SimpleNamespace(frompi_path=str(self.root / "downloads"),
                                        remote_pigrow_path=str(remote_root) + "/"),
            parent=SimpleNamespace(link_pnl=link),
        )
        for name in ("create_datawall_data", "read_info_module", "_import_info_images",
                     "_download_manifest_image"):
            setattr(self.panel, name, MethodType(getattr(datawall_pnl.ctrl_pnl, name), self.panel))

    def tearDown(self):
        self.folder.cleanup()

    def test_real_link_wrapper_preserves_setting_values_and_quoted_module_path(self):
        marker = self.root / "unexpected-command"
        capture_path = ("/captures with an apostrophe's; $(touch " + str(marker) + ") "
                        "`touch " + str(marker) + "` $HOME")
        start = "2026-10-16 17:00:00"
        command = "timelapse path={capture_path} start={start} interval={interval}"
        result = self.panel.create_datawall_data([
            "info_read=" + command,
            "setting:capture_path=" + capture_path,
            "setting:start=" + start,
            "setting:interval=60",
        ])
        self.assertEqual(json.loads(result["info"][command]), [
            "path=" + capture_path, "start=" + start, "interval=60",
        ])
        self.assertFalse(marker.exists())
        self.assertEqual(len(self.ssh.commands), 1)

    def test_explicit_legacy_argument_quotes_survive_the_wrapper(self):
        command = "timelapse path='existing capture folder' start='2026-10-16 17:00:00'"
        result = self.panel.create_datawall_data(["info_read=" + command])
        self.assertEqual(json.loads(result["info"][command]), [
            "path=existing capture folder", "start=2026-10-16 17:00:00",
        ])
        self.assertNotIn("settings", result)


@unittest.skipIf(wx is None, "wxPython is required to import the GUI panel")
class DatawallImportTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.link = FakeLink(self.folder.name)
        self.requests = []
        self.panel = SimpleNamespace(
            shared_data=SimpleNamespace(frompi_path=self.folder.name),
            parent=SimpleNamespace(link_pnl=self.link),
        )
        for name in ("create_datawall_data", "_import_info_images", "_download_manifest_image"):
            setattr(self.panel, name, MethodType(getattr(datawall_pnl.ctrl_pnl, name), self.panel))

        def read_info(command):
            self.requests.append(command)
            return self.link.response

        self.panel.read_info_module = read_info
        self.panel.get_image = lambda value: "old-picture:" + value

    def tearDown(self):
        self.folder.cleanup()

    def manifest(self, images):
        self.link.response = json.dumps({"datawall_images": images})
        return self.panel.create_datawall_data(["info_read=timelapse mode=detailed"])

    def test_existing_plain_info_and_picture_import_are_unchanged(self):
        result = self.panel.create_datawall_data([
            "module=general", "info_read=boxname", "picture_path:recent=recent",
        ])
        self.assertEqual(result["info"], {"boxname": "plain info"})
        self.assertEqual(result["images"], {"recent": "old-picture:recent"})
        self.assertNotIn("settings", result)
        self.assertNotIn("image_errors", result)
        self.assertEqual(self.requests, ["boxname"])
        self.assertEqual(self.link.downloads, [])

    def test_settings_are_available_before_their_lines_and_are_shell_quoted(self):
        capture_path = "/captures with spaces/$(not-a-command); 'quote'"
        command = "timelapse path={capture_path} interval={interval} extra={unknown}"
        result = self.panel.create_datawall_data([
            "info_read=" + command,
            "setting:capture_path=" + capture_path,
            "setting:interval=60",
        ])
        self.assertEqual(shlex.split(self.requests[0]), [
            "timelapse", "path=" + capture_path, "interval=60", "extra={unknown}",
        ])
        self.assertEqual(result["info"], {command: "plain info"})
        self.assertEqual(result["settings"]["capture_path"], capture_path)

    def test_unconfigured_commands_and_non_named_braces_are_unchanged(self):
        command = 'legacy argument={capture_path} json={"value": 1}'
        self.panel.create_datawall_data(["info_read=" + command])
        self.assertEqual(self.requests, [command])
        self.assertEqual(datawall_pnl._info_command_with_settings(
            command, {"capture_path": "auto"}),
            'legacy argument=auto json={"value": 1}')

    def test_shared_hero_and_thumbnail_download_once_and_use_local_cache(self):
        entry = {"path": "/captures/latest.jpg", "size": 4, "mtime": 1000}
        result = self.manifest({"latest": entry, "thumbnail_1": entry, "thumbnail_2": None})
        self.assertEqual(len(self.link.downloads), 1)
        self.assertEqual(result["images"]["latest"], result["images"]["thumbnail_1"])
        self.assertIsNone(result["images"]["thumbnail_2"])
        self.assertEqual(Path(result["images"]["latest"]).read_bytes(), b"test")
        self.assertTrue(Path(result["images"]["latest"]).is_relative_to(self.folder.name))
        self.assertNotIn("image_errors", result)
        self.manifest({"latest": entry})
        self.assertEqual(len(self.link.downloads), 1)
        self.assertEqual(len(self.requests), 2)

    def test_cache_distinguishes_full_remote_paths_and_changed_metadata(self):
        first = {"path": "/first/caps/image.jpg", "size": 4, "mtime": 10}
        second = {"path": "/second/caps/image.jpg", "size": 4, "mtime": 10}
        result = self.manifest({"first": first, "second": second})
        self.assertNotEqual(result["images"]["first"], result["images"]["second"])
        changed = dict(first, mtime=11)
        refreshed = self.manifest({"first": changed})
        self.assertNotEqual(result["images"]["first"], refreshed["images"]["first"])
        self.assertEqual(len(self.link.downloads), 3)

    def test_partial_cached_files_are_downloaded_again(self):
        entry = {"path": "/captures/image.jpg", "size": 4, "mtime": 10}
        result = self.manifest({"latest": entry})
        Path(result["images"]["latest"]).write_bytes(b"x")
        refreshed = self.manifest({"latest": entry})
        self.assertEqual(Path(refreshed["images"]["latest"]).read_bytes(), b"test")
        self.assertEqual(len(self.link.downloads), 2)

    def test_failed_duplicate_download_is_attempted_once_and_partial_file_removed(self):
        entry = {"path": "/captures/missing.jpg", "size": 4, "mtime": 10}
        self.link.failures.add(entry["path"])
        result = self.manifest({"latest": entry, "thumbnail_1": entry})
        self.assertEqual(result["images"], {"latest": None, "thumbnail_1": None})
        self.assertEqual(set(result["image_errors"]), {"latest", "thumbnail_1"})
        self.assertEqual(len(self.link.downloads), 1)
        self.assertFalse((Path(self.folder.name) / self.link.downloads[0][1]).exists())

    def test_missing_download_and_wrong_size_are_reported_per_image(self):
        absent = {"path": "/captures/absent.jpg", "size": 4, "mtime": 10}
        wrong_size = {"path": "/captures/short.jpg", "size": 100, "mtime": 10}
        self.link.missing.add(absent["path"])
        result = self.manifest({"missing": absent, "wrong_size": wrong_size})
        self.assertIsNone(result["images"]["missing"])
        self.assertIsNone(result["images"]["wrong_size"])
        self.assertIn("missing", result["image_errors"]["missing"].lower())
        self.assertIn("size", result["image_errors"]["wrong_size"].lower())

    def test_invalid_json_and_manifest_entries_do_not_abort_import(self):
        for response in ("", "{invalid JSON", "[]", "null", '{"datawall_images": []}'):
            with self.subTest(response=response):
                self.link.response = response
                result = self.panel.create_datawall_data(["info_read=timelapse"])
                self.assertEqual(result["info"]["timelapse"], response)
                self.assertEqual(result["images"], {})
        result = self.manifest({"bad": {"size": 4}, "also_bad": "path.jpg", "empty": None})
        self.assertEqual(result["images"], {"bad": None, "also_bad": None, "empty": None})
        self.assertEqual(set(result["image_errors"]), {"bad", "also_bad"})
        self.assertEqual(self.link.downloads, [])


HAS_DISPLAY = bool(os.environ.get("DISPLAY")) or sys.platform in ("win32", "darwin")


@unittest.skipIf(wx is None or not HAS_DISPLAY, "wxPython and a display are required")
class DatawallPresetWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.previous_cwd = os.getcwd()
        os.chdir(self.folder.name)
        self.link = FakeLink(self.folder.name)
        self.frame = wx.Frame(None)
        self.frame.shared_data = SimpleNamespace(
            frompi_path=self.folder.name,
            remote_pigrow_path="/home/pi/Pigrow/",
        )
        self.frame.link_pnl = self.link
        self.frame.dict_C_pnl = {}
        self.panel = datawall_pnl.ctrl_pnl(self.frame)
        self.panel.module_choice.Append("timelapse_test")
        self.panel.module_choice.SetStringSelection("timelapse_test")
        self.presets = self.panel.preset_options_panel
        self.request = "timelapse mode=detailed path={capture_path} daily_time={daily_time}"
        self.presets.update_preset_panel({
            "settings": {
                "capture_path": "auto", "interval": "auto", "start": "auto",
                "gallery_mode": ["recent", "hourly", "daily"], "daily_time": "1700",
                "test_checkbox": "false",
            },
            "info_read": [self.request],
        })

    def tearDown(self):
        self.frame.Destroy()
        self.app.ProcessPendingEvents()
        os.chdir(self.previous_cwd)
        self.folder.cleanup()

    def test_settings_save_restore_control_types_and_parameterize_import(self):
        controls = self.presets.settings_panel.controls
        self.assertIsInstance(controls["gallery_mode"], wx.ComboBox)
        self.assertIsInstance(controls["daily_time"], wx.TextCtrl)
        self.assertIsInstance(controls["test_checkbox"], wx.CheckBox)
        controls["capture_path"].SetValue("/captures with spaces")
        controls["interval"].SetValue("60")
        controls["gallery_mode"].SetValue("daily")
        controls["daily_time"].SetValue("0700")
        controls["test_checkbox"].SetValue(True)
        with patch.object(wx, "GetTextFromUser", return_value="saved"), patch.object(wx, "MessageBox"):
            self.presets.on_save(None)
        saved_text = Path("datawall_presets/datawall_saved.txt").read_text()
        self.assertIn("setting:daily_time=0700", saved_text)
        self.assertIn("setting:test_checkbox=true", saved_text)
        self.assertIn("info_read=" + self.request, saved_text)

        controls["capture_path"].SetValue("changed")
        controls["gallery_mode"].SetValue("hourly")
        controls["daily_time"].SetValue("1700")
        controls["test_checkbox"].SetValue(False)
        self.presets.on_preset_select(None)
        self.assertEqual(controls["capture_path"].GetValue(), "/captures with spaces")
        self.assertEqual(controls["gallery_mode"].GetValue(), "daily")
        self.assertEqual(controls["daily_time"].GetValue(), "0700")
        self.assertTrue(controls["test_checkbox"].GetValue())

        self.panel.on_import_data(None)
        self.assertEqual(self.panel.datawall_data["settings"]["daily_time"], "0700")
        self.assertIn(self.request, self.panel.datawall_data["info"])
        self.assertEqual(len(self.link.commands), 1)
        # FakeLink records the escaped input to run_on_pi; undo its outer shell
        # argument boundary before examining the actual info-module arguments.
        wrapper = "/bin/bash -l -c '" + self.link.commands[0] + "'"
        full_command = shlex.split(wrapper)[3]
        self.assertEqual(shlex.split(full_command)[1:], [
            "mode=detailed", "path=/captures with spaces", "daily_time=0700",
        ])

    def test_loading_preset_without_settings_restores_defaults(self):
        Path("datawall_presets").mkdir()
        Path("datawall_presets/datawall_legacy.txt").write_text("module=timelapse_test\n")
        controls = self.presets.settings_panel.controls
        controls["capture_path"].SetValue("changed")
        controls["daily_time"].SetValue("0700")
        controls["test_checkbox"].SetValue(True)
        self.presets.preset_choice.Append("legacy")
        self.presets.preset_choice.SetStringSelection("legacy")
        self.presets.on_preset_select(None)
        self.assertEqual(controls["capture_path"].GetValue(), "auto")
        self.assertEqual(controls["daily_time"].GetValue(), "1700")
        self.assertFalse(controls["test_checkbox"].GetValue())

    def test_switching_to_module_without_settings_clears_old_controls(self):
        self.presets.update_preset_panel({"info_read": ["boxname"]})
        self.assertIsNone(self.presets.settings_panel)
        self.assertFalse(any(line.startswith("setting:") for line in self.presets.get_text()))


if __name__ == "__main__":
    unittest.main()
