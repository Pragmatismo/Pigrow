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

        self.read_caps_json = wx.Button(self, label="Read caps JSON")
        self.main_sizer.Add(self.read_caps_json, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_dataset)
        self.read_caps_json.Bind(wx.EVT_BUTTON, self.on_read_caps_json)

        # Set the sizer
        self.SetSizer(self.main_sizer)

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
    def __init__( self, parent ):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['graphs_pnl']
        w = 1000
        wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self,  label='Graphs')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This will be where graphs are made, at the moment you still need to use the older gui. "
        page_sub_title =  wx.StaticText(self,  label=sub_title_text)



        # Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)
        self.SetupScrolling()


import wx
import os
import json

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

# class caps_data_dialog(wx,Dialog):
#     def __init__(self, parent, *args, **kw):
#         self.parent = parent
#         timelapse_set = parent.parent.dict_C_pnl['timelapse_pnl'].trimmed_frame_list
#         if timelapse_set:
#             self.caps_set = timelapse_set
#         else:
#             self.caps_set = self.select_caps_set()
#         json_keys = # get list of all keys in selected json file
#
#         # create a text box displaying the currently selected caps_set's first item and length of list
#         # beside that have a button which runs select_caps_set and changes value of cap set box, recalculates json keys
#         # have a dropdown box below that with a choice of all avilable json keys
#         # have a button below that 'read json files' that run on_read_json_files
#         # below that a button 'save in log format' on_save_in_log_format
#         # at the bottom there are two buttons 'add dataset' and 'cancel'
#
#
#
#     def select_caps_set(self, e=None):
#         frompi_path = self.parent.parent.shared_data.frompi_path
#         # open dialog box to select json file
#         # default path for dialog box is frompi path.
#
#         base_path, filename = os.path.split(file_path)
#         cap_set = filename.split("_")[0]
#         # get a list of all files that match {base_path}/{cap_set}_*.json
#         # return list
#
#     def on_read_json_files(self, e=None):
#         date_from_file = self.parent.parent.dict_I_pnl['timelapse_pnl']
#         # for every item in the json files list
#         # read the file and extract the value of the item
#         # read the date from the filename using;
#         date = date_from_file(filename)
#         # create list of tuples [(date, value), (date, value), (date, value)]
#
#     def on_save_in_log_format(self, e=None):
#         # ask user to select a save location and filename
#         # cycle trough each item in self.caps_Set
#         # make a string adding "date={item[1]}, {selected_json_key}={value}\n"
#         # save the sring to the locaion the user gave
#
#     def on_add_dataset(self, e=None):
#         set1 = [{path_to_json_file}, {selected_key}, {list_of_dates_and_values}]
#         self.parent.loaded_datasets.append(set1)
