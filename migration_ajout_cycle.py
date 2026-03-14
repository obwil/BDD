import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

conn = sqlite3.connect(DB_PATH)
try:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activite_cycle (
            activite_id  INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
            cycle_id     INTEGER NOT NULL REFERENCES cycle(id) ON DELETE CASCADE,
            PRIMARY KEY (activite_id, cycle_id)
        )
    """)
    conn.commit()
    print("OK : table activite_cycle creee (ou deja presente)")
except Exception as e:
    print(f"ERREUR : {e}")
finally:
    conn.close()
