# Migration to add language columns to settings table
import sqlite3

conn = sqlite3.connect('english_ia.db')
cursor = conn.cursor()

try:
    # Add native_language column
    cursor.execute('''
        ALTER TABLE settings ADD COLUMN native_language VARCHAR(10) DEFAULT 'pt-BR' NOT NULL
    ''')
    print("Added native_language column")
except sqlite3.OperationalError as e:
    print(f"native_language column might already exist: {e}")

try:
    # Add target_language column
    cursor.execute('''
        ALTER TABLE settings ADD COLUMN target_language VARCHAR(10) DEFAULT 'en' NOT NULL
    ''')
    print("Added target_language column")
except sqlite3.OperationalError as e:
    print(f"target_language column might already exist: {e}")

conn.commit()
conn.close()
print("Migration completed successfully")
