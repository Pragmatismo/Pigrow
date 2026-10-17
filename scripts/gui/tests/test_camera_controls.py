"""Camera UI regressions using real wx widgets and a fake Raspberry Pi link.

Run with a display (or under ``xvfb-run -a``)::

    python3 scripts/gui/tests/test_camera_controls.py

No camera, SSH connection, or remote command is required.
"""

import os
from pathlib import Path
import shlex
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))

import wx
from PIL import Image, ImageGrab

from panels import camera_pnl
from panels.camera_controls import NumericControl
from panels.rpicap_set_pnl import SetAFROIDialog, parse_roi
from panels.image_region import ImageRegionDialog
from shared_data import shared_data


V4L2_CONTROLS = """User Controls
                     brightness 0x00980900 (int)    : min=0 max=255 step=1 default=128 value=128
                       contrast 0x00980901 (int)    : min=0 max=255 step=1 default=32 value=32
                   power_line_frequency 0x00980918 (menu)   : min=0 max=5 default=2 value=2
                                0: Disabled
                                2: 50 Hz
                                5: 60 Hz
                 white_balance_automatic 0x0098090c (bool)   : default=1 value=1
                          sensor_status 0x009a090b (int)    : min=0 max=255 step=1 default=0 value=2 flags=read-only
                          focus_absolute 0x009a090a (int)    : min=0 max=1023 step=1 default=0 value=17 flags=inactive"""


def config_dict(text):
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


class FakeLink:
    def __init__(self):
        self.commands = []
        self.written_configs = []
        self.responses = {}
        self.control_output = V4L2_CONTROLS
        self.resolution_output = """ioctl: VIDIOC_ENUM_FMT
    Size: Discrete 640x480
    Size: Discrete 1920x1080
"""

    def run_on_pi(self, command):
        self.commands.append(command)
        if command in self.responses:
            return self.responses[command]
        if "--list-ctrls" in command:
            return self.control_output, ""
        if "--list-formats" in command:
            return self.resolution_output, ""
        raise AssertionError("Unexpected remote command in UI test: " + command)

    def write_textfile_to_pi(self, text, path):
        self.written_configs.append((path, text))


class CameraControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)
        scratch_parent = GUI.parents[1] / "work"
        scratch_parent.mkdir(exist_ok=True)
        cls.scratch = tempfile.TemporaryDirectory(prefix="camera-ui-", dir=scratch_parent)
        cls.image_path = Path(cls.scratch.name) / "photograph.png"
        Image.new("RGB", (700, 1000), "#24546b").save(cls.image_path)
        cls.large_image_path = Path(cls.scratch.name) / "large-photograph.png"
        Image.new("RGB", (2400, 1200), "#24546b").save(cls.large_image_path)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def setUp(self):
        self.frame = wx.Frame(None, size=(1050, 700))
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.frame.shared_data = SimpleNamespace(
            button_font=font,
            title_font=font,
            sub_title_font=font,
            remote_pigrow_path="/home/pi/Pigrow/",
            camcomf_compare_image="",
            most_recent_camconf_image="",
        )
        self.frame.link_pnl = FakeLink()
        self.frame.dict_C_pnl = {}
        self.frame.dict_I_pnl = {}
        self.controls = camera_pnl.ctrl_pnl(self.frame)
        self.frame.dict_C_pnl["camera_pnl"] = self.controls
        self.panel = camera_pnl.info_pnl(self.frame)
        self.frame.dict_I_pnl["camera_pnl"] = self.panel
        self.controls.Hide()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.frame.SetSizer(sizer)
        self.frame.Show()
        self.pump()

    def tearDown(self):
        self.frame.Destroy()
        self.pump()

    def pump(self):
        self.app.ProcessPendingEvents()
        self.app.Yield(True)

    def select(self, tool):
        self.controls.captool_cb.SetValue(tool)
        self.controls.camcap_combo_go(None)
        self.frame.Layout()
        self.pump()
        return self.panel.sets_pnl

    def saved(self, panel):
        return config_dict(panel.make_conf_text(panel.setting_crtl_dict))

    def press(self, button):
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        button.GetEventHandler().ProcessEvent(event)
        self.pump()

    def check(self, checkbox, enabled):
        checkbox.SetValue(enabled)
        event = wx.CommandEvent(wx.EVT_CHECKBOX.typeId, checkbox.GetId())
        event.SetEventObject(checkbox)
        checkbox.GetEventHandler().ProcessEvent(event)
        self.pump()

    def screenshot(self, name):
        destination = os.environ.get("CAMERA_UI_SCREENSHOT_DIR")
        if destination:
            # Let GTK repaint through a real event loop before reading Xvfb.
            self.frame.Refresh()
            loop = wx.GUIEventLoop()
            wx.CallLater(80, loop.Exit)
            with wx.EventLoopActivator(loop):
                loop.Run()
            rect = self.frame.GetScreenRect()
            Path(destination).mkdir(parents=True, exist_ok=True)
            # ScreenDC on wxGTK can return a stale cached root bitmap.
            ImageGrab.grab(bbox=(rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)).save(
                Path(destination) / (name + ".png"))

    def test_existing_defaults_and_tool_switching(self):
        expected = {
            "picamcap": {"resolution": "1920x1080", "brightness": "50", "contrast": "0"},
            "fswebcam": {"resolution": "1920x1080", "fs_delay": "2", "fs_fskip": "5", "fs_jpg_q": "90"},
            "libcamera": {"resolution": "0x0", "brightness": "0", "contrast": "1", "quality": "93"},
            "rpicam": {"Resolution": "4608x2592", "brightness": "0", "autofocus-mode": "auto"},
        }
        for tool, defaults in expected.items():
            with self.subTest(tool=tool):
                panel = self.select(tool)
                actual = self.saved(panel)
                for key, value in defaults.items():
                    self.assertEqual(float(actual[key]), float(value)) if key in {"brightness", "contrast", "quality"} else self.assertEqual(actual[key], value)
                panel.text_into_ui("brightness=23\n")
        for tool in expected:
            with self.subTest(retained_tool=tool):
                self.assertEqual(float(self.saved(self.select(tool))["brightness"]), 23)
        self.assertEqual(self.frame.link_pnl.commands, [])

    def test_picam_legacy_config_and_custom_values_round_trip(self):
        panel = self.select("picamcap")
        panel.text_into_ui(
            "cam_num=picam 0\ncam_opt=picamcap\nx_dim=1600\ny_dim=900\n"
            "b_val=62\ns_val=-17\nc_val=11\ng_val=640\n"
            "image_effect=custom-camera-effect\nexposure_speed=2500000\n"
            "future_camera_option=left=right\n"
        )
        saved = self.saved(panel)
        for key, value in {
            "resolution": "1600x900", "brightness": "62", "saturation": "-17",
            "contrast": "11", "iso": "640", "image_effect": "custom-camera-effect",
            "exposure_speed": "2500000", "future_camera_option": "left=right",
        }.items():
            self.assertEqual(saved[key], value)

    def test_rpicam_config_keeps_fractional_and_custom_values(self):
        panel = self.select("rpicam")
        panel.text_into_ui(
            "Resolution=1234x789\nbrightness=0.375\ncontrast=2.125\n"
            "autofocus-window=0.1,0.2,0.3,0.4\nautofocus-range=macro\n"
            "tuning-file=/home/pi/a=b.json\nfuture_camera_option=enabled\n"
        )
        saved = self.saved(panel)
        self.assertEqual(saved["Resolution"], "1234x789")
        self.assertEqual(float(saved["brightness"]), 0.375)
        self.assertEqual(float(saved["contrast"]), 2.125)
        self.assertEqual(saved["autofocus-window"], "0.1,0.2,0.3,0.4")
        self.assertEqual(saved["autofocus-range"], "macro")
        self.assertEqual(saved["tuning-file"], "/home/pi/a=b.json")
        self.assertEqual(saved["future_camera_option"], "enabled")
        panel.refresh_settings_sizer()
        self.assertEqual(self.saved(panel), saved)

    def test_fswebcam_dynamic_controls_keep_loaded_settings_and_final_option(self):
        panel = self.select("fswebcam")
        self.controls.cam_cb.SetValue("/dev/video2")
        panel.text_into_ui(
            "resolution=800x600\nfs_delay=4\nfs_jpg_q=96\nbrightness=201\n"
            "power_line_frequency=60 Hz\nfuture_device_option=untouched\n"
        )
        panel.get_opt_list(None)
        self.assertIn("focus_absolute", panel.setting_crtl_dict)
        self.assertNotIn("sensor_status", panel.setting_crtl_dict)
        self.assertEqual(float(panel.setting_crtl_dict["focus_absolute"].GetValue()), 17)
        saved = self.saved(panel)
        self.assertEqual(saved["resolution"], "800x600")
        self.assertEqual(saved["fs_delay"], "4")
        self.assertEqual(saved["fs_jpg_q"], "96")
        self.assertEqual(saved["brightness"], "201")
        self.assertEqual(saved["power_line_frequency"].strip(), "60 Hz")
        self.assertEqual(saved["future_device_option"], "untouched")
        child_count = len(panel.GetChildren())
        panel.get_opt_list(None)
        self.assertEqual(len(panel.GetChildren()), child_count)
        self.assertEqual(self.saved(panel), saved)
        self.assertTrue(all("/dev/video2" in command for command in self.frame.link_pnl.commands))

    def test_resolution_refresh_keeps_custom_resolution(self):
        panel = self.select("fswebcam")
        self.controls.cam_cb.SetValue("/dev/video3")
        panel.text_into_ui("resolution=800x600\n")
        panel.get_resolutions_click(None)
        resolution = panel.setting_crtl_dict["resolution"]
        self.assertEqual(resolution.GetValue(), "800x600")
        self.assertIn("640x480", resolution.GetItems())
        self.assertIn("1920x1080", resolution.GetItems())
        resolution.SetValue("")
        self.assertNotIn("resolution", self.saved(panel))

    def test_fswebcam_legacy_extra_values_remain_editable(self):
        panel = self.select("fswebcam")
        extra = '--set "brightness"="200"  --set "contrast"="23" --title "Greenhouse camera"'
        panel.text_into_ui("brightness=100\nfsw_extra=" + extra + "\n")
        self.assertEqual(panel.setting_crtl_dict["brightness"].GetValue(), "200")
        self.assertEqual(self.saved(panel)["fsw_extra"], extra)
        panel.get_opt_list(None)
        panel.setting_crtl_dict["brightness"].SetValue(150)
        saved = self.saved(panel)
        self.assertEqual(saved["brightness"], "150")
        self.assertIn("brightness=150", shlex.split(saved["fsw_extra"]))
        self.assertIn("contrast=23", shlex.split(saved["fsw_extra"]))
        panel.setting_crtl_dict["contrast"].SetValue("")
        saved = self.saved(panel)
        self.assertNotIn("contrast", saved)
        self.assertNotIn('"contrast"', saved["fsw_extra"])
        self.assertIn('--title "Greenhouse camera"', saved["fsw_extra"])

    def test_clearing_a_setting_also_clears_its_legacy_alias(self):
        panel = self.select("picamcap")
        panel.text_into_ui("x_dim=800\ny_dim=600\nb_val=62\ng_val=640\n")
        for key in ("resolution", "brightness", "iso"):
            panel.setting_crtl_dict[key].SetValue("")
        saved = self.saved(panel)
        for key in ("resolution", "brightness", "iso", "x_dim", "y_dim", "b_val", "g_val"):
            self.assertNotIn(key, saved)

    def test_uvc_defaults_legacy_dimensions_and_extra_arguments(self):
        panel = self.select("uvccapture")
        self.assertEqual(self.saved(panel), {})
        panel.text_into_ui(
            "resolution=800x600\nx_dim=1024\nb_val=201\ns_val=63\n"
            "uvc_extra=-t0 --option=a=b\nfuture_device_option=unchanged\n"
        )
        saved = self.saved(panel)
        self.assertEqual(saved["resolution"], "1024x600")
        self.assertEqual(saved["b_val"], "201")
        self.assertEqual(saved["s_val"], "63")
        self.assertEqual(saved["uvc_extra"], "-t0 --option=a=b")
        self.assertEqual(saved["future_device_option"], "unchanged")
        panel.text_into_ui("y_dim=720\n")
        self.assertEqual(self.saved(panel)["resolution"], "100000x720")
        self.assertNotIn("b_val", self.saved(panel))
        panel.setting_crtl_dict["resolution"].SetValue("")
        self.assertNotIn("y_dim", self.saved(panel))

    def test_uvc_capture_result_and_selected_camera_default(self):
        panel = self.select("uvccapture")
        self.controls.cam_cb.SetValue("/dev/video4")
        link = self.frame.link_pnl
        link.responses[
            "/home/pi/Pigrow/scripts/cron/camcap.py caps=/tmp/caps/ set=/tmp/camera.txt"
        ] = ("Capture Finished, Image path : /tmp/caps/photo.jpg\n", "")
        path, output = panel.take_image("/tmp/camera.txt", "/tmp/caps/")
        self.assertEqual(path, "/tmp/caps/photo.jpg")
        self.assertIn("Capture Finished", output)
        link.responses["uvccapture -x100000 -y100000 -v -t0 -d/dev/video4 -o/tmp/default.jpg"] = ("done", "")
        self.assertEqual(panel.take_default("/tmp/default.jpg"), ("/tmp/default.jpg", "uvccapture", "done"))

    def test_libcamera_optional_discovery_preserves_config_and_default_command(self):
        panel = self.select("libcamera")
        before = self.saved(panel)
        link = self.frame.link_pnl
        link.responses["/usr/local/bin/libcamera-still --help 2>&1"] = (
            "--timeout --autofocus-mode --autofocus-window --awbgains", ""
        )
        panel.find_extra_options(None)
        self.assertEqual(self.saved(panel), before)
        self.assertIn("autofocus-window", panel.setting_crtl_dict)
        self.assertNotIn("lens-position", panel.setting_crtl_dict)
        panel.text_into_ui(
            "resolution=1000x700\nbrightness=0.125\ntimeout=5sec\n"
            "lens-position=1.35\nautofocus-mode=manual\nfuture_option=kept\n"
        )
        saved = self.saved(panel)
        self.assertEqual(saved["resolution"], "1000x700")
        self.assertEqual(float(saved["brightness"]), 0.125)
        self.assertEqual(saved["timeout"], "5sec")
        self.assertEqual(saved["lens-position"], "1.35")
        self.assertEqual(saved["future_option"], "kept")
        child_count = len(panel.GetChildren())
        panel.find_extra_options(None)
        self.assertEqual(len(panel.GetChildren()), child_count)
        self.assertEqual(self.saved(panel), saved)
        panel.text_into_ui("resolution=1920x1080\n")
        for optional in ("timeout", "autofocus-mode", "lens-position"):
            self.assertEqual(panel.setting_crtl_dict[optional].GetValue(), "")
            self.assertNotIn(optional, self.saved(panel))

    def test_motion_launcher_config_round_trip(self):
        panel = self.select("motion")
        panel.text_into_ui(
            "config_path=/home/pi/a=b.conf\nlog_path=/var/log/motion test.log\n"
            "log_level=9\nfuture_launcher_option=kept\n"
        )
        saved = self.saved(panel)
        self.assertEqual(saved["config_path"], "/home/pi/a=b.conf")
        self.assertEqual(saved["log_path"], "/var/log/motion test.log")
        self.assertEqual(saved["log_level"], "9")
        self.assertEqual(saved["future_launcher_option"], "kept")
        panel.log_path_tc.SetValue("")
        self.assertNotIn("log_level", self.saved(panel))

    def test_motion_installed_version_status_including_epochs(self):
        panel = self.select("motion")
        link = self.frame.link_pnl
        for installed, candidate, expected in (
            ("1:4.5.1", "1:4.5.1", "current"),
            ("1:4.5.1", "1:4.6.0", "updatable"),
            ("(none)", "1:4.6.0", "none"),
        ):
            with self.subTest(installed=installed, candidate=candidate):
                link.responses["apt-cache policy motion"] = (
                    "motion:\n  Installed: " + installed + "\n  Candidate: " + candidate + "\n", ""
                )
                self.assertEqual(panel.check_installed(), expected)

    def test_capture_sidebar_can_scroll(self):
        self.frame.GetSizer().Detach(self.panel)
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(self.controls, 0, wx.EXPAND)
        layout.Add(self.panel, 1, wx.EXPAND)
        self.frame.SetSizer(layout)
        self.controls.Show()
        self.frame.SetSize((1050, 500))
        self.frame.Layout()
        self.pump()
        self.assertGreater(self.controls.GetVirtualSize().height, self.controls.GetClientSize().height)
        self.controls.Scroll(0, 100000)
        self.pump()
        self.assertGreater(self.controls.GetViewStart()[1], 0)

    def test_large_photo_does_not_stretch_camera_controls(self):
        self.select("rpicam")
        self.panel.show_image_onscreen(str(self.large_image_path), "Large photograph")
        self.pump()
        self.screenshot("camera-controls-large-photo")
        self.assertLessEqual(
            self.panel.settings_body.GetSize().width,
            self.panel.scroll_panel.GetClientSize().width,
        )

    def test_settings_are_compact_left_indented_with_small_right_toggle(self):
        self.select("rpicam")
        toggle = self.panel.settings_toggle_btn
        body = self.panel.settings_body
        self.assertLess(toggle.GetSize().width, 240)
        self.assertLessEqual(abs(toggle.GetRect().right - self.panel.GetClientSize().width), 12)
        self.assertGreaterEqual(body.GetPosition().x, 8)
        self.assertLessEqual(body.GetSize().width, 650)
        self.assertLess(body.GetRect().right, self.panel.scroll_panel.GetClientSize().width - 100)
        self.panel.show_image_onscreen(str(self.large_image_path), "Large photograph")
        self.pump()
        self.assertLessEqual(body.GetSize().width, 650)

    def test_photo_footer_is_fixed_and_clear_tracks_displayed_photos(self):
        self.select("rpicam")
        toolbar = self.panel.photo_toolbar
        self.assertIs(toolbar.GetParent(), self.panel)
        self.assertIs(self.panel.clear_pics_btn.GetParent(), toolbar)
        self.assertIs(self.panel.show_last_btn.GetParent(), toolbar)
        self.assertFalse(self.panel.clear_pics_btn.IsEnabled())
        self.assertFalse(self.panel.scale_to_fit_cb.GetValue())
        self.assertEqual(self.panel.photo_nav_buttons, [])
        self.panel.show_image_onscreen(str(self.image_path), "First photo")
        self.panel.show_image_onscreen(str(self.image_path), "Second photo")
        self.pump()
        self.assertTrue(self.panel.clear_pics_btn.IsEnabled())
        footer_y = toolbar.GetScreenPosition().y
        self.panel.scroll_panel.Scroll(0, 100000)
        self.pump()
        self.assertGreater(self.panel.scroll_panel.GetViewStart()[1], 0)
        self.assertTrue(toolbar.IsShownOnScreen())
        self.assertEqual(toolbar.GetScreenPosition().y, footer_y)
        # A settings hide/restore does not displace the bottom photo actions.
        self.press(self.panel.settings_toggle_btn)
        self.press(self.panel.settings_toggle_btn)
        self.assertEqual(toolbar.GetScreenPosition().y, footer_y)
        self.frame.SetSize((800, 550))
        self.frame.Layout()
        self.pump()
        self.assertTrue(toolbar.IsShownOnScreen())
        self.assertLessEqual(toolbar.GetRect().bottom, self.panel.GetClientSize().height)
        self.press(self.panel.clear_pics_btn)
        self.assertFalse(self.panel.clear_pics_btn.IsEnabled())
        self.assertEqual(self.panel.photo_store.records, [])
        self.assertEqual(self.panel.photo_views, {})
        self.assertEqual(self.panel.photo_nav_buttons, [])
        self.assertEqual(self.panel.picture_sizer.GetItemCount(), 0)

    def test_photo_navigation_uses_first_five_and_oldest_for_last(self):
        self.select("rpicam")
        for number in range(7):
            self.panel.show_image_onscreen(str(self.image_path), "Photo " + str(number + 1))
        self.pump()
        self.assertEqual([button.GetLabel() for button in self.panel.photo_nav_buttons],
                         ["1", "2", "3", "4", "5", "Last"])
        targets = self.panel.photo_store.records[:5] + [self.panel.photo_store.records[-1]]
        for button, target in zip(self.panel.photo_nav_buttons, targets):
            with self.subTest(target=target.label):
                self.assertTrue(button.GetBitmap().IsOk())
                self.press(button)
                view = self.panel.photo_views[target.record_id]
                relative_y = view.panel.GetScreenPosition().y - self.panel.scroll_panel.GetScreenPosition().y
                self.assertLessEqual(abs(relative_y), 15)
        self.assertTrue(self.panel.settings_expanded)
        self.press(self.panel.settings_toggle_btn)
        self.press(self.panel.settings_toggle_btn)
        self.assertFalse(self.panel.settings_expanded)
        self.press(self.panel.photo_nav_buttons[2])
        target = self.panel.photo_store.records[2]
        relative_y = (self.panel.photo_views[target.record_id].panel.GetScreenPosition().y
                      - self.panel.scroll_panel.GetScreenPosition().y)
        self.assertLessEqual(abs(relative_y), 15)

    def test_last_short_photo_scrolls_to_top_and_footer_wraps_at_narrow_width(self):
        path = Path(self.scratch.name) / "small-photo.png"
        Image.new("RGB", (120, 80), "#24546b").save(path)
        for number in range(7):
            self.panel.show_image_onscreen(str(path), "Small photo " + str(number + 1))
        self.pump()
        self.press(self.panel.settings_toggle_btn)
        self.press(self.panel.photo_nav_buttons[-1])
        oldest = self.panel.photo_store.records[-1]
        view = self.panel.photo_views[oldest.record_id]
        relative_y = view.GetScreenPosition().y - self.panel.scroll_panel.GetScreenPosition().y
        self.assertLessEqual(abs(relative_y), 15)
        self.frame.SetSize((350, 650))
        self.frame.Layout()
        self.pump()
        self.pump()
        toolbar = self.panel.photo_toolbar
        self.assertTrue(toolbar.IsShownOnScreen())
        for control in (self.panel.photo_nav_buttons + [self.panel.clear_pics_btn,
                        self.panel.show_last_btn, self.panel.scale_to_fit_cb]):
            with self.subTest(control=control.GetName()):
                self.assertGreaterEqual(control.GetRect().left, 0)
                self.assertLessEqual(control.GetRect().right, toolbar.GetClientSize().width)
                self.assertLessEqual(control.GetRect().bottom, toolbar.GetClientSize().height)

    def test_fit_photos_follow_width_and_restore_original_pixels(self):
        self.panel.show_image_onscreen(str(self.large_image_path), "Large photograph")
        self.pump()
        record = self.panel.photo_store.records[0]
        bitmap = self.panel.photo_views[record.record_id].bitmap
        self.assertEqual(bitmap.GetBitmap().GetSize(), (2400, 1200))
        self.check(self.panel.scale_to_fit_cb, True)
        self.pump()
        fitted = bitmap.GetBitmap().GetSize()
        self.assertLessEqual(fitted.width, self.panel.scroll_panel.GetClientSize().width)
        self.assertGreater(fitted.width, self.panel.scroll_panel.GetClientSize().width * 0.8)
        self.assertAlmostEqual(fitted.width / fitted.height, 2, delta=0.01)
        self.frame.SetSize((800, 600))
        self.frame.Layout()
        self.pump()
        self.pump()
        resized = bitmap.GetBitmap().GetSize()
        self.assertLess(resized.width, fitted.width)
        self.assertLessEqual(resized.width, self.panel.scroll_panel.GetClientSize().width)
        self.assertAlmostEqual(resized.width / resized.height, 2, delta=0.01)
        self.check(self.panel.scale_to_fit_cb, False)
        self.assertEqual(bitmap.GetBitmap().GetSize(), (2400, 1200))
        self.assertEqual(record.image.GetSize(), (2400, 1200))

    def test_clicking_an_overwritten_photo_opens_its_snapshot(self):
        path = Path(self.scratch.name) / "reused-capture.png"
        Image.new("RGB", (120, 80), "#ed2314").save(path)
        self.panel.show_image_onscreen(str(path), "First capture")
        original = self.panel.photo_store.records[0]
        Image.new("RGB", (120, 80), "#1423ed").save(path)
        self.panel.show_image_onscreen(str(path), "Second capture")
        opened = []

        def dialog(*args, **kwargs):
            opened.append((args, kwargs))
            return SimpleNamespace(ShowModal=lambda: wx.ID_OK, Destroy=lambda: None)

        self.frame.shared_data.show_image_dialog = dialog
        bitmap = self.panel.photo_views[original.record_id].bitmap
        event = wx.MouseEvent(wx.wxEVT_LEFT_DOWN)
        event.SetEventObject(bitmap)
        bitmap.GetEventHandler().ProcessEvent(event)
        self.pump()
        self.assertEqual(len(opened), 1)
        args, kwargs = opened[0]
        self.assertTrue(kwargs["original_overwritten"])
        self.assertEqual(kwargs["image"].GetRed(0, 0), 237)
        self.assertEqual(kwargs["image"].GetBlue(0, 0), 20)
        self.panel.show_last_click(None)
        self.assertEqual(len(opened), 2)
        self.assertEqual(opened[-1][1]["image"].GetBlue(0, 0), 237)
        self.panel.clear_pics_click(None)
        self.panel.show_last_click(None)
        self.assertEqual(len(opened), 3)
        self.assertEqual(opened[-1][1]["image"].GetBlue(0, 0), 237)

    def test_open_photo_dialog_title_updates_when_a_capture_reuses_its_filename(self):
        path = Path(self.scratch.name) / "open-capture.png"
        Image.new("RGB", (120, 80), "#ed2314").save(path)
        self.panel.show_image_onscreen(str(path), "First capture")
        record = self.panel.photo_store.records[0]
        panel = self.panel
        observed = []

        class TestDialog(shared_data.show_image_dialog):
            def ShowModal(dialog):
                observed.append(dialog.GetTitle())
                Image.new("RGB", (120, 80), "#1423ed").save(path)
                panel.show_image_onscreen(str(path), "Second capture")
                observed.append(dialog.GetTitle())
                observed.append(dialog.original_image.GetRed(0, 0))
                return wx.ID_OK

        self.frame.shared_data.show_image_dialog = TestDialog
        self.panel.open_photo(record)
        self.assertNotIn("(original overwritten)", observed[0])
        self.assertTrue(observed[1].endswith(" (original overwritten)"))
        self.assertEqual(observed[2], 237)

    def test_autofocus_region_dialog_without_photo_and_with_scaled_photo(self):
        dialog = SetAFROIDialog(self.frame, initial_roi="0.1,0.2,0.3,0.4")
        try:
            dialog.Show()
            self.pump()
            self.assertEqual(parse_roi(dialog.get_roi()), (0.1, 0.2, 0.3, 0.4))
            dialog.set_roi((0, 0, 1, 1))
            self.assertEqual(parse_roi(dialog.get_roi()), (0, 0, 1, 1))
            self.assertTrue(dialog.load_image(str(self.large_image_path)))
            dialog._layout_image()
            left, top, width, height = dialog._image_rect
            available = dialog.image_panel.GetClientSize()
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            self.assertLessEqual(left + width, available.width)
            self.assertLessEqual(top + height, available.height)
            self.assertAlmostEqual(width / height, 2, delta=0.02)
            # Decimal fields can be edited directly and update the selection.
            for field, value in zip(dialog.roi_fields, ("0.2", "0.3", "0.4", "0.5")):
                field.SetValue(value)
            self.assertEqual(dialog._roi, (0.2, 0.3, 0.4, 0.5))
            for bad in ("0,0,0,1", "0.9,0,0.2,1", "nan,0,1,1"):
                with self.subTest(invalid_roi=bad), self.assertRaises(ValueError):
                    parse_roi(bad)
        finally:
            dialog.Destroy()

    def test_region_buttons_are_beside_their_fields(self):
        for tool, keys in (("rpicam", ("roi", "autofocus-window")),
                           ("libcamera", ("roi",)), ("picamcap", ("zoom",))):
            panel = self.select(tool)
            for key in keys:
                with self.subTest(tool=tool, setting=key):
                    control = panel.setting_crtl_dict[key]
                    button = panel.setting_t_dict[key]
                    self.assertEqual(button.GetLabel(), "Set region")
                    self.assertGreater(button.GetPosition().x, control.GetRect().right)
                    button_y = button.GetPosition().y + button.GetSize().height / 2
                    control_y = control.GetPosition().y + control.GetSize().height / 2
                    self.assertLessEqual(abs(button_y - control_y), 2)

    def test_region_cancel_keeps_config_and_accept_updates_only_the_selected_setting(self):
        created = []
        result = [wx.ID_CANCEL]

        def make_dialog(*args, **kwargs):
            created.append((args, kwargs))
            return SimpleNamespace(ShowModal=lambda: result[0],
                                   get_roi=lambda: "0.2,0.3,0.4,0.5", Destroy=lambda: None)

        with patch("panels.image_region.ImageRegionDialog", side_effect=make_dialog):
            for tool, key, value in (("rpicam", "autofocus-window", "0.1,0.2,0.3,0.4"),
                                     ("rpicam", "roi", "0.1,0.2,0.3,0.4"),
                                     ("libcamera", "roi", "0.1,0.2,0.3,0.4"),
                                     ("picamcap", "zoom", "(0.1,0.2,0.3,0.4)")):
                with self.subTest(tool=tool, setting=key):
                    panel = self.select(tool)
                    panel.text_into_ui(key + "=" + value + "\nfuture_camera_option=kept\n")
                    original = self.saved(panel)
                    result[0] = wx.ID_CANCEL
                    self.press(panel.setting_t_dict[key])
                    self.assertEqual(self.saved(panel), original)
                    self.assertEqual(created[-1][0][2], (0.1, 0.2, 0.3, 0.4))
                    expected_kind = "autofocus" if key == "autofocus-window" else "crop"
                    self.assertEqual(created[-1][1]["region_kind"], expected_kind)
                    result[0] = wx.ID_OK
                    self.press(panel.setting_t_dict[key])
                    expected = "(0.2,0.3,0.4,0.5)" if key == "zoom" else "0.2,0.3,0.4,0.5"
                    original[key] = expected
                    self.assertEqual(self.saved(panel), original)

    def test_crop_dialog_maps_a_cropped_memory_reference_to_full_sensor_coordinates(self):
        image = wx.Image(str(self.large_image_path))
        dialog = ImageRegionDialog(
            self.frame, initial_roi=(0.2, 0.1, 0.5, 0.7), region_kind="crop",
            image=image, reference_roi=(0.2, 0.1, 0.5, 0.7),
        )
        try:
            dialog.Show()
            self.pump()
            self.assertEqual(dialog.GetTitle(), "Set crop region")
            dialog._layout_image()
            left, top, width, height = dialog._image_rect
            top_left = dialog._normalized_position(wx.Point(left, top))
            bottom_right = dialog._normalized_position(wx.Point(left + width, top + height))
            self.assertEqual(top_left, (0.2, 0.1))
            self.assertAlmostEqual(bottom_right[0], 0.7)
            self.assertAlmostEqual(bottom_right[1], 0.8)
            self.assertIn("already cropped", dialog.instruction.GetLabel())
            self.assertEqual(dialog.image.GetSize(), (2400, 1200))
        finally:
            dialog.Destroy()

    def test_numeric_edits_apply_without_enter_and_reject_invalid_text(self):
        panel = self.select("rpicam")
        control = panel.setting_crtl_dict["brightness"]
        control.text.SetValue("0.37625")
        self.assertEqual(float(self.saved(panel)["brightness"]), 0.37625)
        for invalid in ("-", "nan", "inf", "1e999", "typo"):
            with self.subTest(invalid=invalid):
                control.text.SetValue(invalid)
                self.assertEqual(float(self.saved(panel)["brightness"]), 0.37625)
                self.assertEqual(control.text.GetValue(), "0.37625")
        # Camera metadata is advisory; valid values from existing configs survive.
        control.SetValue("42.125")
        self.assertEqual(control.GetValue(), 42.125)
        self.assertEqual(control.slider.GetValue(), control.slider.GetMax())
        control.text.SetValue("")
        self.assertNotIn("brightness", self.saved(panel))
        integer = self.select("picamcap").setting_crtl_dict["brightness"]
        integer.text.SetValue("15.5")
        self.assertEqual(integer.GetValue(), 50)
        large_integer = NumericControl(self.frame, "int64_setting", 0, -(2**63), 2**63 - 1)
        large_integer.text.SetValue("9223372036854775807")
        self.assertEqual(large_integer.GetValue(), 9223372036854775807)
        large_integer.Destroy()

    def test_fractional_capture_ranges_replace_only_the_selected_key(self):
        panel = self.select("rpicam")
        panel.text_into_ui("brightness=0\nfuture_brightness=leave this unchanged\n")
        self.controls.range_combo.SetValue("brightness")
        for box, value in zip(
            (self.controls.range_start_tc, self.controls.range_end_tc, self.controls.range_every_tc),
            ("-0.1", "0.1", "0.1"),
        ):
            box.SetValue(value)
        self.assertEqual(self.controls.range_values(panel.setting_crtl_dict["brightness"]), ["-0.1", "0.0", "0.1"])
        panel.take_image = lambda settings_file, outpath: ("/fake/photo.jpg", "saved")
        displayed = []
        self.controls.download_and_show_picture = lambda path, label, **kwargs: displayed.append((path, label))
        self.controls.range_btn_click(None)
        written = self.frame.link_pnl.written_configs
        self.assertEqual(len(written), 3)
        self.assertEqual(len(displayed), 3)
        for (_, text), value in zip(written, ("-0.1", "0.0", "0.1")):
            self.assertEqual(sum(line.startswith("brightness=") for line in text.splitlines()), 1)
            self.assertEqual(config_dict(text)["brightness"], value)
            self.assertEqual(config_dict(text)["future_brightness"], "leave this unchanged")
        self.controls.range_every_tc.SetValue("0")
        with self.assertRaises(ValueError):
            self.controls.range_values(panel.setting_crtl_dict["brightness"])
        self.controls.range_every_tc.SetValue("-0.1")
        with self.assertRaises(ValueError):
            self.controls.range_values(panel.setting_crtl_dict["brightness"])
        integer = self.select("picamcap").setting_crtl_dict["brightness"]
        for box, value in zip(
            (self.controls.range_start_tc, self.controls.range_end_tc, self.controls.range_every_tc),
            ("0.0", "2.0", "1.0"),
        ):
            box.SetValue(value)
        self.assertEqual(self.controls.range_values(integer), ["0", "1", "2"])

    def test_capture_reference_crop_uses_the_settings_taken_with_the_photo(self):
        panel = self.select("rpicam")
        initial_roi = "0.1,0.2,0.3,0.4"
        panel.text_into_ui("roi=" + initial_roi + "\n")
        downloaded = []

        def capture(settings_file, outpath):
            # A later UI edit must not change the coordinate system of a photo
            # captured using the already serialized settings.
            panel.setting_crtl_dict["roi"].SetValue("0,0,1,1")
            return "/fake/photo.jpg", "saved"

        panel.take_image = capture
        self.controls.download_and_show_picture = lambda *args, **kwargs: downloaded.append(kwargs)
        self.controls.take_set_click(None)
        self.assertEqual(downloaded[-1]["crop_region"], (0.1, 0.2, 0.3, 0.4))

        settings_path = "/home/pi/Pigrow/config/saved-camera.txt"
        self.panel.camconf_path_tc.SetValue(settings_path)
        self.frame.link_pnl.responses["cat -- " + settings_path] = (
            "cam_opt=rpicam\n roi = 0.15,0.2,0.3,0.4\n", "")
        self.controls.take_saved_set_click(None)
        self.assertEqual(downloaded[-1]["crop_region"], (0.15, 0.2, 0.3, 0.4))

        panel.setting_crtl_dict["roi"].SetValue(initial_roi)
        self.controls.range_combo.SetValue("brightness")
        for box, value in zip((self.controls.range_start_tc, self.controls.range_end_tc,
                               self.controls.range_every_tc), ("0", "0.2", "0.1")):
            box.SetValue(value)
        downloaded.clear()
        self.controls.range_btn_click(None)
        self.assertEqual([call["crop_region"] for call in downloaded], [(0.1, 0.2, 0.3, 0.4)] * 3)

    def test_resolution_ranges_use_capture_script_dimensions(self):
        panel = self.select("rpicam")
        resolution = panel.setting_crtl_dict["Resolution"]
        original = resolution.GetValue()
        resolution.SetItems(['1920x1080 "Full HD"', '640x480 "VGA"'])
        resolution.SetValue(original)
        self.controls.range_combo.SetValue("Resolution")
        panel.take_image = lambda settings_file, outpath: ("/fake/photo.jpg", "saved")
        self.controls.download_and_show_picture = lambda *args, **kwargs: None
        self.controls.range_btn_click(None)
        self.assertEqual(
            [config_dict(text)["Resolution"] for _, text in self.frame.link_pnl.written_configs],
            ["1920x1080", "640x480"],
        )
        self.assertEqual(resolution.GetValue(), original)

    def test_fswebcam_ranges_update_the_legacy_extra_override(self):
        panel = self.select("fswebcam")
        panel.text_into_ui('brightness=100\nfsw_extra=--set "brightness"="200" --title "Camera"\n')
        panel.get_opt_list(None)
        self.controls.range_combo.SetValue("brightness")
        for box, value in zip(
            (self.controls.range_start_tc, self.controls.range_end_tc, self.controls.range_every_tc),
            ("198", "200", "1"),
        ):
            box.SetValue(value)
        panel.take_image = lambda settings_file, outpath: ("/fake/photo.jpg", "saved")
        self.controls.download_and_show_picture = lambda *args, **kwargs: None
        self.controls.range_btn_click(None)
        self.assertEqual(len(self.frame.link_pnl.written_configs), 3)
        for (_, text), value in zip(self.frame.link_pnl.written_configs, ("198", "199", "200")):
            saved = config_dict(text)
            self.assertEqual(saved["brightness"], value)
            self.assertIn("brightness=" + value, shlex.split(saved["fsw_extra"]))
            self.assertIn('--title "Camera"', saved["fsw_extra"])
        self.assertEqual(panel.setting_crtl_dict["brightness"].GetValue(), 200)

    def test_collapse_and_scrolling_keep_settings_and_access_to_photos(self):
        panel = self.select("rpicam")
        panel.text_into_ui("brightness=0.375\nautofocus-range=macro\n")
        before = self.saved(panel)
        self.panel.camconf_path_tc.SetValue("/home/pi/Pigrow/config/existing.txt")
        self.panel.show_image_onscreen(str(self.image_path), "Test photograph")
        self.pump()
        self.screenshot("camera-controls-expanded")
        scroller = self.panel.scroll_panel
        toggle = self.panel.settings_toggle_btn
        header_y = toggle.GetScreenPosition().y
        scroller.Scroll(0, 100000)
        self.pump()
        self.assertGreater(scroller.GetViewStart()[1], 0)
        self.assertEqual(toggle.GetScreenPosition().y, header_y)
        self.assertTrue(toggle.IsShownOnScreen())
        self.assertTrue(self.panel.settings_body.IsShown())
        self.screenshot("camera-controls-scrolled")
        # The fixed pulldown returns the user to the settings while scrolled away.
        self.press(toggle)
        self.assertTrue(self.panel.settings_body.IsShown())
        self.assertEqual(scroller.GetViewStart()[1], 0)
        # At the settings, the same control folds the entire settings section.
        self.press(toggle)
        self.assertFalse(self.panel.settings_body.IsShown())
        self.screenshot("camera-controls-collapsed")
        self.assertGreater(self.panel.picture_sizer.GetItemCount(), 0)
        scroller.Scroll(0, 100000)
        self.pump()
        self.assertTrue(toggle.IsShownOnScreen())
        self.press(toggle)
        self.assertTrue(self.panel.settings_body.IsShown())
        self.assertEqual(scroller.GetViewStart()[1], 0)
        self.assertEqual(self.saved(panel), before)
        self.assertEqual(self.panel.camconf_path_tc.GetValue(), "/home/pi/Pigrow/config/existing.txt")
        self.panel.clear_pics_click(None)
        self.pump()
        self.assertEqual(self.panel.picture_sizer.GetItemCount(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
