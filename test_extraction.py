import re

TITRES_RUBRIQUES = [
    "Posologie", "Ne prenez jamais", "Autres médicaments et",
    "Avertissements et précautions", "Effets indésirables",
    "Comment conserver", "Mode d'administration", "Durée du traitement",
]

def chunker_structurel(texte, taille_min=100):
    if "QU\u2019EST-CE QUE" in texte:
        texte = texte.split("QU\u2019EST-CE QUE", 1)[-1]
    positions = []
    for titre in TITRES_RUBRIQUES:
        pattern_titre = r"^" + re.escape(titre) + r"$" if titre == "Posologie" else re.escape(titre)
        flags = re.MULTILINE if titre == "Posologie" else 0
        match = re.search(pattern_titre, texte, flags)
        if match:
            positions.append((match.start(), titre))
    positions_valeurs = sorted(set(p[0] for p in positions))
    if not positions_valeurs:
        return {}
    if positions_valeurs[0] > 0:
        positions_valeurs = [0] + positions_valeurs
    rubriques = {}
    for i in range(len(positions_valeurs)):
        debut = positions_valeurs[i]
        fin = positions_valeurs[i + 1] if i + 1 < len(positions_valeurs) else len(texte)
        morceau = texte[debut:fin].strip()
        for titre in TITRES_RUBRIQUES:
            if morceau.startswith(titre):
                rubriques[titre] = morceau
                break
    return rubriques

with open("corpus/01_doliprane_clean.txt", "r", encoding="utf-8") as f:
    texte = f.read()

rubriques = chunker_structurel(texte)


import glob
import os

for chemin_fichier in sorted(glob.glob("corpus/*_clean.txt")):
    nom_medicament = os.path.basename(chemin_fichier).replace("_clean.txt", "")
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        texte_notice = f.read()
    rubriques_notice = chunker_structurel(texte_notice)
    posologie = rubriques_notice.get("Posologie", "NON TROUVE")
    print(f"=== {nom_medicament} ===")
    print(posologie[:700])
    print()
