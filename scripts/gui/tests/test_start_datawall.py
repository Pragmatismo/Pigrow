"""Startup preset precedence and per-Pigrow/global selection using real wx controls."""

import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))
try:
    import wx
except ImportError:
    wx = None

if wx is not None:
    from panels import start_pnl


@unittest.skipIf(wx is None, 'wxPython and a display required')
class StartDatawallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def setUp(self):
        scratch = GUI.parents[1] / 'work'
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix='start-datawall-', dir=scratch)
        self.previous_cwd = os.getcwd()
        os.chdir(self.folder.name)
        presets = Path('datawall_presets')
        presets.mkdir()
        for name in ('device_wall', 'global_wall', 'new_wall'):
            (presets / ('datawall_' + name + '.txt')).write_text(
                'module=start_selection_fixture\ninfo_read=' + name + '\n')
        self.shared = SimpleNamespace(
            box_name='Garden', config_dict={}, remote_pigrow_path='/home/grower/Pigrow/',
            gui_set_dict={'default_datawall': 'global_wall', 'start_datawall': 'True'},
            save_gui_settings=Mock(), update_pigrow_config_file_on_pi=Mock())
        self.frame = wx.Frame(None)
        self.frame.shared_data = self.shared
        self.import_data = Mock(return_value={'info': {}, 'images': {}})
        self.frame.dict_C_pnl = {'datawall_pnl': SimpleNamespace(create_datawall_data=self.import_data)}
        self.display = SimpleNamespace(display_image=None, Refresh=Mock(), Update=Mock())
        self.frame.dict_I_pnl = {'start_pnl': self.display}
        self.panel = start_pnl.ctrl_pnl(self.frame)

    def tearDown(self):
        self.frame.Destroy()
        self.app.ProcessPendingEvents()
        os.chdir(self.previous_cwd)
        self.folder.cleanup()

    def render_startup(self):
        renderer = SimpleNamespace(make_datawall=Mock(return_value='rendered.png'))
        with patch.object(start_pnl.importlib, 'import_module', return_value=renderer):
            self.panel.connect_to_pigrow()
        self.assertEqual(self.display.display_image, 'rendered.png')
        renderer.make_datawall.assert_called_once()
        return self.import_data.call_args.args[0]

    def dialog(self):
        dialog = start_pnl.DatawallPresetDialog(self.panel, self.shared)
        self.addCleanup(dialog.Destroy)
        return dialog

    def test_first_startup_render_prefers_pigrow_setting_over_global_default(self):
        self.shared.config_dict['gui_datawall'] = 'device_wall'
        self.assertIn('info_read=device_wall', self.render_startup())
        self.assertEqual(self.shared.gui_set_dict['default_datawall'], 'global_wall')

    def test_startup_falls_back_only_when_pigrow_setting_is_empty(self):
        for value in (None, '', '   '):
            with self.subTest(value=value):
                self.shared.config_dict = {} if value is None else {'gui_datawall': value}
                self.assertIn('info_read=global_wall', self.render_startup())

    def test_dialog_uses_same_pigrow_precedence_and_empty_setting_fallback(self):
        for value, expected in (('device_wall', 'device_wall'), ('', 'global_wall'),
                                ('   ', 'global_wall'), (None, 'global_wall')):
            with self.subTest(value=value):
                self.shared.config_dict = {} if value is None else {'gui_datawall': value}
                dialog = self.dialog()
                self.assertEqual(dialog.choicePreset.GetStringSelection(), expected)
                self.assertFalse(dialog.cbSetAll.GetValue())

    def test_selecting_pigrow_preset_leaves_global_default_unchanged(self):
        dialog = self.dialog()
        dialog.choicePreset.SetStringSelection('new_wall')
        with patch.object(dialog, 'EndModal') as end_modal:
            dialog.onOk(None)
        end_modal.assert_called_once_with(wx.ID_OK)
        self.assertEqual(self.shared.config_dict['gui_datawall'], 'new_wall')
        self.assertEqual(self.shared.gui_set_dict['default_datawall'], 'global_wall')
        self.shared.save_gui_settings.assert_not_called()
        self.shared.update_pigrow_config_file_on_pi.assert_called_once()
        self.assertFalse(self.dialog().cbSetAll.GetValue())

    def test_global_default_changes_only_when_checkbox_is_selected(self):
        dialog = self.dialog()
        dialog.choicePreset.SetStringSelection('new_wall')
        dialog.cbSetAll.SetValue(True)
        with patch.object(dialog, 'EndModal'):
            dialog.onOk(None)
        self.assertEqual(self.shared.config_dict['gui_datawall'], 'new_wall')
        self.assertEqual(self.shared.gui_set_dict['default_datawall'], 'new_wall')
        self.shared.save_gui_settings.assert_called_once()
        self.shared.update_pigrow_config_file_on_pi.assert_called_once()
        self.assertFalse(self.dialog().cbSetAll.GetValue())

    def test_cancelling_selection_preserves_both_settings(self):
        self.shared.config_dict['gui_datawall'] = 'device_wall'
        dialog = self.dialog()
        dialog.choicePreset.SetStringSelection('new_wall')
        dialog.cbSetAll.SetValue(True)
        with patch.object(dialog, 'EndModal') as end_modal:
            dialog.onCancel(None)
        end_modal.assert_called_once_with(wx.ID_CANCEL)
        self.assertEqual(self.shared.config_dict['gui_datawall'], 'device_wall')
        self.assertEqual(self.shared.gui_set_dict['default_datawall'], 'global_wall')
        self.shared.save_gui_settings.assert_not_called()
        self.shared.update_pigrow_config_file_on_pi.assert_not_called()


if __name__ == '__main__':
    unittest.main()
