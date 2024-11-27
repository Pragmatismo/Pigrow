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

        self.graph_choice.SetItems(self.graph_names)
        if self.graph_names:
            self.graph_choice.SetSelection(0)

    def on_make_graph(self, event):
        datasets = self.prepare_datasets_for_graph()
        # Get selected graph and options
        selected_graph = self.graph_choice.GetStringSelection()
        if not selected_graph:
            wx.MessageBox("Please select a graph.", "Error", wx.OK | wx.ICON_ERROR)
            return

        options = self.options_panel.get_options()

        # Extract values from options with default conversion
        ymax = options.get("Y axis Maximum", "")
        if not ymax == "":
            try:
                int(ymax)
            except:
                ymax = ""
        ymin = options.get("Y axis Minimum", "")
        if not ymin == "":
            try:
                int(ymin)
            except:
                ymin = ""

        size_h = int(options.get("Width", 12))
        size_v = int(options.get("Height", 7))

        # Define the graph file path
        module_name = f"graph_{selected_graph}"
        file_name = module_name + "_graph.png"
        graph_path = os.path.join(self.shared_data.frompi_path, file_name)

        # Import the selected graph module and make the graph
        graph_modules_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'graph_modules'))

        # Add graph_modules_dir to sys.path if not already present
        if graph_modules_dir not in sys.path:
            sys.path.insert(0, graph_modules_dir)

        try:
            # Load or reload the module
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                graph_module = sys.modules[module_name]
            else:
                graph_module = importlib.import_module(module_name)

            # Ensure 'make_graph' function exists in the module
            if hasattr(graph_module, 'make_graph'):
                make_graph = graph_module.make_graph

                # Time the graph creation
                start_time = time.time()
                make_graph(datasets, graph_path, ymax, ymin, size_h, size_v, None, None, None, None,
                           options)
                end_time = time.time()

                elapsed_time = round(end_time - start_time, 2)
                print(f"{module_name} graph created in {elapsed_time} seconds and saved to {graph_path}")
                self.parent.dict_I_pnl['graphs_pnl'].add_graph_to_panel(graph_path)
            else:
                print(f"The module '{module_name}' does not have a 'make_graph' function.")
        except Exception as e:
            raise
            print(f"Failed to import or execute '{module_name}':\n{e}")

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
                    print(f"Graph options for '{selected_graph}':\n{options}")
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
        self.grid.ClearGrid()

        # Update the grid with the new dataset length
        self.grid.DeleteRows(0, self.grid.GetNumberRows())  # Clear all rows
        self.grid.AppendRows(len(self.loaded_datasets))  # Add the number of rows we need

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


        self.grid.AutoSizeColumns()  # Adjust column sizes
        self.adjust_table_size()  # Adjust table size after refreshing

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
        dataset = {
            'file_path': self.caps_set[0],
            'key': selected_key,
            'data': self.data_tuples,
            'trimmed_data': self.data_tuples,
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
        wx.MessageBox("Loading logs from Pi not yet coded", "Info", wx.OK | wx.ICON_INFORMATION)

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

            # Proceed to load the file
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
        self.extract_dates()
        filtered_keys = [key for key in self.keys if key != self.date_key]
        self.key_choice.SetItems(filtered_keys)
        self.key_choice.SetSelection(0)


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
            duration = str(last_date - first_date)
            f_first_date = first_date.strftime("%d-%b-%y %H:%M")
            f_last_date = last_date.strftime("%d-%b-%y %H:%M")
            if "." in duration:
                duration = duration.split(".")[0]
            date_info = f"From: {f_first_date} to {f_last_date}\nDuration: {duration}"
            self.date_info_text.SetLabel(date_info)
        else:
            self.date_info_text.SetLabel("No dates found.")
        self.Layout()
        self.Fit()

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
        self.Layout()

    def on_import_data(self, event):
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
        dataset = {
            'file_path': self.log_title,
            'key': selected_key,
            'data': data_tuples,
            'trimmed_data': data_tuples,  # Initially same as data
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
        self.time_unit_choice = wx.Choice(self, choices=["Hour", "Day", "Week", "Month", "Year", "None"])
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
        trimmed_data = dataset['trimmed_data']

        if not data:
            wx.MessageBox("No data available in the selected dataset.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Set the date and time controls to the range of the trimmed data
        if len(trimmed_data) > 0:
            start_datetime = trimmed_data[0][0]
            end_datetime = trimmed_data[-1][0]

            # Set the date and time pickers
            self.start_date_ctrl.SetValue(wx.DateTime.FromDMY(start_datetime.day, start_datetime.month - 1, start_datetime.year))
            self.start_time_ctrl.SetValue(wx.DateTime.FromHMS(start_datetime.hour, start_datetime.minute, start_datetime.second))
            self.end_date_ctrl.SetValue(wx.DateTime.FromDMY(end_datetime.day, end_datetime.month - 1, end_datetime.year))
            self.end_time_ctrl.SetValue(wx.DateTime.FromHMS(end_datetime.hour, end_datetime.minute, end_datetime.second))

        # Limit the date controls to the range of the full data
        full_start_datetime = data[0][0]
        full_end_datetime = data[-1][0]

        self.start_date_ctrl.SetRange(wx.DateTime.FromDMY(full_start_datetime.day, full_start_datetime.month - 1, full_start_datetime.year),
                                      wx.DateTime.FromDMY(full_end_datetime.day, full_end_datetime.month - 1, full_end_datetime.year))
        self.end_date_ctrl.SetRange(wx.DateTime.FromDMY(full_start_datetime.day, full_start_datetime.month - 1, full_start_datetime.year),
                                    wx.DateTime.FromDMY(full_end_datetime.day, full_end_datetime.month - 1, full_end_datetime.year))

        # Update dataset choices for 'trim date to log'
        dataset_names = [d['file_path'] for d in self.c_pnl.loaded_datasets if d != dataset]
        self.dataset_choice.SetItems(dataset_names)

        # Update info
        self.update_info()

    def on_limit_changed(self, event):
        if not self.current_dataset:
            return
        value = self.limit_text.GetValue()
        try:
            n = int(value)
        except ValueError:
            wx.MessageBox("Please enter a valid number.", "Error", wx.OK | wx.ICON_ERROR)
            return
        unit = self.time_unit_choice.GetStringSelection()
        now = datetime.datetime.now()
        end_datetime = now

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

        if delta == None:
            start_datetime = self.current_dataset['data'][0][0]
        else:
            start_datetime = now - delta

        # Set the date and time pickers
        self.start_date_ctrl.SetValue(wx.DateTime.FromDMY(start_datetime.day, start_datetime.month - 1, start_datetime.year))
        self.start_time_ctrl.SetValue(wx.DateTime.FromHMS(start_datetime.hour, start_datetime.minute, start_datetime.second))
        self.end_date_ctrl.SetValue(wx.DateTime.FromDMY(end_datetime.day, end_datetime.month - 1, end_datetime.year))
        self.end_time_ctrl.SetValue(wx.DateTime.FromHMS(end_datetime.hour, end_datetime.minute, end_datetime.second))

        self.apply_trim()

    def on_dataset_selected(self, event):
        selected_dataset_name = self.dataset_choice.GetStringSelection()
        selected_dataset = next((d for d in self.c_pnl.loaded_datasets if d['file_path'] == selected_dataset_name), None)
        if selected_dataset:
            trimmed_data = selected_dataset['trimmed_data']
            start_datetime = trimmed_data[0][0]
            end_datetime = trimmed_data[-1][0]

            # Update the date and time pickers
            self.start_date_ctrl.SetValue(wx.DateTime.FromDMY(start_datetime.day, start_datetime.month - 1, start_datetime.year))
            self.start_time_ctrl.SetValue(wx.DateTime.FromHMS(start_datetime.hour, start_datetime.minute, start_datetime.second))
            self.end_date_ctrl.SetValue(wx.DateTime.FromDMY(end_datetime.day, end_datetime.month - 1, end_datetime.year))
            self.end_time_ctrl.SetValue(wx.DateTime.FromHMS(end_datetime.hour, end_datetime.minute, end_datetime.second))

            self.apply_trim()

    def on_date_time_changed(self, event):
        self.apply_trim()

    def apply_trim(self):
        if not self.current_dataset:
            return

        data = self.current_dataset['data']

        # Get start datetime
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

        # Get end datetime
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

        # Ensure start_datetime is before end_datetime
        if start_datetime > end_datetime:
            wx.MessageBox("Start date/time must be before end date/time.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Trim the data
        trimmed_data = [d for d in data if start_datetime <= d[0] <= end_datetime]
        self.current_dataset['trimmed_data'] = trimmed_data

        # Update info
        self.update_info()

        # Refresh the table in ctrl_pnl
        self.c_pnl.refresh_table()

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


class GraphOptionsPanel(wx.Panel):
    def __init__(self, parent):
        super(GraphOptionsPanel, self).__init__(parent)
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        # Initialize a dictionary to keep track of controls
        self.controls = {}

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

        mpl_style_options = [
            "default", "classic", "Solarize_Light2", "bmh", "dark_background",
            "fast", "fivethirtyeight", "ggplot", "grayscale", "seaborn",
            "seaborn-bright", "seaborn-colorblind", "seaborn-dark",
            "seaborn-dark-palette", "seaborn-darkgrid", "seaborn-deep",
            "seaborn-muted", "seaborn-notebook", "seaborn-paper",
            "seaborn-pastel", "seaborn-poster", "seaborn-talk", "seaborn-ticks",
            "seaborn-white", "seaborn-whitegrid", "tableau-colorblind10"
        ]

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
        selected_module = self.module_dropdown.GetValue()
        if not selected_module:
            return

        # Dynamically import the selected module
        try:
            module_name = f"graph_modules.sucker_{selected_module}"
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
            data_label, selected_key, data = self.module.suckdata(self.settings_dict)
            dataset = {
                "file_path": data_label,
                "key": selected_key,
                "data": data,
                "trimmed_data": data,
            }
            self.parent.loaded_datasets.append(dataset)
            self.parent.refresh_table()  # Refresh table
            wx.MessageBox(f"Dataset '{selected_key}' added successfully.", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error adding dataset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event=None):
        """Close the dialog."""
        self.Close()
