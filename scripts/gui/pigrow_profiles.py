"""Saved connection profiles, independent of wx and network access.

Profiles are stored as one JSON value in the existing GUI settings file.  A
tentative profile identifies a discovered device until its Pigrow name is read.
"""

import json
import uuid


UNKNOWN_PI = "unknown pi"


def _text(value, default=""):
    return default if value is None else str(value)


def normalized_address(address):
    """Compare IP addresses and hostnames without making DNS requests."""
    return _text(address).strip().casefold().rstrip(".")


def _tentative(value):
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "no", "0")
    return bool(value)


def new_profile(box_name=UNKNOWN_PI, address="", username="pi", password="",
                tentative=True):
    return {
        "id": uuid.uuid4().hex,
        "box_name": _text(box_name).strip() or UNKNOWN_PI,
        "address": _text(address).strip(),
        "username": _text(username, "pi").strip(),
        "password": _text(password),
        "tentative": _tentative(tentative),
    }


def normalize_profiles(profiles):
    """Return valid, independent records with distinct stable identifiers."""
    if not isinstance(profiles, list):
        return []
    result = []
    seen_ids = set()
    for item in profiles:
        if not isinstance(item, dict):
            continue
        name = _text(item.get("box_name")).strip() or UNKNOWN_PI
        profile = new_profile(
            box_name=name,
            address=item.get("address", ""),
            username=item.get("username", "pi"),
            password=item.get("password", ""),
            tentative=item.get("tentative", name.casefold() == UNKNOWN_PI),
        )
        profile_id = _text(item.get("id")).strip()
        if profile_id and profile_id not in seen_ids:
            profile["id"] = profile_id
        seen_ids.add(profile["id"])
        result.append(profile)
    return result


def load_profiles(settings):
    """Load JSON profiles or migrate the legacy single-device defaults.

    An explicitly saved empty list remains empty. Invalid JSON also remains
    empty instead of reviving deleted legacy credentials.
    """
    if "pigrows" not in settings:
        address = _text(settings.get("default_address", "")).strip()
        if not address:
            return []
        return [new_profile(
            address=address,
            username=settings.get("username", "pi"),
            password=settings.get("password", ""),
        )]
    profiles = settings["pigrows"]
    if isinstance(profiles, str):
        try:
            profiles = json.loads(profiles)
        except (ValueError, TypeError):
            return []
    return normalize_profiles(profiles)


def serialize_profiles(profiles):
    """Escape credentials so they cannot introduce extra settings lines."""
    return json.dumps(normalize_profiles(profiles), ensure_ascii=True,
                      separators=(",", ":"))


def find_address_conflicts(profiles, address, box_name, exclude_id=None):
    """Find older named devices using the newly connected device's address."""
    address_key = normalized_address(address)
    if not address_key:
        return []
    name = _text(box_name).strip() or UNKNOWN_PI
    if name.casefold() == UNKNOWN_PI:
        return []
    return [profile for profile in normalize_profiles(profiles)
            if profile["id"] != exclude_id
            and not profile["tentative"]
            and profile["box_name"] != name
            and normalized_address(profile["address"]) == address_key]


def record_connection(profiles, box_name, address, username, password,
                      selected_id=None, conflict_actions=None):
    """Save a successful connection and return (profiles, selected_id).

    A moved device updates the record with its known name. A tentative record
    receives its confirmed name in place. An established differently named
    device is preserved unless the user chooses remove or unlink for its ID;
    ignore leaves its address and credentials intact.
    """
    result = normalize_profiles(profiles)
    name = _text(box_name).strip() or UNKNOWN_PI
    address = _text(address).strip()
    address_key = normalized_address(address)
    tentative = name.casefold() == UNKNOWN_PI
    selected = next((item for item in result
                     if item["id"] == selected_id), None)

    # Prefer an existing named Pigrow when discovering its new location.
    target = None
    if not tentative:
        if selected and selected["box_name"] == name:
            target = selected
        else:
            target = next((item for item in result
                           if item["box_name"] == name), None)
    if target is None and selected and selected["tentative"]:
        target = selected
    if target is None and address_key:
        target = next((item for item in result
                       if item["tentative"]
                       and normalized_address(item["address"]) == address_key), None)
    if target is None:
        target = new_profile()
        result.append(target)

    actions = conflict_actions or {}
    removed_ids = set()
    # The panel may confirm that a hostname and numeric IP reach the same
    # peer. Honour those explicit choices without doing DNS work here.
    for older in result:
        if older["id"] == target["id"] or older["box_name"] == name:
            continue
        action = actions.get(older["id"], "ignore")
        if action not in ("remove", "unlink", "ignore"):
            raise ValueError("Unknown Pigrow conflict action: " + str(action))
        if action == "remove":
            removed_ids.add(older["id"])
        elif action == "unlink":
            older["address"] = ""

    # Merge tentative sightings of this address and duplicate known names.
    for item in result:
        if item["id"] == target["id"]:
            continue
        if (item["tentative"] and address_key
                and normalized_address(item["address"]) == address_key):
            removed_ids.add(item["id"])
        elif not tentative and item["box_name"] == name:
            removed_ids.add(item["id"])
    if selected and selected["tentative"] and selected["id"] != target["id"]:
        removed_ids.add(selected["id"])

    target.update(box_name=name, address=address,
                  username=_text(username, "pi").strip(),
                  password=_text(password), tentative=tentative)
    return ([item for item in result if item["id"] not in removed_ids],
            target["id"])
