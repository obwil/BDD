import sqlite3

# Chemin sans accent dans le nom du script, le chemin réel avec accent
db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Lister les tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

conn.close()
