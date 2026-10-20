# Image Set Analyse

These tools analyse the selected, trimmed frame list in the Timelapse panel.
Choose a tool and press **Go**, then click the preview to inspect the complete
PNG. The description below the menu explains what each tool reveals.

| Tool | Use |
| --- | --- |
| `daygrid` | Compare capture days on the same midnight-to-midnight scale. Dates run across and UTC time runs down; partial days keep their correct position. Grey areas show gaps and salmon areas mark unreadable sampled images. |
| `filesize` | Find transitions and unusual files in a file-size timeline. Sizes are in MiB (1,048,576 bytes), with a median reference. |
| `filesizedistribution` | Compare file-size groups. A valley between groups can suggest a cutoff for separating light and dark captures; file size is only a proxy for lighting. |
| `time` | Compare elapsed capture time against frame number to spot breaks, cadence changes and images out of order. |
| `timediff` | Inspect the interval since the previous frame, including duplicates, backwards timestamps and unusually long gaps. The median positive interval is descriptive, not an assumed camera schedule. |
| `colourswatch` | Compare compressed full-image strips with vertical detail and a mean-colour strip. Magenta marks unreadable images; grey means no readable image in that strip. |
| `colorgraph` | Compare normalized red, green and blue intensity. Each panel shows the mean and the 10th–90th pixel percentiles, estimated from thumbnails. These replace the old dominant-colour totals and allow comparison across different image dimensions. |
| `brightness` | Inspect weighted RGB brightness and the proportion of thumbnail pixels near black or white. This helps locate day/night transitions and exposure changes. |

Frame numbers start at **1** and retain the supplied set order. Missing files or
unknown timestamps keep their positions as gaps; time differences never bridge
an unknown timestamp. Dated tools read `_YYYYMMDDHHMMSS` or epoch suffixes
(including fractional seconds) from filenames. Epochs use UTC; compact dates
are interpreted as written. Modification times are not substituted because
downloading can change them.

All graphs have bounded output dimensions. Dense timelines use consecutive-frame
groups: a mean curve and vertical min–max ranges retain short spikes. Missing
values break the mean curve. Colourswatch processes every frame and averages
consecutive groups when necessary. Daygrid samples photographs to the available
output rows, wraps long sets into panels and caps inferred strip coverage at one
hour, so sparse photographs do not suggest continuous coverage. Daygrid notes
the number of undated files and unreadable sampled images. An exceptionally long
range of separate days can exceed its readable canvas limit; select a shorter
range in that case. The redundant `daygridGPT` experiment has been removed.

Colour and brightness tools decode small thumbnails sequentially, avoiding large
worker pools and full-resolution pixel arrays. Their values are estimates;
near-limit pixel percentages describe thumbnails rather than a full-resolution
clipping measurement. Source images close after each read.

Processing uses a snapshot of the frame selection. Each run writes a fresh
temporary PNG, which is checked before display. If setup, processing or display
fails, a message explains the error, the last successful preview remains
available, and **Go** and the menu are enabled again. Failed and superseded
temporary outputs are removed. Tools raise a clear error when no usable input
is available.

Run the focused regression suite without a Pi or display:

```sh
python3 -m unittest discover -s scripts/gui/tests -p 'test_timelapse_*.py' -v
```

The panel workflow tests require wxPython; rendering tests require Pillow,
NumPy and Matplotlib. Tests cover partial days, corrupt files, timestamp gaps,
one-frame sets, dense sets and failure recovery.
