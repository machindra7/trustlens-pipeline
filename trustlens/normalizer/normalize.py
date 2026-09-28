"""
Normalizer - converts raw scanner output to Unified Finding Model (UFM)
Handles deduplication and severity mapping
"""
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.finding import UnifiedFinding, Location

logger = logging.getLogger(__name__)


class SeverityMapper:
    """Maps various severity formats to standard severity levels"""

    SEVERITY_RANK = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    @staticmethod
    def normalize(severity: str) -> str:
        """
        Normalize severity strings to CRITICAL, HIGH, MEDIUM, LOW
        """
        if not severity:
            return "MEDIUM"

        severity_upper = severity.upper().strip()

        # Direct mappings
        if severity_upper in SeverityMapper.SEVERITY_RANK:
            return severity_upper

        # Common variations
        severity_map = {
            "CRITICAL": ["CRITICAL", "CRITICAL_RISK"],
            "HIGH": ["HIGH", "WARNING", "ERROR", "MAJOR"],
            "MEDIUM": ["MEDIUM", "INFO", "MINOR"],
            "LOW": ["LOW", "NOTE", "TRIVIAL"],
        }

        for standard, variants in severity_map.items():
            if severity_upper in variants:
                return standard

        # Default
        return "MEDIUM"


class CheckovNormalizer:
    """Normalizes Checkov findings to UFM"""

    @staticmethod
    def normalize(findings: List[Dict[str, Any]], repo_path: str) -> List[UnifiedFinding]:
        """Convert Checkov findings to UFM format"""
        ufm_findings = []

        for finding in findings:
            if finding.get("type") != "failed":
                continue

            check_id = finding.get("check_id", "UNKNOWN")
            file_path = finding.get("file_path", "")
            resource = finding.get("resource", "")

            # Extract line numbers from code_block
            start_line = None
            end_line = None
            code_snippet = ""
            if finding.get("code_block"):
                code_lines = finding["code_block"]
                if len(code_lines) > 0:
                    start_line = code_lines[0][0] if len(code_lines[0]) > 0 else None
                    end_line = code_lines[-1][0] if len(code_lines[-1]) > 0 else None
                    # code_block is list of [line_number, content]
                    code_parts = []
                    for line in code_lines:
                        if len(line) >= 2:
                            code_parts.append(str(line[1]))
                        elif len(line) >= 1:
                            code_parts.append(str(line[0]))
                    code_snippet = "\n".join(code_parts)

            # Map Checkov severity
            severity = "MEDIUM"  # Checkov failed checks are usually high/medium

            # Determine category from check_id
            category = CheckovNormalizer._map_category(check_id)

            ufm = UnifiedFinding(
                source_tool="checkov",
                rule_id=check_id,
                title=finding.get("check_name", "Unknown check"),
                severity_raw=severity,
                category=category,
                resource=resource,
                location=Location(
                    file=file_path,
                    start_line=start_line,
                    end_line=end_line,
                ),
                code_snippet=code_snippet if code_snippet else None,
                cwe=CheckovNormalizer._extract_cwe(finding),
                description=finding.get("description", ""),
            )

            ufm_findings.append(ufm)

        return ufm_findings

    @staticmethod
    def _map_category(check_id: str) -> str:
        """Map Checkov check ID to category"""
        if "S3" in check_id or "BUCKET" in check_id:
            return "storage_encryption"
        elif "IAM" in check_id:
            return "iam"
        elif "LOGGING" in check_id or "LOG" in check_id:
            return "logging_monitoring"
        elif "ENCRYPT" in check_id:
            return "encryption"
        elif "NETWORK" in check_id or "SECURITY_GROUP" in check_id:
            return "network_security"
        else:
            return "misconfiguration"

    @staticmethod
    def _extract_cwe(finding: Dict[str, Any]) -> List[str]:
        """Extract CWE IDs from finding if available"""
        cwe_list = []
        guideline = finding.get("guideline", "")
        if "CWE" in guideline:
            # Try to extract CWE numbers (simple extraction)
            import re
            matches = re.findall(r"CWE-\d+", guideline)
            cwe_list = matches
        return cwe_list if cwe_list else None


class TrivyNormalizer:
    """Normalizes Trivy findings to UFM"""

    @staticmethod
    def normalize(findings: List[Dict[str, Any]], repo_path: str) -> List[UnifiedFinding]:
        """Convert Trivy findings to UFM format"""
        ufm_findings = []

        for finding in findings:
            if finding.get("type") != "vulnerability":
                continue

            vuln_id = finding.get("vulnerability_id", "UNKNOWN")
            target = finding.get("target", "")
            severity = finding.get("severity", "MEDIUM")

            ufm = UnifiedFinding(
                source_tool="trivy",
                rule_id=vuln_id,
                title=finding.get("title", f"Vulnerability {vuln_id}"),
                severity_raw=SeverityMapper.normalize(severity),
                category="vulnerability",
                resource=finding.get("pkg_name", ""),
                location=Location(
                    file=target,
                    start_line=None,
                    end_line=None,
                ),
                code_snippet=None,
                cwe=None,
                description=finding.get("description", f"Installed: {finding.get('installed_version', 'unknown')}"),
            )

            ufm_findings.append(ufm)

        return ufm_findings


class SemgrepNormalizer:
    """Normalizes Semgrep findings to UFM"""

    @staticmethod
    def normalize(findings: List[Dict[str, Any]], repo_path: str) -> List[UnifiedFinding]:
        """Convert Semgrep findings to UFM format"""
        ufm_findings = []

        for finding in findings:
            if finding.get("type") != "code_issue":
                continue

            rule_id = finding.get("rule_id", "UNKNOWN")
            file_path = finding.get("file_path", "")
            severity = finding.get("severity", "MEDIUM")

            start_line = finding.get("start", {}).get("line")
            end_line = finding.get("end", {}).get("line")

            ufm = UnifiedFinding(
                source_tool="semgrep",
                rule_id=rule_id,
                title=finding.get("message", "Code issue detected"),
                severity_raw=SeverityMapper.normalize(severity),
                category=SemgrepNormalizer._map_category(rule_id),
                resource=None,
                location=Location(
                    file=file_path,
                    start_line=start_line,
                    end_line=end_line,
                ),
                code_snippet=finding.get("code"),
                cwe=SemgrepNormalizer._extract_cwe(finding),
                description=finding.get("message", ""),
            )

            ufm_findings.append(ufm)

        return ufm_findings

    @staticmethod
    def _map_category(rule_id: str) -> str:
        """Map Semgrep rule to category"""
        if "sql" in rule_id.lower() or "injection" in rule_id.lower():
            return "injection"
        elif "hardcode" in rule_id.lower() or "secret" in rule_id.lower():
            return "secrets"
        elif "auth" in rule_id.lower() or "crypto" in rule_id.lower():
            return "cryptography"
        else:
            return "code_vulnerability"

    @staticmethod
    def _extract_cwe(finding: Dict[str, Any]) -> List[str]:
        """Extract CWE IDs from Semgrep metadata"""
        cwe_list = []
        metadata = finding.get("metadata", {})
        if "cwe" in metadata:
            cwe = metadata["cwe"]
            if isinstance(cwe, list):
                cwe_list = [str(c) for c in cwe]
            else:
                cwe_list = [str(cwe)]
        return cwe_list if cwe_list else None


class Normalizer:
    """Main normalizer - coordinates all scanner normalizations and deduplication"""

    def __init__(self):
        self.findings: List[UnifiedFinding] = []

    def normalize_all(
        self,
        checkov_findings: List[Dict[str, Any]],
        trivy_findings: List[Dict[str, Any]],
        semgrep_findings: List[Dict[str, Any]],
        repo_path: str,
    ) -> List[UnifiedFinding]:
        """
        Normalize all scanner outputs and deduplicate
        """
        logger.info("==================================================")
        logger.info("  TrustLens — Step 2: Normalizing")
        logger.info("==================================================")

        # Normalize each scanner's output
        ufm_checkov = CheckovNormalizer.normalize(checkov_findings, repo_path)
        ufm_trivy = TrivyNormalizer.normalize(trivy_findings, repo_path)
        ufm_semgrep = SemgrepNormalizer.normalize(semgrep_findings, repo_path)

        logger.info(f"[Normalizer] Checkov findings  : {len(ufm_checkov)}")
        logger.info(f"[Normalizer] Trivy findings    : {len(ufm_trivy)}")
        logger.info(f"[Normalizer] Semgrep findings  : {len(ufm_semgrep)}")

        # Combine all findings
        all_findings = ufm_checkov + ufm_trivy + ufm_semgrep

        # Deduplicate
        deduplicated = self._deduplicate(all_findings)

        logger.info(f"[Normalizer] After dedup       : {len(deduplicated)}")

        # Sort by severity
        deduplicated.sort(
            key=lambda x: SeverityMapper.SEVERITY_RANK.get(x.severity_raw, 0),
            reverse=True
        )

        self.findings = deduplicated
        return deduplicated

    def _deduplicate(self, findings: List[UnifiedFinding]) -> List[UnifiedFinding]:
        """
        Deduplicate findings based on rule_id + file + resource
        Keeps the first occurrence of each dedup key
        """
        seen: Set[str] = set()
        deduplicated = []

        for finding in findings:
            key = finding.dedup_key()
            if key not in seen:
                seen.add(key)
                deduplicated.append(finding)

        return deduplicated

    def print_summary(self, repo_path: str):
        """Print human-readable summary of findings"""
        logger.info("")
        logger.info(f"[Result] {len(self.findings)} unique findings saved to findings.json")
        logger.info("")

        for finding in self.findings[:10]:  # Show top 10
            severity_pad = finding.severity_raw.ljust(8)
            tool_pad = finding.source_tool.upper().ljust(7)
            rule_pad = finding.rule_id.ljust(15)

            logger.info(
                f"  [{severity_pad}] {tool_pad} | {rule_pad} | {finding.title[:40]:40} | {finding.location.file}"
            )

        if len(self.findings) > 10:
            logger.info(f"  ... and {len(self.findings) - 10} more findings")
