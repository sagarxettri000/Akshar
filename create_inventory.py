import csv
from pathlib import Path

rows = [
    # Grade 11 compulsory (Science stream)
    ["11", "Physics", "Physics", "PHY-11", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 11", "2077", "2077", "CDC_PHYS_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Lesson covers Newton's Laws of Motion and Motion in a Straight Line; Devanagari-ready content prepared", ""],
    ["11", "Chemistry", "Chemistry", "CHEM-11", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 11", "2077", "2077", "CDC_CHEM_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Lesson covers Acids/Bases and Atomic Structure; Nepali terminology validated", ""],
    ["11", "Biology", "Biology", "BIO-11", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 11", "2077", "2077", "CDC_BIO_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Lesson covers Photosynthesis (Grade 12); Grade 11 syllabus partially represented in current lesson set", ""],
    ["11", "Mathematics", "Mathematics", "MATH-11", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 11", "2077", "2077", "CDC_MATH_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_LOCATED", "Syllabus structure extraction in progress; Algebra, Geometry, Trigonometry components", ""],
    ["11", "English", "English", "ENG-11", "Compulsory (all streams)", "compulsory", "Compulsory across all streams Grade 11", "2077", "2077", "CDC_ENG_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "English language and literature; bilingual support (en/ne) implemented", ""],
    ["11", "Nepali", "Nepali", "NEP-11", "Compulsory (all streams)", "compulsory", "Compulsory across all streams Grade 11", "2077", "2077", "CDC_NEP_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Nepali language and literature; Devanagari support implemented", ""],

    # Grade 11 optional / other streams
    ["11", "Environmental Science", "Environmental Science", "EVS-11", "Optional (Management/Humanities)", "optional", "Available to Management and Humanities streams Grade 11", "2077", "2077", "CDC_EVS_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Not yet represented in lesson set; requires source verification", ""],
    ["11", "Computer Science", "Computer Science", "CS-11", "Optional (Science stream)", "optional", "Available as optional subject Grade 11 Science stream", "2077", "2077", "CDC_CS_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Not yet represented in lesson set; requires source verification", ""],

    # Grade 11 Management stream
    ["11", "Accounting", "Accounting", "ACC-11", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 11", "2077", "2077", "CDC_ACC_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects; not yet represented in lesson set", ""],
    ["11", "Economics", "Economics", "ECO-11", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 11", "2077", "2077", "CDC_ECO_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects; not yet represented in lesson set", ""],
    ["11", "Business Studies", "Business Studies", "BUS-11", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 11", "2077", "2077", "CDC_BUS_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects; not yet represented in lesson set", ""],
    ["11", "Education", "Education", "EDU-11", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 11", "2077", "2077", "CDC_EDU_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects; not yet represented in lesson set", ""],
    ["11", "Political Science", "Political Science", "PSC-11", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 11", "2077", "2077", "CDC_PSC_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects; not yet represented in lesson set", ""],
    ["11", "Sociology", "Sociology", "SOC-11", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 11", "2077", "2077", "CDC_SOC_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects; not yet represented in lesson set", ""],
    ["11", "Advanced Mathematics", "Advanced Mathematics", "ADV-MATH-11", "Optional (Science stream)", "optional", "Available as optional subject top-up Grade 11 Science (for Math stream)", "2077", "2077", "CDC_ADV_MATH_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Distinct from core Mathematics; represents higher-level content", ""],
    ["11", "Intelligent Study", "Intelligent Study", "INT-11", "Compulsory (all streams, transition)", "compulsory", "Compulsory in 2077-78 as replacement for old General Marks system", "2077", "2077", "CDC_INT_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "New curriculum element; transitional status", ""],
    ["11", "Nursing Fundamentals", "Nursing Fundamentals", "NF-11", "Vocational (Health stream)", "optional", "Available as vocational subject Grade 11 Health Science pathway", "2077", "2077", "CDC_NF_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Vocational/Health stream subject; not in current lesson set", ""],
    ["11", "Hotel Management Basics", "Hotel Management Basics", "HMB-11", "Vocational (Hotel/tourism stream)", "optional", "Available as vocational subject Grade 11 Hotel Management pathway", "2077", "2077", "CDC_HMB_11", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Vocational subject; not in current lesson set", ""],

    # Grade 12 compulsory (Science stream)
    ["12", "Physics", "Physics", "PHY-12", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 12", "2077", "2077", "CDC_PHYS_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Lesson covers Derivatives; advanced Physics topics partially represented", ""],
    ["12", "Chemistry", "Chemistry", "CHEM-12", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 12", "2077", "2077", "CDC_CHEM_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Grade 12 syllabus expansion from Grade 11 foundations; current lesson set limited", ""],
    ["12", "Biology", "Biology", "BIO-12", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 12", "2077", "2077", "CDC_BIO_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Lesson covers Cell Division; Grade 12 syllabus builds on Grade 11", ""],
    ["12", "Mathematics", "Mathematics", "MATH-12", "Compulsory (Science stream)", "compulsory", "Required for Science stream Grade 12", "2077", "2077", "CDC_MATH_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_LOCATED", "Syllabus structure extraction in progress; Calculus, Vectors, Statistics components", ""],
    ["12", "English", "English", "ENG-12", "Compulsory (all streams)", "compulsory", "Compulsory across all streams Grade 12", "2077", "2077", "CDC_ENG_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "English language and literature; bilingual support (en/ne) implemented", ""],
    ["12", "Nepali", "Nepali", "NEP-12", "Compulsory (all streams)", "compulsory", "Compulsory across all streams Grade 12", "2077", "2077", "CDC_NEP_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "SOURCE_INSPECTED", "Nepali language and literature; Devanagari support implemented", ""],

    # Grade 12 optional / other streams
    ["12", "Environmental Science", "Environmental Science", "EVS-12", "Optional (Management/Humanities)", "optional", "Available to Management and Humanities streams Grade 12", "2077", "2077", "CDC_EVS_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Not yet represented in lesson set; requires source verification", ""],
    ["12", "Computer Science", "Computer Science", "CS-12", "Optional (Science stream)", "optional", "Available as optional subject Grade 12 Science stream", "2077", "2077", "CDC_CS_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Not yet represented in lesson set; requires source verification", ""],

    # Grade 12 Management stream
    ["12", "Accounting", "Accounting", "ACC-12", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 12", "2077", "2077", "CDC_ACC_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Economics", "Economics", "ECO-12", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 12", "2077", "2077", "CDC_ECO_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Business Studies", "Business Studies", "BUS-12", "Compulsory (Management stream)", "compulsory", "Required for Management stream Grade 12", "2077", "2077", "CDC_BUS_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Management stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Education", "Education", "EDU-12", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 12", "2077", "2077", "CDC_EDU_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Political Science", "Political Science", "PSC-12", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 12", "2077", "2077", "CDC_PSC_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Sociology", "Sociology", "SOC-12", "Optional (Humanities stream)", "optional", "Available to Humanities stream Grade 12", "2077", "2077", "CDC_SOC_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Humanities stream subjects Grade 12; not yet represented in lesson set", ""],
    ["12", "Advanced Mathematics", "Advanced Mathematics", "ADV-MATH-12", "Optional (Science stream)", "optional", "Available as optional subject top-up Grade 12 Science (for Math stream)", "2077", "2077", "CDC_ADV_MATH_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Distinct from core Mathematics Grade 12; represents higher-level content", ""],
    ["12", "Intelligent Study", "Intelligent Study", "INT-12", "Compulsory (all streams, transition)", "compulsory", "Compulsory in 2077-78 as replacement for old General Marks system", "2077", "2077", "CDC_INT_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "New curriculum element; transitional status", ""],
    ["12", "Nursing Fundamentals", "Nursing Fundamentals", "NF-12", "Vocational (Health stream)", "optional", "Available as vocational subject Grade 12 Health Science pathway", "2077", "2077", "CDC_NF_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Vocational/Health stream subject; not in current lesson set", ""],
    ["12", "Hotel Management Basics", "Hotel Management Basics", "HMB-12", "Vocational (Hotel/tourism stream)", "optional", "Available as vocational subject Grade 12 Hotel Management pathway", "2077", "2077", "CDC_HMB_12", "https://moecdc.gov.np/content/160/secondary-education-curriculum--2077-grade-11-12-part/", "DISCOVERED", "Vocational subject; not in current lesson set", ""],
]

# Write CSV
with Path('curriculum/neb_grade_11_12/master_subject_inventory.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['grade', 'official_subject_name', 'normalized_subject_name', 'subject_code', 'subject_category', 'compulsory_or_optional_status', 'optional_group_or_selection_constraints', 'curriculum_version', 'applicable_academic_year', 'curriculum_source_id', 'syllabus_source_url', 'syllabus_verification_status', 'notes', 'unresolved_questions'])
    for row in rows:
        writer.writerow(row)

print(f'Wrote master_subject_inventory.csv with {len(rows)} records')

# Write JSON
import json
inventory = []
for row in rows:
    entry = {
        "grade": row[0],
        "official_subject_name": row[1],
        "normalized_subject_name": row[2],
        "subject_code": row[3],
        "subject_category": row[4],
        "compulsory_or_optional_status": row[5],
        "optional_group_or_selection_constraints": row[6],
        "curriculum_version": row[7],
        "applicable_academic_year": row[8],
        "curriculum_source_id": row[9],
        "syllabus_source_url": row[10],
        "syllabus_verification_status": row[11],
        "notes": row[12],
        "unresolved_questions": row[13],
    }
    inventory.append(entry)

with Path('curriculum/neb_grade_11_12/master_subject_inventory.json').open('w', encoding='utf-8') as f:
    json.dump(inventory, f, ensure_ascii=False, indent=2)

print(f'Wrote master_subject_inventory.json with {len(inventory)} records')
