import wx
import wx.grid as gridlib
import wx.lib.scrolledpanel as scrolled
import os
import json

class ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data

        # Initialize the list of datasets (empty for now)
        self.loaded_datasets = []

        wx.Panel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the label 'Loaded Datasets' above the table
        label = wx.StaticText(self, label="Loaded Datasets")
        self.main_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Add table to display datasets
        self.datasets_table = self.create_datasets_table()
        self.main_sizer.Add(self.datasets_table, 0, wx.EXPAND | wx.ALL, 5)

        # Button to add datasets for testing
        self.add_btn = wx.Button(self, label="Add Dataset")
        self.main_sizer.Add(self.add_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Button to toggle Load Log panel
        self.toggle_load_log_btn = wx.Button(self, label="Load Log")
        self.main_sizer.Add(self.toggle_load_log_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.read_caps_json = wx.Button(self, label="Read caps JSON")
        self.main_sizer.Add(self.read_caps_json, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_dataset)
        self.toggle_load_log_btn.Bind(wx.EVT_BUTTON, self.on_toggle_load_log)
        self.read_caps_json.Bind(wx.EVT_BUTTON, self.on_read_caps_json)

        # Set the sizer
        self.SetSizer(self.main_sizer)

    def on_toggle_load_log(self, event):
        """Toggle the visibility of the Load Log panel in info_pnl."""
        i_pnl = self.parent.dict_I_pnl['graphs_pnl']
        i_pnl.toggle_load_log_panel()

    def create_datasets_table(self):
        # Create a panel to hold the dataset table
        self.table_panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create the grid to display datasets
        self.grid = gridlib.Grid(self.table_panel)
        self.grid.CreateGrid(1, 3)  # Create grid with 3 columns, 1 empty row initially

        # Hide the row and column labels
        self.grid.HideRowLabels()
        self.grid.DisableDragGridSize()
        self.grid.EnableEditing(False)

        # Set grid to select entire rows
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)

        # Set the columns to be read-only
        self.grid.SetColLabelSize(0)  # Hide column headers
        for col in range(3):
            self.grid.SetColFormatFloat(col, width=-1)  # Prevent resizing of columns

        # Column Alignment and Size
        self.grid.SetColSize(0, 200)  # File Name
        self.grid.SetColSize(1, 100)  # Key
        self.grid.SetColSize(2, 50)   # Length

        # Center align text in "Key" and "Length" columns
        self.grid.SetColAttr(1, wx.grid.GridCellAttr().SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER))
        self.grid.SetColAttr(2, wx.grid.GridCellAttr().SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER))

        # Start with empty fields
        self.grid.SetCellValue(0, 0, "")
        self.grid.SetCellValue(0, 1, "")
        self.grid.SetCellValue(0, 2, "")

        # Add the grid to the panel
        panel_sizer.Add(self.grid, 1, wx.EXPAND)

        # Add buttons for row interaction (delete and move up)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.delete_btn = wx.Button(self.table_panel, label="Delete")
        self.up_btn = wx.Button(self.table_panel, label="Move Up")

        button_sizer.Add(self.up_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.delete_btn, 0, wx.ALL, 5)

        # Bind button events
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        self.up_btn.Bind(wx.EVT_BUTTON, self.on_move_up)

        # Add the buttons to the panel sizer
        panel_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        # Bind key events for delete functionality
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.table_panel.SetSizer(panel_sizer)
        return self.table_panel

    def adjust_table_size(self):
        """Adjust the table height dynamically based on the number of rows."""
        num_rows = max(1, len(self.loaded_datasets))  # Ensure at least 1 row is visible
        row_height = self.grid.GetRowSize(0)
        total_height = num_rows * row_height

        # Adjust grid size to fit the number of rows
        self.grid.SetSize((-1, total_height))
        self.table_panel.SetSize((-1, total_height))
        self.main_sizer.Layout()  # Update the layout to apply changes

    def on_key_down(self, event):
        """Handle key events like Delete."""
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_DELETE:
            self.delete_selected_rows()

        event.Skip()

    def on_delete(self, event):
        """Handle Delete button press."""
        self.delete_selected_rows()

    def delete_selected_rows(self):
        """Delete the selected rows from the table and ask for confirmation."""
        selected_rows = self.grid.GetSelectedRows()

        if not selected_rows:
            return  # No rows selected

        # Show confirmation dialog for multiple rows
        for row in selected_rows:
            if row != -1 and row < len(self.loaded_datasets):  # Ensure it's a valid row
                file_name = self.grid.GetCellValue(row, 0)
                key = self.grid.GetCellValue(row, 1)

                # Show confirmation dialog for each selected row
                confirm_dialog = wx.MessageDialog(self, f"Do you want to remove {file_name}, {key}?", "Confirm Deletion", wx.YES_NO | wx.ICON_QUESTION)

                if confirm_dialog.ShowModal() == wx.ID_YES:
                    # Remove from dataset
                    del self.loaded_datasets[row]

        # Refresh the table to remove deleted rows
        self.refresh_table()

    def on_move_up(self, event):
        """Move the selected row up in the dataset list."""
        selected_rows = self.grid.GetSelectedRows()

        if selected_rows and selected_rows[0] > 0:  # Ensure we can move up
            row = selected_rows[0]
            # Swap datasets
            self.loaded_datasets[row], self.loaded_datasets[row-1] = self.loaded_datasets[row-1], self.loaded_datasets[row]
            self.refresh_table()

    def refresh_table(self):
        """Refresh the grid to reflect the updated dataset list."""
        self.grid.ClearGrid()

        # Update the grid with the new dataset length
        self.grid.DeleteRows(0, self.grid.GetNumberRows())  # Clear all rows
        self.grid.AppendRows(len(self.loaded_datasets))  # Add the number of rows we need

        for i, dataset in enumerate(self.loaded_datasets):
            file_path, key, data = dataset

            # Use os.path to handle file name and extension
            filename = os.path.splitext(os.path.basename(file_path))[0]  # Remove path and extension
            length = len(data)  # Get the length of the dataset

            self.grid.SetCellValue(i, 0, filename)
            self.grid.SetCellValue(i, 1, key)
            self.grid.SetCellValue(i, 2, str(length))

        self.grid.AutoSizeColumns()  # Adjust column sizes
        self.adjust_table_size()  # Adjust table size after refreshing

    def on_add_dataset(self, event):
        """Add dataset to the table (simulates loading a dataset)."""
        if len(self.loaded_datasets) == 0:
            set1 = ["./logs/sensorbank/sensor1.txt", "height", [("10:00", 1), ("11:00", 3), ("12:00", 2)]]
            self.loaded_datasets.append(set1)
        elif len(self.loaded_datasets) > 0:
            set2 = ["./logs/sensorbank/sensor2.txt", "speed", [("10:00", 1), ("11:00", 3), ("12:00", 2), ("13:00", 3)]]
            self.loaded_datasets.append(set2)

        # Refresh the table to show the new dataset
        self.refresh_table()

    def on_read_caps_json(self, event):
        self.caps_dbox = CapsDataDialog(self)
        self.caps_dbox.ShowModal()
        if self.caps_dbox:
            if not self.caps_dbox.IsBeingDeleted():
                self.caps_dbox.Destroy()
        self.refresh_table()


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['graphs_pnl']
        w = 1000
        wx.Panel.__init__(self, parent, size=(w, -1), id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self, label='Graphs')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This will be where graphs are made, at the moment you still need to use the older gui."
        page_sub_title = wx.StaticText(self, label=sub_title_text)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Load Log Panel (initially hidden)
        self.load_log_pnl = LoadLogPanel(self)
        self.load_log_pnl.Hide()
        self.main_sizer.Add(self.load_log_pnl, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def toggle_load_log_panel(self):
        """Show or hide the Load Log panel."""
        if self.load_log_pnl.IsShown():
            self.load_log_pnl.Hide()
        else:
            self.load_log_pnl.Show()
        self.main_sizer.Layout()


class CapsDataDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(CapsDataDialog, self).__init__(parent, *args, **kw)
        self.parent = parent
        self.base_path = None  # To store the base path of the selected file

        timelapse_set = parent.parent.dict_C_pnl['timelapse_pnl'].trimmed_frame_list

        # Initialize the caps_set
        if timelapse_set:
            self.caps_set = timelapse_set
        else:
            self.caps_set = []

        # UI initialization
        self.init_ui()

        # After UI elements are created, set initial data
        if timelapse_set:
            self.update_caps_display()

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Caps Set display (first item and length)
        self.caps_display = wx.TextCtrl(self, value="", style=wx.TE_READONLY)
        vbox.Add(self.caps_display, flag=wx.EXPAND | wx.ALL, border=5)

        # Button to select a new cap set
        select_caps_btn = wx.Button(self, label="Select Caps Set")
        select_caps_btn.Bind(wx.EVT_BUTTON, self.on_select_caps_set)
        vbox.Add(select_caps_btn, flag=wx.EXPAND | wx.ALL, border=5)

        # Dropdown for JSON keys (empty initially)
        self.json_key_choice = wx.Choice(self)
        vbox.Add(self.json_key_choice, flag=wx.EXPAND | wx.ALL, border=5)

        # Buttons for "Read JSON Files" and "Save in Log Format"
        read_json_btn = wx.Button(self, label="Read JSON Files")
        read_json_btn.Bind(wx.EVT_BUTTON, self.on_read_json_files)
        vbox.Add(read_json_btn, flag=wx.EXPAND | wx.ALL, border=5)

        save_log_btn = wx.Button(self, label="Save in Log Format")
        save_log_btn.Bind(wx.EVT_BUTTON, self.on_save_in_log_format)
        vbox.Add(save_log_btn, flag=wx.EXPAND | wx.ALL, border=5)

        # Add "Add Dataset" and "Cancel" buttons
        add_dataset_btn = wx.Button(self, label="Add Dataset")
        add_dataset_btn.Bind(wx.EVT_BUTTON, self.on_add_dataset)
        vbox.Add(add_dataset_btn, flag=wx.EXPAND | wx.ALL, border=5)

        cancel_btn = wx.Button(self, label="Cancel")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        vbox.Add(cancel_btn, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(vbox)
        self.SetTitle("Caps Data Dialog")
        self.Fit()

    def update_caps_display(self):
        """Update the caps set display text box."""
        if self.caps_set:
            self.caps_display.SetValue(f"{self.caps_set[0]} ({len(self.caps_set)} items)")
        else:
            self.caps_display.SetValue("No caps set selected")

        # Update JSON key choices after selecting a new caps set
        self.json_keys = self.get_json_keys()
        self.json_key_choice.SetItems(self.json_keys)

    def get_json_keys(self):
        """Get the keys from the first JSON file in caps_set."""
        if self.caps_set and self.base_path:
            first_file = os.path.join(self.base_path, self.caps_set[0])
            with open(first_file, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        return []

    def select_caps_set(self, e=None):
        frompi_path = self.parent.parent.shared_data.frompi_path

        # Open dialog box to select JSON file
        with wx.FileDialog(self, "Select JSON file", defaultDir=frompi_path, wildcard="JSON files (*.json)|*.json", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed to select the file
            file_path = fileDialog.GetPath()
            self.base_path, filename = os.path.split(file_path)  # Store base path
            cap_set = filename.split("_")[0]

            # Get a list of all files that match {base_path}/{cap_set}_*.json
            files = [f for f in os.listdir(self.base_path) if f.startswith(cap_set) and f.endswith(".json")]

            self.caps_set = files
            self.update_caps_display()

    def on_read_json_files(self, e=None):
        if not self.base_path:
            wx.MessageBox("Please select a caps set first.", "Error", wx.OK | wx.ICON_ERROR)
            return

        date_from_filename = self.parent.parent.dict_I_pnl['timelapse_pnl'].date_from_filename
        selected_key = self.json_key_choice.GetStringSelection()

        data_tuples = []
        for file in self.caps_set:
            file_path = os.path.join(self.base_path, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
            value = data.get(selected_key, None)
            date = date_from_filename(file)
            data_tuples.append((date[1], value))

        data_tuples = sorted(data_tuples, key=lambda x: x[0])
        self.data_tuples = data_tuples

    def on_save_in_log_format(self, e=None):
        if not hasattr(self, 'data_tuples'):
            wx.MessageBox("Please read the JSON files first.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Ask user to select a save location and filename
        with wx.FileDialog(self, "Save log file", wildcard="Text files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as saveDialog:
            if saveDialog.ShowModal() == wx.ID_CANCEL:
                return

            save_path = saveDialog.GetPath()

            # Construct the log format
            selected_key = self.json_key_choice.GetStringSelection()
            log_str = ""
            for date, value in self.data_tuples:
                log_str += f"date={str(date)}>{selected_key}={value}\n"

            # Save the string to the location the user gave
            with open(save_path, 'w') as log_file:
                log_file.write(log_str)

    def on_add_dataset(self, e=None):
        if not hasattr(self, 'data_tuples'):
            wx.MessageBox("Please read the JSON files first.", "Error", wx.OK | wx.ICON_ERROR)
            return

        selected_key = self.json_key_choice.GetStringSelection()
        set1 = [self.caps_set[0], selected_key, self.data_tuples]
        self.parent.loaded_datasets.append(set1)
        self.Close()

    def on_cancel(self, e=None):
        self.Close()

    def on_select_caps_set(self, e=None):
        self.select_caps_set()

import datetime
import time

class LoadLogPanel(wx.Panel):
    def __init__(self, parent):
        super(LoadLogPanel, self).__init__(parent)
        self.parent = parent  # Reference to info_pnl
        self.c_pnl = parent.c_pnl  # Reference to ctrl_pnl
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title label 'Load Log' justified left
        title_label = wx.StaticText(self, label="Load Log")
        main_sizer.Add(title_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Buttons 'load from pi' and 'load local' beside each other
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.load_from_pi_btn = wx.Button(self, label="Load from Pi")
        self.load_local_btn = wx.Button(self, label="Load Local")
        button_sizer.Add(self.load_from_pi_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.load_local_btn, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_LEFT)

        # Bind events
        self.load_from_pi_btn.Bind(wx.EVT_BUTTON, self.on_load_from_pi)
        self.load_local_btn.Bind(wx.EVT_BUTTON, self.on_load_local)

        # Log info display
        self.log_info_text = wx.StaticText(self, label="")
        main_sizer.Add(self.log_info_text, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Split Character and KV Split Character text boxes
        split_sizer = wx.BoxSizer(wx.HORIZONTAL)
        split_char_label = wx.StaticText(self, label="Split Character:")
        self.split_char_text = wx.TextCtrl(self, value="", style=wx.TE_READONLY)
        kv_split_char_label = wx.StaticText(self, label="KV Split Character:")
        self.kv_split_char_text = wx.TextCtrl(self, value="", style=wx.TE_READONLY)
        split_sizer.Add(split_char_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        split_sizer.Add(self.split_char_text, 0, wx.ALL, 5)
        split_sizer.Add(kv_split_char_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        split_sizer.Add(self.kv_split_char_text, 0, wx.ALL, 5)
        main_sizer.Add(split_sizer, 0, wx.ALIGN_LEFT)

        # Date information display
        date_info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.date_info_text = wx.StaticText(self, label="")
        date_info_sizer.Add(self.date_info_text, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        main_sizer.Add(date_info_sizer, 0, wx.ALIGN_LEFT)

        # Dropdown box for available keys
        key_sizer = wx.BoxSizer(wx.HORIZONTAL)
        key_label = wx.StaticText(self, label="Available Keys:")
        self.key_choice = wx.Choice(self)
        self.key_value_text = wx.StaticText(self, label="")
        key_sizer.Add(key_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        key_sizer.Add(self.key_choice, 0, wx.ALL, 5)
        key_sizer.Add(self.key_value_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        main_sizer.Add(key_sizer, 0, wx.ALIGN_LEFT)

        # Bind event for key_choice
        self.key_choice.Bind(wx.EVT_CHOICE, self.on_key_selected)

        # 'Load Data' button
        self.load_data_btn = wx.Button(self, label="Load Data")
        main_sizer.Add(self.load_data_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.load_data_btn.Bind(wx.EVT_BUTTON, self.on_load_data)

        self.SetSizer(main_sizer)

    def on_load_from_pi(self, event):
        wx.MessageBox("Loading logs from Pi not yet coded", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_load_local(self, event):
        # Open file dialog to select a file
        with wx.FileDialog(self, "Open Log File", wildcard="Log files (*.txt;*.log)|*.txt;*.log|All files|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            # Proceed to load the file
            path = fileDialog.GetPath()
            self.load_log_file(path)

    def load_log_file(self, path):
        try:
            with open(path, 'r') as f:
                self.lines = f.readlines()
            self.log_title = os.path.basename(path)
            # Display log title and first and last lines
            first_line = self.lines[0].strip()
            last_line = self.lines[-1].strip()
            log_info = f"{self.log_title}:\n    {first_line}\n    {last_line}"
            self.log_info_text.SetLabel(log_info)
            # Proceed to identify split characters
            self.identify_split_characters()
        except Exception as e:
            wx.MessageBox(f"Failed to load log file: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def identify_split_characters(self):
        """Identify the split character and KV split character."""
        first_line = self.lines[0].strip()
        split_char_candidates = ['>', ',', ';', '|', ' ']
        kv_split_char_candidates = ['=', ':']
        found = False
        for sc in split_char_candidates:
            fields = first_line.split(sc)
            if len(fields) > 1:
                for kv_sc in kv_split_char_candidates:
                    date_field = self.find_date_field(fields, kv_sc)
                    if date_field is not None:
                        self.split_char = sc
                        self.kv_split_char = kv_sc
                        self.split_char_text.SetValue(self.split_char)
                        self.kv_split_char_text.SetValue(self.kv_split_char)
                        found = True
                        break
                if found:
                    break
        if found:
            # Now extract all keys
            self.extract_keys()
        else:
            wx.MessageBox("Failed to identify split characters and date field.", "Error", wx.OK | wx.ICON_ERROR)

    def find_date_field(self, fields, kv_sc):
        """Find the field containing the date."""
        for field in fields:
            if kv_sc in field:
                key, value = field.split(kv_sc, 1)
                if self.is_date(value):
                    self.date_key = key
                    return field
            else:
                if self.is_date(field):
                    self.date_key = None
                    return field
        return None

    def is_date(self, text):
        """Check if a text string is a date."""
        try:
            # Try to parse as a Unix timestamp
            timestamp = float(text)
            datetime.datetime.fromtimestamp(timestamp)
            return True
        except:
            pass
        # Try common date formats
        date_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S.%f"]
        for fmt in date_formats:
            try:
                datetime.datetime.strptime(text, fmt)
                return True
            except:
                pass
        return False

    def extract_keys(self):
        """Extract keys from the first line."""
        first_line = self.lines[0].strip()
        fields = first_line.split(self.split_char)
        keys = []
        for field in fields:
            if self.kv_split_char in field:
                key, value = field.split(self.kv_split_char, 1)
                keys.append(key)
        self.keys = keys
        self.key_choice.SetItems(keys)
        self.key_choice.SetSelection(0)
        self.extract_dates()

    def extract_dates(self):
        """Extract dates from all lines."""
        self.dates = []
        self.data_lines = []
        for line in self.lines:
            line = line.strip()
            fields = line.split(self.split_char)
            date_found = False
            for field in fields:
                if self.kv_split_char in field:
                    key, value = field.split(self.kv_split_char, 1)
                    if key == self.date_key or self.date_key is None:
                        date = self.parse_date(value)
                        if date:
                            self.dates.append(date)
                            date_found = True
                            self.data_lines.append(line)
                            break
                else:
                    if self.date_key is None:
                        date = self.parse_date(field)
                        if date:
                            self.dates.append(date)
                            date_found = True
                            self.data_lines.append(line)
                            break
            if not date_found:
                continue  # Skip lines without date
        if self.dates:
            first_date = self.dates[0]
            last_date = self.dates[-1]
            duration = last_date - first_date
            date_info = f"First Date: {first_date}\nLast Date: {last_date}\nDuration: {duration}"
            self.date_info_text.SetLabel(date_info)
        else:
            self.date_info_text.SetLabel("No dates found.")

    def parse_date(self, text):
        """Parse a date from text."""
        try:
            timestamp = float(text)
            date = datetime.datetime.fromtimestamp(timestamp)
            return date
        except:
            pass
        date_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S.%f"]
        for fmt in date_formats:
            try:
                date = datetime.datetime.strptime(text, fmt)
                return date
            except:
                pass
        return None

    def on_key_selected(self, event):
        selected_key = self.key_choice.GetStringSelection()
        # Get the value of that key in the first line
        first_line = self.lines[0].strip()
        fields = first_line.split(self.split_char)
        value = None
        for field in fields:
            if self.kv_split_char in field:
                key, val = field.split(self.kv_split_char, 1)
                if key == selected_key:
                    value = val
                    break
        if value:
            self.key_value_text.SetLabel(f"Value: {value}")
        else:
            self.key_value_text.SetLabel("Value not found.")

    def on_load_data(self, event):
        """Load data and add to ctrl_pnl."""
        selected_key = self.key_choice.GetStringSelection()
        data_tuples = []
        for line in self.data_lines:
            line = line.strip()
            fields = line.split(self.split_char)
            date = None
            value = None
            for field in fields:
                if self.kv_split_char in field:
                    key, val = field.split(self.kv_split_char, 1)
                    if key == selected_key:
                        value = val
                    if key == self.date_key or self.date_key is None:
                        date = self.parse_date(val)
                else:
                    if self.date_key is None:
                        date = self.parse_date(field)
            if date and value is not None:
                try:
                    data_tuples.append((date, float(value)))
                except ValueError:
                    continue  # Skip lines where value cannot be converted to float
        # Add the dataset to ctrl_pnl
        set1 = [self.log_title, selected_key, data_tuples]
        self.c_pnl.loaded_datasets.append(set1)
        self.c_pnl.refresh_table()
        wx.MessageBox("Data loaded successfully.", "Info", wx.OK | wx.ICON_INFORMATION)
