"""Camera photo snapshots and image dialogs, using wx without a Pi."""

import os
from pathlib import Path
import sys
import tempfile
import unittest

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))

import wx
from PIL import Image

from panels.camera_photos import PhotoStore
from shared_data import shared_data


class CameraPhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(False)

    def setUp(self):
        scratch = GUI.parents[1] / "work"
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix="camera-photos-", dir=scratch)
        self.path = Path(self.folder.name) / "capture.png"
        self.write_photo("#ed2314")
        self.store = PhotoStore()

    def tearDown(self):
        self.store.clear()
        self.folder.cleanup()
        self.app.ProcessPendingEvents()
        self.app.Yield(True)

    def write_photo(self, color):
        Image.new("RGB", (240, 120), color).save(self.path)

    def assert_red(self, image):
        self.assertEqual((image.GetRed(0, 0), image.GetGreen(0, 0), image.GetBlue(0, 0)),
                         (237, 35, 20))

    def test_path_reuse_keeps_each_capture_and_stable_identity(self):
        first = self.store.add(str(self.path), "First capture")
        self.write_photo("#1423ed")
        second = self.store.add(str(self.path), "Second capture")
        self.assertIs(self.store.get(first.record_id), first)
        self.assertIs(self.store.get(second.record_id), second)
        self.assertNotEqual(first.record_id, second.record_id)
        self.assertEqual(self.store.records, [second, first])
        self.assert_red(first.image)
        self.assertEqual(second.image.GetBlue(0, 0), 237)
        self.assertTrue(first.original_overwritten)
        self.assertFalse(second.original_overwritten)
        # A caller can edit the returned copy without corrupting later viewers.
        image = first.image
        image.SetRGB(wx.Rect(0, 0, 240, 120), 0, 0, 0)
        self.assert_red(first.image)

    def test_external_overwrite_and_deleted_original_use_snapshot(self):
        first = self.store.add(str(self.path), "Capture")
        self.assertEqual(self.store.check_sources(), [])
        self.write_photo("#1423ed")
        self.assertIn(first, self.store.check_sources(str(self.path)))
        self.assertTrue(first.original_overwritten)
        self.assert_red(first.image)
        second = self.store.add(str(self.path), "Replacement")
        self.path.unlink()
        self.assertEqual(self.store.check_sources(), [])
        self.assertFalse(second.original_overwritten)
        self.assertEqual(second.image.GetBlue(0, 0), 237)

    def test_before_overwrite_marking_is_idempotent_and_preserves_pixels(self):
        record = self.store.add(str(self.path), "Capture")
        self.assertIn(record, self.store.mark_overwritten(str(self.path)))
        self.assertEqual(self.store.mark_overwritten(str(self.path)), [])
        self.write_photo("#1423ed")
        self.assert_red(record.image)

    def test_source_check_detects_replacement_even_when_size_and_mtime_match(self):
        path = Path(self.folder.name) / "same-size.bmp"
        Image.new("RGB", (240, 120), "#ed2314").save(path)
        record = self.store.add(str(path), "Capture")
        before = path.stat()
        Image.new("RGB", (240, 120), "#1423ed").save(path)
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertEqual(path.stat().st_size, before.st_size)
        self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertIn(record, self.store.check_sources())
        self.assert_red(record.image)

    def test_scaled_bitmap_and_thumbnail_keep_aspect_ratio(self):
        record = self.store.add(str(self.path), "Capture")
        original = record.get_bitmap()
        self.assertEqual(original.GetSize(), (240, 120))
        scaled = record.get_bitmap(width=60)
        self.assertEqual(scaled.GetSize(), (60, 30))
        thumbnail = record.thumbnail(width=40, height=30)
        self.assertLessEqual(thumbnail.GetWidth(), 40)
        self.assertLessEqual(thumbnail.GetHeight(), 30)
        self.assertAlmostEqual(thumbnail.GetWidth() / thumbnail.GetHeight(), 2, delta=0.05)
        self.assertEqual(record.get_bitmap().GetSize(), (240, 120))

    def test_clear_releases_lookup_and_does_not_reuse_record_ids(self):
        first = self.store.add(str(self.path), "Capture")
        original_id = first.record_id
        self.store.clear()
        self.assertEqual(self.store.records, [])
        self.assertIsNone(self.store.get(original_id))
        next_record = self.store.add(str(self.path), "Next capture")
        self.assertNotEqual(next_record.record_id, original_id)
        self.assertEqual(self.store.records, [next_record])
        # Show last photo may retain a single snapshot after clearing the list.
        self.write_photo("#1423ed")
        self.assertTrue(first.check_source())
        self.assertFalse(first.check_source())
        self.assert_red(first.image)

    def test_dialog_snapshot_and_overwritten_title_survive_zoom_and_resize(self):
        record = self.store.add(str(self.path), "Capture")
        self.path.unlink()
        dialog = shared_data.show_image_dialog(
            None, str(self.path), "Capture", image=record.image,
            original_overwritten=True,
        )
        try:
            dialog.Show()
            self.app.Yield(True)
            self.assert_red(dialog.original_image)
            self.assertRegex(dialog.GetTitle(), r"Zoom:.* \(original overwritten\)$")
            dialog.zoom_factor *= 1.1
            dialog.update_image()
            dialog.update_title()
            zoomed_title = dialog.GetTitle()
            self.assertTrue(zoomed_title.endswith(" (original overwritten)"))
            dialog.SetSize((400, 300))
            self.app.Yield(True)
            self.assertTrue(dialog.GetTitle().endswith(" (original overwritten)"))
            dialog.set_original_overwritten(False)
            self.assertNotIn("(original overwritten)", dialog.GetTitle())
            dialog.set_original_overwritten(True)
            self.assertTrue(dialog.GetTitle().endswith(" (original overwritten)"))
        finally:
            dialog.Destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
