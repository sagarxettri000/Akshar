import csv

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    master = [(r["grade"], r["official_subject_name"]) for r in csv.DictReader(f)]

with open("../Nepluro/curriculum/neb_grade_11_12/curriculum_sources.csv", "r", encoding="utf-8") as f:
    sources = [(r["grade"], r["subject"]) for r in csv.DictReader(f)]

print("Master keys:", len(master))
print("Sources keys:", len(sources))
print("In Master but not Sources:", set(master) - set(sources))
print("In Sources but not Master:", set(sources) - set(master))
