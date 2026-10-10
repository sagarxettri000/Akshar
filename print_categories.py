import csv

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    categories = set(r["subject_category"] for r in csv.DictReader(f))

print("Unique subject categories in master_subject_inventory.csv:")
for c in sorted(categories):
    print(" -", repr(c))
