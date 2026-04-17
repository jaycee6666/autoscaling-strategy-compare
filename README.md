# Autoscaling Strategy Comparison Project

**Project**: Comparative Analysis of Autoscaling Strategies: CPU Utilization vs. Request Rate

**Team**: CHEN Sijie (jaycee6666)  
**Deadline**: April 24, 2026, 23:59 HKT  
**Course**: CS5296 Cloud Computing  
**Status**: Phase 4-6 Complete ✅ | Phase 7 (Report & Demo) - Next

---

## 📖 Documentation Guide

### 🎯 Start Here (Choose One)
- **`EXPERIMENTS_COMPLETED.md`** - Summary of Phase 4-6 results with real AWS metrics
- **`MASTER_EXECUTION_GUIDE.md`** - How to run all experiments (Steps 2-4)
- **`docs/`** - Detailed reference documentation (deployment, troubleshooting, etc.)

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
├── EXPERIMENTS_COMPLETED.md            # ⭐ Latest results (Phase 4-6)
├── MASTER_EXECUTION_GUIDE.md           # ⭐ How to run experiments
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
├── docs/                               # 📚 Detailed documentation
│   ├── PHASE1_DEPLOYMENT_GUIDE.md      # Infrastructure setup
│   ├── FINAL_READINESS_REPORT.md       # Pre-execution checklist
│   ├── STEP2_DIAGNOSIS_AND_FIX.md      # Troubleshooting
│   ├── SESSION_SUMMARY.md              # Work history
│   └── ... (more reference docs)
│
├── .github/                            # 🐙 GitHub setup
│   ├── GITHUB_QUICK_SETUP.md           # GitHub repository config
│   ├── HOW_TO_UPLOAD_TO_GITHUB.md      # Upload instructions
│   └── READY_FOR_GITHUB.md             # Pre-push checklist
│
└── venv/                               # Python virtual environment
```

---

## 🧪 Experiment Results

**✅ Phase 4-6 Complete** (April 17, 2026)

- **CPU Strategy**: 92.95% success rate, 970.6ms avg response time
- **Request-Rate Strategy**: 93.74% success rate, 959.9ms avg response time
- **Winner**: Request-Rate Strategy (12.7% better P95 latency, 3.6% lower cost)

See `EXPERIMENTS_COMPLETED.md` for full details with real AWS CloudWatch metrics.

---

## 🔧 Prerequisites

- Python 3.9+ (upgrade to 3.10+ recommended)
- AWS credentials configured
- Virtual environment: `venv\Scripts\activate.bat` (Windows) or `. venv/bin/activate` (Mac/Linux)
