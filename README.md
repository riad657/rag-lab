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

## Tableau de métriques

| Version | Recall@3 | MRR | Date |
|---|---|---|---|
| Naïf (chunking fixe 500/50, embedding seul) | 0.633 | 0.522 | 2026-09-08 |
| Chunking structurel (découpage par rubrique) | 0.767 | 0.656 | 2026-09-08 |

**Décision 2.4** : nette progression du chunking structurel comparé au chunking naïf (+0.134 recall@3, +0.134 MRR) — on conserve le chunking structurel comme base pour la suite des améliorations (2.5, 2.6). Échecs restants (7/30) concentrés sur Amoxicilline/Augmentin, deux antibiotiques chimiquement proches — plus un problème de proximité sémantique légitime qu'un défaut de chunking, à traiter en 2.5/2.6.

| Hybride BM25 + dense (fusion des scores) | 0.833 | 0.794 | 2026-09-09 |

**Décision 2.5** : nette progression avec l'hybride BM25+dense (+0.066 recall@3, +0.138 MRR vs structurel seul). On conserve l'hybride. 5 échecs restants concentrent tous sur le couple Amoxicilline/Augmentin — vérifié empiriquement : le mot "amoxicilline" apparaît littéralement dans la notice Augmentin (association amoxicilline + acide clavulanique), rendant la confusion inévitable pour toute méthode par mots-clés ou par sens, sans connaissance externe du nom commercial exact.

| Reranking cross-encoder (top-10 → rerank → top-3) | 0.867 | 0.850 | 2026-09-09 |

**Décision 2.6** : gain marginal avec le reranking (+0.034 recall@3, +0.056 MRR) comparé au coût introduit (latence moyenne 199ms/question, contre quasi-instantané pour l'hybride seul) et à l'apparition d'un nouvel échec (Q17, absent avec l'hybride simple). Le reranking corrige 2 cas mais en casse 1 — pas strictement supérieur, juste différent. Décision : reranking NON conservé pour la suite du projet ; l'hybride BM25+dense (2.5) reste la version retenue, meilleur rapport gain/coût de toute la phase 2B.
