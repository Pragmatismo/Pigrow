# Timelapse datawalls

These use the GUI's Datawall tab and the same presets used by automatic datawall
creation on connection. Update both the desktop GUI and the connected Pigrow:
the GUI runs the datawall modules locally and runs `info_timelapse.py` on the Pi.
The info module uses only Python's standard library; the detailed wall uses the
GUI's existing Pillow and matplotlib dependencies.

## Create a wall

1. In **Datawall**, select module **timelapse_fast** or **timelapse_detailed**.
2. Choose a preset: **timelapse_fast**, **timelapse_detailed** (recent images),
   **timelapse_hourly**, or **timelapse_daily_1700**.
3. Adjust the import settings, then click **Import Data** and **Create Datawall**.
   Import again after changing the capture folder, timing, or gallery settings.
4. Save the preset to keep your settings. Select that saved preset in the start
   tab's datawall controls to use it automatically when connecting to the Pi.

Fast mode reads file metadata and reports recording status, including actual
versus expected captures. It does not download photos or create a graph.
Detailed mode adds a file-size graph over capture time, a large latest capture,
and a row of five comparison images. Only the selected photos are downloaded;
the complete capture directory stays on the Pi. An image shared by the latest
view and comparison row is downloaded once.

## Import settings

| Setting | Meaning |
| --- | --- |
| `capture_path` | Remote capture folder. `auto` reads `caps_path` from the Pi's `~/Pigrow/config/dirlocs.txt`, falling back to `~/Pigrow/caps`. |
| `interval` | Expected capture interval in **seconds**, or `auto` to read an active camera cron job for this folder. |
| `start` | Recording start as an ISO date/time or Unix timestamp. `auto` starts the comparison at the first observed capture. |
| `gallery_mode` | Detailed mode: `recent`, `hourly`, or `daily`. |
| `daily_time` | Detailed daily target, such as `1700` or `17:00`. |

Photo labels and daily/hourly targets use the connected Pi's local time; graph
axes are labelled in UTC. An explicit
start is useful when the beginning of a recording contains missing frames, or
when a folder holds captures from several recording sessions. Counts cover that
start through the time the info module runs, so a recording that has stopped
continues to accumulate missing expected captures.

With `interval=auto`, expected counts use the matching camera cron schedule.
If a usable schedule cannot be identified, the report shows the expected count
as unknown and explains why. It does not infer a healthy recording cadence from
the files already present. Set an explicit interval for quick timelapses or
recorders outside cron. Counts based on `start=auto` cannot identify captures
missing before the first surviving image.

The metadata scan accepts image files directly in the selected folder, without
opening their contents. Pigrow's `cap_<Unix timestamp>` filenames supply capture
times; other filenames use modification time. Subdirectories and non-image
files are ignored. File-size data can reveal unusual captures, but metadata
alone cannot establish whether an image is visually correct.

## Comparison images

- **Recent:** the five newest images, newest first. This includes the latest
  image also shown large.
- **Hourly:** images nearest the five most recent elapsed hour marks. Missing
  periods remain empty instead of reusing an unrelated old image. Each hour
  mark uses a window from 30 minutes before to 30 minutes after the target,
  limited to images already captured. Targets follow elapsed hours through
  daylight-saving changes; timezone labels distinguish repeated hour marks.
- **Daily:** images nearest the selected time on each of the five most recent
  dates whose target time has passed. For example, before 17:00, the 17:00 daily
  sequence starts with yesterday. Selection stays within each target's date.

Each slot labels the requested target and the actual capture time. Sparse
recordings, missing downloads, and unreadable images show placeholders. The
latest large image is independent of the comparison mode.

## Extension points

The implementation lives in `datawall_modules/datawall_timelapse_fast.py`,
`datawall_modules/datawall_timelapse_detailed.py`, their `timelapse_tools.py`
helper, `info_modules/info_timelapse.py`, and the four `datawall_presets` files.

Two additive importer features in `panels/datawall_pnl.py` support this:

- A module's `preset_req["settings"]` defines import controls using the existing
  dynamic options panel. Presets persist these as `setting:<name>=<value>`.
  Named placeholders in info requests are replaced by shell-quoted setting
  values. The unexpanded request remains the key in `data["info"]`.
- An info module may return JSON containing `datawall_images`, a mapping of
  image keys to `{ "path": ..., "size": ..., "mtime": ... }` or null. The
  importer downloads these into `data["images"]`, caches by remote path and
  metadata, and records individual failures in `data["image_errors"]`.

Existing text info modules, picture requests, graph presets, and log presets
continue to use their current formats. The start panel uses these additions
through its existing call to `create_datawall_data()`.

## Verification

Run the GUI test suite with wxPython, Pillow, matplotlib, and a display:

```sh
python3 -m unittest discover -s scripts/gui/tests -v
```

On a headless Linux machine, prefix this command with `xvfb-run -a`. Tests use
synthetic captures and simulated SSH/SFTP, including all four presets through
the automatic import/render path. They do not require a camera or connected Pi.
