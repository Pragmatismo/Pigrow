"""Ensure fswebcam launcher settings are not sent as hardware controls."""

import contextlib
import importlib.util
import io
from pathlib import Path
import shlex
import sys
import types
import unittest
from unittest.mock import patch


CAPTURE_SCRIPT = Path(__file__).resolve().parents[2] / 'cron' / 'camcap.py'
spec = importlib.util.spec_from_file_location('fswebcam_capture_under_test', CAPTURE_SCRIPT)
capture = importlib.util.module_from_spec(spec)
with patch.object(sys, 'argv', [str(CAPTURE_SCRIPT)]), patch.object(sys, 'path', list(sys.path)), \
        patch.dict(sys.modules, {'pigrow_defs': types.ModuleType('pigrow_defs')}):
    spec.loader.exec_module(capture)


class FswebcamCaptureCommandTests(unittest.TestCase):
    def command(self, settings):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(capture.time, 'time', return_value=1234567890), \
                patch.object(capture.os, 'system') as run:
            filename = capture.take_with_fswebcam(dict(settings), '/caps/')
        self.assertEqual(filename, 'cap_1234567890.jpg')
        return run.call_args.args[0]

    @staticmethod
    def hardware_options(command):
        arguments = shlex.split(command)
        return [arguments[index + 1] for index, value in enumerate(arguments) if value == '--set']

    def test_launcher_values_keep_their_dedicated_flags(self):
        command = self.command(dict(cam_num='/dev/video2', resolution='1280x720', fs_delay='3',
                                    fs_fskip='8', fs_jpg_q='97', fs_banner='False', brightness='12'))
        self.assertEqual(command, 'fswebcam -r 1280x720 -d v4l2:/dev/video2 -D 3 -S 8 --no-banner'
                                  ' --set "brightness"="12" --jpeg 97 /caps/cap_1234567890.jpg')
        self.assertEqual(self.hardware_options(command), ['brightness=12'])

    def test_legacy_aliases_have_same_effect_as_modern_settings(self):
        legacy = dict(cam_num='/dev/video0', x_dim='800', y_dim='600', s_val='22', c_val='33', g_val='44', b_val='55')
        modern = dict(cam_num='/dev/video0', resolution='800x600', saturation='22', contrast='33', gain='44', brightness='55')
        self.assertEqual(self.command(legacy), self.command(modern))
        self.assertEqual(self.hardware_options(self.command(legacy)),
                         ['saturation=22', 'contrast=33', 'gain=44', 'brightness=55'])

    def test_explicit_modern_values_still_override_legacy_aliases(self):
        command = self.command(dict(cam_num='/dev/video0', x_dim='800', y_dim='600', resolution='640x480',
                                    s_val='1', saturation='10', c_val='2', contrast='20',
                                    g_val='3', gain='30', b_val='4', brightness='40'))
        self.assertIn('fswebcam -r 640x480 ', command)
        self.assertEqual(self.hardware_options(command),
                         ['saturation=10', 'contrast=20', 'gain=30', 'brightness=40'])

    def test_custom_hardware_names_and_extra_settings_are_retained(self):
        command = self.command({'cam_num': '/dev/video0', 'White Balance Temperature': '4500',
                                'focus_absolute': '23', 'custom_future_option': '7',
                                'fsw_extra': '--set "Power Line Frequency"="2"',
                                'uvc_extra': '-m', 'cam_opt': 'fswebcam'})
        self.assertEqual(self.hardware_options(command),
                         ['White Balance Temperature=4500', 'focus_absolute=23',
                          'custom_future_option=7', 'Power Line Frequency=2'])
        self.assertIn(' -r 1920x1080 ', command)
        self.assertIn(' -D 2 -S 5 ', command)
        self.assertIn(' --jpeg 90 ', command)


if __name__ == '__main__':
    unittest.main()
