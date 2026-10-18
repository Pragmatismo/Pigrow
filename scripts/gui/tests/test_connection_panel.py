"""Run with wxPython and a display, e.g. xvfb-run python -m unittest discover.

SSH is simulated; these checks never connect to a network or require a Pi.
"""
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import wx
except ImportError:
    wx = None

if wx is not None:
    from shared_data import shared_data
    from pigrow_profiles import new_profile
    from panels import link_pnl as connection


class FakeSSH:
    def __init__(self):
        self.box_name = 'Garden'
        self.config = ''
        self.failure = None
        self.closed = False
        self.peer = '192.168.1.20'

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, address, **kwargs):
        if self.failure:
            raise self.failure
        self.closed = False
        self.login = (address, kwargs['username'], kwargs['password'])

    def close(self):
        self.closed = True

    def get_transport(self):
        class Sock:
            def getpeername(inner):
                return (self.peer, 22)
        class Transport:
            sock = Sock()
        return Transport()

    def exec_command(self, command):
        if 'pigrow_config.txt' in command:
            out = 'box_name=' + self.box_name + '\n' if self.box_name else ''
            out += self.config
        elif 'firmware' in command:
            out = 'exists\n'
        else:
            out = ''
        return None, io.BytesIO(out.encode()), io.BytesIO(b'')


@unittest.skipIf(wx is None, 'wxPython and a display required')
class ConnectionPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def setUp(self):
        self.previous_cwd = os.getcwd()
        self.folder = tempfile.TemporaryDirectory()
        os.chdir(self.folder.name)
        self.shared = shared_data.__new__(shared_data)
        self.shared.gui_set_dict = {
            'default_address': '192.168.1.20', 'username': 'pi',
            'password': 'legacy', 'ssh_port': '22', 'pigrows': '[]',
        }
        self.shared.button_font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                                          wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.shared.box_name = None
        self.shared.config_dict = {}
        self.shared.frompi_base_path = self.folder.name
        self.shared.remote_pigrow_path = ''
        self.shared.frompi_path = ''
        self.frame = wx.Frame(None)
        self.shared.parent = self.frame
        self.frame.shared_data = self.shared
        self.frame.tell_pnls_connected = lambda: None
        self.ssh = FakeSSH()
        with patch.object(connection.paramiko, 'SSHClient', return_value=self.ssh):
            self.panel = connection.link_pnl(self.frame, self.shared)
        self.frame.link_pnl = self.panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.frame.SetSizerAndFit(sizer)
        self.frame.Show()
        self.app.Yield()

    def tearDown(self):
        self.frame.Destroy()
        self.app.Yield()
        os.chdir(self.previous_cwd)
        self.folder.cleanup()

    def saved(self):
        return self.shared.get_pigrow_profiles()

    def test_compact_layout_selection_unlink_and_toggle(self):
        self.assertFalse(self.panel.quick_controls.IsShown())
        self.assertEqual(self.panel.link_status_text.GetLabel(), 'disconnected')
        unlinked = new_profile('Moved garden', '', 'gardener', 'saved secret', False)
        self.shared.save_pigrow_profiles([unlinked], unlinked['id'])
        self.panel.refresh_profiles(unlinked['id'])
        self.panel.select_pigrow(None)
        self.assertTrue(self.panel.quick_controls.IsShown())
        self.assertEqual(self.panel.cb_ip.GetValue(), '')
        self.assertEqual(self.panel.tb_user.GetValue(), 'gardener')
        self.assertEqual(self.panel.tb_pass.GetValue(), 'saved secret')
        self.panel.toggle_quick_controls(None)
        self.assertFalse(self.panel.quick_controls.IsShown())
        self.assertTrue(self.panel.tb_pass.GetWindowStyle() & wx.TE_PASSWORD)

    def test_success_saves_edited_credentials_and_updates_dropdown(self):
        tentative = new_profile(address='192.168.1.20', password='old')
        self.shared.save_pigrow_profiles([tentative], tentative['id'])
        self.panel.refresh_profiles(tentative['id'])
        self.panel.tb_user.ChangeValue('grower')
        self.panel.tb_pass.ChangeValue('secret=one\nsecond')
        self.panel.link_with_pi_btn_click(None)
        self.assertTrue(self.panel.connected)
        self.assertEqual(self.panel.link_status_text.GetLabel(), 'connected')
        self.assertEqual(self.panel.link_with_pi_btn.GetLabel(), 'Disconnect')
        self.assertEqual(self.panel.pigrow_choice.GetStringSelection(), 'Garden')
        profile, = self.saved()
        self.assertEqual(profile['id'], tentative['id'])
        self.assertEqual(profile['username'], 'grower')
        self.assertEqual(profile['password'], 'secret=one\nsecond')
        self.assertFalse(profile['tentative'])
        self.assertFalse(self.panel.pigrow_choice.IsEnabled())
        self.panel.link_with_pi_btn_click(None)
        self.assertFalse(self.panel.connected)
        self.assertTrue(self.panel.pigrow_choice.IsEnabled())
        self.assertEqual(self.panel.link_status_text.GetLabel(), 'disconnected')

    def test_failed_login_does_not_save_edits(self):
        old = new_profile('Garden', '192.168.1.20', 'grower', 'old', False)
        self.shared.save_pigrow_profiles([old], old['id'])
        self.panel.refresh_profiles(old['id'])
        self.panel.tb_pass.ChangeValue('wrong')
        self.ssh.failure = RuntimeError('Authentication failed')
        self.panel.link_with_pi_btn_click(None)
        self.assertFalse(self.panel.connected)
        self.assertIn('Authentication failed', ' '.join(self.panel.link_status_text.GetLabel().split()))
        self.assertEqual(tuple(self.panel.link_status_text.GetForegroundColour())[:3], (0, 0, 139))
        self.assertEqual(self.saved()[0]['password'], 'old')

    def test_remote_config_is_loaded_before_panels_receive_connection(self):
        self.ssh.config = 'gui_datawall=timelapse_detailed\n'
        observed = []
        self.frame.tell_pnls_connected = lambda: observed.append(dict(self.shared.config_dict))
        self.panel.link_with_pi_btn_click(None)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]['gui_datawall'], 'timelapse_detailed')
        self.assertEqual(observed[0]['box_name'], 'Garden')

    def test_new_connection_does_not_reuse_previous_pigrow_datawall(self):
        self.shared.config_dict = {'box_name': 'Previous garden', 'gui_datawall': 'previous_wall'}
        observed = []
        self.frame.tell_pnls_connected = lambda: observed.append(dict(self.shared.config_dict))
        self.panel.link_with_pi_btn_click(None)
        self.assertEqual(observed, [{'box_name': 'Garden'}])

    def test_unknown_ssh_connection_promotes_on_later_name_detection(self):
        self.ssh.box_name = ''
        self.panel.link_with_pi_btn_click(None)
        profile, = self.saved()
        self.assertEqual(profile['box_name'], 'unknown pi')
        self.assertTrue(profile['tentative'])
        self.assertEqual(self.panel.link_status_text.GetLabel(), 'connected')
        self.ssh.box_name = 'Named after installation'
        self.panel.get_box_name()
        updated, = self.saved()
        self.assertEqual(updated['id'], profile['id'])
        self.assertEqual(updated['box_name'], self.ssh.box_name)
        self.assertEqual(self.panel.pigrow_choice.GetStringSelection(), self.ssh.box_name)

    def test_hostname_connection_merges_tentative_ip_sighting(self):
        unknown = new_profile(address=self.ssh.peer)
        self.shared.save_pigrow_profiles([unknown])
        self.panel.refresh_profiles(None)
        self.panel.cb_ip.SetValue('garden.local')
        self.panel.link_with_pi_btn_click(None)
        saved, = self.saved()
        self.assertEqual(saved['id'], unknown['id'])
        self.assertEqual(saved['box_name'], 'Garden')
        self.assertEqual(saved['address'], 'garden.local')

    def test_device_editor_cancel_isolated_and_save_keeps_form_edits(self):
        original = new_profile('Garden', 'old.local', 'grower', 'saved', False)
        for outcome in (wx.ID_CANCEL, wx.ID_OK):
            with self.subTest(outcome=outcome):
                dialog = connection.PigrowProfilesDialog(self.panel, [original])
                self.assertTrue(dialog.password.GetWindowStyle() & wx.TE_PASSWORD)
                dialog.address.ChangeValue('new.local')
                dialog.password.ChangeValue('edited')
                handler = dialog.on_save if outcome == wx.ID_OK else dialog.on_cancel
                wx.CallAfter(handler, None)
                self.assertEqual(dialog.ShowModal(), outcome)
                self.assertEqual(original['address'], 'old.local')
                if outcome == wx.ID_OK:
                    profile, = dialog.get_profiles()
                    self.assertEqual(profile['address'], 'new.local')
                    self.assertEqual(profile['password'], 'edited')
                dialog.Destroy()
                self.app.Yield()

    def test_discovery_dialog_keeps_results_and_selects_hostnames(self):
        from panels import pigrow_discovery as discovery
        devices = [dict(address='192.168.1.20', hostname='garden.local',
                        is_pi=True, evidence='Raspberry Pi MAC')]
        with patch.object(discovery, 'local_default_targets', return_value=['192.168.1.0/24']):
            dialog = discovery.DiscoverIPDialog(self.panel)
        dialog._queue.put(('done', devices))
        dialog._poll(None)
        self.assertEqual(dialog.get_devices(), devices)
        self.assertEqual(dialog.results.GetItemCount(), 2)
        self.assertFalse(dialog.IsModal())
        dialog.results.Select(1)
        self.assertEqual(dialog.get_selected_addresses(), ['garden.local'])
        dialog.timer.Stop()
        dialog.Destroy()
        self.app.Yield()

    def test_peer_ip_rename_choices_and_idempotent_ignore(self):
        for action in ('remove', 'unlink', 'ignore'):
            with self.subTest(action=action):
                if self.panel.connected:
                    self.panel.link_with_pi_btn_click(None)
                old = new_profile('Old garden', self.ssh.peer, 'old user', 'old pass', False)
                self.shared.save_pigrow_profiles([old], old['id'])
                self.panel.refresh_profiles(old['id'])
                self.panel.cb_ip.SetValue('garden.local')
                with patch.object(connection, 'AddressConflictDialog') as dialog:
                    dialog.return_value.action = action
                    self.panel.link_with_pi_btn_click(None)
                    self.panel.get_box_name()
                    self.panel.sync_connected_profile('Garden')
                    self.assertEqual(dialog.call_count, 1)
                profiles = self.saved()
                older = next((p for p in profiles if p['id'] == old['id']), None)
                if action == 'remove':
                    self.assertIsNone(older)
                else:
                    self.assertEqual(older['address'], '' if action == 'unlink' else self.ssh.peer)
                    self.assertEqual(older['password'], 'old pass')
                current = next(p for p in profiles if p['box_name'] == 'Garden')
                self.assertEqual(current['address'], 'garden.local')


if __name__ == '__main__':
    unittest.main()
