"""Capture command compatibility checks; no camera or libcamera is required."""

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


CAPTURE_SCRIPT = Path(__file__).resolve().parents[2] / 'cron' / 'libcam_cap.py'
spec = importlib.util.spec_from_file_location('libcam_capture_under_test', CAPTURE_SCRIPT)
capture = importlib.util.module_from_spec(spec)
with patch.object(sys, 'argv', [str(CAPTURE_SCRIPT)]):
    spec.loader.exec_module(capture)


class LibcameraCaptureCommandTests(unittest.TestCase):
    def command(self, **settings):
        values = dict(brightness='0', quality='93.7', resolution='640x480', cam_num='picam 0')
        values.update(settings)
        with contextlib.redirect_stdout(io.StringIO()):
            configured = capture.create_set_string(values)
            with patch.object(capture.time, 'time', return_value=1234567890), patch.object(capture.os, 'system') as run:
                path = capture.take_libcamera(configured, '/caps/')
        return run.call_args.args[0], path

    def test_existing_config_keeps_original_command_and_quality_conversion(self):
        command, path = self.command()
        self.assertEqual(path, '/caps/cap_1234567890.jpg')
        self.assertEqual(command, '/usr/local/bin/libcamera-still -t 5000 -o /caps/cap_1234567890.jpg --autofocus '
                                  ' --brightness "0" --quality "93" --width "640" --height "480"')

    def test_explicit_timeout_replaces_default_only(self):
        command, _ = self.command(timeout='2sec')
        self.assertNotIn('-t 5000', command)
        self.assertIn('--timeout "2sec"', command)
        self.assertIn(' --autofocus ', command)

    def test_explicit_focus_mode_replaces_legacy_autofocus(self):
        command, _ = self.command(**{'autofocus-mode': 'manual', 'lens-position': '1.25'})
        self.assertNotIn(' --autofocus ', command)
        self.assertIn('--autofocus-mode "manual"', command)
        self.assertIn('--lens-position "1.25"', command)
        self.assertIn('-t 5000', command)

    def test_optional_focus_range_retains_legacy_autofocus(self):
        command, _ = self.command(**{'autofocus-range': 'macro', 'autofocus-speed': 'fast',
                                     'autofocus-window': '0.1,0.2,0.3,0.4', 'awbgains': '1.5,1.2'})
        self.assertIn(' --autofocus ', command)
        for expected in ('--autofocus-range "macro"', '--autofocus-speed "fast"',
                         '--autofocus-window "0.1,0.2,0.3,0.4"', '--awbgains "1.5,1.2"'):
            self.assertIn(expected, command)

    def test_unknown_setting_is_still_excluded_by_whitelist(self):
        command, _ = self.command(**{'not-a-camera-option': 'value'})
        self.assertNotIn('not-a-camera-option', command)


if __name__ == '__main__':
    unittest.main()
