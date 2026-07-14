# Loading and visualizing NWB data from DANDI (Python)

This is the authoritative guide for the code you write when exploring a
dandiset. You (the agent) run Python directly with your Bash tool. NWB files are
**streamed over the network** from the DANDI Archive — you never download them
whole — so loading discipline matters.

**Work in the open.** Write each script to a `.py` file in the working directory
`dandiset_exploration/<id>_<version>/`, save plots as `.png` there, and give the
user clickable links to both — so they can open exactly what you ran and saw.
See SKILL.md → "Working directory". The examples below use `WORK/` as shorthand
for that folder.

## The golden rule: inspect before you load

**Never write code to load data from an NWB file until you have run
`scripts/nwbfile_info.py` for that file.** Its usage script tells you the exact
neurodata objects present, their paths, shapes, dtypes, and how to reach them.
Guessing paths wastes network round-trips and usually fails.

The usage script is a **reference for you, not output for the user.** Do not
paste it into your reply. Read it, then write your own focused code.

Treat the usage script as a strong hint, not gospel. pynwb sometimes resolves an
attribute to a plain `h5py.Dataset` where the script's nesting suggests an
object. If an access like `x.timestamps.data[:]` raises `AttributeError`, try
the attribute directly (`x.timestamps[:]`). Always confirm shapes at runtime.

## Opening a remote NWB file

```python
import pynwb, h5py, remfile
from dandi.dandiapi import DandiAPIClient

client = DandiAPIClient()
dandiset = client.get_dandiset("000402", "0.230307.2132")
path = "sub-17797/sub-17797_ses-4-scan-7_behavior+image+ophys.nwb"
url = dandiset.get_asset_by_path(path).download_url

remote_file = remfile.File(url)
h5_file = h5py.File(remote_file)
io = pynwb.NWBHDF5IO(file=h5_file)
nwb = io.read()
```

`asset.size` gives the file size in bytes. `dandiset.get_assets_by_glob("*.nwb")`
returns an iterator — respect it for large dandisets rather than materializing a
full list. (For a quick file listing without pynwb, use `scripts/list_assets.py`.)

## Each run is a fresh process

Every `python3 ...` invocation starts a brand-new interpreter — there is no
shared state between runs, exactly like a fresh Jupyter kernel. **Every script
you run must be fully self-contained**: re-open the NWB file, re-import
everything. You cannot pick up where a previous script left off.

## Subset-loading discipline (important)

Datasets are streamed. Reading a whole array can mean pulling gigabytes.

- Load only the slice you need: `data[:2000]`, `data[start:stop, :4]`.
- **Never** load all timestamps just to take a subset. Load the matching slice:
  use `ts.timestamps[i0:i1]`, not `ts.timestamps[:]` unless you truly need all.
- When you show a subset, **say so** in your summary (e.g. "first 2000 of
  104,227 samples") so the user does not mistake it for the whole recording.
- Do not subsample silently when the user asked for a full picture; instead
  explain the size trade-off.

## h5py gotchas

- You **cannot** index an `h5py.Dataset` with a NumPy array of indices
  (fancy-indexing). Slice with plain ranges, or read then index in memory.
- You **cannot** call `np.sum`/`np.mean`/etc. directly on an `h5py.Dataset`.
  Materialize first: `arr = dataset[:]; arr.sum()`.
- `import numpy as np` — don't forget it.

## Domain specifics

- **Spike times:** the spike times for unit *i* are
  `nwb.units.spike_times_index[i]` (a vector of times). Despite the name it is
  **not** an index into anything. Do **not** use `nwb.units.spike_times`.
- **IDs vs indices:** when showing unit or channel IDs, use the real IDs
  (`nwb.units.id[:]`, electrode table `id`), not positional indices.
- **Image masks** (ophys) have values in [0, 1]. To show many masks at once,
  superimpose with a max-projection heatmap: `np.max(np.stack(masks), axis=0)`.
- **Raw extracellular ephys:** do **not** attempt spike detection or spike
  sorting in a script — it is far too computationally intensive and needs heavy
  offline processing. Just load a reasonable window and visualize the traces.

## Plotting (headless) and viewing the result

Your environment has no display, so use a file-based workflow:

```python
import matplotlib
matplotlib.use("Agg")            # headless backend; set before pyplot import
import matplotlib.pyplot as plt
# ... build the figure ...
plt.savefig("WORK/plot.png", dpi=100)   # WORK = dandiset_exploration/<id>_<version>/
```

Then **Read the PNG** to actually look at it, and check for problems (empty axes,
wrong scale, all-NaN, mislabeled units) before describing it to the user. If it
is wrong, fix the code and re-run — iterate a few times as needed. Once it's
right, **give the user a markdown link** to the image (and to the script that
made it) so they can open it too.

- Default to `figsize` width ~10.
- For seaborn styling use `import seaborn as sns; sns.set_theme()`.
  `plt.style.use('seaborn')` is deprecated. Do **not** use seaborn styling for
  image/heatmap plots.
- Save plots into the working directory (`dandiset_exploration/<id>_<version>/`),
  where the user can open them — not a temp dir.

## Neurosift links

The **first time** you mention a given `.nwb` file, give the user a Neurosift
link so they can browse it interactively:

```
[<label>](https://neurosift.app/nwb?dandisetId=<id>&dandisetVersion=<version>&path=<asset_path>)
```

Choose a readable label (e.g. the file name).

## Worked example: load a subset and plot it

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pynwb, h5py, remfile
from dandi.dandiapi import DandiAPIClient

client = DandiAPIClient()
dandiset = client.get_dandiset("000402", "0.230307.2132")
path = "sub-17797/sub-17797_ses-4-scan-7_behavior+image+ophys.nwb"
url = dandiset.get_asset_by_path(path).download_url
nwb = pynwb.NWBHDF5IO(file=h5py.File(remfile.File(url))).read()

ts = nwb.acquisition["PupilTracking"].time_series["pupil_major_radius"]
n = 2000                          # subset of 104,227 samples
y = ts.data[:n]
t = ts.timestamps[:n]             # .timestamps is itself the Dataset here

plt.figure(figsize=(10, 4))
plt.plot(t, y, lw=0.7)
plt.xlabel("time (s)"); plt.ylabel(f"pupil major radius ({ts.unit})")
plt.title("pupil_major_radius (first 2000 samples)")
plt.tight_layout()
plt.savefig("WORK/pupil.png", dpi=100)   # WORK = dandiset_exploration/000402_0.230307.2132/
print("y", y.shape, "t", float(t[0]), "->", float(t[-1]))
```

## Worked example: spike raster for a few units

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pynwb, h5py, remfile
from dandi.dandiapi import DandiAPIClient

client = DandiAPIClient()
dandiset = client.get_dandiset("<id>", "<version>")
url = dandiset.get_asset_by_path("<path>.nwb").download_url
nwb = pynwb.NWBHDF5IO(file=h5py.File(remfile.File(url))).read()

unit_ids = nwb.units.id[:]                     # real IDs, not indices
plt.figure(figsize=(10, 5))
for row, uid in enumerate(unit_ids[:10]):      # first 10 units
    st = nwb.units.spike_times_index[row]      # spike times for this unit
    st = st[st < 60.0]                         # first 60 s only
    plt.vlines(st, row + 0.5, row + 1.5, lw=0.5)
plt.yticks(range(1, 11), [str(u) for u in unit_ids[:10]])
plt.xlabel("time (s)"); plt.ylabel("unit ID")
plt.title("Spike raster (first 10 units, first 60 s)")
plt.tight_layout()
plt.savefig("WORK/raster.png", dpi=100)   # WORK = dandiset_exploration/<id>_<version>/
```
