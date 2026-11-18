# Relecture croisée de la paire B

Relecteur : Casimir Rey, paires A et C
Date : 18/11/2026

## Ce que j'ai rejoué

- [x] `python td2/etape-b/run.py` lancé sur ma machine (Windows), résultats identiques à `sorties/` : référence 446690, requêtes north et Dots à 0, requête delta à 6 clients, vérification Python à 446690
- [x] Les deux requêtes fausses de `sql/` correspondent à celles de `traces-td1.csv` (cellules `openrouter:cohere/north-mini-code:free:C11` et `openrouter:dots-studio/dots-3-note-preview:free:C11`)
- [x] Le comptage 2-of-3 et 3-of-5 donne le même résultat avec `vote_k_sur_n` (`outils/vote_table.py`, ligne C11)

## Ce que je sais expliquer

- **Pourquoi la requête Cohere ne garde aucun client :** elle calcule l'âge à l'envers (année de naissance − 2026, donc un nombre négatif) et ne compare jamais à 25 : elle teste si cette différence vaut 0 ou 1. Sur notre base, elle vaut entre −68 et −20, donc la condition n'est jamais vraie et aucun client n'est gardé.
- **Pourquoi la requête Dots donne 0 (deux raisons) :** d'abord, `birth_date = '2001-12-01'` ne garde que les clients nés ce jour précis, au lieu de tous ceux nés entre le 02/12/2000 et le 01/12/2001, et personne n'est né ce jour-là. Ensuite, elle ajoute un filtre sur les commandes du 01/12/2026, alors que la question porte sur toutes les commandes, et la dernière commande de la base date du 20/09/2026. Chaque condition seule suffit déjà à donner 0.
- **Pourquoi 2-of-3 donne 446 690 et 3-of-5 s'abstient :** dans le panel 2-sur-3 (120b, north, qwen), 446690 a 2 voix et 0 n'en a qu'une, car Dots n'est pas dans ce panel : consensus juste. En 3-sur-5, Dots rejoint north sur 0, qui a donc 2 voix, autant que 446690, et 20b donne 322160 : aucune valeur n'atteint 3 voix, abstention. La valeur fausse ne gagne pas, mais elle bloque la bonne.

## Remarques et corrections demandées

- `run.sh` demandait bash et le programme `sqlite3`, absents sous Windows : ajout de `run.py`, qui fait la même chose avec le module sqlite3 de Python. Sorties identiques.
- Le README indiquait « à revérifier avec `vote_k_sur_n` » : c'est fait, les décisions sont identiques.
- Point à retenir pour l'étape 3 : si un panel contenait north et Dots ensemble, le 0 gagnerait en 2-sur-3. Sur la famille âge, un vote ne suffit donc pas pour un chiffre client ou un versement.


