import os
import docx
import pdfplumber

dossiers = [
    (921, r"C:\Users\moina\Dropbox\Animation\Activités v2\Balade musicale contée"),
    (226, r"C:\Users\moina\Dropbox\Animation\Activités v2\Concours d'anecdotes"),
    (486, r"C:\Users\moina\Dropbox\Animation\Activités v2\Histoire loopstation"),
    (293, r"C:\Users\moina\Dropbox\Animation\Activités v2\Jeu des 10s"),
    (259, r"C:\Users\moina\Dropbox\Animation\Activités v2\Qu'est-ce qu'un être vivant"),
    (1054, r"C:\Users\moina\Dropbox\Animation\Activités v2\Redonner un visage à l'arbre en créant un petit bonhomme"),
    (242, r"C:\Users\moina\Dropbox\Animation\Activités v2\Sexualité des fleurs"),
]

def lire_docx(path):
    doc = docx.Document(path)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())

def lire_pdf(path):
    texte = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:5]:
            t = page.extract_text()
            if t:
                texte.append(t)
    return '\n'.join(texte)

for aid, dossier in dossiers:
    print(f"\n{'='*60}")
    print(f"ID: {aid} | {os.path.basename(dossier)}")
    fichiers = os.listdir(dossier)
    desc_files = [f for f in fichiers if '_DESC_' in f.upper()]
    for df in desc_files:
        path = os.path.join(dossier, df)
        ext = os.path.splitext(df)[1].lower()
        print(f"\n  -- Fichier: {df}")
        try:
            if ext == '.docx':
                content = lire_docx(path)
            elif ext == '.pdf':
                content = lire_pdf(path)
            else:
                print("  (type non géré)")
                continue
            print(content[:3000])
        except Exception as e:
            print(f"  ERREUR: {e}")
