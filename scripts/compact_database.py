"""
Utility script to generate a memory-friendly version of the comprehensive
drug database by keeping only the fields that the Streamlit app needs.

Usage:
    python scripts/compact_database.py

This reads `comprehensive_drug_database.json` and writes a trimmed version
to `comprehensive_drug_database_compact.json`. The script streams the source
file with ijson so peak memory usage stays low even though the original file
is ~1.3GB.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import ijson

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "comprehensive_drug_database.json"
TARGET = ROOT / "comprehensive_drug_database_compact.json"

ESSENTIAL_PROPERTY_KINDS = {
    "Melting Point",
    "Water Solubility",
    "Molecular Weight",
    "logP",
    "pKa",
}


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def simplify_dosing(dosing: dict | None) -> dict:
    if not isinstance(dosing, dict):
        return {}
    keep_keys = [
        "has_dosing",
        "source",
        "frequency",
        "times_per_day",
        "routes",
        "instructions",
    ]
    simplified = {k: dosing.get(k) for k in keep_keys if dosing.get(k) is not None}
    openfda_full = dosing.get("openfda_full")
    if isinstance(openfda_full, dict):
        simplified["openfda_full"] = {
            key: openfda_full.get(key)
            for key in ["frequency", "times_per_day", "times_per_day_range", "route", "routes", "instructions"]
            if openfda_full.get(key) is not None
        }
    return simplified


def simplify_interactions(interactions: list | None) -> list:
    if not isinstance(interactions, list):
        return []
    simplified = []
    for interaction in interactions:
        if not isinstance(interaction, dict):
            continue
        simplified.append(
            {
                "drugbank_id": interaction.get("drugbank_id"),
                "name": interaction.get("name"),
                "description": interaction.get("description"),
            }
        )
    return simplified


def simplify_dosages(dosages: list | None) -> list:
    if not isinstance(dosages, list):
        return []
    simplified = []
    for dosage in dosages:
        if not isinstance(dosage, dict):
            continue
        simplified.append(
            {
                "form": dosage.get("form"),
                "route": dosage.get("route"),
                "strength": dosage.get("strength"),
            }
        )
    return simplified


def simplify_properties(properties: list | None) -> list:
    if not isinstance(properties, list):
        return []
    simplified = []
    for prop in properties:
        if not isinstance(prop, dict):
            continue
        if prop.get("kind") in ESSENTIAL_PROPERTY_KINDS:
            simplified.append({"kind": prop.get("kind"), "value": prop.get("value"), "unit": prop.get("unit")})
    return simplified


def simplify_categories(categories: list | None) -> list:
    if not isinstance(categories, list):
        return []
    simplified = []
    for category in categories:
        if isinstance(category, dict):
            label = category.get("category") or category.get("mesh_id") or category.get("name")
            if label:
                simplified.append(label)
        elif isinstance(category, str):
            simplified.append(category)
    return simplified


def trim_drug(drug: dict) -> dict:
    trimmed = {
        "name": drug.get("name"),
        "drugbank_ids": {
            "primary": drug.get("drugbank_ids", {}).get("primary"),
            "secondary": drug.get("drugbank_ids", {}).get("secondary", []),
        },
        "description": drug.get("description"),
        "type": drug.get("type"),
        "groups": drug.get("groups", []),
        "categories": simplify_categories(drug.get("categories")),
        "mechanism_of_action": drug.get("mechanism_of_action"),
        "half_life": drug.get("half_life"),
        "absorption": drug.get("absorption"),
        "metabolism": drug.get("metabolism"),
        "food_interactions": drug.get("food_interactions", []),
        "drug_interactions": simplify_interactions(drug.get("drug_interactions")),
        "experimental_properties": simplify_properties(drug.get("experimental_properties")),
        "dosages": simplify_dosages(drug.get("dosages")),
        "dosing_info": simplify_dosing(drug.get("dosing_info")),
    }
    return trimmed


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source database not found at {SOURCE}")

    # Skip if compact file already exists (useful for local dev)
    if TARGET.exists():
        print(f"Compact database already exists at {TARGET}, skipping generation.")
        return

    print(f"Reading {SOURCE.stat().st_size / (1024**3):.2f} GB source file...")

    # Extract metadata first
    with SOURCE.open("rb") as f:
        metadata = next(ijson.items(f, "metadata"))

    with TARGET.open("w", encoding="utf-8") as out:
        out.write('{"metadata":')
        json.dump(metadata, out, default=_json_default, separators=(",", ":"))
        out.write(',"drugs":[')

        first = True
        with SOURCE.open("rb") as f:
            for drug in ijson.items(f, "drugs.item"):
                trimmed = trim_drug(drug)
                if not first:
                    out.write(",")
                json.dump(trimmed, out, default=_json_default, separators=(",", ":"))
                first = False
        out.write("]}")

    print(f"Wrote compact database to {TARGET} ({TARGET.stat().st_size / (1024**2):.1f} MB)")


if __name__ == "__main__":
    main()


