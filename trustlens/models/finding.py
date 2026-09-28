"""
Unified Finding Model (UFM) for TrustLens
Represents a normalized security finding from any scanner
"""
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class Location(BaseModel):
    """Location information for a finding"""
    file: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class UnifiedFinding(BaseModel):
    """
    Unified Finding Model - standard format for all scanner outputs
    """
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_tool: str  # checkov, trivy, semgrep
    rule_id: str  # e.g., CKV_AWS_18, CVE-2023-1234, etc.
    title: str
    severity_raw: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # e.g., encryption, iam, secrets, vulnerability, logging_monitoring
    resource: Optional[str] = None  # affected resource name
    location: Location  # file path and line info
    code_snippet: Optional[str] = None  # relevant code
    cwe: Optional[List[str]] = None  # CWE IDs like ["CWE-778"]
    description: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "finding_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_tool": "checkov",
                "rule_id": "CKV_AWS_18",
                "title": "Ensure S3 bucket has access logging enabled",
                "severity_raw": "HIGH",
                "category": "logging_monitoring",
                "resource": "aws_s3_bucket.bad_bucket",
                "location": {
                    "file": "sample_repo/main.tf",
                    "start_line": 2,
                    "end_line": 6
                },
                "code_snippet": 'resource "aws_s3_bucket" "bad_bucket" { ... }',
                "cwe": ["CWE-778"],
                "description": "S3 bucket does not have access logging enabled"
            }
        }

    def dedup_key(self) -> str:
        """
        Generate a deduplication key.
        Findings with same rule_id + file + resource are considered duplicates.
        """
        return f"{self.rule_id}|{self.location.file}|{self.resource or 'none'}"
