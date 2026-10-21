"""Real wx modeless builder, preview lifecycle and independent export monitoring."""

from copy import deepcopy
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from PIL import Image

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
try:
    import wx
except ImportError:
    wx = None
else:
    from panels import stylized_set_dialog as editor
    from stylized_sets import default_layer, default_settings


@unittest.skipIf(wx is None or not os.environ.get("DISPLAY"), "wxPython and a display are required")
class StylizedSetDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)
        cls.app.SetExitOnFrameDelete(False)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="stylized-dialog-")
        self.root = Path(self.folder.name)
        self.frames = []
        for index, color in enumerate(((15, 30, 45), (70, 40, 50), (80, 95, 105))):
            path = self.root / "cap_{}.png".format(1720000000 + index)
            with Image.new("RGB", (80, 60), color) as image:
                image.save(path)
            self.frames.append(str(path))
        self.parent = wx.Frame(None)
        self.use_set = mock.Mock()
        self.dialogs = []
        self.progress = []

    def tearDown(self):
        for dialog in self.dialogs:
            if dialog and not dialog.IsBeingDeleted():
                dialog.Destroy()
        for progress in self.progress:
            if progress and not progress.IsBeingDeleted():
                progress.Destroy()
        if self.parent and not self.parent.IsBeingDeleted():
            self.parent.Destroy()
        self.app.ProcessPendingEvents()
        self.app.Yield(True)
        self.folder.cleanup()

    def builder(self, **kwargs):
        kwargs.setdefault("preset_path", self.root / "presets.json")
        dialog = editor.StylizedSetDialog(self.parent, self.frames, str(self.root),
                                          on_use_set=self.use_set, **kwargs)
        self.dialogs.append(dialog)
        dialog.Show()
        self.app.Yield(True)
        return dialog

    def wait_for(self, predicate, timeout=6):
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            self.app.ProcessPendingEvents()
            self.app.Yield(True)
            time.sleep(0.01)
        self.assertTrue(predicate(), "Timed out waiting for asynchronous GUI work")

    def test_initial_second_frame_next_and_reset_rebuild_state(self):
        dialog = self.builder()
        self.assertFalse(dialog.IsModal())
        self.wait_for(lambda: dialog._preview_index == 1)
        revision = dialog._preview_revision
        dialog.on_next(None)
        self.wait_for(lambda: dialog._preview_index == 2)
        self.assertEqual(dialog._preview_revision, revision)
        self.assertFalse(dialog.next_button.IsEnabled())
        dialog.on_reset(None)
        self.wait_for(lambda: dialog._preview_index == 1 and dialog.next_button.IsEnabled())
        self.assertGreater(dialog._preview_revision, revision)
        self.assertIn("Output image 2 of 3", dialog.preview_status.GetLabel())

    def test_single_input_previews_first_and_snapshots_source_list(self):
        self.frames[:] = self.frames[:1]
        dialog = self.builder()
        self.frames.clear()
        self.wait_for(lambda: dialog._preview_index == 0)
        self.assertEqual(len(dialog.frames), 1)
        self.assertFalse(dialog.next_button.IsEnabled())

    def test_layer_add_duplicate_reorder_remove_and_disable(self):
        dialog = self.builder()
        original = deepcopy(dialog._settings["layers"][0])
        dialog.on_duplicate_layer(None)
        self.assertEqual(len(dialog._settings["layers"]), 2)
        self.assertEqual(dialog._selected_layer, 1)
        dialog.layer_controls["name"].SetValue("Second effect")
        dialog.layer_controls["enabled"].SetValue(False)
        dialog.on_layer_change(None)
        self.assertFalse(dialog._settings["layers"][1]["enabled"])
        dialog.on_layer_up(None)
        self.assertEqual(dialog._settings["layers"][0]["name"], "Second effect")
        self.assertEqual(dialog._settings["layers"][1], original)
        dialog.on_layer_down(None)
        self.assertEqual(dialog._settings["layers"][0], original)
        dialog.on_remove_layer(None)
        self.assertEqual(dialog._settings["layers"], [original])
        dialog.on_add_layer(None)
        self.assertEqual(len(dialog._settings["layers"]), 2)
        snapshot = dialog.get_settings()
        snapshot["layers"][0]["name"] = "mutated copy"
        self.assertEqual(dialog._settings["layers"][0], original)
        for unused in range(20):
            dialog.on_add_layer(None)
        self.assertEqual(len(dialog._settings["layers"]), 16)
        self.assertFalse(dialog.layer_buttons["add"].IsEnabled())
        self.assertFalse(dialog.layer_buttons["duplicate"].IsEnabled())

    def test_irrelevant_options_disable_and_invalid_tint_recovers(self):
        dialog = self.builder()
        editor._select_value(dialog.layer_controls["source"], editor.SOURCE_CHOICES, "copy")
        editor._select_value(dialog.layer_controls["persistence"], editor.PERSISTENCE_CHOICES, "permanent")
        dialog.on_layer_change(None)
        self.assertFalse(dialog.layer_controls["threshold"].IsEnabled())
        self.assertFalse(dialog.layer_controls["trail_frames"].IsEnabled())
        self.assertFalse(dialog.layer_controls["decay"].IsEnabled())
        editor._select_value(dialog.layer_controls["persistence"], editor.PERSISTENCE_CHOICES, "trail")
        dialog.on_layer_change(None)
        self.assertTrue(dialog.layer_controls["trail_frames"].IsEnabled())
        self.assertTrue(dialog.layer_controls["decay"].IsEnabled())
        dialog.layer_controls["tint"].SetValue("#bad")
        dialog.on_layer_change(None)
        self.assertFalse(dialog.create_button.IsEnabled())
        self.assertIn("tint", dialog.validation_status.GetLabel())
        dialog.layer_controls["tint"].SetValue("#33aaff")
        dialog.on_layer_change(None)
        self.assertTrue(dialog.create_button.IsEnabled())
        self.assertEqual(dialog.get_settings()["layers"][0]["tint"], "#33aaff")

    def test_corrupt_presets_fall_back_visibly_and_save_round_trip(self):
        damaged = self.root / "damaged.json"
        damaged.write_text("{invalid json", encoding="utf-8")
        dialog = self.builder(preset_path=damaged)
        self.assertIn("Could not load saved presets", dialog.preset_status.GetLabel())
        self.assertTrue(dialog.preset_choice.GetCount())
        dialog.preset_path = self.root / "saved.json"
        entry = mock.Mock()
        entry.ShowModal.return_value = wx.ID_OK
        entry.GetValue.return_value = "My exact layers"
        with mock.patch.object(editor.wx, "TextEntryDialog", return_value=entry):
            dialog.on_save_preset(None)
        self.assertEqual(dialog.preset_choice.GetStringSelection(), "My exact layers")
        loaded = editor.load_presets(path=dialog.preset_path)
        self.assertEqual(loaded["My exact layers"], dialog.get_settings())
        entry.Destroy.assert_called_once()

    def test_stale_preview_is_discarded_and_close_releases_on_worker_thread(self):
        started = threading.Event()
        release = threading.Event()
        closed = threading.Event()
        closing_started = threading.Event()
        closing_release = threading.Event()
        instances = []
        main_thread = threading.get_ident()

        class FakeSession:
            def __init__(self, frames, settings, max_size):
                self.number = len(instances)
                self.worker_thread = threading.get_ident()
                self.closed_thread = None
                instances.append(self)

            def preview(self, index):
                if self.number == 0:
                    started.set()
                    release.wait(5)
                elif self.number == 2:
                    closing_started.set()
                    closing_release.wait(5)
                return Image.new("RGB", (80, 60), "red" if self.number == 0 else "blue")

            def close(self):
                self.closed_thread = threading.get_ident()
                closed.set()

        with mock.patch.object(editor, "PreviewSession", FakeSession):
            dialog = self.builder()
            self.wait_for(started.is_set)
            display = mock.Mock(wraps=dialog._display_preview)
            dialog._display_preview = display
            dialog.layer_controls["gain"].SetValue(2.0)
            dialog.on_layer_change(None)
            release.set()
            self.wait_for(lambda: dialog._preview_index == 1)
            self.assertEqual(display.call_count, 1)
            self.assertEqual(len(instances), 2)
            self.assertNotEqual(instances[0].worker_thread, main_thread)
            self.assertEqual(instances[0].closed_thread, instances[0].worker_thread)
            dialog.on_reset(None)
            self.wait_for(closing_started.is_set)
            dialog.Destroy()
            closing_release.set()
            self.app.Yield(True)
            self.wait_for(lambda: instances[2].closed_thread is not None)
            self.assertEqual(instances[2].closed_thread, instances[2].worker_thread)
            self.assertEqual(display.call_count, 1)

    def test_export_progress_survives_builder_close_and_imports_all_frames(self):
        dialog = self.builder()
        dialog.set_name.SetValue("my-styled-set")
        with mock.patch.object(editor.ExportProgressFrame, "start") as start:
            dialog.on_create(None)
        self.assertEqual(start.call_count, 1)
        progress = next(window for window in editor._EXPORT_WINDOWS
                        if window.GetParent() is self.parent)
        self.progress.append(progress)
        self.assertIs(progress.GetParent(), self.parent)
        job = progress.job
        dialog.Close()
        self.app.Yield(True)
        self.assertFalse(progress.IsBeingDeleted())
        progress.start()
        self.wait_for(lambda: progress._finished)
        state = job.snapshot()
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["completed"], 3)
        self.assertTrue(progress.use_button.IsEnabled())
        progress.on_use(None)
        self.use_set.assert_called_once_with(state["output_dir"], "png", "my-styled-set")
        self.assertEqual(len(list(Path(state["output_dir"]).glob("*.png"))), 3)

    def test_active_progress_close_minimizes_then_cancel_keeps_partial_set(self):
        state = {"status": "running", "completed": 2, "total": 10,
                 "output_dir": str(self.root / "partial"), "set_name": "partial", "error": ""}
        job = mock.Mock()
        job.snapshot.side_effect = lambda: dict(state)
        progress = editor.ExportProgressFrame(self.parent, job, on_use_set=self.use_set)
        self.progress.append(progress)
        progress.start()
        event = mock.Mock()
        event.CanVeto.return_value = True
        with mock.patch.object(progress, "Iconize") as iconize:
            progress.on_close(event)
        event.Veto.assert_called_once()
        iconize.assert_called_once_with(True)
        self.assertFalse(progress._finished)
        progress.on_cancel(None)
        job.cancel.assert_called_once()
        self.assertFalse(progress.cancel_button.IsEnabled())
        state["status"] = "cancelled"
        progress.on_poll(None)
        self.assertTrue(progress._finished)
        self.assertIn("2 completed images were kept", progress.status_text.GetLabel())
        progress.on_use(None)
        self.use_set.assert_called_once_with(state["output_dir"], "png", "partial")

    def test_builder_fits_a_common_laptop_window_with_bottom_actions_visible(self):
        dialog = self.builder()
        dialog.SetSize((1050, 700))
        dialog.Layout()
        self.app.Yield(True)
        client = dialog.GetClientRect()
        for button in (dialog.create_button, dialog.cancel_button):
            corner = dialog.ScreenToClient(button.ClientToScreen((button.GetSize().width, button.GetSize().height)))
            self.assertLessEqual(corner.x, client.width)
            self.assertLessEqual(corner.y, client.height)
        editor_panel = dialog.layer_list.GetParent()
        editor_panel.Scroll(0, 999)
        self.app.Yield(True)
        bottom_control = dialog.layer_controls["invert"]
        corner = editor_panel.ScreenToClient(bottom_control.ClientToScreen((0, 0)))
        self.assertGreaterEqual(corner.y, 0)
        self.assertLess(corner.y, editor_panel.GetClientSize().height)

    def test_preview_worker_submission_failure_is_visible_and_close_still_works(self):
        dialog = self.builder()
        self.wait_for(lambda: dialog._preview_index == 1)
        with mock.patch.object(dialog._executor, "submit", side_effect=RuntimeError("worker unavailable")):
            dialog.on_reset(None)
            dialog.on_preview_poll(None)
            self.assertIn("worker unavailable", dialog.preview_status.GetLabel())
            self.assertTrue(dialog.reset_button.IsEnabled())
            dialog.Destroy()
        self.app.Yield(True)

    def test_preview_failure_is_visible_and_reset_remains_available(self):
        with mock.patch.object(editor, "_render_preview", side_effect=ValueError("broken input")):
            dialog = self.builder()
            self.wait_for(lambda: "Preview failed" in dialog.preview_status.GetLabel())
            self.assertIn("broken input", dialog.preview_status.GetLabel())
            self.assertTrue(dialog.reset_button.IsEnabled())
            self.assertFalse(dialog.next_button.IsEnabled())


if __name__ == "__main__":
    unittest.main()
