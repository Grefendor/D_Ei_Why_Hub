import sqlite3
import os
from datetime import datetime, timedelta

TASK_DB_PATH = os.path.join("data", "tasks.db")
PANTRY_DB_PATH = os.path.join("data", "lebensmittel.db")
CALENDAR_DB_PATH = os.path.join("data", "events.db")

def seed_task_board():
    print(f"Seeding Task Board at {TASK_DB_PATH}...")
    
    os.makedirs(os.path.dirname(TASK_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(TASK_DB_PATH)
    c = conn.cursor()
    
    # Drop existing tables to ensure fresh schema
    c.execute("DROP TABLE IF EXISTS task_completions")
    c.execute("DROP TABLE IF EXISTS tasks")
    c.execute("DROP TABLE IF EXISTS people")
    
    # Create tables (matching database.py schema)
    c.execute('''
        CREATE TABLE people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    c.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            assignment_type TEXT NOT NULL,
            assignment_value TEXT,
            frequency TEXT NOT NULL,
            last_completed TEXT,
            next_due TEXT,
            required_completions INTEGER DEFAULT 1,
            current_completions INTEGER DEFAULT 0,
            last_reset_date TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            person_id INTEGER,
            completion_date TEXT,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        )
    ''')
    
    # Add People
    people = ["Alice", "Bob", "Charlie", "Dave"]
    for p in people:
        c.execute("INSERT INTO people (name) VALUES (?)", (p,))
    print("Added people: " + ", ".join(people))
    
    # Get IDs
    c.execute("SELECT id, name FROM people")
    people_map = {name: pid for pid, name in c.fetchall()}
    
    # Add Tasks
    tasks = [
        ("Clean Kitchen", "any_n", "1", "Daily"),
        ("Team Meeting", "all", None, "Weekly"),
        ("Water Plants", "specific", str(people_map["Alice"]), "Every 3 Days"),
        ("Code Review", "any_n", "2", "Daily"),
        ("Prepare Lunch", "specific", f"{people_map['Alice']},{people_map['Bob']}", "Daily")
    ]
    
    for name, atype, aval, freq in tasks:
        # Calculate required
        required = 1
        if atype == 'all':
            required = len(people)
        elif atype == 'any_n':
            required = int(aval)
        elif atype == 'specific':
            required = len(aval.split(','))
            
        c.execute('''
            INSERT INTO tasks (name, assignment_type, assignment_value, frequency, next_due, required_completions) 
            VALUES (?, ?, ?, ?, date('now'), ?)
        ''', (name, atype, aval, freq, required))
        
    print(f"Added {len(tasks)} tasks.")
    
    conn.commit()
    conn.close()

def seed_pantry():
    print(f"Seeding Pantry Manager at {PANTRY_DB_PATH}...")
    
    os.makedirs(os.path.dirname(PANTRY_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(PANTRY_DB_PATH)
    c = conn.cursor()
    
    # Create tables if not exist (simplified from database.py)
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            weight_volume TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT
        )
    ''')

    c.execute('''
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
    
    # Clear data
    c.execute("DELETE FROM inventory")
    c.execute("DELETE FROM locations")
    c.execute("DELETE FROM products")
    
    # Add Locations
    locations = ["Pantry", "Fridge", "Freezer", "Basement"]
    for loc in locations:
        c.execute("INSERT INTO locations (name, description) VALUES (?, '')", (loc,))
    
    c.execute("SELECT id, name FROM locations")
    loc_map = {name: lid for lid, name in c.fetchall()}
    
    # Add Products & Inventory
    products = [
        ("123456", "Milk", "Dairy", "1L", "Fridge", 2, 7),
        ("234567", "Eggs", "Dairy", "12 pack", "Fridge", 1, 14),
        ("345678", "Pasta", "Grains", "500g", "Pantry", 5, 365),
        ("456789", "Tomato Sauce", "Canned", "400g", "Pantry", 3, 180),
        ("567890", "Frozen Pizza", "Frozen", "350g", "Freezer", 2, 90),
        ("678901", "Apples", "Fruit", "1kg", "Fridge", 1, 10),
        ("789012", "Rice", "Grains", "1kg", "Pantry", 2, 365)
    ]
    
    today = datetime.now()
    
    for barcode, name, cat, weight, loc_name, qty, days_expiry in products:
        c.execute("INSERT INTO products (barcode, name, category, weight_volume) VALUES (?, ?, ?, ?)",
                  (barcode, name, cat, weight))
        
        expiry = (today + timedelta(days=days_expiry)).strftime('%Y-%m-%d')
        loc_id = loc_map.get(loc_name, loc_map["Pantry"])
        
        c.execute("INSERT INTO inventory (barcode, location_id, expiry_date, quantity) VALUES (?, ?, ?, ?)",
                  (barcode, loc_id, expiry, qty))
                  
    print(f"Added {len(locations)} locations and {len(products)} products.")
    conn.commit()
    conn.close()

def seed_calendar():
    print(f"Seeding Calendar at {CALENDAR_DB_PATH}...")
    
    os.makedirs(os.path.dirname(CALENDAR_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(CALENDAR_DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            day INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER,
            category TEXT DEFAULT 'General'
        )
    """)
    
    # Clear data
    c.execute("DELETE FROM events")
    
    # Add Events
    events = [
        ("New Year's Day", 1, 1, None, "Holiday"),
        ("Alice's Birthday", 15, 5, 1990, "Birthday"),
        ("Bob's Birthday", 20, 8, 1985, "Birthday"),
        ("Team Lunch", 10, 12, 2025, "Work"),
        ("Project Deadline", 25, 12, 2025, "Work"),
        ("Christmas", 25, 12, None, "Holiday")
    ]
    
    for title, day, month, year, cat in events:
        c.execute("INSERT INTO events (title, day, month, year, category) VALUES (?, ?, ?, ?, ?)",
                  (title, day, month, year, cat))
                  
    print(f"Added {len(events)} events.")
    conn.commit()
    conn.close()

def seed_weather():
    config_path = os.path.join("config", "weather_config.json")
    print(f"Seeding Weather Config at {config_path}...")
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    import json
    # New York Coordinates
    data = {
        "lat": 40.7128,
        "lon": -74.0060,
        "city": "New York"
    }
    
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print("Weather config seeded for New York.")

def seed_data():
    seed_task_board()
    seed_pantry()
    seed_calendar()
    seed_weather()
    print("All databases seeded successfully.")

if __name__ == "__main__":
    seed_data()
