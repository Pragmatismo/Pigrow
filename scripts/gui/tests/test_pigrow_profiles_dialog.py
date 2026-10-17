"""Draft editor behavior, runnable without wxPython or a local network."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


GUI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI_DIR))
from pigrow_profiles import new_profile, normalize_profiles


# Load this module separately so GUI tests can continue to use real wxPython.
fake_wx = types.ModuleType("wx")
fake_wx.Dialog = object
fake_wx.ID_OK = 5100
fake_wx.ID_CANCEL = 5101
spec = importlib.util.spec_from_file_location(
    "profile_dialog_draft_tests", GUI_DIR / "panels" / "pigrow_profiles_dialog.py")
editor = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"wx": fake_wx}):
    spec.loader.exec_module(editor)


class Control:
    def __init__(self, value=""):
        self.value = value

    def GetValue(self):
        return self.value

    def ChangeValue(self, value):
        self.value = value

    def Enable(self, enabled):
        self.enabled = enabled

    def SetLabel(self, value):
        self.value = value


def draft_dialog(profiles):
    """Supply controls while exercising the real draft editor handlers."""
    dialog = editor.PigrowProfilesDialog.__new__(editor.PigrowProfilesDialog)
    dialog._profiles = normalize_profiles(profiles)
    dialog.default_username = "pi"
    dialog.default_password = "default secret"
    dialog.ssh_port = 2222
    dialog._selected_profile_id = None
    dialog._refreshing_list = False
    dialog._form_baseline = None
    for name in ("box_name", "address", "username", "password", "update_button",
                 "remove_button", "unlink_button", "info_text"):
        setattr(dialog, name, Control())

    def refresh(selected_id):
        dialog._selected_profile_id = selected_id
        dialog._row_ids = [profile["id"] for profile in dialog._profiles]
        dialog._load_form(dialog._selected_profile())

    dialog._refresh_list = refresh
    dialog.EndModal = lambda result: setattr(dialog, "modal_result", result)
    refresh(dialog._profiles[0]["id"] if dialog._profiles else None)
    return dialog


class ProfileDialogDraftTests(unittest.TestCase):
    def test_selection_keeps_form_edits_without_mutating_supplied_profiles(self):
        first = new_profile("Garden", "192.168.1.2", "grower", "old", False)
        second = new_profile(address="192.168.1.3")
        source = [first, second]
        dialog = draft_dialog(source)
        dialog.password.ChangeValue("new secret")
        dialog.address.ChangeValue("garden.local")
        event = types.SimpleNamespace(GetIndex=lambda: 1)
        dialog.on_select(event)
        self.assertEqual(dialog.get_selected_profile_id(), second["id"])
        updated = dialog.get_profiles()[0]
        self.assertEqual(updated["address"], "garden.local")
        self.assertEqual(updated["password"], "new secret")
        self.assertEqual(first["address"], "192.168.1.2")
        self.assertEqual(first["password"], "old")

    def test_save_normalizes_blank_name_and_preserves_password(self):
        first = new_profile("Garden", "old.local", "pi", "old", False)
        dialog = draft_dialog([first])
        dialog.box_name.ChangeValue("  ")
        dialog.address.ChangeValue(" new.local ")
        dialog.password.ChangeValue("one=two\nthree")
        dialog.on_save(None)
        saved, = dialog.get_profiles()
        self.assertEqual(dialog.modal_result, fake_wx.ID_OK)
        self.assertEqual(saved["box_name"], "unknown pi")
        self.assertEqual(saved["address"], "new.local")
        self.assertTrue(saved["tentative"])
        self.assertEqual(saved["password"], "one=two\nthree")
        self.assertEqual(first["password"], "old")

    def test_unlink_keeps_credentials_and_cancel_discards_all_draft_changes(self):
        source = [new_profile("Garden", "old.local", "grower", "saved", False)]
        snapshot = normalize_profiles(source)
        dialog = draft_dialog(source)
        dialog.username.ChangeValue("new grower")
        dialog.on_unlink(None)
        unlinked, = dialog.get_profiles()
        self.assertEqual(unlinked["address"], "")
        self.assertEqual(unlinked["username"], "new grower")
        self.assertEqual(unlinked["password"], "saved")
        dialog.on_remove(None)
        dialog._stage_discoveries(
            [{"address": "192.168.1.7", "is_pi": True}], [])
        dialog.on_cancel(None)
        self.assertEqual(dialog.modal_result, fake_wx.ID_CANCEL)
        self.assertEqual(source, snapshot)

    def test_saving_first_manual_record_does_not_require_pressing_add(self):
        dialog = draft_dialog([])
        dialog.box_name.ChangeValue("New garden")
        dialog.address.ChangeValue("new.local")
        dialog.username.ChangeValue("grower")
        dialog.on_save(None)
        saved, = dialog.get_profiles()
        self.assertEqual(saved["box_name"], "New garden")
        self.assertEqual(saved["username"], "grower")
        self.assertEqual(dialog.selected_profile_id, saved["id"])

    def test_discoveries_stage_pis_and_selected_candidates_with_unique_ids(self):
        known = new_profile("Garden", "GARDEN.LOCAL.", "grower", "secret", False)
        dialog = draft_dialog([known])
        devices = [
            {"address": "192.168.1.2", "hostname": "garden.local", "is_pi": True},
            {"address": "192.168.1.3", "hostname": "new.local", "is_pi": True},
            {"address": "192.168.1.4", "hostname": "other.local", "is_pi": False},
            {"address": "192.168.1.5", "is_pi": False},
            {"address": "192.168.1.6", "is_pi": True},
        ]
        added = dialog._stage_discoveries(devices, ["new.local", "192.168.1.4"])
        saved = dialog.get_profiles()
        self.assertEqual(len(added), 3)
        self.assertEqual({p["address"] for p in saved},
                         {"GARDEN.LOCAL.", "new.local", "192.168.1.4", "192.168.1.6"})
        self.assertEqual(len({p["id"] for p in saved}), 4)
        for tentative in saved[1:]:
            self.assertEqual(tentative["box_name"], "unknown pi")
            self.assertTrue(tentative["tentative"])
            self.assertEqual(tentative["password"], "default secret")
        self.assertEqual(dialog._stage_discoveries(devices, ["new.local", "192.168.1.4"]), [])

    def test_seek_can_move_selected_device_to_hostname_and_keep_credentials(self):
        old = new_profile("Garden", "old.local", "grower", "saved secret", False)
        dialog = draft_dialog([old])
        dialog._choose_discovered_location = lambda addresses: "garden.local"
        discovery_module = types.ModuleType("panels.pigrow_discovery")

        class Discovery:
            def __init__(self, parent, **kwargs):
                self.options = kwargs

            def ShowModal(self):
                return fake_wx.ID_OK

            def get_devices(self):
                return [{"address": "192.168.2.9", "hostname": "garden.local", "is_pi": True}]

            def get_selected_addresses(self):
                return ["garden.local"]

            def Destroy(self):
                pass

        discovery_module.DiscoverIPDialog = Discovery
        with patch.dict(sys.modules, {"panels.pigrow_discovery": discovery_module}):
            dialog.on_seek(None)
        saved, = dialog.get_profiles()
        self.assertEqual(saved["id"], old["id"])
        self.assertEqual(saved["address"], "garden.local")
        self.assertEqual(saved["username"], "grower")
        self.assertEqual(saved["password"], "saved secret")
        self.assertEqual(old["address"], "old.local")


if __name__ == "__main__":
    unittest.main()
