# TD 2, étape 2 : faux consensus 

| Fichier | Contenu |
|---|---|
| [sql/c11-cohere.sql](sql/c11-cohere.sql), [sql/c11-dots.sql](sql/c11-dots.sql) | Les deux requêtes fausses, copiées de [traces-td1.csv](../../traces-td1.csv) |
| [sql/c11-reference.sql](sql/c11-reference.sql) | La requête de référence (446 690, comme [reference-td1.csv](../../reference-td1.csv)) |
| [sql/c11-delta.sql](sql/c11-delta.sql) | La requête delta |
| [sql/c11-dots-conditions.sql](sql/c11-dots-conditions.sql), [sql/c11-cohere-lhs.sql](sql/c11-cohere-lhs.sql) | Les tests qui isolent les clauses fautives |
| [verif_c11.py](verif_c11.py) | Recalcul en Python sans SQL |
| [run.py](run.py) | Rejoue tout sur `data/boutique.sqlite` avec le module `sqlite3` de Python (Windows, macOS, Linux) : `python td2/etape-b/run.py` |
| [run.sh](run.sh) | Même chose en bash avec le programme `sqlite3` (Linux, macOS) |
| [sorties/](sorties/) | Résultats obtenus |
| [review-1.md](review-1.md), [review-2.md](review-2.md) | Relectures croisées par les autres paires |

### Cas trouvé

On a cherché dans les 100 cellules de `traces-td1.csv` (5 modèles) les valeurs fausses identiques entre au moins deux modèles. Il y en a une seule :

- question : C11 (CA HT des clients qui ont 25 ans au 2026-12-01)
- valeur fausse : 0
- modèles : cohere/north-mini-code:free et dots-studio/dots-3-note-preview:free
- référence (`reference-td1.csv`) : 446 690
- nature : `real`, HTTP 200, une seule tentative

On utilise donc notre propre cas, pas DEMO-SQL-C11.

Réponses des cinq modèles sur C11 :

| Modèle | Verdict | Valeur |
|---|---|---|
| gpt-oss-120b | correct | 446 690 |
| qwen3.8-27b | correct | 446 690 |
| north-mini-code (Cohere) | incorrect | 0 |
| dots-3-note-preview | incorrect | 0 |
| gpt-oss-20b | incorrect | 322 160 |

### Résultat des quorums

Compté à la main, puis vérifié avec `vote_k_sur_n` de la paire A (`outils/vote_table.py`, ligne C11) : mêmes décisions.

- 2-of-3 (120b, Cohere, Qwen) : 446 690 a 2 voix, 0 a 1 voix. Consensus sur 446 690, c'est juste. Dots n'est pas dans ce panel, donc le 0 n'a qu'une voix.
- 3-of-5 (les 5 modèles) : 446 690 a 2 voix, 0 a 2 voix, 322 160 a 1 voix. Personne n'atteint 3, donc abstention.

Le 0 ne gagne dans aucun des deux cas, mais en 3-of-5 il bloque la bonne réponse. Si le panel avait contenu Cohere et Dots, le 0 aurait gagné en 2-of-3.

### Pourquoi les deux requêtes donnent 0

Pour avoir 25 ans le 2026-12-01, il faut être né entre le 2000-12-02 et le 2001-12-01 inclus.

Requête Cohere :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  (
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    CAST(SUBSTR('2026-12-01', 1, 4) AS INTEGER)
  ) =
  CASE
    WHEN SUBSTR(c.birth_date, 6, 2) || '-' || SUBSTR(c.birth_date, 9, 2) >
         SUBSTR('2026-12-01', 6, 2) || '-' || SUBSTR('2026-12-01', 9, 2)
    THEN 1 ELSE 0 END;
```

Le problème est dans le WHERE : la soustraction est à l'envers (année de naissance - 2026) et il n'y a pas de `= 25`. La partie gauche vaut entre -68 et -20 sur notre base, elle n'est jamais égale à 0 ou 1. Aucun client n'est gardé, donc on obtient 0.

Requête Dots :

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01'
  AND o.date >= '2026-12-01' AND o.date < '2026-12-02';
```

Deux erreurs dans le WHERE :
- `birth_date = '2001-12-01'` ne garde qu'un seul jour de naissance au lieu d'une année entière. Personne n'est né ce jour-là.
- le filtre sur `o.date` ne garde que les commandes du 1er décembre, alors que la question porte sur toutes les commandes. Nos commandes vont du 2026-01-06 au 2026-09-20.

On a testé chaque condition seule : les deux donnent 0.

Les erreurs ne sont pas les mêmes, mais elles finissent toutes les deux sur une sélection vide, donc 0.

### Requête delta

```sql
SELECT c.customer_id, c.birth_date,
       COUNT(*) AS order_lines,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product  p ON o.product_id  = p.product_id
WHERE c.birth_date >  date('2026-12-01', '-26 years')
  AND c.birth_date <= date('2026-12-01', '-25 years')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
```

Résultat sur `data/boutique.sqlite` ([sorties/resultats-sql.txt](sorties/resultats-sql.txt)) :

| customer_id | birth_date | lignes | revenue_cents |
|---|---|---|---|
| C001 | 2001-09-25 | 18 | 135 000 |
| C002 | 2001-09-24 | 6 | 25 920 |
| C003 | 2001-09-26 | 6 | 47 900 |
| C006 | 2001-11-30 | 10 | 77 450 |
| C008 | 2001-05-15 | 11 | 99 090 |
| C009 | 2001-03-10 | 9 | 61 330 |
| Total | | 60 | 446 690 |

Les requêtes fausses ne comptent aucune ligne, donc ces 6 clients font tout l'écart : 446 690 - 0 = 446 690.

Vérification des bornes : C007 (né le 2000-11-30) a 26 ans et C014 (né le 2001-12-08) a 24 ans, ils sont bien exclus.

### Vérification indépendante

On a recalculé en Python à partir des CSV de `data/` (sans SQL) : mêmes 6 clients, même total 446 690 ([sorties/verif-python.txt](sorties/verif-python.txt)).

### Conséquence

Sur C11 (famille F2), 3 modèles sur 5 se trompent et deux donnent la même valeur. Un vote ne suffit pas quand les modèles font des erreurs qui tombent sur la même valeur (ici 0). Pour un chiffre client ou un paiement sur F2, il faut une vérification déterministe (requête de référence), et un résultat à 0 doit être vérifié. On le transmet à la paire C.

*Aide IA (Claude) pour la rédaction et les scripts ; requêtes réexécutées et vérifiées par Simon et Vianney.*
