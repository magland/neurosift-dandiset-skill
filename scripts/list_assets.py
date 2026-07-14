#!/usr/bin/env python3
"""List the assets (files) in a dandiset via the DANDI REST API.

Queries https://api.dandiarchive.org directly, so it needs only the Python 3
standard library and outbound HTTPS (no dandi/pynwb import). By default it lists
``.nwb`` files and paginates through the whole dandiset up to ``--max``.

Usage:
    python3 list_assets.py <dandiset_id> [version] [options]

Options:
    --glob GLOB      Glob passed to the API (default: "*.nwb"; "" for all).
                     DANDI globs match across "/", so "*.nwb" finds nested files.
    --max N          Stop after N assets (default: 100).
    --page-size N    API page size (default: 100).
    --json           Print the raw list of {asset_id, path, size} as JSON.

Version defaults to "draft" if omitted.
Exit codes: 0 on success, 1 on a transport/HTTP failure.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.dandiarchive.org/api"


def human_size(n: int) -> str:
    step = 1024.0
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < step:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= step
    return f"{n:.1f} PB"


def fetch_page(dandiset_id, version, glob, page, page_size):
    query = urllib.parse.urlencode(
        {
            "page": page,
            "page_size": page_size,
            "metadata": "false",
            "zarr": "false",
            "glob": glob,
        }
    )
    url = f"{API}/dandisets/{dandiset_id}/versions/{version}/assets/?{query}"
    request = urllib.request.Request(url, headers={"accept": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="List assets in a dandiset.")
    parser.add_argument("dandiset_id", help="Dandiset ID, e.g. 000402")
    parser.add_argument("version", nargs="?", default="draft", help="Version (default: draft)")
    parser.add_argument("--glob", default="*.nwb", help='Glob filter (default "*.nwb")')
    parser.add_argument("--max", type=int, default=100, help="Max assets to list")
    parser.add_argument("--page-size", type=int, default=100, help="API page size")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    assets = []
    page = 1
    total = None
    try:
        while len(assets) < args.max:
            data = fetch_page(
                args.dandiset_id, args.version, args.glob, page, args.page_size
            )
            total = data.get("count", total)
            results = data.get("results", [])
            if not results:
                break
            for r in results:
                assets.append(
                    {
                        "asset_id": r.get("asset_id"),
                        "path": r.get("path"),
                        "size": r.get("size"),
                    }
                )
                if len(assets) >= args.max:
                    break
            if not data.get("next"):
                break
            page += 1
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        print(f"error: HTTP {e.code} from DANDI: {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"error: request failed: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(assets, indent=2))
        return 0

    if not assets:
        print(f"No assets matched glob {args.glob!r} in {args.dandiset_id}/{args.version}.")
        return 0

    for a in assets:
        size = human_size(a["size"]) if isinstance(a["size"], int) else "?"
        print(f"{size:>10}  {a['path']}")
    shown = len(assets)
    if total is not None and total > shown:
        print(f"\n… showing {shown} of {total} matching assets (raise --max for more).")
    else:
        print(f"\n{shown} asset(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
