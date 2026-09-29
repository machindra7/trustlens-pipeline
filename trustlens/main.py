#!/usr/bin/env python3
"""
TrustLens - Cloud Security Auditing Framework
Main entry point for Step 1 (Scanning), Step 2 (Normalization), and Step 3 (Ingestion)
"""
import logging
import json
import sys
import os           # NEW: Needed to check for environment variables (like secrets)
import argparse     # NEW: Needed to read command-line flags (like --path)
from pathlib import Path
from typing import List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scanners.checkov_scanner import CheckovScanner
from scanners.trivy_scanner import TrivyScanner
from scanners.semgrep_scanner import SemgrepScanner
from normalizer.normalize import Normalizer
from models.finding import UnifiedFinding

# NEW: Import the database ingestion function we updated in the previous step
from ingest_findings import run_ingestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger(__name__)


def run_scanning(repo_path: str):
    """
    Step 1: Run all three security scanners on the given repository path
    """
    logger.info("==================================================")
    logger.info("  TrustLens — Scanning The Code")
    logger.info("==================================================")

    checkov_findings = []
    trivy_findings = []
    semgrep_findings = []

    # Run Checkov
    checkov = CheckovScanner()
    logger.info(f"[Checkov] Scanning: {repo_path} ...")
    checkov_findings = checkov.scan(repo_path)

    # Run Trivy
    trivy = TrivyScanner()
    logger.info(f"[Trivy]   Scanning: {repo_path} ...")
    trivy_findings = trivy.scan(repo_path)

    # Run Semgrep
    semgrep = SemgrepScanner()
    logger.info(f"[Semgrep] Scanning: {repo_path} ...")
    semgrep_findings = semgrep.scan(repo_path)

    logger.info("")

    return checkov_findings, trivy_findings, semgrep_findings


def run_normalization(
    checkov_findings: List,
    trivy_findings: List,
    semgrep_findings: List,
    repo_path: str,
) -> List[UnifiedFinding]:
    """
    Normalize all findings into Unified Finding Model (UFM)
    """
    normalizer = Normalizer()
    ufm_findings = normalizer.normalize_all(
        checkov_findings,
        trivy_findings,
        semgrep_findings,
        repo_path,
    )
    normalizer.print_summary(repo_path)

    return ufm_findings


def save_findings(findings: List[UnifiedFinding], output_path: str):
    """
    Save findings to JSON file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert findings to JSON-serializable format
    findings_dict = [json.loads(f.model_dump_json()) for f in findings]

    with open(output_file, "w") as f:
        json.dump(findings_dict, f, indent=2)

    logger.info(f"Findings saved to: {output_file}")


def main():
    """Main entry point"""
    # 1. DEFINE THE COMMAND-LINE FLAGS
    parser = argparse.ArgumentParser(description="TrustLens Security Scanner")
    parser.add_argument("--path", help="Path to the project you want to scan")
    parser.add_argument("--db-url", help="Neon Database connection string")
    args = parser.parse_args()

    logger.info("🛡️ Welcome to TrustLens CLI")

    # 2. DETERMINE THE PATH (Flag vs. Interactive)
    repo_path = args.path
    if not repo_path:
        repo_path = input("? Enter the path to the project to scan [Default: .]: ") or "."

    # 3. DETERMINE THE DATABASE URL (Flag vs. Secret vs. Interactive)
    db_url = args.db_url or os.getenv("DATABASE_URL")
    if not db_url:
        db_url = input("? Enter your Neon DATABASE_URL (leave blank to skip DB upload): ")

    # 4. VERIFY REPOSITORY EXISTS
    if not Path(repo_path).exists():
        logger.error(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)

    # Clean up output path logic based on the user's input
    output_path = f"{repo_path}/findings.json" if repo_path != "." else "./findings.json"

    # Step 1: Scanning
    checkov_findings, trivy_findings, semgrep_findings = run_scanning(repo_path)

    # Step 2: Normalization
    ufm_findings = run_normalization(
        checkov_findings,
        trivy_findings,
        semgrep_findings,
        repo_path,
    )

    # Save findings
    save_findings(ufm_findings, output_path)

    # Step 3: Database Ingestion
    if db_url:
        logger.info("\nUploading findings to Neon Cloud Database...")
        run_ingestion(output_path, db_url)
    else:
        logger.info("\nSkipping database upload (no URL provided).")

    logger.info("")
    logger.info("✅ TrustLens pipeline completed successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(main())