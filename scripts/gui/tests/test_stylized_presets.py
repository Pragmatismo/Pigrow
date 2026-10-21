"""Built-in recipes and atomic custom-preset storage without wx or user config."""

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))

import stylized_presets as presets
from stylized_sets import (MAX_MEMORY_BYTES, default_layer, default_settings,
                           estimate_memory_bytes, validate_settings)


class StylizedPresetTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="stylized-presets-")
        self.root = Path(self.folder.name)
        self.path = self.root / "config" / "presets.json"

    def tearDown(self):
        self.folder.cleanup()

    def write_document(self, value):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(value), encoding="utf-8")

    def test_six_builtins_are_valid_distinct_and_independent(self):
        values = presets.builtin_presets()
        self.assertEqual(set(values), {"Accumulated difference", "Motion ghosts",
                                      "Light painting", "Neon motion", "Changed pixels",
                                      "RGB ghost trails"})
        for settings in values.values():
            self.assertEqual(settings, validate_settings(settings))
            self.assertEqual(settings["max_size"], 1920)
        self.assertEqual(len({json.dumps(settings, sort_keys=True) for settings in values.values()}), 6)
        accumulated = values["Accumulated difference"]
        self.assertEqual(accumulated["base"], "first")
        self.assertEqual(accumulated["layers"][0]["blend"], "add_modulo")
        self.assertEqual(accumulated["layers"][0]["persistence"], "permanent")
        ghosts = values["Motion ghosts"]["layers"][0]
        self.assertEqual((ghosts["trail_frames"], ghosts["decay"], ghosts["opacity"]), (12, .8, .6))
        self.assertEqual(len(values["RGB ghost trails"]["layers"]), 3)
        original = copy.deepcopy(values)
        values["RGB ghost trails"]["layers"][0]["tint"] = "#123456"
        values["Motion ghosts"]["layers"].clear()
        self.assertEqual(presets.builtin_presets(), original)
        self.assertNotEqual(values["RGB ghost trails"]["layers"][0]["tint"],
                            values["RGB ghost trails"]["layers"][1]["tint"])

    def test_builtin_export_size_keeps_all_recipes_inside_engine_memory_budget(self):
        for name, settings in presets.builtin_presets().items():
            with self.subTest(preset=name):
                self.assertEqual(settings["max_size"], 1920)
                self.assertLess(estimate_memory_bytes(settings, (1920, 1080)), MAX_MEMORY_BYTES)
        self.assertEqual(default_settings()["max_size"], 0)
        original_size = default_settings()
        presets.save_preset("Original resolution", original_size, self.path)
        self.assertEqual(presets.load_presets(self.path)["Original resolution"]["max_size"], 0)

    def test_missing_file_returns_defaults_without_creating_directory(self):
        self.assertEqual(presets.load_presets(self.path), presets.builtin_presets())
        self.assertFalse(self.path.parent.exists())

    def test_roundtrip_retains_every_layer_field_and_does_not_mutate_input(self):
        settings = default_settings()
        layer = default_layer()
        layer.update(name="Colour & movement / layer", enabled=False, source="edges",
                     persistence="trail", blend="multiply", opacity=.37, threshold=81,
                     gain=2.25, trail_frames=23, decay=.73, tint="#Aa33BB", invert=True)
        settings.update(base="white", max_size=384, layers=[layer])
        before = copy.deepcopy(settings)
        self.assertIsNone(presets.save_preset("  My colour study / v2!  ", settings, self.path))
        self.assertEqual(settings, before)
        result = presets.load_presets(self.path)
        self.assertEqual(result["My colour study / v2!"], validate_settings(settings))
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(document["version"], 1)
        self.assertEqual(set(document["presets"]), {"My colour study / v2!"})
        self.assertEqual(set(document["presets"]["My colour study / v2!"]["layers"][0]), set(default_layer()))
        self.assertEqual(result["My colour study / v2!"]["layers"][0]["tint"], "#aa33bb")
        result["My colour study / v2!"]["layers"][0]["opacity"] = .99
        self.assertEqual(presets.load_presets(self.path)["My colour study / v2!"]["layers"][0]["opacity"], .37)

    def test_updating_custom_name_preserves_other_presets_and_builtins(self):
        first = presets.builtin_presets()["Motion ghosts"]
        second = presets.builtin_presets()["Neon motion"]
        presets.save_preset("Custom one", first, self.path)
        presets.save_preset("Custom two", second, self.path)
        first["base"] = "black"
        presets.save_preset(" Custom one ", first, self.path)
        loaded = presets.load_presets(self.path)
        self.assertEqual(loaded["Custom one"], first)
        self.assertEqual(loaded["Custom two"], second)
        for name, settings in presets.builtin_presets().items():
            self.assertEqual(loaded[name], settings)

    def test_names_support_unicode_spaces_and_punctuation_but_reject_controls(self):
        for name in ("Café / after rain: 2?", "a" * 80):
            presets.save_preset(name, default_settings(), self.path)
            self.assertIn(name, presets.load_presets(self.path))
        before = self.path.read_bytes()
        for name in (None, 12, "", "   ", "a" * 81, "line\nbreak", "nul\0name", "delete\x7fname", "\ttrim"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    presets.save_preset(name, default_settings(), self.path)
                self.assertEqual(self.path.read_bytes(), before)

    def test_builtin_names_cannot_be_replaced(self):
        for name in presets.builtin_presets():
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "built-in.*different name"):
                    presets.save_preset(" " + name + " ", default_settings(), self.path)
                self.assertFalse(self.path.exists())

    def test_corrupt_json_and_schema_are_explained_and_never_overwritten(self):
        invalid_documents = [
            [], {}, {"version": 2, "presets": {}}, {"version": True, "presets": {}},
            {"version": 1, "presets": [], "other": 1}, {"version": 1, "presets": []},
            {"version": 1, "presets": {"": default_settings()}},
            {"version": 1, "presets": {"x": {"unknown_field": 1}}},
            {"version": 1, "presets": {"x": {"base": "no such base"}}},
            {"version": 1, "presets": {"x": {"layers": [{"gain": 0}]}}},
            {"version": 1, "presets": {"x": {"layers": [dict(default_layer(), opacity=True)]}}},
            {"version": 1, "presets": {"x": {"layers": [dict(default_layer(), opacity=float("nan"))]}}},
            {"version": 1, "presets": {"Accumulated difference": default_settings()}},
            {"version": 1, "presets": {"x": default_settings(), " x ": default_settings()}},
        ]
        for document in invalid_documents:
            with self.subTest(document=document):
                self.write_document(document)
                before = self.path.read_bytes()
                with self.assertRaises(ValueError) as caught:
                    presets.load_presets(self.path)
                self.assertIn(str(self.path), str(caught.exception))
                with self.assertRaises(ValueError):
                    presets.save_preset("New", default_settings(), self.path)
                self.assertEqual(self.path.read_bytes(), before)
        for raw in (b"{not JSON", b"\xff", b'{"version":1,"version":1,"presets":{}}',
                    b'{"version":1,"presets":{"x":{},"x":{}}}'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    presets.load_presets(self.path)
                with self.assertRaises(ValueError):
                    presets.save_preset("New", default_settings(), self.path)
                self.assertEqual(self.path.read_bytes(), raw)

    def test_one_invalid_preset_rejects_the_whole_collection(self):
        self.write_document({"version": 1, "presets": {
            "Valid": default_settings(), "Invalid": {"layers": [{"trail_frames": 101}]}}})
        with self.assertRaisesRegex(ValueError, "Invalid"):
            presets.load_presets(self.path)

    def test_oversized_files_are_bounded_and_never_overwritten(self):
        self.path.parent.mkdir(exist_ok=True)
        data = b" " * (presets.MAX_FILE_BYTES + 1)
        self.path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "1 MiB"):
            presets.load_presets(self.path)
        with self.assertRaises(ValueError):
            presets.save_preset("New", default_settings(), self.path)
        self.assertEqual(self.path.read_bytes(), data)

    def test_custom_count_limit_allows_updating_but_blocks_new_presets(self):
        users = {"Preset {}".format(index): default_settings() for index in range(100)}
        self.write_document({"version": 1, "presets": users})
        presets.save_preset("Preset 0", presets.builtin_presets()["Neon motion"], self.path)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "100 custom"):
            presets.save_preset("Preset 101", default_settings(), self.path)
        self.assertEqual(self.path.read_bytes(), before)
        users["Preset 101"] = default_settings()
        self.write_document({"version": 1, "presets": users})
        with self.assertRaisesRegex(ValueError, "100 custom"):
            presets.load_presets(self.path)

    def test_atomic_replace_failure_preserves_original_and_cleans_temporary(self):
        presets.save_preset("Original", default_settings(), self.path)
        before = self.path.read_bytes()
        original_entries = set(self.path.parent.iterdir())
        with mock.patch.object(presets.os, "replace", side_effect=OSError("disk refused replace")) as replace:
            with self.assertRaisesRegex(OSError, "disk refused replace"):
                presets.save_preset("New", default_settings(), self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(set(self.path.parent.iterdir()), original_entries)
        self.assertEqual(Path(replace.call_args.args[0]).parent, self.path.parent)

    def test_write_failure_is_not_swallowed_and_preserves_existing_file(self):
        presets.save_preset("Original", default_settings(), self.path)
        before = self.path.read_bytes()
        with mock.patch.object(presets.os, "fsync", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                presets.save_preset("New", default_settings(), self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob(".stylized-presets-*")), [])

    def test_invalid_settings_are_rejected_before_any_file_is_written(self):
        with self.assertRaises(ValueError):
            presets.save_preset("Invalid", {"max_size": 1}, self.path)
        self.assertFalse(self.path.parent.exists())

    def test_default_paths_select_platform_config_without_writing_home(self):
        with mock.patch.object(presets.os, "name", "posix"), mock.patch.dict(
                os.environ, {"XDG_CONFIG_HOME": str(self.root / "xdg")}, clear=True):
            self.assertEqual(presets.default_preset_path(),
                             str(self.root / "xdg" / "Pigrow" / "stylized_presets.json"))
        expected = os.path.join(str(self.root), "roaming", "Pigrow", "stylized_presets.json")
        with mock.patch.object(presets.os, "name", "nt"), mock.patch.dict(
                os.environ, {"APPDATA": os.path.join(str(self.root), "roaming")}, clear=True):
            self.assertEqual(presets.default_preset_path(), expected)
        with mock.patch.object(presets.os, "name", "posix"), mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(presets.os.path, "expanduser", return_value=str(self.root)):
            self.assertEqual(presets.default_preset_path(),
                             str(self.root / ".config" / "Pigrow" / "stylized_presets.json"))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_default_path_override_uses_same_storage_api(self):
        with mock.patch.object(presets, "default_preset_path", return_value=str(self.path)):
            self.assertEqual(presets.load_presets(), presets.builtin_presets())
            presets.save_preset("Default location", default_settings())
            self.assertIn("Default location", presets.load_presets())


if __name__ == "__main__":
    unittest.main()
