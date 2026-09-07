# RAG-LAB

Projet en cours — assistant RAG sur les données publiques du médicament (BDPM/ANSM).

Statut : Phase 1 terminée.

## Ce qui casse (Phase 1)

1. **Dosage Doliprane confondu avec Amoxicilline/Oméprazole** — Sur une question de dosage par poids pour Doliprane, le retrieval a renvoyé en priorité des chunks d'Amoxicilline et d'Oméprazole (résultats 1 et 2), le bon chunk Doliprane n'arrivant qu'en 3e position.
2. **Dose max Ibuprofène noyée dans un mauvais résultat** — Sur "dose maximale d'Ibuprofène par jour", le résultat le mieux classé provenait d'Oméprazole, sans rapport avec la question.
3. **Écart de vocabulaire marque/catégorie** — Sur "Previscan + Ibuprofène, interaction ?", les 3 chunks retournés parlaient bien d'Ibuprofène mais aucun ne mentionnait "Previscan" : la notice parle d'"anticoagulants oraux", jamais du nom de marque. Le retrieval par similarité ne fait pas ce pont sémantique.
4. **Mauvaise interaction remontée (Xanax)** — Sur "Xanax + Amoxicilline", le seul résultat pertinent trouvé concernait une interaction Xanax/opioïdes, un tout autre sujet.
5. **Échec total sur "dose oubliée" (Ventoline)** — Sur une question de dose oubliée pour Ventoline, les 3 résultats provenaient d'Amlor, Kardegic et Oméprazole : bon thème (dose oubliée) mais aucun ne concernait le bon médicament.
6. **Mot coupé en plein milieu par le chunking fixe** — Le découpage à taille fixe (500 caractères) coupe parfois au milieu d'un mot ("scrupuleusement" coupé en "cett" / "crupuleusement" entre deux chunks), sans respect du sens.
7. **Mélange de rubriques dans un même chunk** — Un chunk peut contenir la fin d'une rubrique et le début d'une autre sans rapport (ex: fin d'un paragraphe sur les délais de consultation + début du sommaire de la notice), diluant le sens du vecteur d'embedding associé.
8. **Absence d'indication thérapeutique dans le contexte retrouvé** — Sur "mal de tête, dois-je prendre du Doliprane ?", le système a refusé de répondre : les chunks trouvés concernaient Efferalgan/Dafalgan (pas Doliprane) et aucun ne mentionnait "maux de tête" comme indication.
9. **Retrieval totalement hors sujet sur Levothyrox** — Sur "à quoi sert le Levothyrox ?", alors que le document `03_levothyrox` existe bien dans la base (41 chunks indexés), le retrieval a renvoyé des chunks Kardegic et Dafalgan, sans aucun rapport.
10. **Modèle d'embedding par défaut de Chroma non-multilingue** — Sans configuration explicite, Chroma utilise un modèle d'embedding anglais (`all-MiniLM-L6-v2`) par défaut, incohérent avec un corpus entièrement en français. Repéré et corrigé avant l'indexation finale (1.3d), mais un piège silencieux facile à manquer.
