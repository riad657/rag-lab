from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

texte_court = "Je m'appelle Riad."

texte_long = """
La posologie recommandée est de 500 mg par voie orale, trois fois par jour,
pendant une durée maximale de sept jours consécutifs. Ce médicament est
contre-indiqué chez les patients présentant une insuffisance hépatique sévère,
une hypersensibilité connue à la substance active ou à l'un des excipients,
ainsi que chez la femme enceinte au cours du premier trimestre. Des interactions
ont été rapportées avec les anticoagulants oraux, augmentant le risque hémorragique,
et avec les inhibiteurs de l'enzyme de conversion, pouvant entraîner une hyperkaliémie.
Les effets indésirables les plus fréquemment observés incluent des nausées, des
céphalées et une somnolence légère à modérée.
"""

tokens_court = tokenizer.tokenize(texte_court)
tokens_long = tokenizer.tokenize(texte_long)

print(f"Texte court : {len(texte_court)} caractères, {len(tokens_court)} tokens")
print(f"Détail des tokens : {tokens_court}")
print()
print(f"Texte long : {len(texte_long)} caractères, {len(tokens_long)} tokens")
