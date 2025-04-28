import wx
import wx.grid as gridlib
import wx.adv
import wx.lib.scrolledpanel as scrolled
import importlib
import os
import json
import datetime
import time
import sys
import matplotlib.pyplot as plt
from Onboard.utils import funcKeys
from scipy.stats import trim_mean


class ctrl_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.loaded_datasets = []

        # Initialize ScrolledPanel instead of Panel
        scrolled.ScrolledPanel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the label 'Loaded Datasets' above the table
        label = wx.StaticText(self, label="Loaded Datasets")
        self.main_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Add table to display datasets
        self.datasets_table = self.create_datasets_table()
        self.main_sizer.Add(self.datasets_table, 0, wx.EXPAND | wx.ALL, 5)

        # Preset sizer
        self.preset_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Preset label
        preset_label = wx.StaticText(self, label="Preset")
        self.preset_sizer.Add(preset_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # Preset choice (combobox)
        self.preset_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        # Initialize GraphPreset and populate preset list
        self.graph_preset = GraphPreset(self)
        preset_list = self.graph_preset.get_preset_list()
        self.preset_choice.SetItems(preset_list)
        if preset_list:
            self.preset_choice.SetSelection(0)

        self.preset_sizer.Add(self.preset_choice, 1, wx.EXPAND | wx.ALL, 5)

        # Load button
        self.load_preset_btn = wx.Button(self, label="Load")
        self.preset_sizer.Add(self.load_preset_btn, 0, wx.ALL, 5)

        # Save button
        self.save_preset_btn = wx.Button(self, label="Save")
        self.preset_sizer.Add(self.save_preset_btn, 0, wx.ALL, 5)

        # Bind button events
        self.load_preset_btn.Bind(wx.EVT_BUTTON, self.on_load_preset)
        self.save_preset_btn.Bind(wx.EVT_BUTTON, self.on_save_preset)

        # Add preset_sizer to main_sizer
        self.main_sizer.Add(self.preset_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Button to toggle Load Log panel
        self.toggle_load_log_btn = wx.Button(self, label="Load Log")
        self.main_sizer.Add(self.toggle_load_log_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Data loading buttons
        self.datal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.read_caps_json = wx.Button(self, label="Read caps JSON")
        self.open_datasucker = wx.Button(self, label="Data Sucker")
        self.datal_sizer.Add(self.read_caps_json, 0, wx.ALL, 5)
        self.datal_sizer.Add(self.open_datasucker, 0, wx.ALL, 5)
        self.main_sizer.Add(self.datal_sizer, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.toggle_load_log_btn.Bind(wx.EVT_BUTTON, self.on_toggle_load_log)
        self.read_caps_json.Bind(wx.EVT_BUTTON, self.on_read_caps_json)
        self.open_datasucker.Bind(wx.EVT_BUTTON, self.on_open_datasucker)

        self.create_make_graphs_section()

        # Create the empty options panel
        self.options_panel = GraphOptionsPanel(self)
        self.main_sizer.Add(self.options_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Set the sizer
        self.SetSizer(self.main_sizer)

        # Setup scrolling
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def on_load_preset(self, event):
        self.graph_preset.load_preset(self)

    def on_save_preset(self, event):
        self.graph_preset.save_preset(
            parent=self,
            loaded_datasets=self.loaded_datasets,
            graph_type=self.graph_choice.GetStringSelection(),
            graph_settings=self.options_panel.get_options() if self.configure_graph_chk.IsChecked() else {}
        )

    def create_make_graphs_section(self):
        """Create the 'Make Graphs' section in the control panel."""
        # Section Heading
        heading = wx.StaticText(self, label="Make Graphs")
        self.main_sizer.Add(heading, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Sizer for graph selection and 'Make' button
        graph_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Combo box for available graphs
        self.graph_choice = wx.ComboBox(self, style=wx.CB_READONLY)
        self.populate_graph_choices()
        self.graph_choice.Bind(wx.EVT_COMBOBOX, self.on_graph_selected)

        # 'Make' button
        self.make_graph_btn = wx.Button(self, label="Make")
        self.make_graph_btn.Bind(wx.EVT_BUTTON, self.on_make_graph)

        graph_sizer.Add(self.graph_choice, 1, wx.EXPAND | wx.ALL, 5)
        graph_sizer.Add(self.make_graph_btn, 0, wx.ALL, 5)

        self.main_sizer.Add(graph_sizer, 0, wx.EXPAND)

        # 'Configure Graph' checkbox
        self.configure_graph_chk = wx.CheckBox(self, label="Configure Graph")
        self.configure_graph_chk.Bind(wx.EVT_CHECKBOX, self.on_configure_graph)
        self.main_sizer.Add(self.configure_graph_chk, 0, wx.ALIGN_LEFT | wx.ALL, 5)

    def on_graph_selected(self, e):
        self.on_configure_graph(None)

    def populate_graph_choices(self):
        """Populate the combo box with available graph modules."""
        graph_modules_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'graph_modules'))
        self.graph_names = []

        if os.path.isdir(graph_modules_dir):
            for filename in os.listdir(graph_modules_dir):
                if filename.startswith('graph_') and filename.endswith('.py'):
                    graph_name = filename[len('graph_'):-len('.py')]
                    self.graph_names.append(graph_name)
        else:
            wx.MessageBox(f"Graph modules directory not found: {graph_modules_dir}", "Error", wx.OK | wx.ICON_ERROR)

        # Reorder based on default_order
        default_order = ['line', 'overlaid_days', 'averages', 'high_low', 'histogram', 'bar']
        # We'll loop in reverse so we insert them at the front in correct order
        for name in reversed(default_order):
            if name in self.graph_names:
                self.graph_names.remove(name)
                self.graph_names.insert(0, name)

        self.graph_choice.SetItems(self.graph_names)
        if self.graph_names:
            self.graph_choice.SetSelection(0)

    def do_make_graph(self):
        """Creates the graph image and returns the graph file path."""
        datasets = self.prepare_datasets_for_graph()
        selected_graph = self.graph_choice.GetStringSelection()
        if not selected_graph:
            wx.MessageBox("Please select a graph.", "Error", wx.OK | wx.ICON_ERROR)
            return None

        options = self.options_panel.get_options()

        # Validate axis limits:
        ymax = options.get("Y axis Maximum", "")
        if ymax != "":
            try:
                int(ymax)
            except:
                ymax = ""
        ymin = options.get("Y axis Minimum", "")
        if ymin != "":
            try:
                int(ymin)
            except:
                ymin = ""

        size_h = int(options.get("Width", 12))
        size_v = int(options.get("Height", 7))

        module_name = f"graph_{selected_graph}"
        file_name = module_name + ".png"
        graph_path = os.path.join(self.shared_data.frompi_path, file_name)

        # Add the graph_modules folder to sys.path if needed:
        graph_modules_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'graph_modules'))
        if graph_modules_dir not in sys.path:
            sys.path.insert(0, graph_modules_dir)

        try:
            # Import or reload the graph module
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                graph_module = sys.modules[module_name]
            else:
                graph_module = importlib.import_module(module_name)

            if hasattr(graph_module, 'make_graph'):
                make_graph = graph_module.make_graph
                start_time = time.time()
                make_graph(datasets, graph_path, ymax, ymin, size_h, size_v,
                           None, None, None, None, options)
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"{module_name} graph created in {elapsed_time} seconds and saved to {graph_path}")
                return graph_path
            else:
                print(f"The module '{module_name}' does not have a 'make_graph' function.")
                return None
        except Exception as e:
            print(f"Failed to import or execute '{module_name}': {e}")
            return None

    def on_make_graph(self, event):
        graph_path = self.do_make_graph()
        if graph_path:
            self.parent.dict_I_pnl['graphs_pnl'].add_graph_to_panel(graph_path)

    def create_graph_by_preset(self, preset_name):
        """
        This method is called externally (e.g. from the datawall tab). It loads the given graph preset,
        then creates the graph and returns its path.
        """
        # Load the preset by name (using the updated load_preset)
        self.graph_preset.load_preset(self, preset_name)
        # Now create the graph:
        graph_path = self.do_make_graph()
        return graph_path

    def prepare_datasets_for_graph(self):
        new_dataset = []

        for dataset in self.loaded_datasets:
            key = dataset["key"]
            data = dataset["trimmed_data"]

            # Separate dates and values into their own lists
            date_list = [item[0] for item in data]
            value_list = [item[1] for item in data]

            # Package the lists into the format [date_list, value_list, [key]]
            formatted_dataset = [date_list, value_list, [key]]
            new_dataset.append(formatted_dataset)

        return new_dataset

    def on_configure_graph(self, event):
        """Handle the 'Configure Graph' checkbox."""
        if self.configure_graph_chk.IsChecked():
            selected_graph = self.graph_choice.GetStringSelection()
            if not selected_graph:
                wx.MessageBox("Please select a graph.", "Error", wx.OK | wx.ICON_ERROR)
                return

            module_name = f"graph_{selected_graph}"
            graph_modules_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'graph_modules'))

            # Add graph_modules_dir to sys.path if not already present
            if graph_modules_dir not in sys.path:
                sys.path.insert(0, graph_modules_dir)

            try:
                # Reload the module if it's already loaded
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    graph_module = sys.modules[module_name]
                else:
                    graph_module = importlib.import_module(module_name)

                # Read graph options (for now, just print them)
                if hasattr(graph_module, 'read_graph_options'):
                    options = graph_module.read_graph_options()
                    self.options_panel.update_options(options)
                else:
                    print(f"The module '{module_name}' does not have a 'read_graph_options' function.")
            except Exception as e:
                print(f"Failed to import or execute '{module_name}':\n{e}")
        else:
            # Checkbox unchecked; add hide function once display is done
            pass

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
        self.grid.CreateGrid(1, 4)  # Create grid with 3 columns, 1 empty row initially

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
        self.grid.SetColSize(3, 80)   # Trimmed Length

        # Center align text in "Key", "Length", and "Trimmed Length" columns
        for col in [1, 2, 3]:
            self.grid.SetColAttr(col, wx.grid.GridCellAttr().SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER))

        # Start with empty fields
        self.grid.SetCellValue(0, 0, "")
        self.grid.SetCellValue(0, 1, "")
        self.grid.SetCellValue(0, 2, "")
        self.grid.SetCellValue(0, 3, "")

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

        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_cell_dclick)

        # Add the buttons to the panel sizer
        panel_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        # Bind key events for delete functionality
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.table_panel.SetSizer(panel_sizer)
        return self.table_panel

    def on_cell_dclick(self, event):
        row = event.GetRow()
        if row < len(self.loaded_datasets):
            dataset = self.loaded_datasets[row]
            i_pnl = self.parent.dict_I_pnl['graphs_pnl']
            i_pnl.show_duration_select_panel(dataset)
        event.Skip()


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
        # Clear the grid only if there are rows to delete
        num_rows = self.grid.GetNumberRows()
        if num_rows > 0:
            self.grid.DeleteRows(0, num_rows)

        # Append new rows based on the number of loaded datasets
        num_datasets = len(self.loaded_datasets)
        if num_datasets > 0:
            self.grid.AppendRows(num_datasets)

        for i, dataset in enumerate(self.loaded_datasets):
            file_path = dataset['file_path']
            key = dataset['key']
            data = dataset['data']
            trimmed_data = dataset['trimmed_data']

            filename = os.path.splitext(os.path.basename(file_path))[0]
            length = len(data)
            trimmed_length = len(trimmed_data)

            self.grid.SetCellValue(i, 0, filename)
            self.grid.SetCellValue(i, 1, key)
            self.grid.SetCellValue(i, 2, str(length))
            self.grid.SetCellValue(i, 3, str(trimmed_length))

        # If there are no datasets, add an empty row
        if num_datasets == 0:
            self.grid.AppendRows(1)
            for col in range(4):
                self.grid.SetCellValue(0, col, "")

        self.grid.AutoSizeColumns()
        self.adjust_table_size()

    def on_read_caps_json(self, event):
        self.caps_dbox = CapsDataDialog(self)
        self.caps_dbox.ShowModal()
        if self.caps_dbox:
            if not self.caps_dbox.IsBeingDeleted():
                self.caps_dbox.Destroy()
        self.refresh_table()

    def on_open_datasucker(self, event):
        self.sucker_dbox = SuckerDialog(self)
        self.sucker_dbox.ShowModal()
        if self.sucker_dbox:
            if not self.sucker_dbox.IsBeingDeleted():
                self.sucker_dbox.Destroy()
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
        #sub_title_text = "."
        #page_sub_title = wx.StaticText(self, label=sub_title_text)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        #self.main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Load Log Panel
        self.load_log_pnl = LoadLogPanel(self)
        self.main_sizer.Add(self.load_log_pnl, 0, wx.EXPAND | wx.ALL, 5)

        # Duration Select Panel (initially hidden)
        self.duration_select_pnl = DurationSelectPanel(self)
        self.duration_select_pnl.Hide()
        self.main_sizer.Add(self.duration_select_pnl, 0, wx.EXPAND | wx.ALL, 5)

        # Graph Panel
        self.graph_panel = GraphPanel(self)
        self.main_sizer.Add(self.graph_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def show_duration_select_panel(self, dataset):
        """Show the Duration Select panel for the given dataset."""
        self.duration_select_pnl.load_dataset(dataset)
        self.duration_select_pnl.Show()
        self.main_sizer.Layout()

    def toggle_load_log_panel(self):
        """Show or hide the Load Log panel."""
        if self.load_log_pnl.IsShown():
            self.load_log_pnl.Hide()
        else:
            self.load_log_pnl.Show()
        self.main_sizer.Layout()

    def add_graph_to_panel(self, graph_path):
        """Add a graph to the GraphPanel."""
        self.graph_panel.add_graph(graph_path)


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
            self.cap_set = filename.split("_")[0]

            # Get a list of all files that match {base_path}/{cap_set}_*.json
            files = [f for f in os.listdir(self.base_path) if f.startswith(self.cap_set) and f.endswith(".json")]

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
        dataset = {
            'file_path': self.base_path +":J",
            'key': selected_key,
            'data': self.data_tuples,
            'trimmed_data': self.data_tuples,
            'base_path': self.base_path,
            'cap_set': self.cap_set
        }
        self.parent.loaded_datasets.append(dataset)
        self.Close()


    def on_cancel(self, e=None):
        self.Close()

    def on_select_caps_set(self, e=None):
        self.select_caps_set()

class LoadLogPanel(wx.Panel):
    def __init__(self, parent):
        super(LoadLogPanel, self).__init__(parent)
        self.parent = parent  # Reference to info_pnl
        self.c_pnl = parent.c_pnl  # Reference to ctrl_pnl

        # Flag to indicate which parsing approach we’ll use
        self.use_key_value = False
        # In positional mode, we’ll store which field is the date
        self.date_index = None

        self.init_ui()

    def init_ui(self):
        self.SetBackgroundColour(wx.Colour(220, 220, 220))
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top bar label and button
        title_label = wx.StaticText(self, label="Load Log")
        self.hide_btn = wx.Button(self, label="Hide")
        self.hide_btn.Bind(wx.EVT_BUTTON, self.on_hide_btn)
        topbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        topbar_sizer.Add(title_label, 0, wx.ALL, 5)
        topbar_sizer.AddStretchSpacer()
        topbar_sizer.Add(self.hide_btn, 0, wx.ALL, 5)
        main_sizer.Add(topbar_sizer, 0, wx.EXPAND, 5)

        # Buttons 'load from pi' and 'load local'
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
        main_sizer.Add(split_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

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
        self.load_data_btn = wx.Button(self, label="Import Data")
        self.load_data_btn.Disable()
        main_sizer.Add(self.load_data_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.load_data_btn.Bind(wx.EVT_BUTTON, self.on_import_data)

        self.SetSizer(main_sizer)
        self.parent.Layout()

    def on_hide_btn(self, event):
        self.Hide()
        self.parent.main_sizer.Layout()

    def on_load_from_pi(self, event):
        # Select files on Pi
        pi_logs = self.parent.parent.shared_data.remote_pigrow_path + "/logs/"
        select_files = self.parent.parent.link_pnl.select_files_on_pi
        selected_files, selected_folders = select_files(single_folder=False,
                                                        default_path=pi_logs)
        if not selected_files:
            return

        # Download File
        remote_path = selected_files[0][0]
        filename = os.path.splitext(os.path.basename(remote_path))[0]
        fp_path = self.parent.parent.shared_data.frompi_path
        local_path = os.path.join(fp_path, "logs", filename)
        print("Copying", remote_path, "to", local_path)
        self.parent.parent.link_pnl.download_file_to_folder(remote_path, local_path)

        # Load the downloaded log
        self.load_log_file(local_path)
        self.load_data_btn.Enable()
        self.Layout()
        self.parent.Layout()

    def on_load_local(self, event):
        with wx.FileDialog(
            self,
            "Open Log File",
            wildcard="Log files (*.txt;*.log)|*.txt;*.log",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            defaultDir=self.parent.parent.shared_data.frompi_path
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path = fileDialog.GetPath()
            self.load_log_file(path)
        self.load_data_btn.Enable()
        self.Layout()
        self.parent.Layout()

    def load_log_file(self, path):
        try:
            with open(path, 'r') as f:
                self.lines = f.readlines()
            self.log_title = os.path.basename(path)
            # Display log title and first and last lines
            first_line = self.lines[0].strip()
            last_line = self.lines[-1].strip()
            log_info = f"{self.log_title}:\n       {first_line}\n       {last_line}"
            self.log_info_text.SetLabel(log_info)

            # Attempt to detect key=value pairs or fallback to positional
            self.identify_format()

        except Exception as e:
            wx.MessageBox(f"Failed to load log file: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def identify_format(self):
        """
        Try to identify if the log lines are in key=value format or
        if we should treat them as CSV/positional.
        """
        # Reset stuff
        self.use_key_value = False
        self.date_index = None
        self.split_char = None
        self.kv_split_char = None

        # Try to find a key and a date in the first line(s) as before
        if self.identify_key_value_format():
            print("Found Key=Value pair type")
            # If we found key-value format (use_key_value = True),
            # we do the old logic: extract keys, then extract dates
            self.split_char_text.SetValue(self.split_char)
            self.kv_split_char_text.SetValue(self.kv_split_char)
            self.extract_keys_kv()
            self.extract_dates_kv()
        else:
            # If we fail, fallback to a positional approach
            # Attempt to detect a suitable split char and date field index
            if self.identify_positional_format():
                self.split_char_text.SetValue(self.split_char)
                self.kv_split_char_text.SetValue("")  # no kv split in positional
                self.extract_keys_positional()
                self.extract_dates_positional()
            else:
                wx.MessageBox("Failed to identify format or date field.",
                              "Error", wx.OK | wx.ICON_ERROR)

    def identify_key_value_format(self):
        split_char_candidates = ['>', ',', ';', '|', ' ']
        kv_split_char_candidates = ['=', ':']
        first_line = self.lines[0].strip()

        for sc in split_char_candidates:
            fields = first_line.split(sc)
            if len(fields) > 1:
                for kv_sc in kv_split_char_candidates:
                    # Quick skip: does any field contain kv_sc at all?
                    if not any(kv_sc in f for f in fields):
                        continue  # No point in checking if none has kv_sc

                    date_field = self.find_date_field_kv(fields, kv_sc)
                    if date_field is not None:
                        # We found a valid date in 'key=val' form
                        self.split_char = sc
                        self.kv_split_char = kv_sc
                        self.use_key_value = True
                        return True
        return False

    def find_date_field_kv(self, fields, kv_sc):
        """Find a field that includes a date. Return the field if found, else None."""
        for field in fields:
            if kv_sc in field:
                key, value = field.split(kv_sc, 1)
                if self.is_date(value):
                    # We'll store date_key for key=value mode
                    self.date_key = key
                    return field
        return None

    def identify_positional_format(self):
        """
        Attempt to find a single 'split_char' and a single position
        that is interpretable as date in the first line.
        """
        split_char_candidates = ['>', ',', ';', '|', ' ']
        first_line = self.lines[0].strip()

        for sc in split_char_candidates:
            fields = first_line.split(sc)
            # see how many date-like fields we can find
            date_positions = []
            for i, fld in enumerate(fields):
                if self.is_date(fld):
                    print("Found date", i, fld)
                    date_positions.append(i)
            # For simplicity, if there's exactly 1 date field, we pick that as the date index
            if len(date_positions) > 0:
                self.split_char = sc
                self.date_index = date_positions[0]
                # For positional mode, we won't have a date_key
                self.date_key = None
                return True
        # if we get here, we haven't found a workable positional format
        return False

    def is_date(self, text):
        """Check if the text is interpretable as a date or timestamp."""
        # 1) try float -> timestamp
        try:
            timestamp = float(text)
            datetime.datetime.fromtimestamp(timestamp)
            return True
        except:
            pass
        # 2) try common date formats
        date_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S.%f"]
        for fmt in date_formats:
            try:
                datetime.datetime.strptime(text, fmt)
                return True
            except:
                pass
        return False

    # -------------------------------------------------------------------------
    # Key=Value Mode
    # -------------------------------------------------------------------------
    def extract_keys_kv(self):
        """Extract keys from the first line (key=value style)."""
        first_line = self.lines[0].strip()
        fields = first_line.split(self.split_char)
        keys = []
        for field in fields:
            if self.kv_split_char in field:
                key, value = field.split(self.kv_split_char, 1)
                keys.append(key)
        self.keys = keys
        # Filter out the date key
        filtered_keys = [key for key in self.keys if key != self.date_key]
        self.key_choice.SetItems(filtered_keys)
        if filtered_keys:
            self.key_choice.SetSelection(0)

    def extract_dates_kv(self):
        """Extract dates from all lines in key=value mode."""
        self.dates = []
        self.data_lines = []
        for line in self.lines:
            line = line.strip()
            fields = line.split(self.split_char)
            date_found = False
            for field in fields:
                if self.kv_split_char in field:
                    key, val = field.split(self.kv_split_char, 1)
                    if key == self.date_key or self.date_key is None:
                        date = self.parse_date(val)
                        if date:
                            self.dates.append(date)
                            self.data_lines.append(line)
                            date_found = True
                            break
                else:
                    # If date_key is None, we also consider the entire field for a date
                    if self.date_key is None:
                        date = self.parse_date(field)
                        if date:
                            self.dates.append(date)
                            self.data_lines.append(line)
                            date_found = True
                            break
            # If no date found, we skip the line
            if not date_found:
                continue

        self.update_date_info()

    # -------------------------------------------------------------------------
    # Positional (CSV-like) Mode
    # -------------------------------------------------------------------------
    def extract_keys_positional(self):
        """
        In positional mode, we just use numeric indexes as possible keys,
        excluding self.date_index.
        """
        first_line = self.lines[0].strip()
        fields = first_line.split(self.split_char)
        # create a list of indexes as strings, skipping the date_index
        self.positional_keys = [
            str(i) for i in range(len(fields)) if i != self.date_index
        ]
        self.key_choice.SetItems(self.positional_keys)
        if self.positional_keys:
            self.key_choice.SetSelection(0)

    def extract_dates_positional(self):
        """Extract dates by picking the field at self.date_index."""
        self.dates = []
        self.data_lines = []
        for line in self.lines:
            line = line.strip()
            fields = line.split(self.split_char)
            if len(fields) <= self.date_index:
                continue
            date_text = fields[self.date_index]
            date_obj = self.parse_date(date_text)
            if date_obj:
                self.dates.append(date_obj)
                self.data_lines.append(line)

        self.update_date_info()

    # -------------------------------------------------------------------------
    # Common Helpers
    # -------------------------------------------------------------------------
    def parse_date(self, text):
        """Parse a date from text as float or various date formats."""
        # 1) float -> timestamp
        try:
            timestamp = float(text)
            return datetime.datetime.fromtimestamp(timestamp)
        except:
            pass

        # 2) common date formats
        date_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S.%f"]
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(text, fmt)
            except:
                pass
        return None

    def update_date_info(self):
        """Update self.date_info_text with summary of first/last date and duration."""
        if self.dates:
            first_date = self.dates[0]
            last_date = self.dates[-1]
            duration = str(last_date - first_date)
            if "." in duration:
                # strip microseconds, optional
                duration = duration.split(".")[0]
            f_first_date = first_date.strftime("%d-%b-%y %H:%M")
            f_last_date = last_date.strftime("%d-%b-%y %H:%M")
            date_info = f"From: {f_first_date} to {f_last_date}\nDuration: {duration}"
            self.date_info_text.SetLabel(date_info)
        else:
            self.date_info_text.SetLabel("No dates found.")

        self.Layout()
        self.Fit()

    def on_key_selected(self, event):
        """
        When the user picks a key from the choice, we display
        its value from the first line. This logic differs
        slightly based on mode.
        """
        selected_key = self.key_choice.GetStringSelection()
        first_line = self.lines[0].strip()
        fields = first_line.split(self.split_char)

        if self.use_key_value:
            # Key=Value mode
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
        else:
            # Positional mode
            try:
                index = int(selected_key)
                if index < len(fields):
                    self.key_value_text.SetLabel(f"Value: {fields[index]}")
                else:
                    self.key_value_text.SetLabel("Value not found.")
            except:
                self.key_value_text.SetLabel("Value not found.")

        self.Layout()

    def on_import_data(self, event):
        """Load data and add to ctrl_pnl based on whichever mode (K=V or positional)."""
        selected_key = self.key_choice.GetStringSelection()
        data_tuples = []

        if self.use_key_value:
            # Key=Value mode
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
                        pass  # skip lines where value isn't float
        else:
            # Positional mode
            try:
                value_index = int(selected_key)
            except:
                wx.MessageBox("Invalid key selection for positional data.",
                              "Error", wx.OK | wx.ICON_ERROR)
                return

            for line in self.data_lines:
                line = line.strip()
                fields = line.split(self.split_char)
                if len(fields) <= max(self.date_index, value_index):
                    continue
                date_text = fields[self.date_index]
                val_text = fields[value_index]
                date = self.parse_date(date_text)
                if date is not None:
                    try:
                        data_tuples.append((date, float(val_text)))
                    except ValueError:
                        pass  # skip lines with non-numeric data

        # Add the dataset to ctrl_pnl
        dataset = {
            'file_path': self.log_title,
            'key': selected_key,
            'data': data_tuples,
            'trimmed_data': data_tuples,  # Initially same as data
            'split_char': self.split_char,
            'kv_split_char': self.kv_split_char if self.use_key_value else "",
            'date_key': self.date_key
        }
        self.c_pnl.loaded_datasets.append(dataset)
        self.c_pnl.refresh_table()

        # Show Duration Select panel
        self.parent.show_duration_select_panel(dataset)


class DurationSelectPanel(wx.Panel):
    def __init__(self, parent):
        super(DurationSelectPanel, self).__init__(parent)
        self.parent = parent  # Reference to info_pnl
        self.c_pnl = parent.c_pnl  # Reference to ctrl_pnl
        self.current_dataset = None
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top bar label and button
        title_label = wx.StaticText(self, label="Duration Select")
        self.hide_btn = wx.Button(self, label="Hide")
        self.hide_btn.Bind(wx.EVT_BUTTON, self.on_hide)
        topbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        topbar_sizer.Add(title_label, 0, wx.ALL, 5)
        topbar_sizer.AddStretchSpacer()
        topbar_sizer.Add(self.hide_btn, 0, wx.ALL, 5)
        main_sizer.Add(topbar_sizer, 0, wx.EXPAND, 5)

        # Date and Time controls for Start
        start_sizer = wx.BoxSizer(wx.HORIZONTAL)
        start_label = wx.StaticText(self, label="Start:")
        self.start_date_ctrl = wx.adv.DatePickerCtrl(self)
        self.start_time_ctrl = wx.adv.TimePickerCtrl(self)
        start_sizer.Add(start_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        start_sizer.Add(self.start_date_ctrl, 0, wx.ALL, 5)
        start_sizer.Add(self.start_time_ctrl, 0, wx.ALL, 5)
        main_sizer.Add(start_sizer, 0, wx.ALIGN_LEFT)

        # Date and Time controls for End
        end_sizer = wx.BoxSizer(wx.HORIZONTAL)
        end_label = wx.StaticText(self, label="End:")
        self.end_date_ctrl = wx.adv.DatePickerCtrl(self)
        self.end_time_ctrl = wx.adv.TimePickerCtrl(self)
        end_sizer.Add(end_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        end_sizer.Add(self.end_date_ctrl, 0, wx.ALL, 5)
        end_sizer.Add(self.end_time_ctrl, 0, wx.ALL, 5)
        main_sizer.Add(end_sizer, 0, wx.ALIGN_LEFT)

        # Limit to last N time units
        limit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        limit_label = wx.StaticText(self, label="Limit to last:")
        self.limit_text = wx.TextCtrl(self, value="1")
        self.time_unit_choice = wx.Choice(self, choices=["Hour", "Day", "Week", "Month", "Year", "None", "Custom"])
        self.time_unit_choice.SetStringSelection("None")
        limit_sizer.Add(limit_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        limit_sizer.Add(self.limit_text, 0, wx.ALL, 5)
        limit_sizer.Add(self.time_unit_choice, 0, wx.ALL, 5)
        main_sizer.Add(limit_sizer, 0, wx.ALIGN_LEFT)

        # Bind events
        self.limit_text.Bind(wx.EVT_TEXT, self.on_limit_changed)
        self.time_unit_choice.Bind(wx.EVT_CHOICE, self.on_limit_changed)
        self.start_date_ctrl.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_time_changed)
        self.start_time_ctrl.Bind(wx.adv.EVT_TIME_CHANGED, self.on_date_time_changed)
        self.end_date_ctrl.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_time_changed)
        self.end_time_ctrl.Bind(wx.adv.EVT_TIME_CHANGED, self.on_date_time_changed)

        # Trim date to log
        trim_sizer = wx.BoxSizer(wx.HORIZONTAL)
        trim_label = wx.StaticText(self, label="Trim date to log:")
        self.dataset_choice = wx.Choice(self)
        trim_sizer.Add(trim_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        trim_sizer.Add(self.dataset_choice, 0, wx.ALL, 5)
        main_sizer.Add(trim_sizer, 0, wx.ALIGN_LEFT)

        self.dataset_choice.Bind(wx.EVT_CHOICE, self.on_dataset_selected)

        # Info about current selection
        self.info_label = wx.StaticText(self, label="")
        main_sizer.Add(self.info_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def on_hide(self, event):
        self.Hide()
        self.parent.main_sizer.Layout()

    def load_dataset(self, dataset):
        self.current_dataset = dataset
        data = dataset['data']

        # Add "None" to dataset_choice and set it as default
        dataset_names = ["None"]  # None means no 'trim to log'
        # Add other datasets as "trim to log" options
        dataset_names += [d['file_path'] for d in self.c_pnl.loaded_datasets if d != dataset]

        self.dataset_choice.SetItems(dataset_names)
        # Determine mode from dataset (if previously saved in presets)
        trim_mode = dataset.get('trim_mode', 'none')
        if trim_mode == 'none':
            self.dataset_choice.SetSelection(0)  # None selected
        else:
            # Find the dataset in the list
            if trim_mode.startswith('log:'):
                target_ds = trim_mode.split(':', 1)[1]
                idx = self.dataset_choice.FindString(target_ds)
                if idx != wx.NOT_FOUND:
                    self.dataset_choice.SetSelection(idx)
                else:
                    self.dataset_choice.SetSelection(0)
            else:
                self.dataset_choice.SetSelection(0)  # fallback

        # If we have start/end times stored in dataset, apply them
        start_dt = dataset.get('start_datetime')
        end_dt = dataset.get('end_datetime')

        if not data:
            return
        full_start_datetime = data[0][0]
        full_end_datetime = data[-1][0]

        if start_dt is None: start_dt = full_start_datetime
        if end_dt is None: end_dt = full_end_datetime

        # Set date/time pickers
        self.start_date_ctrl.SetRange(
            wx.DateTime.FromDMY(full_start_datetime.day, full_start_datetime.month - 1, full_start_datetime.year),
            wx.DateTime.FromDMY(full_end_datetime.day, full_end_datetime.month - 1, full_end_datetime.year))
        self.end_date_ctrl.SetRange(
            wx.DateTime.FromDMY(full_start_datetime.day, full_start_datetime.month - 1, full_start_datetime.year),
            wx.DateTime.FromDMY(full_end_datetime.day, full_end_datetime.month - 1, full_end_datetime.year))

        self.start_date_ctrl.SetValue(wx.DateTime.FromDMY(start_dt.day, start_dt.month - 1, start_dt.year))
        self.start_time_ctrl.SetValue(wx.DateTime.FromHMS(start_dt.hour, start_dt.minute, start_dt.second))
        self.end_date_ctrl.SetValue(wx.DateTime.FromDMY(end_dt.day, end_dt.month - 1, end_dt.year))
        self.end_time_ctrl.SetValue(wx.DateTime.FromHMS(end_dt.hour, end_dt.minute, end_dt.second))

        # Set Limit to Last default to "None"
        self.time_unit_choice.SetSelection(self.time_unit_choice.FindString("None"))

        # Update UI states based on current selection
        self.update_ui_for_mode()

        self.update_info()

    def on_limit_changed(self, event):
        if not self.current_dataset:
            return

        unit = self.time_unit_choice.GetStringSelection()
        if unit == "None":
            # If None selected, we revert to direct date/time pickers (no special calculation)
            # Just leave date/time as is (user may have set them)
            pass
        elif unit == "Custom":
            # If Custom selected, we rely on the current date/time pickers and treat as custom range
            # No immediate recalculation needed here, apply_trim will handle saving mode
            pass
        else:
            # Unit is Hour/Day/Week/Month/Year
            value = self.limit_text.GetValue()
            try:
                n = int(value)
            except ValueError:
                wx.MessageBox("Please enter a valid number.", "Error", wx.OK | wx.ICON_ERROR)
                return

            now = datetime.datetime.now()
            if unit == "Hour":
                delta = datetime.timedelta(hours=n)
            elif unit == "Day":
                delta = datetime.timedelta(days=n)
            elif unit == "Week":
                delta = datetime.timedelta(weeks=n)
            elif unit == "Month":
                delta = datetime.timedelta(days=30 * n)  # Approximate
            elif unit == "Year":
                delta = datetime.timedelta(days=365 * n)  # Approximate
            else:
                delta = None

            if delta is not None:
                start_datetime = now - delta
                end_datetime = now
                # Set the date/time pickers according to the calculated range
                self.start_date_ctrl.SetValue(
                    wx.DateTime.FromDMY(start_datetime.day, start_datetime.month - 1, start_datetime.year))
                self.start_time_ctrl.SetValue(
                    wx.DateTime.FromHMS(start_datetime.hour, start_datetime.minute, start_datetime.second))
                self.end_date_ctrl.SetValue(
                    wx.DateTime.FromDMY(end_datetime.day, end_datetime.month - 1, end_datetime.year))
                self.end_time_ctrl.SetValue(
                    wx.DateTime.FromHMS(end_datetime.hour, end_datetime.minute, end_datetime.second))

        self.apply_trim()

    def on_dataset_selected(self, event):
        selection = self.dataset_choice.GetStringSelection()
        if selection == "None":
            # None selected, enable date/time pickers and limit fields
            self.enable_datetime_controls(True)
            self.enable_limit_controls(True)
            # Use current dataset's stored start/end if any
            self.apply_trim()
        else:
            # A dataset was selected to 'trim to log'
            # Find that dataset and apply its trimmed range directly, disable date/time controls
            target_dataset = next((d for d in self.c_pnl.loaded_datasets if d['file_path'] == selection), None)
            if target_dataset and target_dataset['trimmed_data']:
                trimmed_data = target_dataset['trimmed_data']
                start_datetime = trimmed_data[0][0]
                end_datetime = trimmed_data[-1][0]

                self.start_date_ctrl.SetValue(
                    wx.DateTime.FromDMY(start_datetime.day, start_datetime.month - 1, start_datetime.year))
                self.start_time_ctrl.SetValue(
                    wx.DateTime.FromHMS(start_datetime.hour, start_datetime.minute, start_datetime.second))
                self.end_date_ctrl.SetValue(
                    wx.DateTime.FromDMY(end_datetime.day, end_datetime.month - 1, end_datetime.year))
                self.end_time_ctrl.SetValue(
                    wx.DateTime.FromHMS(end_datetime.hour, end_datetime.minute, end_datetime.second))

                # Disable other date/time and limit fields
                self.enable_datetime_controls(False)
                self.enable_limit_controls(False)
            else:
                # No data found in that dataset or dataset not found
                # Just disable fields and apply trim to show no data
                self.enable_datetime_controls(False)
                self.enable_limit_controls(False)

            self.apply_trim()

    def on_date_time_changed(self, event):
        self.apply_trim()

    def apply_trim(self):
        if not self.current_dataset:
            return

        data = self.current_dataset['data']
        if not data:
            self.current_dataset['trimmed_data'] = []
            self.update_info()
            self.c_pnl.refresh_table()
            return

        selection = self.dataset_choice.GetStringSelection()
        unit = self.time_unit_choice.GetStringSelection()
        value = self.limit_text.GetValue()

        if selection == "None":
            # No dataset selected for 'trim to log'
            # Determine trim_mode based on unit selection
            if unit == "None":
                # Using exact date/time from pickers => trim_mode = 'none'
                trim_mode = 'none'
                start_datetime, end_datetime = self.get_current_datetime_range_from_pickers()
                trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
                self.current_dataset['start_datetime'] = start_datetime
                self.current_dataset['end_datetime'] = end_datetime

            elif unit == "Custom":
                # Custom means we store exact date/time but mark as 'custom'
                trim_mode = 'custom'
                start_datetime, end_datetime = self.get_current_datetime_range_from_pickers()
                trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
                self.current_dataset['start_datetime'] = start_datetime
                self.current_dataset['end_datetime'] = end_datetime

            else:
                # One of Hour/Day/Week/Month/Year chosen
                # Interpret as 'last:<unit>:<count>'
                try:
                    count = int(value)
                except ValueError:
                    wx.MessageBox("Please enter a valid number for the limit.", "Error", wx.OK | wx.ICON_ERROR)
                    return

                # 'last:<unit>:<count>'
                # In this mode, we do not store start/end directly, as they are derived
                # But we still apply them now to show the user immediate effect
                now = datetime.datetime.now()
                if unit == "Hour":
                    delta = datetime.timedelta(hours=count)
                elif unit == "Day":
                    delta = datetime.timedelta(days=count)
                elif unit == "Week":
                    delta = datetime.timedelta(weeks=count)
                elif unit == "Month":
                    delta = datetime.timedelta(days=30 * count)
                elif unit == "Year":
                    delta = datetime.timedelta(days=365 * count)
                else:
                    delta = None

                if delta is None:
                    # If for some reason unit not recognized, fallback to none
                    trim_mode = 'none'
                    start_datetime, end_datetime = self.get_current_datetime_range_from_pickers()
                    trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
                    self.current_dataset['start_datetime'] = start_datetime
                    self.current_dataset['end_datetime'] = end_datetime
                else:
                    trim_mode = f"last:{unit}:{count}"
                    start_datetime = now - delta
                    end_datetime = now
                    trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
                    # In 'last:' mode, no start/end stored since it's dynamic
                    self.current_dataset['start_datetime'] = None
                    self.current_dataset['end_datetime'] = None

            self.current_dataset['trim_mode'] = trim_mode

        else:
            # 'Trim date to log' selected
            target_dataset = next((d for d in self.c_pnl.loaded_datasets if d['file_path'] == selection), None)
            if target_dataset and target_dataset['trimmed_data']:
                idx = self.c_pnl.loaded_datasets.index(target_dataset)
                self.current_dataset['trim_mode'] = f'log:{idx}'
                # Get the date range from target_dataset's trimmed_data
                ref_start = target_dataset['trimmed_data'][0][0]
                ref_end = target_dataset['trimmed_data'][-1][0]
                data = self.current_dataset['data']
                trimmed_data = [d for d in data if ref_start <= d[0] <= ref_end]
                self.current_dataset['start_datetime'] = None
                self.current_dataset['end_datetime'] = None
            else:
                # If no target dataset found or no trimmed_data, fallback to none
                self.current_dataset['trim_mode'] = 'none'
                start_datetime, end_datetime = self.get_current_datetime_range_from_pickers()
                trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
                self.current_dataset['start_datetime'] = start_datetime
                self.current_dataset['end_datetime'] = end_datetime

        if not trimmed_data:
            trimmed_data = []
            wx.MessageBox("No data in the selected date range.", "Info", wx.OK | wx.ICON_INFORMATION)

        self.current_dataset['trimmed_data'] = trimmed_data
        self.update_info()
        self.c_pnl.refresh_table()

    def get_current_datetime_range_from_pickers(self):
        start_date_wx = self.start_date_ctrl.GetValue()
        start_time_wx = self.start_time_ctrl.GetValue()
        start_datetime = datetime.datetime(
            start_date_wx.GetYear(),
            start_date_wx.GetMonth() + 1,
            start_date_wx.GetDay(),
            start_time_wx.GetHour(),
            start_time_wx.GetMinute(),
            start_time_wx.GetSecond()
        )

        end_date_wx = self.end_date_ctrl.GetValue()
        end_time_wx = self.end_time_ctrl.GetValue()
        end_datetime = datetime.datetime(
            end_date_wx.GetYear(),
            end_date_wx.GetMonth() + 1,
            end_date_wx.GetDay(),
            end_time_wx.GetHour(),
            end_time_wx.GetMinute(),
            end_time_wx.GetSecond()
        )
        return start_datetime, end_datetime

    def update_info(self):
        data_len = len(self.current_dataset['data'])
        trimmed_len = len(self.current_dataset['trimmed_data'])

        if trimmed_len > 0:
            start_date = self.current_dataset['trimmed_data'][0][0]
            end_date = self.current_dataset['trimmed_data'][-1][0]
            duration = end_date - start_date
        else:
            duration = datetime.timedelta(0)

        if "." in str(duration):
            duration = str(duration).split(".")[0]

        info_text = f"Using: {trimmed_len} of {data_len}\nDuration: {duration}"
        self.info_label.SetLabel(info_text)

        self.Layout()
        self.parent.main_sizer.Layout()

    def update_ui_for_mode(self):
        selection = self.dataset_choice.GetStringSelection()
        if selection == "None":
            # Enable date/time and limit fields
            self.enable_datetime_controls(True)
            self.enable_limit_controls(True)
        else:
            # Another dataset is selected, disable date/time and limit fields
            self.enable_datetime_controls(False)
            self.enable_limit_controls(False)

    def enable_datetime_controls(self, enable):
        self.start_date_ctrl.Enable(enable)
        self.start_time_ctrl.Enable(enable)
        self.end_date_ctrl.Enable(enable)
        self.end_time_ctrl.Enable(enable)

    def enable_limit_controls(self, enable):
        self.limit_text.Enable(enable)
        self.time_unit_choice.Enable(enable)


class GraphOptionsPanel(wx.Panel):
    def __init__(self, parent):
        super(GraphOptionsPanel, self).__init__(parent)
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        # Initialize a dictionary to keep track of controls
        self.controls = {}

        self.mpl_style_options = plt.style.available

    def default_graph_opts(self, options_dict):
        defaults = {
            "Y axis Minimum": "",
            "Y axis Maximum": "",
            "Width": "12",
            "Height": "7"
        }
        # Update options_dict with any missing default values
        return {**defaults, **options_dict}

    def update_options(self, options_dict):
        options_dict = self.default_graph_opts(options_dict)
        # Clear existing controls
        self.main_sizer.Clear(True)
        self.controls = {}  # Reset controls dictionary

        # Create a grid sizer with two columns
        grid_sizer = wx.FlexGridSizer(rows=len(options_dict), cols=2, hgap=1, vgap=2)
        grid_sizer.AddGrowableCol(1, 1)

        # Predefined options for special combo boxes
        marker_options = [
            ". point", ", pixel", "o circle", "v triangle_down", "^ triangle_up",
            "< triangle_left", "> triangle_right", "1 tri_down", "2 tri_up",
            "3 tri_left", "4 tri_right", "s square", "p pentagon", "* star",
            "h hexagon1", "H hexagon2", "+ plus", "x x", "D diamond",
            "d thin_diamond", "| vline", "_ hline"
        ]
        linestyle_options = [
            "- solid", "-- dashed", "-. dash_dot", ": dotted", "None None"
        ]

        # Color cycles for the 'color_cycle' option
        color_cycle_options = [
            # High contrast palettes (first five)
            "tab:blue, tab:orange, tab:green, tab:red, tab:purple, tab:brown, tab:pink, tab:gray, tab:olive, tab:cyan",
            # Tableau 'T10'
            "xkcd:bright blue, xkcd:bright green, xkcd:bright red, xkcd:bright purple, xkcd:bright orange",
            # High contrast xkcd colors
            "tab:red, tab:blue, yellow, tab:green, tab:purple, tab:brown",  # Minimal contrast mix
            "xkcd:turquoise, xkcd:lime green, xkcd:deep pink, xkcd:gold, xkcd:violet",  # Vivid contrast colors
            "tab:green, tab:purple, tab:orange, tab:brown, tab:pink",  # Alternating contrast
            # Stylized palettes (next ten)
            "xkcd:soft pink, xkcd:mint green, xkcd:light purple, xkcd:sky blue, xkcd:peach",  # Pastel tones
            "xkcd:dark teal, xkcd:rust, xkcd:dark olive, xkcd:dark purple, xkcd:ochre",  # Earthy tones
            "tab:blue, tab:cyan, xkcd:dark blue, xkcd:sea green, xkcd:navy",  # Cool blues and greens
            "xkcd:wine, xkcd:brick red, xkcd:burnt orange, xkcd:dark brown, xkcd:mustard yellow",  # Warm, muted tones
            "xkcd:cerulean, xkcd:aquamarine, xkcd:seafoam, xkcd:turquoise, xkcd:sky blue",  # Ocean-inspired palette
            "tab:gray, tab:olive, tab:cyan, xkcd:slate, xkcd:charcoal",  # Neutral palette
            "xkcd:sage green, xkcd:dusty rose, xkcd:lavender, xkcd:peach, xkcd:light teal",  # Soft, vintage colors
            "tab:pink, xkcd:light brown, xkcd:mustard, xkcd:coral, tab:red",  # Retro palette
            "xkcd:midnight blue, xkcd:deep red, xkcd:forest green, xkcd:slate gray, xkcd:mustard",  # Dark, bold tones
            "tab:purple, xkcd:rose pink, tab:blue, xkcd:teal, tab:orange"  # Contemporary vibrant mix
        ]

        color_palette_options = [
            "viridis", "plasma", "inferno", "magma", "cividis",  # Sequential color maps
            "tab10", "tab20", "tab20b", "tab20c",  # Categorical color maps
            "Set1", "Set2", "Set3", "Paired", "Accent",  # Other categorical maps
            "Dark2", "Pastel1", "Pastel2",  # Pastel and subdued palettes
            "Spectral", "coolwarm", "bwr", "seismic"  # Diverging color maps
        ]

        legend_position_options = [
            "best", "upper right", "upper left", "lower left", "lower right",
            "right", "center left", "center right", "lower center", "upper center", "center"
        ]

        color_options = [
            "white", "black", "lightgray", "darkgray", "dimgray",  # Grayscale options
            "whitesmoke", "gainsboro", "snow", "ivory",  # Light shades
            "beige", "linen", "seashell", "mintcream", "aliceblue",  # Soft pastel shades
            "lightyellow", "honeydew", "lavender", "azure",  # Subtle tints
            "cornsilk", "ghostwhite", "oldlace", "floralwhite",  # Warm, light shades
            "xkcd:light blue", "xkcd:light pink", "xkcd:light green",  # xkcd colors
            "tab:blue", "tab:gray", "tab:purple", "tab:olive"  # Tableau colors
        ]

        text_color_options = [
            "black", "white", "darkblue", "darkgreen", "darkred", "navy", "midnightblue",
            "indigo", "teal", "darkorange", "maroon", "purple", "saddlebrown",
            "slategray", "grey",
            "tab:blue", "tab:green", "tab:red", "tab:purple",
            "tab:pink" "tab:olive", "tab:cyan",
            "xkcd:light blue", "xkcd:light green", "xkcd:light pink", "xkcd:bright green",
            "xkcd:sky blue", "xkcd:rose", "xkcd:turquoise", "xkcd:light purple"
        ]

        mpl_style_options = self.mpl_style_options

        # Dictionary of special options
        self.special_options = {
            'marker': marker_options,
            'line_style': linestyle_options,
            'color_cycle': color_cycle_options,
            'color_palette': color_palette_options,
            'legend_position': legend_position_options,
            'background_color': color_options,
            'axes_background_color': color_options,
            'grid_color': color_options,
            'title_color': text_color_options,
            'label_color': text_color_options,
            'legend_color': text_color_options,
            'x_axis_color': text_color_options,
            'y_axis_color': text_color_options,
            'x_tick_color': text_color_options,
            'y_tick_color': text_color_options,
            'mpl_style': mpl_style_options
        }

        for key, value in options_dict.items():
            # Left column: key label
            key_label = wx.StaticText(self, label=key)
            key_label.Wrap(150)  # Set maximum width (adjust value as needed)
            grid_sizer.Add(key_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)


            # Determine the control for the right column
            control = None

            # Check for boolean values
            if str(value).lower() == 'true' or str(value).lower() == 'false' and not key in self.special_options:
                checkbox = wx.CheckBox(self)
                checkbox.SetValue(str(value).lower() == 'true')
                control = checkbox
            # Check for special options
            elif key in self.special_options:
                choices = self.special_options[key]
                combo = wx.ComboBox(self, choices=choices)
                combo.SetMinSize((200, -1))
                current_value = value
                # Find the option that starts with the current value
                if current_value != "":
                    for option in choices:
                        if option.startswith(current_value):
                            combo.SetStringSelection(option)
                            break
                control = combo
            # Check if value is a list
            elif isinstance(value, list):
                # If value is a list, create a combo with these as options
                if value:  # Ensure not empty
                    combo = wx.ComboBox(self, choices=value)
                    combo.SetMinSize((200, -1))
                    # Select the first item by default
                    combo.SetSelection(0)
                    control = combo
                else:
                    # If for some reason it's an empty list, just create a text ctrl
                    text_ctrl = wx.TextCtrl(self, value="")
                    control = text_ctrl
            else:
                # Default to text control
                text_ctrl = wx.TextCtrl(self, value=str(value))
                control = text_ctrl

            # Add control to the grid sizer
            grid_sizer.Add(control, 0, wx.EXPAND | wx.ALL, 1)

            # Store the control with its corresponding key
            self.controls[key] = control

        # Add grid sizer to main sizer
        self.main_sizer.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Refresh layout
        self.Layout()
        self.Fit()

    def apply_settings(self, settings_dict):
        """Apply settings to existing controls without changing the layout."""
        for key, value in settings_dict.items():
            if key in self.controls:
                control = self.controls[key]
                if isinstance(control, wx.CheckBox):
                    control.SetValue(str(value).lower() == 'true')
                elif isinstance(control, wx.ComboBox):
                    choices = control.GetItems()
                    # If value is in choices, set selection
                    # Otherwise, set the value directly
                    if value in choices:
                        control.SetStringSelection(value)
                    else:
                        control.SetValue(value)
                elif isinstance(control, wx.TextCtrl):
                    control.SetValue(str(value))
                else:
                    # Handle other control types if necessary
                    pass
            else:
                # Key not in controls, ignore
                pass

    def get_options(self):
        """Reads all controls and returns a dictionary of settings."""
        options = {}
        trim_by_space = ["line_style", "marker"]

        for key, control in self.controls.items():
            if isinstance(control, wx.CheckBox):
                options[key] = 'true' if control.GetValue() else 'false'
            elif isinstance(control, wx.ComboBox):
                value = control.GetValue()
                if key in trim_by_space:
                    value = value.split(' ')[0]
                options[key] = value
            elif isinstance(control, wx.TextCtrl):
                options[key] = control.GetValue()
            else:
                # Handle other control types if necessary
                options[key] = control.GetValue()

        return options


class GraphPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        # Main Sizer for Graph Panel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Section
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_label = wx.StaticText(self, label="Graphs")
        clear_button = wx.Button(self, label="Clear")
        header_sizer.Add(title_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        header_sizer.AddStretchSpacer()
        header_sizer.Add(clear_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Content Section (For Graphs)
        self.graph_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.graph_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.sizer)

        # Event Binding
        clear_button.Bind(wx.EVT_BUTTON, self.clear_graphs)

        # Store graph paths for later use
        self.graphs = []

    def add_graph(self, graph_path):
        """Add a graph image to the panel."""
        bmp = wx.Image(graph_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.StaticBitmap(self, bitmap=bmp)
        bitmap.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.on_double_click(graph_path))

        # Add the image to the top
        self.graph_sizer.Insert(0, bitmap, 0, wx.CENTER | wx.ALL, 5)
        self.graphs.insert(0, graph_path)

        # Update Layout
        self.sizer.Layout()
        self.GetParent().FitInside()  # Update the scrolled panel's size

    def clear_graphs(self, event=None):
        """Clear all graphs from the panel."""
        for child in self.graph_sizer.GetChildren():
            child.GetWindow().Destroy()
        self.graph_sizer.Clear()
        self.graphs.clear()

        # Update Layout
        self.sizer.Layout()
        self.GetParent().FitInside()

    def on_double_click(self, graph_path):
        """Handle double-click event on a graph."""
        print(f"Graph clicked: {graph_path}")

class SuckerDialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(SuckerDialog, self).__init__(parent, *args, **kw)
        self.parent = parent
        self.module = None  # Placeholder for dynamically loaded module
        self.settings_dict = {}  # Settings from the selected module
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog user interface."""
        self.SetTitle("Data Sucker Module")
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, label="Data Sucker Module")
        subtitle = wx.StaticText(self, label="Load data from online or local sources using custom modules")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, flag=wx.ALL, border=10)
        main_sizer.Add(subtitle, flag=wx.ALL, border=10)

        # Dropdown for module selection
        self.module_dropdown = wx.ComboBox(self, choices=self.get_available_modules(), style=wx.CB_READONLY)
        self.module_dropdown.Bind(wx.EVT_COMBOBOX, self.on_module_select)
        main_sizer.Add(wx.StaticText(self, label="Select a Module:"), flag=wx.LEFT, border=10)
        main_sizer.Add(self.module_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Horizontal sizer for options and description
        options_description_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Scrollable panel for options
        self.scroll_panel = scrolled.ScrolledPanel(self, style=wx.VSCROLL)
        self.scroll_panel.SetAutoLayout(1)
        self.scroll_panel.SetupScrolling()
        self.scroll_sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        self.scroll_panel.SetSizer(self.scroll_sizer)
        options_description_sizer.Add(self.scroll_panel, proportion=2, flag=wx.EXPAND | wx.ALL, border=10)

        # Text box for description
        self.description_box = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP)
        self.description_box.SetMinSize((250, -1))  # Default minimum width
        self.description_box.SetValue("No description available")  # Default text
        options_description_sizer.Add(self.description_box, proportion=3, flag=wx.EXPAND | wx.ALL, border=10)

        main_sizer.Add(options_description_sizer, proportion=1, flag=wx.EXPAND)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_button = wx.Button(self, label="Add Dataset")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_dataset)
        self.done_button = wx.Button(self, label="Done")
        self.done_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_sizer.Add(self.add_button, flag=wx.RIGHT, border=5)
        button_sizer.Add(self.done_button, flag=wx.RIGHT, border=5)
        main_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(main_sizer)
        self.SetSize((800, 500))

    def get_available_modules(self):
        """Scan the graph_modules folder for available 'sucker_' modules."""
        modules = []
        module_path = "./graph_modules/"
        for filename in os.listdir(module_path):
            if filename.startswith("sucker_") and filename.endswith(".py"):
                module_name = filename[7:-3]  # Remove 'sucker_' prefix and '.py' suffix
                modules.append(module_name)
        return modules

    def on_module_select(self, event):
        """Load the selected module and display its options."""
        self.selected_module = self.module_dropdown.GetValue()
        if not self.selected_module:
            return

        # Dynamically import the selected module
        try:
            module_name = f"graph_modules.sucker_{self.selected_module}"
            self.module = importlib.import_module(module_name)
            self.settings_dict = self.module.read_datasucker_options()
            self.populate_options()

            # Load module description
            description = getattr(self.module, "read_description", lambda: "No description available")()
            self.description_box.SetValue(description)
        except Exception as e:
            wx.MessageBox(f"Error loading module: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def populate_options(self):
        """Populate the scroll panel with settings controls."""
        self.scroll_sizer.Clear(True)  # Clear existing controls

        for key, value in self.settings_dict.items():
            self.scroll_sizer.Add(wx.StaticText(self.scroll_panel, label=key), flag=wx.ALIGN_CENTER_VERTICAL)

            if isinstance(value, list):
                # Dropdown for list options
                control = wx.ComboBox(self.scroll_panel, choices=value, style=wx.CB_READONLY)
                control.SetSelection(0)  # Default to the first item
            elif isinstance(value, str) and value.startswith("DATE$"):
                # Date and time picker
                if value == "DATE$NOW":
                    default_date = datetime.datetime.now()
                else:
                    default_date = datetime.datetime(datetime.datetime.now().year, 1, 1)
                control = wx.adv.DatePickerCtrl(self.scroll_panel, dt=wx.DateTime.FromDMY(
                    default_date.day, default_date.month - 1, default_date.year))
            else:
                # Text control for other types
                control = wx.TextCtrl(self.scroll_panel, value=str(value))

            control.SetName(key)  # Store the key in the control name
            self.scroll_sizer.Add(control, flag=wx.EXPAND)

        self.scroll_panel.Layout()
        self.scroll_panel.SetupScrolling()

    def on_add_dataset(self, event=None):
        """Run the selected module and add the dataset."""
        if not self.module or not self.settings_dict:
            wx.MessageBox("No module or settings available.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Read the current settings from the controls
        for child in self.scroll_panel.GetChildren():
            if isinstance(child, wx.Control):
                key = child.GetName()
                if isinstance(child, wx.ComboBox):
                    self.settings_dict[key] = child.GetValue()
                elif isinstance(child, wx.adv.DatePickerCtrl):
                    dt = child.GetValue()
                    if self.settings_dict[key] == "DATE$":
                        self.settings_dict[key] = dt.FormatISODate() + " 00:00"
                    elif self.settings_dict[key] == "DATE$NOW":
                        self.settings_dict[key] = dt.FormatISODate() + " 23:59"
                    else:
                        self.settings_dict[key] = dt.FormatISODate() + " 00:00"
                elif isinstance(child, wx.TextCtrl):
                    self.settings_dict[key] = child.GetValue()

        try:
            # Run the module's suckdata method with current settings
            selected_key, data = self.module.suckdata(self.settings_dict)
            dataset = {
                "file_path": self.selected_module + ":M",
                "key": selected_key,
                "data": data,
                "trimmed_data": data,
                "ds_settings": self.settings_dict
            }
            self.parent.loaded_datasets.append(dataset)
            self.parent.refresh_table()  # Refresh table
            wx.MessageBox(f"Dataset '{selected_key}' added successfully.", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error adding dataset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event=None):
        self.Close()

class GraphPreset:
    def __init__(self, parent):
        self.parent = parent
        self.preset_folder = "./graph_presets/"
        if not os.path.exists(self.preset_folder):
            os.makedirs(self.preset_folder)

    def get_preset_list(self):
        # Return a list of .json files in the preset folder
        preset_files = []
        if os.path.isdir(self.preset_folder):
            for filename in os.listdir(self.preset_folder):
                if filename.endswith('.json'):
                    preset_files.append(filename[:-5])  # Remove '.json' extension
        return preset_files

    def save_preset(self, parent, loaded_datasets, graph_type, graph_settings):
        # Prompt the user for the preset name
        dlg = wx.TextEntryDialog(parent, "Enter a name for the preset:", "Save Preset")
        if dlg.ShowModal() == wx.ID_OK:
            preset_name = dlg.GetValue()
            if preset_name:
                # Construct datasets list
                datasets_list = self.construct_datasets_list(loaded_datasets)
                # Build graph information
                graph_info = {'type': graph_type}
                if graph_settings:
                    graph_info['settings'] = graph_settings
                # Create the JSON structure
                preset_data = {
                    'datasets': datasets_list,
                    'graph': graph_info
                }
                # Save the preset data to a JSON file
                preset_file = os.path.join(self.preset_folder, preset_name + '.json')
                try:
                    with open(preset_file, 'w') as f:
                        json.dump(preset_data, f, indent=4)
                    print(f"Preset saved to {preset_file}")
                except Exception as e:
                    print(f"Failed to save preset: {e}")
            else:
                wx.MessageBox("Preset name cannot be empty.", "Error", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def construct_datasets_list(self, loaded_datasets):
        datasets_list = []
        for dataset in loaded_datasets:
            dataset_entry = {
                'key': dataset.get('key', ''),
                'trim_mode': dataset.get('trim_mode', 'none')
            }

            trim_mode = dataset_entry['trim_mode']
            if trim_mode == 'none':
                trim_to_last = None
            elif trim_mode == 'custom':
                # Store start/end times if available
                start_dt = dataset.get('start_datetime')
                end_dt = dataset.get('end_datetime')
                if start_dt:
                    dataset_entry['start_datetime'] = start_dt.isoformat()
                if end_dt:
                    dataset_entry['end_datetime'] = end_dt.isoformat()
            elif trim_mode.startswith('last:'):
                # not needed?
                trim_to_last = trim_mode[5:]
                pass
            elif trim_mode.startswith('log:'):
                # log:<index>, no start/end needed
                pass

            # Store other dataset-specific info (same as before)
            if 'split_char' in dataset:
                dataset_entry.update({
                    'file_path': dataset.get('file_path', ''),
                    'split_char': dataset.get('split_char', ''),
                    'kv_split_char': dataset.get('kv_split_char', ''),
                    'date_key': dataset.get('date_key', None)
                })

            if 'ds_settings' in dataset:
                ds_settings = dataset.get('ds_settings', {})
                if 'file_path' in dataset and dataset['file_path'].endswith(':M'):
                    module_name = dataset['file_path'][:-2]  # remove ':M'
                    dataset_entry['module_name'] = module_name
                    dataset_entry['ds_settings'] = ds_settings

            if 'base_path' in dataset and 'cap_set' in dataset:
                dataset_entry.update({
                    'base_path': dataset.get('base_path', ''),
                    'cap_set': dataset.get('cap_set', '')
                })

            datasets_list.append(dataset_entry)

        return datasets_list

    def load_preset(self, parent, preset_name=None):
        # If no name is given, use the preset currently selected in the GUI
        if preset_name is None:
            preset_name = parent.preset_choice.GetStringSelection()

        preset_file = os.path.join(self.preset_folder, preset_name + '.json')
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
            datasets_info = preset_data.get('datasets', [])

            # Clear existing datasets
            parent.loaded_datasets = []
            for dataset_params in datasets_info:
                ds = self.construct_dataset_from_params(parent, dataset_params)
                parent.loaded_datasets.append(ds)
            parent.refresh_table()

                        # After all datasets are loaded, re-apply trimming logic
            self.reapply_trimming(parent.loaded_datasets)
            parent.refresh_table()

            # Update graph selection and options
            graph_info = preset_data.get('graph', {})
            graph_type = graph_info.get('type', '')
            parent.graph_choice.SetStringSelection(graph_type)
            if 'settings' in graph_info:
                options = graph_info['settings']
                parent.options_panel.update_options(options)
                parent.configure_graph_chk.SetValue(True)
            else:
                parent.configure_graph_chk.SetValue(False)
        else:
            print(f"Preset file {preset_file} does not exist.")

    def load_dataset_preset(self, parent, preset_name):
        """
        loads the preset file (by name) and returns the list
        of dataset dictionaries that it contains.
        """
        preset_file = os.path.join(self.preset_folder, preset_name + '.json')
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
            datasets_info = preset_data.get('datasets', [])
            dataset_list = []
            for dataset_params in datasets_info:
                ds = self.construct_dataset_from_params(parent, dataset_params)
                dataset_list.append(ds)
            return dataset_list
        else:
            print(f"Preset file {preset_file} does not exist.")
            return None

    def construct_dataset_from_params(self, parent, dataset_params):
        """
        Given a dataset parameters dictionary (from the preset JSON),
        create a dataset dictionary in the same format used by the graphs tab.
        """
        dataset = {
            'data': [],
            'trimmed_data': [],
            'trim_mode': dataset_params.get('trim_mode', 'none'),
            'key': dataset_params.get('key', '')
        }
        # For 'custom' mode load start/end times if available.
        if dataset['trim_mode'] == 'custom':
            start_str = dataset_params.get('start_datetime')
            end_str = dataset_params.get('end_datetime')
            if start_str and end_str:
                dataset['start_datetime'] = datetime.datetime.fromisoformat(start_str)
                dataset['end_datetime'] = datetime.datetime.fromisoformat(end_str)
            else:
                dataset['start_datetime'] = None
                dataset['end_datetime'] = None
        else:
            print("SET TRIM MODE TO", dataset['trim_mode'])
            dataset['start_datetime'] = None
            dataset['end_datetime'] = None

        # Now call the appropriate loader based on the dataset parameters.
        if 'module_name' in dataset_params:
            module_name = dataset_params.get('module_name')
            ds_settings = dataset_params.get('ds_settings', {})
            self.load_datasucker_dataset(parent, module_name, ds_settings, dataset)
        elif 'split_char' in dataset_params:
            file_path = dataset_params.get('file_path', '')
            split_char = dataset_params.get('split_char', '')
            kv_split_char = dataset_params.get('kv_split_char', '')
            date_key = dataset_params.get('date_key', None)
            self.load_log_dataset(parent, file_path, dataset['key'], split_char, kv_split_char, date_key, dataset)
        elif 'base_path' in dataset_params and 'cap_set' in dataset_params:
            base_path = dataset_params.get('base_path', '')
            cap_set = dataset_params.get('cap_set', '')
            self.load_caps_dataset(parent, base_path, cap_set, dataset['key'], dataset)
        return dataset

    def reapply_trimming(self, loaded_datasets):
        """
        After all datasets are loaded, re-apply trimming logic based on trim_mode.
        This now also ensures that datasets referencing 'log:<index>' modes
        can correctly find the corresponding dataset by index.
        """
        # First pass: handle none, custom, last
        for dataset in loaded_datasets:
            trim_mode = dataset.get('trim_mode', 'none')
            if trim_mode == 'custom':
                data = dataset['data']
                start_dt = dataset.get('start_datetime')
                end_dt = dataset.get('end_datetime')
                if start_dt and end_dt:
                    trimmed = [d for d in data if start_dt <= d[0] <= end_dt]
                else:
                    trimmed = data
                dataset['trimmed_data'] = trimmed if trimmed else []
            elif trim_mode.startswith('last:'):
                parts = trim_mode.split(':')
                if len(parts) == 3:
                    _, unit, count_str = parts
                    try:
                        count = int(count_str.strip())
                    except ValueError:
                        count = 1
                    now = datetime.datetime.now()
                    if unit == "Hour":
                        delta = datetime.timedelta(hours=count)
                    elif unit == "Day":
                        delta = datetime.timedelta(days=count)
                    elif unit == "Week":
                        delta = datetime.timedelta(weeks=count)
                    elif unit == "Month":
                        delta = datetime.timedelta(days=30 * count)
                    elif unit == "Year":
                        delta = datetime.timedelta(days=365 * count)
                    else:
                        delta = None

                    data = dataset['data']
                    if delta:
                        start_dt = now - delta
                        end_dt = now
                        trimmed = [d for d in data if start_dt <= d[0] <= end_dt]
                    else:
                        trimmed = data
                    dataset['trimmed_data'] = trimmed if trimmed else []
                else:
                    print(f"Trimming data to {parts} failed.")
                    dataset['trimmed_data'] = dataset['data']
            # log: handled in second pass

        # Second pass: handle log: references
        for dataset in loaded_datasets:
            trim_mode = dataset.get('trim_mode', 'none')
            if trim_mode.startswith('log:'):
                parts = trim_mode.split(':', 1)
                if len(parts) == 2:
                    index_str = parts[1]
                    try:
                        idx = int(index_str)
                    except ValueError:
                        idx = None

                    if idx is not None and 0 <= idx < len(loaded_datasets):
                        ref_dataset = loaded_datasets[idx]
                        if ref_dataset['trimmed_data']:
                            ref_start = ref_dataset['trimmed_data'][0][0]
                            ref_end = ref_dataset['trimmed_data'][-1][0]
                            data = dataset['data']
                            trimmed = [d for d in data if ref_start <= d[0] <= ref_end]
                            dataset['trimmed_data'] = trimmed if trimmed else []
                        else:
                            dataset['trimmed_data'] = []
                    else:
                        dataset['trimmed_data'] = []
                else:
                    dataset['trimmed_data'] = dataset['data']

    def load_caps_dataset(self, parent, base_path, cap_set, key, dataset):
        try:
            date_from_filename = parent.parent.dict_I_pnl['timelapse_pnl'].date_from_filename
            files = [f for f in os.listdir(base_path) if f.startswith(cap_set) and f.endswith('.json')]
            if not files:
                wx.MessageBox(f"No JSON files found in {base_path} with prefix '{cap_set}'.", "Error",
                              wx.OK | wx.ICON_ERROR)
                return

            data_tuples = []
            for file in files:
                file_path = os.path.join(base_path, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                value = data.get(key, None)
                date_tuple = date_from_filename(file)
                if date_tuple:
                    _, date = date_tuple
                else:
                    date = None
                if date and value is not None:
                    data_tuples.append((date, value))

            data_tuples.sort(key=lambda x: x[0])
            if not data_tuples:
                # If empty, no data for that dataset
                pass
            dataset['data'] = data_tuples
            dataset['trimmed_data'] = data_tuples
            dataset['base_path'] = base_path
            dataset['cap_set'] = cap_set
            dataset['file_path'] = base_path + ":J"
        except Exception as e:
            wx.MessageBox(f"Error loading dataset from caps folder: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def load_datasucker_dataset(self, parent, module_name, ds_settings, dataset):
        try:
            module_full_name = f"graph_modules.sucker_{module_name}"
            module = importlib.import_module(module_full_name)
            selected_key, data = module.suckdata(ds_settings)
            dataset['data'] = data
            dataset['trimmed_data'] = data
            dataset['ds_settings'] = ds_settings
            dataset['file_path'] = module_name + ":M"
            dataset['key'] = selected_key
        except Exception as e:
            wx.MessageBox(f"Error loading dataset from module '{module_name}': {e}", "Error", wx.OK | wx.ICON_ERROR)

    def load_log_dataset(self, parent, file_path, key, split_char, kv_split_char, date_key, dataset):
        try:
            full_file_path = os.path.join(self.parent.shared_data.frompi_path, 'logs', file_path)
            with open(full_file_path, 'r') as f:
                lines = f.readlines()
            data_tuples = []
            for line in lines:
                line = line.strip()
                fields = line.split(split_char)
                date = None
                value = None
                for field in fields:
                    if kv_split_char in field:
                        k, val = field.split(kv_split_char, 1)
                        if k == key:
                            value = val
                        if k == date_key or date_key is None:
                            date = self.parse_date(val)
                    else:
                        if date_key is None:
                            date = self.parse_date(field)
                if date and value is not None:
                    try:
                        data_tuples.append((date, float(value)))
                    except ValueError:
                        continue
            dataset['data'] = data_tuples
            dataset['trimmed_data'] = data_tuples
            dataset['file_path'] = file_path
            dataset['split_char'] = split_char
            dataset['kv_split_char'] = kv_split_char
            dataset['date_key'] = date_key
            dataset['key'] = key
        except Exception as e:
            wx.MessageBox(f"Failed to load log file: {e}", "Error", wx.OK | wx.ICON_ERROR)
            dataset['data'] = []
            dataset['trimmed_data'] = []
            dataset['file_path'] = 'log not found'
            dataset['split_char'] = ''
            dataset['kv_split_char'] = ''
            dataset['date_key'] = None
            dataset['key'] = key

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

