#!/usr/bin/env python3
"""
BitacuDrone — Catalog validator
===============================
Validates BitacuDrone/Resources/components_catalog.json (the catalog source of
truth) against the schema the app expects. Run locally and in CI on every PR
to the catalog repo. Exits non-zero on any error.

Usage:
    python3 scripts/validate_catalog.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, "components_catalog.json")

SCHEMA_VERSION = 3
SLOTS = {"frame", "motor", "esc", "fc", "vtx", "camera", "receiver", "antenna", "prop", "battery"}
LOCALES = {"es", "en", "fr", "de", "it", "pt", "ja", "zh-Hans", "ko", "nl", "pl", "ru"}


def main() -> int:
    if not os.path.exists(CATALOG):
        print(f"✗ Not found: {CATALOG}")
        return 1

    with open(CATALOG, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
            return 1

    errors, warnings = [], []

    if data.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}, got {data.get('schemaVersion')}")

    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty array")
        items = []

    seen_ids = set()
    for i, it in enumerate(items):
        where = it.get("id", f"index {i}")
        for req in ("id", "category", "title"):
            if not it.get(req):
                errors.append(f"[{where}] missing required field '{req}'")
        cid = it.get("id")
        if cid in seen_ids:
            errors.append(f"duplicate id '{cid}'")
        seen_ids.add(cid)

        if it.get("category") not in SLOTS:
            errors.append(f"[{where}] category '{it.get('category')}' not in {sorted(SLOTS)}")

        # slug convention: id should start with category.
        if cid and it.get("category") and not cid.startswith(it["category"] + "."):
            warnings.append(f"[{where}] id should start with '{it['category']}.'")

        desc = it.get("description", {})
        for loc in desc:
            if loc not in LOCALES:
                warnings.append(f"[{where}] description locale '{loc}' not in supported set")

        # Any user-followable URL in the catalog must be absolute https — the
        # app refuses anything else (CatalogURL.safe); fail CI so it never ships.
        def _check_url(field, value):
            if value and not str(value).lower().startswith("https://"):
                errors.append(f"[{where}] {field} must be an https URL, got: {value}")
        _check_url("image.remoteURL", (it.get("image") or {}).get("remoteURL"))
        _check_url("manualURL", it.get("manualURL"))
        _check_url("pinoutURL", it.get("pinoutURL"))

        for link in it.get("buyLinks", []):
            if "price" in link:
                errors.append(f"[{where}] buyLinks must NOT carry a price (rots; use live affiliate API)")
            if not link.get("url"):
                errors.append(f"[{where}] buyLink missing url")
            _check_url("buyLink.url", link.get("url"))

        img = it.get("image", {})
        if img and not isinstance(img, dict):
            errors.append(f"[{where}] image must be an object")

    # Manifest integrity: the published sha256/itemCount MUST match the catalog,
    # because the app accepts an OTA payload only if it matches the manifest.
    man_path = os.path.join(os.path.dirname(CATALOG), "components_catalog.manifest.json")
    if os.path.exists(man_path):
        import hashlib
        man = json.load(open(man_path, encoding="utf-8"))
        actual_sha = hashlib.sha256(open(CATALOG, "rb").read()).hexdigest()
        if man.get("sha256", "").lower() != actual_sha.lower():
            errors.append(f"manifest sha256 mismatch (run scripts/build_seed.py): {man.get('sha256')} != {actual_sha}")
        if man.get("itemCount") != len(items):
            errors.append(f"manifest itemCount {man.get('itemCount')} != {len(items)} items")
        if man.get("schemaVersion") != SCHEMA_VERSION:
            errors.append(f"manifest schemaVersion must be {SCHEMA_VERSION}")
    else:
        warnings.append("components_catalog.manifest.json missing — run scripts/build_seed.py")

    # Report
    for w in warnings:
        print(f"⚠︎  {w}")
    for e in errors:
        print(f"✗  {e}")

    if errors:
        print(f"\n✗ {len(errors)} error(s), {len(warnings)} warning(s). Catalog invalid.")
        return 1

    by_slot = {}
    for it in items:
        by_slot[it["category"]] = by_slot.get(it["category"], 0) + 1
    enriched = sum(1 for it in items if it.get("specs"))
    print(f"✓ Catalog valid: {len(items)} items, {enriched} enriched, {len(warnings)} warning(s).")
    for slot in sorted(by_slot):
        print(f"    {slot:10s} {by_slot[slot]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
