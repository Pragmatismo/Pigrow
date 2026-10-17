"""Profile lifecycle and credential persistence, runnable without wxPython."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


GUI_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI_PATH))

from pigrow_profiles import (find_address_conflicts, load_profiles, new_profile,
                             normalize_profiles, normalized_address,
                             record_connection, serialize_profiles)


def settings_module_without_gui():
    """Load real settings methods while leaving GUI widgets unconstructed."""
    wx = types.ModuleType("wx")
    wx.ART_MISSING_IMAGE = 0
    wx.Dialog = object
    wx.lib = types.ModuleType("wx.lib")
    wx.lib.scrolledpanel = types.ModuleType("wx.lib.scrolledpanel")
    spec = importlib.util.spec_from_file_location(
        "_profile_settings_under_test", GUI_PATH / "shared_data.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
        "wx": wx, "wx.lib": wx.lib,
        "wx.lib.scrolledpanel": wx.lib.scrolledpanel,
    }):
        spec.loader.exec_module(module)
    return module


SETTINGS = settings_module_without_gui()


class ProfileLifecycleTests(unittest.TestCase):
    def test_legacy_migrates_only_when_no_saved_list(self):
        legacy = {"default_address": "192.168.1.42", "username": "grower",
                  "password": "a=b"}
        profiles = load_profiles(legacy)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["box_name"], "unknown pi")
        self.assertTrue(profiles[0]["tentative"])
        self.assertEqual(profiles[0]["username"], "grower")
        self.assertEqual(profiles[0]["password"], "a=b")
        for saved in ("[]", "invalid JSON"):
            self.assertEqual(load_profiles(dict(legacy, pigrows=saved)), [])

    def test_unknown_device_gets_confirmed_name_without_changing_id(self):
        unknown = new_profile(address="192.168.1.42")
        profiles, selected_id = record_connection(
            [unknown], "propagator", "192.168.1.42", "grower", "secret",
            selected_id=unknown["id"])
        self.assertEqual(selected_id, unknown["id"])
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["box_name"], "propagator")
        self.assertFalse(profiles[0]["tentative"])
        self.assertEqual(unknown["box_name"], "unknown pi")

    def test_moved_named_device_merges_tentative_location(self):
        known = new_profile("propagator", "192.168.1.42", "grower", "old",
                            tentative=False)
        sighting = new_profile(address="192.168.2.42")
        profiles, selected_id = record_connection(
            [known, sighting], "propagator", "192.168.2.42", "newuser", "new",
            selected_id=sighting["id"])
        self.assertEqual(selected_id, known["id"])
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["address"], "192.168.2.42")
        self.assertEqual(profiles[0]["username"], "newuser")
        self.assertEqual(profiles[0]["password"], "new")

    def test_confirmed_name_merges_manual_tentative_name(self):
        manual = new_profile("propagator", "old.local")
        sighting = new_profile(address="192.168.2.42")
        profiles, selected_id = record_connection(
            [manual, sighting], "propagator", "192.168.2.42", "pi", "new",
            selected_id=sighting["id"])
        self.assertEqual(selected_id, manual["id"])
        self.assertEqual(len(profiles), 1)
        self.assertFalse(profiles[0]["tentative"])

    def test_rename_remove_unlink_and_ignore_preserve_expected_credentials(self):
        for action in ("remove", "unlink", "ignore"):
            with self.subTest(action=action):
                older = new_profile("oldname", "grow.local", "olduser", "oldpass",
                                    tentative=False)
                original = copy.deepcopy(older)
                conflicts = find_address_conflicts([older], "GROW.local.", "newname")
                self.assertEqual([item["id"] for item in conflicts], [older["id"]])
                profiles, selected_id = record_connection(
                    [older], "newname", "GROW.local.", "newuser", "newpass",
                    selected_id=older["id"], conflict_actions={older["id"]: action})
                connected = next(item for item in profiles if item["id"] == selected_id)
                self.assertEqual(connected["box_name"], "newname")
                self.assertEqual(connected["password"], "newpass")
                remaining = next((item for item in profiles
                                  if item["id"] == older["id"]), None)
                if action == "remove":
                    self.assertIsNone(remaining)
                else:
                    self.assertEqual(remaining["address"], "" if action == "unlink" else "grow.local")
                    self.assertEqual(remaining["username"], "olduser")
                    self.assertEqual(remaining["password"], "oldpass")
                self.assertEqual(older, original)

    def test_hostname_peer_conflict_honours_explicit_choices(self):
        for action in ("remove", "unlink"):
            with self.subTest(action=action):
                older = new_profile("oldname", "192.168.1.42", "olduser", "oldpass",
                                    tentative=False)
                profiles, selected_id = record_connection(
                    [older], "newname", "grow.local", "pi", "newpass",
                    conflict_actions={older["id"]: action})
                self.assertEqual(next(item for item in profiles
                                      if item["id"] == selected_id)["address"], "grow.local")
                if action == "remove":
                    self.assertEqual(len(profiles), 1)
                else:
                    self.assertEqual(profiles[0]["address"], "")
                    self.assertEqual(profiles[0]["password"], "oldpass")

    def test_rename_defaults_to_preserving_older_record(self):
        older = new_profile("oldname", "192.168.1.42", tentative=False)
        profiles, selected_id = record_connection(
            [older], "newname", "192.168.1.42", "pi", "new",
            selected_id=older["id"])
        self.assertEqual(len(profiles), 2)
        self.assertNotEqual(selected_id, older["id"])
        self.assertEqual(profiles[0], older)

    def test_no_confirmed_name_does_not_claim_a_rename(self):
        older = new_profile("oldname", "192.168.1.42", tentative=False)
        self.assertEqual(find_address_conflicts([older], older["address"], None), [])
        profiles, selected_id = record_connection(
            [], None, "192.168.1.42", "pi", "secret")
        self.assertEqual(profiles[0]["id"], selected_id)
        self.assertEqual(profiles[0]["box_name"], "unknown pi")
        self.assertTrue(profiles[0]["tentative"])

    def test_normalize_repairs_identifiers_without_merging_unknown_devices(self):
        first = new_profile(address="192.168.1.42")
        second = dict(first, address="192.168.1.43")
        profiles = normalize_profiles([first, second, "invalid"])
        self.assertEqual(len(profiles), 2)
        self.assertNotEqual(profiles[0]["id"], profiles[1]["id"])
        self.assertEqual(normalized_address(" GROW.local. "), "grow.local")


class ProfilePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.previous_directory = os.getcwd()
        os.chdir(self.temporary_directory.name)
        self.shared = SETTINGS.shared_data.__new__(SETTINGS.shared_data)
        self.shared.gui_set_dict = {}

    def tearDown(self):
        os.chdir(self.previous_directory)
        self.temporary_directory.cleanup()

    def test_credentials_round_trip_without_creating_settings(self):
        password = '="quoted"\\path\nssh_port=9999\r\n雪\u2028end'
        profile = new_profile("grow=雪", "grow.local", "a=b", password,
                              tentative=False)
        self.shared.gui_set_dict = {"ssh_port": "22", "password": password,
                                    "marker": "@pigrow-json-string:\"literal\""}
        self.shared.save_pigrow_profiles([profile], profile["id"])
        text = Path("gui_settings.txt").read_text(encoding="utf-8")
        self.assertEqual(len(text.splitlines()), 5)
        restored = SETTINGS.shared_data.__new__(SETTINGS.shared_data)
        restored.gui_set_dict = {}
        restored.load_gui_settings()
        self.assertEqual(restored.gui_set_dict["ssh_port"], "22")
        self.assertEqual(restored.gui_set_dict["password"], password)
        self.assertEqual(restored.gui_set_dict["marker"], self.shared.gui_set_dict["marker"])
        self.assertEqual(restored.gui_set_dict["selected_pigrow"], profile["id"])
        self.assertEqual(restored.get_pigrow_profiles(), [profile])
        self.assertEqual(json.loads(restored.gui_set_dict["pigrows"]), [profile])
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(Path("gui_settings.txt").stat().st_mode), 0o600)

    def test_atomic_replace_failure_keeps_previous_settings(self):
        profile = new_profile(address="192.168.1.42", password="original")
        self.shared.save_pigrow_profiles([profile], profile["id"])
        previous = Path("gui_settings.txt").read_bytes()
        profile["password"] = "updated"
        with patch.object(SETTINGS.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                self.shared.save_pigrow_profiles([profile], profile["id"])
        self.assertEqual(Path("gui_settings.txt").read_bytes(), previous)
        self.assertEqual(list(Path(".").iterdir()), [Path("gui_settings.txt")])
        self.assertEqual(self.shared.get_pigrow_profiles()[0]["password"], "original")

    def test_migration_has_stable_ids_and_empty_list_stays_empty(self):
        self.shared.gui_set_dict = {"default_address": "192.168.1.42",
                                    "username": "pi", "password": "legacy"}
        first = self.shared.get_pigrow_profiles()
        self.assertEqual(self.shared.get_pigrow_profiles(), first)
        self.shared.save_pigrow_profiles([], first[0]["id"])
        self.assertEqual(self.shared.get_pigrow_profiles(), [])
        self.assertEqual(self.shared.gui_set_dict["selected_pigrow"], "")
        self.shared.load_gui_settings()
        self.assertEqual(self.shared.get_pigrow_profiles(), [])

    def test_json_special_characters_are_preserved(self):
        profile = new_profile("雪", "grow.local", "a=b", '"\\\n\u2028')
        self.assertEqual(load_profiles({"pigrows": serialize_profiles([profile])}), [profile])

    def test_legacy_local_encoding_is_read_before_utf8_save(self):
        Path("gui_settings.txt").write_bytes(b"default_address=grow.local\npassword=caf\xe9\n")
        with patch.object(SETTINGS.locale, "getpreferredencoding", return_value="cp1252"):
            self.shared.load_gui_settings()
        profile = self.shared.get_pigrow_profiles()[0]
        self.assertEqual(profile["password"], "café")
        self.shared.save_pigrow_profiles([profile], profile["id"])
        Path("gui_settings.txt").read_bytes().decode("utf-8")

    def test_remote_settings_syncs_only_confirmed_nonempty_name(self):
        for output, error, expected in (
                ("box_name=new-name\n", "", "new-name"),
                ("box_name=new-name\n", "read failed", None),
                ("box_name=  \n", "", None),
                ("camera=enabled\n", "", None)):
            with self.subTest(output=output, error=error):
                link = types.SimpleNamespace(
                    run_on_pi=Mock(return_value=(output, error)),
                    sync_connected_profile=Mock())
                self.shared.parent = types.SimpleNamespace(link_pnl=link)
                self.shared.remote_pigrow_path = "/home/pi/Pigrow/"
                self.shared.config_dict = {}
                self.shared.read_pigrow_settings_file()
                if expected:
                    link.sync_connected_profile.assert_called_once_with(expected)
                else:
                    link.sync_connected_profile.assert_not_called()


if __name__ == "__main__":
    unittest.main()
