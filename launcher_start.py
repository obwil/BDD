import subprocess
from pathlib import Path

bat = Path(r"C:\Users\moina\Dropbox\Outils\BDD activités\_OUTIL\lancer_launcher.bat")
subprocess.Popen(["cmd", "/c", str(bat)], cwd=str(bat.parent))
