"""Exercise the real analysis workflow with fake controls; no display or Pi needed."""

from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from PIL import Image

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
try:
    import wx
except ImportError:
    panel = None
else:
    from panels import timelapse_pnl as panel


class Control:
    def __init__(self, value=""):
        self.value = value
        self.enabled = True
        self.shown = True
        self.label = ""

    def GetValue(self):
        return self.value

    def SetLabel(self, value):
        self.label = value

    def Wrap(self, width):
        pass

    def Show(self):
        self.shown = True

    def Hide(self):
        self.shown = False

    def Disable(self):
        self.enabled = False

    def Enable(self, enabled=True):
        self.enabled = enabled


class Harness:
    def Layout(self):
        pass


if panel is not None:
    # Bind actual production methods to a small host instead of constructing wx windows.
    for name in ("get_analyse_opts", "do_analyse_click", "_run_analyse_set",
                 "_on_analyse_result", "_restore_analysis_controls", "_show_analysis_error",
                 "_cleanup_analysis_folder", "graph_image_in_process", "on_analysis_destroy"):
        setattr(Harness, name, getattr(panel.info_pnl, name))


@unittest.skipIf(panel is None, "wxPython is required to import the timelapse panel")
class AnalysisPanelTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="timelapse-analysis-panel-")
        self.root = Path(self.folder.name)
        self.host = Harness()
        self.host.parent = SimpleNamespace(shared_data=SimpleNamespace(
            frompi_path=str(self.root), frompi_base_path=str(self.root),
            get_module_options=lambda *args: ["filesize", "daygridGPT", "custom", "not-valid"]))
        self.host.c_pnl = SimpleNamespace(trimmed_frame_list=["one.jpg", "two.jpg"])
        self.host.analyse_cb = Control("filesize")
        self.host.do_analyse_btn = Control()
        self.host.graph_image_box = Control()
        self.host.graph_progress_l = Control()
        self.host.graph_image_path = "previous.png"
        self.host._analysis_running = False
        self.host._analysis_destroyed = False
        self.host._analysis_output_dir = None
        self.host._graph_output_dir = None
        self.host._analysis_option = "filesize"
        self.host.set_graph_image = mock.Mock(side_effect=self.display)
        self.importer = mock.patch.object(panel.importlib, "import_module",
                                          return_value=SimpleNamespace(analyse_set=self.write_image))
        self.importer.start()
        self.worker = mock.patch.object(panel.delayedresult, "startWorker")
        self.start_worker = self.worker.start()
        self.addCleanup(self.importer.stop)
        self.addCleanup(self.worker.stop)

    def tearDown(self):
        self.folder.cleanup()

    def display(self, path):
        self.host.graph_image_path = path

    @staticmethod
    def write_image(frames, path):
        Image.new("RGB", (8, 8), "red").save(path)
        return True

    def assert_restored(self):
        self.assertTrue(self.host.do_analyse_btn.enabled)
        self.assertTrue(self.host.analyse_cb.enabled)
        self.assertTrue(self.host.graph_image_box.shown)
        self.assertFalse(self.host._analysis_running)

    def result_folder(self):
        output = self.root / "output"
        output.mkdir()
        self.host._analysis_output_dir = str(output)
        self.host._analysis_running = True
        self.host.graph_image_in_process()
        return output

    def test_options_remove_obsolete_tool_but_keep_custom_modules(self):
        self.assertEqual(self.host.get_analyse_opts(), ["custom", "filesize"])

    def test_start_freezes_frames_and_function_in_unique_output_folder(self):
        self.host.do_analyse_click(None)
        self.assertFalse(self.host.do_analyse_btn.enabled)
        self.assertFalse(self.host.analyse_cb.enabled)
        frames, output, analyse = self.start_worker.call_args.kwargs["wargs"]
        self.host.c_pnl.trimmed_frame_list[:] = ["changed.jpg"]
        self.assertEqual(frames, ["one.jpg", "two.jpg"])
        self.assertFalse(Path(output).exists())
        self.assertTrue(Path(output).parent.is_dir())
        self.assertIs(analyse, self.write_image)
        self.host.do_analyse_click(None)
        self.assertEqual(self.start_worker.call_count, 1)

    def test_empty_selection_and_import_failure_restore_controls(self):
        self.host.c_pnl.trimmed_frame_list.clear()
        self.host.do_analyse_click(None)
        self.assert_restored()
        self.assertIn("at least one image", self.host.graph_progress_l.label)
        self.host.c_pnl.trimmed_frame_list.append("one.jpg")
        with mock.patch.object(panel.importlib, "import_module", side_effect=ImportError("tool missing")):
            self.host.do_analyse_click(None)
        self.assert_restored()
        self.assertIn("tool missing", self.host.graph_progress_l.label)
        self.start_worker.assert_not_called()

    def test_folder_setup_failure_restores_controls(self):
        with mock.patch.object(panel.os, "makedirs", side_effect=PermissionError("folder is read only")):
            self.host.do_analyse_click(None)
        self.assert_restored()
        self.assertIn("read only", self.host.graph_progress_l.label)

    def test_worker_start_failure_cleans_output_and_restores_controls(self):
        self.start_worker.side_effect = RuntimeError("cannot start worker")
        self.host.do_analyse_click(None)
        self.assert_restored()
        self.assertEqual(list((self.root / "temp").iterdir()), [])
        self.assertIn("cannot start worker", self.host.graph_progress_l.label)

    def test_worker_requires_success_and_a_fresh_readable_output(self):
        output = self.root / "result.png"
        for result in (False, None, "error - failed"):
            with self.subTest(result=result):
                with self.assertRaises(ValueError):
                    self.host._run_analyse_set([], str(output), lambda *args: result)
        with self.assertRaisesRegex(ValueError, "without creating"):
            self.host._run_analyse_set([], str(output), lambda *args: True)
        output.write_bytes(b"not an image")
        with self.assertRaises(Exception):
            self.host._run_analyse_set([], str(output), lambda *args: True)
        output.unlink()
        self.assertEqual(self.host._run_analyse_set([], str(output), self.write_image), str(output))

    def test_result_failure_keeps_previous_preview_cleans_output_and_restores(self):
        output = self.result_folder()
        result = mock.Mock()
        result.get.side_effect = RuntimeError("bad image data")
        self.host._on_analyse_result(result)
        self.assert_restored()
        self.assertFalse(output.exists())
        self.assertEqual(self.host.graph_image_path, "previous.png")
        self.assertTrue(self.host.graph_progress_l.shown)
        self.assertIn("bad image data", self.host.graph_progress_l.label)

    def test_display_failure_keeps_previous_preview_and_restores(self):
        output = self.result_folder()
        self.host.set_graph_image.side_effect = RuntimeError("preview could not be displayed")
        self.host._on_analyse_result(SimpleNamespace(get=lambda: str(output / "result.png")))
        self.assert_restored()
        self.assertFalse(output.exists())
        self.assertEqual(self.host.graph_image_path, "previous.png")

    def test_success_retains_current_output_and_removes_old_output(self):
        old = self.root / "old"
        old.mkdir()
        self.host._graph_output_dir = str(old)
        output = self.result_folder()
        image = output / "result.png"
        self.write_image([], image)
        self.host._on_analyse_result(SimpleNamespace(get=lambda: str(image)))
        self.assert_restored()
        self.assertTrue(output.exists())
        self.assertFalse(old.exists())
        self.assertEqual(self.host.graph_image_path, str(image))
        self.assertFalse(self.host.graph_progress_l.shown)

    def test_callback_after_panel_destroy_only_cleans_temporary_output(self):
        output = self.result_folder()
        event = SimpleNamespace(GetEventObject=lambda: self.host, Skip=mock.Mock())
        self.host.on_analysis_destroy(event)
        self.assertTrue(output.exists())
        self.host._on_analyse_result(SimpleNamespace(get=mock.Mock()))
        self.assertFalse(output.exists())
        self.host.set_graph_image.assert_not_called()


if __name__ == "__main__":
    unittest.main()
