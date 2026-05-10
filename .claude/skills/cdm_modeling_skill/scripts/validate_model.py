#!/usr/bin/env python3
"""
validate_model.py - CDM 生成产物校验工具
========================================
检查 output/cdm-modeling 下的 SQL 和 docs 产物是否满足基本门禁。
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict


REQUIRED_DOCS = [
    "dim_list.csv",
    "dwd_list.csv",
    "field_mapping.csv",
    "dependency.csv",
    "model_design.md",
    "validation_report.md",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_output_dir(output_dir: Path) -> tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    docs_dir = output_dir / "docs"
    ddl_dir = output_dir / "ddl"
    etl_dir = output_dir / "etl"

    for directory in [docs_dir, ddl_dir, etl_dir]:
        if not directory.exists():
            errors.append(f"missing directory: {directory}")

    for filename in REQUIRED_DOCS:
        path = docs_dir / filename
        if not path.exists():
            errors.append(f"missing docs file: {path}")

    dim_rows = read_csv(docs_dir / "dim_list.csv")
    dwd_rows = read_csv(docs_dir / "dwd_list.csv")
    field_rows = read_csv(docs_dir / "field_mapping.csv")
    dependency_rows = read_csv(docs_dir / "dependency.csv")

    if not dim_rows:
        errors.append("dim_list.csv has no rows")
    if not dwd_rows:
        warnings.append("dwd_list.csv has no rows")
    if not field_rows:
        warnings.append("field_mapping.csv has no rows")
    if not dependency_rows:
        warnings.append("dependency.csv has no rows")

    dim_tables = {row.get("table_name", "") for row in dim_rows}
    for row in dwd_rows:
        dimensions = [item for item in row.get("dimensions", "").split("+") if item]
        for dim in dimensions:
            if f"dim_{dim}" not in dim_tables:
                errors.append(f"DWD {row.get('table_name')} references missing DIM: dim_{dim}")
        if row.get("fact_type") != "factless" and not row.get("measures"):
            errors.append(f"DWD {row.get('table_name')} has no measures")
        if not row.get("grain"):
            errors.append(f"DWD {row.get('table_name')} has no grain")

    sql_files = list((ddl_dir).glob("**/*.sql")) + list((etl_dir).glob("**/*.sql"))
    if not sql_files:
        errors.append("no SQL files generated under ddl/ or etl/")

    for sql_file in sql_files:
        text = sql_file.read_text(encoding="utf-8")
        if "{{" in text or "}}" in text:
            errors.append(f"unrendered template placeholder in {sql_file}")

    return errors, warnings


def write_report(report_file: Path, errors: List[str], warnings: List[str]) -> None:
    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    lines = ["# Validation Report", "", f"Status: {status}", ""]
    if errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    if not errors and not warnings:
        lines.append("No validation issues.")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated CDM artifacts.")
    parser.add_argument("output_dir", help="Path to output/cdm-modeling")
    parser.add_argument("--write-report", action="store_true", help="Rewrite docs/validation_report.md")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    errors, warnings = validate_output_dir(output_dir)
    if args.write_report:
        write_report(output_dir / "docs" / "validation_report.md", errors, warnings)

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
