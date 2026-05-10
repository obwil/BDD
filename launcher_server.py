# launcher_server.py — serveur local pour l'interface de lancement des scripts
# Port 18766 — accès via http://localhost:18766

import subprocess
import sys
from pathlib import Path
from flask import Flask, Response, send_from_directory, request, jsonify

app = Flask(__name__)
OUTIL_DIR = Path(__file__).parent
PYTHON = r"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe"

# Scripts qui ouvrent leur propre fenêtre (lancés en détaché, pas de streaming)
DETACHED = {
    "demarrer_app.bat",
    "demarrer_favoris.bat",
    "reinitialiser_bdd.bat",
}

@app.route("/")
def index():
    return send_from_directory(str(OUTIL_DIR), "launcher.html")

@app.route("/api/run", methods=["POST"])
def run_script():
    data = request.get_json()
    script = data.get("script", "")
    script_path = OUTIL_DIR / script

    if not script_path.exists():
        return jsonify({"error": f"Fichier introuvable : {script}"}), 404

    is_bat = script.endswith(".bat")
    is_detached = script in DETACHED

    if is_detached:
        # Lancer en détaché sans capturer la sortie
        if is_bat:
            subprocess.Popen(
                ["cmd", "/c", "start", "", str(script_path)],
                cwd=str(OUTIL_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            subprocess.Popen(
                [PYTHON, str(script_path)],
                cwd=str(OUTIL_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        return jsonify({"ok": True, "detached": True})

    def generate():
        if is_bat:
            cmd = ["cmd", "/c", str(script_path)]
        else:
            cmd = [PYTHON, str(script_path)]

        proc = subprocess.Popen(
            cmd,
            cwd=str(OUTIL_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        for line in proc.stdout:
            yield f"data: {line.rstrip()}\n\n"
        proc.wait()
        code = proc.returncode
        yield f"data: [TERMINÉ — code {code}]\n\n"
        yield "data: __END__\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

if __name__ == "__main__":
    print("Launcher disponible sur http://localhost:18766")
    app.run(host="127.0.0.1", port=18766, debug=False, threaded=True)
