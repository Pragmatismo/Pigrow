"""Headless, cancellable image-set exports and deterministic sequential previews.

Each export exclusively claims a new directory. Completed PNGs remain usable if
processing is cancelled or a later frame fails; the manifest describes that state.
This module has no wx dependency and never changes source files.
"""

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading

from stylized_sets import StylizedRenderer, validate_settings
from timelapse_modules.analysis_common import capture_datetime

MANIFEST_NAME = ".pigrow-stylized.json"
_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,63}\Z")


def validate_set_name(set_name):
    """Keep set names portable and separate from timestamp filename suffixes."""
    if not isinstance(set_name, str) or not _NAME_PATTERN.fullmatch(set_name):
        raise ValueError("Set name must be 1–64 letters, digits or hyphens, starting with a letter or digit.")
    return set_name


def _snapshot_frames(frames):
    paths = tuple(os.path.abspath(os.fspath(path)) for path in frames)
    if not paths:
        raise ValueError("There are no images in the selected frame range.")
    return paths


def _configuration(frames, settings, output_parent, set_name):
    return (_snapshot_frames(frames), validate_settings(deepcopy(settings)),
            os.path.abspath(os.fspath(output_parent)), validate_set_name(set_name))


def output_filename(set_name, index, source_path):
    """Index is one-based; repeated captures remain distinct and sortable."""
    suffix = Path(source_path).stem.rsplit("_", 1)[-1]
    if capture_datetime(source_path) is None:
        suffix = "undated"
    return "{}_{:08d}_{}.png".format(set_name, index, suffix)


def _write_manifest(output_dir, metadata):
    handle, temporary = tempfile.mkstemp(prefix=".manifest-", suffix=".tmp", dir=output_dir)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(metadata, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, os.path.join(output_dir, MANIFEST_NAME))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _save_png_exclusive(image, destination):
    """Publish a complete PNG atomically, refusing even a raced existing file."""
    handle, temporary = tempfile.mkstemp(prefix=".frame-", suffix=".tmp", dir=os.path.dirname(destination))
    os.close(handle)
    try:
        image.save(temporary, format="PNG")
        # link is an atomic no-clobber operation; replace/rename may overwrite.
        try:
            os.link(temporary, destination)
        except FileExistsError:
            raise
        except OSError:
            # exFAT, some network shares and Windows configurations cannot
            # hardlink. Exclusive creation still prevents clobbering anything;
            # remove an incomplete fallback copy before reporting an error.
            created = False
            try:
                with open(temporary, "rb") as source:
                    with open(destination, "xb") as target:
                        created = True
                        shutil.copyfileobj(source, target, length=1024 * 1024)
            except BaseException:
                if created:
                    os.unlink(destination)
                raise
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def export_set(frames, settings, output_parent, set_name, *, cancel_event=None, progress=None):
    """Process every selected frame into a newly claimed image set directory.

    Cancellation is cooperative between frames, so an image already processing
    may finish. Errors name the failing frame and preserve all completed files.
    The caller owns a supplied cancellation event; progress runs on this thread.
    """
    frames, settings, output_parent, set_name = _configuration(
        frames, settings, output_parent, set_name)
    if not os.path.isdir(output_parent):
        raise ValueError("Output parent folder does not exist: {}".format(output_parent))
    output_dir = os.path.join(output_parent, set_name)
    try:
        os.mkdir(output_dir)
    except FileExistsError as error:
        raise FileExistsError("Output already exists; choose a new set name: {}".format(output_dir)) from error
    metadata = {"version": 1, "set_name": set_name, "settings": settings,
                "source_count": len(frames), "completed": 0, "state": "running"}
    renderer = None
    source_path = None
    index = 0
    try:
        _write_manifest(output_dir, metadata)
        if cancel_event is None or not cancel_event.is_set():
            renderer = StylizedRenderer(settings)
        for index, source_path in enumerate(frames, 1):
            if cancel_event is not None and cancel_event.is_set():
                break
            image = None
            try:
                image = renderer.process(source_path)
                destination = os.path.join(output_dir, output_filename(set_name, index, source_path))
                _save_png_exclusive(image, destination)
            except Exception as error:
                raise RuntimeError("Frame {} of {} ({}): {}".format(
                    index, len(frames), os.path.basename(source_path), error)) from error
            finally:
                if image is not None:
                    image.close()
            metadata["completed"] += 1
            # Report only committed complete frames; a later metadata failure
            # still leaves this output usable and reflected in job snapshots.
            if progress is not None:
                progress(metadata["completed"], len(frames), source_path)
            _write_manifest(output_dir, metadata)
        if renderer is not None:
            renderer.close()
            renderer = None
        # A late cancellation after the last committed frame is still a complete export.
        state = "completed" if metadata["completed"] == len(frames) else "cancelled"
        metadata["state"] = state
        _write_manifest(output_dir, metadata)
        return {"status": state, "output_dir": output_dir, "set_name": set_name,
                "completed": metadata["completed"], "total": len(frames)}
    except Exception as error:
        metadata["state"] = "failed"
        metadata["error"] = str(error)
        try:
            _write_manifest(output_dir, metadata)
        except Exception as manifest_error:
            raise RuntimeError("{}; failure metadata could not be saved: {}. Completed images remain in {}".format(
                error, manifest_error, output_dir)) from error
        raise
    finally:
        if renderer is not None:
            try:
                renderer.close()
            except Exception:
                # Do not replace the original processing/storage error.
                pass


class ExportJob:
    """A daemon worker with immutable inputs and lock-protected polling state."""

    def __init__(self, frames, settings, output_parent, set_name):
        self._frames, self._settings, self._output_parent, self._set_name = _configuration(
            frames, settings, output_parent, set_name)
        self._cancel_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self._state = {"status": "pending", "error": "", "completed": 0,
                       "total": len(self._frames), "set_name": self._set_name,
                       "output_dir": os.path.join(self._output_parent, self._set_name),
                       "source_path": ""}

    def start(self):
        """Start once; validation errors are synchronous and create no output."""
        # Revalidation is cheap, and makes start's contract explicit.
        validate_set_name(self._set_name)
        validate_settings(deepcopy(self._settings))
        with self._lock:
            if self._thread is not None:
                raise RuntimeError("This image-set export has already been started.")
            self._thread = threading.Thread(target=self._run, name="stylized-set-export", daemon=True)
            self._thread.start()
        return self

    def cancel(self):
        self._cancel_event.set()

    def snapshot(self):
        with self._lock:
            return deepcopy(self._state)

    def _progress(self, completed, total, source_path):
        with self._lock:
            self._state.update(completed=completed, total=total, source_path=source_path)

    def _run(self):
        with self._lock:
            self._state["status"] = "running"
        try:
            result = export_set(self._frames, self._settings, self._output_parent, self._set_name,
                                cancel_event=self._cancel_event, progress=self._progress)
        except Exception as error:
            with self._lock:
                self._state.update(status="failed", error=str(error))
        else:
            with self._lock:
                self._state.update(result)


class PreviewSession:
    """Replay stateful effects in set order, returning caller-owned RGB images."""

    def __init__(self, frames, settings, max_size=640):
        self._frames = _snapshot_frames(frames)
        self._settings = validate_settings(deepcopy(settings))
        if not isinstance(max_size, int) or isinstance(max_size, bool) or max_size <= 0:
            raise ValueError("Preview size must be a positive integer.")
        configured_size = self._settings["max_size"]
        # A preview cap may reduce full-size processing, but must never exceed
        # an explicitly chosen export size: edge/threshold effects depend on it.
        self._max_size = min(max_size, configured_size) if configured_size else max_size
        self._renderer = None
        self._last_image = None
        self._index = -1
        self._closed = False

    def _reset(self):
        if self._renderer is not None:
            self._renderer.close()
        self._renderer = None
        if self._last_image is not None:
            self._last_image.close()
        self._last_image = None
        self._index = -1

    def preview(self, index):
        if self._closed:
            raise RuntimeError("The preview session is closed.")
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(self._frames):
            raise ValueError("Preview frame must be between 0 and {}.".format(len(self._frames) - 1))
        if index < self._index:
            self._reset()
        if self._renderer is None:
            self._renderer = StylizedRenderer(self._settings, max_size=self._max_size)
        for current in range(self._index + 1, index + 1):
            try:
                image = self._renderer.process(self._frames[current])
            except Exception as error:
                self._reset()
                raise RuntimeError("Preview frame {} of {} ({}): {}".format(
                    current + 1, len(self._frames), os.path.basename(self._frames[current]), error)) from error
            if self._last_image is not None:
                self._last_image.close()
            self._last_image = image
            self._index = current
        return self._last_image.copy()

    def close(self):
        self._reset()
        self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError("The preview session is closed.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
