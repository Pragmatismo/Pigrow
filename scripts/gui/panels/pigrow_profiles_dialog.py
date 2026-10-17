"""Edit saved Pigrows without changing settings until the caller accepts Save."""

import wx

from pigrow_profiles import new_profile, normalize_profiles, normalized_address


class PigrowProfilesDialog(wx.Dialog):
    """A private, editable draft of the saved connection profiles."""

    def __init__(self, parent, profiles, default_username="pi",
                 default_password="", ssh_port=22, selected_profile_id=None):
        super().__init__(parent, title="Saved Pigrows", size=(760, 580),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self._profiles = normalize_profiles(profiles)
        self.default_username = default_username
        self.default_password = default_password
        self.ssh_port = ssh_port
        self._selected_profile_id = None
        self._row_ids = []
        self._refreshing_list = False
        self._form_baseline = None

        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(
            panel, label="Select a Pigrow to edit its connection details. "
                         "Changes are kept only when you Save.")
        help_text.Wrap(700)
        layout.Add(help_text, 0, wx.EXPAND | wx.ALL, 10)

        self.profile_list = wx.ListCtrl(
            panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        for column, title, width in (
                (0, "Box name", 190), (1, "Address / hostname", 240),
                (2, "Username", 120), (3, "State", 125)):
            self.profile_list.InsertColumn(column, title, width=width)
        self.profile_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        layout.Add(self.profile_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        form = wx.FlexGridSizer(rows=4, cols=2, vgap=7, hgap=10)
        form.AddGrowableCol(1, 1)
        self.box_name = wx.TextCtrl(panel)
        self.address = wx.TextCtrl(panel)
        self.username = wx.TextCtrl(panel)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.password.SetToolTip("Password stored with this Pigrow's connection details")
        for label, control in (("Box name", self.box_name),
                               ("Address / hostname", self.address),
                               ("Username", self.username),
                               ("Password", self.password)):
            form.Add(wx.StaticText(panel, label=label), 0,
                     wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)
        layout.Add(form, 0, wx.EXPAND | wx.ALL, 10)

        controls = wx.BoxSizer(wx.HORIZONTAL)
        self.add_button = wx.Button(panel, label="Add")
        self.update_button = wx.Button(panel, label="Update")
        self.remove_button = wx.Button(panel, label="Remove")
        self.unlink_button = wx.Button(panel, label="Unlink")
        self.seek_button = wx.Button(panel, label="Seek IPs")
        self.add_button.SetToolTip("Add a new Pigrow using the details above")
        self.update_button.SetToolTip("Apply the details above to the selected Pigrow")
        self.unlink_button.SetToolTip("Clear the address while keeping the box name and login details")
        for button, handler in ((self.add_button, self.on_add),
                                (self.update_button, self.on_update),
                                (self.remove_button, self.on_remove),
                                (self.unlink_button, self.on_unlink)):
            button.Bind(wx.EVT_BUTTON, handler)
            controls.Add(button, 0, wx.RIGHT, 5)
        controls.AddStretchSpacer()
        self.seek_button.Bind(wx.EVT_BUTTON, self.on_seek)
        controls.Add(self.seek_button, 0)
        layout.Add(controls, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.info_text = wx.StaticText(
            panel, label="Unlinked Pigrows keep their login details. "
                         "New discoveries remain tentative until connected.")
        self.info_text.Wrap(700)
        layout.Add(self.info_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        buttons = wx.StdDialogButtonSizer()
        save_button = wx.Button(panel, wx.ID_OK, label="Save")
        cancel_button = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
        buttons.AddButton(save_button)
        buttons.AddButton(cancel_button)
        buttons.Realize()
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        save_button.SetDefault()
        layout.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(layout)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(outer)
        self.SetMinSize((640, 500))
        if not any(profile["id"] == selected_profile_id for profile in self._profiles):
            selected_profile_id = self._profiles[0]["id"] if self._profiles else None
        self._refresh_list(selected_profile_id)
        self.CentreOnParent()

    @property
    def selected_profile_id(self):
        return self._selected_profile_id

    def get_selected_profile_id(self):
        return self.selected_profile_id

    def get_profiles(self):
        """Return a fresh draft; the caller decides whether to persist it."""
        return normalize_profiles(self._profiles)

    def _selected_profile(self):
        return next((profile for profile in self._profiles
                     if profile["id"] == self._selected_profile_id), None)

    def _form_values(self):
        return (self.box_name.GetValue(), self.address.GetValue(),
                self.username.GetValue(), self.password.GetValue())

    def _load_form(self, profile):
        values = ((profile["box_name"], profile["address"],
                   profile["username"], profile["password"]) if profile else
                  ("", "", self.default_username, self.default_password))
        for control, value in zip((self.box_name, self.address,
                                   self.username, self.password), values):
            control.ChangeValue(value)
        self._form_baseline = self._form_values()
        selected = profile is not None
        for button in (self.update_button, self.remove_button, self.unlink_button):
            button.Enable(selected)

    def _apply_form(self):
        """Keep unsaved form edits when moving between draft rows."""
        profile = self._selected_profile()
        if profile is None or self._form_values() == self._form_baseline:
            return
        box_name, address, username, password = self._form_values()
        profile.update(box_name=box_name.strip() or "unknown pi",
                       address=address.strip(), username=username.strip(),
                       password=password)
        if not box_name.strip() or box_name.strip().casefold() == "unknown pi":
            profile["tentative"] = True
        self._form_baseline = self._form_values()

    @staticmethod
    def _state_text(profile):
        if not profile["address"]:
            return "Unlinked"
        return "Tentative" if profile["tentative"] else "Saved"

    def _refresh_list(self, selected_id=None):
        self._refreshing_list = True
        self.profile_list.Freeze()
        try:
            self.profile_list.DeleteAllItems()
            self._row_ids = []
            self._selected_profile_id = None
            for profile in self._profiles:
                index = self.profile_list.InsertItem(
                    self.profile_list.GetItemCount(), profile["box_name"])
                self.profile_list.SetItem(index, 1, profile["address"])
                self.profile_list.SetItem(index, 2, profile["username"])
                self.profile_list.SetItem(index, 3, self._state_text(profile))
                self._row_ids.append(profile["id"])
                if profile["id"] == selected_id:
                    self._selected_profile_id = selected_id
                    self.profile_list.SetItemState(
                        index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                        wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                    self.profile_list.EnsureVisible(index)
        finally:
            self.profile_list.Thaw()
            self._refreshing_list = False
        self._load_form(self._selected_profile())

    def on_select(self, event):
        if self._refreshing_list:
            return
        index = event.GetIndex()
        if not 0 <= index < len(self._row_ids):
            return
        selected_id = self._row_ids[index]
        if selected_id == self._selected_profile_id:
            return
        self._apply_form()
        self._refresh_list(selected_id)

    def on_add(self, event):
        box_name, address, username, password = self._form_values()
        profile = new_profile(box_name=box_name.strip() or "unknown pi",
                              address=address.strip(), username=username.strip(),
                              password=password, tentative=True)
        self._profiles.append(profile)
        self._refresh_list(profile["id"])
        self.info_text.SetLabel("Added to the draft. Save to keep your changes.")

    def on_update(self, event):
        self._apply_form()
        self._refresh_list(self._selected_profile_id)

    def on_remove(self, event):
        selected_id = self._selected_profile_id
        if selected_id is None:
            return
        index = next(index for index, profile in enumerate(self._profiles)
                     if profile["id"] == selected_id)
        del self._profiles[index]
        next_id = (self._profiles[min(index, len(self._profiles) - 1)]["id"]
                   if self._profiles else None)
        self._refresh_list(next_id)
        self.info_text.SetLabel("Removed from the draft. Save to keep your changes.")

    def on_unlink(self, event):
        self._apply_form()
        profile = self._selected_profile()
        if profile is not None:
            profile["address"] = ""
            self._refresh_list(profile["id"])
            self.info_text.SetLabel("Address cleared; the box name and login details are kept.")

    def _choose_discovered_location(self, addresses):
        profile = self._selected_profile()
        if profile is None or not addresses:
            return None
        choices = ["Add found devices; keep the current location"] + addresses
        dialog = wx.SingleChoiceDialog(
            self, "Add the discoveries, or choose a new location for %s.\n"
                  "Changing its location keeps its username and password." % profile["box_name"],
            "Use discovered location", choices)
        try:
            if dialog.ShowModal() == wx.ID_OK and dialog.GetSelection() > 0:
                return addresses[dialog.GetSelection() - 1]
        finally:
            dialog.Destroy()
        return None

    def _stage_discoveries(self, devices, selected_addresses):
        """Stage Pi results and chosen candidates, deduplicating scan aliases."""
        chosen = {normalized_address(address): address.strip()
                  for address in selected_addresses if address.strip()}
        added_ids = []
        handled = set()
        for device in devices:
            address = str(device.get("address", "") or "").strip()
            hostname = str(device.get("hostname", "") or "").strip()
            aliases = {normalized_address(value) for value in (address, hostname) if value}
            if not address or not (device.get("is_pi") or aliases.intersection(chosen)):
                continue
            handled.update(aliases)
            # A chosen hostname is a useful stable location for a moved device.
            preferred = chosen.get(normalized_address(hostname)) if hostname else None
            preferred = preferred or chosen.get(normalized_address(address)) or address
            if any(normalized_address(profile["address"]) in aliases
                   for profile in self._profiles if profile["address"]):
                continue
            profile = new_profile(address=preferred, username=self.default_username,
                                  password=self.default_password, tentative=True)
            self._profiles.append(profile)
            added_ids.append(profile["id"])
        for key, address in chosen.items():
            if key in handled or any(normalized_address(profile["address"]) == key
                                     for profile in self._profiles):
                continue
            profile = new_profile(address=address, username=self.default_username,
                                  password=self.default_password, tentative=True)
            self._profiles.append(profile)
            added_ids.append(profile["id"])
        return added_ids

    def on_seek(self, event):
        from panels.pigrow_discovery import DiscoverIPDialog

        self._apply_form()
        self._refresh_list(self._selected_profile_id)
        dialog = DiscoverIPDialog(
            self, title="Seek IPs",
            addresses=[profile["address"] for profile in self._profiles if profile["address"]],
            ssh_port=self.ssh_port)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            devices = dialog.get_devices()
            selected_addresses = dialog.get_selected_addresses()
        finally:
            dialog.Destroy()

        new_location = self._choose_discovered_location(selected_addresses)
        profile = self._selected_profile()
        if new_location and profile is not None:
            profile["address"] = new_location.strip()
        added_ids = self._stage_discoveries(devices, selected_addresses)
        selected_id = (profile["id"] if new_location and profile is not None else
                       added_ids[0] if added_ids else self._selected_profile_id)
        self._refresh_list(selected_id)
        changes = "%s tentative Pigrow%s added" % (len(added_ids), "" if len(added_ids) == 1 else "s")
        if new_location:
            changes += "; selected Pigrow's location updated"
        self.info_text.SetLabel(changes + ". Save to keep your changes.")

    def on_save(self, event):
        if self._selected_profile() is not None:
            self._apply_form()
        elif self._form_values() != self._form_baseline:
            # Saving a manually entered first row should not lose the form.
            self.on_add(None)
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
