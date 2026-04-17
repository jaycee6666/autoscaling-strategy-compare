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

## 🔧 Prerequisites & Setup

**Before running experiments, complete these one-time setup steps:**

### Step 1: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### Step 2: Run Setup Script
```bash
# One-command environment initialization
python setup.py
```

This script will:
- Install all dependencies from `requirements.txt`
- Configure AWS credentials
- Verify infrastructure connectivity
- Set up experiment directories

### Step 3: Verify Infrastructure
```bash
# Confirm ALB and ASG are healthy
python experiments/01_verify_infrastructure.py
```

**Expected output**: JSON report confirming ALB and both ASGs are operational

### Step 4: Troubleshooting

If you encounter issues during setup:
- **Windows path errors**: Use forward slashes in commands or check `.github/CROSSPLATFORM_GUIDE.md`
- **AWS credentials not found**: Run `aws configure` or check `~/.aws/credentials`
- **Python version mismatch**: Ensure Python 3.9+ is installed (`python --version`)
- **Virtual environment issues**: See `.github/CROSSPLATFORM_GUIDE.md` for platform-specific solutions

For detailed cross-platform troubleshooting, see **`.github/CROSSPLATFORM_GUIDE.md`**

---

## 🚀 Running Experiments

Once setup is complete, you can run experiments in three ways:

### Option 1: Run All Experiments (One Command)
```bash
python run_all_experiments.py
```

**Total time**: ~75 minutes (CPU strategy: 30 min + Request-Rate strategy: 30 min + Aggregation: 10 min)

### Option 2: Run Experiments Individually
```bash
# Verify infrastructure before starting
python experiments/01_verify_infrastructure.py

# Run CPU utilization strategy experiment (30 min)
python experiments/02_run_cpu_experiment.py

# Run request-rate strategy experiment (30 min)
python experiments/03_run_request_rate_experiment.py

# Aggregate and compare results (10 min)
python experiments/04_aggregate_results.py
```

### Option 3: Run Custom Experiments
For advanced customization, see `docs/guides/MASTER_EXECUTION_GUIDE.md`

### Output
- `experiments/results/cpu_strategy_metrics.json` - CPU strategy results
- `experiments/results/request_rate_experiment_metrics.json` - Request-rate strategy results
- `experiments/results/comparison_report.json` - Winner analysis
- `experiments/results/metrics_comparison.csv` - Spreadsheet format

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
