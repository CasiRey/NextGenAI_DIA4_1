#!/usr/bin/env python3
"""Replays every query of sql/ on data/boutique.sqlite, then the Python check.

Same job as run.sh, but with Python's built-in sqlite3 module, so it also runs
on Windows (no bash, no sqlite3 program needed):

    python td2/etape-b/run.py

Writes sorties/resultats-sql.txt and sorties/verif-python.txt, and prints both.
"""
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parents[1] / "data" / "boutique.sqlite"

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)  # read-only
con.execute("PRAGMA query_only = 1")

lines = []
for sql_file in sorted((HERE / "sql").glob("*.sql")):
    cursor = con.execute(sql_file.read_text(encoding="utf-8"))
    lines.append(f"== sql/{sql_file.name}")
    lines.append(" | ".join(col[0] for col in cursor.description))
    for row in cursor.fetchall():
        lines.append(" | ".join(str(value) for value in row))
    lines.append("")

(HERE / "sorties").mkdir(exist_ok=True)
sql_output = "\n".join(lines) + "\n"
(HERE / "sorties" / "resultats-sql.txt").write_text(sql_output, encoding="utf-8")

check = subprocess.run([sys.executable, str(HERE / "verif_c11.py")],
                       capture_output=True, text=True, check=True).stdout
(HERE / "sorties" / "verif-python.txt").write_text(check, encoding="utf-8")

print(sql_output + check)
