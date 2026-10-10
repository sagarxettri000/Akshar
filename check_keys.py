import csv

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    master = [(r["grade"], r["official_subject_name"]) for r in csv.DictReader(f)]

with open("../Nepluro/curriculum/neb_grade_11_12/coverage_matrix.csv", "r", encoding="utf-8") as f:
    coverage = [(r["grade"], r["subject"]) for r in csv.DictReader(f)]

print("Master keys:", len(master))
print("Coverage keys:", len(coverage))
print("In Master but not Coverage:", set(master) - set(coverage))
print("In Coverage but not Master:", set(coverage) - set(master))
