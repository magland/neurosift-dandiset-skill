#!/usr/bin/env python3
"""Check that the Python packages this skill needs are importable.

Prints an OK/MISSING line per package and, if anything is missing, the exact
commands to install it. Exit code is 0 when everything is present, 1 otherwise.

Per the skill's rules: if packages are missing, ASK the user before installing
anything, or give them these commands to run themselves. Do not silently
pip-install into their environment.
"""

import importlib.util
import sys

# (import name, pip install target)
REQUIRED = [
    ("numpy", "numpy"),
    ("matplotlib", "matplotlib"),
    ("h5py", "h5py"),
    ("remfile", "remfile"),
    ("pynwb", "pynwb"),
    ("dandi", "dandi"),
    ("get_nwbfile_info", "git+https://github.com/rly/get-nwbfile-info"),
]


def main() -> int:
    missing = []
    for import_name, pip_target in REQUIRED:
        present = importlib.util.find_spec(import_name) is not None
        print(f"{'OK     ' if present else 'MISSING'}  {import_name}")
        if not present:
            missing.append(pip_target)

    print()
    if not missing:
        print("All required packages are available.")
        return 0

    print(f"{len(missing)} package(s) missing. To install:")
    print()
    print(f"    {sys.executable} -m pip install {' '.join(missing)}")
    print()
    print("Ask the user before installing, or share the command above for them")
    print("to run. get-nwbfile-info installs from GitHub (not on PyPI).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
