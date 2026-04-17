# Phase 2b: Application Development Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create load generation tools, metrics collection utilities, and a test Flask application to support autoscaling experiments.

**Architecture:** 
- **load_generator.py**: HTTP load generation with configurable patterns (constant/ramp/wave)
- **metrics_collector.py**: Real-time CloudWatch metrics polling and CSV export
- **experiment_runner.py**: Orchestration layer coordinating load tests and metrics collection
- **apps/test_app/app.py**: Lightweight Flask application with health checks, data endpoints, and CPU-intensive operations

**Tech Stack:** 
- Python 3.8+, boto3, requests, Flask, pandas, matplotlib
- AWS CloudWatch API
- HTTP/REST protocols

> ⚠️ **CANONICAL GUIDE**: For step-by-step implementation instructions, see **[../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)**. This document contains the planning tasks and verification steps; the deployment guide contains the detailed code and setup instructions.

---

## Implementation Tasks

**See [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) for complete step-by-step implementation instructions, code examples, and verification procedures.**

This plan document outlines the task structure and validation criteria. The canonical execution guide is in the guides/ directory.

### Task 1: Create Load Generator Core

**Files:**
- Create: `scripts/load_generator.py`
- Test: `tests/test_load_generator.py`

**Objective:** Implement HTTP load generation with configurable patterns (constant rate, ramp-up, wave).

**Deliverables:**
- ✅ LoadGenerator class with constant/ramp/wave pattern support
- ✅ Thread-based request execution with configurable concurrency
- ✅ Response time tracking and statistical analysis (mean, P95)
- ✅ CSV export functionality for load statistics
- ✅ Comprehensive test suite (≥4 test cases)

**Success Criteria:**
- `pytest tests/test_load_generator.py` returns all PASS
- LoadGenerator produces correct request rates within ±10% tolerance
- Response times captured with microsecond precision

**For implementation**: See Task 1 in [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)

---

### Task 2: Create Metrics Collector

**Files:**
- Create: `scripts/metrics_collector.py`
- Test: `tests/test_metrics_collector.py`

**Objective:** Poll CloudWatch metrics for ASG health, instance counts, and CPU utilization.

**Deliverables:**
- ✅ MetricsCollector class with background polling thread
- ✅ CloudWatch integration for CPU utilization, network metrics
- ✅ ASG integration for instance count and health status
- ✅ CSV export with timestamp, CPU, instance_count, request_rate columns
- ✅ Summary statistics (avg, min, max for all metrics)
- ✅ Comprehensive test suite (≥3 test cases)

**Success Criteria:**
- `pytest tests/test_metrics_collector.py` returns all PASS
- Metrics collected at configurable intervals (default 10s)
- CSV export contains valid timestamps and numeric data

**For implementation**: See Task 2 in [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)

---

### Task 3: Create Experiment Runner Orchestrator

**Files:**
- Create: `scripts/experiment_runner.py`
- Test: `tests/test_experiment_runner.py`

**Objective:** Orchestrate load generation and metrics collection for experiments.

**Deliverables:**
- ✅ ExperimentRunner class coordinating load + metrics
- ✅ Automatic output directory creation per experiment
- ✅ Parallel execution of load and metrics collection
- ✅ JSON experiment log with metadata and results
- ✅ Results export: experiment_log.json, load_stats.csv, metrics.csv
- ✅ Results summary with status, load stats, metrics summary
- ✅ Comprehensive test suite (≥3 test cases)

**Success Criteria:**
- `pytest tests/test_experiment_runner.py` returns all PASS
- ExperimentRunner validates parameters (positive request_rate, duration, valid pattern)
- Output directory created successfully under experiments/<experiment_name>/
- All three output files generated after successful run

**For implementation**: See Task 3 in [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)

---

### Task 4: Create Test Flask Application

**Files:**
- Create: `apps/test_app/app.py`
- Create: `apps/test_app/Dockerfile`
- Test: `tests/test_app_endpoints.py`

**Objective:** Lightweight HTTP service for testing autoscaling strategies.

**Deliverables:**
- ✅ Flask application listening on 0.0.0.0:8080
- ✅ `/health` endpoint (GET): Simple health check
- ✅ `/data` endpoint (GET): Return configurable random payload
- ✅ `/cpu-intensive` endpoint (POST): CPU-bound workload simulation
- ✅ `/metrics` endpoint (GET): In-process request tracking
- ✅ `/reset` endpoint (POST): Reset metrics counters
- ✅ Dockerfile with Python 3.9 base, health check, auto-restart
- ✅ Comprehensive endpoint tests (≥5 test cases)

**Success Criteria:**
- `pytest tests/test_app_endpoints.py` returns all PASS
- Flask app runs standalone: `python apps/test_app/app.py`
- Docker build succeeds: `docker build -t test-app:latest apps/test_app`
- All endpoints respond with 200 OK to valid requests
- HEALTHCHECK curl command succeeds in container

**For implementation**: See Task 4 in [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)

---

### Task 5: Project Structure & Documentation

**Files:**
- Update: `README.md` (add Phase 2b reference)
- Reference: `docs/PHASE2B_IMPLEMENTATION_GUIDE.md` (pointer to this plan)

**Objective:** Document Phase 2b components and usage.

**Deliverables:**
- ✅ README.md updated with Phase 2b quick-start
- ✅ Clear references from planning doc to canonical deployment guide
- ✅ Integration instructions for Phase 2b outputs into Phase 3

**Success Criteria:**
- README.md includes Phase 2b section with component overview
- Users can find deployment guide from this document
- No broken links between plan and guide documents

**For implementation**: See Task 5 in [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)

---

## Commit Guidelines

When implementing this plan, make atomic commits with descriptive messages:

```bash
# Task 1 commit
git add scripts/load_generator.py tests/test_load_generator.py
git commit -m "feat: implement LoadGenerator with constant/ramp/wave patterns

- Add LoadGenerator class with configurable HTTP load generation
- Support constant, ramp-up, and wave load patterns
- Track response times, success rates, and errors
- Export statistics to CSV format
- Add comprehensive test suite"

# Task 2 commit
git add scripts/metrics_collector.py tests/test_metrics_collector.py
git commit -m "feat: implement MetricsCollector for CloudWatch monitoring

- Add background metrics collection thread
- Poll ASG metrics: CPU, instance count, health status
- Support network metrics (in/out bytes)
- Export metrics history to CSV format
- Add comprehensive test suite"

# Task 3 commit
git add scripts/experiment_runner.py tests/test_experiment_runner.py
git commit -m "feat: implement ExperimentRunner orchestration

- Coordinate load generation and metrics collection
- Run complete experiments with validation
- Export results (logs, stats, metrics)
- Provide experiment results summary"

# Task 4 commit
git add apps/test_app/app.py apps/test_app/Dockerfile tests/test_app_endpoints.py
git commit -m "feat: create test Flask application for autoscaling

- Add /health endpoint for ALB health checks
- Add /data endpoint for payload testing
- Add /cpu-intensive endpoint for CPU strategy testing
- Add /metrics endpoint for application metrics
- Dockerize application for AWS deployment
- Add comprehensive endpoint tests"
```

---

## Verification Checklist

- [ ] All tasks implemented per deployment guide
- [ ] All tests passing: `pytest tests/test_*.py -v`
- [ ] Type checking clean: `mypy scripts apps tests` (if available)
- [ ] All files use boto3 (no AWS CLI subprocess calls)
- [ ] Cross-platform compatible (Windows/macOS/Linux)
- [ ] Git commits use author: jaycee6666 <sijiechan2-c@my.cityu.edu.hk>
- [ ] README.md updated with Phase 2b overview
- [ ] All deliverables working correctly
- [ ] Output directory structure: experiments/<name>/{experiment_log.json, load_stats.csv, metrics.csv}

---

## Next Steps (Phase 3)

After completing Phase 2b implementation and verification:
1. Deploy test Flask application to AWS EC2 instances
2. Configure ALB to route traffic to application
3. Verify application health checks succeed
4. Proceed to Phase 4-5 experimental execution
