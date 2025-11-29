"""
Calendar Database Module.

This module handles all database interactions for the Calendar application.
It manages the storage, retrieval, and deletion of events using SQLite.
"""

import sqlite3
import os
from datetime import datetime, date

# Go up 3 levels from apps/calendar/database.py to root, then into data
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'events.db')

def init_db():
    """
    Initializes the database schema.

    Creates the 'events' table if it does not already exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # We are changing the schema, so for simplicity in this prototype, we'll create a new table 'events'.
    # If 'birthdays' exists, we could migrate, but let's just start fresh or coexist.
    # Let's drop the old one to be clean if we want to replace it, or just make a new one.
    # Given the user said "change it", let's assume we can start fresh or migrate.
    # I'll just create 'events' table.
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            day INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER,
            category TEXT DEFAULT 'General'
        )
    """)
    conn.commit()
    conn.close()

def add_event(title, day, month, year=None, category="General"):
    """
    Adds a new event to the database.

    Args:
        title (str): The title/description of the event.
        day (int): The day of the month (1-31).
        month (int): The month (1-12).
        year (int, optional): The year of the event. Defaults to None.
        category (str, optional): The category of the event. Defaults to "General".
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (title, day, month, year, category) VALUES (?, ?, ?, ?, ?)", 
                   (title, day, month, year, category))
    conn.commit()
    conn.close()

def get_all_events():
    """
    Retrieves all events from the database.

    Returns:
        list: A list of dictionaries, each representing an event.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, day, month, year, category FROM events ORDER BY month, day")
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "title": row[1],
            "day": row[2],
            "month": row[3],
            "year": row[4],
            "category": row[5]
        })
    return events

def get_upcoming_events(days_ahead=7):
    """
    Returns events occurring within the next `days_ahead` days.
    Includes today.

    Args:
        days_ahead (int): The number of days to look ahead. Defaults to 7.

    Returns:
        list: A sorted list of upcoming events with a 'days_until' key.
    """
    all_events = get_all_events()
    upcoming = []
    today = date.today()
    current_year = today.year
    
    for e in all_events:
        # Create a date object for this event in the current year
        try:
            e_date = date(current_year, e["month"], e["day"])
        except ValueError:
            if e["month"] == 2 and e["day"] == 29:
                 e_date = date(current_year, 3, 1)
            else:
                continue

        # If event has passed this year, check next year
        if e_date < today:
            try:
                e_date = date(current_year + 1, e["month"], e["day"])
            except ValueError:
                 if e["month"] == 2 and e["day"] == 29:
                     e_date = date(current_year + 1, 3, 1)

        delta = (e_date - today).days
        
        if 0 <= delta <= days_ahead:
            e["days_until"] = delta
            upcoming.append(e)
            
    # Sort by days until
    upcoming.sort(key=lambda x: x["days_until"])
    return upcoming

def delete_event(event_id):
    """
    Deletes an event from the database.

    Args:
        event_id (int): The ID of the event to delete.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
