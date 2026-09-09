import chromadb
from chromadb.utils import embedding_functions

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="notices", embedding_function=modele_fr)

questions = [
    "Je pèse 70 kg, quelle dose de Doliprane dois-je prendre ?",
    "Quelle est la dose maximale d'Ibuprofène par jour ?",
    "Je prends du Previscan, puis-je prendre de l'Ibuprofène en même temps ?",
    "Le Xanax et l'Amoxicilline peuvent-ils être pris ensemble ?",
    "J'ai oublié ma dose de Ventoline ce matin, puis-je doubler la dose ce soir ?",
]

for i, question in enumerate(questions):
    resultats = collection.query(query_texts=[question], n_results=3)
    print(f"=== Question {i+1} : {question} ===")
    for j, doc_id in enumerate(resultats["ids"][0]):
        print(f"--- Résultat {j+1} (id: {doc_id}) ---")
        print(resultats["documents"][0][j][:300])
        print()
    print()
