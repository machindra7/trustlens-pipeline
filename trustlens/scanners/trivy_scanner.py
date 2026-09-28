"""
Trivy Scanner - scans for CVEs in dependencies and container images
"""
import subprocess
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class TrivyScanner:
    """Runs Trivy scanner on a given path for vulnerabilities"""

    def __init__(self):
        self.tool_name = "trivy"

    def scan(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Run Trivy scanner on the given path.
        Returns list of raw findings from Trivy output.
        """
        try:
            cmd = [
                "trivy",
                "fs",
                repo_path,
                "--format", "json",
                "--severity", "CRITICAL,HIGH,MEDIUM,LOW",
                "--quiet",
            ]

            logger.info(f"[Trivy] Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Trivy returns exit code 1 if vulnerabilities found, which is okay
            if result.returncode in [0, 1]:
                if result.stdout.strip():
                    try:
                        output = json.loads(result.stdout)
                        findings = self._extract_findings(output)
                        logger.info(f"[Trivy] Found {len(findings)} vulnerabilities")
                        return findings
                    except json.JSONDecodeError as e:
                        logger.error(f"[Trivy] Failed to parse JSON: {e}")
                        return []
                else:
                    logger.info("[Trivy] No output received")
                    return []
            else:
                logger.error(f"[Trivy] Command failed with code {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                return []

        except FileNotFoundError:
            logger.warning("[Trivy] trivy not found - skipping Trivy scan")
            return []
        except subprocess.TimeoutExpired:
            logger.error("[Trivy] Scanner timeout exceeded")
            return []
        except Exception as e:
            logger.error(f"[Trivy] Unexpected error: {e}")
            return []

    def _extract_findings(self, output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract findings from Trivy JSON output.
        Trivy format includes 'Results' array with vulnerabilities
        """
        findings = []

        if "Results" in output:
            for result in output["Results"]:
                if "Vulnerabilities" in result:
                    for vuln in result["Vulnerabilities"]:
                        findings.append({
                            "type": "vulnerability",
                            "vulnerability_id": vuln.get("VulnerabilityID", ""),
                            "pkg_name": vuln.get("PkgName", ""),
                            "installed_version": vuln.get("InstalledVersion", ""),
                            "fixed_version": vuln.get("FixedVersion", ""),
                            "severity": vuln.get("Severity", ""),
                            "title": vuln.get("Title", ""),
                            "description": vuln.get("Description", ""),
                            "target": result.get("Target", ""),
                            "type_result": result.get("Type", ""),
                        })

        return findings
