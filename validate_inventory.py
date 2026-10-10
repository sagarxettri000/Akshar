#!/usr/bin/env python3
"""
validate_inventory.py — Robust validator for NEB/CDC Grade 11–12 Curriculum Inventory.

Validates the Phase 1 master curriculum inventory files against schema rules,
detects syntax errors, data inconsistencies, invalid references, and false
verification claims using Python's standard library.

Usage:
    python validate_inventory.py [--path curriculum/neb_grade_11_12] [--strict]
"""

import argparse
import csv
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


# Schema constants
VALID_GRADES: Set[str] = {"11", "12"}

VALID_COMPULSORY_OR_OPTIONAL: Set[str] = {"compulsory", "optional"}

VALID_STATUS_LEVELS: Set[str] = {
    "DISCOVERED",
    "SOURCE_LOCATED",
    "SOURCE_INSPECTED",
    "APPLICABILITY_VERIFIED",
    "SYLLABUS_EXTRACTED",
    "NEEDS_REVIEW",
    "UNAVAILABLE",
}

VALID_COVERAGE_STATUSES: Set[str] = {
    "APPROVED",
    "PENDING",
    "REVIEW_REQUIRED",
    "NOT_EXTRACTED",
}

VALID_CONTENT_READY: Set[str] = {
    "content-ready",
    "needs-review",
    "needs-source",
}

VALID_ACCESS_STATUSES: Set[str] = {
    "PUBLIC_ACCESS",
    "PUBLIC_ONLINE",
    "OFFICIAL_PORTAL",
    "AVAILABLE",
    "ONLINE",
    "RESTRICTED",
    "UNAVAILABLE",
    "PENDING",
}

# Accepted subject categories (including documented case variations)
VALID_SUBJECT_CATEGORIES: Set[str] = {
    "Compulsory (Science stream)",
    "Compulsory (Management stream)",
    "Compulsory (All streams)",
    "Compulsory (all streams)",
    "Optional (Science stream)",
    "Optional (Management stream)",
    "Optional (Humanities stream)",
    "Optional (Health stream)",
    "Optional (Hotel/tourism stream)",
    "Optional (Management/Humanities)",
    "Compulsory (all streams, transition)",
    "Compulsory (All streams, transition)",
    "Vocational (Health stream)",
    "Vocational (Hotel/tourism stream)",
    "Vocational",
    "DISCOVERED",
}

# Expected headers for CSV files
EXPECTED_MASTER_HEADERS: List[str] = [
    "grade",
    "official_subject_name",
    "normalized_subject_name",
    "subject_code",
    "subject_category",
    "compulsory_or_optional_status",
    "optional_group_or_selection_constraints",
    "curriculum_version",
    "applicable_academic_year",
    "curriculum_source_id",
    "syllabus_source_url",
    "syllabus_verification_status",
    "notes",
    "unresolved_questions",
]

EXPECTED_SOURCES_HEADERS: List[str] = [
    "source_id",
    "document_title",
    "publishing_authority",
    "grade",
    "subject",
    "curriculum_year",
    "document_type",
    "official_url",
    "access_status",
    "verification_status",
    "notes",
]

EXPECTED_COVERAGE_HEADERS: List[str] = [
    "grade",
    "subject",
    "source_status",
    "coverage_status",
    "syllabus_structure_status",
    "learning_outcomes_status",
    "assessment_status",
    "content_ready_status",
    "outstanding_issues",
]


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


class InventoryValidator:
    """Validates NEB/CDC Grade 11-12 curriculum inventory files."""

    def __init__(self, base_dir: Path | str, strict: bool = False):
        self.base_dir = Path(base_dir)
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

        # Cached parsed data
        self.master_csv_records: List[Dict[str, str]] = []
        self.master_json_records: List[Dict[str, Any]] = []
        self.sources_records: List[Dict[str, str]] = []
        self.coverage_records: List[Dict[str, str]] = []
        self.syllabus_records: List[Dict[str, Any]] = []

    def add_error(self, message: str, detail: str = "") -> None:
        if detail:
            self.errors.append(f"{message}: {detail}")
        else:
            self.errors.append(message)

    def add_warning(self, message: str, detail: str = "") -> None:
        if detail:
            self.warnings.append(f"{message}: {detail}")
        else:
            self.warnings.append(message)

    def _read_csv(self, file_path: Path, expected_headers: List[str], file_name: str) -> Optional[List[Dict[str, str]]]:
        if not file_path.exists():
            self.add_error(f"Missing required file '{file_name}' at {file_path}")
            return None

        try:
            with file_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if headers is None:
                    self.add_error(f"{file_name}: CSV file is empty")
                    return None

                if headers != expected_headers:
                    self.add_error(
                        f"{file_name}: Header mismatch",
                        f"Expected {len(expected_headers)} columns {expected_headers}, got {len(headers)} columns {headers}",
                    )

                records: List[Dict[str, str]] = []
                for row_idx, row in enumerate(reader, start=1):
                    if len(row) != len(headers):
                        self.add_error(
                            f"{file_name} row {row_idx}: Column count mismatch",
                            f"Expected {len(headers)} columns, got {len(row)} values",
                        )
                    # Create dict with header keys
                    row_dict = {
                        headers[i] if i < len(headers) else f"col_{i}": val
                        for i, val in enumerate(row)
                    }
                    records.append(row_dict)

                return records
        except UnicodeDecodeError as e:
            self.add_error(f"{file_name}: Encoding error — must be UTF-8 ({e})")
            return None
        except Exception as e:
            self.add_error(f"{file_name}: Failed to read CSV ({e})")
            return None

    def _read_json(self, file_path: Path, file_name: str) -> Optional[Any]:
        if not file_path.exists():
            self.add_error(f"Missing required file '{file_name}' at {file_path}")
            return None

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            self.add_error(f"{file_name}: JSON syntax error", str(e))
            return None
        except UnicodeDecodeError as e:
            self.add_error(f"{file_name}: Encoding error — must be UTF-8 ({e})")
            return None
        except Exception as e:
            self.add_error(f"{file_name}: Failed to read JSON ({e})")
            return None

    def validate_master_csv(self) -> None:
        csv_path = self.base_dir / "master_subject_inventory.csv"
        records = self._read_csv(csv_path, EXPECTED_MASTER_HEADERS, "master_subject_inventory.csv")
        if records is None:
            return
        self.master_csv_records = records
        self.stats["master_csv_count"] = len(records)

        required_fields = [
            "grade",
            "official_subject_name",
            "normalized_subject_name",
            "subject_code",
            "subject_category",
            "compulsory_or_optional_status",
            "curriculum_version",
            "applicable_academic_year",
            "curriculum_source_id",
            "syllabus_source_url",
            "syllabus_verification_status",
        ]

        seen_keys: Set[Tuple[str, str]] = set()
        seen_codes: Set[Tuple[str, str]] = set()

        for idx, rec in enumerate(records, start=1):
            # Check required fields
            for rf in required_fields:
                val = rec.get(rf, "")
                if val is None or not str(val).strip():
                    self.add_error(
                        f"master_subject_inventory.csv record {idx}: Missing required field '{rf}'"
                    )

            grade = rec.get("grade", "").strip()
            if grade not in VALID_GRADES:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Invalid grade '{grade}'",
                    f"Must be one of {sorted(VALID_GRADES)}",
                )

            comp_opt = rec.get("compulsory_or_optional_status", "").strip()
            if comp_opt not in VALID_COMPULSORY_OR_OPTIONAL:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Invalid compulsory_or_optional_status '{comp_opt}'",
                    f"Must be one of {sorted(VALID_COMPULSORY_OR_OPTIONAL)}",
                )

            status = rec.get("syllabus_verification_status", "").strip()
            if status not in VALID_STATUS_LEVELS:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Invalid syllabus_verification_status '{status}'",
                    f"Must be one of {sorted(VALID_STATUS_LEVELS)}",
                )

            cat = rec.get("subject_category", "").strip()
            if cat not in VALID_SUBJECT_CATEGORIES:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Invalid subject_category '{cat}'",
                    f"Must be one of {sorted(VALID_SUBJECT_CATEGORIES)}",
                )

            # Uniqueness
            subj = rec.get("official_subject_name", "").strip()
            key = (grade, subj)
            if key in seen_keys:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Duplicate (grade, official_subject_name) {key}"
                )
            seen_keys.add(key)

            code = rec.get("subject_code", "").strip()
            code_key = (grade, code)
            if code and code_key in seen_codes:
                self.add_error(
                    f"master_subject_inventory.csv record {idx}: Duplicate (grade, subject_code) {code_key}"
                )
            if code:
                seen_codes.add(code_key)

    def validate_master_json(self) -> None:
        json_path = self.base_dir / "master_subject_inventory.json"
        data = self._read_json(json_path, "master_subject_inventory.json")
        if data is None:
            return

        if not isinstance(data, list):
            self.add_error("master_subject_inventory.json: Root element must be a JSON array")
            return

        self.master_json_records = data
        self.stats["master_json_count"] = len(data)

        seen_keys: Set[Tuple[str, str]] = set()
        for idx, rec in enumerate(data, start=1):
            if not isinstance(rec, dict):
                self.add_error(f"master_subject_inventory.json entry {idx}: Expected object/dict")
                continue

            grade = str(rec.get("grade", "")).strip()
            subj = str(rec.get("official_subject_name", "")).strip()
            if grade not in VALID_GRADES:
                self.add_error(
                    f"master_subject_inventory.json entry {idx}: Invalid grade '{grade}'"
                )

            key = (grade, subj)
            if key in seen_keys:
                self.add_error(
                    f"master_subject_inventory.json entry {idx}: Duplicate (grade, official_subject_name) {key}"
                )
            seen_keys.add(key)

            status = str(rec.get("syllabus_verification_status", "")).strip()
            if status not in VALID_STATUS_LEVELS:
                self.add_error(
                    f"master_subject_inventory.json entry {idx}: Invalid syllabus_verification_status '{status}'"
                )

    def validate_curriculum_sources_csv(self) -> None:
        csv_path = self.base_dir / "curriculum_sources.csv"
        records = self._read_csv(csv_path, EXPECTED_SOURCES_HEADERS, "curriculum_sources.csv")
        if records is None:
            return
        self.sources_records = records
        self.stats["sources_count"] = len(records)

        required_fields = [
            "source_id",
            "document_title",
            "publishing_authority",
            "grade",
            "subject",
            "curriculum_year",
            "document_type",
            "official_url",
            "access_status",
            "verification_status",
        ]

        seen_source_ids: Set[str] = set()
        for idx, rec in enumerate(records, start=1):
            for rf in required_fields:
                val = rec.get(rf, "")
                if val is None or not str(val).strip():
                    self.add_error(
                        f"curriculum_sources.csv record {idx}: Missing required field '{rf}'"
                    )

            src_id = rec.get("source_id", "").strip()
            if src_id in seen_source_ids:
                self.add_error(
                    f"curriculum_sources.csv record {idx}: Duplicate source_id '{src_id}'"
                )
            seen_source_ids.add(src_id)

            grade = rec.get("grade", "").strip()
            if grade not in VALID_GRADES:
                self.add_error(
                    f"curriculum_sources.csv record {idx}: Invalid grade '{grade}'"
                )

            verif = rec.get("verification_status", "").strip()
            if verif not in VALID_STATUS_LEVELS:
                self.add_error(
                    f"curriculum_sources.csv record {idx}: Invalid verification_status '{verif}'",
                    f"Must be one of {sorted(VALID_STATUS_LEVELS)}",
                )

            access = rec.get("access_status", "").strip()
            if access not in VALID_ACCESS_STATUSES:
                self.add_error(
                    f"curriculum_sources.csv record {idx}: Invalid access_status '{access}'",
                    f"Must be one of {sorted(VALID_ACCESS_STATUSES)}",
                )

    def validate_coverage_matrix_csv(self) -> None:
        csv_path = self.base_dir / "coverage_matrix.csv"
        records = self._read_csv(csv_path, EXPECTED_COVERAGE_HEADERS, "coverage_matrix.csv")
        if records is None:
            return
        self.coverage_records = records
        self.stats["coverage_count"] = len(records)

        seen_keys: Set[Tuple[str, str]] = set()
        for idx, rec in enumerate(records, start=1):
            grade = rec.get("grade", "").strip()
            subj = rec.get("subject", "").strip()
            key = (grade, subj)

            if key in seen_keys:
                self.add_error(
                    f"coverage_matrix.csv record {idx}: Duplicate (grade, subject) {key}"
                )
            seen_keys.add(key)

            if grade not in VALID_GRADES:
                self.add_error(f"coverage_matrix.csv record {idx}: Invalid grade '{grade}'")

            src_status = rec.get("source_status", "").strip()
            if src_status not in VALID_STATUS_LEVELS:
                self.add_error(
                    f"coverage_matrix.csv record {idx}: Invalid source_status '{src_status}'"
                )

            cov_status = rec.get("coverage_status", "").strip()
            if cov_status not in VALID_COVERAGE_STATUSES:
                self.add_error(
                    f"coverage_matrix.csv record {idx}: Invalid coverage_status '{cov_status}'"
                )

            ready_status = rec.get("content_ready_status", "").strip()
            if ready_status not in VALID_CONTENT_READY:
                self.add_error(
                    f"coverage_matrix.csv record {idx}: Invalid content_ready_status '{ready_status}'"
                )

    def validate_syllabus_structure_json(self) -> None:
        json_path = self.base_dir / "syllabus_structure.json"
        if not json_path.exists():
            self.add_warning(
                f"syllabus_structure.json does not exist in {self.base_dir} (extraction may be pending)"
            )
            return

        data = self._read_json(json_path, "syllabus_structure.json")
        if data is None:
            return

        if not isinstance(data, list):
            self.add_error("syllabus_structure.json: Root element must be a JSON array")
            return

        self.syllabus_records = data
        self.stats["syllabus_count"] = len(data)

        seen_keys: Set[Tuple[str, str]] = set()
        for idx, entry in enumerate(data, start=1):
            if not isinstance(entry, dict):
                self.add_error(f"syllabus_structure.json entry {idx}: Must be an object")
                continue

            grade = str(entry.get("grade", "")).strip()
            subj = str(entry.get("subject", "")).strip()

            if not grade or grade not in VALID_GRADES:
                self.add_error(f"syllabus_structure.json entry {idx}: Invalid grade '{grade}'")
            if not subj:
                self.add_error(f"syllabus_structure.json entry {idx}: Missing 'subject' field")

            key = (grade, subj)
            if key in seen_keys:
                self.add_error(
                    f"syllabus_structure.json entry {idx}: Duplicate entry for {key}"
                )
            seen_keys.add(key)

            structure = entry.get("syllabus_structure")
            if not isinstance(structure, dict):
                self.add_error(
                    f"syllabus_structure.json entry {idx} ({key}): Missing or invalid 'syllabus_structure' object"
                )
                continue

            units = structure.get("units")
            if not isinstance(units, list) or len(units) == 0:
                self.add_warning(
                    f"syllabus_structure.json entry {idx} ({key}): 'units' list is empty"
                )
            else:
                for u_idx, unit in enumerate(units):
                    if not isinstance(unit, dict) or "unit_number" not in unit or "unit_title" not in unit:
                        self.add_error(
                            f"syllabus_structure.json entry {idx} ({key}) unit {u_idx}: Must have 'unit_number' and 'unit_title'"
                        )

            assessment = structure.get("assessment_components")
            if not isinstance(assessment, dict):
                self.add_warning(
                    f"syllabus_structure.json entry {idx} ({key}): 'assessment_components' should be an object"
                )

    def validate_unresolved_items_md(self) -> None:
        md_path = self.base_dir / "unresolved_items.md"
        if not md_path.exists():
            self.add_error(f"Missing unresolved_items.md at {md_path}")
            return
        if md_path.stat().st_size == 0:
            self.add_error(f"unresolved_items.md is empty")

    def validate_cross_file_consistency(self) -> None:
        """Cross-checks consistency between CSV and JSON files, and foreign keys."""
        # 1. master CSV vs master JSON
        if self.master_csv_records and self.master_json_records:
            csv_map = {
                (r.get("grade", "").strip(), r.get("official_subject_name", "").strip()): r
                for r in self.master_csv_records
            }
            json_map = {
                (str(r.get("grade", "")).strip(), str(r.get("official_subject_name", "")).strip()): r
                for r in self.master_json_records
            }

            csv_keys = set(csv_map.keys())
            json_keys = set(json_map.keys())

            missing_in_json = csv_keys - json_keys
            if missing_in_json:
                self.add_error(
                    "master_subject_inventory.json missing records present in CSV",
                    str(sorted(missing_in_json)),
                )

            missing_in_csv = json_keys - csv_keys
            if missing_in_csv:
                self.add_error(
                    "master_subject_inventory.csv missing records present in JSON",
                    str(sorted(missing_in_csv)),
                )

            # Compare common fields
            common_keys = csv_keys & json_keys
            fields_to_compare = [
                "subject_code",
                "subject_category",
                "compulsory_or_optional_status",
                "curriculum_version",
                "applicable_academic_year",
                "curriculum_source_id",
                "syllabus_verification_status",
            ]
            for key in common_keys:
                c_rec = csv_map[key]
                j_rec = json_map[key]
                for fld in fields_to_compare:
                    c_val = str(c_rec.get(fld, "")).strip()
                    j_val = str(j_rec.get(fld, "")).strip()
                    if c_val != j_val:
                        self.add_error(
                            f"CSV/JSON mismatch for {key} in '{fld}'",
                            f"CSV='{c_val}', JSON='{j_val}'",
                        )

        # 2. Foreign key: master inventory curriculum_source_id -> curriculum_sources source_id
        if self.master_csv_records and self.sources_records:
            valid_source_ids = {r.get("source_id", "").strip() for r in self.sources_records}
            for idx, r in enumerate(self.master_csv_records, start=1):
                src_id = r.get("curriculum_source_id", "").strip()
                if src_id and src_id not in valid_source_ids:
                    self.add_error(
                        f"master_subject_inventory.csv record {idx}: Invalid curriculum_source_id '{src_id}'",
                        "Source ID does not exist in curriculum_sources.csv",
                    )

        # 3. Foreign key: coverage_matrix (grade, subject) -> master_subject_inventory (grade, official_subject_name)
        if self.coverage_records and self.master_csv_records:
            master_keys = {
                (r.get("grade", "").strip(), r.get("official_subject_name", "").strip())
                for r in self.master_csv_records
            }
            for idx, r in enumerate(self.coverage_records, start=1):
                cov_key = (r.get("grade", "").strip(), r.get("subject", "").strip())
                if cov_key not in master_keys:
                    self.add_error(
                        f"coverage_matrix.csv record {idx}: Subject {cov_key} not found in master_subject_inventory.csv"
                    )

        # 4. Foreign key: syllabus_structure (grade, subject) -> master_subject_inventory (grade, official_subject_name)
        if self.syllabus_records and self.master_csv_records:
            master_keys = {
                (r.get("grade", "").strip(), r.get("official_subject_name", "").strip())
                for r in self.master_csv_records
            }
            for idx, r in enumerate(self.syllabus_records, start=1):
                syl_key = (str(r.get("grade", "")).strip(), str(r.get("subject", "")).strip())
                if syl_key not in master_keys:
                    self.add_error(
                        f"syllabus_structure.json entry {idx}: Subject {syl_key} not found in master_subject_inventory.csv"
                    )

    def validate_verification_claims(self) -> None:
        """Ensures statuses do not falsely claim verification without backing evidence."""
        syllabus_keys = {
            (str(r.get("grade", "")).strip(), str(r.get("subject", "")).strip())
            for r in self.syllabus_records
        }

        # Check master inventory status claims
        for idx, r in enumerate(self.master_csv_records, start=1):
            grade = r.get("grade", "").strip()
            subj = r.get("official_subject_name", "").strip()
            key = (grade, subj)
            status = r.get("syllabus_verification_status", "").strip()
            url = r.get("syllabus_source_url", "").strip()

            if status == "SYLLABUS_EXTRACTED":
                if key not in syllabus_keys:
                    self.add_error(
                        f"False verification claim for {key}: Marked SYLLABUS_EXTRACTED in master inventory but missing from syllabus_structure.json"
                    )

            if status in {"SOURCE_INSPECTED", "APPLICABILITY_VERIFIED", "SYLLABUS_EXTRACTED"}:
                if not url or url == "UNAVAILABLE":
                    self.add_error(
                        f"False verification claim for {key}: Marked {status} but syllabus_source_url is empty or UNAVAILABLE"
                    )

        # Check coverage matrix status claims
        for idx, r in enumerate(self.coverage_records, start=1):
            grade = r.get("grade", "").strip()
            subj = r.get("subject", "").strip()
            key = (grade, subj)
            syl_status = r.get("syllabus_structure_status", "").strip()
            cov_status = r.get("coverage_status", "").strip()
            src_status = r.get("source_status", "").strip()

            if syl_status in {"SYLLABUS_EXTRACTED", "SYLLABUS_EXTRACTED_PARTIAL"} and key not in syllabus_keys:
                self.add_error(
                    f"False coverage claim for {key}: syllabus_structure_status is {syl_status} but not found in syllabus_structure.json"
                )

            if cov_status == "APPROVED" and src_status in {"DISCOVERED", "UNAVAILABLE"}:
                self.add_error(
                    f"Contradictory status for {key}: coverage_status is APPROVED but source_status is {src_status}"
                )

        # Check curriculum sources access & verification consistency
        for idx, r in enumerate(self.sources_records, start=1):
            src_id = r.get("source_id", "").strip()
            verif = r.get("verification_status", "").strip()
            access = r.get("access_status", "").strip()
            url = r.get("official_url", "").strip()

            if verif in {"SOURCE_INSPECTED", "APPLICABILITY_VERIFIED", "SYLLABUS_EXTRACTED"}:
                if access == "UNAVAILABLE":
                    self.add_error(
                        f"Contradictory source for {src_id}: verification_status is {verif} but access_status is UNAVAILABLE"
                    )
                if not url or url == "UNAVAILABLE":
                    self.add_error(
                        f"Contradictory source for {src_id}: verification_status is {verif} but official_url is empty or UNAVAILABLE"
                    )

    def validate(self) -> ValidationResult:
        """Runs the complete validation pipeline."""
        self.errors.clear()
        self.warnings.clear()
        self.stats.clear()

        self.validate_master_csv()
        self.validate_master_json()
        self.validate_curriculum_sources_csv()
        self.validate_coverage_matrix_csv()
        self.validate_syllabus_structure_json()
        self.validate_unresolved_items_md()
        self.validate_cross_file_consistency()
        self.validate_verification_claims()

        is_valid = len(self.errors) == 0
        if self.strict and len(self.warnings) > 0:
            is_valid = False

        return ValidationResult(
            is_valid=is_valid,
            errors=list(self.errors),
            warnings=list(self.warnings),
            stats=dict(self.stats),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NEB Grade 11-12 Curriculum Inventory")
    parser.add_argument(
        "--path",
        type=str,
        default="curriculum/neb_grade_11_12",
        help="Path to inventory directory (default: curriculum/neb_grade_11_12)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    validator = InventoryValidator(args.path, strict=args.strict)
    result = validator.validate()

    if args.json:
        output = {
            "valid": result.is_valid,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "errors": result.errors,
            "warnings": result.warnings,
            "stats": result.stats,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0 if result.is_valid else 1

    print("=" * 65)
    print(f"NEB/CDC Grade 11-12 Curriculum Inventory Validation")
    print(f"Target Directory: {validator.base_dir}")
    print("=" * 65)

    if result.stats:
        print("Inventory Records Summary:")
        for k, v in sorted(result.stats.items()):
            print(f"  - {k}: {v}")
        print("-" * 65)

    if result.warnings:
        print(f"WARNINGS ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  [WARN] {w}")
        print("-" * 65)

    if result.errors:
        print(f"VALIDATION FAILED: {len(result.errors)} issue(s) found:")
        for err in result.errors:
            print(f"  [FAIL] {err}")
        print("=" * 65)
        return 1

    print("VALIDATION PASSED: All curriculum files and integrity checks successful.")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
