import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
ids = [1425,918,919,5,236,923,924,926,423,669,430,927,505,380,847,929,930,932,518,933,934,937,938,939,940,943,944,946,947,948,822,957,961,951,953,954,955,956,958,960,971,968,969,1182,1183,1184,1186,1189,572,1201,1190,1192,1193,1194,1195,1196,1412,1198,1199,1200,1202,1203,1204,1205,1206,1207,1210,1211,158,1213,1215,1217,764,699,701,1270,1222,1223,1224,1226,1227,1228,258,611,469,1237,892,758,354,215,757,755,1241,1243,193,1244,1240,455,1245,1246,220,583,581,584,201,1250,379,157,1259,904,586,871,1233,1234,1272,809]
placeholders = ",".join("?" for _ in ids)
cur.execute(f"SELECT id, nom, lieu FROM activite WHERE id IN ({placeholders}) AND (description IS NOT NULL AND description != '') AND (lieu IS NULL OR lieu = '') ORDER BY nom", ids)
rows = cur.fetchall()
print(f"Avec description mais sans lieu: {len(rows)}")
for r in rows:
    print(f"  {r[0]} | {r[1]}")
db.close()
