#!/usr/bin/env python3
"""Fetch and summarize a dandiset's metadata from the DANDI REST API.

Needs only the Python 3 standard library and outbound HTTPS. Prints an overview
(title, description, keywords, contributors, license, file counts, size) that is
a good first orientation for a dandiset. Use ``--json`` for the raw metadata.

Usage:
    python3 dandiset_info.py <dandiset_id> [version]

Version defaults to "draft" if omitted.
Exit codes: 0 on success, 1 on a transport/HTTP failure.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

API = "https://api.dandiarchive.org/api"


def human_size(n) -> str:
    if not isinstance(n, (int, float)):
        return "?"
    step = 1024.0
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < step:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= step
    return f"{n:.1f} PB"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize dandiset metadata.")
    parser.add_argument("dandiset_id", help="Dandiset ID, e.g. 000402")
    parser.add_argument("version", nargs="?", default="draft", help="Version (default: draft)")
    parser.add_argument("--json", action="store_true", help="Print raw metadata JSON")
    args = parser.parse_args()

    url = f"{API}/dandisets/{args.dandiset_id}/versions/{args.version}/"
    request = urllib.request.Request(url, headers={"accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        print(f"error: HTTP {e.code} from DANDI: {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"error: request failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    # The version endpoint returns the Dandiset metadata fields at the top
    # level; fall back to a nested "metadata" object for other API shapes.
    meta = data.get("metadata") or data
    summary = meta.get("assetsSummary", {}) or {}

    print(f"# {meta.get('name') or data.get('name') or '(untitled)'}")
    print(f"DANDI:{args.dandiset_id} version {args.version}")
    print(f"https://dandiarchive.org/dandiset/{args.dandiset_id}/{args.version}")
    print()

    desc = meta.get("description")
    if desc:
        print("## Description")
        print(desc.strip())
        print()

    contributors = []
    for c in meta.get("contributor", []) or []:
        name = c.get("name") if isinstance(c, dict) else None
        if name:
            contributors.append(name)
    if contributors:
        shown = ", ".join(contributors[:15])
        more = "" if len(contributors) <= 15 else f", … (+{len(contributors) - 15} more)"
        print(f"Contributors: {shown}{more}")

    keywords = meta.get("keywords") or []
    if keywords:
        print(f"Keywords: {', '.join(keywords)}")

    measures = [
        m.get("name")
        for m in (summary.get("measurementTechnique") or [])
        if isinstance(m, dict) and m.get("name")
    ]
    if measures:
        print(f"Measurement techniques: {', '.join(measures)}")

    species = [
        s.get("name")
        for s in (summary.get("species") or [])
        if isinstance(s, dict) and s.get("name")
    ]
    if species:
        print(f"Species: {', '.join(species)}")

    lic = meta.get("license")
    if lic:
        print(f"License: {', '.join(lic) if isinstance(lic, list) else lic}")

    n_files = summary.get("numberOfFiles")
    n_bytes = summary.get("numberOfBytes")
    print(
        f"Assets: {data.get('asset_count') or n_files or '?'} files, "
        f"{human_size(n_bytes)} total"
    )
    print()
    print("Use scripts/list_assets.py to list the NWB files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
