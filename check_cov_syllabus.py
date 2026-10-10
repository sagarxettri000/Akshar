import csv

with open("../Nepluro/curriculum/neb_grade_11_12/coverage_matrix.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    if r["syllabus_structure_status"] != "NOT_EXTRACTED":
        print(f"Grade {r['grade']} {r['subject']}: syllabus_structure_status={r['syllabus_structure_status']}")
