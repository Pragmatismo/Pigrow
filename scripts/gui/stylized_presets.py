"""Built-in and per-user presets for the stylized image-set builder.

Storage is independent of wx. A malformed file is reported as a whole so a
subsequent save cannot silently discard an unreadable preset collection.
"""

import json
import os
import tempfile
import unicodedata

from stylized_sets import default_layer, default_settings, validate_settings


MAX_FILE_BYTES = 1024 * 1024
MAX_USER_PRESETS = 100
MAX_NAME_LENGTH = 80


def _layer(name, **options):
    layer = default_layer()
    layer.update(options)
    layer["name"] = name
    return layer


def _settings(base, layers):
    settings = default_settings()
    settings.update(base=base, max_size=1920, layers=layers)
    return validate_settings(settings)


def builtin_presets():
    """Return independent settings for the six supplied creative starting points."""
    return {
        "Accumulated difference": _settings("first", [_layer(
            "Accumulated changes", source="difference_previous",
            persistence="permanent", blend="add_modulo", opacity=1.0,
            threshold=0, gain=1.0)]),
        "Motion ghosts": _settings("current", [_layer(
            "Recent movement", source="changed_pixels", persistence="trail",
            blend="normal", opacity=0.6, threshold=12, gain=1.0,
            trail_frames=12, decay=0.8)]),
        "Light painting": _settings("black", [_layer(
            "Brightest captures", source="copy", persistence="permanent",
            blend="lighten", opacity=1.0, threshold=0, gain=1.0)]),
        "Neon motion": _settings("black", [_layer(
            "Cyan motion trails", source="difference_previous",
            persistence="trail", blend="screen", opacity=1.0,
            threshold=8, gain=3.0, trail_frames=12, decay=0.8,
            tint="#00ffff")]),
        "Changed pixels": _settings("first", [_layer(
            "Last changed pixels", source="changed_pixels",
            persistence="permanent", blend="normal", opacity=1.0,
            threshold=20, gain=1.0)]),
        "RGB ghost trails": _settings("current", [
            _layer("Red short trail", source="difference_previous",
                   persistence="trail", blend="screen", opacity=0.65,
                   threshold=10, gain=2.0, trail_frames=4, decay=0.75,
                   tint="#ff3030"),
            _layer("Green medium trail", source="difference_previous",
                   persistence="trail", blend="screen", opacity=0.55,
                   threshold=10, gain=2.0, trail_frames=8, decay=0.85,
                   tint="#30ff30"),
            _layer("Blue long trail", source="difference_previous",
                   persistence="trail", blend="screen", opacity=0.55,
                   threshold=10, gain=2.0, trail_frames=16, decay=0.9,
                   tint="#3060ff"),
        ]),
    }


def default_preset_path():
    """Use the platform's user configuration directory without creating it."""
    if os.name == "nt":
        root = os.environ.get("APPDATA") or os.path.join(
            os.path.expanduser("~"), "AppData", "Roaming")
    else:
        root = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config")
    return os.path.join(root, "Pigrow", "stylized_presets.json")


def _name(value):
    if not isinstance(value, str):
        raise ValueError("Preset names must be text.")
    if any(unicodedata.category(character) == "Cc" for character in value):
        raise ValueError("Preset names cannot contain control characters.")
    value = value.strip()
    if not value:
        raise ValueError("Enter a name for the preset.")
    if len(value) > MAX_NAME_LENGTH:
        raise ValueError("Preset names must be at most 80 characters long.")
    return value


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: {!r}.".format(key))
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Invalid JSON number: {}.".format(value))


def _read_user_presets(path, builtin_names):
    try:
        with open(path, "rb") as source:
            data = source.read(MAX_FILE_BYTES + 1)
    except FileNotFoundError:
        return {}
    try:
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("Preset files must be no larger than 1 MiB.")
        document = json.loads(data.decode("utf-8"), object_pairs_hook=_json_object,
                              parse_constant=_reject_constant)
        if not isinstance(document, dict) or set(document) != {"version", "presets"}:
            raise ValueError("Expected an object containing only version and presets.")
        if type(document["version"]) is not int or document["version"] != 1:
            raise ValueError("Unsupported preset file version; expected version 1.")
        presets = document["presets"]
        if not isinstance(presets, dict):
            raise ValueError("The presets field must be an object.")
        if len(presets) > MAX_USER_PRESETS:
            raise ValueError("At most 100 custom presets can be stored.")
        result = {}
        for raw_name, settings in presets.items():
            name = _name(raw_name)
            if name in builtin_names:
                raise ValueError("{!r} is a built-in preset; use a different name.".format(name))
            if name in result:
                raise ValueError("Duplicate preset name after trimming spaces: {!r}.".format(name))
            try:
                result[name] = validate_settings(settings)
            except (TypeError, ValueError) as error:
                raise ValueError("Invalid settings for preset {!r}: {}".format(name, error)) from error
        return result
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise ValueError("Could not read stylized presets from {!r}: {}".format(
            os.fspath(path), error)) from error


def load_presets(path=None):
    """Return fresh built-ins plus all valid user presets, or explain corruption."""
    path = default_preset_path() if path is None else os.fspath(path)
    result = builtin_presets()
    result.update(_read_user_presets(path, result))
    return result


def save_preset(name, settings, path=None):
    """Add/update a custom preset atomically, preserving the file on any failure."""
    name = _name(name)
    builtins = builtin_presets()
    if name in builtins:
        raise ValueError("{!r} is a built-in preset; use a different name.".format(name))
    settings = validate_settings(settings)
    path = default_preset_path() if path is None else os.fspath(path)
    users = _read_user_presets(path, builtins)
    if name not in users and len(users) >= MAX_USER_PRESETS:
        raise ValueError("At most 100 custom presets can be stored. Update an existing preset.")
    users[name] = settings
    data = (json.dumps({"version": 1, "presets": users}, ensure_ascii=False,
                       allow_nan=False, indent=2) + "\n").encode("utf-8")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("The saved preset collection would exceed the 1 MiB limit.")
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".stylized-presets-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
