import chromadb
from chromadb.utils import embedding_functions
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

modele_fr = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client_chroma = chromadb.PersistentClient(path="./chroma_db")
collection = client_chroma.get_collection(name="notices", embedding_function=modele_fr)

client_claude = Anthropic()

def repondre(question, n_chunks=3):
    resultats = collection.query(query_texts=[question], n_results=n_chunks)
    chunks_trouves = resultats["documents"][0]
    ids_trouves = resultats["ids"][0]

    contexte = ""
    for i, (chunk, chunk_id) in enumerate(zip(chunks_trouves, ids_trouves)):
        contexte += f"[Source {i+1} - {chunk_id}]\n{chunk}\n\n"

    prompt = f"""Tu es un assistant qui répond à des questions sur des médicaments, en te basant UNIQUEMENT sur les extraits de notices fournis ci-dessous.

Règles strictes :
- Réponds uniquement à partir des extraits fournis, jamais de tes connaissances générales.
- Cite la source utilisée entre crochets, par exemple [Source 1].
- Si les extraits ne contiennent pas l'information demandée, dis-le clairement : "Je ne trouve pas cette information dans les extraits fournis."

EXTRAITS :
{contexte}

QUESTION : {question}

RÉPONSE :"""

    reponse = client_claude.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return reponse.content[0].text

question_test = "Je prends du Previscan, puis-je prendre de l'Ibuprofène en même temps ?"
print(f"QUESTION : {question_test}\n")
print(repondre(question_test))
