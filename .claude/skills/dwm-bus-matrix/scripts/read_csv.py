#!/usr/bin/env python3
"""
CSV reader for dwm-bus-matrix skill.

Usage:
    # Read all rows
    python read_csv.py output/dwm-bus-matrix/step1/dwm_s1_source_registry.csv

    # Filter by column value
    python read_csv.py output/dwm-bus-matrix/step1/dwm_s1_field_registry.csv --where "constraint_type=PK"

    # Multiple filters (AND)
    python read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv --where "core_tag=外键" --where "review_status=approved"

    # Select specific columns
    python read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv --select "ods_table_name,col_name,core_tag"

    # Count rows
    python read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv --where "core_tag=外键" --count

    # Distinct values of a column
    python read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv --distinct "core_tag"
"""

import csv
import json
import sys
import argparse


def read_csv(filepath: str) -> list[dict]:
    """Read CSV with BOM handling, return list of dicts."""
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def apply_filters(rows: list[dict], filters: list[str]) -> list[dict]:
    """Filter rows by key=value conditions (AND logic)."""
    for f in filters:
        key, value = f.split("=", 1)
        rows = [r for r in rows if r.get(key, "") == value]
    return rows


def select_columns(rows: list[dict], columns: list[str]) -> list[dict]:
    """Keep only specified columns."""
    return [{k: r.get(k, "") for k in columns} for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Read CSV, output JSON")
    parser.add_argument("filepath", help="Input CSV file path")
    parser.add_argument("--where", "-w", action="append", default=[], help="Filter: key=value (repeatable, AND)")
    parser.add_argument("--select", "-s", help="Comma-separated columns to include")
    parser.add_argument("--count", action="store_true", help="Output row count only")
    parser.add_argument("--distinct", "-d", help="Output distinct values of a column")
    args = parser.parse_args()

    rows = read_csv(args.filepath)

    if args.where:
        rows = apply_filters(rows, args.where)

    if args.distinct:
        values = sorted(set(r.get(args.distinct, "") for r in rows))
        print(json.dumps(values, ensure_ascii=False, indent=2))
        return

    if args.count:
        print(len(rows))
        return

    if args.select:
        rows = select_columns(rows, args.select.split(","))

    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
