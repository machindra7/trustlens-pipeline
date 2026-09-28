"""
Checkov Scanner - scans for infrastructure misconfigurations
Checks Terraform, CloudFormation, Kubernetes, Dockerfile, and more
"""
import subprocess
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class CheckovScanner:
    """Runs Checkov scanner on a given path"""

    def __init__(self):
        self.tool_name = "checkov"

    def scan(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Run Checkov scanner on the given path.
        Returns list of raw findings from Checkov output.
        """
        try:
            cmd = [
                "checkov",
                "-d", repo_path,
                "--output", "json",
                "--quiet",
            ]

            logger.info(f"[Checkov] Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Checkov returns exit code 1 if findings exist, which is okay
            if result.returncode in [0, 1]:
                if result.stdout.strip():
                    try:
                        output = json.loads(result.stdout)
                        findings = self._extract_findings(output)
                        logger.info(f"[Checkov] Found {len(findings)} issues")
                        return findings
                    except json.JSONDecodeError as e:
                        logger.error(f"[Checkov] Failed to parse JSON: {e}")
                        return []
                else:
                    logger.info("[Checkov] No output received")
                    return []
            else:
                logger.error(f"[Checkov] Command failed with code {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                return []

        except FileNotFoundError:
            logger.warning("[Checkov] checkov not found - skipping Checkov scan")
            return []
        except subprocess.TimeoutExpired:
            logger.error("[Checkov] Scanner timeout exceeded")
            return []
        except Exception as e:
            logger.error(f"[Checkov] Unexpected error: {e}")
            return []

    def _extract_findings(self, output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings from Checkov JSON output.
        Checkov format includes 'failed_checks', 'passed_checks', 'skipped_checks'
        """
        findings = []

        # Process failed checks
        if "failed_checks" in output:
            for check in output["failed_checks"]:
                findings.append({
                    "type": "failed",
                    "check_id": check.get("check_id", ""),
                    "check_name": check.get("check_name", ""),
                    "file_path": check.get("file_path", ""),
                    "file_abs_path": check.get("file_abs_path", ""),
                    "check_result": check.get("check_result", {}),
                    "code_block": check.get("code_block", []),
                    "resource": check.get("resource", ""),
                    "check_class": check.get("check_class", ""),
                    "description": check.get("description", ""),
                    "guideline": check.get("guideline", ""),
                })

        return findings
