import csv
from pathlib import Path

source_csv = Path("../Nepluro/curriculum/neb_grade_11_12/curriculum_sources.csv")
with source_csv.open("r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    raw_rows = list(reader)

print(f"Header ({len(header)}): {header}")
print(f"Raw rows: {len(raw_rows)}, first row len: {len(raw_rows[0])}")

fixed_rows = []
for i, r in enumerate(raw_rows):
    if len(r) == 10:
        # r[0..7] are source_id .. official_url
        # r[8] was placed where access_status should be, but it holds the verification_status (e.g. SOURCE_INSPECTED)
        # r[9] was placed where verification_status should be, but it holds the notes
        src_id, doc_title, pub_auth, grade, subject, curr_yr, doc_type, off_url, verif_status, notes = r
        access_status = "PUBLIC_ACCESS"
        fixed_rows.append([src_id, doc_title, pub_auth, grade, subject, curr_yr, doc_type, off_url, access_status, verif_status, notes])
    elif len(r) == 11:
        fixed_rows.append(r)
    else:
        print(f"Unexpected row {i} len {len(r)}: {r}")

print(f"Fixed {len(fixed_rows)} rows. Sample fixed row 0:")
print(fixed_rows[0])
