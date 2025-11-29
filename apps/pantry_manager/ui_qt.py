import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QDialog, QFormLayout, QMessageBox, QComboBox,
    QAbstractItemView, QInputDialog, QFileDialog, QListWidget, QListWidgetItem
)
import csv
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor

from .database import DatabaseManager
from .api import OpenFoodFactsAPI

"""
Pantry Manager UI Module.

This is the main UI for the Pantry Manager. It handles showing your inventory, 
letting you add/edit/delete stuff, and managing where everything is stored.
"""

from src.ui.theme import Theme

"""
Pantry Manager UI Module.

This is the main UI for the Pantry Manager. It handles showing your inventory, 
letting you add/edit/delete stuff, and managing where everything is stored.
"""

STYLESHEET = f"""
    QMainWindow {{
        background-color: {Theme.BACKGROUND_COLOR};
        color: {Theme.TEXT_PRIMARY};
    }}
    QWidget {{
        background-color: {Theme.BACKGROUND_COLOR};
        color: {Theme.TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }}
    QTableWidget {{
        background-color: {Theme.BACKGROUND_COLOR};
        alternate-background-color: {Theme.GLASS_COLOR};
        gridline-color: {Theme.GLASS_BORDER};
        border: {Theme.GLASS_BORDER};
        border-radius: 8px;
        selection-background-color: {Theme.ACCENT_COLOR};
        selection-color: {Theme.TEXT_PRIMARY};
        outline: 0;
    }}
    QTableWidget::item {{
        color: {Theme.TEXT_PRIMARY};
        padding: 5px;
    }}
    QHeaderView::section {{
        background-color: {Theme.GLASS_COLOR};
        color: {Theme.TEXT_PRIMARY};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {Theme.ACCENT_COLOR};
        font-weight: bold;
    }}
    QPushButton {{
        background-color: {Theme.GLASS_COLOR};
        color: {Theme.TEXT_PRIMARY};
        border: {Theme.GLASS_BORDER};
        border-radius: 5px;
        padding: 5px;
    }}
    QPushButton:hover {{
        background-color: {Theme.GLASS_HOVER};
    }}
    QLineEdit, QComboBox {{
        background-color: {Theme.GLASS_COLOR};
        color: {Theme.TEXT_PRIMARY};
        border: {Theme.GLASS_BORDER};
        border-radius: 5px;
        padding: 5px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {Theme.ACCENT_COLOR};
    }}
    QDialog {{
        background-color: {Theme.BACKGROUND_COLOR};
    }}
"""

class AddEntryDialog(QDialog):
    def __init__(self, api, db_manager, parent=None, language_manager=None):
        super().__init__(parent)
        self.api = api
        self.db_manager = db_manager
        self.language_manager = language_manager
        
        title = "Neuen Eintrag hinzufügen"
        if self.language_manager:
            title = self.language_manager.translate("new_entry", "Add New Entry")
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Barcode
        scan_text = "Barcode scannen"
        barcode_text = "Barcode"
        if self.language_manager:
            scan_text = self.language_manager.translate("scan_barcode", "Scan Barcode")
            barcode_text = self.language_manager.translate("barcode", "Barcode")
            
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(scan_text)
        self.barcode_input.editingFinished.connect(self.lookup_product)
        
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.weight_input = QLineEdit()
        self.expiry_input = QLineEdit()
        self.expiry_input.setPlaceholderText("YYYY-MM-DD")
        self.quantity_input = QLineEdit()
        
        # Location Dropdown
        self.location_combo = QComboBox()
        self.load_locations()

        form_layout.addRow(f"{barcode_text}:", self.barcode_input)
        
        name_text = "Name"
        cat_text = "Kategorie"
        weight_text = "Gewicht/Volumen"
        loc_text = "Lagerort"
        exp_text = "Ablaufdatum"
        qty_text = "Anzahl"
        
        if self.language_manager:
            name_text = self.language_manager.translate("name", "Name")
            cat_text = self.language_manager.translate("category", "Category")
            weight_text = self.language_manager.translate("weight_vol", "Weight/Volume")
            loc_text = self.language_manager.translate("location", "Location")
            exp_text = self.language_manager.translate("expiry_date", "Expiry Date")
            qty_text = self.language_manager.translate("quantity", "Quantity")

        form_layout.addRow(f"{name_text}:", self.name_input)
        form_layout.addRow(f"{cat_text}:", self.category_input)
        form_layout.addRow(f"{weight_text}:", self.weight_input)
        form_layout.addRow(f"{loc_text}:", self.location_combo)
        form_layout.addRow(f"{exp_text}:", self.expiry_input)
        form_layout.addRow(f"{qty_text}:", self.quantity_input)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_text = "Speichern"
        cancel_text = "Abbrechen"
        if self.language_manager:
            save_text = self.language_manager.translate("save", "Save")
            cancel_text = self.language_manager.translate("cancel", "Cancel")
            
        save_btn = QPushButton(save_text)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def load_locations(self):
        locations = self.db_manager.get_locations()
        for loc_id, name in locations:
            self.location_combo.addItem(name, loc_id)

    def lookup_product(self):
        barcode = self.barcode_input.text()
        if not barcode:
            return
            
        # 1. Check local DB first
        local_data = self.db_manager.get_product_by_barcode(barcode)
        if local_data:
            self.name_input.setText(local_data[0])
            self.category_input.setText(local_data[1])
            self.weight_input.setText(local_data[2])
            return

        # 2. Check API
        name, category, weight = self.api.get_product_info(barcode)
        if name:
            self.name_input.setText(name)
        if category:
            self.category_input.setText(category)
        if weight:
            self.weight_input.setText(weight)

    def get_data(self):
        return (
            self.barcode_input.text(),
            self.name_input.text(),
            self.category_input.text(),
            self.expiry_input.text(),
            self.quantity_input.text(),
            self.weight_input.text(),
            self.location_combo.currentData() # Returns location_id
        )



class EditEntryDialog(QDialog):
    """
    Dialog for editing an existing inventory entry.
    """
    def __init__(self, db_manager, entry_data, parent=None, language_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.entry_data = entry_data # (id, barcode, name, category, expiry, quantity, weight, location_name, location_id)
        self.language_manager = language_manager
        
        title = "Eintrag bearbeiten"
        if self.language_manager:
            title = self.language_manager.translate("edit_entry_title", "Edit Entry")
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Read-only fields
        self.name_label = QLabel(self.entry_data[2])
        self.category_label = QLabel(self.entry_data[3])
        self.barcode_label = QLabel(self.entry_data[1])
        
        # Editable fields
        self.expiry_input = QLineEdit(self.entry_data[4])
        self.expiry_input.setPlaceholderText("YYYY-MM-DD")
        
        self.quantity_input = QLineEdit(str(self.entry_data[5]))
        
        # Location Dropdown
        self.location_combo = QComboBox()
        self.load_locations() # Call load_locations to populate the combo box
        
        # Set current location
        index = self.location_combo.findData(self.entry_data[8])
        if index >= 0:
            self.location_combo.setCurrentIndex(index)

        name_text = "Name"
        cat_text = "Kategorie"
        barcode_text = "Barcode"
        loc_text = "Lagerort"
        exp_text = "Ablaufdatum"
        qty_text = "Anzahl"
        
        if self.language_manager:
            name_text = self.language_manager.translate("name", "Name")
            cat_text = self.language_manager.translate("category", "Category")
            barcode_text = self.language_manager.translate("barcode", "Barcode")
            loc_text = self.language_manager.translate("location", "Location")
            exp_text = self.language_manager.translate("expiry_date", "Expiry Date")
            qty_text = self.language_manager.translate("quantity", "Quantity")

        form_layout.addRow(f"{name_text}:", self.name_label)
        form_layout.addRow(f"{cat_text}:", self.category_label)
        form_layout.addRow(f"{barcode_text}:", self.barcode_label)
        form_layout.addRow(f"{loc_text}:", self.location_combo)
        form_layout.addRow(f"{exp_text}:", self.expiry_input)
        form_layout.addRow(f"{qty_text}:", self.quantity_input)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_text = "Speichern"
        cancel_text = "Abbrechen"
        if self.language_manager:
            save_text = self.language_manager.translate("save", "Save")
            cancel_text = self.language_manager.translate("cancel", "Cancel")
            
        save_btn = QPushButton(save_text)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def load_locations(self):
        locations = self.db_manager.get_locations()
        for loc_id, name in locations:
            self.location_combo.addItem(name, loc_id)

    def get_data(self):
        return (
            self.location_combo.currentData(), # location_id
            self.expiry_input.text(),
            self.quantity_input.text()
        )

class ManageLocationsDialog(QDialog):
    """
    Dialog for managing storage locations.
    """
    def __init__(self, db_manager, parent=None, language_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.language_manager = language_manager
        
        title = "Lagerorte verwalten"
        if self.language_manager:
            title = self.language_manager.translate("manage_locations", "Manage Locations")
        self.setWindowTitle(title)
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.refresh_list()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_text = "Neu"
        del_text = "Löschen"
        if self.language_manager:
            add_text = self.language_manager.translate("add_entry", "Add").replace(" Entry", "") # Hacky reuse
            del_text = self.language_manager.translate("delete_selected", "Delete Selected")
            
        add_btn = QPushButton(add_text)
        add_btn.clicked.connect(self.add_location)
        del_btn = QPushButton(del_text)
        del_btn.clicked.connect(self.delete_location)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

    def refresh_list(self):
        self.list_widget.clear()
        locations = self.db_manager.get_locations()
        for loc_id, name in locations:
            item = QListWidgetItem(f"{loc_id}: {name}")
            self.list_widget.addItem(item)

    def add_location(self):
        title = "Neuer Lagerort"
        label = "Name:"
        if self.language_manager:
            title = self.language_manager.translate("new_location", "New Location")
            label = self.language_manager.translate("location_name", "Name:")
            
        name, ok = QInputDialog.getText(self, title, label)
        if ok and name:
            success, msg = self.db_manager.add_location(name)
            if success:
                self.refresh_list()
            else:
                QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)

    def delete_location(self):
        rows = self.list_widget.selectedItems()
        if not rows:
            return
            
        loc_str = rows[0].text()
        loc_id = int(loc_str.split(":")[0])
        
        success, msg = self.db_manager.delete_location(loc_id)
        if success:
            self.refresh_list()
        else:
            QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)

class LebensmittelManagerApp(QMainWindow):
    """
    Main application window for the Pantry Manager.

    This shows the big table of all your food and gives you buttons to 
    manage items and locations.
    """
    def __init__(self, language_manager=None):
        super().__init__()
        self.language_manager = language_manager
        self.setWindowTitle("Lebensmittel Manager Pro")
        if self.language_manager:
            self.setWindowTitle(self.language_manager.translate("pantry_manager", "Lebensmittel Manager Pro"))
        self.resize(1100, 650)
        
        self.db_manager = DatabaseManager()
        self.api = OpenFoodFactsAPI()
        
        self.show_expiring_only = False
        
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        """
        Sets up the whole UI layout, buttons, and table.
        """
        self.setStyleSheet(STYLESHEET)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.ACCENT_COLOR};")
        header.addWidget(self.title_label)
        header.addStretch()
        
        self.loc_btn = QPushButton()
        self.loc_btn.clicked.connect(self.manage_locations)
        header.addWidget(self.loc_btn)
        
        self.expiring_btn = QPushButton()
        self.expiring_btn.setCheckable(True)
        self.expiring_btn.clicked.connect(self.toggle_expiring_filter)
        header.addWidget(self.expiring_btn)
        
        main_layout.addLayout(header)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(self.add_entry)
        
        self.edit_btn = QPushButton()
        self.edit_btn.clicked.connect(self.edit_entry)
        
        self.del_btn = QPushButton()
        self.del_btn.clicked.connect(self.delete_entry)
        
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.refresh_table)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        
        self.export_full_btn = QPushButton()
        self.export_full_btn.clicked.connect(self.export_full_inventory)
        btn_layout.addWidget(self.export_full_btn)

        self.export_selected_btn = QPushButton()
        self.export_selected_btn.clicked.connect(self.export_selected_items)
        btn_layout.addWidget(self.export_selected_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.update_texts()
        if self.language_manager:
            self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        """Updates UI texts based on current language."""
        title = "Lebensmittel Manager Pro"
        header_title = "Vorratsschrank"
        loc_text = "Lagerorte verwalten"
        exp_text = "⚠️ Bald ablaufend"
        search_placeholder = "🔍 Suchen (Name oder Barcode)..."
        
        add_text = "Eintrag hinzufügen"
        edit_text = "Bearbeiten"
        del_text = "Eintrag löschen/reduzieren"
        refresh_text = "Aktualisieren"
        export_full_text = "Export Complete Inventory"
        export_sel_text = "Export Selected"
        
        columns = ["ID", "Barcode", "Name", "Kategorie", "Ablaufdatum", "Anzahl", "Gewicht", "Lagerort"]
        
        if self.language_manager:
            title = self.language_manager.translate("pantry_manager", "Lebensmittel Manager Pro")
            header_title = self.language_manager.translate("pantry_manager_title", "Vorratsschrank")
            loc_text = self.language_manager.translate("manage_locations", "Manage Locations")
            exp_text = self.language_manager.translate("expiring_soon", "⚠️ Expiring Soon")
            search_placeholder = self.language_manager.translate("search_placeholder", search_placeholder)
            
            add_text = self.language_manager.translate("add_entry", add_text)
            edit_text = self.language_manager.translate("edit_entry", edit_text)
            del_text = self.language_manager.translate("delete_entry", del_text)
            refresh_text = self.language_manager.translate("refresh", refresh_text)
            export_full_text = self.language_manager.translate("export_full", export_full_text)
            export_sel_text = self.language_manager.translate("export_selected", export_sel_text)
            
            columns = [
                "ID",
                self.language_manager.translate("barcode", "Barcode"),
                self.language_manager.translate("name", "Name"),
                self.language_manager.translate("category", "Category"),
                self.language_manager.translate("expiry_date", "Expiry Date"),
                self.language_manager.translate("quantity", "Quantity"),
                self.language_manager.translate("weight_vol", "Weight/Volume"),
                self.language_manager.translate("location", "Location")
            ]

        self.setWindowTitle(title)
        self.title_label.setText(header_title)
        self.loc_btn.setText(loc_text)
        self.expiring_btn.setText(exp_text)
        self.search_input.setPlaceholderText(search_placeholder)
        
        self.add_btn.setText(add_text)
        self.edit_btn.setText(edit_text)
        self.del_btn.setText(del_text)
        self.refresh_btn.setText(refresh_text)
        self.export_full_btn.setText(export_full_text)
        self.export_selected_btn.setText(export_sel_text)
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

    def refresh_table(self):
        """
        Reloads the table data from the database.
        
        Also handles the "expiring soon" filter and colors rows red/yellow 
        if they are about to go bad.
        """
        self.table.setRowCount(0)
        
        if self.show_expiring_only:
            entries = self.db_manager.get_expiring_inventory(30)
        else:
            entries = self.db_manager.get_inventory_with_details()
            
        from datetime import datetime, timedelta
        today = datetime.now().date()
        warning_date = today + timedelta(days=30)
        
        for row_idx, entry in enumerate(entries):
            self.table.insertRow(row_idx)
            # entry: id, barcode, name, category, expiry, quantity, weight, location
            # Map to columns: ID, Barcode, Name, Kategorie, Ablaufdatum, Anzahl, Gewicht, Lagerort
            
            mapping = [0, 1, 2, 3, 4, 5, 6, 7]
            
            for col_idx, map_idx in enumerate(mapping):
                val = entry[map_idx]
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Color coding for expiry
                try:
                    expiry_date = datetime.strptime(entry[4], "%Y-%m-%d").date()
                    if expiry_date < today:
                        item.setForeground(QColor("#ff5555")) # Red for expired
                    elif expiry_date <= warning_date:
                        item.setForeground(QColor("#f1fa8c")) # Yellow for warning
                except ValueError:
                    pass
                    
                self.table.setItem(row_idx, col_idx, item)

    def toggle_expiring_filter(self):
        self.show_expiring_only = self.expiring_btn.isChecked()
        self.refresh_table()

    def filter_table(self, text):
        """
        Filters rows based on what you type in the search bar.

        Args:
            text (str): What you're looking for (name or barcode).
        """
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            # Check Name (col 2) and Barcode (col 1)
            name = self.table.item(row, 2).text().lower()
            barcode = self.table.item(row, 1).text().lower()
            
            if text in name or text in barcode:
                match = True
            
            self.table.setRowHidden(row, not match)

    def export_full_inventory(self):
        """
        Exports the entire inventory to a CSV file.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Export Complete Inventory", "full_inventory.csv", "CSV Files (*.csv)")
        if not path:
            return
            
        try:
            entries = self.db_manager.get_inventory_with_details()
            # entries structure: id, barcode, name, category, expiry, quantity, weight, location_name
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Headers matching the DB columns we get
                headers = ["ID", "Barcode", "Name", "Category", "Expiry Date", "Quantity", "Weight/Volume", "Location"]
                writer.writerow(headers)
                
                for entry in entries:
                    writer.writerow(entry)
            
            QMessageBox.information(self, "Success", "Full inventory exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_selected_items(self):
        """
        Exports currently selected items to a CSV file (e.g., for a shopping list).
        """
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select items to export for your grocery list!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Selected Items", "grocery_list.csv", "CSV Files (*.csv)")
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write headers from table
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data from selected rows
                for row in selected_rows:
                    if self.table.isRowHidden(row):
                        continue
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", "Selected items exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def add_entry(self):
        """
        Opens the dialog to add a new inventory item.
        """
        dialog = AddEntryDialog(self.api, self.db_manager, self, language_manager=self.language_manager)
        if dialog.exec():
            barcode, name, category, expiry, quantity, weight, location_id = dialog.get_data()
            
            if not name:
                msg = "Name is required!"
                if self.language_manager:
                    msg = self.language_manager.translate("name_required", msg)
                QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)
                return
            try:
                qty = int(quantity)
            except ValueError:
                msg = "Quantity must be a number!"
                if self.language_manager:
                    msg = self.language_manager.translate("qty_must_be_number", msg)
                QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)
                return

            success, message = self.db_manager.add_product(barcode, name, category, expiry, qty, weight, location_id)
            
            if success:
                self.refresh_table()
            else:
                QMessageBox.critical(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", message)

    def delete_entry(self):
        """
        Deletes or reduces the quantity of the selected inventory item.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            msg = "Please select an entry!"
            if self.language_manager:
                msg = self.language_manager.translate("select_entry_warning", msg)
            QMessageBox.warning(self, self.language_manager.translate("warning", "Warning") if self.language_manager else "Warnung", msg)
            return
            
        row = selected_rows[0].row()
        inv_id = int(self.table.item(row, 0).text())
        
        title = "Remove Quantity"
        label = "How many units to remove?"
        if self.language_manager:
            title = self.language_manager.translate("remove_qty", title)
            label = self.language_manager.translate("how_many_remove", label)

        qty, ok = QInputDialog.getInt(self, title, label, 1, 1, 1000)
        if ok:
            if self.db_manager.delete_inventory_item(inv_id, qty):
                self.refresh_table()
            else:
                msg = "Could not update entry."
                if self.language_manager:
                    msg = self.language_manager.translate("error_update_entry", msg)
                QMessageBox.critical(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)

    def edit_entry(self):
        """
        Opens the dialog to edit the selected inventory item.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            msg = "Please select an entry!"
            if self.language_manager:
                msg = self.language_manager.translate("select_entry_warning", msg)
            QMessageBox.warning(self, self.language_manager.translate("warning", "Warning") if self.language_manager else "Warnung", msg)
            return
            
        row = selected_rows[0].row()
        inv_id = int(self.table.item(row, 0).text())
        
        # Get location ID from name
        loc_name = self.table.item(row, 7).text()
        locations = self.db_manager.get_locations()
        location_id = next((id for id, name in locations if name == loc_name), None)
        
        if location_id is None:
             msg = "Location not found."
             if self.language_manager:
                 msg = self.language_manager.translate("location_not_found", msg)
             QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)
             return

        entry_data = (
            inv_id,
            self.table.item(row, 1).text(), # barcode
            self.table.item(row, 2).text(), # name
            self.table.item(row, 3).text(), # category
            self.table.item(row, 4).text(), # expiry
            self.table.item(row, 5).text(), # quantity
            self.table.item(row, 6).text(), # weight
            loc_name,
            location_id
        )
        
        dialog = EditEntryDialog(self.db_manager, entry_data, self, language_manager=self.language_manager)
        if dialog.exec():
            new_loc_id, new_expiry, new_qty = dialog.get_data()
            try:
                qty = int(new_qty)
            except ValueError:
                msg = "Quantity must be a number!"
                if self.language_manager:
                    msg = self.language_manager.translate("qty_must_be_number", msg)
                QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)
                return
                
            success, msg = self.db_manager.update_inventory_item(inv_id, new_loc_id, new_expiry, qty)
            if success:
                self.refresh_table()
            else:
                QMessageBox.critical(self, self.language_manager.translate("error", "Error") if self.language_manager else "Fehler", msg)

    def manage_locations(self):
        """
        Opens the dialog to manage storage locations.
        """
        dialog = ManageLocationsDialog(self.db_manager, self, language_manager=self.language_manager)
        dialog.exec()
