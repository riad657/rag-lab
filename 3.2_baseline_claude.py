import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

with open("dataset_test.jsonl", "r", encoding="utf-8") as f:
    exemples_test = [json.loads(line) for line in f]

def extraire_json(texte_input):
    prompt = f"""Extrait les informations de posologie de ce texte en JSON, avec les champs : medicament, population, dose_max_prise, intervalle_minimum, dose_max_jour.

Texte : "{texte_input}"

Reponds UNIQUEMENT avec le JSON, sans commentaire."""

    reponse = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return reponse.content[0].text

for i, ex in enumerate(exemples_test):
    print(f"\n=== Exemple test {i+1} ===")
    print("INPUT:", ex["input"])
    print("ATTENDU:", json.dumps(ex["output"]))
    print("CLAUDE REPOND:")
    print(extraire_json(ex["input"]))
