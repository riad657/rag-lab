import re

TITRES_RUBRIQUES = [
    "^Posologie$",
    "Ne prenez jamais",
    "Autres médicaments et",
    "Avertissements et précautions",
    "Effets indésirables",
    "Comment conserver",
    "Mode d'administration",
    "Durée du traitement",
]

def chunker_structurel(texte, taille_min=100):
    if "QU\u2019EST-CE QUE" in texte:
        texte = texte.split("QU\u2019EST-CE QUE", 1)[-1]

    positions = []
    for titre in TITRES_RUBRIQUES:
        match = re.search(re.escape(titre) if not titre.startswith("^") else titre, texte, re.MULTILINE)
        if match:
            positions.append(match.start())

    positions = sorted(set(positions))

    if not positions:
        return [texte]

    if positions[0] > 0:
        positions = [0] + positions

    chunks = []
    for i in range(len(positions)):
        debut = positions[i]
        fin = positions[i + 1] if i + 1 < len(positions) else len(texte)
        morceau = texte[debut:fin].strip()
        if len(morceau) >= taille_min:
            chunks.append(morceau)

    return chunks

if __name__ == "__main__":
    with open("corpus/01_doliprane_clean.txt", "r", encoding="utf-8") as f:
        texte = f.read()

    chunks = chunker_structurel(texte)
    print(f"Nombre de chunks structurels : {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ({len(c)} caractères) ---")
        print(c[:200])
