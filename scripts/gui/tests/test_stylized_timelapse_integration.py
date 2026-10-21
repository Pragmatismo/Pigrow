"""The experimental builder coexists with the legacy tool and imports full sets."""

import datetime as dt
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
import wx
from PIL import Image
from panels import timelapse_pnl
from shared_data import shared_data


class StylizedTimelapseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="stylized-import-")
        self.root = Path(self.folder.name)
        self.frame = wx.Frame(None)
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.frame.shared_data = SimpleNamespace(
            frompi_path=str(self.root), frompi_base_path=str(self.root),
            title_font=font, sub_title_font=font, item_title_font=font, info_font=font,
            get_module_options=lambda prefix, folder: sorted(
                path.stem.removeprefix(prefix) for path in (GUI / folder).glob(prefix + "*.py")),
            scale_pic=lambda image, size: shared_data.scale_pic(None, image, size),
        )
        self.ctrl = timelapse_pnl.ctrl_pnl(self.frame)
        self.frame.dict_C_pnl = {"timelapse_pnl": self.ctrl}
        self.info = timelapse_pnl.info_pnl(self.frame)
        self.frame.dict_I_pnl = {"timelapse_pnl": self.info}

    def tearDown(self):
        self.frame.Destroy()
        self.app.Yield(True)
        self.folder.cleanup()

    def image(self, name):
        path = self.root / name
        with Image.new("RGB", (48, 32), "red") as image:
            image.save(path)
        return str(path)

    def test_new_button_is_below_legacy_and_dialog_is_modeless_snapshot(self):
        sizer = self.ctrl.make_imgset_sizer()
        labels = [item.GetWindow().GetLabel() for item in sizer.GetChildren()]
        self.assertEqual(labels[-2:], ["Stylized Set", "Stylized Set (new)"])
        self.ctrl.trimmed_frame_list = ["one.jpg", "two.jpg"]
        with mock.patch("panels.stylized_set_dialog.StylizedSetDialog") as factory:
            dialog = factory.return_value
            dialog.IsBeingDeleted.return_value = False
            self.ctrl.stylized_new_click(None)
            snapshot = factory.call_args.args[1]
            self.ctrl.trimmed_frame_list.append("three.jpg")
            self.assertEqual(snapshot, ["one.jpg", "two.jpg"])
            dialog.Show.assert_called_once_with()
            dialog.ShowModal.assert_not_called()
            self.ctrl.stylized_new_click(None)
            factory.assert_called_once()
            dialog.Raise.assert_called_once()

    def test_empty_selection_has_clear_message_and_does_not_open_builder(self):
        with mock.patch.object(wx, "MessageBox") as message:
            self.ctrl.stylized_new_click(None)
        self.assertIn("at least one image", message.call_args.args[0])
        self.assertIsNone(getattr(self.ctrl, "_stylized_new_dialog", None))

    def test_using_new_set_clears_old_filters_and_keeps_every_frame(self):
        paths = [self.image("experiment_{:08d}_{}.png".format(index, suffix))
                 for index, suffix in enumerate(("1700000000", "1700000000.125", "undated"), 1)]
        self.ctrl.calc_cb.SetValue(False)
        self.ctrl.use_every_tc.ChangeValue("3")
        self.ctrl.min_size_tc.ChangeValue("999999999")
        self.ctrl.time_lim_tc.ChangeValue("1")
        self.ctrl.time_lim_cb.SetValue("hours")
        self.ctrl.time_picker_before.SetTime(12, 0, 0)
        self.ctrl.time_picker_after.SetTime(13, 0, 0)
        self.ctrl._use_new_stylized_set(str(self.root), "png", "experiment")
        self.assertEqual(self.ctrl.cap_file_paths, paths)
        self.assertEqual(self.ctrl.trimmed_frame_list, paths)
        self.assertEqual(self.ctrl.time_lim_cb.GetValue(), "all")
        self.assertEqual(self.ctrl.use_every_tc.GetValue(), "")
        self.assertFalse(self.ctrl.calc_cb.GetValue())
        self.assertEqual(self.info.frame_count_t.GetLabel(), "3")
        self.assertEqual(self.info.interval_t.GetLabel(), "undetermined")
        self.assertIn("Capture time unknown", self.info.last_img_l.GetLabel())

    def test_one_frame_and_last_frame_are_included_and_zero_fps_is_safe(self):
        first = self.image("trial_00000001_1700000000.png")
        self.ctrl._use_new_stylized_set(str(self.root), "png", "trial")
        self.assertEqual(self.ctrl.trimmed_frame_list, [first])
        last = self.image("trial_00000002_1700000300.png")
        self.ctrl.fps_tc.ChangeValue("0")
        self.ctrl._use_new_stylized_set(str(self.root), "png", "trial")
        self.assertEqual(self.ctrl.trimmed_frame_list, [first, last])
        self.assertEqual(self.info.interval_t.GetLabel(), "0:05:00")
        self.assertEqual(self.info.speed_t.GetLabel(), "0")

    def test_capture_suffix_parser_handles_exported_dates_and_unknown_filters(self):
        self.assertEqual(self.info.date_from_filename("set_00000001_20260102123456.png")[1],
                         dt.datetime(2026, 1, 2, 12, 34, 56))
        self.assertEqual(self.info.date_from_filename("set_00000001_1700000000.125.png")[1].microsecond,
                         125000)
        unknown = "set_00000002_undated.png"
        self.assertEqual(self.info.date_from_filename(unknown)[1], "undetermined")
        self.ctrl.time_lim_cb.SetValue("days")
        self.ctrl.time_lim_tc.ChangeValue("1")
        self.assertEqual(self.ctrl.limit_to_date([unknown]), [])
        self.ctrl.time_picker_before.SetTime(10, 0, 0)
        self.assertEqual(self.ctrl.limit_by_time_cutoff([unknown]), [])


if __name__ == "__main__":
    unittest.main()
