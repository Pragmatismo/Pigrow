# Stylized Set (new)

In the Timelapse panel, select the frames to use and click **Stylized Set (new)**
below the existing **Stylized Set** button. The experimental builder opens a
separate, modeless window. The original dialog and effect modules are unchanged.

Choose a preset at the top, adjust its layers, and save a new named preset to
reuse the settings. Built-in presets are kept intact; save edited versions under
a different name. Custom presets live in the user's Pigrow configuration folder,
so they remain writable in packaged installations.

The initial preview is the **second output frame**, after processing the first
two inputs in order. **Next frame** generates one more static preview with the
same accumulated history. **Reset preview**, a preset change or a settings change
restarts from the second frame. A one-image selection previews its only frame.
Preview processing runs in a worker and never plays automatically. Previews use
up to 640px, capped by the chosen output size, so fine detail and thresholds may
look different from larger exports. Export processing uses the same engine.

## Layers

Layers are applied in the listed order, starting at the top of the list. Each
layer has its own history. Add, duplicate, remove or move layers, or disable them
temporarily. With no enabled layers, the selected base image is the output.

| Control | Meaning |
| --- | --- |
| Base image | Start each output with the current input, first input, black or white. |
| Source | Copy the input; extract its absolute difference from the previous or first input; keep current pixels where they changed; or extract edges. References always use original input images. |
| Persistence | Apply only to this frame, accumulate on a permanent canvas, or retain a finite ghost trail. |
| Blend | Combine using normal alpha blending, clamped addition, wraparound addition, screen, lighten, multiply or difference. The same blend combines contributions within a history and applies that layer to the base. |
| Opacity | For frame/permanent modes, set the strength of the completed layer. For a ghost trail, set each retained contribution's opacity before blending it into the trail. Lower this below 100% to see older normal-blend copies through newer ones. |
| Threshold | Ignore small differences or faint edges, measured on the original 0–255 intensity scale before gain. Copy ignores this control. |
| Gain | Amplify the extracted source. |
| Trail length | Keep this many input positions, including the current frame. Even unchanged frames age the trail. |
| Trail decay | Multiply older contributions by this factor for each frame of age. 100% retains their strength; 0% keeps only the current contribution. Permanent canvases never fade. |
| Tint / invert | Optionally recolour the source from its luminance or invert its colours before blending. Masks still exclude unchanged regions. |
| Output longest edge | Use 0 for original dimensions or 128–4096px to reduce output size. Mixed-size inputs are normalized to the first image's oriented dimensions. Images are not enlarged beyond that size by this control. |

The first frame has no previous-frame difference. It still produces an output.
An **Accumulated difference** preset uses the first image as its base and adds
permanent previous-frame differences with wraparound addition. Later frames
match the old difflayer arithmetic at the same resolution; the new set also
includes its first input frame.

Other built-ins offer changed-pixel accumulation, motion ghosts, light painting,
neon motion and layered RGB trails. Built-ins use a 1920px maximum as a practical
starting point. You can change this and save your own original-resolution preset.
Long trails and multiple layers consume memory; the renderer checks an estimated
512MiB budget and reports how to reduce it before allocating an oversized history.

## Export

Choose an existing **output parent folder** and an **image set name** consisting
of 1–64 letters, numbers or hyphens. A fresh subfolder with that name is created.
Existing folders and images are never overwritten. The selected frame paths and
settings are copied when the export starts, so editing the builder or selecting
another set in the main GUI does not change that job.

**Create image set** opens an independent progress window showing the number of
completed images. You can minimize it and continue using the GUI. Closing an
active progress window minimizes it so its cancel button remains accessible.
**Cancel export** requests cancellation after the current image operation; every
completed PNG is kept. A corrupt input or storage error reports the frame and
keeps earlier completed images. Closing the builder does not stop an export.
Closing the application requests cancellation of running jobs.

Use **Use this set (all frames)** after completion, or **Use partial set** after
cancellation/failure. This loads every completed image and clears the source's
frame filters so the exported selection is not trimmed a second time. Frame
selection includes both the first and last positions. FPS and render settings
stay available for rendering the new set.

PNG names contain a padded sequence index and retain valid source timestamp
suffixes, including fractional epochs and compact dates. This preserves frame
order and duplicate timestamps while keeping time analyses useful. Unknown
capture times stay explicitly undated; the Timelapse panel displays them without
inventing dates. Active time/date filters cannot match undated images.
The hidden `.pigrow-stylized.json` file records the settings and completed,
cancelled or failed state of an export.

## Reuse and checks

The engine (`stylized_sets.py`), presets (`stylized_presets.py`) and export/preview
jobs (`stylized_jobs.py`) have no wx dependency. A future camera-panel entry point
can supply image paths, settings and a completion callback to the same builder.

Headless processing tests:

```sh
python3 -m unittest discover -s scripts/gui/tests -p 'test_stylized_sets.py' -v
python3 -m unittest discover -s scripts/gui/tests -p 'test_stylized_jobs.py' -v
python3 -m unittest discover -s scripts/gui/tests -p 'test_stylized_presets.py' -v
```

Dialog and Timelapse integration tests require wxPython and a display; they use
temporary images and a fake main window, without a Pi or camera connection.
