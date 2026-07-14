#!/usr/bin/env python3
"""Print a Python "usage script" describing the contents of one NWB file.

This wraps ``get_nwbfile_usage_script`` from the ``get-nwbfile-info`` package.
The usage script it prints enumerates the neurodata objects inside the NWB file
(their paths, types, shapes, columns, sampling rates, ...) together with ready
Python snippets showing how to open the remote file and read each object.

The usage script is a REFERENCE FOR YOU (the agent), not something to paste to
the user. Read it to learn what the file contains and how to load each piece,
then write your own focused, self-contained Python (see
``reference/nwb-python-guide.md``).

Usage:
    python3 nwbfile_info.py <dandiset_id> <version> <asset_path>
    python3 nwbfile_info.py --url <download_url>

Example:
    python3 nwbfile_info.py 000402 0.230307.2132 \\
        sub-17797/sub-17797_ses-4-scan-7_behavior+image+ophys.nwb

Exit codes: 0 on success; 1 if the package is missing or the lookup fails.
Requires the ``get-nwbfile-info`` package (see scripts/check_deps.py).

NOTE: this file is deliberately NOT named ``get_nwbfile_info.py`` so it does not
shadow the installed ``get_nwbfile_info`` package on ``sys.path``.
"""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the get-nwbfile-info usage script for an NWB file.",
    )
    parser.add_argument("dandiset_id", nargs="?", help="Dandiset ID, e.g. 000402")
    parser.add_argument(
        "version",
        nargs="?",
        help="Dandiset version, e.g. draft or 0.230307.2132",
    )
    parser.add_argument(
        "asset_path",
        nargs="?",
        help="Path of the .nwb asset within the dandiset",
    )
    parser.add_argument(
        "--url",
        help="A direct NWB download URL instead of dandiset id/version/path.",
    )
    args = parser.parse_args()

    if args.url:
        spec = args.url
    elif args.dandiset_id and args.version and args.asset_path:
        # The get-nwbfile-info package understands this "DANDI:" locator form.
        spec = f"DANDI:{args.dandiset_id}:{args.version}:{args.asset_path}"
    else:
        parser.error(
            "provide either <dandiset_id> <version> <asset_path>, or --url URL"
        )
        return 1

    try:
        from get_nwbfile_info import get_nwbfile_usage_script
    except ImportError:
        print(
            "error: the 'get-nwbfile-info' package is not installed.\n"
            "Install it with:\n"
            "    pip install git+https://github.com/rly/get-nwbfile-info\n"
            "Do NOT invent usage information if it is missing.",
            file=sys.stderr,
        )
        return 1

    try:
        usage_script = get_nwbfile_usage_script(spec)
    except Exception as e:  # noqa: BLE001 - surface any lookup/parse failure
        print(f"error: failed to build usage script for {spec}: {e}", file=sys.stderr)
        return 1

    print("```python")
    print(usage_script)
    print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
