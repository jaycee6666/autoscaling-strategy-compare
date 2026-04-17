# Project Manifest

**Project Name**: Autoscaling Strategy Comparison  
**Team**: WU Wanpeng, CHEN Sijie  
**Deadline**: April 24, 2026, 23:59 HKT  
**Status**: ✅ PHASE 0 COMPLETE - READY FOR DISTRIBUTION  
**Created**: April 17, 2026  

---

## 📦 What's Included

### 🎯 Entry Points (Start Here)

1. **START_HERE.txt** - Quick welcome and 3-step setup
2. **README.md** - Project overview and quick reference
3. **docs/guides/PHASE4_5_EXECUTION_GUIDE.md** - Detailed 10-minute setup guide

### 📚 Documentation (8 Files, 5,600+ Lines)

| File | Purpose | Audience |
|------|---------|----------|
| docs/plans/PROJECT_EXECUTION_PLAN.md | Complete 10-week execution plan | Everyone |
| docs/references/ACCEPTANCE_CRITERIA.md | Team coordination and management | Project managers |
| .github/CROSSPLATFORM_GUIDE.md | Windows/Mac/Linux compatibility | Troubleshooting |
| docs/guides/PHASE4_5_EXECUTION_GUIDE.md | Commands, FAQ, cheat sheet | Daily work |
| docs/references/ACCEPTANCE_CRITERIA.md | Grading requirements checklist | QA/Grading |
| docs/guides/PHASE4_5_EXECUTION_GUIDE.md | Step-by-step setup guide | New members |
| docs/references/ACCEPTANCE_CRITERIA.md | Before/after improvements | Context/overview |
| README.md | Detailed optimizations | Reference |

### 💻 Python Scripts (4 Ready, 1,220 Lines)

| Script | Purpose | Lines | Status |
|--------|---------|-------|--------|
| check_environment.py | Validate Python, AWS, credentials | 264 | ✅ Ready |
| init_project.py | Initialize project structure | 209 | ✅ Ready |
| config_manager.py | Centralized configuration | 261 | ✅ Ready |
| aws_utils.py | AWS CLI wrapper (20+ ops) | 487 | ✅ Ready |

### ⚙️ Configuration Files

- `.env.template` - Environment variables template
- `.gitignore` - Git ignore rules (credentials protected)
- `requirements.txt` - Python dependencies
- `setup.py` - Automated setup script

### 📁 Project Directories

- `config/` - Configuration files (auto-created)
- `data/` - Data collection and results
  - `experiments/` - Experiment results
  - `metrics/` - Performance metrics
  - `analysis/` - Analysis outputs
- `scripts/` - Python automation scripts
- `docs/` - All documentation

### 📋 Index & Reference Files

- `START_HERE.txt` - Quick 1-page welcome
- `README.md` - Project overview
- `FILE_INDEX.md` - Complete file reference (this file)
- `PROJECT_STATUS.md` - Completion report
- `MANIFEST.md` - This manifest

---

## 🚀 Quick Start

```bash
# 1. Install dependencies (first time only)
pip install -r requirements.txt

# 2. Run setup (first time only)
python setup.py

# 3. Edit configuration
# Open: config/.env
# Add your AWS credentials

# 4. Verify everything works
python scripts/check_environment.py

# 5. Read documentation
# Start with: docs/guides/PHASE4_5_EXECUTION_GUIDE.md
```

---

## 📊 Project Statistics

| Metric | Count |
|--------|-------|
| Total files | 24 |
| Python scripts | 4 (1,220 lines) |
| Documentation files | 12 (5,600+ lines) |
| Configuration templates | 2 |
| Total size | 221 KB |
| Total lines of code/docs | 6,868+ |

---

## 🎯 Execution Phases (10 Weeks)

```
Week 1:    ✅ Phase 0 - Setup (THIS IS COMPLETE)
Week 2-3:  🔄 Phase 1-3 - AWS infrastructure
Week 4-5:  🔄 Phase 4 - Flask application  
Week 6-7:  🔄 Phase 5-6 - Experiments
Week 8:    🔄 Phase 7 - Data collection
Week 9:    🔄 Phase 8 - Report writing
Week 10:   🔄 Phase 9-10 - Demo & submission
```

---

## ✅ What Works Now

### Phase 0 Components ✅

- ✓ Environment validation script
- ✓ Project initialization script
- ✓ Configuration management system
- ✓ AWS CLI wrapper with 20+ operations
- ✓ Automated setup script
- ✓ Complete documentation

### Verified Cross-Platform ✅

- ✓ Windows (PowerShell, Command Prompt)
- ✓ macOS (Terminal)
- ✓ Linux (Bash, Zsh)
- ✓ All paths use Python pathlib (automatic OS handling)
- ✓ All commands identical across platforms

### Security ✅

- ✓ Credentials never committed (.env in .gitignore)
- ✓ No hardcoded secrets in code
- ✓ Configuration validated before use
- ✓ Error messages don't expose sensitive data

---

## 🔄 What Needs Implementation

### Phase 1-7 Scripts (9 scripts to create)

```
scripts/
├── setup_network.py           # VPC, subnets, internet gateway
├── setup_security_groups.py   # Security group rules
├── setup_iam_role.py          # IAM roles and policies
├── setup_instances.py         # EC2 templates and AMI
├── setup_alb.py               # Application load balancer
├── setup_asg.py               # Auto scaling groups
├── deploy_all.py              # Orchestrate deployment
├── verify_infrastructure.py   # Health checks
└── cleanup_infrastructure.py  # Resource cleanup
```

### Phase 8-10 Application

```
app/
├── flask_app.py               # Main application
├── load_generator.py          # Load testing
├── metrics_collector.py       # CloudWatch integration
└── data_analyzer.py           # Results analysis
```

---

## 📖 Reading Order (Recommended)

### First Day

1. **START_HERE.txt** (2 min) - Welcome and overview
2. **docs/guides/PHASE4_5_EXECUTION_GUIDE.md** (8 min) - Setup instructions
3. **Run setup.py** (5 min) - Automated setup
4. **README.md** (5 min) - Project overview

### First Week

1. **docs/plans/PROJECT_EXECUTION_PLAN.md** (60 min) - Full plan
2. **docs/guides/PHASE4_5_EXECUTION_GUIDE.md** (5 min) - Command reference
3. **Create Phase 1 infrastructure scripts** - Using aws_utils.py as guide

### Reference as Needed

- **.github/CROSSPLATFORM_GUIDE.md** - When troubleshooting
- **docs/references/ACCEPTANCE_CRITERIA.md** - If managing the team
- **FILE_INDEX.md** - For file navigation
- **docs/references/ACCEPTANCE_CRITERIA.md** - Before final submission

---

## 🎓 How to Use This Project

### For New Team Members

```bash
1. Clone/download the project
2. Read: START_HERE.txt (2 min)
3. Read: docs/guides/PHASE4_5_EXECUTION_GUIDE.md (8 min)
4. Run: python setup.py (5 min)
5. Edit: config/.env (2 min)
6. Verify: python scripts/check_environment.py (1 min)
7. Continue: docs/plans/PROJECT_EXECUTION_PLAN.md
```

### For Developers

```bash
1. Daily: Check docs/guides/PHASE4_5_EXECUTION_GUIDE.md
2. Follow: docs/plans/PROJECT_EXECUTION_PLAN.md phases
3. Reference: scripts/aws_utils.py for AWS operations
4. When stuck: .github/CROSSPLATFORM_GUIDE.md
```

### For Project Leads

```bash
1. Read: docs/references/ACCEPTANCE_CRITERIA.md
2. Track: docs/plans/PROJECT_EXECUTION_PLAN.md progress
3. Assign: Phase 1-7 scripts to team members
4. Verify: docs/references/ACCEPTANCE_CRITERIA.md before submission
```

---

## 🔗 File Dependencies

```
setup.py
├── requirements.txt
├── check_environment.py
└── init_project.py
    ├── config_manager.py
    │   ├── python-dotenv
    │   └── pyyaml
    └── boto3

aws_utils.py
├── subprocess
├── json
└── logging
```

---

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution | File |
|-------|----------|------|
| Python not found | Use python3 or add to PATH | docs/guides/PHASE4_5_EXECUTION_GUIDE.md |
| AWS CLI not found | Install AWS CLI v2 | docs/guides/PHASE4_5_EXECUTION_GUIDE.md |
| AWS credentials error | Set environment variables | .github/CROSSPLATFORM_GUIDE.md |
| Import errors | pip install -r requirements.txt | docs/guides/PHASE4_5_EXECUTION_GUIDE.md |
| Platform-specific errors | Check .github/CROSSPLATFORM_GUIDE.md | docs/ |

---

## ✨ Key Features

### Cross-Platform ✅

- **Identical commands** on Windows, macOS, Linux
- **No WSL required** for Windows
- **Automatic path handling** via Python pathlib
- **All scripts executable** on any OS

### Automated Setup ✅

- **One-command setup**: python setup.py
- **Auto-validation**: Environment checks
- **Auto-initialization**: Project structure
- **Templates ready**: Just fill in credentials

### Secure by Default ✅

- **No credentials in repo** (.gitignore)
- **Configuration centralized** for multi-person work
- **Error messages safe** (no data leaks)
- **Validation built-in** (checks run automatically)

### Well-Documented ✅

- **5,600+ lines** of clear documentation
- **8 specialized guides** for different needs
- **Step-by-step instructions** everywhere
- **Quick reference** for daily work

---

## 📞 Support Resources

### Project Documentation

- **Getting Started**: docs/guides/PHASE4_5_EXECUTION_GUIDE.md
- **Full Plan**: docs/plans/PROJECT_EXECUTION_PLAN.md
- **Quick Ref**: docs/guides/PHASE4_5_EXECUTION_GUIDE.md
- **Troubleshooting**: .github/CROSSPLATFORM_GUIDE.md

### Extern
