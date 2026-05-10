import os, glob

dossiers = [
    (921, r"C:\Users\moina\Dropbox\Animation\Activités v2\Balade musicale contée"),
    (226, r"C:\Users\moina\Dropbox\Animation\Activités v2\Concours d'anecdotes"),
    (486, r"C:\Users\moina\Dropbox\Animation\Activités v2\Histoire loopstation"),
    (293, r"C:\Users\moina\Dropbox\Animation\Activités v2\Jeu des 10s"),
    (259, r"C:\Users\moina\Dropbox\Animation\Activités v2\Qu'est-ce qu'un être vivant"),
    (1054, r"C:\Users\moina\Dropbox\Animation\Activités v2\Redonner un visage à l'arbre en créant un petit bonhomme"),
    (242, r"C:\Users\moina\Dropbox\Animation\Activités v2\Sexualité des fleurs"),
]

for aid, dossier in dossiers:
    print(f"\n{'='*60}")
    print(f"ID: {aid} | {os.path.basename(dossier)}")
    if not os.path.exists(dossier):
        print("  DOSSIER INTROUVABLE")
        continue
    fichiers = os.listdir(dossier)
    desc_files = [f for f in fichiers if '_DESC_' in f.upper() or f.upper().startswith('_DESC')]
    if not desc_files:
        print("  AUCUN FICHIER _DESC_")
        print(f"  Fichiers présents: {fichiers[:5]}")
        continue
    for df in desc_files:
        path = os.path.join(dossier, df)
        print(f"  Fichier: {df}")
        if df.lower().endswith('.txt'):
            try:
                with open(path, encoding='utf-8') as f:
                    content = f.read(2000)
                print(f"  Contenu:\n{content}")
            except:
                try:
                    with open(path, encoding='cp1252') as f:
                        content = f.read(2000)
                    print(f"  Contenu (cp1252):\n{content}")
                except Exception as e:
                    print(f"  Erreur lecture: {e}")
        else:
            print(f"  (non-texte, type: {os.path.splitext(df)[1]})")
