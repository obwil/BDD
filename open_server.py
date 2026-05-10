# -*- coding: utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import subprocess
import sqlite3
from pathlib import Path

PORT = 18765
DB_PATH = Path("C:/Users/moina/Dropbox/Outils/BDD activités/_OUTIL/activites.db")
DROPBOX = Path("C:/Users/moina/Dropbox/Animation/Activités v2")

MOTS_VIDES = [
    "contenu manquant", "contenu absent", "contenu vide",
    "empeche creation", "description impossible", "impossible decrire",
    "impossible a nommer", "details pedagogiques manquants",
    "non decrite", "non decrit",
    "contenu detaille manquant", "contenu manquant a l analyse",
    "contenu a completer", "contenu non fourni",
    "objectif et format non specifie", "objectifs a definir",
    "format non defini", "format et objectifs a definir",
    "nom d'activite", "nom d activite",
    "fiche activite pedagogique manquant",
    "absence contenu", "absence de contenu",
    "definir une activite pedagogique",
    "ebauche activite pedagogique",
    "activite pedagogique contenu",
    "activite sans contenu",
    "objectif et format activite non specifies",
]

NOMS_EXACTS = {
    "Activité pédagogique Contenu à compléter format non défini",
    "Activité sans contenu ni objectif défini",
    "Contenu activité pédagogique absent impossible à nommer ou résumer",
    "Définir une activité pédagogique format modèle",
    "Ébauche activité pédagogique format et objectifs à définir",
}

def est_generique(nom):
    if nom in NOMS_EXACTS:
        return True
    return any(mot in nom.lower() for mot in MOTS_VIDES)

def get_generiques():
    conn = sqlite3.connect(str(DB_PATH))
    noms_bdd = {r[0] for r in conn.execute("SELECT nom FROM activite").fetchall()}
    conn.close()
    result = []
    for d in DROPBOX.iterdir():
        if d.is_dir() and not d.name.startswith("_"):
            if d.name not in noms_bdd and est_generique(d.name):
                result.append((d.name, str(d)))
    result.sort(key=lambda x: x[0])
    return result

def build_html(generiques):
    rows = ""
    for i, (nom, chemin) in enumerate(generiques):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        import urllib.parse
        chemin_enc = urllib.parse.quote(chemin, safe='')
        nom_html = nom.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows += f'<tr style="background:{bg}"><td style="padding:6px 10px;color:#888;font-size:12px;width:40px;">{i+1}</td>'
        rows += f'<td style="padding:6px 10px;"><a href="#" data-path="{chemin_enc}" class="ouvrir" style="color:#c0392b;text-decoration:none;">{nom_html}</a></td></tr>\n'

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Dossiers génériques ({len(generiques)})</title>
<style>
  body {{ font-family: Segoe UI, sans-serif; margin: 30px; background: #f0f0f0; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .subtitle {{ color: #666; font-size: 13px; margin-bottom: 20px; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-radius: 6px; overflow: hidden; }}
  th {{ background: #c0392b; color: white; padding: 8px 10px; text-align: left; font-size: 13px; }}
  tr:hover td {{ background: #fdecea !important; }}
  a {{ cursor: pointer; }}
  .info {{ background: #e8f5e9; border: 1px solid #66bb6a; border-radius: 4px; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }}
</style>
</head>
<body>
<h1>Dossiers génériques / contenu absent</h1>
<div class="subtitle">{len(generiques)} dossiers identifiés</div>
<div class="info">Cliquez sur un nom pour ouvrir le dossier dans l'Explorateur.</div>
<table>
<thead><tr><th>#</th><th>Nom du dossier</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
<script>
document.querySelectorAll('a.ouvrir').forEach(function(a) {{
  a.addEventListener('click', function(e) {{
    e.preventDefault();
    var path = decodeURIComponent(this.getAttribute('data-path'));
    fetch('http://localhost:{PORT}/open?path=' + encodeURIComponent(path));
  }});
}});
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/open":
            params = parse_qs(parsed.query)
            path = unquote(params.get("path", [""])[0])
            if path:
                # Forcer les backslashes pour Windows
                path_win = path.replace("/", "\\")
                subprocess.Popen(['explorer', path_win])
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
        elif parsed.path in ("/", "/index.html"):
            generiques = get_generiques()
            html = build_html(generiques).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

print(f"Serveur actif sur http://localhost:{PORT}")
print("Ouvrez cette adresse dans votre navigateur.")
HTTPServer(("localhost", PORT), Handler).serve_forever()
