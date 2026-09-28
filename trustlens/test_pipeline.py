#!/usr/bin/env python3
"""
Test script for TrustLens pipeline
Simulates the full pipeline with mock scanner data
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, '.')

from normalizer.normalize import Normalizer
from models.finding import UnifiedFinding
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def generate_mock_findings():
    """Generate realistic mock findings for testing"""

    # Mock Checkov findings
    checkov_raw = [
        {
            "type": "failed",
            "check_id": "CKV_AWS_18",
            "check_name": "Ensure S3 bucket has access logging enabled",
            "file_path": "sample_repo/main.tf",
            "code_block": [[6, 'bucket = "publicly-accessible-bucket"']],
            "resource": "aws_s3_bucket.bad_bucket",
            "description": "S3 bucket does not have access logging enabled",
            "guideline": "CWE-778"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_19",
            "check_name": "Ensure S3 encryption is enabled",
            "file_path": "sample_repo/main.tf",
            "code_block": [[6, 'bucket = "publicly-accessible-bucket"']],
            "resource": "aws_s3_bucket.bad_bucket",
            "description": "S3 bucket is not encrypted",
            "guideline": "CWE-311"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_21",
            "check_name": "Ensure all S3 buckets are encrypted",
            "file_path": "sample_repo/main.tf",
            "code_block": [[6, 'bucket = "publicly-accessible-bucket"']],
            "resource": "aws_s3_bucket.bad_bucket",
            "description": "S3 bucket is not encrypted with KMS",
            "guideline": "CWE-311"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_23",
            "check_name": "Ensure security groups do not allow ingress from 0.0.0.0",
            "file_path": "sample_repo/main.tf",
            "code_block": [[47, 'cidr_blocks = ["0.0.0.0/0"]']],
            "resource": "aws_security_group.bad_sg",
            "description": "Security group allows ingress from 0.0.0.0/0",
            "guideline": "CWE-22"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_24",
            "check_name": "Ensure SSH is not allowed from 0.0.0.0",
            "file_path": "sample_repo/main.tf",
            "code_block": [[54, 'cidr_blocks = ["0.0.0.0/0"]']],
            "resource": "aws_security_group.bad_sg",
            "description": "SSH is exposed to the entire internet",
            "guideline": "CWE-22"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_8",
            "check_name": "Ensure EC2 instance does not have public IP",
            "file_path": "sample_repo/main.tf",
            "code_block": [[73, 'associate_public_ip_address = true']],
            "resource": "aws_instance.bad_instance",
            "description": "EC2 instance has a public IP address",
            "guideline": "CWE-200"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_37",
            "check_name": "Ensure DB instances do not have public access",
            "file_path": "sample_repo/main.tf",
            "code_block": [[103, 'publicly_accessible = true']],
            "resource": "aws_db_instance.bad_rds",
            "description": "RDS instance is publicly accessible",
            "guideline": "CWE-200"
        },
        {
            "type": "failed",
            "check_id": "CKV_AWS_7",
            "check_name": "Ensure KMS key rotation is enabled",
            "file_path": "sample_repo/main.tf",
            "code_block": [[123, 'enable_key_rotation = false']],
            "resource": "aws_kms_key.bad_key",
            "description": "KMS key does not have automatic rotation enabled",
            "guideline": "CWE-320"
        },
    ]

    # Mock Trivy findings
    trivy_raw = [
        {
            "type": "vulnerability",
            "vulnerability_id": "CVE-2022-1234",
            "pkg_name": "flask",
            "installed_version": "1.0.0",
            "fixed_version": "2.0.0",
            "severity": "HIGH",
            "title": "Flask XSS vulnerability",
            "description": "Outdated version of Flask with known XSS vulnerability",
            "target": "sample_repo/requirements.txt",
            "type_result": "python"
        },
        {
            "type": "vulnerability",
            "vulnerability_id": "CVE-2021-5555",
            "pkg_name": "urllib3",
            "installed_version": "1.14",
            "fixed_version": "1.26.0",
            "severity": "CRITICAL",
            "title": "urllib3 SSL/TLS certificate verification bypass",
            "description": "Vulnerability in SSL certificate verification",
            "target": "sample_repo/requirements.txt",
            "type_result": "python"
        },
        {
            "type": "vulnerability",
            "vulnerability_id": "CVE-2020-9494",
            "pkg_name": "requests",
            "installed_version": "2.6.0",
            "fixed_version": "2.25.0",
            "severity": "MEDIUM",
            "title": "Requests HTTP/HTTPS redirects to FTP allowed",
            "description": "Requests library allows redirect to FTP protocol",
            "target": "sample_repo/requirements.txt",
            "type_result": "python"
        },
    ]

    # Mock Semgrep findings
    semgrep_raw = [
        {
            "type": "code_issue",
            "rule_id": "python.lang.security.injection.sql.sql-injection",
            "message": "User-controlled SQL query detected",
            "file_path": "sample_repo/app.py",
            "start": {"line": 26},
            "end": {"line": 28},
            "severity": "CRITICAL",
            "code": 'query = f"SELECT * FROM users WHERE id = {user_id}"',
            "metadata": {"cwe": ["CWE-89"]}
        },
        {
            "type": "code_issue",
            "rule_id": "python.lang.security.insecure-pickle.insecure-pickle-use",
            "message": "Unsafe use of pickle.loads() detected",
            "file_path": "sample_repo/app.py",
            "start": {"line": 59},
            "end": {"line": 61},
            "severity": "CRITICAL",
            "code": "deserialized = pickle.loads(data)",
            "metadata": {"cwe": ["CWE-502"]}
        },
    ]

    return checkov_raw, trivy_raw, semgrep_raw


def test_pipeline():
    """Test the full normalization pipeline"""
    logger.info("==================================================")
    logger.info("  TrustLens — Test Pipeline (Mock Data)")
    logger.info("==================================================")
    logger.info("")

    # Generate mock data
    checkov_raw, trivy_raw, semgrep_raw = generate_mock_findings()

    # Create normalizer and process all findings
    normalizer = Normalizer()
    ufm_findings = normalizer.normalize_all(
        checkov_raw,
        trivy_raw,
        semgrep_raw,
        "./sample_repo"
    )

    logger.info("")
    normalizer.print_summary("./sample_repo")

    logger.info("")
    logger.info("==================================================")
    logger.info("  Sample Findings (First 5)")
    logger.info("==================================================")
    logger.info("")

    for i, finding in enumerate(ufm_findings[:5], 1):
        logger.info(f"{i}. {finding.severity_raw} | {finding.source_tool.upper()}")
        logger.info(f"   Rule: {finding.rule_id}")
        logger.info(f"   Title: {finding.title}")
        logger.info(f"   File: {finding.location.file}")
        logger.info(f"   Category: {finding.category}")
        logger.info("")

    # Save to file
    findings_dict = [json.loads(f.model_dump_json()) for f in ufm_findings]
    with open("findings_test.json", "w") as f:
        json.dump(findings_dict, f, indent=2)

    logger.info(f"Saved {len(ufm_findings)} test findings to findings_test.json")
    logger.info("")
    logger.info("✓ Pipeline test completed successfully!")

    return len(ufm_findings)


if __name__ == "__main__":
    count = test_pipeline()
    sys.exit(0 if count > 0 else 1)
