from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

phrases = [
    "Je m'appelle Riad.",
    "Mon nom est Riad.",
    "Le soleil s'est levé tôt aujourd'hui.",
    "J'aime pas les concombres dans mon burger.",
    "Ma bouteille est bleue.",
]

vecteurs = model.encode(phrases)

def similarite_cosinus(a, b):
    produit_scalaire = np.dot(a, b)
    norme_a = np.linalg.norm(a)
    norme_b = np.linalg.norm(b)
    return produit_scalaire / (norme_a * norme_b)

for i in range(len(phrases)):
    for j in range(i + 1, len(phrases)):
        score = similarite_cosinus(vecteurs[i], vecteurs[j])
        print(f"Phrase {i+1} vs Phrase {j+1} : {score:.3f}")
