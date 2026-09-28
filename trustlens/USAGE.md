# TrustLens Usage Guide

Complete guide to using TrustLens for cloud security scanning.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Command Line Options](#command-line-options)
3. [Configuration](#configuration)
4. [Output Format](#output-format)
5. [Real-World Examples](#real-world-examples)
6. [Integration](#integration)
7. [Tips & Tricks](#tips--tricks)

## Basic Usage

### Simplest: Scan Default Location

```bash
cd trustlens
python main.py
```

This scans `./sample_repo` and outputs to `./findings.json`.

### Scan Custom Repository

```bash
python main.py /path/to/your/repo
```

Outputs to `./findings.json` in the current directory.

### Custom Output Path

```bash
python main.py /path/to/your/repo /custom/output/findings.json
```

---

## Command Line Options

### Current Implementation

```bash
python main.py [REPO_PATH] [OUTPUT_PATH]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `REPO_PATH` | `./sample_repo` | Path to repository to scan |
| `OUTPUT_PATH` | `./findings.json` | Output file path for findings |

### Examples

```bash
# Scan current directory
python main.py . ./audit/findings.json

# Scan absolute path
python main.py /home/user/project /home/user/audit.json

# Use relative paths
python main.py ../other_repo ../results/findings.json
```

---

## Configuration

### Logging Control

Modify `main.py` to control logging verbosity:

```python
# In main.py, change:
logging.basicConfig(
    level=logging.DEBUG,  # Change INFO to DEBUG for more details
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

Log levels:
- `DEBUG`: Detailed scanner operations
- `INFO`: General progress (default)
- `WARNING`: Issues but continues
- `ERROR`: Failures, but continues
- `CRITICAL`: Fatal errors

### Scanner Timeouts

Modify `scanners/*.py` to adjust timeouts:

```python
# In each scanner, the timeout is set to 120 seconds:
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=300  # Change to 300 seconds for large repos
)
```

### Scanner-Specific Options

#### Checkov

Currently uses basic scanning. To customize, edit `checkov_scanner.py`:

```python
# Add to cmd list:
"--skip-framework", "kubernetes",  # Skip Kubernetes checks
"--check", "CKV_AWS_18",  # Only run specific check
"--external-checks", "/path/to/custom/checks"  # Custom checks
```

#### Trivy

To add vulnerability filtering in `trivy_scanner.py`:

```python
cmd = [
    "trivy", "fs",
    repo_path,
    "--format", "json",
    "--severity", "CRITICAL,HIGH",  # Skip MEDIUM and LOW
    "--ignore-unfixed",  # Skip CVEs without fixes
]
```

#### Semgrep

To use different rule configs in `semgrep_scanner.py`:

```python
# Change from default OWASP Top 10:
"--config=p/security-audit",  # CWE-based rules
# Or use custom rules:
"--config=/path/to/custom.yaml",
```

---

## Output Format

### findings.json Structure

Each finding is a JSON object with:

```json
{
  "finding_id": "550e8400-e29b-41d4-a716-446655440000",
  "source_tool": "checkov|trivy|semgrep",
  "rule_id": "CKV_AWS_18|CVE-2021-1234|python.lang.security",
  "title": "Human-readable title",
  "severity_raw": "CRITICAL|HIGH|MEDIUM|LOW",
  "category": "encryption|iam|vulnerability|injection|...",
  "resource": "aws_s3_bucket.name",
  "location": {
    "file": "path/to/file",
    "start_line": 10,
    "end_line": 15
  },
  "code_snippet": "relevant code excerpt",
  "cwe": ["CWE-89", "CWE-200"],
  "description": "Detailed description",
  "timestamp": "2025-01-15T10:30:45.123456"
}
```

### Severity Levels

| Level | Risk | Action |
|-------|------|--------|
| CRITICAL | Immediate | Fix immediately, block deployment |
| HIGH | Urgent | Fix before production |
| MEDIUM | Important | Fix in next sprint |
| LOW | Minor | Fix when possible |

### Categories

- **encryption**: Encryption-related misconfigurations
- **iam**: Identity & Access Management issues
- **secrets**: Hard-coded secrets, exposed credentials
- **vulnerability**: Known CVEs in dependencies
- **injection**: SQL, command, code injection
- **network_security**: Network configuration issues
- **logging_monitoring**: Missing logs, monitoring
- **misconfiguration**: General IAC misconfigurations
- **storage_encryption**: Storage-specific encryption
- **code_vulnerability**: Code-level vulnerabilities
- **cryptography**: Crypto algorithm issues

---

## Real-World Examples

### Example 1: Scan a Terraform Repository

```bash
cd trustlens

# Scan Terraform code
python main.py ../my-terraform-repo ./terraform-findings.json

# View top issues
python -m json.tool terraform-findings.json | grep -A5 "CRITICAL"
```

### Example 2: CI/CD Pipeline Integration

```bash
#!/bin/bash
# scan-security.sh

cd trustlens

# Run TrustLens
python main.py ../repo-to-scan ./findings.json

# Count critical findings
CRITICAL=$(python -c "
import json
with open('findings.json') as f:
    findings = json.load(f)
    count = sum(1 for f in findings if f['severity_raw'] == 'CRITICAL')
    print(count)
")

if [ "$CRITICAL" -gt 0 ]; then
    echo "❌ Found $CRITICAL critical issues"
    exit 1
else
    echo "✓ No critical issues found"
    exit 0
fi
```

### Example 3: Generate HTML Report

```python
# create_report.py
import json
from datetime import datetime

with open('findings.json') as f:
    findings = json.load(f)

html = f"""
<html>
<head>
    <title>TrustLens Security Report</title>
    <style>
        .critical {{ background: #ff4444; color: white; }}
        .high {{ background: #ff8800; color: white; }}
        .medium {{ background: #ffaa00; color: white; }}
        .low {{ background: #ffdd00; }}
    </style>
</head>
<body>
    <h1>TrustLens Security Report</h1>
    <p>Generated: {datetime.now()}</p>
    <p>Total Findings: {len(findings)}</p>
    
    <table border="1">
        <tr>
            <th>Severity</th>
            <th>Tool</th>
            <th>Rule</th>
            <th>Title</th>
            <th>File</th>
        </tr>
"""

for finding in findings:
    severity_class = finding['severity_raw'].lower()
    html += f"""
        <tr class="{severity_class}">
            <td>{finding['severity_raw']}</td>
            <td>{finding['source_tool'].upper()}</td>
            <td>{finding['rule_id']}</td>
            <td>{finding['title']}</td>
            <td>{finding['location']['file']}</td>
        </tr>
    """

html += """
    </table>
</body>
</html>
"""

with open('report.html', 'w') as f:
    f.write(html)

print("Report saved to report.html")
```

Run: `python create_report.py`

### Example 4: Filter and Export Findings

```python
# export_findings.py
import json
import sys

# Load findings
with open('findings.json') as f:
    findings = json.load(f)

# Filter by severity
if len(sys.argv) > 1:
    severity = sys.argv[1].upper()
    findings = [f for f in findings if f['severity_raw'] == severity]

# Filter by tool
if len(sys.argv) > 2:
    tool = sys.argv[2].lower()
    findings = [f for f in findings if f['source_tool'] == tool]

# Filter by file pattern
if len(sys.argv) > 3:
    pattern = sys.argv[3]
    findings = [f for f in findings if pattern in f['location']['file']]

# Export
output = sys.argv[-1] if sys.argv[-1].endswith('.json') else 'filtered.json'
with open(output, 'w') as f:
    json.dump(findings, f, indent=2)

print(f"Exported {len(findings)} findings to {output}")
```

Usage:
```bash
# Export only CRITICAL findings from Semgrep in Python files
python export_findings.py CRITICAL semgrep "*.py" critical-findings.json

# Export all HIGH findings
python export_findings.py HIGH findings_high.json
```

---

## Integration

### GitHub Actions

```yaml
# .github/workflows/security-scan.yml
name: TrustLens Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install TrustLens
        run: |
          cd trustlens
          pip install -r requirements.txt
          pip install checkov trivy semgrep
      
      - name: Run TrustLens
        run: |
          cd trustlens
          python main.py ../ ./findings.json
      
      - name: Upload findings
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-findings
          path: trustlens/findings.json
      
      - name: Check for critical issues
        run: |
          cd trustlens
          python -c "
          import json, sys
          with open('findings.json') as f:
              findings = json.load(f)
              critical = [f for f in findings if f['severity_raw'] == 'CRITICAL']
              if critical:
                  print(f'❌ Found {len(critical)} critical findings')
                  sys.exit(1)
              print('✓ No critical findings')
          "
```

### GitLab CI

```yaml
# .gitlab-ci.yml
security-scan:
  image: python:3.11
  script:
    - cd trustlens
    - pip install -r requirements.txt
    - apt-get update && apt-get install -y checkov trivy
    - pip install semgrep
    - python main.py ../ ./findings.json
  artifacts:
    paths:
      - trustlens/findings.json
    expire_in: 30 days
  allow_failure: true
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Scan') {
            steps {
                sh '''
                    cd trustlens
                    pip install -r requirements.txt
                    python main.py ../ ./findings.json
                '''
            }
        }
        
        stage('Report') {
            steps {
                step([
                    $class: 'JSONSummaryArchiver',
                    jsonFile: 'trustlens/findings.json'
                ])
            }
        }
    }
}
```

---

## Tips & Tricks

### 1. Quick Severity Count

```bash
python -c "
import json
with open('findings.json') as f:
    findings = json.load(f)
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = sum(1 for f in findings if f['severity_raw'] == severity)
        print(f'{severity}: {count}')
"
```

### 2. Find Findings by File

```bash
python -c "
import json
import sys
pattern = sys.argv[1]
with open('findings.json') as f:
    findings = json.load(f)
    for f in findings:
        if pattern in f['location']['file']:
            print(f\"{f['severity_raw']} | {f['source_tool']} | {f['rule_id']}\")
" "*.py"
```

### 3. Trending (Compare Scans)

```python
# compare_scans.py
import json
import sys

def load_findings(filepath):
    with open(filepath) as f:
        return json.load(f)

old = load_findings(sys.argv[1])
new = load_findings(sys.argv[2])

old_ids = {f['finding_id'] for f in old}
new_ids = {f['finding_id'] for f in new}

added = new_ids - old_ids
resolved = old_ids - new_ids

print(f"New issues: {len(added)}")
print(f"Resolved: {len(resolved)}")
print(f"Remaining: {len(new)}")
```

### 4. Bulk Fix Recommendations

```bash
# Extract all SQL injection findings
python -c "
import json
with open('findings.json') as f:
    findings = json.load(f)
    for f in findings:
        if 'sql' in f['rule_id'].lower():
            print(f\"Use parameterized queries instead of string concatenation\")
            print(f\"File: {f['location']['file']}\")
            print(f\"Line: {f['location']['start_line']}\")
            print()
" | sort | uniq
```

### 5. Monitor Specific Rule

```bash
# Watch for new CKV_AWS_* findings over time
python -c "
import json
with open('findings.json') as f:
    findings = json.load(f)
    aws_checks = [f for f in findings if 'CKV_AWS' in f['rule_id']]
    for check_id in sorted(set(f['rule_id'] for f in aws_checks)):
        count = sum(1 for f in aws_checks if f['rule_id'] == check_id)
        print(f'{check_id}: {count}')
"
```

### 6. Performance Profiling

Add timing to your scans:

```python
# main.py modification
import time

start = time.time()
# ... run scanning ...
scan_time = time.time() - start

print(f"Scan completed in {scan_time:.1f} seconds")
```

### 7. Ignore Files/Patterns

Modify scanners to exclude directories:

```python
# In checkov_scanner.py
cmd = [
    "checkov",
    "-d", repo_path,
    "--skip-path", ".git",  # Exclude .git
    "--skip-path", "node_modules",  # Exclude node_modules
    # ...
]
```

---

## Troubleshooting Usage

### Issue: Empty findings.json

**Possible causes**:
1. Scanners not installed
2. No vulnerable files in repo
3. Scanner paths incorrect

**Solution**:
```bash
# Test each scanner individually
checkov -d ./sample_repo --output json
trivy fs ./sample_repo --format json
semgrep --config=p/owasp-top-ten ./sample_repo --json
```

### Issue: Findings seem incomplete

**Solution**: Check if specific scanners failed:
```bash
python main.py ./repo 2>&1 | grep -i "error\|skip"
```

### Issue: Scanning takes too long

**Solution**: 
1. Increase timeout in scanner code
2. Exclude large directories
3. Use parallel processing (advanced)

---

## Performance Benchmarks

Typical scan times on sample_repo/ (3 files):

| Scanner | Time | Files Scanned |
|---------|------|---------------|
| Checkov | 2-4s | 1 (Terraform) |
| Trivy | 3-6s | 1 (requirements) |
| Semgrep | 5-10s | 2 (Python) |
| **Total** | **10-20s** | **4** |

Larger repos (100+ files):
- Add ~2-5 seconds per scanner
- Full scan: 30-60 seconds

---

## Next Steps

1. **Customize Rules**: Modify scanner configs for your needs
2. **Integrate with CI/CD**: Use GitHub Actions/GitLab CI examples
3. **Automate Reports**: Create email/Slack notifications
4. **Historical Tracking**: Store findings in database
5. **Await Step 3**: LLM-powered remediation guidance

Happy scanning! 🔐
