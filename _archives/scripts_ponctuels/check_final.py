import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT COUNT(*) FROM activite WHERE description IS NULL OR description = ''")
print("Sans description restantes:", cur.fetchone()[0])
db.close()
