"""Modeless layer editor and independent progress windows for styled image sets."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
import re
import time

import wx
from PIL import Image

from stylized_jobs import ExportJob, PreviewSession
from stylized_presets import builtin_presets, load_presets, save_preset
from stylized_sets import default_layer, default_settings, validate_settings


SOURCE_CHOICES = (
    ("Copy current image", "copy"),
    ("Difference from previous frame", "difference_previous"),
    ("Difference from first frame", "difference_first"),
    ("Changed pixels", "changed_pixels"),
    ("Edges", "edges"),
)
PERSISTENCE_CHOICES = (
    ("This frame only", "frame"),
    ("Permanent canvas", "permanent"),
    ("Ghost trail", "trail"),
)
BLEND_CHOICES = (
    ("Normal", "normal"),
    ("Add (clip)", "add"),
    ("Add (wrap / modulo)", "add_modulo"),
    ("Screen", "screen"),
    ("Lighten", "lighten"),
    ("Multiply", "multiply"),
    ("Difference", "difference"),
)
BASE_CHOICES = (
    ("Current frame", "current"), ("First frame", "first"),
    ("Black canvas", "black"), ("White canvas", "white"),
)
SOURCE_HELP = {
    "copy": "Copy the whole current image. Useful for colour washes and accumulated exposures.",
    "difference_previous": "Extract changes from the previous input image. The first image has no previous-frame difference.",
    "difference_first": "Extract changes from the first input image, which stays the same reference throughout the set.",
    "changed_pixels": "Keep the current image's changed pixels; threshold suppresses small changes from the previous frame.",
    "edges": "Extract image edges. Threshold removes faint edges; gain makes the remaining detail stronger.",
}
PERSISTENCE_HELP = {
    "frame": "This layer starts fresh for every image.",
    "permanent": "Keep this layer's canvas for the whole set; changes accumulate without fading.",
    "trail": "Keep only the selected number of recent frames. Decay makes older contributions fainter.",
}

# A progress window belongs to the main GUI, independently of its builder window.
_EXPORT_WINDOWS = set()


def _choice_value(control, choices):
    selected = control.GetSelection()
    if selected == wx.NOT_FOUND:
        raise ValueError("Choose a value from each options list.")
    return choices[selected][1]


def _select_value(control, choices, value):
    control.SetSelection(next((index for index, pair in enumerate(choices)
                               if pair[1] == value), 0))


def _render_preview(state, frames, settings, revision, index):
    """Only the single preview worker accesses or closes its stateful session."""
    if state.get("revision") != revision:
        previous = state.pop("session", None)
        if previous is not None:
            previous.close()
        state["session"] = PreviewSession(frames, settings, max_size=640)
        state["revision"] = revision
    try:
        return state["session"].preview(index)
    except Exception:
        session = state.pop("session", None)
        state.pop("revision", None)
        if session is not None:
            session.close()
        raise


def _close_preview_state(state):
    session = state.pop("session", None)
    if session is not None:
        session.close()


def _close_future_image(future):
    """A finished task after a window closes must not retain its image buffer."""
    try:
        image = future.result()
    except Exception:
        return
    image.close()


class ExportProgressFrame(wx.Frame):
    """A modeless, minimizable export monitor which retains partial results."""

    def __init__(self, parent, job, on_use_set=None):
        super().__init__(parent, title="Create stylized image set", size=(640, 340),
                         style=wx.DEFAULT_FRAME_STYLE)
        self.job = job
        self.on_use_set = on_use_set
        self._finished = False
        self._cancel_requested = False
        self._closed = False
        self._snapshot = {"status": "pending", "completed": 0, "total": 0,
                          "output_dir": "", "set_name": "", "error": ""}
        _EXPORT_WINDOWS.add(self)
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)
        self.status_text = wx.StaticText(panel, label="Preparing export…")
        self.count_text = wx.StaticText(panel, label="0 images processed")
        self.gauge = wx.Gauge(panel, range=1)
        self.path_text = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.detail_text = wx.StaticText(
            panel, label="You can minimize this window and keep using the GUI. "
                         "Cancel keeps every image already written.")
        self.detail_text.Wrap(590)
        for control in (self.status_text, self.count_text, self.gauge):
            layout.Add(control, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)
        layout.Add(wx.StaticText(panel, label="Output folder"), 0,
                   wx.LEFT | wx.RIGHT | wx.TOP, 12)
        layout.Add(self.path_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)
        layout.Add(self.detail_text, 1, wx.EXPAND | wx.ALL, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.minimize_button = wx.Button(panel, label="Minimize")
        self.use_button = wx.Button(panel, label="Use this set (all frames)")
        self.cancel_button = wx.Button(panel, label="Cancel export")
        self.use_button.Disable()
        self.minimize_button.Bind(wx.EVT_BUTTON, lambda event: self.Iconize(True))
        self.use_button.Bind(wx.EVT_BUTTON, self.on_use)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        buttons.Add(self.minimize_button, 0, wx.RIGHT, 7)
        buttons.AddStretchSpacer()
        buttons.Add(self.use_button, 0, wx.RIGHT, 7)
        buttons.Add(self.cancel_button, 0)
        layout.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(layout)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(outer)
        self.SetMinSize((520, 320))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_poll, self.timer)
        self.CentreOnParent()

    def start(self):
        self.Show()
        try:
            self.job.start()
            self.timer.Start(100)
            self.on_poll(None)
        except Exception as error:
            self._show_snapshot(dict(self._snapshot, status="failed", error=str(error)))

    def on_poll(self, event):
        if self._closed:
            return
        try:
            self._show_snapshot(self.job.snapshot())
        except Exception as error:
            self.job.cancel()
            self._show_snapshot(dict(self._snapshot, status="failed", error=str(error)))

    def _show_snapshot(self, snapshot):
        self._snapshot = dict(snapshot)
        completed = int(snapshot.get("completed", 0))
        total = int(snapshot.get("total", 0))
        status = snapshot.get("status", "pending")
        self.count_text.SetLabel("{:,} of {:,} images processed".format(completed, total))
        self.gauge.SetRange(max(total, 1))
        self.gauge.SetValue(min(completed, max(total, 1)))
        self.path_text.ChangeValue(snapshot.get("output_dir") or "Preparing output folder…")
        self._finished = status in ("completed", "cancelled", "failed")
        if status == "completed":
            message = "Image set created."
        elif status == "cancelled":
            message = "Export cancelled; {:,} completed images were kept.".format(completed)
        elif status == "failed":
            message = "Export failed; {:,} completed images were kept.".format(completed)
        elif self._cancel_requested:
            message = "Cancelling after the current image…"
        else:
            message = "Creating image set…"
        self.status_text.SetLabel(message)
        if self._finished:
            self.timer.Stop()
            self.cancel_button.SetLabel("Close")
            self.cancel_button.Enable()
            partial = status != "completed"
            self.use_button.SetLabel("Use partial set (all frames)" if partial else "Use this set (all frames)")
            self.use_button.Enable(bool(completed and snapshot.get("output_dir") and self.on_use_set))
            error = snapshot.get("error")
            detail = (str(error) + "\n" if error else "") + (
                "The completed images remain in the folder above."
                if partial else "Use this set loads every completed PNG into the Timelapse panel and resets its frame filters.")
            self.detail_text.SetLabel(detail)
            self.detail_text.Wrap(max(450, self.GetClientSize().width - 40))
        self.Layout()

    def on_cancel(self, event):
        if self._finished:
            self.Close()
            return
        self._cancel_requested = True
        self.job.cancel()
        self.cancel_button.Disable()
        self.status_text.SetLabel("Cancelling after the current image…")

    def on_use(self, event):
        if not self._finished or not self.on_use_set or not self._snapshot.get("completed"):
            return
        try:
            self.on_use_set(self._snapshot["output_dir"], "png", self._snapshot["set_name"])
        except Exception as error:
            wx.MessageBox(str(error), "Could not load image set", wx.OK | wx.ICON_ERROR, self)

    def on_close(self, event):
        if not self._finished and event.CanVeto():
            # Keep the cancel control accessible while work continues.
            event.Veto()
            self.Iconize(True)
            return
        self._release()
        event.Skip()

    def _release(self):
        if self._closed:
            return
        self._closed = True
        _EXPORT_WINDOWS.discard(self)
        self.timer.Stop()
        if not self._finished:
            self.job.cancel()

    def Destroy(self):
        self._release()
        return super().Destroy()

    def on_destroy(self, event):
        if event.GetEventObject() is self:
            self._release()
        event.Skip()


class StylizedSetDialog(wx.Dialog):
    """Edit independent ordered layers and export a snapshot without blocking wx."""

    def __init__(self, parent, frames, output_parent="", preset_path=None, on_use_set=None):
        super().__init__(parent, title="Create stylized image set", size=(1180, 880),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER |
                               wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)
        self.frames = tuple(os.path.abspath(os.fspath(path)) for path in frames)
        self.preset_path = preset_path
        self.on_use_set = on_use_set
        self._settings = deepcopy(default_settings())
        self._selected_layer = 0 if self._settings.get("layers") else -1
        self._updating = False
        self._closed = False
        self._preview_generation = 0
        self._preview_revision = 0
        self._preview_index = -1
        self._preview_pending = None
        self._preview_future = None
        self._preview_task_generation = None
        self._preview_task_index = None
        self._preview_due = 0.0
        self._preview_state = {}
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="stylized-preview")
        self._presets = {}
        self._build_ui(output_parent or (os.path.dirname(self.frames[0]) if self.frames else ""))
        self._load_presets()
        self._refresh_settings()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_preview_poll, self.timer)
        self.timer.Start(70)
        display_index = wx.Display.GetFromWindow(parent) if parent else wx.NOT_FOUND
        area = wx.Display(max(display_index, 0)).GetClientArea()
        available_width, available_height = max(700, area.width - 36), max(520, area.height - 56)
        self.SetMinSize((min(980, available_width), min(660, available_height)))
        self.SetSize((min(1120, available_width), min(820, available_height)))
        self.CentreOnParent()
        self.queue_preview(reset=True, immediate=True)

    def _build_ui(self, output_parent):
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)
        presets = wx.BoxSizer(wx.HORIZONTAL)
        presets.Add(wx.StaticText(panel, label="Preset"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 7)
        self.preset_choice = wx.Choice(panel)
        self.save_preset_button = wx.Button(panel, label="Save preset…")
        self.preset_choice.Bind(wx.EVT_CHOICE, self.on_preset)
        self.save_preset_button.Bind(wx.EVT_BUTTON, self.on_save_preset)
        presets.Add(self.preset_choice, 1, wx.RIGHT, 7)
        presets.Add(self.save_preset_button, 0)
        layout.Add(presets, 0, wx.EXPAND | wx.ALL, 12)
        self.preset_status = wx.StaticText(panel, label="")
        layout.Add(self.preset_status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        body = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        left.Add(wx.StaticText(panel, label="Preview"), 0, wx.BOTTOM, 7)
        self.preview_panel = wx.Panel(panel, style=wx.BORDER_SUNKEN)
        self.preview_panel.SetBackgroundColour(wx.Colour(35, 38, 42))
        self.preview_panel.SetMinSize((340, 220))
        self.preview_bitmap = wx.StaticBitmap(self.preview_panel, bitmap=wx.Bitmap(1, 1))
        preview_layout = wx.BoxSizer(wx.VERTICAL)
        preview_layout.AddStretchSpacer()
        preview_layout.Add(self.preview_bitmap, 0, wx.ALIGN_CENTER_HORIZONTAL)
        preview_layout.AddStretchSpacer()
        self.preview_panel.SetSizer(preview_layout)
        left.Add(self.preview_panel, 1, wx.EXPAND)
        self.preview_status = wx.StaticText(panel, label="Preparing the second output image…")
        self.preview_status.Wrap(490)
        left.Add(self.preview_status, 0, wx.EXPAND | wx.TOP, 7)
        preview_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.next_button = wx.Button(panel, label="Next frame")
        self.reset_button = wx.Button(panel, label="Reset preview")
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        preview_buttons.Add(self.next_button, 0, wx.RIGHT, 7)
        preview_buttons.Add(self.reset_button, 0)
        left.Add(preview_buttons, 0, wx.TOP, 7)
        preview_note = wx.StaticText(panel, label="Preview processes frames in set order at up to 640 px. "
                                     "Full-size exports may show finer detail. Nothing plays automatically. "
                                     "For large images or long trails, export at 1920 px to use less memory.")
        preview_note.Wrap(490)
        left.Add(preview_note, 0, wx.EXPAND | wx.TOP, 8)
        base_grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=10)
        base_grid.AddGrowableCol(1, 1)
        self.base_choice = wx.Choice(panel, choices=[label for label, value in BASE_CHOICES])
        self.base_choice.SetToolTip("The background used before applying the ordered layers to each output.")
        self.max_size = wx.ComboBox(panel, choices=["0 (original)", "128", "256", "512", "640", "1024", "1920", "2048", "4096"])
        self.max_size.SetToolTip("Longest edge of exported images: 0 keeps original resolution; otherwise choose 128–4096 pixels.")
        for label, control in (("Base image", self.base_choice), ("Output longest edge (px)", self.max_size)):
            base_grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            base_grid.Add(control, 1, wx.EXPAND)
        self.base_choice.Bind(wx.EVT_CHOICE, self.on_base_change)
        self.max_size.Bind(wx.EVT_TEXT, self.on_base_change)
        left.Add(base_grid, 0, wx.EXPAND | wx.TOP, 12)
        body.Add(left, 1, wx.EXPAND | wx.RIGHT, 14)

        right_panel = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        right_panel.SetScrollRate(0, 14)
        right = wx.BoxSizer(wx.VERTICAL)
        right.Add(wx.StaticText(right_panel, label="Layers — applied in listed order"), 0, wx.BOTTOM, 6)
        self.layer_list = wx.ListBox(right_panel, size=(-1, 115), style=wx.LB_SINGLE)
        self.layer_list.Bind(wx.EVT_LISTBOX, self.on_select_layer)
        right.Add(self.layer_list, 0, wx.EXPAND)
        layer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.layer_buttons = {}
        for key, label, handler in (("add", "Add", self.on_add_layer),
                                    ("duplicate", "Duplicate", self.on_duplicate_layer),
                                    ("remove", "Remove", self.on_remove_layer),
                                    ("up", "Move up", self.on_layer_up),
                                    ("down", "Move down", self.on_layer_down)):
            button = wx.Button(right_panel, label=label, size=(80, -1))
            button.Bind(wx.EVT_BUTTON, handler)
            self.layer_buttons[key] = button
            layer_buttons.Add(button, 0, wx.RIGHT, 4)
        right.Add(layer_buttons, 0, wx.TOP | wx.BOTTOM, 7)

        self.layer_controls = {}
        grid = wx.FlexGridSizer(cols=2, vgap=6, hgap=9)
        grid.AddGrowableCol(1, 1)
        for key, label in (("name", "Layer name"), ("enabled", "Enabled"),
                           ("source", "Source"), ("persistence", "Persistence"),
                           ("blend", "Blend"), ("opacity", "Opacity (%)"),
                           ("threshold", "Threshold (0–255)"), ("gain", "Gain"),
                           ("trail_frames", "Trail length (frames)"), ("decay", "Trail decay (%)"),
                           ("tint", "Tint (#rrggbb; optional)"), ("invert", "Invert source")):
            if key in ("enabled", "invert"):
                control = wx.CheckBox(right_panel)
                control.Bind(wx.EVT_CHECKBOX, self.on_layer_change)
            elif key in ("source", "persistence", "blend"):
                choices = {"source": SOURCE_CHOICES, "persistence": PERSISTENCE_CHOICES, "blend": BLEND_CHOICES}[key]
                control = wx.Choice(right_panel, choices=[text for text, value in choices])
                control.Bind(wx.EVT_CHOICE, self.on_layer_change)
            elif key in ("opacity", "gain", "decay"):
                low, high, increment = (0.1, 8.0, 0.1) if key == "gain" else (0.0, 100.0, 1.0)
                control = wx.SpinCtrlDouble(right_panel, min=low, max=high, inc=increment)
                control.SetDigits(1)
                control.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_layer_change)
                control.Bind(wx.EVT_TEXT, self.on_layer_change)
            elif key in ("threshold", "trail_frames"):
                control = wx.SpinCtrl(right_panel, min=1 if key == "trail_frames" else 0,
                                      max=100 if key == "trail_frames" else 255)
                control.Bind(wx.EVT_SPINCTRL, self.on_layer_change)
                control.Bind(wx.EVT_TEXT, self.on_layer_change)
            else:
                control = wx.TextCtrl(right_panel)
                control.Bind(wx.EVT_TEXT, self.on_layer_change)
            self.layer_controls[key] = control
            grid.Add(wx.StaticText(right_panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        tooltips = {
            "enabled": "Temporarily skip this layer without removing its settings.",
            "blend": "How the layer combines with the image below it. Add wrap reproduces the older wraparound effect.",
            "opacity": "Layer strength: 0% is invisible. In a ghost trail this controls each retained contribution, so older copies can show through.",
            "threshold": "Ignore source changes or edges below this intensity; higher values remove more fine detail and noise.",
            "gain": "Multiply the extracted source before blending; 1.0 keeps its original strength.",
            "trail_frames": "Maximum number of recent contributions retained by a ghost trail.",
            "decay": "Strength retained per older trail frame: 100% keeps each contribution equally strong; 0% keeps only the newest.",
            "tint": "Optional colour for the source; leave blank to keep its original colours. Example: #ff8844.",
            "invert": "Invert the source colours before they enter the layer's canvas.",
        }
        for key, tooltip in tooltips.items():
            self.layer_controls[key].SetToolTip(tooltip)
        right.Add(grid, 0, wx.EXPAND)
        self.layer_help = wx.StaticText(right_panel, label="")
        self.layer_help.Wrap(440)
        right.Add(self.layer_help, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 9)
        right_panel.SetSizer(right)
        body.Add(right_panel, 1, wx.EXPAND)
        layout.Add(body, 1, wx.EXPAND | wx.ALL, 12)

        output_grid = wx.FlexGridSizer(cols=3, vgap=7, hgap=8)
        output_grid.AddGrowableCol(1, 1)
        self.output_parent = wx.TextCtrl(panel, value=output_parent)
        self.set_name = wx.TextCtrl(panel, value="stylized-set")
        self.set_name.SetToolTip("Use only letters, numbers and hyphens. A new folder is created; existing folders are never overwritten.")
        browse = wx.Button(panel, label="Browse…")
        browse.Bind(wx.EVT_BUTTON, self.on_browse)
        output_grid.Add(wx.StaticText(panel, label="Output parent folder"), 0, wx.ALIGN_CENTER_VERTICAL)
        output_grid.Add(self.output_parent, 1, wx.EXPAND)
        output_grid.Add(browse, 0)
        output_grid.Add(wx.StaticText(panel, label="Image set name"), 0, wx.ALIGN_CENTER_VERTICAL)
        output_grid.Add(self.set_name, 1, wx.EXPAND)
        output_grid.AddSpacer(1)
        layout.Add(output_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.validation_status = wx.StaticText(panel, label="")
        buttons.Add(self.validation_status, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self.create_button = wx.Button(panel, label="Create image set")
        self.cancel_button = wx.Button(panel, wx.ID_CANCEL, label="Close builder")
        self.create_button.Bind(wx.EVT_BUTTON, self.on_create)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close_button)
        buttons.Add(self.create_button, 0, wx.RIGHT, 8)
        buttons.Add(self.cancel_button, 0)
        layout.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(layout)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(outer)
        self.SetMinSize((980, 660))

    def _load_presets(self, select_name=None):
        try:
            self._presets = load_presets(path=self.preset_path)
            self.preset_status.SetLabel("")
        except Exception as error:
            self._presets = builtin_presets()
            self.preset_status.SetLabel("Could not load saved presets: {}. Built-in presets are still available.".format(error))
            self.preset_status.Wrap(1080)
        names = sorted(self._presets, key=str.casefold)
        self.preset_choice.Set(names)
        preferred = select_name or "Accumulated difference"
        if preferred not in self._presets:
            preferred = names[0] if names else None
        if preferred:
            self.preset_choice.SetStringSelection(preferred)
            self._settings = deepcopy(self._presets[preferred])
            self._selected_layer = 0 if self._settings.get("layers") else -1

    def _refresh_settings(self):
        self._updating = True
        try:
            _select_value(self.base_choice, BASE_CHOICES, self._settings["base"])
            maximum = self._settings["max_size"]
            self.max_size.SetValue(str(maximum) if maximum else "0 (original)")
            self._refresh_layer_list()
            self._load_layer_controls()
        finally:
            self._updating = False

    def _refresh_layer_list(self):
        layers = self._settings["layers"]
        self.layer_list.Set(["{}. {}{}".format(index + 1, layer.get("name") or "Layer", "" if layer["enabled"] else " (disabled)")
                             for index, layer in enumerate(layers)])
        if layers:
            self._selected_layer = min(max(self._selected_layer, 0), len(layers) - 1)
            self.layer_list.SetSelection(self._selected_layer)
        else:
            self._selected_layer = -1
        selected = self._selected_layer >= 0
        self.layer_buttons["add"].Enable(len(layers) < 16)
        self.layer_buttons["duplicate"].Enable(selected and len(layers) < 16)
        self.layer_buttons["remove"].Enable(selected)
        self.layer_buttons["up"].Enable(selected and self._selected_layer > 0)
        self.layer_buttons["down"].Enable(selected and self._selected_layer < len(layers) - 1)

    def _load_layer_controls(self):
        old_updating = self._updating
        self._updating = True
        try:
            layer = (self._settings["layers"][self._selected_layer]
                     if self._selected_layer >= 0 else default_layer())
            for key, control in self.layer_controls.items():
                if key in ("source", "persistence", "blend"):
                    choices = {"source": SOURCE_CHOICES, "persistence": PERSISTENCE_CHOICES, "blend": BLEND_CHOICES}[key]
                    _select_value(control, choices, layer[key])
                else:
                    value = layer[key]
                    control.SetValue(value * 100 if key in ("opacity", "decay") else value)
            self._update_layer_availability()
        finally:
            self._updating = old_updating

    def _update_layer_availability(self):
        selected = self._selected_layer >= 0
        source = _choice_value(self.layer_controls["source"], SOURCE_CHOICES)
        persistence = _choice_value(self.layer_controls["persistence"], PERSISTENCE_CHOICES)
        for key, control in self.layer_controls.items():
            active = selected
            if key == "threshold":
                active = active and source != "copy"
            elif key in ("trail_frames", "decay"):
                active = active and persistence == "trail"
            control.Enable(active)
        self.layer_help.SetLabel((SOURCE_HELP[source] + "\n" + PERSISTENCE_HELP[persistence]) if selected else "Add a layer to build an effect. With no layers, only the selected base image is exported.")
        self.layer_help.Wrap(440)

    def _pull_layer_controls(self):
        if self._selected_layer < 0:
            return
        layer = self._settings["layers"][self._selected_layer]
        for key, control in self.layer_controls.items():
            if key in ("source", "persistence", "blend"):
                choices = {"source": SOURCE_CHOICES, "persistence": PERSISTENCE_CHOICES, "blend": BLEND_CHOICES}[key]
                layer[key] = _choice_value(control, choices)
            else:
                value = control.GetValue()
                layer[key] = value / 100.0 if key in ("opacity", "decay") else value

    def get_settings(self):
        """Return a validated independent snapshot, suitable for saving or exporting."""
        return validate_settings(deepcopy(self._settings))

    def on_select_layer(self, event):
        if self._closed or self._updating:
            return
        self._selected_layer = self.layer_list.GetSelection()
        self._load_layer_controls()
        self._refresh_layer_list()

    def on_layer_change(self, event):
        if self._closed or self._updating:
            return
        self._pull_layer_controls()
        self._updating = True
        try:
            self._refresh_layer_list()
            self._update_layer_availability()
        finally:
            self._updating = False
        self.queue_preview(reset=True)

    def on_base_change(self, event):
        if self._closed or self._updating:
            return
        self._settings["base"] = _choice_value(self.base_choice, BASE_CHOICES)
        try:
            self._settings["max_size"] = int(self.max_size.GetValue().split()[0])
        except (ValueError, IndexError):
            self._settings["max_size"] = self.max_size.GetValue()
        self.queue_preview(reset=True)

    def _layers_changed(self):
        self._updating = True
        try:
            self._refresh_layer_list()
            self._load_layer_controls()
        finally:
            self._updating = False
        self.queue_preview(reset=True)

    def on_add_layer(self, event):
        if len(self._settings["layers"]) >= 16:
            return
        layer = default_layer()
        layer["name"] = "Layer {}".format(len(self._settings["layers"]) + 1)
        self._settings["layers"].append(layer)
        self._selected_layer = len(self._settings["layers"]) - 1
        self._layers_changed()

    def on_duplicate_layer(self, event):
        if self._selected_layer < 0 or len(self._settings["layers"]) >= 16:
            return
        layer = deepcopy(self._settings["layers"][self._selected_layer])
        layer["name"] = (layer["name"] or "Layer")[:75] + " copy"
        self._selected_layer += 1
        self._settings["layers"].insert(self._selected_layer, layer)
        self._layers_changed()

    def on_remove_layer(self, event):
        if self._selected_layer < 0:
            return
        self._settings["layers"].pop(self._selected_layer)
        self._selected_layer = min(self._selected_layer, len(self._settings["layers"]) - 1)
        self._layers_changed()

    def _move_layer(self, direction):
        destination = self._selected_layer + direction
        layers = self._settings["layers"]
        if self._selected_layer < 0 or not 0 <= destination < len(layers):
            return
        layers[self._selected_layer], layers[destination] = layers[destination], layers[self._selected_layer]
        self._selected_layer = destination
        self._layers_changed()

    def on_layer_up(self, event):
        self._move_layer(-1)

    def on_layer_down(self, event):
        self._move_layer(1)

    def on_preset(self, event):
        name = self.preset_choice.GetStringSelection()
        if name not in self._presets:
            return
        self._settings = deepcopy(self._presets[name])
        self._selected_layer = 0 if self._settings.get("layers") else -1
        self._refresh_settings()
        self.queue_preview(reset=True, immediate=True)

    def on_save_preset(self, event):
        try:
            settings = self.get_settings()
        except Exception as error:
            self._show_error(error)
            return
        dialog = wx.TextEntryDialog(self, "Name this preset (built-in presets keep their original names).", "Save stylized preset")
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            name = dialog.GetValue().strip()
            save_preset(name, settings, path=self.preset_path)
            self._load_presets(select_name=name)
            self._refresh_settings()
            self.preset_status.SetLabel("Saved preset: " + name)
        except Exception as error:
            self._show_error(error)
        finally:
            dialog.Destroy()

    def on_browse(self, event):
        dialog = wx.DirDialog(self, "Choose the parent folder for the new image set",
                              defaultPath=self.output_parent.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.output_parent.SetValue(dialog.GetPath())
        finally:
            dialog.Destroy()

    def _show_error(self, error):
        wx.MessageBox(str(error) or type(error).__name__, "Stylized image set", wx.OK | wx.ICON_ERROR, self)

    def on_create(self, event):
        try:
            settings = self.get_settings()
            if not self.frames:
                raise ValueError("Select an image set before creating a styled set.")
            name = self.set_name.GetValue().strip()
            if not re.fullmatch(r"[A-Za-z0-9-]+", name):
                raise ValueError("Image set names may contain only letters, numbers and hyphens.")
            entered_folder = self.output_parent.GetValue().strip()
            if not entered_folder:
                raise ValueError("Choose an output parent folder.")
            folder = os.path.abspath(os.path.expanduser(entered_folder))
            if not os.path.isdir(folder):
                raise ValueError("Choose an existing output parent folder.")
            job = ExportJob(self.frames, settings, folder, name)
            owner = wx.GetTopLevelParent(self.GetParent()) if self.GetParent() else None
            progress = ExportProgressFrame(owner, job, on_use_set=self.on_use_set)
            progress.start()
        except Exception as error:
            self._show_error(error)

    def queue_preview(self, reset=False, immediate=False):
        if self._closed:
            return
        self._preview_generation += 1
        if reset:
            self._preview_revision += 1
        try:
            settings = self.get_settings()
            self.validation_status.SetLabel("")
            self.create_button.Enable(bool(self.frames))
        except Exception as error:
            self._preview_pending = None
            self.validation_status.SetLabel(str(error))
            self.validation_status.Wrap(550)
            self.create_button.Disable()
            self.next_button.Disable()
            return
        if not self.frames:
            self.preview_status.SetLabel("This image set is empty.")
            self.next_button.Disable()
            self.reset_button.Disable()
            return
        index = min(1, len(self.frames) - 1) if reset else min(self._preview_index + 1, len(self.frames) - 1)
        self._preview_pending = (self._preview_generation, settings, self._preview_revision, index)
        self._preview_due = time.monotonic() + (0 if immediate else 0.22)
        self.next_button.Disable()
        self.preview_status.SetLabel("Preparing output image {:,} of {:,}…".format(index + 1, len(self.frames)))

    def on_preview_poll(self, event):
        if self._closed:
            return
        if self._preview_future is not None and self._preview_future.done():
            future = self._preview_future
            self._preview_future = None
            generation = self._preview_task_generation
            index = self._preview_task_index
            image = None
            try:
                image = future.result()
                if generation == self._preview_generation:
                    self._display_preview(image, index)
            except Exception as error:
                if generation == self._preview_generation:
                    self.preview_status.SetLabel("Preview failed: " + str(error))
                    self.preview_status.Wrap(490)
                    self.next_button.Disable()
            finally:
                if image is not None:
                    image.close()
        if (self._preview_future is None and self._preview_pending is not None
                and time.monotonic() >= self._preview_due):
            generation, settings, revision, index = self._preview_pending
            self._preview_pending = None
            self._preview_task_generation = generation
            self._preview_task_index = index
            try:
                self._preview_future = self._executor.submit(_render_preview, self._preview_state,
                                                             self.frames, settings, revision, index)
            except Exception as error:
                self.preview_status.SetLabel("Preview failed: " + str(error))
                self.preview_status.Wrap(490)
                self.next_button.Disable()

    def _display_preview(self, image, index):
        available = self.preview_panel.GetClientSize()
        maximum = (max(150, available.width - 12), max(120, available.height - 12))
        with image.convert("RGB") as thumbnail:
            thumbnail.thumbnail(maximum, Image.Resampling.LANCZOS)
            bitmap_image = wx.Image(thumbnail.width, thumbnail.height)
            bitmap_image.SetData(thumbnail.tobytes())
            self.preview_bitmap.SetBitmap(bitmap_image.ConvertToBitmap())
        self._preview_index = index
        path = self.frames[index]
        self.preview_status.SetLabel("Output image {:,} of {:,}\n{}".format(index + 1, len(self.frames), os.path.basename(path)))
        self.preview_status.SetToolTip(path)
        self.preview_status.Wrap(490)
        self.next_button.Enable(index < len(self.frames) - 1)
        self.preview_panel.Layout()
        self.Layout()

    def on_next(self, event):
        if self._preview_future is not None or self._preview_pending is not None:
            return
        if self._preview_index < len(self.frames) - 1:
            self.queue_preview(immediate=True)

    def on_reset(self, event):
        self.queue_preview(reset=True, immediate=True)

    def _shutdown_preview(self):
        if self._closed:
            return
        self._closed = True
        self.timer.Stop()
        self._preview_pending = None
        if self._preview_future is not None:
            self._preview_future.add_done_callback(_close_future_image)
        # Cleanup queues behind the active task; the wx thread never waits for decoding.
        try:
            self._executor.submit(_close_preview_state, self._preview_state)
        except Exception:
            state = self._preview_state
            if self._preview_future is not None and not self._preview_future.done():
                self._preview_future.add_done_callback(lambda completed: _close_preview_state(state))
            else:
                _close_preview_state(state)
        finally:
            self._executor.shutdown(wait=False)

    def Destroy(self):
        # Native text/spin events may still be queued when a caller destroys us.
        # Mark closed before wx begins destroying the child controls.
        if hasattr(self, "timer"):
            self._shutdown_preview()
        return super().Destroy()

    def on_close_button(self, event):
        self.Close()

    def on_close(self, event):
        self._shutdown_preview()
        self.Destroy()

    def on_destroy(self, event):
        if event.GetEventObject() is self:
            self._shutdown_preview()
        event.Skip()
