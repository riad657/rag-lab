import chromadb
from chromadb.utils import embedding_functions
import glob
import os

def chunker(texte, taille_chunk, overlap):
    chunks = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille_chunk
        morceau = texte[debut:fin]
        chunks.append(morceau)
        debut = debut + taille_chunk - overlap
    return chunks

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
client.delete_collection(name="notices")
collection = client.get_or_create_collection(name="notices", embedding_function=modele_fr)

fichiers = glob.glob("corpus/*_clean.txt")
total_chunks = 0

for chemin_fichier in fichiers:
    nom_medicament = os.path.basename(chemin_fichier).replace("_clean.txt", "")

    with open(chemin_fichier, "r", encoding="utf-8") as f:
        texte = f.read()

    chunks = chunker(texte, taille_chunk=500, overlap=50)
    ids = [f"{nom_medicament}_{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, ids=ids)
    total_chunks += len(chunks)

    print(f"{nom_medicament} : {len(chunks)} chunks")

print()
print(f"Total de chunks générés : {total_chunks}")
print(f"Total de chunks dans Chroma : {collection.count()}")
