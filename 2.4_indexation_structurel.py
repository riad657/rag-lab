import chromadb
from chromadb.utils import embedding_functions
import glob
import os
import re

TITRES_RUBRIQUES = [
    "Posologie",
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
        pattern_titre = r"^" + re.escape(titre) + r"$" if titre == "Posologie" else re.escape(titre)
        flags = re.MULTILINE if titre == "Posologie" else 0
        match = re.search(pattern_titre, texte, flags)
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

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
try:
    client.delete_collection(name="notices_structurel")
except Exception:
    pass
collection = client.get_or_create_collection(name="notices_structurel", embedding_function=modele_fr)

fichiers = glob.glob("corpus/*_clean.txt")
total_chunks = 0

for chemin_fichier in fichiers:
    nom_medicament = os.path.basename(chemin_fichier).replace("_clean.txt", "")

    with open(chemin_fichier, "r", encoding="utf-8") as f:
        texte = f.read()

    chunks = chunker_structurel(texte)
    ids = [f"{nom_medicament}_{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, ids=ids)
    total_chunks += len(chunks)

    print(f"{nom_medicament} : {len(chunks)} chunks")

print()
print(f"Total de chunks générés : {total_chunks}")
print(f"Total de chunks dans Chroma : {collection.count()}")
