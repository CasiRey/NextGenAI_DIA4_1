# Rapport du TD 2 : le quorum, puis la règle de routage

DIA4, sous-groupe 4. Séance du 18/11/2026. Aucun nouvel appel réseau : tout part des traces du TD 1 (traces-td1.csv).

## Étape 1 : le vote k-sur-n (Casimir et Lavinia)

Panel 2-sur-3 : gpt-oss-120b, north-mini-code, qwen3.8-27b. Quorum 3-sur-5 : les cinq modèles du TD 1. Tableau généré par `outils/vote_table.py` avec notre `vote_k_sur_n`.

[tableau des votes](../resultats/vote-td2.md)

**Bilan :** 2-sur-3 décide juste 16 fois et s'abstient 4 fois ; 3-sur-5 décide juste 15 fois et s'abstient 5 fois. Aucun des deux ne valide une valeur fausse. Toutes les abstentions portent sur des questions avec un filtre d'âge.

### Les trois questions où la décision change

- **C02, consensus → abstention.** En 2-sur-3, 120b et qwen donnent 590320 : 2 voix pour k = 2, consensus juste ; north (SQL invalide) reste dans n sans voter. En 3-sur-5, 590320 reste à 2 voix pour k = 3, car 20b (0) et Dots (321340) se trompent sur des valeurs différentes : abstention. Élargir le panel avec deux modèles faibles sur l'âge fait perdre une bonne réponse.
- **C10, abstention → consensus.** En 2-sur-3, qwen renvoie un SQL invalide (il compte dans n = 3 sans voter) et north donne 907310 : 120b reste seul avec 558980, 1 voix pour k = 2, abstention. En 3-sur-5, 20b et Dots rejoignent 120b sur 558980 : 3 voix pour k = 3, consensus juste.
- **C11, consensus → abstention, à cause d'un faux consensus.** En 2-sur-3, 120b et qwen donnent 446690 : consensus juste ; north (0) est battu. En 3-sur-5, 446690 a 2 voix, mais 0 en a aussi 2 (north et Dots), et 20b donne 322160 : personne n'atteint 3, abstention. La valeur fausse ne gagne pas, mais elle empêche la bonne de gagner (voir l'étape B).

Les autres abstentions sont communes aux deux quorums : sur C09, C15 et C17, gpt-oss-120b a la bonne valeur, mais aucune valeur ne dépasse 1 voix en 2-sur-3 ni 2 voix en 3-sur-5. Un seul modèle juste ne suffit pas à un quorum.


## Étape 2 : le faux consensus (Simon et Vianney)

Seul cas du lot : sur C11, north-mini-code et Dots renvoient tous deux 0 (référence 446 690). En 2-sur-3 le 0 est battu (Dots n'est pas dans le panel) ; en 3-sur-5 il fait égalité 2 contre 2 avec la bonne valeur, et le vote s'abstient. Vérifié avec notre `vote_k_sur_n`.

- north : soustraction inversée (année de naissance − 2026) et `= 25` absent ; la partie gauche vaut entre −68 et −20, jamais 0 ou 1 : aucun client.
- Dots : `birth_date = '2001-12-01'` (un seul jour au lieu d'une année, personne n'est né ce jour-là) et un filtre sur la date de commande absent de la question (aucune commande en décembre).
- Requête delta : 6 clients (C001, C002, C003, C006, C008, C009) pour exactement 446 690 centimes, recalculés aussi en Python sans SQL.

Détail, requêtes et sorties : [td2/etape-b/README.md](../td2/etape-b/README.md). Pour rejouer : `python td2/etape-b/run.py`.


## Étape 3 : la règle de routage (Augustin et Basile)

### Taux du TD 1 par famille

Dernière tentative par cellule, correct / questions. Vingt questions donnent une hypothèse pour ce lot, pas un taux d'erreur général.

| Famille | Questions | 120b | 20b | qwen | north | dots |
|---|---|---|---|---|---|---|
| F1 période | C01, C04-C07, C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F2 âge à une date | C02, C08, C09, C11 | 4/4 | 1/4 | 3/4 | 0/4 | 1/4 |
| F2b âge à la commande | C10 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| F3 produits | C03, C12-C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combinées avec l'âge | C15-C19 | 5/5 | 5/5 | 2/5 | 2/5 | 1/5 |

### La règle

Premier modèle : le moins cher selon le portefeuille parmi les modèles à 100 % sur la famille. Coût estimé par requête sur la route payante du même modèle (tokens moyens du TD 1 × prix) : 20b ≈ 0,000034 $, qwen ≈ 0,00021 $, 120b ≈ 0,000245 $. north et Dots n'ont pas de prix documenté : ils ne peuvent pas être classés, donc ils passent après.

| Famille | Premier modèle | Tableau de bord interne | Chiffre client | Versement |
|---|---|---|---|---|
| F1 période, F3 produits | 20b | aucun contrôle (5 modèles à 100 %) | 2-sur-3, abstention → revue humaine | requête de référence déterministe + revue humaine |
| F2 âge | 120b (seul à 4/4) | 2-sur-3 (erreurs au TD 1 sur C02, C08, C09, C11) | 2-sur-3, abstention → revue humaine | requête de référence déterministe + revue humaine |
| F2b et combinées avec l'âge | 20b (100 % sur C10, C15-C19), 120b en repli | 2-sur-3 | 2-sur-3, abstention → revue humaine | requête de référence déterministe + revue humaine |

« Aucun contrôle » n'apparaît que pour un tableau de bord interne ET une famille sans erreur au TD 1. Plus l'erreur coûte cher, plus le contrôle est fort : un tableau de bord se corrige au prochain rafraîchissement ; pour un chiffre client, on préfère l'abstention à une valeur fausse ; pour un versement, un vote ne suffit pas, car C11 montre deux modèles d'accord sur une valeur fausse.

Repli : modèle éligible suivant le moins cher ; sinon, attente de la recharge gratuite si la demande peut attendre (disponibilité mesurée à nouveau au réveil) ; sinon, route payante de 120b dans le budget ; sinon, abstention.

### Le simulateur, avant et après

**Avant** (kit d'origine, [resultats/routage-avant-td2.jsonl](../resultats/routage-avant-td2.jsonl)) : trois ressources fictives (small-free, senior-subscription, senior-api), choisies par niveau de capacité.
La version d’origine est conservée dans atelier-routage-ancien.py

**Après** ([atelier-routage.py](../atelier-routage.py), sortie dans [resultats/routage-apres-td2.jsonl](../resultats/routage-apres-td2.jsonl)) : les 5 modèles du TD 1, plus la route payante de 120b. Un modèle est éligible sur une famille s'il y a fait 100 % au TD 1 ; la demande porte une famille et un usage ; chaque `reason` cite les cellules du TD 1. L'ordre des branches de `choose` est inchangé.

| Scénario | Décision | Ressource | Contrôle |
|---|---|---|---|
| période, tableau de bord | run | 20b (Groq gratuit) | aucun (F1 à 100 %) |
| période, quota de 20b épuisé | run | qwen (Groq gratuit) | aucun ; qwen est le suivant le moins cher à 6/6 |
| produits, chiffre client | run | 20b (Groq gratuit) | 2-sur-3 |
| âge, tableau de bord | run | 120b (Groq gratuit) | 2-sur-3 (erreurs F2 au TD 1) |
| âge, chiffre client | run | 120b (Groq gratuit) | 2-sur-3, abstention → humain |
| âge, versement | run | 120b (Groq gratuit) | référence déterministe + revue humaine |
| âge, Groq épuisé, peut attendre | defer 60 min | 120b (Groq gratuit) | 2-sur-3 ; recharge avant l'échéance, revérifier au réveil |
| âge, Groq épuisé, urgent | run, 0,000245 $ | 120b (OpenRouter payant) | 2-sur-3 |
| âge, Groq épuisé, budget 0 | abstain | — | aucune valeur plutôt qu'une valeur non vérifiée |

### Analyse de la priorité de `choose`

`choose` teste ses branches dans un ordre fixe : (1) capacité incluse disponible maintenant (`available` et `cash == 0`), (2) attente d'une recharge gratuite, (3) route payante, (4) abstention. Un abonnement disponible a `cash = 0` : il tombe dans la branche 1, évaluée avant la branche 2, et il est donc choisi même si une ressource gratuite épuisée se recharge avant l'échéance.

C'est justifié : l'abonnement est déjà payé, son coût marginal est nul, il répond tout de suite, et il n'y a pas le risque de découvrir au réveil que le quota gratuit n'est toujours pas revenu. Attendre coûterait du délai sans rien économiser.

On inverserait cette priorité si l'allocation de l'abonnement était rare, par exemple un plafond mensuel partagé presque atteint, ou une capacité à garder pour des demandes urgentes à fort impact. Pour une demande qui peut attendre, il vaudrait alors mieux attendre la recharge gratuite et préserver l'abonnement. Dans le code, il suffirait de tester la branche « attente » avant la branche 1 pour les demandes `can_wait`.

## Limites

- 20 questions, un seul lot : les taux sont des hypothèses pour ce lot. Les familles combinées reposent sur 1 ou 2 cellules.
- Le vote 2-sur-3 contient qwen (Groq) : quand Groq est épuisé, le contrôle prévu n'est plus disponible non plus. Le simulateur ne vérifie la disponibilité que du premier modèle.
- La route payante de 120b n'a pas été appelée au TD 1 : on suppose que le même modèle se comporte de la même façon chez un autre fournisseur.
- Les coûts par requête sont estimés (tokens moyens × prix du portefeuille), pas mesurés.