import wx
import wx.grid as gridlib
import wx.lib.scrolledpanel as scrolled
import os

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

        # Bind button event for adding datasets
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_dataset)

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
