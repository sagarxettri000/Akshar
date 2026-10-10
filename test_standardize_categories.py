import csv
import json
from pathlib import Path

csv_path = Path("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv")
with csv_path.open("r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

for r in records:
    if r["subject_category"] == "Compulsory (all streams)":
        r["subject_category"] = "Compulsory (All streams)"

print("Standardized categories in records:")
for r in records:
    if r["official_subject_name"] in ("English", "Nepali"):
        print(f"Grade {r['grade']} {r['official_subject_name']}: {r['subject_category']}")
