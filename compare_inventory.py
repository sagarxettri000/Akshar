import csv
import json

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.csv", "r", encoding="utf-8") as f:
    csv_records = list(csv.DictReader(f))

with open("../Nepluro/curriculum/neb_grade_11_12/master_subject_inventory.json", "r", encoding="utf-8") as f:
    json_records = json.load(f)

print(f"CSV count: {len(csv_records)}, JSON count: {len(json_records)}")

# Compare fields
for i, (c, j) in enumerate(zip(csv_records, json_records)):
    diffs = []
    for k in c:
        if c.get(k) != j.get(k):
            diffs.append((k, c.get(k), j.get(k)))
    if diffs:
        print(f"Record {i} ({c.get('grade')} {c.get('official_subject_name')}): {diffs}")

# Check source IDs in master vs curriculum_sources
with open("../Nepluro/curriculum/neb_grade_11_12/curriculum_sources.csv", "r", encoding="utf-8") as f:
    source_records = list(csv.DictReader(f))

source_ids = set(r["source_id"] for r in source_records)
master_source_ids = set(r["curriculum_source_id"] for r in csv_records)

missing_sources = master_source_ids - source_ids
print("Missing source IDs in curriculum_sources.csv:", missing_sources)
