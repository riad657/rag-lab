import csv
import chromadb
from chromadb.utils import embedding_functions

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="notices", embedding_function=modele_fr)

with open("eval_questions.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    questions = list(reader)

k = 3
succes_recall = 0
somme_reciprocal_rank = 0

for q in questions:
    resultats = collection.query(query_texts=[q["question"]], n_results=k)
    ids_trouves = resultats["ids"][0]

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

print()
print(f"Recall@{k} : {recall_at_k:.3f} ({succes_recall}/{len(questions)})")
print(f"MRR : {mrr:.3f}")
