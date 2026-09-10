import json

# Resultats colles a la main depuis les sorties de 3.2 et 3.4
resultats = {
    "Qwen zero-shot": [
        {"population": "objets structures (age/poids/genre)", "dose_max_prise": 1000, "intervalle_minimum": 4, "dose_max_jour": 3000},
        {"population": "aucune indication donnee", "dose_max_prise": 2000, "intervalle_minimum": None, "dose_max_jour": 2000},
    ],
    "Claude zero-shot": [
        {"population": "adulte et enfant a partir de 50 kg (environ 15 ans)", "dose_max_prise": "1000 mg", "intervalle_minimum": "4 heures", "dose_max_jour": "3000 mg"},
        {"population": "Insuffisance hepatique, alcoolisme chronique et syndrome de Gilbert", "dose_max_prise": None, "intervalle_minimum": None, "dose_max_jour": "2000 mg"},
    ],
    "Qwen fine-tune": [
        {"population": "objets structures (age/taille)", "dose_max_prise": 1000, "intervalle_minimum": 4, "dose_max_jour": 3000},
        {"population": "", "dose_max_prise": 2000, "intervalle_minimum": "", "dose_max_jour": ""},
    ],
}

attendus = [
    {"population": "adulte et enfant a partir de 50kg", "dose_max_prise": "1000 mg", "intervalle_minimum": "4 heures", "dose_max_jour": "3000 mg"},
    {"population": "insuffisance hepatique, alcoolisme chronique, syndrome de Gilbert", "dose_max_prise": None, "intervalle_minimum": None, "dose_max_jour": "2000 mg"},
]

def format_respecte(valeur):
    # Un champ respecte le format si c'est du texte avec unite (ou None), pas un nombre brut ou une structure
    if valeur is None or valeur == "":
        return None  # non evalue ici, gere separement
    return isinstance(valeur, str)

for nom_modele, sorties in resultats.items():
    total_champs = 0
    format_ok = 0
    for sortie, attendu in zip(sorties, attendus):
        for champ in ["population", "dose_max_prise", "intervalle_minimum", "dose_max_jour"]:
            total_champs += 1
            if format_respecte(sortie[champ]):
                format_ok += 1
    print(f"{nom_modele} : {format_ok}/{total_champs} champs au bon format ({100*format_ok/total_champs:.0f}%)")
