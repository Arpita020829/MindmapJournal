import sqlite3

conn = sqlite3.connect("journal.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS journal_entries(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_text TEXT,
    prediction TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database Created")