# TrustLens - Complete Project Index

## 📋 Quick Navigation

### Getting Started
- **New to TrustLens?** → Start with [README.md](README.md)
- **Want to install?** → See [INSTALLATION.md](INSTALLATION.md)
- **Want to use it?** → Check [USAGE.md](USAGE.md)
- **Want overview?** → Read [SUMMARY.md](SUMMARY.md)
- **This is?** → You're reading [INDEX.md](INDEX.md)

---

## 📁 File Structure & Descriptions

### Documentation Files

| File | Size | Purpose | Read Time |
|------|------|---------|-----------|
| [README.md](README.md) | 250 lines | Project overview, features, sample output | 5 min |
| [INSTALLATION.md](INSTALLATION.md) | 400 lines | Detailed setup, troubleshooting, Docker | 10 min |
| [USAGE.md](USAGE.md) | 450 lines | Advanced features, examples, integration | 15 min |
| [SUMMARY.md](SUMMARY.md) | 300 lines | Architecture, design decisions, benchmarks | 10 min |
| [INDEX.md](INDEX.md) | This file | Navigation guide for entire project | 5 min |

### Core Python Files

| File | Lines | Purpose |
|------|-------|---------|
| **Entry Point** | | |
| [main.py](main.py) | 130 | Main pipeline orchestrator |
| [test_pipeline.py](test_pipeline.py) | 140 | Test pipeline with mock data |
| **Data Models** | | |
| [models/finding.py](models/finding.py) | 110 | Pydantic UFM models |
| **Scanners** | | |
| [scanners/checkov_scanner.py](scanners/checkov_scanner.py) | 70 | Checkov integration |
| [scanners/trivy_scanner.py](scanners/trivy_scanner.py) | 65 | Trivy integration |
| [scanners/semgrep_scanner.py](scanners/semgrep_scanner.py) | 70 | Semgrep integration |
| **Normalization** | | |
| [normalizer/normalize.py](normalizer/normalize.py) | 290 | UFM conversion & deduplication |

### Configuration Files

| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python dependencies (Pydantic, python-dotenv) |
| [sample_repo/requirements.txt](sample_repo/requirements.txt) | Intentionally vulnerable dependencies |

### Sample Vulnerable Files

| File | Type | Vulnerabilities |
|------|------|-----------------|
| [sample_repo/main.tf](sample_repo/main.tf) | Terraform | 8+ infrastructure misconfigs |
| [sample_repo/Dockerfile](sample_repo/Dockerfile) | Container | 3-5 container security issues |
| [sample_repo/app.py](sample_repo/app.py) | Python | 7+ code vulnerabilities |

### Package Structure

```
trustlens/
├── models/
│   ├── __init__.py              # Package marker
│   └── finding.py               # Pydantic models for UFM
├── scanners/
│   ├── __init__.py              # Package marker
│   ├── checkov_scanner.py       # Checkov wrapper
│   ├── trivy_scanner.py         # Trivy wrapper
│   └── semgrep_scanner.py       # Semgrep wrapper
├── normalizer/
│   ├── __init__.py              # Package marker
│   └── normalize.py             # Normalization logic
└── sample_repo/
    ├── main.tf                  # Vulnerable Terraform
    ├── Dockerfile               # Vulnerable container
    ├── app.py                   # Vulnerable Python
    └── requirements.txt         # Vulnerable dependencies
```

---

## 🚀 Quick Start Paths

### Path 1: I Just Want to Try It (5 minutes)

```bash
cd trustlens

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Test with mock data (no scanners needed)
python test_pipeline.py

# 3. View results
cat findings_test.json
```

→ **Expected**: 13 findings in `findings_test.json`

### Path 2: I Want Full Installation (15 minutes)

```bash
# 1. Read installation guide
cat INSTALLATION.md

# 2. Install scanners (follow INSTALLATION.md)
pip install checkov trivy semgrep

# 3. Run full pipeline
python main.py ./sample_repo

# 4. Inspect findings
python -m json.tool findings.json | head -50
```

→ **Expected**: findings.json with mix of CRITICAL/HIGH/MEDIUM/LOW

### Path 3: I Want to Integrate with CI/CD (20 minutes)

```bash
# 1. Read integration examples
grep -A20 "GitHub Actions" USAGE.md

# 2. Copy example workflow
# 3. Customize for your repository
# 4. Add to .github/workflows/scan.yml
# 5. Test on next commit
```

→ **Expected**: Security scan runs on every push

### Path 4: I Want to Understand the Code (30 minutes)

```bash
# 1. Read SUMMARY.md for architecture
# 2. Read USAGE.md for advanced features
# 3. Review finding.py for data model
# 4. Review normalize.py for logic
# 5. Try test_pipeline.py with modifications
```

→ **Expected**: Understanding of entire pipeline

---

## 📖 Documentation Reading Order

### For First-Time Users
1. **README.md** (5 min) - What is TrustLens?
2. **INSTALLATION.md** (10 min) - How to set up?
3. **test_pipeline.py** (1 min) - Run this first!
4. **USAGE.md** (15 min) - How to use it?

### For Developers
1. **SUMMARY.md** (10 min) - Architecture overview
2. **main.py** (5 min) - Entry point walkthrough
3. **models/finding.py** (5 min) - Data structures
4. **normalizer/normalize.py** (10 min) - Core logic
5. **scanners/*.py** (5 min) - Scanner wrappers

### For DevOps/CI-CD
1. **INSTALLATION.md** - Setup section
2. **USAGE.md** - Integration section
3. **GitHub Actions example** in USAGE.md
4. **GitLab CI example** in USAGE.md

### For Security Teams
1. **README.md** - Overview
2. **USAGE.md** - Examples section
3. **sample_repo/** - Review vulnerabilities
4. **findings.json** format in SUMMARY.md

---

## 🔍 Finding What You Need

### By Task

**"I want to install TrustLens"**
→ [INSTALLATION.md](INSTALLATION.md) - Full setup guide

**"I want to run a scan"**
→ [USAGE.md](USAGE.md) - Basic usage section or README Quick Start

**"I want to integrate with GitHub"**
→ [USAGE.md](USAGE.md) - GitHub Actions section

**"I want to understand the code"**
→ [SUMMARY.md](SUMMARY.md) - Architecture section

**"I got an error"**
→ [INSTALLATION.md](INSTALLATION.md) - Troubleshooting section

**"I want to see what's in the code"**
→ [SUMMARY.md](SUMMARY.md) - File descriptions section

**"I want to test without scanners"**
→ Run `python test_pipeline.py` or see README Quick Start

### By Problem

| Problem | Solution | Documentation |
|---------|----------|-----------------|
| Scanner not found | Install via brew/pip | INSTALLATION.md > Installation |
| Empty results | Use sample_repo or check paths | USAGE.md > Troubleshooting |
| Want more details | Check log level or run test_pipeline.py | INSTALLATION.md > Configuration |
| Need faster scans | Increase timeouts or parallelize | USAGE.md > Performance Optimization |
| Want HTML report | Use example script in USAGE.md | USAGE.md > Real-World Examples |

---

## 💡 Key Concepts

### Unified Finding Model (UFM)
The standard format for all security findings. All three scanners output different formats - UFM unifies them.

**Location**: [models/finding.py](models/finding.py)
**Read**: [SUMMARY.md](SUMMARY.md) - "What Was Built" section

### Step 1: Scanning
Run three security scanners on a repository:
- Checkov (infrastructure)
- Trivy (vulnerabilities)
- Semgrep (code patterns)

**Code**: [scanners/](scanners/) directory
**Details**: [README.md](README.md) - "How It Works"

### Step 2: Normalization
Convert scanner output to UFM format, normalize severity, deduplicate findings.

**Code**: [normalizer/normalize.py](normalizer/normalize.py)
**Details**: [SUMMARY.md](SUMMARY.md) - "Step 2: Normalization"

---

## 🎯 Common Use Cases

### Use Case 1: One-Time Security Audit
```bash
python main.py /path/to/repo findings.json
# Review findings.json
```

**Read**: [README.md](README.md) - Quick Start

### Use Case 2: CI/CD Integration
Add to your pipeline to scan on every commit.

**Read**: [USAGE.md](USAGE.md) - Integration section

### Use Case 3: Automated Reporting
Generate reports and send to security team.

**Read**: [USAGE.md](USAGE.md) - Real-World Examples

### Use Case 4: Compliance Tracking
Store findings over time, track remediation progress.

**Read**: [USAGE.md](USAGE.md) - Bulk operations section

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Python Files | 8 |
| Lines of Code | ~1,600 |
| Lines of Docs | ~1,100 |
| Scanners | 3 |
| UFM Fields | 11 |
| Severity Levels | 4 |
| Sample Vulnerabilities | 20+ |
| Test Coverage | Step 1 & 2 |

---

## 🔗 Dependencies

### Python (in requirements.txt)
- pydantic==2.5.0 - Data validation
- python-dotenv==1.0.0 - Environment variables

### External Tools (install separately)
- Checkov - Infrastructure scanning
- Trivy - Vulnerability scanning
- Semgrep - Code pattern matching

**Details**: [INSTALLATION.md](INSTALLATION.md) - Scanner Installation

---

## 📝 Implementation Details

### What's Implemented (Step 1 & 2)
✅ Scanning with 3 scanners
✅ Normalization to UFM
✅ Deduplication
✅ Severity mapping
✅ Error handling
✅ JSON export
✅ Test pipeline

### What's Not Implemented (Steps 3-6)
❌ LLM explanations (Step 3)
❌ OPA policy evaluation (Step 3)
❌ Remediation patches (Step 5)
❌ Compliance mapping (Step 5)
❌ Dashboard/API (Step 6)

**Details**: [SUMMARY.md](SUMMARY.md) - "Limitations"

---

## 🛠️ Customization

### To Add a New Scanner
1. Create `scanners/new_scanner.py` (copy template from existing scanner)
2. Implement `.scan()` method
3. Implement `._extract_findings()` method
4. Add to `main.py` import and call
5. Update `normalizer/normalize.py` with normalizer class

**Guide**: [USAGE.md](USAGE.md) - Configuration section

### To Change Severity Mapping
Edit `SeverityMapper` class in [normalizer/normalize.py](normalizer/normalize.py)

**Details**: [SUMMARY.md](SUMMARY.md) - "Severity Normalization"

### To Filter Findings
Modify scanner commands or add filtering after normalization.

**Examples**: [USAGE.md](USAGE.md) - Real-World Examples

---

## 🆘 Getting Help

### Within This Project
- **Setup Help**: [INSTALLATION.md](INSTALLATION.md) > Troubleshooting
- **Usage Help**: [USAGE.md](USAGE.md) > Troubleshooting
- **Code Understanding**: [SUMMARY.md](SUMMARY.md) > Architecture
- **Quick Check**: Run `python test_pipeline.py`

### External Resources
- [Checkov Docs](https://www.checkov.io/)
- [Trivy Docs](https://aquasecurity.github.io/trivy/)
- [Semgrep Docs](https://semgrep.dev/docs/)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Verify Installation
```bash
# Check all dependencies
python test_pipeline.py
# Check scanners
checkov --version && trivy version && semgrep --version
```

---

## 📈 Next Steps

### Short Term (This Week)
1. Install TrustLens (INSTALLATION.md)
2. Run test pipeline (test_pipeline.py)
3. Scan your repository (main.py)
4. Review findings (findings.json)

### Medium Term (This Month)
1. Integrate with CI/CD (USAGE.md - Integration)
2. Customize rules (INSTALLATION.md - Configuration)
3. Generate reports (USAGE.md - Real-World Examples)
4. Track metrics (USAGE.md - Tips & Tricks)

### Long Term (This Quarter)
1. Await Step 3 - LLM explanations
2. Implement Step 5 - Remediation patches
3. Deploy Step 6 - Dashboard/API
4. Build compliance reporting

---

## 📌 Important Reminders

- **Scanners Must Be Installed** - See INSTALLATION.md
- **Test Without Scanners** - Run `python test_pipeline.py`
- **Read Documentation** - Start with README.md
- **Check Troubleshooting** - See INSTALLATION.md > Troubleshooting
- **Graceful Errors** - Pipeline continues if a scanner fails

---

## ✅ Verification Checklist

Before considering installation complete:

- [ ] `pip install -r requirements.txt` succeeds
- [ ] `python test_pipeline.py` produces findings_test.json
- [ ] `findings_test.json` contains 13+ findings
- [ ] `checkov --version` works (optional, for full pipeline)
- [ ] `trivy version` works (optional, for full pipeline)
- [ ] `semgrep --version` works (optional, for full pipeline)
- [ ] `python main.py ./sample_repo` produces findings.json
- [ ] `findings.json` contains findings in UFM format

---

## 🎓 Learning Resources

### Understand the Code
1. Read [SUMMARY.md](SUMMARY.md) - Architecture section
2. Review [models/finding.py](models/finding.py) - 110 lines, well-commented
3. Review [normalizer/normalize.py](normalizer/normalize.py) - 290 lines, all logic
4. Review [main.py](main.py) - 130 lines, orchestration

### Understand the Tools
- [Checkov](https://www.checkov.io/) - Infrastructure scanning
- [Trivy](https://aquasecurity.github.io/trivy/) - Vulnerability DB
- [Semgrep](https://semgrep.dev/) - Code patterns
- [Pydantic](https://docs.pydantic.dev/) - Data validation

### See Examples
1. Run `python test_pipeline.py` - See mock pipeline
2. Read [USAGE.md](USAGE.md) - Real-World Examples
3. Check [sample_repo/](sample_repo/) - Vulnerable code

---

## 📞 Support Summary

| Question | Answer | Documentation |
|----------|--------|-----------------|
| What is this? | Cloud security scanner | README.md |
| How to install? | Follow steps | INSTALLATION.md |
| How to use? | Run python main.py | README.md or USAGE.md |
| How does it work? | 3 scanners → UFM → JSON | SUMMARY.md |
| Got an error? | Check troubleshooting | INSTALLATION.md |
| Want more features? | See future steps | SUMMARY.md |

---

## 🎉 You're Ready!

You have everything you need:
- ✅ Complete Python implementation
- ✅ Three vulnerable test files
- ✅ Comprehensive documentation
- ✅ Test pipeline that works without scanners
- ✅ Examples for CI/CD integration

**Next Step**: Start with [README.md](README.md) or run `python test_pipeline.py`

Happy scanning! 🔐
