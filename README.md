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

## CHECKPOINT DÉCISION D2

**Ce qui est gardé** : chunking structurel (2.4) + recherche hybride BM25+dense (2.5), version finale du retrieval pour la suite du projet (recall@3=0.833, MRR=0.794).

**Ce qui est jeté** : reranking cross-encoder (2.6). Gain trop marginal (+0.034 recall@3, +0.056 MRR) par rapport au coût en vitesse de réponse (199ms/question sur CPU, contre quasi-instantané sans).

**Avec un budget GPU** : deux changements. (1) Passer sur un modèle d'embedding plus grand que le MiniLM actuel, pour capter des nuances sémantiques plus fines (utile notamment sur le couple Amoxicilline/Augmentin). (2) Réintégrer le reranking : un GPU absorberait le sacrifice en vitesse actuellement rédhibitoire sur CPU, rendant le gain de précision du cross-encoder rentable sans coût perçu par l'utilisateur.

## Phase 3 — CHECKPOINT DÉCISION D3

**Choix retenu : (a) extraction structurée de la posologie en JSON.**

**Utilité produit** : (b) classification de gravité d'interaction serait plus directement utile — les interactions sont le point faible récurrent du retrieval (D1, D2), et les questions les plus critiques pour un utilisateur. Mais (a) reste utile : structurer la posologie en JSON est une brique concrète pour tout produit qui affiche des doses de façon fiable.

**Mesurabilité** : (a) a une réponse vérifiable objectivement (le JSON extrait correspond ou non au texte source). (b) nécessiterait de définir soi-même une échelle de gravité, avec un risque de subjectivité.

**Faisabilité du dataset** : différence décisive. Les notices contiennent déjà, littéralement, l'information de posologie structurée (ex: tableaux poids/dose/intervalle vus en 0.5c) — un dataset pour (a) est auto-extractible du texte source. Pour (b), aucun label de gravité n'existe dans les notices ; il faudrait annoter chaque interaction manuellement, sans expertise pharmaceutique, ce qui introduirait un vrai risque d'erreur dans le dataset d'entraînement lui-même.

**Verdict** : (b) serait le choix pertinent en situation réelle, avec le temps et l'expertise pour annoter correctement. Dans le cadre de cet apprentissage, (a) offre un dataset fiable et rapide à construire, permettant de bien exécuter les étapes 3.1 à 3.5 sans que la qualité du fine-tuning soit polluée par des labels de départ discutables.

## Phase 3 — Fine-tuning

### 3.1 — Dataset

Extraction automatique de la section Posologie sur les 15 notices (12/15 trouvées via le chunking structurel de 2.4 ; Smecta, Ventoline, Amlor non détectés, à creuser si besoin). Socle de 10 exemples réels construits à la main (texte source → JSON structuré), couvrant les deux cas observés : dose chiffrée exploitable (ex: Doliprane, Ibuprofène) et absence de dose fixe avec renvoi médecin (ex: Kardegic, Xanax) — le modèle doit apprendre à représenter les deux honnêtement, pas halluciner un chiffre absent.

Split train/val/test (7/1/2) figé avant toute génération de volume supplémentaire, pour éviter toute fuite de données entre reformulations proches d'un même exemple.

**Volume restant à générer** : 10/300-500 exemples réels obtenus directement du texte source. Le reste sera généré par reformulation (piste 2) du texte d'entrée, JSON de sortie identique, appliqué uniquement sur train/val — le test set (2 exemples) reste intouché jusqu'à 3.5.

**Décision volume dataset** : 44 exemples au total (41 train / 1 val / 2 test), en dessous de la fourchette indicative 300-500 du programme. Décision assumée : plutôt que de multiplier les reformulations par exemple (risque de redondance croissante — les variations tardives d'un même texte source deviennent de moins en moins distinctes), on privilégie un dataset plus petit mais entièrement vérifié (chaque reformulation contrôlée automatiquement contre falsification de chiffres, 1 seul rejet sur 35 générées). Cohérent avec la décision déjà prise en 1.1 (15 vs 20 documents) : questionner un volume cible du programme avec justification plutôt que le suivre aveuglément.
