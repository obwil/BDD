import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM activite WHERE description IS NULL OR description = '' ORDER BY nom")
for r in cur.fetchall():
    print(f"{r[0]} | {r[1]}")
db.close()
