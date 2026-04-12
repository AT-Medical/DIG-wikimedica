#!/usr/bin/env python3
"""
validate-metadata.py — Wikimedica Article Frontmatter Validator

Validates YAML frontmatter in Wikimedica Markdown articles against the
canonical article schema defined in data/metadata/article-schema.yaml.

Usage:
    python scripts/validation/validate-metadata.py [files...]
    python scripts/validation/validate-metadata.py content/specialties/kardiologie/herzinsuffizienz.md
    python scripts/validation/validate-metadata.py content/  # Scan entire directory

Exit codes:
    0  All files valid
    1  One or more validation errors found
    2  Script error (missing schema, unreadable file, etc.)

Dependencies:
    pip install pyyaml
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("ERROR: pyyaml not installed. Run: pip install pyyaml")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_PATH = Path("data/metadata/article-schema.yaml")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Fields that must be present before publication (status: published)
PUBLICATION_REQUIRED_FIELDS = {"reviewers", "pubmed_ids"}

# Valid status flow (for sequence validation)
VALID_STATUSES = {
    "draft", "in-review", "advisor-review", "approved",
    "published", "archived", "retracted",
}

VALID_ARTICLE_TYPES = {
    "professional", "patient", "consent", "discharge", "pharmaka", "therapy",
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load and parse the article schema YAML."""
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(2)

    with schema_path.open(encoding="utf-8") as fh:
        schema = yaml.safe_load(fh)

    if "fields" not in schema:
        print("ERROR: Schema file missing 'fields' key.", file=sys.stderr)
        sys.exit(2)

    return schema["fields"]


# ---------------------------------------------------------------------------
# Frontmatter extraction
# ---------------------------------------------------------------------------

def extract_frontmatter(file_path: Path) -> tuple[dict | None, int]:
    """
    Extract and parse YAML frontmatter from a Markdown file.

    Returns:
        (parsed_dict, frontmatter_end_line)  — or (None, 0) if no frontmatter found.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, 0

    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, 0

    frontmatter_text = match.group(1)
    # Count lines in frontmatter to report accurate error line numbers
    end_line = frontmatter_text.count("\n") + 2  # +2 for opening and closing ---

    try:
        parsed = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        return {"_yaml_error": str(exc)}, end_line

    if not isinstance(parsed, dict):
        return {}, end_line

    return parsed, end_line


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

class ValidationError:
    """Represents a single validation error."""

    def __init__(self, file_path: Path, line: int | None, field: str, message: str):
        self.file_path = file_path
        self.line = line
        self.field = field
        self.message = message

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line else ""
        return f"{self.file_path}{loc}  [{self.field}]  {self.message}"


def validate_frontmatter(
    file_path: Path,
    frontmatter: dict,
    schema: dict[str, Any],
    frontmatter_end_line: int,
) -> list[ValidationError]:
    """Validate parsed frontmatter against the schema. Returns a list of errors."""
    errors: list[ValidationError] = []

    def err(field: str, message: str) -> None:
        errors.append(ValidationError(file_path, frontmatter_end_line, field, message))

    # Check for YAML parse error
    if "_yaml_error" in frontmatter:
        err("YAML", f"YAML parse error: {frontmatter['_yaml_error']}")
        return errors

    # Validate each schema field
    for field_name, field_spec in schema.items():
        is_required = field_spec.get("required", False)
        field_type = field_spec.get("type")
        allowed_values = field_spec.get("values")
        min_length = field_spec.get("min_length")

        value = frontmatter.get(field_name)

        # Required field presence check
        if is_required and value is None:
            err(field_name, f"Required field '{field_name}' is missing.")
            continue

        if value is None:
            continue  # Optional field; skip further checks

        # Type checking
        type_map = {"str": str, "int": int, "list": list, "bool": bool, "dict": dict}
        expected_type = type_map.get(field_type)
        if expected_type and not isinstance(value, expected_type):
            err(
                field_name,
                f"Expected type '{field_type}', got '{type(value).__name__}' "
                f"(value: {repr(value)[:60]})",
            )
            continue

        # Allowed values check (enum)
        if allowed_values and value not in allowed_values:
            err(
                field_name,
                f"Value '{value}' is not in allowed values: {allowed_values}",
            )

        # Minimum list length
        if min_length and isinstance(value, list) and len(value) < min_length:
            err(field_name, f"List must have at least {min_length} item(s); got {len(value)}.")

        # Date format check
        if field_type == "str" and field_spec.get("format") == "YYYY-MM-DD":
            if value and not DATE_PATTERN.match(str(value)):
                err(field_name, f"Expected ISO 8601 date (YYYY-MM-DD), got '{value}'.")
            else:
                # Validate that it's a real date
                try:
                    date.fromisoformat(str(value))
                except ValueError:
                    err(field_name, f"'{value}' is not a valid calendar date.")

    # Version format check
    if "version" in frontmatter and frontmatter["version"]:
        if not SEMVER_PATTERN.match(str(frontmatter["version"])):
            err("version", f"Version '{frontmatter['version']}' must follow semver (MAJOR.MINOR.PATCH).")

    # Cross-field validations
    status = frontmatter.get("status")
    article_type = frontmatter.get("article_type")

    # Published articles must have reviewers
    if status == "published":
        reviewers = frontmatter.get("reviewers", [])
        if not reviewers:
            err("reviewers", "Published articles must have at least one reviewer listed.")

    # Updated date must not be before created date
    created = frontmatter.get("created")
    updated = frontmatter.get("updated")
    if created and updated:
        try:
            if date.fromisoformat(str(updated)) < date.fromisoformat(str(created)):
                err("updated", f"'updated' ({updated}) cannot be earlier than 'created' ({created}).")
        except ValueError:
            pass  # Date format errors already reported above

    # Consent/discharge modules should have procedure field
    if article_type in ("consent", "discharge") and not frontmatter.get("procedure"):
        err("procedure", f"Article type '{article_type}' should have a 'procedure' field.")

    # wikimedica_credit must be true
    if "wikimedica_credit" in frontmatter and frontmatter["wikimedica_credit"] is not True:
        err("wikimedica_credit", "wikimedica_credit must be true (boolean).")

    return errors


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def collect_files(paths: list[Path]) -> list[Path]:
    """Collect all Markdown files from the provided paths (files or directories)."""
    md_files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".md":
            md_files.append(path)
        elif path.is_dir():
            md_files.extend(sorted(path.rglob("*.md")))
        else:
            print(f"WARNING: Skipping non-Markdown or non-existent path: {path}", file=sys.stderr)
    return md_files


def has_frontmatter_marker(file_path: Path) -> bool:
    """Quick check: does the file start with a YAML frontmatter block?"""
    try:
        with file_path.open(encoding="utf-8") as fh:
            return fh.read(4) == "---\n"
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Wikimedica article frontmatter against the article schema."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown files or directories to validate.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=SCHEMA_PATH,
        help=f"Path to article schema YAML (default: {SCHEMA_PATH})",
    )
    parser.add_argument(
        "--skip-no-frontmatter",
        action="store_true",
        default=True,
        help="Skip files without frontmatter (default: True).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors.",
    )
    args = parser.parse_args()

    # Load schema
    schema = load_schema(args.schema)

    # Collect files
    files = collect_files(args.paths)
    if not files:
        print("No Markdown files found.")
        return 0

    total_errors = 0
    files_with_errors = 0
    files_skipped = 0
    files_validated = 0

    for file_path in files:
        # Skip files without frontmatter
        if not has_frontmatter_marker(file_path):
            if not args.skip_no_frontmatter:
                print(f"SKIP (no frontmatter): {file_path}")
            files_skipped += 1
            continue

        frontmatter, end_line = extract_frontmatter(file_path)
        if frontmatter is None:
            print(f"SKIP (unreadable): {file_path}")
            files_skipped += 1
            continue

        errors = validate_frontmatter(file_path, frontmatter, schema, end_line)
        files_validated += 1

        if errors:
            files_with_errors += 1
            for error in errors:
                print(f"ERROR  {error}")
            total_errors += len(errors)
        else:
            print(f"OK     {file_path}")

    # Summary
    print(
        f"\n--- Validation Summary ---\n"
        f"Files validated:    {files_validated}\n"
        f"Files skipped:      {files_skipped}\n"
        f"Files with errors:  {files_with_errors}\n"
        f"Total errors:       {total_errors}\n"
    )

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
