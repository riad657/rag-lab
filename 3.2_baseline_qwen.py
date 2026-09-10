import json
from transformers import AutoModelForCausalLM, AutoTokenizer

print("Chargement du modele (peut prendre plusieurs minutes)...")
nom_modele = "Qwen/Qwen2.5-1.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(nom_modele)
model = AutoModelForCausalLM.from_pretrained(nom_modele)
print("Modele charge.")

with open("dataset_test.jsonl", "r", encoding="utf-8") as f:
    exemples_test = [json.loads(line) for line in f]

def extraire_json(texte_input):
    prompt = f"""Extrait les informations de posologie de ce texte en JSON, avec les champs : medicament, population, dose_max_prise, intervalle_minimum, dose_max_jour.

Texte : "{texte_input}"

Reponds UNIQUEMENT avec le JSON, sans commentaire."""

    messages = [{"role": "user", "content": prompt}]
    texte_formate = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(texte_formate, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=200)
    reponse = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return reponse

for i, ex in enumerate(exemples_test):
    print(f"\n=== Exemple test {i+1} ===")
    print("INPUT:", ex["input"])
    print("ATTENDU:", json.dumps(ex["output"]))
    print("QWEN 1.5B REPOND:")
    print(extraire_json(ex["input"]))
