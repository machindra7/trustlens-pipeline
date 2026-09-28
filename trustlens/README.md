# TrustLens — Cloud Security Auditing Framework

A powerful AI-powered security auditing tool that scans cloud repositories for vulnerabilities, misconfigurations, exposed secrets, and compliance violations.

This implementation includes **Step 1 (Scanning)** and **Step 2 (Normalization)** of the TrustLens pipeline.

## Overview

TrustLens runs three industry-standard security scanners on your code repository:

1. **Checkov** - Scans Infrastructure-as-Code (Terraform, Kubernetes, Dockerfile) for misconfigurations
2. **Trivy** - Scans for CVEs in dependencies and container images
3. **Semgrep** - Scans application source code for OWASP Top 10 patterns

All findings are normalized into a unified format (UFM - Unified Finding Model) and deduplicated.

## Project Structure

```
trustlens/
├── scanners/
│   ├── checkov_scanner.py      # Checkov integration
│   ├── trivy_scanner.py        # Trivy integration
│   └── semgrep_scanner.py      # Semgrep integration
├── normalizer/
│   └── normalize.py            # UFM conversion and deduplication
├── models/
│   └── finding.py              # Pydantic models for UFM
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── sample_repo/
│   ├── main.tf                 # Intentionally vulnerable Terraform
│   ├── Dockerfile              # Intentionally vulnerable Dockerfile
│   └── app.py                  # Intentionally vulnerable Python app
└── README.md                   # This file
```

## Installation

### Prerequisites

You need Python 3.11+ and the three security scanners installed:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install scanners (via package managers)
# macOS (Homebrew)
brew install checkov trivy semgrep

# Linux (Ubuntu/Debian)
sudo apt-get install -y python3-pip
pip install checkov
brew install trivy semgrep

# Or using Docker (if you prefer)
# docker run --rm -v $(pwd):/repo bridgecrewio/checkov -d /repo --output json
```

### Verify Scanner Installation

```bash
checkov --version
trivy version
semgrep --version
```

## Usage

### Run the Full Pipeline

```bash
cd trustlens
python main.py
```

This will:
1. **Step 1**: Run all three scanners on `./sample_repo`
2. **Step 2**: Normalize findings into UFM format
3. **Save**: Output to `findings.json` in the project root

### Run on a Custom Repository

```bash
python main.py /path/to/your/repo /path/to/output/findings.json
```

### Example Output

```
==================================================
  TrustLens — Step 1: Scanning
==================================================
[Checkov] Scanning: ./sample_repo ...
[Trivy]   Scanning: ./sample_repo ...
[Semgrep] Scanning: ./sample_repo ...

==================================================
  TrustLens — Step 2: Normalizing
==================================================
[Normalizer] Checkov findings  : 8
[Normalizer] Trivy findings    : 3
[Normalizer] Semgrep findings  : 2
[Normalizer] After dedup       : 11

[Result] 11 unique findings saved to findings.json

  [CRITICAL] CHECKOV | CKV_AWS_19 | S3 encryption disabled         | sample_repo/main.tf
  [HIGH]     CHECKOV | CKV_AWS_18 | S3 logging not enabled         | sample_repo/main.tf
  [HIGH]     SEMGREP | python.sql | SQL injection pattern found    | sample_repo/app.py
  [MEDIUM]   TRIVY   | CVE-2021-44228 | Vulnerable package found  | sample_repo/

TrustLens pipeline completed successfully!
```

## Output Format

The `findings.json` file contains normalized findings in the Unified Finding Model (UFM) format:

```json
[
  {
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
    "code_snippet": "resource \"aws_s3_bucket\" \"bad_bucket\" { ... }",
    "cwe": ["CWE-778"],
    "description": "S3 bucket does not have access logging enabled",
    "timestamp": "2025-01-15T10:30:45.123456"
  }
]
```

## UFM Fields

| Field | Type | Description |
|-------|------|-------------|
| `finding_id` | UUID | Unique identifier for this finding |
| `source_tool` | string | Scanner that found this: `checkov`, `trivy`, `semgrep` |
| `rule_id` | string | Rule identifier (e.g., `CKV_AWS_18`, `CVE-2023-1234`) |
| `title` | string | Human-readable title |
| `severity_raw` | string | Normalized severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `category` | string | Finding category (encryption, iam, secrets, vulnerability, etc.) |
| `resource` | string | Affected resource (optional) |
| `location` | object | File path and line numbers |
| `code_snippet` | string | Relevant code excerpt (optional) |
| `cwe` | array | CWE IDs like `["CWE-778"]` (optional) |
| `description` | string | Detailed description |
| `timestamp` | string | When finding was generated (ISO 8601) |

## Severity Normalization

All scanners use different severity formats. TrustLens normalizes them:

| Standard | Checkov | Trivy | Semgrep |
|----------|---------|-------|---------|
| CRITICAL | - | CRITICAL | CRITICAL |
| HIGH | ERROR, WARNING | HIGH | WARNING |
| MEDIUM | INFO | MEDIUM | INFO |
| LOW | NOTE | LOW | NOTE |

## Sample Vulnerable Files

The `sample_repo/` directory contains intentionally vulnerable files for testing:

### main.tf (Terraform)
- Public S3 bucket without access control
- Security group open to 0.0.0.0/0 (entire internet)
- No encryption on S3 bucket
- No logging enabled
- EC2 instance without encryption
- RDS database with hard-coded password
- KMS key without rotation
- CloudTrail without log validation

### Dockerfile
- Using outdated Python 3.6 base image
- Running as root user
- No HEALTHCHECK instruction
- Hard-coded secrets in environment variables

### app.py (Python)
- SQL injection vulnerabilities
- Hard-coded passwords and API keys
- Insecure deserialization (pickle.loads)
- Use of eval() on user input
- XXE injection vulnerability
- Broken access control
- No authentication checks

## Deduplication Logic

When multiple scanners find the same issue, TrustLens deduplicates based on:
- **rule_id**: The security rule identifier
- **file**: The affected file path
- **resource**: The resource name (if applicable)

This prevents duplicate alerts and provides a cleaner report.

## Error Handling

Each scanner is isolated. If one fails:
- The error is logged
- The pipeline continues with other scanners
- Results are incomplete but functional

This graceful degradation ensures TrustLens is resilient to scanner issues.

## Architecture

### Scanning (Step 1)
```
sample_repo/
    ↓
[Checkov Scanner] → Raw findings (JSON)
[Trivy Scanner]   → Raw findings (JSON)
[Semgrep Scanner] → Raw findings (JSON)
```

### Normalization (Step 2)
```
Raw findings (3 formats)
    ↓
[CheckovNormalizer]   → UFM findings
[TrivyNormalizer]     → UFM findings
[SemgrepNormalizer]   → UFM findings
    ↓
[Deduplication] → Remove duplicates based on rule_id + file + resource
    ↓
[Severity Mapping] → Normalize severity to CRITICAL/HIGH/MEDIUM/LOW
    ↓
findings.json
```

## Next Steps (Future Implementation)

Step 3-6 of TrustLens (not included in this release):

- **Step 3**: AI Explanation (LLM-powered context and remediation guidance)
- **Step 4**: Policy Evaluation (OPA/Rego rules based on business profile)
- **Step 5**: Remediation & Patch Generation
- **Step 6**: Dashboard & API (Web interface for findings)

## Logging

The tool uses Python's standard logging module at INFO level. To increase verbosity:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### Scanner not found
```
[Checkov] checkov not found - skipping Checkov scan
```
**Solution**: Install the scanner (see Installation section)

### No findings detected
1. Verify scanners are installed: `checkov --version`
2. Check repo path is correct and readable
3. Ensure sample files contain actual issues

### JSON parse errors
The tool handles this gracefully - check the logs for details:
```
[Trivy] Failed to parse JSON: ...
```

## Testing

To verify everything is working:

```bash
cd trustlens

# Run on sample vulnerable repository
python main.py ./sample_repo ./findings.json

# Verify output was created
ls -lh findings.json

# Inspect findings
python -m json.tool findings.json | head -50
```

Expected output: 10+ findings with mix of CRITICAL, HIGH, MEDIUM, LOW severity.

## Performance

Typical scan times on sample_repo/:
- **Checkov**: 2-5 seconds
- **Trivy**: 3-8 seconds
- **Semgrep**: 5-10 seconds
- **Total**: 10-23 seconds

Times vary based on:
- Repository size
- Number of files
- System resources
- Scanner configuration

## License

MIT License - Feel free to use and modify

## Support

For issues or questions about TrustLens Step 1 & 2, check the main project documentation.
