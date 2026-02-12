#!/usr/bin/env python3
import sqlite3
import os

db_path = 'valuations.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add vehicle_variant column
        cursor.execute('ALTER TABLE valuations ADD COLUMN vehicle_variant TEXT')
        conn.commit()
        print("✅ Added vehicle_variant column to valuations table")
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print("✅ Column already exists")
        else:
            print(f"❌ Error: {e}")
    
    conn.close()
else:
    print("❌ Database not found")
