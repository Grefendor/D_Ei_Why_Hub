import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .database import DatabaseManager
from .api import OpenFoodFactsAPI

class LebensmittelManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lebensmittel-Manager")
        self.db_manager = DatabaseManager()
        self.api = OpenFoodFactsAPI()
        self.create_ui()
        self.refresh_table()

    def create_ui(self):
        # Tabelle (Treeview)
        columns = ("ID", "Barcode", "Name", "Kategorie", "Ablaufdatum", "Anzahl", "Gewicht/Volumen")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Barcode", text="Barcode")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Kategorie", text="Kategorie")
        self.tree.heading("Ablaufdatum", text="Ablaufdatum")
        self.tree.heading("Anzahl", text="Anzahl")
        self.tree.heading("Gewicht/Volumen", text="Gewicht/Volumen")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Barcode", width=150, anchor="center")
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("Kategorie", width=150, anchor="center")
        self.tree.column("Ablaufdatum", width=100, anchor="center")
        self.tree.column("Anzahl", width=80, anchor="center")
        self.tree.column("Gewicht/Volumen", width=120, anchor="center")
        
        self.tree.pack(fill="both", expand=True)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x")
        tk.Button(button_frame, text="Eintrag hinzufügen", command=self.add_entry).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Eintrag löschen", command=self.delete_entry).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Liste aktualisieren", command=self.refresh_table).pack(side=tk.LEFT, padx=5, pady=5)

    def add_entry(self):
        barcode = simpledialog.askstring("Barcode", "Scanne oder gib den Barcode ein:")
        if not barcode:
            return

        name, kategorie, gewicht_volumen = self.api.get_product_info(barcode)
        
        if not name:
            name = simpledialog.askstring("Name", "Name des Lebensmittels:")
        if not kategorie:
            kategorie = simpledialog.askstring("Kategorie", "Kategorie (z.B. Obst, Gemüse, Fleisch):")
        if not gewicht_volumen or gewicht_volumen == "Unbekannt":
            gewicht_volumen = simpledialog.askstring("Gewicht/Volumen", "Gewicht/Volumen (z.B. 500g, 1.5l):")

        ablaufdatum = simpledialog.askstring("Ablaufdatum", "Ablaufdatum (YYYY-MM-DD):")
        anzahl = simpledialog.askinteger("Anzahl", "Anzahl der Einheiten:")

        if anzahl is not None:
            success, message = self.db_manager.add_product(barcode, name, kategorie, ablaufdatum, anzahl, gewicht_volumen)
            if success:
                messagebox.showinfo("Erfolg", message)
            else:
                messagebox.showerror("Fehler", message)
            self.refresh_table()

    def delete_entry(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warnung", "Bitte wähle einen Eintrag aus!")
            return

        entry_id = self.tree.item(selected_item)["values"][0]
        menge = simpledialog.askinteger("Menge löschen", "Wie viele Einheiten möchtest du löschen?")
        if menge:
            if self.db_manager.delete_product(entry_id, menge):
                messagebox.showinfo("Erfolg", "Eintrag wurde aktualisiert oder gelöscht.")
                self.refresh_table()
            else:
                messagebox.showerror("Fehler", "Fehler beim Löschen des Eintrags.")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        entries = self.db_manager.get_all_products()
        for entry in entries:
            self.tree.insert("", "end", values=entry)
