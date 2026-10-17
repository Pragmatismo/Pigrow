"""Stable, full-resolution snapshots for photographs displayed by the camera UI.

A capture may reuse its output filename.  A photo's identity therefore belongs
to this snapshot, rather than to the file that originally supplied its pixels.
File checks are explicit: rendering and resizing never read or hash the source.
"""

import hashlib
import io
import os
from uuid import uuid4

import wx


def _source_key(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(os.fspath(path))))


def _fingerprint(path):
    """Return a content fingerprint, or None when the source is unavailable."""
    try:
        with open(path, "rb") as source:
            digest = hashlib.sha256()
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


class PhotoRecord:
    """One displayed photograph, independently addressable after path reuse."""

    def __init__(self, source_path, label, image, source_fingerprint):
        self.record_id = uuid4().hex
        self.source_path = os.fspath(source_path)
        self.label = label
        self.source_fingerprint = source_fingerprint
        self.original_overwritten = False
        self._source_key = _source_key(source_path)
        # Keep private pixels: neither callers nor future file writes can mutate
        # the snapshot used by thumbnails, scaled previews and image dialogs.
        self._image = image.Copy()

    @property
    def image(self):
        return self._image.Copy()

    @property
    def width(self):
        return self._image.GetWidth()

    @property
    def height(self):
        return self._image.GetHeight()

    def check_source(self):
        """Mark a replacement even when this photo is retained outside a store.

        Return True only on the transition to overwritten.  Missing originals
        leave the snapshot usable without inaccurately calling them replaced.
        """
        if self.original_overwritten:
            return False
        fingerprint = _fingerprint(self.source_path)
        if fingerprint is not None and fingerprint != self.source_fingerprint:
            self.original_overwritten = True
            return True
        return False

    def get_bitmap(self, width=None):
        """Render at full size or fit exactly to a width, retaining aspect ratio."""
        if width is None or int(width) == self.width:
            return self._image.ConvertToBitmap()
        width = max(1, int(width))
        height = max(1, round(self.height * width / self.width))
        return self._image.Scale(width, height, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()

    def thumbnail(self, width=40, height=30):
        """Return a small aspect-preserving bitmap within the requested bounds."""
        scale = min(max(1, width) / self.width, max(1, height) / self.height, 1.0)
        return self._image.Scale(
            max(1, round(self.width * scale)),
            max(1, round(self.height * scale)),
            wx.IMAGE_QUALITY_HIGH,
        ).ConvertToBitmap()


class PhotoStore:
    """Newest-first camera photo records with explicit source-change checks."""

    def __init__(self):
        self.records = []
        self._by_id = {}

    def add(self, source_path, label):
        """Read a file once and add a distinct snapshot, even for a reused path.

        Hash the exact bytes decoded into the new image.  This also detects old
        records whose source was replaced before this new photo was displayed.
        Invalid images leave existing records intact.
        """
        source_path = os.fspath(source_path)
        with open(source_path, "rb") as source:
            data = source.read()
        fingerprint = hashlib.sha256(data).hexdigest()
        image = wx.Image(io.BytesIO(data), wx.BITMAP_TYPE_ANY)
        if not image.IsOk():
            raise ValueError("Unable to load camera photograph: " + source_path)
        source_key = _source_key(source_path)
        self._check_fingerprint(source_key, fingerprint)
        record = PhotoRecord(source_path, label, image, fingerprint)
        self.records.insert(0, record)
        self._by_id[record.record_id] = record
        return record

    def get(self, record_id):
        return self._by_id.get(record_id)

    def clear(self):
        self.records.clear()
        self._by_id.clear()

    def mark_overwritten(self, source_path):
        """Mark a known successful write to a displayed source filename."""
        key = _source_key(source_path)
        changed = []
        for record in self.records:
            if record._source_key == key and not record.original_overwritten:
                record.original_overwritten = True
                changed.append(record)
        return changed

    def _check_fingerprint(self, source_key, fingerprint):
        changed = []
        for record in self.records:
            if (record._source_key == source_key
                    and not record.original_overwritten
                    and record.source_fingerprint != fingerprint):
                record.original_overwritten = True
                changed.append(record)
        return changed

    def check_sources(self, source_path=None):
        """Detect replacements at open time or after a known file operation.

        Each source is hashed once per call, regardless of the number of photos
        taken at that path.  Deletion is not an overwrite; the snapshot remains
        usable and retains its current title in that case.
        """
        if source_path is None:
            sources = {record._source_key: record.source_path for record in self.records
                       if not record.original_overwritten}
        else:
            sources = {_source_key(source_path): os.fspath(source_path)}
        changed = []
        for key, path in sources.items():
            fingerprint = _fingerprint(path)
            if fingerprint is not None:
                changed.extend(self._check_fingerprint(key, fingerprint))
        return changed
