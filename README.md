# Autoscaling Strategy Comparison Project

**Project**: Comparative Analysis of Autoscaling Strategies: Resource-Based CPU Utilization vs. Workload-Based Request Rate

**Team**: WU Wanpeng, CHEN Sijie

**Deadline**: April 24, 2026, 23:59 HKT

**Course**: CS5296 Cloud Computing

---

## 📋 Quick Start

### For First-Time Setup (All Platforms)

```bash
# 1. Check your environment (Python, AWS CLI, etc.)
python scripts/check_environment.py

# 2. Initialize the project
python scripts/init_project.py

# 3. Configure AWS credentials
# Edit config/.env with your AWS access key and secret key

# 4. Deploy infrastructure
python scripts/deploy_all.py
```

### Accessing Documentation

- **Start here**: `docs/QUICK_REFERENCE.md` - Quick lookup and command cheat sheet
- **Full plan**: `docs/PROJECT_EXECUTION_PLAN.md` - Phase-by-phase execution guide
- **Cross-platform**: `docs/CROSSPLATFORM_GUIDE.md` - Troubleshooting and platform-specific issues
- **Team lead**: `docs/ADMIN_GUIDE.md` - Coordination and management guide
- **Grading**: `docs/ACCEPTANCE_CRITERIA.md` - What the course expects

---

## 📁 Directory Structure

```
autoscaling-strategy-compare/
├── README.md                          # This file
├── docs/                              # All documentation
│   ├── PROJECT_EXECUTION_PLAN.md     # Detailed execution phases
│   ├── CROSSPLATFORM_GUIDE.md        # Windows/Mac/Linux compatibility
│   ├── QUICK_REFERENCE.md            # Quick lookup guide
│   ├── ADMIN_GUIDE.md                # Team management
│   ├── OPTIMIZATION_SUMMARY.md       # Before/after improvements
│   └── ACCEPTANCE_CRITERIA.md        # Grading requirements
├── scripts/                           # Python automation scripts
│   ├── check_environment.py          # Environment validation (Phase 0)
│   ├── init_project.py               # Project initialization (Phase 0)
│   ├── config_manager.py             # Configuration management (Phase 0)
│   ├── aws_utils.py                  # AWS CLI wrapper (Phase 0)
│   ├── setup_*.py                    # Infrastructure setup scripts (Phase 1-5)
│   ├── deploy_all.py                 # One-click deployment (Phase 6)
│   └── verify_deployment.py          # Deployment verification (Phase 6)
├── config/                            # Configuration files
│   ├── .env.template                 # Environment variables template
│   ├── .env                          # Actual configuration (git-ignored)
│   └── config.yaml                   # Project configuration
├── data/                              # Data collection and analysis
│   ├── experiments/                  # Experiment results
│   ├── metrics/                      # Performance metrics
│   └── analysis/                     # Analysis outputs
└── .gitignore                         # Git ignore rules
```

---

## 🚀 Execution Phases (10 Weeks)

| Week | Phase | What | Lead |
|------|-------|------|------|
| 1 | Phase 0 | Setup & infrastructure foundation | WU Wanpeng |
| 2-3 | Phase 1-3 | AWS infrastructure deployment | Both |
| 4-5 | Phase 4 | Flask application development | CHEN Sijie |
| 6-7 | Phase 5-6 | Experiment execution | Both |
| 8 | Phase 7 | Data collection & analysis | Both |
| 9 | Phase 8 | Report writing | Both |
| 10 | Phase 9-10 | Demo video & final submission | Both |

---

## ✅ Key Features

✅ **Cross-Platform**: Windows, macOS, Linux with identical commands  
✅ **Automated Setup**: One-command environment checking and initialization  
✅ **CLI-Based**: All AWS operations via CLI, no AWS Console required  
✅ **Team Collaboration**: Centralized configuration for multi-person work  
✅ **Error Handling**: Comprehensive logging and error messages  
✅ **Modular Design**: Each phase is independent and can be retried  

---

## 🔗 Resources

- **AWS CLI Documentation**: https://docs.aws.amazon.com/cli/
- **Course Materials**: See `../project_instruction.md`
- **Proposal**: See `../proposal.md`

---

## 📞 Support

For issues or questions:
1. Check `docs/QUICK_REFERENCE.md` for common problems
2. Review `docs/CROSSPLATFORM_GUIDE.md` for platform-specific solutions
3. Consult `docs/PROJECT_EXECUTION_PLAN.md` for detailed phase info
4. Contact team lead (check `docs/ADMIN_GUIDE.md`)

---

**Last Updated**: April 17, 2026  
**Version**: 1.0 - Initial Setup
