import sys
import importlib.util
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

spec = importlib.util.spec_from_file_location("hybride", "2.5_hybride.py")
hybride = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybride)

def repondre(question, k=3):
    ids_trouves = hybride.recherche_hybride(question, k=k)
    contexte = ""
    for i, cid in enumerate(ids_trouves):
        contexte += f"[Source {i+1} - {cid}]\n{dict(zip(hybride.tous_ids, hybride.tous_chunks))[cid]}\n\n"

    prompt = f"""Tu es un assistant qui repond a des questions sur des medicaments, en te basant UNIQUEMENT sur les extraits fournis.

Regles strictes :
- Reponds uniquement a partir des extraits fournis.
- Cite la source entre crochets, ex: [Source 1].
- Si l'info n'y est pas, dis-le clairement.

EXTRAITS:
{contexte}

QUESTION : {question}

REPONSE :"""

    reponse = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return reponse.content[0].text

questions_demo = [
    "Quelle est la posologie du Doliprane pour un adulte de 70 kg ?",
    "Quelles sont les contre-indications du Kardegic ?",
    "Puis-je prendre du Previscan avec de l'Ibuprofene ?",
]

print("=== RAG-LAB - Demonstration ===\n")
for q in questions_demo:
    print(f">>> {q}\n")
    print(repondre(q))
    print("\n" + "-"*60 + "\n")
