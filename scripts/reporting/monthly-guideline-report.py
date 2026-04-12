#!/usr/bin/env python3
"""
monthly-guideline-report.py — Wikimedica Monthly Guideline Review Reminder

Reads data/registries/guideline-registry.yaml, identifies guidelines
due for review in the next 30 days or with a status of 'under-revision'
or 'superseded', and outputs a Markdown report suitable for use as a
GitHub Issue body.

Usage:
    python scripts/reporting/monthly-guideline-report.py [--registry PATH]
        [--output PATH] [--lookahead-days N]

Exit codes:
    0  Report generated; no urgent items
    1  Report generated; urgent/overdue guidelines found (triggers issue creation in CI)
    2  Script error
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("ERROR: pyyaml not installed. Run: pip install pyyaml")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REGISTRY = Path("data/registries/guideline-registry.yaml")
DEFAULT_LOOKAHEAD_DAYS = 30


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

def load_registry(registry_path: Path) -> list[dict[str, Any]]:
    """Load the guideline registry YAML and return the list of guidelines."""
    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}", file=sys.stderr)
        sys.exit(2)

    with registry_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    guidelines = data.get("guidelines", [])
    if not isinstance(guidelines, list):
        print("ERROR: 'guidelines' key in registry is not a list.", file=sys.stderr)
        sys.exit(2)

    return guidelines


# ---------------------------------------------------------------------------
# Guideline classification
# ---------------------------------------------------------------------------

def classify_guidelines(
    guidelines: list[dict], today: date, lookahead_days: int
) -> dict[str, list[dict]]:
    """
    Classify guidelines into urgency buckets.

    Returns a dict with keys:
      - overdue:        next_review is in the past
      - due_soon:       next_review within lookahead_days from today
      - under_revision: status == 'under-revision'
      - superseded:     status == 'superseded'
      - ok:             all others
    """
    buckets: dict[str, list[dict]] = {
        "overdue": [],
        "due_soon": [],
        "under_revision": [],
        "superseded": [],
        "ok": [],
    }

    lookahead_date = today + timedelta(days=lookahead_days)

    for gl in guidelines:
        status = gl.get("status", "current")
        next_review_str = gl.get("next_review")

        if status == "superseded":
            buckets["superseded"].append(gl)
            continue

        if status == "under-revision":
            buckets["under_revision"].append(gl)
            continue

        if status == "withdrawn":
            # Skip withdrawn guidelines
            continue

        if next_review_str:
            try:
                next_review = date.fromisoformat(str(next_review_str))
            except ValueError:
                buckets["ok"].append(gl)
                continue

            if next_review < today:
                buckets["overdue"].append(gl)
            elif next_review <= lookahead_date:
                buckets["due_soon"].append(gl)
            else:
                buckets["ok"].append(gl)
        else:
            buckets["ok"].append(gl)

    return buckets


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def format_guideline_row(gl: dict, note: str = "") -> str:
    """Format a guideline as a Markdown table row."""
    title = str(gl.get("title", ""))[:70]
    specialty = gl.get("specialty", "")
    issuer = gl.get("issuer", "")
    year = gl.get("year", "")
    next_review = gl.get("next_review", "—")
    priority = gl.get("priority", "")
    url = gl.get("url", "")
    url_link = f"[Link]({url})" if url else "—"

    return (
        f"| {title} | {specialty} | {issuer} | {year} "
        f"| {next_review} | {priority} | {url_link} | {note} |"
    )


def generate_report(
    buckets: dict[str, list[dict]],
    today: date,
    lookahead_days: int,
) -> str:
    """Build the full Markdown report."""
    lines: list[str] = []
    total_action = sum(len(buckets[k]) for k in ("overdue", "due_soon", "under_revision", "superseded"))

    lines += [
        "# Wikimedica Monthly Guideline Review Report",
        "",
        f"**Report date:** {today.isoformat()}",
        f"**Lookahead window:** {lookahead_days} days",
        f"**Action items this month:** {total_action}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Category | Count |",
        "|---|---|",
        f"| 🔴 Overdue (review date passed) | {len(buckets['overdue'])} |",
        f"| 🟡 Due soon (within {lookahead_days} days) | {len(buckets['due_soon'])} |",
        f"| 🔵 Currently under revision | {len(buckets['under_revision'])} |",
        f"| ⚫ Superseded (needs content update) | {len(buckets['superseded'])} |",
        f"| ✅ Not due yet | {len(buckets['ok'])} |",
        "",
        "---",
        "",
    ]

    table_header = (
        "| Title | Specialty | Issuer | Year | Next Review | Priority | URL | Action |"
    )
    table_sep = "|---|---|---|---|---|---|---|---|"

    # Overdue
    if buckets["overdue"]:
        lines += [
            "## 🔴 Overdue Guidelines",
            "",
            "*Review dates have passed. Wikimedica articles referencing these guidelines "
            "should be audited immediately.*",
            "",
            table_header, table_sep,
        ]
        for gl in sorted(buckets["overdue"], key=lambda g: g.get("priority", "low")):
            lines.append(format_guideline_row(gl, "Audit articles immediately"))
        lines.append("")

    # Due soon
    if buckets["due_soon"]:
        lines += [
            f"## 🟡 Due for Review Within {lookahead_days} Days",
            "",
            "*Plan editorial review of articles referencing these guidelines.*",
            "",
            table_header, table_sep,
        ]
        for gl in sorted(buckets["due_soon"], key=lambda g: str(g.get("next_review", ""))):
            lines.append(format_guideline_row(gl, "Review articles"))
        lines.append("")

    # Under revision
    if buckets["under_revision"]:
        lines += [
            "## 🔵 Currently Under Revision",
            "",
            "*These guidelines are being updated. Monitor for publication of the new version.*",
            "",
            table_header, table_sep,
        ]
        for gl in buckets["under_revision"]:
            lines.append(format_guideline_row(gl, "Monitor for new version"))
        lines.append("")

    # Superseded
    if buckets["superseded"]:
        lines += [
            "## ⚫ Superseded Guidelines",
            "",
            "*These guidelines have been superseded. All Wikimedica articles referencing "
            "them must be updated to the new version.*",
            "",
            table_header, table_sep,
        ]
        for gl in buckets["superseded"]:
            lines.append(format_guideline_row(gl, "Update to new guideline version"))
        lines.append("")

    # Footer
    lines += [
        "---",
        "",
        "## Instructions for Editors",
        "",
        "1. Review each flagged guideline and identify all Wikimedica articles referencing it.",
        "2. Open a PR to update article content to reflect the current guideline version.",
        "3. Update the `next_review` field in `data/registries/guideline-registry.yaml` "
        "   after review is complete.",
        "4. Close this issue once all action items are resolved.",
        "",
        "---",
        "",
        "*This report was generated automatically by `scripts/reporting/monthly-guideline-report.py`.*",
        "*Wikimedica / AT Medical Digital Solutions · wikimedica.de*",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Wikimedica monthly guideline review report."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=f"Path to guideline registry YAML (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file (default: print to stdout)",
    )
    parser.add_argument(
        "--lookahead-days",
        type=int,
        default=DEFAULT_LOOKAHEAD_DAYS,
        help=f"Alert window in days (default: {DEFAULT_LOOKAHEAD_DAYS})",
    )
    args = parser.parse_args()

    guidelines = load_registry(args.registry)
    today = date.today()
    buckets = classify_guidelines(guidelines, today, args.lookahead_days)
    report = generate_report(buckets, today, args.lookahead_days)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # Exit 1 if there are action items (used by CI to trigger issue creation)
    urgent_count = sum(
        len(buckets[k]) for k in ("overdue", "due_soon", "under_revision", "superseded")
    )
    return 1 if urgent_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
