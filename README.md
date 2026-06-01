# bitacudrone-catalog

Offline-first component catalog for **BitacuDrone** (FPV drone fleet logbook).
Single source of truth: `components_catalog.json` (`CatalogFile`, schemaVersion 3).

The app ships a bundled seed of this file and refreshes over the air via
jsDelivr against an immutable tag — **no App Store release needed** to update
catalog data.

```
https://cdn.jsdelivr.net/gh/<owner>/bitacudrone-catalog@v1/components_catalog.json
```

## Rules
- `buyLinks` carry `{vendor, url, region}` and **never a price** (prices rot;
  use a live affiliate API instead).
- **Never** embed/hotlink manufacturer/retailer/Amazon photos — copyright.
  `image.remoteURL` must point to a licensed/own/affiliate image.
- Each item has localized `description` (12 languages); product titles are not
  translated.

## Contributing
Open a PR editing `components_catalog.json`. CI runs `validate_catalog.py`.
Maintainer merges and bumps the tag (`vN`) to publish.

## Validate locally
```bash
python3 validate_catalog.py
```
