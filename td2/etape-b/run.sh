#!/bin/sh
# Replays every query of the folder on data/boutique.sqlite and writes the outputs to sorties/
cd "$(dirname "$0")"
DB=../../data/boutique.sqlite
for f in sql/*.sql; do
  echo "== $f" ; sqlite3 -header -column "$DB" < "$f"
done > sorties/resultats-sql.txt
python3 verif_c11.py > sorties/verif-python.txt
cat sorties/resultats-sql.txt sorties/verif-python.txt
