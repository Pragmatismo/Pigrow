"""Headless, ordered image layers for previews and exported timelapse sets.

Layer order is bottom to top. Each layer builds its own transparent history;
its blend mode combines contributions into that history and blends the result
onto the base. For frame and permanent layers, opacity applies once to the
completed layer. A trail retains exactly ``trail_frames`` input positions,
including the current position. Each contribution has opacity
``opacity * decay ** age`` so a translucent current copy can reveal older
copies. The completed trail is then composited at full opacity. Permanent
history never fades.

Returned images belong to the caller. The renderer owns only its input history,
so callers can display or save a result after the renderer has closed.
"""

from collections import deque
from copy import deepcopy
import math
import re

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


SOURCE_CHOICES = (
    ("copy", "Current image"),
    ("difference_previous", "Difference from previous image"),
    ("difference_first", "Difference from first image"),
    ("changed_pixels", "Current colors where pixels changed"),
    ("edges", "Edges"),
)
BLEND_CHOICES = (
    ("normal", "Normal"), ("add", "Add (clamped)"),
    ("add_modulo", "Add (wrap around)"), ("screen", "Screen"),
    ("lighten", "Lighten"), ("multiply", "Multiply"),
    ("difference", "Difference"),
)
PERSISTENCE_CHOICES = (
    ("frame", "Current frame only"),
    ("permanent", "Accumulate permanently"),
    ("trail", "Finite fading trail"),
)
BASE_CHOICES = (
    ("current", "Current image"), ("first", "First image"),
    ("black", "Black"), ("white", "White"),
)
MAX_LAYERS = 16
MAX_MEMORY_BYTES = 512 * 1024 * 1024


def default_layer():
    return {
        "name": "Layer 1", "enabled": True,
        "source": "difference_previous", "persistence": "frame",
        "blend": "screen", "opacity": 1.0, "threshold": 0, "gain": 1.0,
        "trail_frames": 8, "decay": 0.8, "tint": "", "invert": False,
    }


def default_settings():
    return {"version": 1, "base": "current", "max_size": 0,
            "layers": [default_layer()]}


def _integer(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError("{} must be an integer between {} and {}.".format(name, minimum, maximum))
    return value


def _number(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{} must be a number between {} and {}.".format(name, minimum, maximum))
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ValueError("{} must be finite.".format(name)) from None
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError("{} must be a finite number between {} and {}.".format(name, minimum, maximum))
    return result


def _choice(value, choices, name):
    if not isinstance(value, str) or value not in dict(choices):
        raise ValueError("{} must be one of {}.".format(name, ", ".join(key for key, _ in choices)))
    return value


def validate_settings(settings):
    """Return an independent canonical configuration, raising useful ValueErrors.

    Missing fields take their defaults. Unknown fields are rejected so a typo or
    a preset from an unsupported version cannot silently change the output.
    """
    if not isinstance(settings, dict):
        raise ValueError("Stylized set settings must be an object.")
    defaults = default_settings()
    unknown = set(settings) - set(defaults)
    if unknown:
        raise ValueError("Unknown settings fields: {}.".format(", ".join(sorted(map(str, unknown)))))
    result = deepcopy(defaults)
    result.update(deepcopy(settings))
    _integer(result["version"], "Settings version", 1, 1)
    result["base"] = _choice(result["base"], BASE_CHOICES, "Base")
    size = _integer(result["max_size"], "Maximum image size", 0, 4096)
    if size and size < 128:
        raise ValueError("Maximum image size must be 0 (original size), or between 128 and 4096 pixels.")
    if not isinstance(result["layers"], list):
        raise ValueError("Layers must be a list.")
    if len(result["layers"]) > MAX_LAYERS:
        raise ValueError("A stylized set can contain at most {} layers.".format(MAX_LAYERS))
    normalized = []
    for index, raw_layer in enumerate(result["layers"], 1):
        prefix = "Layer {}".format(index)
        if not isinstance(raw_layer, dict):
            raise ValueError(prefix + " must be an object.")
        layer = default_layer()
        layer["name"] = prefix
        unknown = set(raw_layer) - set(layer)
        if unknown:
            raise ValueError(prefix + " has unknown fields: " + ", ".join(sorted(map(str, unknown))) + ".")
        layer.update(deepcopy(raw_layer))
        if not isinstance(layer["name"], str) or not layer["name"].strip() or len(layer["name"]) > 80:
            raise ValueError(prefix + " name must contain 1 to 80 characters.")
        layer["name"] = layer["name"].strip()
        for field in ("enabled", "invert"):
            if not isinstance(layer[field], bool):
                raise ValueError(prefix + " " + field + " must be true or false.")
        for field, choices in (("source", SOURCE_CHOICES), ("blend", BLEND_CHOICES),
                               ("persistence", PERSISTENCE_CHOICES)):
            layer[field] = _choice(layer[field], choices, prefix + " " + field)
        for field, minimum, maximum in (("opacity", 0, 1), ("gain", 0.1, 8), ("decay", 0, 1)):
            layer[field] = _number(layer[field], prefix + " " + field, minimum, maximum)
        layer["threshold"] = _integer(layer["threshold"], prefix + " threshold", 0, 255)
        layer["trail_frames"] = _integer(layer["trail_frames"], prefix + " trail length", 1, 100)
        tint = layer["tint"]
        if not isinstance(tint, str) or (tint and re.fullmatch(r"#[0-9a-fA-F]{6}", tint) is None):
            raise ValueError(prefix + " tint must be empty or a color such as #33aaff.")
        layer["tint"] = tint.lower()
        normalized.append(layer)
    result["layers"] = normalized
    return result


def estimate_memory_bytes(settings, size):
    """Conservative working buffers plus all configured retained RGBA frames."""
    settings = validate_settings(settings)
    width, height = size
    history_frames = 0
    pending_frames = 0
    for layer in settings["layers"]:
        if not layer["enabled"]:
            continue
        if layer["persistence"] == "permanent":
            history_frames += 1
            pending_frames += 1
        elif layer["persistence"] == "trail":
            history_frames += layer["trail_frames"]
            pending_frames += 1
    # Pillow RGB buffers commonly use four internal bytes per pixel. The working
    # allowance includes current/previous/first images, masks and blend temporaries.
    return int(width) * int(height) * (48 + 4 * (history_frames + pending_frames))


def _scaled_size(size, maximum):
    if not maximum or max(size) <= maximum:
        return size
    scale = maximum / max(size)
    return max(1, round(size[0] * scale)), max(1, round(size[1] * scale))


def _blend(bottom, top, mode, opacity=1.0):
    """Blend straight RGBA colors with proper source-over alpha semantics."""
    if opacity <= 0:
        return bottom.copy()
    alpha = top.getchannel("A")
    try:
        if opacity < 1:
            scaled = alpha.point([round(value * opacity) for value in range(256)])
            alpha.close()
            alpha = scaled
        if alpha.getbbox() is None:
            return bottom.copy()
        if mode == "normal":
            with top.copy() as overlay:
                overlay.putalpha(alpha)
                return Image.alpha_composite(bottom, overlay)
        operations = {
            "add": ImageChops.add, "add_modulo": ImageChops.add_modulo,
            "screen": ImageChops.screen, "lighten": ImageChops.lighter,
            "multiply": ImageChops.multiply, "difference": ImageChops.difference,
        }
        with bottom.convert("RGB") as below, top.convert("RGB") as above:
            with operations[mode](below, above) as mixed, bottom.getchannel("A") as coverage:
                # A transparent history starts with source colors, even for
                # multiply/difference; its invisible RGB cannot influence them.
                with Image.composite(mixed, above, coverage) as overlay:
                    overlay.putalpha(alpha)
                    return Image.alpha_composite(bottom, overlay)
    finally:
        alpha.close()


class StylizedRenderer:
    """Stateful ordered renderer. Create a new instance to reset its history."""

    def __init__(self, settings, max_size=None):
        self._settings = validate_settings(settings)
        if max_size is not None:
            max_size = _integer(max_size, "Preview maximum size", 0, 4096)
        self.max_size = self._settings["max_size"] if max_size is None else max_size
        self.size = None
        self._first = None
        self._previous = None
        self._index = 0
        self._states = [None for _ in self._settings["layers"]]
        self._closed = False

    @property
    def settings(self):
        return deepcopy(self._settings)

    def __enter__(self):
        if self._closed:
            raise RuntimeError("This stylized renderer has already been closed.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _check_memory(self, target, decoded_size):
        estimate = estimate_memory_bytes(self._settings, target) + decoded_size[0] * decoded_size[1] * 4
        if estimate > MAX_MEMORY_BYTES:
            raise ValueError(
                "This image and layer history need approximately {:,.0f} MiB, above the {} MiB renderer limit. "
                "Choose a smaller maximum image size, fewer layers, or shorter trails. "
                "Very large source images may also need resizing before import.".format(
                    estimate / (1024 * 1024), MAX_MEMORY_BYTES // (1024 * 1024)))

    def _load(self, image_path):
        with Image.open(image_path) as source:
            width, height = source.size
            if source.getexif().get(274) in (5, 6, 7, 8):
                oriented_size = (height, width)
            else:
                oriented_size = (width, height)
            target = self.size or _scaled_size(oriented_size, self.max_size)
            # Draft JPEG decoding reduces the decoded source before the memory
            # check; other formats retain their original decode requirement.
            source.draft("RGB", (max(target), max(target)))
            self._check_memory(target, source.size)
            source.thumbnail((max(target), max(target)), Image.Resampling.LANCZOS)
            with ImageOps.exif_transpose(source) as oriented:
                rgb = oriented.convert("RGB")
            if rgb.size != target:
                try:
                    resized = rgb.resize(target, Image.Resampling.LANCZOS)
                finally:
                    rgb.close()
                rgb = resized
            return rgb

    def _source(self, current, layer):
        source = layer["source"]
        mask = None
        raw = None
        try:
            if source in ("difference_previous", "difference_first", "changed_pixels"):
                reference = self._first if source == "difference_first" else self._previous
                raw = ImageChops.difference(current, reference) if reference is not None else Image.new("RGB", current.size)
                with raw.getchannel("R") as red, raw.getchannel("G") as green, raw.getchannel("B") as blue:
                    with ImageChops.lighter(red, green) as red_green:
                        with ImageChops.lighter(red_green, blue) as strength:
                            mask = strength.point([255 if value > layer["threshold"] else 0 for value in range(256)])
                color = current.copy() if source == "changed_pixels" else raw.copy()
            elif source == "edges":
                raw = current.filter(ImageFilter.FIND_EDGES)
                # FIND_EDGES leaves a copy of the input around its border.
                ImageDraw.Draw(raw).rectangle((0, 0, raw.width - 1, raw.height - 1), outline="black", width=1)
                with raw.convert("L") as strength:
                    mask = strength.point([255 if value > layer["threshold"] else 0 for value in range(256)])
                color = raw.copy()
            else:
                color = current.copy()
                mask = Image.new("L", current.size, 255)
            try:
                if layer["invert"]:
                    transformed = ImageOps.invert(color)
                    color.close()
                    color = transformed
                if layer["tint"]:
                    with ImageOps.grayscale(color) as grey:
                        transformed = ImageOps.colorize(grey, "black", layer["tint"])
                    color.close()
                    color = transformed
                if layer["gain"] != 1:
                    transformed = ImageEnhance.Brightness(color).enhance(layer["gain"])
                    color.close()
                    color = transformed
                result = color.convert("RGBA")
                result.putalpha(mask)
                return result
            finally:
                color.close()
        finally:
            if raw is not None:
                raw.close()
            if mask is not None:
                mask.close()

    @staticmethod
    def _state_images(state):
        if isinstance(state, deque):
            return [image for _, image in state]
        return [] if state is None else [state]

    @classmethod
    def _close_state(cls, state, keep=()):
        for image in cls._state_images(state):
            if id(image) not in keep:
                image.close()

    def process(self, image_path):
        if self._closed:
            raise RuntimeError("This stylized renderer has already been closed.")
        current = self._load(image_path)
        output = None
        pending = []
        new_first = None
        new_previous = None
        result = None
        try:
            base = self._settings["base"]
            if base == "current":
                output = current.convert("RGBA")
            elif base == "first":
                output = (self._first or current).convert("RGBA")
            else:
                output = Image.new("RGBA", current.size, "white" if base == "white" else "black")
            for index, layer in enumerate(self._settings["layers"]):
                if not layer["enabled"]:
                    pending.append(None)
                    continue
                with self._source(current, layer) as source:
                    persistence = layer["persistence"]
                    if persistence == "frame":
                        pending.append(None)
                        rendered = source.copy()
                    elif persistence == "permanent":
                        previous = self._states[index]
                        if previous is None:
                            rendered = source.copy()
                        else:
                            rendered = _blend(previous, source, layer["blend"])
                        pending.append(rendered.copy())
                    else:
                        previous = self._states[index] or deque()
                        history = deque((frame, image) for frame, image in previous
                                        if self._index - frame < layer["trail_frames"])
                        history.append((self._index, source.copy()))
                        pending.append(history)
                        rendered = Image.new("RGBA", current.size)
                        for frame, image in history:
                            strength = layer["opacity"] * layer["decay"] ** (self._index - frame)
                            aged = _blend(rendered, image, layer["blend"], strength)
                            rendered.close()
                            rendered = aged
                    try:
                        opacity = 1.0 if persistence == "trail" else layer["opacity"]
                        composited = _blend(output, rendered, layer["blend"], opacity)
                        output.close()
                        output = composited
                    finally:
                        rendered.close()
            result = output.convert("RGB")
            new_first = current.copy() if self._first is None else None
            new_previous = current.copy()
            # Commit state only after this complete frame rendered successfully.
            retained = {id(image) for state in pending for image in self._state_images(state)}
            for state in self._states:
                self._close_state(state, retained)
            self._states = pending
            pending = []
            if new_first is not None:
                self._first = new_first
                new_first = None
            if self._previous is not None:
                self._previous.close()
            self._previous = new_previous
            new_previous = None
            self.size = current.size
            self._index += 1
            returned = result
            result = None
            return returned
        finally:
            current.close()
            if output is not None:
                output.close()
            if result is not None:
                result.close()
            if new_first is not None:
                new_first.close()
            if new_previous is not None:
                new_previous.close()
            retained = {id(image) for state in self._states for image in self._state_images(state)}
            for state in pending:
                self._close_state(state, retained)

    def close(self):
        if not self._closed:
            for state in self._states:
                self._close_state(state)
            self._states = []
            for image in (self._first, self._previous):
                if image is not None:
                    image.close()
            self._first = self._previous = None
            self._closed = True
