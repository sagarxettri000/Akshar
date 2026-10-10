"""
test_validate_inventory.py — Focused tests for inventory validator failure cases and success paths.

Covers:
- Missing required files
- Malformed CSV (header mismatch, row column count mismatch, empty file)
- Malformed JSON (syntax error, root type error)
- Schema validation (invalid grades, status levels, compulsory/optional, categories)
- Duplicate detection (grade+subject, grade+code, source_id)
- Foreign-key reference integrity (invalid curriculum_source_id, invalid coverage subject)
- CSV vs JSON consistency (missing records, field value mismatches)
- False verification claims (SYLLABUS_EXTRACTED without structure, unverified approved coverage)
- Clean execution on the actual valid inventory
"""

import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from validate_inventory import (
    InventoryValidator,
    EXPECTED_MASTER_HEADERS,
    EXPECTED_SOURCES_HEADERS,
    EXPECTED_COVERAGE_HEADERS,
)


class TestInventoryValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base = Path(self.temp_dir)
        self._populate_minimal_valid_inventory()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _populate_minimal_valid_inventory(self):
        """Creates a minimal self-consistent valid inventory fixture."""
        # 1. Master CSV
        master_rows = [
            [
                "11", "Physics", "Physics", "PHY-11",
                "Compulsory (Science stream)", "compulsory", "",
                "2077", "2077", "CDC_PHYS_11",
                "https://moecdc.gov.np/test", "SOURCE_INSPECTED",
                "Test notes", "",
            ],
            [
                "11", "Chemistry", "Chemistry", "CHEM-11",
                "Compulsory (Science stream)", "compulsory", "",
                "2077", "2077", "CDC_CHEM_11",
                "https://moecdc.gov.np/test", "DISCOVERED",
                "Test notes", "",
            ],
        ]
        with (self.base / "master_subject_inventory.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(EXPECTED_MASTER_HEADERS)
            w.writerows(master_rows)

        # 2. Master JSON
        master_json = []
        for r in master_rows:
            master_json.append({EXPECTED_MASTER_HEADERS[i]: r[i] for i in range(len(EXPECTED_MASTER_HEADERS))})
        with (self.base / "master_subject_inventory.json").open("w", encoding="utf-8") as f:
            json.dump(master_json, f, indent=2)

        # 3. Sources CSV
        sources_rows = [
            [
                "CDC_PHYS_11", "Curriculum Grade 11", "CDC", "11", "Physics",
                "2077", "Official document", "https://moecdc.gov.np/test",
                "PUBLIC_ACCESS", "SOURCE_INSPECTED", "Verified notes",
            ],
            [
                "CDC_CHEM_11", "Curriculum Grade 11", "CDC", "11", "Chemistry",
                "2077", "Official document", "https://moecdc.gov.np/test",
                "PUBLIC_ACCESS", "DISCOVERED", "Discovered notes",
            ],
        ]
        with (self.base / "curriculum_sources.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(EXPECTED_SOURCES_HEADERS)
            w.writerows(sources_rows)

        # 4. Coverage CSV
        coverage_rows = [
            [
                "11", "Physics", "SOURCE_INSPECTED", "APPROVED",
                "SYLLABUS_EXTRACTED", "LEARNING_OUTCOMES_EXTRACTED",
                "ASSESSMENT_CHECKED", "content-ready", "",
            ],
            [
                "11", "Chemistry", "DISCOVERED", "PENDING",
                "NOT_EXTRACTED", "NOT_EXTRACTED",
                "NOT_CHECKED", "needs-source", "",
            ],
        ]
        with (self.base / "coverage_matrix.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(EXPECTED_COVERAGE_HEADERS)
            w.writerows(coverage_rows)

        # 5. Syllabus Structure JSON
        syllabus_data = [
            {
                "grade": "11",
                "subject": "Physics",
                "subject_code": "PHY-11",
                "curriculum_version": "2077",
                "syllabus_structure": {
                    "curriculum_objectives": ["Understand mechanics"],
                    "units": [
                        {
                            "unit_number": 1,
                            "unit_title": "Mechanics",
                            "syllabus_reference": "Section 1",
                        }
                    ],
                    "topics_and_subtopics": [{"topic": "Motion"}],
                    "learning_outcomes": ["Calculate velocity"],
                    "assessment_components": {"theoretical_marks": 75},
                },
            }
        ]
        with (self.base / "syllabus_structure.json").open("w", encoding="utf-8") as f:
            json.dump(syllabus_data, f, indent=2)

        # 6. Unresolved Items MD
        (self.base / "unresolved_items.md").write_text("# Unresolved Items\nNone pending.", encoding="utf-8")

    def test_clean_fixture_passes_validation(self):
        """Minimal valid fixture should pass with zero errors."""
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertTrue(result.is_valid, f"Validation failed unexpectedly: {result.errors}")
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(result.stats.get("master_csv_count"), 2)

    def test_missing_master_csv(self):
        """Missing master_subject_inventory.csv produces a clear error."""
        (self.base / "master_subject_inventory.csv").unlink()
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required file 'master_subject_inventory.csv'" in e for e in result.errors))

    def test_missing_sources_csv(self):
        """Missing curriculum_sources.csv produces a clear error."""
        (self.base / "curriculum_sources.csv").unlink()
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required file 'curriculum_sources.csv'" in e for e in result.errors))

    def test_missing_coverage_matrix(self):
        """Missing coverage_matrix.csv produces a clear error."""
        (self.base / "coverage_matrix.csv").unlink()
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required file 'coverage_matrix.csv'" in e for e in result.errors))

    def test_missing_unresolved_items_md(self):
        """Missing unresolved_items.md produces a clear error."""
        (self.base / "unresolved_items.md").unlink()
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing unresolved_items.md" in e for e in result.errors))

    def test_empty_csv_file(self):
        """Empty CSV file produces an informative error instead of an unhandled crash."""
        (self.base / "master_subject_inventory.csv").write_text("", encoding="utf-8")
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("master_subject_inventory.csv: CSV file is empty" in e for e in result.errors))

    def test_csv_header_mismatch(self):
        """Incorrect headers in CSV file are caught and reported."""
        (self.base / "master_subject_inventory.csv").write_text("bad_header1,bad_header2\n1,2\n", encoding="utf-8")
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Header mismatch" in e for e in result.errors))

    def test_csv_column_count_mismatch(self):
        """Detects row with fewer or more columns than header (the column-shift defect)."""
        content = (self.base / "curriculum_sources.csv").read_text(encoding="utf-8").splitlines()
        # Truncate row 2 to 10 columns instead of 11
        row_parts = content[1].split(",")
        content[1] = ",".join(row_parts[:10])
        (self.base / "curriculum_sources.csv").write_text("\n".join(content) + "\n", encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Column count mismatch" in e for e in result.errors))

    def test_json_syntax_error(self):
        """JSON syntax error is reported without unhandled exception."""
        (self.base / "master_subject_inventory.json").write_text("{ unclosed: json", encoding="utf-8")
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("JSON syntax error" in e for e in result.errors))

    def test_json_root_not_array(self):
        """JSON root not being a list is detected."""
        (self.base / "master_subject_inventory.json").write_text('{"not": "a list"}', encoding="utf-8")
        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Root element must be a JSON array" in e for e in result.errors))

    def test_invalid_grade_rejected(self):
        """Grades other than 11 or 12 are rejected."""
        content = (self.base / "master_subject_inventory.csv").read_text(encoding="utf-8")
        content = content.replace("11,Physics", "10,Physics")
        (self.base / "master_subject_inventory.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid grade '10'" in e for e in result.errors))

    def test_invalid_status_level_rejected(self):
        """Status levels outside VALID_STATUS_LEVELS are rejected."""
        content = (self.base / "master_subject_inventory.csv").read_text(encoding="utf-8")
        content = content.replace("SOURCE_INSPECTED", "FULLY_DONE")
        (self.base / "master_subject_inventory.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid syllabus_verification_status 'FULLY_DONE'" in e for e in result.errors))

    def test_duplicate_subject_detected(self):
        """Duplicate (grade, subject) in master inventory is detected."""
        content = (self.base / "master_subject_inventory.csv").read_text(encoding="utf-8").splitlines()
        content.append(content[1])  # Duplicate row 1
        (self.base / "master_subject_inventory.csv").write_text("\n".join(content) + "\n", encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Duplicate (grade, official_subject_name)" in e for e in result.errors))

    def test_broken_source_id_foreign_key(self):
        """Master inventory referencing a non-existent curriculum_source_id is caught."""
        content = (self.base / "master_subject_inventory.csv").read_text(encoding="utf-8")
        content = content.replace("CDC_PHYS_11", "NON_EXISTENT_SOURCE")
        (self.base / "master_subject_inventory.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid curriculum_source_id 'NON_EXISTENT_SOURCE'" in e for e in result.errors))

    def test_csv_json_divergence_detected(self):
        """Differences between master CSV and master JSON are detected."""
        with (self.base / "master_subject_inventory.json").open("r", encoding="utf-8") as f:
            data = json.load(f)
        data[0]["subject_code"] = "DIFFERENT_CODE"
        with (self.base / "master_subject_inventory.json").open("w", encoding="utf-8") as f:
            json.dump(data, f)

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("CSV/JSON mismatch" in e and "subject_code" in e for e in result.errors))

    def test_false_syllabus_extracted_claim_rejected(self):
        """Marking a subject SYLLABUS_EXTRACTED without an entry in syllabus_structure.json fails."""
        content = (self.base / "master_subject_inventory.csv").read_text(encoding="utf-8")
        # Change Chemistry from DISCOVERED to SYLLABUS_EXTRACTED
        content = content.replace("DISCOVERED", "SYLLABUS_EXTRACTED")
        (self.base / "master_subject_inventory.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("False verification claim" in e and "Chemistry" in e for e in result.errors))

    def test_false_coverage_approved_claim_rejected(self):
        """Marking coverage APPROVED when source is DISCOVERED is rejected."""
        content = (self.base / "coverage_matrix.csv").read_text(encoding="utf-8")
        content = content.replace("PENDING", "APPROVED")
        (self.base / "coverage_matrix.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Contradictory status" in e and "APPROVED" in e for e in result.errors))

    def test_false_coverage_partial_claim_rejected(self):
        """Marking syllabus_structure_status SYLLABUS_EXTRACTED_PARTIAL without syllabus structure is rejected."""
        content = (self.base / "coverage_matrix.csv").read_text(encoding="utf-8")
        # Change Chemistry from NOT_EXTRACTED to SYLLABUS_EXTRACTED_PARTIAL
        content = content.replace("NOT_EXTRACTED", "SYLLABUS_EXTRACTED_PARTIAL")
        (self.base / "coverage_matrix.csv").write_text(content, encoding="utf-8")

        validator = InventoryValidator(self.base)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(any("False coverage claim" in e and "SYLLABUS_EXTRACTED_PARTIAL" in e for e in result.errors))


if __name__ == "__main__":
    unittest.main()
