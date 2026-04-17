# Autoscaling Strategy Comparison Project

**Project**: Comparative Analysis of Autoscaling Strategies: CPU Utilization vs. Request Rate

**Team**: CHEN Sijie (jaycee6666)  
**Deadline**: April 24, 2026, 23:59 HKT  
**Course**: CS5296 Cloud Computing  
**Status**: Phase 4-6 Complete ✅ | Phase 7 (Report & Demo) - Next

---

## 📖 Documentation Guide

### 🎯 Start Here (Choose One)
- **`docs/guides/MASTER_EXECUTION_GUIDE.md`** - How to run all experiments (Steps 2-4)
- **`docs/guides/PHASE4_5_EXECUTION_GUIDE.md`** - Detailed guide for Phase 4-5 experiments
- **`docs/`** - Organized reference documentation by type (plans, guides, references)

### GitHub Setup
- **`.github/`** - GitHub repository and CI/CD setup guides

---

## 🚀 Quick Commands

```bash
# Activate environment
venv\Scripts\activate.bat  # Windows
source venv/bin/activate  # Mac/Linux

# Verify infrastructure
python experiments/01_verify_infrastructure.py

# Run all experiments (CPU + Request-Rate)
python run_all_experiments.py

# Or run individually (30 min each)
python experiments/02_run_cpu_experiment.py
python experiments/03_run_request_rate_experiment.py
python experiments/04_aggregate_results.py
```

---

## 📁 Directory Structure

```
autoscaling-strategy-compare/
├── README.md                           # Project overview (you are here)
├── requirements.txt                    # Python dependencies
│
├── experiments/                        # Phase 4-6 experiment scripts
│   ├── 01_verify_infrastructure.py     # Pre-check
│   ├── 02_run_cpu_experiment.py        # CPU strategy (30 min)
│   ├── 03_run_request_rate_experiment.py # Request-rate strategy (30 min)
│   ├── 04_aggregate_results.py         # Compare results
│   ├── 06_analyze_results.py           # Phase 6 analysis
│   └── results/                        # Experiment outputs (JSON/CSV)
│
├── apps/                               # Flask test application
├── deployment/                         # AWS deployment scripts
├── infrastructure/                     # AWS infrastructure configs
├── scripts/                            # Utility scripts
├── config/                             # Configuration files
│
├── docs/                               # 📚 Organized documentation
│   ├── plans/                          # Project plans & roadmaps (Phases 1-6)
│   │   ├── PROJECT_EXECUTION_PLAN.md
│   │   ├── PHASE1_IMPLEMENTATION_PLAN.md
│   │   ├── PHASE2B_APPLICATION_DEVELOPMENT.md
│   │   ├── PHASE3_DEPLOYMENT.md
│   │   ├── PHASE4_5_EXECUTION_PLAN.md
│   │   ├── PHASE6_ANALYSIS_PLAN.md
│   │   ├── PLANS_INDEX.md
│   │   └── PROJECT_EXECUTION_ROADMAP.md
│   ├── guides/                         # Step-by-step guides & quick starts
│   │   ├── MASTER_EXECUTION_GUIDE.md   # ⭐ How to run experiments
│   │   ├── PHASE1_DEPLOYMENT_GUIDE.md
│   │   ├── PHASE3_DEPLOYMENT_GUIDE.md
│   │   ├── PHASE4_5_EXECUTION_GUIDE.md
│   │   ├── FINAL_EXECUTION_GUIDE.md
│   │   └── references/                     # Indexes, manifests, criteria
│   │       ├── FILE_INDEX.md
│   │       ├── MANIFEST.md
│   │       └── ACCEPTANCE_CRITERIA.md
│
├── .github/                            # 🐙 GitHub setup & Cross-platform Guide
│   ├── GITHUB_QUICK_SETUP.md           # GitHub repository config
│   ├── HOW_TO_UPLOAD_TO_GITHUB.md      # Upload instructions
│   ├── READY_FOR_GITHUB.md             # Pre-push checklist
│   └── CROSSPLATFORM_GUIDE.md          # Windows/Mac/Linux compatibility guide
│
└── venv/                               # Python virtual environment
```

---

## 🧪 Experiment Progress

**✅ Phase 4-6 Execution Scripts Ready** (April 18, 2026)

- All experiment code is complete and tested
- Infrastructure deployment scripts available
- Ready to execute: CPU and Request-Rate autoscaling strategies
- Results will be generated during Phase 4-6 execution

---

## 🔧 Prerequisites

- Python 3.9+ (upgrade to 3.10+ recommended)
- AWS credentials configured
- Virtual environment: `venv\Scripts\activate.bat` (Windows) or `. venv/bin/activate` (Mac/Linux)
