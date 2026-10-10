import csv
import re

with open("../Nepluro/create_sources.py", "r", encoding="utf-8") as f:
    code = f.read()

match = re.search(r'rows = \[\s*(.*?)\s*\]\s*# Write CSV', code, re.DOTALL)
rows = eval(f"[{match.group(1)}]")

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    master = {r["curriculum_source_id"]: r["syllabus_verification_status"] for r in csv.DictReader(f)}

print(f"Total rows in create_sources.py: {len(rows)}")
mismatches = 0
for r in rows:
    src_id = r[0]
    access_status = r[8]  # index 8: access_status
    verif = r[9]          # index 9: verification_status
    master_verif = master.get(src_id)
    if verif != master_verif:
        mismatches += 1
        print(f"Mismatch for {src_id}: source={verif}, master={master_verif}")
if mismatches == 0:
    print("All 36 source verification statuses match master_subject_inventory.csv exactly!")
print("Check completed.")
