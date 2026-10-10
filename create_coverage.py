import csv
from pathlib import Path

rows = [
    # Grade 11 records
    ["11", "Physics", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["11", "Chemistry", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["11", "Biology", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "needs-review", "Needs Grade 12 content mapping"],
    ["11", "Mathematics", "SOURCE_LOCATED", "REVIEW_REQUIRED", "SYLLABUS_EXTRACTED_PARTIAL", "LEARNING_OUTCOMES_PARTIAL", "ASSESSMENT_CHECKED", "needs-review", ""],
    ["11", "English", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["11", "Nepali", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", "Devanagari validation needed"],
    ["11", "Environmental Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Computer Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Accounting", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Economics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Business Studies", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Education", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Political Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Sociology", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Advanced Mathematics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Intelligent Study", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", "Transitional status 2077-78"],
    ["11", "Nursing Fundamentals", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["11", "Hotel Management Basics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],

    # Grade 12 records
    ["12", "Physics", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["12", "Chemistry", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["12", "Biology", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["12", "Mathematics", "SOURCE_LOCATED", "REVIEW_REQUIRED", "SYLLABUS_EXTRACTED_PARTIAL", "LEARNING_OUTCOMES_PARTIAL", "ASSESSMENT_CHECKED", "needs-review", ""],
    ["12", "English", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["12", "Nepali", "SOURCE_INSPECTED", "APPROVED", "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED", "ASSESSMENT_CHECKED", "content-ready", ""],
    ["12", "Environmental Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Computer Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Accounting", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Economics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Business Studies", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Education", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Political Science", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Sociology", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Advanced Mathematics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Intelligent Study", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", "Transitional status 2077-78"],
    ["12", "Nursing Fundamentals", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
    ["12", "Hotel Management Basics", "DISCOVERED", "PENDING", "NOT_EXTRACTED", "NOT_EXTRACTED", "NOT_CHECKED", "needs-source", ""],
]

with Path('curriculum/neb_grade_11_12/coverage_matrix.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'grade', 'subject', 'source_status', 'coverage_status',
        'syllabus_structure_status', 'learning_outcomes_status',
        'assessment_status', 'content_ready_status', 'outstanding_issues'
    ])
    for row in rows:
        writer.writerow(row)

print(f'Wrote coverage_matrix.csv with {len(rows)} records')
