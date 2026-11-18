# Rapport du TD 2 : le quorum, puis la règle de routage

DIA4, sous-groupe 4. Séance du 18/11/2026. Aucun nouvel appel réseau : tout part des traces du TD 1 (traces-td1.csv).

## Étape 1 : le vote k-sur-n

Panel 2-sur-3 : gpt-oss-120b, north-mini-code, qwen3.8-27b. Quorum 3-sur-5 : les cinq modèles du TD 1. Tableau généré par `outils/vote_table.py` avec notre `vote_k_sur_n`.

[tableau des votes](../resultats/vote-td2.md)

**Bilan :** 2-sur-3 décide juste 16 fois et s'abstient 4 fois ; 3-sur-5 décide juste 15 fois et s'abstient 5 fois. Aucun des deux ne valide une valeur fausse. Toutes les abstentions portent sur des questions avec un filtre d'âge.

### Les trois questions où la décision change

- **C02, consensus → abstention.** En 2-sur-3, 120b et qwen donnent 590320 : 2 voix pour k = 2, consensus juste ; north (SQL invalide) reste dans n sans voter. En 3-sur-5, 590320 reste à 2 voix pour k = 3, car 20b (0) et Dots (321340) se trompent sur des valeurs différentes : abstention. Élargir le panel avec deux modèles faibles sur l'âge fait perdre une bonne réponse.
- **C10, abstention → consensus.** En 2-sur-3, qwen renvoie un SQL invalide (il compte dans n = 3 sans voter) et north donne 907310 : 120b reste seul avec 558980, 1 voix pour k = 2, abstention. En 3-sur-5, 20b et Dots rejoignent 120b sur 558980 : 3 voix pour k = 3, consensus juste.
- **C11, consensus → abstention, à cause d'un faux consensus.** En 2-sur-3, 120b et qwen donnent 446690 : consensus juste ; north (0) est battu. En 3-sur-5, 446690 a 2 voix, mais 0 en a aussi 2 (north et Dots), et 20b donne 322160 : personne n'atteint 3, abstention. La valeur fausse ne gagne pas, mais elle empêche la bonne de gagner (voir l'étape B).

Les autres abstentions sont communes aux deux quorums : sur C09, C15 et C17, gpt-oss-120b a la bonne valeur, mais aucune valeur ne dépasse 1 voix en 2-sur-3 ni 2 voix en 3-sur-5. Un seul modèle juste ne suffit pas à un quorum.