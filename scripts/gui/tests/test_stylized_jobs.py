"""Headless export safety, cancellation and stateful preview regressions."""

from copy import deepcopy
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from PIL import Image, ImageChops

GUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GUI))

import stylized_jobs as jobs
from stylized_sets import default_settings, StylizedRenderer
from timelapse_modules.analysis_common import capture_datetime


class StylizedJobsTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="stylized-jobs-")
        self.root = Path(self.folder.name)
        self.sources = self.root / "source"
        self.sources.mkdir()
        self.output = self.root / "output"
        self.output.mkdir()
        self.settings = default_settings()
        self.frames = []
        for index, suffix in enumerate(("1700000000.25", "20260102123000", "undated")):
            path = self.sources / ("cap_" + suffix + ".png")
            with Image.new("RGB", (40, 30), (30 + 50 * index, 60, 130 - 20 * index)) as image:
                image.save(path)
            self.frames.append(str(path))
        self.originals = [Path(path).read_bytes() for path in self.frames]

    def tearDown(self):
        self.folder.cleanup()

    def manifest(self, name):
        return json.loads((self.output / name / jobs.MANIFEST_NAME).read_text())

    def exported(self, name):
        return sorted((self.output / name).glob("*.png"))

    def wait_job(self, job):
        until = time.monotonic() + 10
        while time.monotonic() < until:
            state = job.snapshot()
            if state["status"] in {"completed", "cancelled", "failed"}:
                return state
            time.sleep(0.005)
        self.fail("Export did not finish within 10 seconds")

    def assert_sources_unchanged(self):
        self.assertEqual([Path(path).read_bytes() for path in self.frames], self.originals)

    def test_complete_export_includes_first_frame_and_timestamp_suffixes(self):
        result = jobs.export_set(self.frames, self.settings, self.output, "Plant-1")
        self.assertEqual(result["status"], "completed")
        self.assertEqual((result["completed"], result["total"]), (3, 3))
        paths = self.exported("Plant-1")
        self.assertEqual([path.name for path in paths], [
            "Plant-1_00000001_1700000000.25.png", "Plant-1_00000002_20260102123000.png",
            "Plant-1_00000003_undated.png"])
        self.assertEqual(capture_datetime(paths[0]), capture_datetime(self.frames[0]))
        self.assertEqual(capture_datetime(paths[1]), capture_datetime(self.frames[1]))
        self.assertIsNone(capture_datetime(paths[2]))
        for path in paths:
            with Image.open(path) as image:
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, (40, 30))
                image.verify()
        manifest = self.manifest("Plant-1")
        self.assertEqual((manifest["version"], manifest["source_count"], manifest["completed"],
                          manifest["state"]), (1, 3, 3, "completed"))
        self.assertEqual(manifest["settings"], self.settings)
        self.assert_sources_unchanged()

    def test_duplicate_capture_paths_have_distinct_ordered_output_names(self):
        jobs.export_set([self.frames[0]] * 3, self.settings, self.output, "Repeated")
        paths = self.exported("Repeated")
        self.assertEqual(len(paths), 3)
        self.assertEqual([path.name.split("_")[1] for path in paths],
                         ["00000001", "00000002", "00000003"])
        self.assertEqual({capture_datetime(path) for path in paths}, {capture_datetime(self.frames[0])})

    def test_existing_directory_or_file_is_never_modified(self):
        existing = self.output / "Existing"
        existing.mkdir()
        marker = existing / jobs.MANIFEST_NAME
        marker.write_text("existing user's metadata")
        for destination in (existing, self.output / "A-file"):
            if destination != existing:
                destination.write_text("existing file")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                jobs.export_set(self.frames, self.settings, self.output, destination.name)
        self.assertEqual(marker.read_text(), "existing user's metadata")
        self.assertEqual((self.output / "A-file").read_text(), "existing file")
        self.assert_sources_unchanged()

    def test_output_cannot_reuse_source_directory(self):
        with self.assertRaises(FileExistsError):
            jobs.export_set(self.frames, self.settings, self.root, "source")
        self.assert_sources_unchanged()

    def test_invalid_names_and_empty_frames_create_no_output(self):
        for name in ("", "../escape", "name_with_underscore", " spaces ", ".hidden", "-bad", "a" * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                jobs.export_set(self.frames, self.settings, self.output, name)
        with self.assertRaises(ValueError):
            jobs.export_set([], self.settings, self.output, "Empty")
        self.assertEqual(list(self.output.iterdir()), [])

    def test_cancellation_keeps_complete_frames_and_manifest(self):
        cancel = threading.Event()
        notices = []

        def progress(completed, total, path):
            notices.append((completed, total, path))
            cancel.set()

        result = jobs.export_set(self.frames, self.settings, self.output, "Cancelled",
                                 cancel_event=cancel, progress=progress)
        self.assertEqual((result["status"], result["completed"]), ("cancelled", 1))
        self.assertEqual(notices, [(1, 3, self.frames[0])])
        self.assertEqual(len(self.exported("Cancelled")), 1)
        self.assertEqual(self.manifest("Cancelled")["state"], "cancelled")
        self.assertEqual(self.manifest("Cancelled")["completed"], 1)
        self.assertFalse(list((self.output / "Cancelled").glob("*.tmp")))
        self.assert_sources_unchanged()

    def test_cancel_after_final_frame_reports_completed(self):
        cancel = threading.Event()
        result = jobs.export_set(self.frames, self.settings, self.output, "Last-frame",
                                 cancel_event=cancel,
                                 progress=lambda completed, total, path: cancel.set()
                                 if completed == total else None)
        self.assertEqual((result["status"], result["completed"]), ("completed", 3))
        self.assertEqual(self.manifest("Last-frame")["state"], "completed")

    def test_cancelled_before_first_frame_claims_empty_partial_set(self):
        cancel = threading.Event()
        cancel.set()
        with mock.patch.object(jobs, "StylizedRenderer") as renderer:
            result = jobs.export_set(self.frames, self.settings, self.output, "Zero", cancel_event=cancel)
        renderer.assert_not_called()
        self.assertEqual((result["status"], result["completed"]), ("cancelled", 0))
        self.assertEqual(self.manifest("Zero")["state"], "cancelled")
        self.assertEqual(self.exported("Zero"), [])

    def test_corrupt_frame_preserves_prior_outputs_and_failure_metadata(self):
        corrupt = self.sources / "bad_1700000100.jpg"
        corrupt.write_bytes(b"invalid image")
        with self.assertRaisesRegex(RuntimeError, r"Frame 2 of 3 \(bad_1700000100.jpg\)"):
            jobs.export_set([self.frames[0], str(corrupt), self.frames[2]], self.settings,
                            self.output, "Broken")
        self.assertEqual(len(self.exported("Broken")), 1)
        manifest = self.manifest("Broken")
        self.assertEqual((manifest["state"], manifest["completed"]), ("failed", 1))
        self.assertIn("bad_1700000100.jpg", manifest["error"])
        self.assertFalse(list((self.output / "Broken").glob("*.tmp")))
        self.assert_sources_unchanged()

    def test_save_error_cleans_temporary_frame_and_reports_failure(self):
        with mock.patch.object(Image.Image, "save", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(RuntimeError, "disk full"):
                jobs.export_set(self.frames, self.settings, self.output, "No-space")
        self.assertEqual(self.exported("No-space"), [])
        self.assertFalse(list((self.output / "No-space").glob("*.tmp")))
        self.assertEqual(self.manifest("No-space")["state"], "failed")

    def test_unsupported_hardlinks_use_exclusive_copy(self):
        with mock.patch.object(jobs.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "unsupported")):
            result = jobs.export_set(self.frames, self.settings, self.output, "Portable")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(self.exported("Portable")), 3)
        self.assertFalse(list((self.output / "Portable").glob("*.tmp")))

    def test_failed_portable_copy_removes_incomplete_final_file(self):
        def incomplete_copy(source, target, **kwargs):
            target.write(b"partial")
            raise OSError("storage unavailable")

        with mock.patch.object(jobs.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "unsupported")):
            with mock.patch.object(jobs.shutil, "copyfileobj", side_effect=incomplete_copy):
                with self.assertRaisesRegex(RuntimeError, "storage unavailable"):
                    jobs.export_set(self.frames, self.settings, self.output, "Partial")
        self.assertEqual(self.exported("Partial"), [])
        self.assertFalse(list((self.output / "Partial").glob("*.tmp")))
        self.assertEqual(self.manifest("Partial")["completed"], 0)

    def test_raced_output_file_is_not_overwritten(self):
        def raced_link(source, destination):
            Path(destination).write_bytes(b"someone else's file")
            raise FileExistsError("already present")

        with mock.patch.object(jobs.os, "link", side_effect=raced_link):
            with self.assertRaisesRegex(RuntimeError, "already present"):
                jobs.export_set(self.frames, self.settings, self.output, "Race")
        self.assertEqual(self.exported("Race")[0].read_bytes(), b"someone else's file")
        self.assertEqual(self.manifest("Race")["state"], "failed")

    def test_job_snapshots_input_lists_settings_and_polling_results(self):
        settings = deepcopy(self.settings)
        frames = list(self.frames)
        job = jobs.ExportJob(frames, settings, self.output, "Worker")
        initial = job.snapshot()
        self.assertEqual((initial["status"], initial["total"]), ("pending", 3))
        initial["total"] = 99
        frames.append(str(self.sources / "missing.jpg"))
        settings["layers"][0]["opacity"] = 0.3
        self.assertIs(job.start(), job)
        state = self.wait_job(job)
        self.assertEqual((state["status"], state["completed"], state["total"]), ("completed", 3, 3))
        self.assertEqual(self.manifest("Worker")["settings"], self.settings)
        self.assertEqual(job.snapshot()["total"], 3)
        with self.assertRaisesRegex(RuntimeError, "already been started"):
            job.start()

    def test_job_cancel_before_start_and_failure_are_pollable(self):
        cancelled = jobs.ExportJob(self.frames, self.settings, self.output, "Worker-cancel")
        cancelled.cancel()
        cancelled.start()
        self.assertEqual(self.wait_job(cancelled)["status"], "cancelled")
        failed = jobs.ExportJob([str(self.sources / "missing.jpg")], self.settings, self.output, "Worker-fail")
        failed.start()
        state = self.wait_job(failed)
        self.assertEqual((state["status"], state["completed"]), ("failed", 0))
        self.assertIn("Frame 1", state["error"])
        self.assertEqual(self.manifest("Worker-fail")["state"], "failed")

    def test_preview_matches_sequential_render_after_backtracking(self):
        settings = deepcopy(self.settings)
        with jobs.PreviewSession(self.frames, settings, max_size=32) as session:
            settings["layers"][0]["opacity"] = 0.2
            with StylizedRenderer(self.settings, max_size=32) as renderer:
                expected = [renderer.process(path) for path in self.frames]
            try:
                for index in (2, 0, 1, 1, 2):
                    with session.preview(index) as image:
                        self.assertIsNone(ImageChops.difference(image, expected[index]).getbbox())
                        self.assertLessEqual(max(image.size), 32)
                owned = session.preview(0)
            finally:
                for image in expected:
                    image.close()
        self.assertIsInstance(owned.getpixel((0, 0)), tuple)
        owned.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            session.preview(0)

    def test_preview_uses_smaller_configured_export_resolution_exactly(self):
        settings = deepcopy(self.settings)
        settings["max_size"] = 128
        frames = []
        for index in range(3):
            path = self.sources / ("large_{}.png".format(1700000000 + index))
            # Fine detail makes processing at 640 and then resizing observably
            # different from computing temporal effects directly at 128.
            with Image.new("RGB", (800, 600), "black") as image:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(image)
                for x in range(index, 800, 7):
                    draw.line((x, 0, x, 599), fill=(40 + index * 60, 150, 210), width=2)
                image.save(path)
            frames.append(str(path))
        with jobs.PreviewSession(frames, settings, max_size=640) as session:
            with StylizedRenderer(settings) as renderer:
                for index, path in enumerate(frames):
                    with renderer.process(path) as expected:
                        with session.preview(index) as preview:
                            self.assertEqual(preview.size, (128, 96))
                            self.assertEqual(preview.size, expected.size)
                            self.assertIsNone(ImageChops.difference(preview, expected).getbbox())

    def test_preview_error_names_frame_and_can_replay_after_repair(self):
        bad = self.sources / "broken.jpg"
        bad.write_bytes(b"broken")
        with jobs.PreviewSession([self.frames[0], str(bad)], self.settings) as session:
            with self.assertRaisesRegex(RuntimeError, r"Preview frame 2 of 2 \(broken.jpg\)"):
                session.preview(1)
            with Image.new("RGB", (40, 30), "red") as image:
                image.save(bad)
            with session.preview(1) as image:
                self.assertEqual(image.mode, "RGB")

    def test_module_import_does_not_import_wx(self):
        command = [sys.executable, "-c", "import sys, stylized_jobs; assert 'wx' not in sys.modules"]
        environment = dict(os.environ, PYTHONPATH=str(GUI))
        completed = subprocess.run(command, env=environment, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
