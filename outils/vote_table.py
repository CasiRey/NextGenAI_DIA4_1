#!/usr/bin/env python3
"""TD 2, step 1: 2-of-3 (fixed panel) versus 3-of-5 (all five TD 1 models), C01 to C20.

    python3 outils/vote_table.py                 # Markdown table on stdout
    python3 outils/vote_table.py --csv resultats/vote-td2.csv

Proposals are built exactly as atelier-vote.py does: last attempt per member,
verdict correct/incorrect with a value -> "executed", anything else -> "error"
(the member stays in n but does not vote). The reference is read only AFTER the
vote, to say whether the decision matches it.
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)

PANEL_3 = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"),
           ("groq", "qwen/qwen3.8-27b")]
PANEL_5 = PANEL_3 + [("groq", "openai/gpt-oss-20b"),
                     ("openrouter", "dots-studio/dots-3-note-preview:free")]
SHORT = {"openai/gpt-oss-120b": "120b", "cohere/north-mini-code:free": "north",
         "qwen/qwen3.8-27b": "qwen", "openai/gpt-oss-20b": "20b",
         "dots-studio/dots-3-note-preview:free": "dots"}


def proposals(rows, case, panel):
    last = {}
    for row in rows:  # chronological export: the last row per member is its last attempt
        key = (row["provider"], row["model_requested"])
        if row["case_id"] == case and row["nature"] == "real" and key in panel:
            last[key] = row
    out = []
    for provider, model in panel:
        row = last.get((provider, model), {})
        valid = row.get("verdict") in {"correct", "incorrect"} and row.get("value") not in {None, ""}
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(row["value"]) if valid else None,
                                   verdict="executed" if valid else "error",
                                   raw_verdict=row.get("verdict", "missing")))
    return out


def decide(props, k):
    return skeleton.Orchestrateur.vote_k_sur_n(None, props, k)


def label(decision, reference):
    if not decision["consensus"]:
        return f"abstain ({decision['votes']} max)"
    ok = "OK" if decision["value"] == reference else "WRONG"
    return f"{decision['value']} {ok} ({decision['votes']})"


def detail(props):
    return ", ".join(f"{SHORT[p.model_requested]}={p.value if p.value is not None else p.raw_verdict}"
                     for p in props)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", default=ROOT / "traces-td1.csv", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    rows = list(csv.DictReader(args.traces.open(encoding="utf-8", newline="")))
    refs = {r["case_id"]: int(r["reference"]) for r in rows if r["reference"]}

    table = []
    for i in range(1, 21):
        case = f"C{i:02d}"
        p3, p5 = proposals(rows, case, PANEL_3), proposals(rows, case, PANEL_5)
        d3, d5 = decide(p3, 2), decide(p5, 3)
        table.append({"case_id": case, "reference": refs[case],
                      "2of3": label(d3, refs[case]), "3of5": label(d5, refs[case]),
                      "same_decision": (d3["consensus"], d3["value"]) == (d5["consensus"], d5["value"]),
                      "proposals_5": detail(p5)})

    print("| Case | Reference | 2-of-3 | 3-of-5 | Change | Five proposals (last attempt) |")
    print("|---|---|---|---|---|---|")
    for t in table:
        print(f"| {t['case_id']} | {t['reference']} | {t['2of3']} | {t['3of5']} | "
              f"{'' if t['same_decision'] else 'yes'} | {t['proposals_5']} |")
    for name in ("2of3", "3of5"):
        ok = sum("OK" in t[name] for t in table)
        wrong = sum("WRONG" in t[name] for t in table)
        abst = sum("abstain" in t[name] for t in table)
        print(f"\n{name}: {ok} correct, {wrong} wrong consensus, {abst} abstentions (20 questions)")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)


if __name__ == "__main__":
    main()
