from __future__ import annotations

import re


METHOD_KEY_RE = re.compile(r"^(?P<class>L.+?;)->(?P<name>[^\(]+)(?P<descriptor>\(.*\).*)$")


def _normalize_descriptor(descriptor: str | None) -> str | None:
    if descriptor is None:
        return None
    compact = re.sub(r"\s+", "", descriptor)
    return compact or None


def parse_method_key(key: str) -> dict[str, str | None]:
    match = METHOD_KEY_RE.match(key)
    if not match:
        return {
            "class_name": None,
            "method_name": None,
            "descriptor": None,
            "class_simple_name": None,
            "class_package": None,
        }

    class_name = match.group("class")
    descriptor = _normalize_descriptor(match.group("descriptor"))
    body = class_name[1:-1] if class_name.startswith("L") and class_name.endswith(";") else class_name
    parts = body.split("/")
    simple = parts[-1] if parts else body
    return {
        "class_name": class_name,
        "method_name": match.group("name"),
        "descriptor": descriptor,
        "class_simple_name": simple.split("$")[-1] if simple else None,
        "class_package": "/".join(parts[:-1]) if len(parts) > 1 else "",
    }


def coalesce_node_metadata(meta: dict[str, object]) -> dict[str, object]:
    parsed = parse_method_key(str(meta.get("key") or ""))
    payload = dict(meta)
    for field, value in parsed.items():
        current = payload.get(field)
        if current in (None, "") and value not in (None, ""):
            payload[field] = value
    return payload
