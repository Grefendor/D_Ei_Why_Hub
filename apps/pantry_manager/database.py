import sqlite3
import shutil
import os
from datetime import datetime

"""
Pantry Database Module.

This module manages the SQLite database for the Pantry Manager application.
It handles schema initialization, migrations, and all CRUD operations for
products, inventory, and locations.
"""

class DatabaseManager:
    """
    Manages database connections and operations for the Pantry Manager.
    """
    def __init__(self, db_name=None):
        """
        Initializes the DatabaseManager.

        Args:
            db_name (str, optional): Path to the database file. Defaults to 'lebensmittel.db'.
        """
        if db_name is None:
            # Go up 3 levels from apps/pantry_manager/database.py to root, then into data
            db_name = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'lebensmittel.db')
        self.db_name = db_name
        self.initialize_database()

    def get_connection(self):
        """Creates and returns a new database connection."""
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        """Initialize the database with the new schema. Handles migration if needed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if we need to migrate (if old table exists and new ones don't)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lebensmittel'")
            old_table_exists = cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            new_schema_exists = cursor.fetchone() is not None

            if old_table_exists and not new_schema_exists:
                print("Migrating database to new schema...")
                self._migrate_data(conn, cursor)
            else:
                self._create_tables(cursor)
            
            conn.commit()

    def _create_tables(self, cursor):
        """Creates the new table structure."""
        # Products table: Static data about the item
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                barcode TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                weight_volume TEXT
            )
        ''')

        # Locations table: Where items are stored
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT
            )
        ''')

        # Inventory table: Specific instances of products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                location_id INTEGER,
                expiry_date TEXT,
                quantity INTEGER,
                FOREIGN KEY(barcode) REFERENCES products(barcode),
                FOREIGN KEY(location_id) REFERENCES locations(id)
            )
        ''')
        
        # Ensure a default location exists
        cursor.execute("INSERT OR IGNORE INTO locations (name, description) VALUES (?, ?)", 
                       ("Standard", "Standard Lagerort"))

    def _migrate_data(self, conn, cursor):
        """Migrates data from the old 'lebensmittel' table to the new structure."""
        # 1. Create new tables
        self._create_tables(cursor)
        
        # 2. Get default location ID
        cursor.execute("SELECT id FROM locations WHERE name = 'Standard'")
        default_location_id = cursor.fetchone()[0]

        # 3. Fetch old data
        cursor.execute("SELECT barcode, name, kategorie, ablaufdatum, anzahl, gewicht_volumen FROM lebensmittel")
        old_items = cursor.fetchall()

        for item in old_items:
            barcode, name, category, expiry, quantity, weight = item
            
            # Insert into products (ignore if already exists)
            cursor.execute('''
                INSERT OR IGNORE INTO products (barcode, name, category, weight_volume)
                VALUES (?, ?, ?, ?)
            ''', (barcode, name, category, weight))
            
            # Insert into inventory
            cursor.execute('''
                INSERT INTO inventory (barcode, location_id, expiry_date, quantity)
                VALUES (?, ?, ?, ?)
            ''', (barcode, default_location_id, expiry, quantity))

        # 4. Rename old table to backup (optional, but good for safety)
        cursor.execute("ALTER TABLE lebensmittel RENAME TO lebensmittel_backup_v1")

    # --- Product & Inventory Management ---

    def add_product(self, barcode, name, category, expiry, quantity, weight, location_id):
        """
        Adds a product to inventory, creating the product record if it doesn't exist.

        Args:
            barcode (str): Product barcode.
            name (str): Product name.
            category (str): Product category.
            expiry (str): Expiry date (YYYY-MM-DD).
            quantity (int): Quantity to add.
            weight (str): Weight or volume.
            location_id (int): ID of the storage location.

        Returns:
            tuple: (bool, str) indicating success/failure and a message.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 1. Ensure product exists
                cursor.execute('''
                    INSERT INTO products (barcode, name, category, weight_volume)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(barcode) DO UPDATE SET
                        name=excluded.name,
                        category=excluded.category,
                        weight_volume=excluded.weight_volume
                ''', (barcode, name, category, weight))

                # 2. Add to inventory (or update if exactly same item in same location/expiry exists?)
                # For now, let's just add a new row for every entry to allow distinct expiries.
                # Or we could group by (barcode, location, expiry). Let's group.
                
                cursor.execute('''
                    SELECT id, quantity FROM inventory 
                    WHERE barcode = ? AND location_id = ? AND expiry_date = ?
                ''', (barcode, location_id, expiry))
                existing_entry = cursor.fetchone()

                if existing_entry:
                    new_qty = existing_entry[1] + quantity
                    cursor.execute('UPDATE inventory SET quantity = ? WHERE id = ?', (new_qty, existing_entry[0]))
                    msg = f"Anzahl für '{name}' erhöht."
                else:
                    cursor.execute('''
                        INSERT INTO inventory (barcode, location_id, expiry_date, quantity)
                        VALUES (?, ?, ?, ?)
                    ''', (barcode, location_id, expiry, quantity))
                    msg = f"'{name}' hinzugefügt."

                conn.commit()
                return True, msg
            except Exception as e:
                return False, str(e)

    def get_inventory_with_details(self):
        """
        Retrieves full inventory details joining products and locations.

        Returns:
            list: A list of tuples containing inventory details.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    i.id, 
                    p.barcode, 
                    p.name, 
                    p.category, 
                    i.expiry_date, 
                    i.quantity, 
                    p.weight_volume,
                    l.name as location_name
                FROM inventory i
                JOIN products p ON i.barcode = p.barcode
                JOIN locations l ON i.location_id = l.id
                ORDER BY p.name
            ''')
            return cursor.fetchall()

    def delete_inventory_item(self, inventory_id, quantity_to_remove):
        """
        Reduces quantity or removes an inventory item entirely.

        Args:
            inventory_id (int): The ID of the inventory item.
            quantity_to_remove (int): The quantity to subtract.

        Returns:
            bool: True if successful, False otherwise.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (inventory_id,))
            result = cursor.fetchone()
            
            if not result:
                return False

            current_qty = result[0]
            
            if quantity_to_remove >= current_qty:
                cursor.execute("DELETE FROM inventory WHERE id = ?", (inventory_id,))
            else:
                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", 
                               (quantity_to_remove, inventory_id))
            
            conn.commit()
            return True

    def update_inventory_item(self, inventory_id, location_id, expiry_date, quantity):
        """
        Updates an existing inventory item's details.

        Args:
            inventory_id (int): The ID of the inventory item.
            location_id (int): The new location ID.
            expiry_date (str): The new expiry date.
            quantity (int): The new quantity.

        Returns:
            tuple: (bool, str) indicating success/failure and a message.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE inventory 
                    SET location_id = ?, expiry_date = ?, quantity = ?
                    WHERE id = ?
                ''', (location_id, expiry_date, quantity, inventory_id))
                conn.commit()
                return True, "Eintrag aktualisiert."
            except Exception as e:
                return False, str(e)

    def get_expiring_inventory(self, days_threshold=30):
        """
        Retrieves inventory items expiring within the given number of days.

        Args:
            days_threshold (int): The number of days to look ahead. Defaults to 30.

        Returns:
            list: A list of tuples containing expiring inventory details.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Calculate the target date
            # SQLite date('now', '+30 days')
            cursor.execute(f'''
                SELECT 
                    i.id, 
                    p.barcode, 
                    p.name, 
                    p.category, 
                    i.expiry_date, 
                    i.quantity, 
                    p.weight_volume,
                    l.name as location_name
                FROM inventory i
                JOIN products p ON i.barcode = p.barcode
                JOIN locations l ON i.location_id = l.id
                WHERE i.expiry_date <= date('now', '+{days_threshold} days')
                ORDER BY i.expiry_date ASC
            ''')
            return cursor.fetchall()

    # --- Location Management ---

    def get_locations(self):
        """Retrieves all storage locations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM locations")
            return cursor.fetchall()

    def add_location(self, name):
        """
        Adds a new storage location.

        Args:
            name (str): The name of the location.

        Returns:
            tuple: (bool, str) indicating success/failure and a message.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO locations (name, description) VALUES (?, '')", (name,))
                conn.commit()
                return True, "Ort hinzugefügt."
            except sqlite3.IntegrityError:
                return False, "Ort existiert bereits."

    def delete_location(self, location_id):
        """
        Deletes a storage location if it is empty.

        Args:
            location_id (int): The ID of the location to delete.

        Returns:
            tuple: (bool, str) indicating success/failure and a message.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if used
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE location_id = ?", (location_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Ort ist nicht leer."
            
            cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))
            conn.commit()
            return True, "Ort gelöscht."

    def get_product_by_barcode(self, barcode):
        """
        Retrieves product details by barcode to auto-fill forms.

        Args:
            barcode (str): The product barcode.

        Returns:
            tuple: (name, category, weight_volume) or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, category, weight_volume FROM products WHERE barcode = ?", (barcode,))
            return cursor.fetchone()
