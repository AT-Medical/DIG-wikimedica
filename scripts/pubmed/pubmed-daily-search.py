#!/usr/bin/env python3
"""
pubmed-daily-search.py — Wikimedica PubMed Surveillance Pipeline

Performs daily PubMed searches per specialty, classifies relevance,
maps results to Wikimedica specialties, stores JSONL output, and
triggers GitHub issue creation for high-relevance results.

Usage:
    python pubmed-daily-search.py [--date YYYY-MM-DD] [--dry-run]

Environment variables (required):
    NCBI_API_KEY         — NCBI Entrez API key
    GITHUB_TOKEN         — GitHub personal access token (for issue creation)
    GITHUB_REPO          — GitHub repository (owner/repo format)

Environment variables (optional):
    NCBI_EMAIL           — Email registered with NCBI (default: surveillance@wikimedica.de)
    SEARCH_TERMS_FILE    — Path to search-terms.yaml (default: scripts/pubmed/search-terms.yaml)
    OUTPUT_DIR           — Output directory for JSONL (default: data/pubmed)
    DAYS_BACK            — How many days back to search (default: 2)
    MONDAY_DAYS_BACK     — Days back on Mondays to cover weekend (default: 3)
    LOG_LEVEL            — Logging level (default: INFO)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

# Bio.Entrez is provided by the biopython package.
# Install: pip install biopython requests pyyaml
try:
    from Bio import Entrez, Medline
except ImportError:
    sys.exit(
        "ERROR: biopython is not installed. Run: pip install biopython"
    )

try:
    import requests
except ImportError:
    sys.exit(
        "ERROR: requests is not installed. Run: pip install requests"
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "surveillance@wikimedica.de")
NCBI_API_KEY = os.environ.get("NCBI_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

SEARCH_TERMS_FILE = Path(
    os.environ.get("SEARCH_TERMS_FILE", "scripts/pubmed/search-terms.yaml")
)
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "data/pubmed"))
DAYS_BACK = int(os.environ.get("DAYS_BACK", "2"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Retry settings for NCBI API calls
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

# Relevance score thresholds
HIGH_THRESHOLD = 60
MEDIUM_THRESHOLD = 30

# Publication type scores (used in relevance classification)
PUBTYPE_SCORES: dict[str, int] = {
    "Practice Guideline": 35,
    "Guideline": 30,
    "Meta-Analysis": 30,
    "Systematic Review": 25,
    "Randomized Controlled Trial": 30,
    "Clinical Trial": 20,
    "Multicenter Study": 15,
    "Observational Study": 5,
    "Review": 10,
    "Journal Article": 0,
    "Editorial": -20,
    "Letter": -20,
    "Comment": -15,
    "Congress": -10,
}

# High-impact journal list (abbreviated NLM titles) — extend as needed
HIGH_IMPACT_JOURNALS = {
    "N Engl J Med",
    "Lancet",
    "JAMA",
    "BMJ",
    "Ann Intern Med",
    "Circulation",
    "Eur Heart J",
    "JAMA Intern Med",
    "Lancet Oncol",
    "Lancet Neurol",
    "Gut",
    "Hepatology",
    "Am J Respir Crit Care Med",
    "Diabetes Care",
    "J Clin Oncol",
    "Blood",
    "Neurology",
}

# Patient safety keywords (title/abstract scan)
SAFETY_KEYWORDS = [
    "safety",
    "adverse event",
    "serious adverse",
    "contraindication",
    "drug interaction",
    "recall",
    "warning",
    "Sicherheit",
    "Nebenwirkung",
    "Kontraindikation",
    "Warnhinweis",
]


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure structured logging."""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    return logging.getLogger("pubmed_surveillance")


logger = setup_logging()


# ---------------------------------------------------------------------------
# Search term loading
# ---------------------------------------------------------------------------

def load_search_terms(path: Path) -> dict[str, Any]:
    """Load PubMed search terms from the YAML configuration file."""
    if not path.exists():
        logger.error("Search terms file not found: %s", path)
        sys.exit(1)

    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    logger.info("Loaded search terms for %d specialties", len(data.get("specialties", {})))
    return data


# ---------------------------------------------------------------------------
# NCBI Entrez helpers
# ---------------------------------------------------------------------------

def setup_entrez() -> None:
    """Configure Bio.Entrez with credentials."""
    Entrez.email = NCBI_EMAIL
    if NCBI_API_KEY:
        Entrez.api_key = NCBI_API_KEY
        logger.debug("NCBI API key configured; rate limit: 10 req/s")
    else:
        logger.warning("No NCBI_API_KEY set; rate limit reduced to 3 req/s")


def entrez_call_with_retry(func, *args, **kwargs):
    """Execute an Entrez API call with retry and exponential backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            wait = RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "Entrez call failed (attempt %d/%d): %s. Retrying in %ds...",
                attempt,
                MAX_RETRIES,
                exc,
                wait,
            )
            if attempt == MAX_RETRIES:
                raise
            time.sleep(wait)
    return None


def search_pubmed(query: str, days_back: int) -> list[str]:
    """
    Search PubMed for articles published in the last `days_back` days.

    Returns a list of PMID strings.
    """
    min_date = (date.today() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    max_date = date.today().strftime("%Y/%m/%d")

    full_query = f"({query}) AND (\"{min_date}\"[PDAT]:\"{max_date}\"[PDAT])"
    logger.debug("Searching PubMed: %s", full_query)

    handle = entrez_call_with_retry(
        Entrez.esearch,
        db="pubmed",
        term=full_query,
        retmax=200,
        usehistory="y",
    )
    results = Entrez.read(handle)
    handle.close()

    pmids = results.get("IdList", [])
    logger.info("Query '%s': %d new PMIDs found", query[:60], len(pmids))
    return pmids


def fetch_records(pmids: list[str]) -> list[dict]:
    """Fetch full PubMed records for a list of PMIDs using Medline format."""
    if not pmids:
        return []

    handle = entrez_call_with_retry(
        Entrez.efetch,
        db="pubmed",
        id=",".join(pmids),
        rettype="medline",
        retmode="text",
    )
    records = list(Medline.parse(handle))
    handle.close()
    return records


# ---------------------------------------------------------------------------
# Record normalisation
# ---------------------------------------------------------------------------

def normalise_record(raw: dict, specialty_tags: list[str], query_name: str) -> dict:
    """
    Normalise a raw Medline record into the Wikimedica PubMed schema.
    """
    pmid = raw.get("PMID", "")
    pub_types = raw.get("PT", [])
    journal = raw.get("TA", raw.get("JT", ""))

    relevance_score = compute_relevance_score(raw, pub_types, journal)

    if relevance_score >= HIGH_THRESHOLD:
        relevance_class = "HIGH"
    elif relevance_score >= MEDIUM_THRESHOLD:
        relevance_class = "MEDIUM"
    else:
        relevance_class = "LOW"

    return {
        "pmid": pmid,
        "title": raw.get("TI", ""),
        "abstract": raw.get("AB", ""),
        "authors": raw.get("AU", []),
        "journal": journal,
        "year": int(raw.get("DP", "0")[:4]) if raw.get("DP") else None,
        "publication_date": raw.get("DP", ""),
        "publication_types": pub_types,
        "mesh_terms": raw.get("MH", []),
        "specialty_tags": specialty_tags,
        "relevance_score": relevance_score,
        "relevance_class": relevance_class,
        "action_taken": None,  # Filled in after dispatch
        "github_issue_url": None,
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "source": "pubmed",
        "search_query_matched": query_name,
        "language": raw.get("LA", [""])[0] if raw.get("LA") else "",
        "doi": raw.get("AID", [""])[0] if raw.get("AID") else None,
        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


# ---------------------------------------------------------------------------
# Relevance classification (stub heuristic)
# ---------------------------------------------------------------------------

def compute_relevance_score(raw: dict, pub_types: list[str], journal: str) -> int:
    """
    Compute a relevance score (0–100) using a rule-based heuristic.

    This is a stub designed to be replaced with an ML classifier.
    See docs/pubmed/pubmed-surveillance-architecture.md for the full scoring spec.
    """
    score = 0

    # Publication type contribution
    for pt in pub_types:
        score += PUBTYPE_SCORES.get(pt, 0)

    # High-impact journal bonus
    if journal in HIGH_IMPACT_JOURNALS:
        score += 15

    # Patient safety keyword scan
    title = raw.get("TI", "").lower()
    abstract = raw.get("AB", "").lower()
    text = title + " " + abstract
    for keyword in SAFETY_KEYWORDS:
        if keyword.lower() in text:
            score += 10
            break  # Count once per record

    # Clamp to 0–100
    return max(0, min(100, score))


# ---------------------------------------------------------------------------
# Processed PMID tracking
# ---------------------------------------------------------------------------

def load_processed_pmids(output_dir: Path) -> set[str]:
    """Load the set of already-processed PMIDs from the tracking file."""
    tracking_file = output_dir / "processed_pmids.txt"
    if not tracking_file.exists():
        return set()
    return set(tracking_file.read_text(encoding="utf-8").splitlines())


def save_processed_pmids(output_dir: Path, new_pmids: set[str]) -> None:
    """Append new PMIDs to the processed tracking file."""
    tracking_file = output_dir / "processed_pmids.txt"
    with tracking_file.open("a", encoding="utf-8") as fh:
        for pmid in sorted(new_pmids):
            fh.write(pmid + "\n")


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_jsonl(output_dir: Path, records: list[dict], run_date: str) -> Path:
    """Write normalised records to a dated JSONL file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{run_date}.jsonl"

    with output_file.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Wrote %d records to %s", len(records), output_file)
    return output_file


def write_pending_review(output_dir: Path, records: list[dict]) -> None:
    """Append MEDIUM-relevance records to the pending review queue."""
    pending_file = output_dir / "pending-review.jsonl"
    with pending_file.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# GitHub Issue creation
# ---------------------------------------------------------------------------

def create_github_issue(record: dict, dry_run: bool = False) -> str | None:
    """
    Create a GitHub Issue for a HIGH-relevance PubMed record.

    Returns the issue URL if created, None otherwise.
    """
    if dry_run:
        logger.info("[DRY RUN] Would create issue for PMID %s", record["pmid"])
        return None

    if not GITHUB_TOKEN or not GITHUB_REPO:
        logger.warning(
            "GITHUB_TOKEN or GITHUB_REPO not set; cannot create issue for PMID %s",
            record["pmid"],
        )
        return None

    specialty_labels = [tag.lower().replace("/", "-").replace(" ", "-") for tag in record.get("specialty_tags", [])]
    labels = ["pubmed-alert", "priority-high"] + specialty_labels

    title = f"[PubMed Alert] {record['title'][:120]}"
    abstract_excerpt = (record.get("abstract") or "")[:400]
    body = (
        f"## PubMed Surveillance Alert\n\n"
        f"**PMID:** [{record['pmid']}]({record['pubmed_url']})\n"
        f"**Journal:** {record['journal']} ({record['year']})\n"
        f"**Publication types:** {', '.join(record['publication_types'])}\n"
        f"**Specialty tags:** {', '.join(record['specialty_tags'])}\n"
        f"**Relevance score:** {record['relevance_score']} (HIGH)\n\n"
        f"### Abstract excerpt\n\n{abstract_excerpt}...\n\n"
        f"### Suggested action\n\nPlease review this publication and determine whether "
        f"any Wikimedica articles in the {', '.join(record['specialty_tags'])} specialty "
        f"require updating.\n\n"
        f"*Generated automatically by Wikimedica PubMed Surveillance — {record['processed_at']}*"
    )

    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    response = requests.post(
        api_url,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={"title": title, "body": body, "labels": labels},
        timeout=30,
    )

    if response.status_code == 201:
        issue_url = response.json().get("html_url")
        logger.info("Created GitHub issue for PMID %s: %s", record["pmid"], issue_url)
        return issue_url
    else:
        logger.error(
            "Failed to create GitHub issue for PMID %s: HTTP %d — %s",
            record["pmid"],
            response.status_code,
            response.text[:200],
        )
        return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(run_date: str, days_back: int, dry_run: bool = False) -> None:
    """Execute the full PubMed surveillance pipeline for the given date."""
    logger.info("=== Wikimedica PubMed Surveillance — %s ===", run_date)
    logger.info("Days back: %d | Dry run: %s", days_back, dry_run)

    if not NCBI_API_KEY:
        logger.warning("NCBI_API_KEY not set. Requests will be rate-limited to 3/s.")

    setup_entrez()

    search_config = load_search_terms(SEARCH_TERMS_FILE)
    specialties = search_config.get("specialties", {})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    processed_pmids = load_processed_pmids(OUTPUT_DIR)
    logger.info("Loaded %d already-processed PMIDs", len(processed_pmids))

    all_records: list[dict] = []
    new_pmids: set[str] = set()
    stats = {"high": 0, "medium": 0, "low": 0, "skipped": 0, "errors": 0}

    for specialty_name, specialty_config in specialties.items():
        queries = specialty_config.get("queries", [])
        specialty_tags = specialty_config.get("wikimedica_tags", [specialty_name])

        for query_entry in queries:
            query_name = query_entry.get("name", specialty_name)
            query_string = query_entry.get("query", "")

            if not query_string:
                logger.warning("Empty query for '%s', skipping.", query_name)
                continue

            try:
                pmids = search_pubmed(query_string, days_back)
                # Filter out already-processed PMIDs
                new_in_query = [p for p in pmids if p not in processed_pmids]
                logger.info(
                    "%s: %d total, %d new PMIDs to process",
                    query_name, len(pmids), len(new_in_query),
                )

                if not new_in_query:
                    continue

                raw_records = fetch_records(new_in_query)
                time.sleep(0.5)  # Respect rate limits

                for raw in raw_records:
                    pmid = raw.get("PMID", "")
                    if not pmid:
                        stats["errors"] += 1
                        continue

                    record = normalise_record(raw, specialty_tags, query_name)
                    all_records.append(record)
                    new_pmids.add(pmid)

                    # Dispatch action based on relevance
                    if record["relevance_class"] == "HIGH":
                        stats["high"] += 1
                        issue_url = create_github_issue(record, dry_run=dry_run)
                        record["action_taken"] = "issue_opened"
                        record["github_issue_url"] = issue_url

                    elif record["relevance_class"] == "MEDIUM":
                        stats["medium"] += 1
                        record["action_taken"] = "logged_for_review"

                    else:
                        stats["low"] += 1
                        record["action_taken"] = "stored_only"

            except Exception as exc:  # noqa: BLE001
                logger.error("Error processing query '%s': %s", query_name, exc)
                stats["errors"] += 1
                # Log to error file
                error_log = OUTPUT_DIR / "error.log"
                with error_log.open("a") as ef:
                    ef.write(f"{datetime.utcnow().isoformat()}Z ERROR query={query_name} error={exc}\n")

    # Write all records to dated JSONL
    if all_records:
        write_jsonl(OUTPUT_DIR, all_records, run_date)

        # Write MEDIUM records to pending review queue
        medium_records = [r for r in all_records if r["relevance_class"] == "MEDIUM"]
        if medium_records:
            write_pending_review(OUTPUT_DIR, medium_records)

        # Update processed PMIDs tracking
        if not dry_run:
            save_processed_pmids(OUTPUT_DIR, new_pmids)

    logger.info(
        "=== Pipeline complete: %d HIGH | %d MEDIUM | %d LOW | %d errors ===",
        stats["high"], stats["medium"], stats["low"], stats["errors"],
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wikimedica PubMed daily surveillance pipeline")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Run date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=DAYS_BACK,
        help="Number of days back to search (default: from DAYS_BACK env var or 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process records but do not create GitHub issues or commit files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # On Mondays, extend search window to cover the weekend
    days = args.days_back
    monday_days_back = int(os.environ.get("MONDAY_DAYS_BACK", "3"))
    if date.today().weekday() == 0 and days < monday_days_back:  # Monday
        days = monday_days_back
        logger.info(
            "Monday detected — extending search window to %d days to cover weekend",
            monday_days_back,
        )

    run_pipeline(run_date=args.date, days_back=days, dry_run=args.dry_run)
