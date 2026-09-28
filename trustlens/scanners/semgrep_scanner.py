"""
Semgrep Scanner - scans application source code for OWASP Top 10 patterns
"""
import subprocess
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class SemgrepScanner:
    """Runs Semgrep scanner on a given path for code vulnerabilities"""

    def __init__(self):
        self.tool_name = "semgrep"

    def scan(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Run Semgrep scanner on the given path.
        Returns list of raw findings from Semgrep output.
        """
        try:
            cmd = [
                "semgrep",
                "--config=p/owasp-top-ten",
                repo_path,
                "--json",
                "--quiet",
            ]

            logger.info(f"[Semgrep] Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Semgrep returns exit code 1 if findings exist, which is okay
            if result.returncode in [0, 1]:
                if result.stdout.strip():
                    try:
                        output = json.loads(result.stdout)
                        findings = self._extract_findings(output)
                        logger.info(f"[Semgrep] Found {len(findings)} code issues")
                        return findings
                    except json.JSONDecodeError as e:
                        logger.error(f"[Semgrep] Failed to parse JSON: {e}")
                        return []
                else:
                    logger.info("[Semgrep] No output received")
                    return []
            else:
                logger.error(f"[Semgrep] Command failed with code {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                return []

        except FileNotFoundError:
            logger.warning("[Semgrep] semgrep not found - skipping Semgrep scan")
            return []
        except subprocess.TimeoutExpired:
            logger.error("[Semgrep] Scanner timeout exceeded")
            return []
        except Exception as e:
            logger.error(f"[Semgrep] Unexpected error: {e}")
            return []

    def _extract_findings(self, output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings from Semgrep JSON output.
        Semgrep format includes 'results' array with matched patterns
        """
        findings = []

        if "results" in output:
            for result in output["results"]:
                findings.append({
                    "type": "code_issue",
                    "rule_id": result.get("check_id", ""),
                    "message": result.get("extra", {}).get("message", ""),
                    "file_path": result.get("path", ""),
                    "start": result.get("start", {}),
                    "end": result.get("end", {}),
                    "severity": result.get("extra", {}).get("severity", ""),
                    "code": result.get("extra", {}).get("lines", ""),
                    "metadata": result.get("extra", {}).get("metadata", {}),
                })

        return findings
