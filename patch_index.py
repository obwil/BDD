#!/usr/bin/env python3
from pathlib import Path

INDEX = Path(__file__).parent / "static" / "index.html"
BACKUP = INDEX.with_suffix(".html.bak2")

content = INDEX.read_text(encoding="utf-8")
original = content

# Patch 1 : style .btn-delete
old1 = "    .loading { text-align: center; padding: 40px; color: var(--text-muted); }\n  </style>"
new1 = (
    "    .loading { text-align: center; padding: 40px; color: var(--text-muted); }\n"
    "    .btn-delete {\n"
    "      display: inline-flex; align-items: center; gap: 5px;\n"
    "      font-size: .82rem; color: #c0392b;\n"
    "      border: 1px solid #c0392b; background: none;\n"
    "      padding: 5px 11px; border-radius: var(--radius); cursor: pointer;\n"
    "    }\n"
    "    .btn-delete:hover { background: #fdecea; }\n"
    "  </style>"
)

# Patch 2 : bouton Supprimer dans buildDrawer
# On cible uniquement la div style + le bouton edit, sans toucher aux apostrophes JS
old2 = '="margin-bottom:8px">\n    <button class="btn-edit" onclick="toggleEdit(${a.id})">✏️ Modifier</button>\n  </div>`;'
new2 = (
    '="margin-bottom:8px;display:flex;gap:8px">\n'
    '    <button class="btn-edit" onclick="toggleEdit(${a.id})">✏️ Modifier</button>\n'
    '    <button class="btn-delete" onclick="confirmerSuppression(${a.id}, this)">🗑️ Supprimer</button>\n'
    '  </div>`;'
)

# Patch 3 : fonction confirmerSuppression + init()
old3 = "init();\n</script>"
new3 = (
    "async function confirmerSuppression(id, btn) {\n"
    "  const nom = btn.closest('.drawer').querySelector('h2').textContent.trim();\n"
    "  if (!confirm('Supprimer \"' + nom + '\" ?\\n\\nLe dossier sera déplacé vers la corbeille.\\nCette action est irréversible depuis l\\'interface.')) {\n"
    "    return;\n"
    "  }\n"
    "  try {\n"
    "    const r = await fetch('/api/activites/' + id, { method: 'DELETE' });\n"
    "    if (!r.ok) {\n"
    "      const err = await r.json();\n"
    "      alert('Erreur : ' + (err.detail || r.status));\n"
    "      return;\n"
    "    }\n"
    "    closeDrawer();\n"
    "    search();\n"
    "  } catch(e) {\n"
    "    alert('Erreur réseau : ' + e.message);\n"
    "  }\n"
    "}\n"
    "\n"
    "init();\n"
    "</script>"
)

errors = []
for i, (old, new) in enumerate([(old1, new1), (old2, new2), (old3, new3)], 1):
    if old not in content:
        errors.append(i)
        print(f"ERREUR patch {i} : chaîne introuvable")
        print(f"  cherche : {repr(old[:100])}")
    else:
        content = content.replace(old, new, 1)
        print(f"Patch {i} OK")

if not errors:
    BACKUP.write_text(original, encoding="utf-8")
    INDEX.write_text(content, encoding="utf-8")
    print(f"\nindex.html mis a jour. Backup : {BACKUP.name}")
else:
    print("\nAucune modification appliquee.")
