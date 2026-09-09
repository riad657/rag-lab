import csv
import time
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import glob
import os
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

tous_chunks = []
tous_ids = []
id_vers_texte = {}
for chemin_fichier in glob.glob("corpus/*_clean.txt"):
    nom_medicament = os.path.basename(chemin_fichier).replace("_clean.txt", "")
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        texte = f.read()
    chunks = chunker_structurel(texte)
    for i, c in enumerate(chunks):
        chunk_id = f"{nom_medicament}_{i}"
        tous_chunks.append(c)
        tous_ids.append(chunk_id)
        id_vers_texte[chunk_id] = c

corpus_tokenise = [c.lower().split() for c in tous_chunks]
bm25 = BM25Okapi(corpus_tokenise)

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="notices_structurel", embedding_function=modele_fr)

print("Chargement du cross-encoder...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def recherche_hybride(question, k_large=10):
    scores_bm25 = bm25.get_scores(question.lower().split())
    max_bm25 = max(scores_bm25) if max(scores_bm25) > 0 else 1
    scores_bm25_norm = {tous_ids[i]: scores_bm25[i] / max_bm25 for i in range(len(tous_ids))}

    resultats = collection.query(query_texts=[question], n_results=min(20, len(tous_ids)))
    ids_denses = resultats["ids"][0]
    distances = resultats["distances"][0]
    max_dist = max(distances) if distances else 1
    scores_denses_norm = {ids_denses[i]: 1 - (distances[i] / max_dist) for i in range(len(ids_denses))}

    tous_les_ids_scores = set(scores_bm25_norm.keys()) | set(scores_denses_norm.keys())
    scores_finaux = {}
    for chunk_id in tous_les_ids_scores:
        s_bm25 = scores_bm25_norm.get(chunk_id, 0)
        s_dense = scores_denses_norm.get(chunk_id, 0)
        scores_finaux[chunk_id] = s_bm25 + s_dense

    top_large = sorted(scores_finaux.items(), key=lambda x: x[1], reverse=True)[:k_large]
    return [chunk_id for chunk_id, score in top_large]

def rerank(question, ids_candidats, k=3):
    paires = [(question, id_vers_texte[cid]) for cid in ids_candidats]
    scores_rerank = cross_encoder.predict(paires)
    classement = sorted(zip(ids_candidats, scores_rerank), key=lambda x: x[1], reverse=True)
    return [cid for cid, score in classement[:k]]

if __name__ == "__main__":
    with open("eval_questions.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    k = 3
    succes_recall = 0
    somme_reciprocal_rank = 0
    temps_total = 0

    for q in questions:
        debut_temps = time.time()
        candidats = recherche_hybride(q["question"], k_large=10)
        ids_trouves = rerank(q["question"], candidats, k=k)
        temps_total += time.time() - debut_temps

        medicament_attendu = q["medicament"]
        rang_trouve = None
        for rang, chunk_id in enumerate(ids_trouves, start=1):
            if chunk_id.startswith(medicament_attendu):
                rang_trouve = rang
                break
        if rang_trouve is not None:
            succes_recall += 1
            somme_reciprocal_rank += 1 / rang_trouve
        else:
            print(f"ÉCHEC — Q{q['id']}: {q['question']}")
            print(f"   Attendu: {medicament_attendu}, trouvé: {ids_trouves}")

    recall_at_k = succes_recall / len(questions)
    mrr = somme_reciprocal_rank / len(questions)
    latence_moyenne = temps_total / len(questions)

    print()
    print(f"Recall@{k} : {recall_at_k:.3f} ({succes_recall}/{len(questions)})")
    print(f"MRR : {mrr:.3f}")
    print(f"Latence moyenne par question : {latence_moyenne*1000:.1f} ms")
