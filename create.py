import sqlite3
import json


def save_document(db_path, json_file):
    # 1. Load JSON file
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Connect to SQLite
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 3. Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            title TEXT NOT NULL,
            json_content TEXT NOT NULL
        )
    """)

    # 4. Insert JSON
    cur.execute("""
        INSERT INTO documents (document_id, title, json_content)
        VALUES (?, ?, ?)
    """, (
        data["document_id"],
        data["title"],
        json.dumps(data, indent=2)
    ))

    conn.commit()
    conn.close()

# RUN IT
save_document("docs.db", "data.json")
