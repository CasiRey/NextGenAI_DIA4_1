#!/usr/bin/env python3
"""TD 2 and TD 3: read the decisions of a routing rule, then adapt it to your own.

ADAPTED IN TD 2 by sub-group DIA4-4 (the original kit version is in Git history
and its output in resultats/routage-avant-td2.jsonl). No API call, no key.

Resources are the five TD 1 models, plus the paid OpenRouter route of
gpt-oss-120b as a last resort. Eligibility for a family = 100% correct on that
family's TD 1 cells (traces-td1.csv, last attempt per cell). Twenty questions
support a hypothesis for this batch only, not a general error rate.

Cash = estimated USD excluding tax per request on a paid route: mean TD 1 tokens
(about 641 input, 248 output for gpt-oss-120b) x portfolio price per million
tokens. Free routes cost 0 in cash; their quota is a scenario, not measured.

    python3 atelier-routage.py
    python3 atelier-routage.py --scenario "age, customer figure"
"""
import argparse
import json

# Families of the twenty questions (F1 period, F2 age on a date, F2b age at order, F3 products).
FAMILIES = {
    "F1": ["C01", "C04", "C05", "C06", "C07", "C20"],
    "F2": ["C02", "C08", "C09", "C11"],
    "F2b": ["C10"],
    "F3": ["C03", "C12", "C13", "C14"],
    "F1+F2": ["C15"],
    "F2+F3": ["C16"],
    "F1+F2+F3": ["C17", "C19"],
    "F1+F2b": ["C18"],
}

# TD 1 evidence per model: families where it was 100% correct, and the cells it missed.
RESOURCES = [
    {"id": "gpt-oss-20b@groq-free", "access": "free", "available": True, "cash": 0.0,
     "price_rank": 0.0000338,  # est. USD/request on the paid route of the same model: 641x0.018 + 247x0.09 per M
     "families": ["F1", "F2b", "F3", "F1+F2", "F2+F3", "F1+F2+F3", "F1+F2b"],
     "td1": "17/20; wrong on C02, C09, C11 (all F2, age bounds)", "reset_minutes": None},
    {"id": "gpt-oss-120b@groq-free", "access": "free", "available": True, "cash": 0.0,
     "price_rank": 0.000245, "families": list(FAMILIES),
     "td1": "20/20, every family", "reset_minutes": None},
    {"id": "qwen3.8-27b@groq-free", "access": "free", "available": True, "cash": 0.0,
     "price_rank": 0.000210,  # 630x0.04 + 137x1.35 per M
     "families": ["F1", "F3", "F2+F3", "F1+F2b"],
     "td1": "15/20; wrong on C09, C15, C17, C19, SQL invalid on C10", "reset_minutes": None},
    {"id": "north-mini-code@openrouter-free", "access": "free", "available": True, "cash": 0.0,
     "price_rank": None,  # no paid route documented: cannot be ranked on price
     "families": ["F1", "F3", "F1+F2b"],
     "td1": "12/20; 0/4 on F2, wrong on C10, C15, C16, C17 (C11 wrong consensus at 0)",
     "reset_minutes": None},
    {"id": "dots-3-note@openrouter-free", "access": "free", "available": True, "cash": 0.0,
     "price_rank": None, "families": ["F1", "F2b", "F3"],
     "td1": "13/20; wrong on C02, C08, C11 (F2) and C15-C18", "reset_minutes": None},
    {"id": "gpt-oss-120b@openrouter-paid", "access": "tokens", "available": True,
     "cash": 0.000245,  # 641 x 0.15/1e6 + 248 x 0.60/1e6
     "price_rank": 0.000245, "families": list(FAMILIES),
     "td1": "same model as gpt-oss-120b@groq-free (20/20); paid route not run in TD 1",
     "reset_minutes": None},
]

PANEL_2_OF_3 = "2-of-3 vote (gpt-oss-120b, north-mini-code, qwen3.8-27b), abstain -> human review"


def required_check(family, use):
    """The one-page rule (reports/td2.md): the check depends on the cost of an error."""
    cells = ",".join(FAMILIES[family])
    involves_age = "F2" in family
    if use == "payout":
        return f"deterministic reference SQL template + human review ({family}: {cells})"
    if use == "customer":
        return f"{PANEL_2_OF_3} ({family}: {cells})"
    # internal dashboard: no check only if low stakes AND the first model was 100% on the family
    if involves_age:
        return f"{PANEL_2_OF_3}; age family had TD 1 errors on C02, C08, C09, C11 ({family})"
    return f"none beyond read-only execution; first model 100% on {family} ({cells})"


def choose(request, resources):
    """Deterministic routing with an inspectable reason citing TD 1 cells.

    Order of preference, as in the kit: (1) eligible capacity available now at no
    cash, cheapest documented model first; (2) wait for a free refill if the request
    can wait and the refill comes before the deadline; (3) a paid route within
    budget; (4) abstain. At wake-up, availability must be measured again.
    """
    family = request["family"]
    checks = required_check(family, request["use"])
    eligible = [r for r in resources if family in r["families"]]
    rank = lambda r: (r["price_rank"] is None, r["price_rank"] or 0, r["id"])
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=rank)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"cheapest available free model 100% correct on {family} in TD 1 "
                          f"({','.join(FAMILIES[family])}); TD 1: {chosen['td1']}"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"free quota of the only eligible models exhausted; refill in "
                          f"{chosen['reset_minutes']} min, before the deadline; recheck at wake-up",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": f"no free eligible model now and the request cannot wait; paid route of a "
                          f"model 100% on {family} in TD 1; TD 1: {chosen['td1']}"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no model 100% on {family} in TD 1 available within deadline and budget; "
                      f"no value is returned rather than an unverified one"}


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.001}
    groq_out = [dict(r, available=False, reset_minutes=60) if r["id"].endswith("groq-free") else dict(r)
                for r in RESOURCES]
    only_20b_out = [dict(r, available=False, reset_minutes=60) if r["id"].startswith("gpt-oss-20b") else dict(r)
                    for r in RESOURCES]
    return [
        ("period, dashboard", base, RESOURCES),
        ("period, 20b quota exhausted", base, only_20b_out),
        ("products, customer figure", {**base, "family": "F3", "use": "customer"}, RESOURCES),
        ("age, dashboard", {**base, "family": "F2"}, RESOURCES),
        ("age, customer figure", {**base, "family": "F2", "use": "customer"}, RESOURCES),
        ("age, payout", {**base, "family": "F2", "use": "payout"}, RESOURCES),
        ("age, Groq exhausted, can wait", {**base, "family": "F2"}, groq_out),
        ("age, Groq exhausted, urgent", {**base, "family": "F2", "can_wait": False,
                                         "deadline_minutes": 5}, groq_out),
        ("age, Groq exhausted, no budget", {**base, "family": "F2", "can_wait": False,
                                            "budget": 0}, groq_out),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
