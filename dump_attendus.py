import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, cycle_id, domaine, sous_domaine, libelle, type FROM attendu_scolaire ORDER BY cycle_id, type, domaine, id")
for r in cur.fetchall():
    print(f"{r[0]}|C{r[1]}|{r[5]}|{r[2]}|{r[3]}|{r[4]}")
db.close()
