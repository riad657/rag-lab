import importlib.util
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

spec = importlib.util.spec_from_file_location("hybride", "2.5_hybride.py")
hybride = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybride)

id_vers_texte = dict(zip(hybride.tous_ids, hybride.tous_chunks))

def repondre(question, k=3):
    ids_trouves = hybride.recherche_hybride(question, k=k)
    contexte = ""
    for i, cid in enumerate(ids_trouves):
        contexte += f"[Source {i+1} - {cid}]\n{id_vers_texte[cid]}\n\n"

    prompt = f"""Tu es un assistant qui repond a des questions sur des medicaments, en te basant UNIQUEMENT sur les extraits fournis.

Regles strictes :
- Reponds uniquement a partir des extraits fournis.
- Cite la source entre crochets, ex: [Source 1].
- Si l'info n'y est pas, dis-le clairement : "Je ne trouve pas cette information dans les extraits fournis."

EXTRAITS:
{contexte}

QUESTION : {question}

REPONSE :"""

    reponse = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return reponse.content[0].text

print("=== Assistant RAG-LAB (retrieval hybride BM25+dense) ===")
print("Tapez votre question, ou 'quitter' pour arreter.\n")

while True:
    question = input("Votre question : ")
    if question.strip().lower() == "quitter":
        print("Au revoir.")
        break
    if question.strip() == "":
        continue
    print()
    print(repondre(question))
    print()
