"""Independent check of C11 without SQL: reads the CSV files in data/."""
import csv
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
REF_DATE = date(2026, 12, 1)

def age(birth):
    y, m, d = map(int, birth.split("-"))
    return REF_DATE.year - y - ((REF_DATE.month, REF_DATE.day) < (m, d))

price = {r["product_id"]: int(r["price"]) for r in csv.DictReader(open(DATA / "product.csv"))}
aged_25 = {r["customer_id"] for r in csv.DictReader(open(DATA / "customers.csv")) if age(r["birth_date"]) == 25}
total = sum(int(o["quantity_product"]) * price[o["product_id"]]
            for o in csv.DictReader(open(DATA / "orders.csv")) if o["customer_id"] in aged_25)
print("customers aged 25:", sorted(aged_25))
print("revenue_cents:", total)
