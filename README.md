# neurosift-dandiset skill

A [Claude Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) for
**deep-diving a single dandiset** on the [DANDI Archive](https://dandiarchive.org).
It gives Claude the capabilities of the
[Dandiset Explorer](https://github.com/dandi-ai-notebooks/dandiset-explorer):
read a dandiset's metadata, list its NWB files, inspect what data is inside a
given NWB file, and **load, visualize, and analyze that data in Python** by
streaming the remote NWB files (pynwb + h5py + remfile).

Unlike the hosted Dandiset Explorer app, this skill runs Python **locally** via
Claude's Bash tool — no server or API key. It only needs Python 3 with the
scientific NWB stack installed (see below).

## The Neurosift skill family

This is one of three Claude skills that work together for neuroscience data on
the DANDI Archive (and, for search, OpenNeuro / EBRAINS). Install whichever you
need — they complement each other:

- **[neurosift-datasets](https://github.com/magland/neurosift-datasets-skill)** —
  find, filter, rank, and count datasets **across** DANDI, OpenNeuro, and
  EBRAINS, and check which neurodata types a file has. *Discovery across many
  datasets.*
- **[neurosift-dandiset](https://github.com/magland/neurosift-dandiset-skill)**
  *(this skill)* — deep-dive a **single** dandiset or NWB file and load /
  visualize / analyze its data in Python by streaming the remote file. *Depth on
  one file.*
- **[neurosift-links](https://github.com/magland/neurosift-links-skill)** — build
  **neurosift.app** URLs that open a dandiset, an NWB file, or a specific
  object/visualization in the interactive web viewer. *Clickable views to share.*

Typical flow: **datasets** → **dandiset** → **links** (discover, then analyze,
then share an interactive view). Use this one to go deep on a dandiset you
already have in hand.

## What it can do

- Summarize a dandiset's metadata (title, description, contributors, species,
  techniques, file/byte counts)
- List the NWB files in a dandiset (with glob filtering)
- Inspect one NWB file's contents — every neurodata object, its shape/type, and
  how to load it in Python (via the `get-nwbfile-info` usage script)
- Stream subsets of remote NWB data and produce plots and analyses
- Emit Neurosift links for interactive browsing

It saves the scripts it runs and the plots it makes into a
`dandiset_exploration/<id>_<version>/` folder in your workspace and links them in
chat, so you can open and inspect exactly what the agent ran and saw.

Example prompts:

- "Tell me about Dandiset 000402 version 0.230307.2132."
- "List the NWB files in 001333 and load pupil data from one of them."
- "Plot a spike raster for the first 10 units in this NWB file."

## Requirements

Python 3 plus: `numpy`, `matplotlib`, `h5py`, `remfile`, `pynwb`, `dandi`, and
[`get-nwbfile-info`](https://github.com/rly/get-nwbfile-info) (installs from
GitHub, not PyPI). Check and install with:

```bash
python3 scripts/check_deps.py                 # report what's present/missing
python3 -m pip install -r requirements.txt    # install everything
```

The skill checks dependencies at the start and, if any are missing, asks before
installing (or gives you the command to run yourself).

## Install

**As a personal skill (all your Claude Code sessions):**

```bash
git clone https://github.com/magland/neurosift-dandiset-skill ~/.claude/skills/neurosift-dandiset
```

**As a project skill (one repo):**

```bash
git clone https://github.com/magland/neurosift-dandiset-skill \
  /path/to/your/project/.claude/skills/neurosift-dandiset
```

The directory name must be `neurosift-dandiset` (it matches the skill's `name`).
Claude loads the skill automatically when a dandiset question is relevant.

## Contents

| Path | Purpose |
|------|---------|
| `SKILL.md` | Skill definition + the procedure Claude follows |
| `reference/nwb-python-guide.md` | Loading remote NWB in Python: recipe, subset discipline, gotchas, plotting, worked examples |
| `reference/dandi-api.md` | DANDI REST API shapes, metadata fields, asset listing, URLs, link formats |
| `scripts/check_deps.py` | Report present/missing packages + install command |
| `scripts/dandiset_info.py` | Summarize a dandiset's metadata |
| `scripts/list_assets.py` | List `.nwb` assets in a dandiset |
| `scripts/nwbfile_info.py` | Print the usage script describing one NWB file's contents |
| `requirements.txt` | Python dependencies |

## Use the scripts directly (without Claude)

```bash
python3 scripts/dandiset_info.py 000402 0.230307.2132
python3 scripts/list_assets.py   000402 0.230307.2132 --max 5
python3 scripts/nwbfile_info.py  000402 0.230307.2132 \
  "sub-17797/sub-17797_ses-4-scan-7_behavior+image+ophys.nwb"
```

## How it works

DANDI metadata and asset listings come from the public DANDI REST API
(`api.dandiarchive.org`). NWB file inspection uses the `get-nwbfile-info`
package, which reads an NWB file's HDF5 structure (over the network, via range
requests) to generate a Python usage script. Data loading and plotting use
`pynwb` + `h5py` + `remfile` to stream just the requested slices of a remote
file. Everything runs in the local Python environment.
