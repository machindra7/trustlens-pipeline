# TrustLens Installation & Setup Guide

This guide will help you install and configure TrustLens Step 1 & 2 for cloud security auditing.

## Quick Start (5 minutes)

### 1. Install Python Dependencies

```bash
cd trustlens
pip install -r requirements.txt
```

**Note**: The three security scanners (Checkov, Trivy, Semgrep) must be installed separately.

### 2. Install Security Scanners

#### Option A: macOS (Homebrew)
```bash
brew install checkov trivy semgrep
```

#### Option B: Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip curl

# Install Checkov
pip install --break-system-packages checkov

# Install Trivy
sudo apt-get install -y apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install -y trivy

# Install Semgrep
pip install --break-system-packages semgrep
```

#### Option C: Docker (All-in-One)
If you prefer Docker:

```bash
docker run --rm -v $(pwd):/app trustlens:latest python main.py /app/sample_repo
```

### 3. Verify Installation

```bash
checkov --version
trivy version
semgrep --version
```

You should see version numbers for all three tools.

### 4. Run TrustLens

```bash
# Test with sample vulnerable repository
python main.py ./sample_repo

# Or specify custom repo and output path
python main.py /path/to/your/repo /path/to/findings.json
```

### 5. View Results

```bash
# Pretty-print the JSON findings
python -m json.tool findings.json | less

# Or open in an editor
cat findings.json
```

---

## Detailed Installation

### Prerequisites

- **Python**: 3.11 or higher
- **OS**: macOS, Linux, or Windows (with WSL2)
- **Disk Space**: ~2GB for scanners
- **Network**: Internet access for tool installation

### Step 1: Clone/Download TrustLens

```bash
# If cloning from repository
git clone https://github.com/yourusername/trustlens.git
cd trustlens

# Or if you have a zip file
unzip trustlens.zip
cd trustlens
```

### Step 2: Create Virtual Environment (Optional but Recommended)

For isolated Python dependencies:

```bash
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install TrustLens dependencies
pip install -r requirements.txt
```

### Step 3: Install Individual Scanners

#### Checkov (Infrastructure-as-Code Scanner)

```bash
# Via pip
pip install checkov

# Via Homebrew (macOS)
brew install checkov

# Via Docker
docker run -v /path/to/repo:/repo bridgecrewio/checkov -d /repo --output json
```

Verify:
```bash
checkov --version
```

#### Trivy (Vulnerability Scanner)

```bash
# Via Homebrew (macOS)
brew install trivy

# Via apt (Ubuntu/Debian)
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list
apt-get update && apt-get install trivy

# Via Docker
docker run ghcr.io/aquasecurity/trivy fs /repo
```

Verify:
```bash
trivy version
```

#### Semgrep (SAST - Static Code Analysis)

```bash
# Via pip
pip install semgrep

# Via Homebrew (macOS)
brew install semgrep

# Via Docker
docker run returntocorp/semgrep semgrep --config=p/owasp-top-ten /repo
```

Verify:
```bash
semgrep --version
```

### Step 4: Test Installation

Run the test pipeline with mock data (no scanners required):

```bash
python test_pipeline.py
```

Expected output:
```
==================================================
  TrustLens — Test Pipeline (Mock Data)
==================================================

==================================================
  TrustLens — Step 2: Normalizing
==================================================
[Normalizer] Checkov findings  : 8
[Normalizer] Trivy findings    : 3
[Normalizer] Semgrep findings  : 2
[Normalizer] After dedup       : 13

✓ Pipeline test completed successfully!
```

---

## Configuration

### Environment Variables (Optional)

You can configure TrustLens behavior via environment variables:

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR)
export TRUSTLENS_LOG_LEVEL=INFO

# Scanner timeouts (seconds)
export CHECKOV_TIMEOUT=120
export TRIVY_TIMEOUT=120
export SEMGREP_TIMEOUT=120

# Custom output directory
export TRUSTLENS_OUTPUT_DIR=/path/to/output
```

### Scanner-Specific Configuration

#### Checkov Configuration

Create `.checkov.yaml` in your repo root:

```yaml
---
framework: [terraform, kubernetes, dockerfile, cloudformation]
skip-checks:
  - CKV_AWS_57  # Example: Skip specific checks
```

#### Trivy Configuration

Create `.trivyignore` file:

```
# Ignore specific CVEs
CVE-2021-1234
CVE-2021-5555
```

#### Semgrep Configuration

Rules are loaded from:
- `-config=p/owasp-top-ten` (default in TrustLens)
- Custom rule files: `semgrep --config=/path/to/rules`

---

## Docker Setup (Alternative)

Build a Docker image with all dependencies:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN pip install --no-cache-dir \
    checkov \
    semgrep \
    pydantic==2.5.0 \
    python-dotenv==1.0.0

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
RUN echo "deb https://aquasecurity.github.io/trivy-repo/deb focal main" | tee -a /etc/apt/sources.list.d/trivy.list
RUN apt-get update && apt-get install -y trivy

# Copy TrustLens
WORKDIR /app
COPY trustlens /app

ENTRYPOINT ["python", "main.py"]
```

Build and run:

```bash
docker build -t trustlens:latest .
docker run --rm -v $(pwd)/sample_repo:/repo trustlens:latest /repo
```

---

## Troubleshooting

### "checkov not found"

```bash
# Solution: Install checkov
pip install checkov

# Verify installation
which checkov
checkov --version
```

### "trivy not found"

```bash
# Solution: Install Trivy
# macOS:
brew install trivy

# Linux:
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### "semgrep not found"

```bash
# Solution: Install Semgrep
pip install semgrep

# Verify
semgrep --version
```

### No findings detected

1. Verify scanners are in PATH:
   ```bash
   which checkov trivy semgrep
   ```

2. Test each scanner individually:
   ```bash
   # Test Checkov
   checkov -d sample_repo --output json

   # Test Trivy
   trivy fs sample_repo --format json

   # Test Semgrep
   semgrep --config=p/owasp-top-ten sample_repo --json
   ```

3. Check file permissions:
   ```bash
   ls -la sample_repo/
   # All files should be readable
   ```

### JSON parsing errors

Look at the log output for scanner-specific errors:

```bash
python main.py ./sample_repo 2>&1 | grep -i "error\|warning"
```

### Out of Memory

Large repositories may need more memory. Increase available RAM or use Docker with memory limits:

```bash
docker run --memory=4g trustlens:latest /repo
```

### Permission denied

```bash
# Make script executable
chmod +x main.py

# Or run with python
python main.py ./sample_repo
```

---

## Performance Optimization

### Parallel Execution (Future Enhancement)

Currently, scanners run sequentially. For faster execution, you can modify `main.py` to use multiprocessing:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    checkov_future = executor.submit(checkov.scan, repo_path)
    trivy_future = executor.submit(trivy.scan, repo_path)
    semgrep_future = executor.submit(semgrep.scan, repo_path)
```

### Caching

To avoid re-scanning large repos:

```bash
# Cache directory
mkdir -p ~/.trustlens/cache

# Modify scanners to use cache
# (Implementation depends on scanner API)
```

---

## Uninstallation

### Remove Python Installation

```bash
cd ..
rm -rf trustlens/
pip uninstall pydantic python-dotenv checkov trivy semgrep
```

### Remove Docker Image

```bash
docker rmi trustlens:latest
```

### Remove Homebrew Installations (macOS)

```bash
brew uninstall checkov trivy semgrep
```

---

## Getting Help

### Check Logs

```bash
# Enable debug logging
python main.py ./sample_repo 2>&1 | tee debug.log
```

### Test Scanner Independently

```bash
# Test Checkov
checkov -d ./sample_repo --output json > checkov_out.json

# Test Trivy
trivy fs ./sample_repo --format json > trivy_out.json

# Test Semgrep
semgrep --config=p/owasp-top-ten ./sample_repo --json > semgrep_out.json
```

### Review Documentation

- [Checkov Documentation](https://www.checkov.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Documentation](https://semgrep.dev/docs/)

---

## Next Steps

Once TrustLens is installed and working:

1. **Run on Your Repository**: `python main.py /path/to/your/repo`
2. **Review Findings**: Open `findings.json` in your editor
3. **Integrate with CI/CD**: Add TrustLens to your pipeline
4. **Configure Rules**: Customize which checks to run
5. **Await Step 3**: LLM-powered explanations and remediation guidance

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.9 | 3.11+ |
| RAM | 2GB | 4GB+ |
| Disk Space | 500MB | 2GB |
| CPU Cores | 2 | 4+ |
| Network | Required | Required |

## Known Limitations

- **Scanners run sequentially**: Takes 10-30 seconds total
- **Requires Python 3.9+**: Some older systems may need upgrade
- **Large repos**: Can take 1+ minute for very large codebases
- **Network required**: Must download scanner databases on first run

---

## Support & Contributing

For issues or improvements:
1. Check the troubleshooting section
2. Review scanner documentation
3. Open an issue on GitHub
4. Contribute via pull requests

Happy scanning! 🔒
