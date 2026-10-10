import csv

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

for field in records[0].keys():
    vals = set(r[field] for r in records)
    if len(vals) < 15:
        print(f"{field}: {vals}")
    else:
        print(f"{field}: ({len(vals)} distinct values)")
