import csv
import json
import re
from pathlib import Path

# Paths
nepluro_base = Path("../Nepluro/curriculum/neb_grade_11_12")
mlh_base = Path("curriculum/neb_grade_11_12")
mlh_base.mkdir(parents=True, exist_ok=True)

# 1. Fix syllabus_structure.json
syllabus_src = Path("../Nepluro/create_syllabus_structure.py").read_text(encoding="utf-8")
fixes = [
    ('"विकास र राष्ट्रवाद" (Development and Nationalism)', '"विकास र राष्ट्रवाद (Development and Nationalism)"'),
    ('"साहित्य प्रसार" (Literature dissemination)', '"साहित्य प्रसार (Literature dissemination)"'),
    ('" भाषा कौशल विकास" (Language skill development)', '"भाषा कौशल विकास (Language skill development)"'),
    ('" नेपाली भाषाको ज्ञान" (Knowledge of Nepali language)', '"नेपाली भाषाको ज्ञान (Knowledge of Nepali language)"'),
    ('" नेपाली भाषाको इतिहास र विकास" (History and development of Nepali language)', '"नेपाली भाषाको इतिहास र विकास (History and development of Nepali language)"'),
    ('" कविता र उपन्यास" (Poetry and Novel)', '"कविता र उपन्यास (Poetry and Novel)"'),
    ('" भाषाको उत्थान" (Language development)', '"भाषाको उत्थान (Language development)"'),
    ('" राष्ट्रीय एकता" (National unity)', '"राष्ट्रिय एकता (National unity)"'),
    ('" नेपाリग文学को इतिहास" (History of Nepali literature)', '"नेपाली साहित्यको इतिहास (History of Nepali literature)"'),
]
for old, new in fixes:
    syllabus_src = syllabus_src.replace(old, new)

syllabus_data = json.loads(syllabus_src)
syllabus_json_text = json.dumps(syllabus_data, indent=2, ensure_ascii=False)
(nepluro_base / "syllabus_structure.json").write_text(syllabus_json_text, encoding="utf-8")
(mlh_base / "syllabus_structure.json").write_text(syllabus_json_text, encoding="utf-8")
print(f"Created syllabus_structure.json with {len(syllabus_data)} subjects")

# Also update create_syllabus_structure.py in Nepluro to have valid JSON
Path("../Nepluro/create_syllabus_structure.py").write_text(syllabus_json_text, encoding="utf-8")

# 2. Fix curriculum_sources.csv
sources_src_path = nepluro_base / "curriculum_sources.csv"
with sources_src_path.open("r", encoding="utf-8") as f:
    rdr = csv.reader(f)
    header = next(rdr)
    raw_rows = list(rdr)

fixed_source_rows = []
for r in raw_rows:
    if len(r) == 10:
        src_id, doc_title, pub_auth, grade, subject, curr_yr, doc_type, off_url, verif_status, notes = r
        access_status = "PUBLIC_ACCESS"
        fixed_source_rows.append([src_id, doc_title, pub_auth, grade, subject, curr_yr, doc_type, off_url, access_status, verif_status, notes])
    elif len(r) == 11:
        fixed_source_rows.append(r)

for target_dir in (nepluro_base, mlh_base):
    with (target_dir / "curriculum_sources.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in fixed_source_rows:
            w.writerow(row)
print(f"Wrote curriculum_sources.csv with {len(fixed_source_rows)} rows (11 cols each)")

# 3. Standardize master_subject_inventory.csv and .json
master_csv_path = nepluro_base / "master_subject_inventory.csv"
with master_csv_path.open("r", encoding="utf-8") as f:
    rdr = csv.reader(f)
    m_header = next(rdr)
    m_rows = list(rdr)

for row in m_rows:
    # index 4 is subject_category
    if row[4] == "Compulsory (all streams)":
        row[4] = "Compulsory (All streams)"

for target_dir in (nepluro_base, mlh_base):
    with (target_dir / "master_subject_inventory.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(m_header)
        for row in m_rows:
            w.writerow(row)

# Update master_subject_inventory.json
master_json = []
for row in m_rows:
    entry = {m_header[i]: row[i] for i in range(len(m_header))}
    master_json.append(entry)

master_json_text = json.dumps(master_json, indent=2, ensure_ascii=False)
(nepluro_base / "master_subject_inventory.json").write_text(master_json_text, encoding="utf-8")
(mlh_base / "master_subject_inventory.json").write_text(master_json_text, encoding="utf-8")
print(f"Wrote master_subject_inventory (.csv and .json) with {len(m_rows)} records")

# 4. Truthful coverage_matrix.csv
cov_path = nepluro_base / "coverage_matrix.csv"
with cov_path.open("r", encoding="utf-8") as f:
    rdr = csv.reader(f)
    cov_header = next(rdr)
    cov_rows = list(rdr)

extracted_keys = {(item["grade"], item["subject"]) for item in syllabus_data}

for row in cov_rows:
    grade, subj = row[0], row[1]
    key = (grade, subj)
    if key in extracted_keys:
        if subj == "Mathematics":
            row[4] = "SYLLABUS_EXTRACTED_PARTIAL"
            row[5] = "LEARNING_OUTCOMES_PARTIAL"
        else:
            row[4] = "SYLLABUS_EXTRACTED"
            row[5] = "LEARNING_OUTCOMES_EXTRACTED"
    else:
        # Not yet extracted into syllabus_structure.json
        if row[4] in ("SYLLABUS_EXTRACTED", "SYLLABUS_EXTRACTED_PARTIAL"):
            row[4] = "NOT_EXTRACTED"
            row[5] = "NOT_EXTRACTED"
            if not row[8]:
                row[8] = "Syllabus structure extraction pending from CDC 2077 document"

for target_dir in (nepluro_base, mlh_base):
    with (target_dir / "coverage_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cov_header)
        for row in cov_rows:
            w.writerow(row)
print(f"Wrote coverage_matrix.csv with {len(cov_rows)} records")

# 5. Mirror unresolved_items.md
unres_text = (nepluro_base / "unresolved_items.md").read_text(encoding="utf-8")
(mlh_base / "unresolved_items.md").write_text(unres_text, encoding="utf-8")
print("Mirrored unresolved_items.md")
