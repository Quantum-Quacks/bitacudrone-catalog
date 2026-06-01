#!/usr/bin/env python3
"""Validate components_catalog.json (repo root). Exits non-zero on errors."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "components_catalog.json")
SCHEMA_VERSION = 3
SLOTS = {"frame","motor","esc","fc","vtx","camera","receiver","antenna","prop","battery"}
LOCALES = {"es","en","fr","de","it","pt","ja","zh-Hans","ko","nl","pl","ru"}

def main():
    data = json.load(open(CATALOG, encoding="utf-8"))
    errors, warnings = [], []
    if data.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")
    items = data.get("items", [])
    if not items: errors.append("items empty")
    seen = set()
    for it in items:
        w = it.get("id","?")
        for r in ("id","category","title"):
            if not it.get(r): errors.append(f"[{w}] missing {r}")
        if it.get("id") in seen: errors.append(f"duplicate id {it.get('id')}")
        seen.add(it.get("id"))
        if it.get("category") not in SLOTS: errors.append(f"[{w}] bad category {it.get('category')}")
        for loc in it.get("description", {}):
            if loc not in LOCALES: warnings.append(f"[{w}] locale {loc}")
        for link in it.get("buyLinks", []):
            if "price" in link: errors.append(f"[{w}] buyLinks must not carry a price")
            if not link.get("url"): errors.append(f"[{w}] buyLink missing url")
    for x in warnings: print("WARN", x)
    for e in errors: print("ERR ", e)
    if errors:
        print(f"\nInvalid: {len(errors)} error(s)."); sys.exit(1)
    print(f"Valid: {len(items)} items, {len(warnings)} warning(s).")

if __name__ == "__main__": main()
