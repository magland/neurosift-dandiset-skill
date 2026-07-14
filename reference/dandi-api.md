# DANDI Archive API reference

The DANDI REST API (`https://api.dandiarchive.org/api`) needs no auth for public
data. The helper scripts wrap the calls you need, but this documents the shapes
so you can go direct when useful.

## Dandiset identity

- **ID**: zero-padded 6-digit string, e.g. `000402`.
- **Version**: either `draft` (unpublished working version) or a published
  version like `0.230307.2132`. If the user gives only an ID, `draft` is the
  safe default; a published version is immutable.
- Web page: `https://dandiarchive.org/dandiset/<id>/<version>`

## Metadata

`scripts/dandiset_info.py <id> [version]` summarizes it; `--json` prints raw.

Endpoint: `GET /dandisets/<id>/versions/<version>/`

The Dandiset metadata fields are returned **at the top level** of the JSON (not
nested under a `metadata` key). Useful fields:

- `name` — title
- `description` — abstract (often long)
- `keywords` — string[] (often empty)
- `contributor` — array of `{ name, roleName, schemaKey, ... }`; people have
  `schemaKey == "Person"`
- `license` — e.g. `["spdx:CC-BY-4.0"]`
- `citation`, `doi`, `url`
- `assetsSummary` — `{ numberOfFiles, numberOfBytes, numberOfSubjects,
  species: [{name}], approach, measurementTechnique: [{name}],
  variableMeasured, dataStandard }`

## Listing assets (files)

`scripts/list_assets.py <id> [version] [--glob "*.nwb"] [--max N] [--json]`

Endpoint:
`GET /dandisets/<id>/versions/<version>/assets/?page=<p>&page_size=<n>&metadata=false&zarr=false&glob=<glob>`

- Response: `{ count, next, previous, results: [ { asset_id, path, size,
  created, modified, blob, zarr } ] }`.
- **Glob semantics:** DANDI's `glob` matches across `/`, so `*.nwb` finds
  deeply nested files (`sub-x/ses-y/file.nwb`). Use `""` for all assets.
- Only `.nwb` files are relevant for this skill.
- Some dandisets have thousands of files — page through, or narrow with a glob
  like `sub-01/*.nwb`; don't try to list everything at once.

## Getting an NWB file's download URL

Two equivalent ways:

```python
# via the dandi client (used in loading code)
url = dandiset.get_asset_by_path("<path>.nwb").download_url
```

```
# direct, from an asset_id (e.g. from list_assets.py --json)
https://api.dandiarchive.org/api/assets/<asset_id>/download/
```

## Links to give the user

- **Dandiset:** `https://dandiarchive.org/dandiset/<id>/<version>`
- **NWB file on Neurosift** (browse/visualize interactively) — give this the
  first time you mention a file:
  `https://neurosift.app/nwb?dandisetId=<id>&dandisetVersion=<version>&path=<asset_path>`
- Markdown form:
  `[<label>](https://neurosift.app/nwb?dandisetId=<id>&dandisetVersion=<version>&path=<asset_path>)`
