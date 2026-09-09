import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

def extraire_chiffres(texte):
    return set(re.findall(r'\d+', texte))

def reformuler(texte_original, n_variations=5):
    prompt = f"""Voici un extrait de notice de médicament concernant la posologie :

"{texte_original}"

Génère {n_variations} reformulations différentes de ce texte, qui gardent EXACTEMENT le même sens et les mêmes chiffres (doses, intervalles, poids), mais avec une formulation différente. IMPORTANT : garde tous les chiffres en format numérique (1, 2, 3...), ne les transforme JAMAIS en toutes lettres (un, deux, trois) (vocabulaire, structure de phrase).

Réponds UNIQUEMENT avec les {n_variations} reformulations, une par ligne, sans numérotation ni commentaire."""

    reponse = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    lignes = [l.strip() for l in reponse.content[0].text.split("\n") if l.strip()]
    return lignes

with open("dataset_train.jsonl", "r", encoding="utf-8") as f:
    exemples_train = [json.loads(line) for line in f]
with open("dataset_val.jsonl", "r", encoding="utf-8") as f:
    exemples_val = [json.loads(line) for line in f]

nouveaux_train = []
rejets = 0

for ex in exemples_train:
    champs_dose = {k: v for k, v in ex["output"].items() if k in ["dose_max_prise", "intervalle_minimum", "dose_max_jour"] and v}
    chiffres_attendus = extraire_chiffres(json.dumps(champs_dose))
    variations = reformuler(ex["input"], n_variations=5)
    for v in variations:
        chiffres_variation = extraire_chiffres(v)
        if chiffres_attendus.issubset(chiffres_variation) or len(chiffres_attendus) == 0:
            nouveaux_train.append({"input": v, "output": ex["output"]})
        else:
            rejets += 1
            print(f"REJETÉ : texte=[{v}] attendu={chiffres_attendus} trouve={chiffres_variation}")

with open("dataset_train.jsonl", "a", encoding="utf-8") as f:
    for ex in nouveaux_train:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"\n{len(nouveaux_train)} reformulations ajoutées au train")
print(f"{rejets} reformulations rejetées (chiffres incohérents)")
