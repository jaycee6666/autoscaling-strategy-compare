# Phase 4-5 Experiment Execution Guide

**Complete step-by-step guide for running CPU-based vs Request-rate-based autoscaling experiments**

Last Updated: April 17, 2026  
Estimated Duration: ~75 minutes total (5 min setup + 30 min CPU test + 30 min request-rate test + 10 min analysis)

---

## 📋 Table of Contents

1. [Pre-Requisites Checklist](#pre-requisites-checklist)
2. [Infrastructure Overview](#infrastructure-overview)
3. [Experiment Process](#experiment-process)
4. [Detailed Step-by-Step Execution](#detailed-step-by-step-execution)
5. [Monitoring During Experiments](#monitoring-during-experiments)
6. [Understanding Output Files](#understanding-output-files)
7. [Troubleshooting](#troubleshooting)
8. [Post-Experiment Verification](#post-experiment-verification)
9. [Next Steps (Phase 6)](#next-steps-phase-6)

---

## Pre-Requisites Checklist

Before starting experiments, verify all prerequisites are met:

### System Requirements
- [ ] Python 3.8+ installed (`python --version`)
- [ ] AWS credentials configured (`aws sts get-caller-identity` returns your account)
- [ ] Internet connection (required for AWS API calls)
- [ ] Terminal/Command Prompt access

### AWS Infrastructure Requirements
- [ ] Application Load Balancer (ALB) is **running** and **healthy**
- [ ] ALB DNS name is accessible via HTTP (test with `curl http://<ALB_DNS>/health`)
- [ ] Auto Scaling Group for CPU strategy (`asg-cpu`) exists with 1-5 instance capacity
- [ ] Auto Scaling Group for request-rate strategy (`asg-request`) exists with 1-5 instance capacity
- [ ] EC2 instances in both ASGs are **healthy** and running the Flask application
- [ ] Security groups allow inbound traffic on port 80 (HTTP)

### Python Dependencies
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Key packages: `boto3`, `requests`, `pandas`, `numpy`

### ALB DNS Configuration
Before proceeding, **identify your ALB DNS name**:

```bash
# Get your ALB DNS from infrastructure config
cat infrastructure/alb-config.json | grep -i "dns"

# Or test directly:
curl -v http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
```

Expected response: `{"status": "healthy"}` with HTTP 200

---

## 🏗️ Infrastructure Overview

### Two Autoscaling Strategies Being Tested

#### Strategy 1: CPU-Based Autoscaling (`asg-cpu`)
- **Metric**: Target 50% CPU utilization across instances
- **Scale-out trigger**: When average CPU > 50%
- **Scale-in trigger**: When average CPU < 20%
- **Min instances**: 1 | **Desired**: 1 | **Max**: 5
- **Expected behavior**: Slower to respond, may overshoot target

#### Strategy 2: Request-Rate-Based Autoscaling (`asg-request`)
- **Metric**: Target 10 requests/second per instance
- **Scale-out trigger**: When request rate > 10 req/s per instance
- **Scale-in trigger**: When request rate < 5 req/s per instance
- **Min instances**: 1 | **Desired**: 2 | **Max**: 5
- **Expected behavior**: Faster to respond, more precise scaling

### Load Configuration
- **Constant load**: 10 requests/second (fixed rate)
- **Duration per experiment**: 30 minutes (1800 seconds)
- **Request type**: HTTP POST to `/request` endpoint
- **Response time target**: < 1 second per request

---

## ⏱️ Experiment Process

### Timeline Breakdown

```
Phase 4-5 Total: ~75 minutes

├─ Step 1: Infrastructure Verification (5 min)
│  └─ Command: python experiments/01_verify_infrastructure.py
│     Validates: ALB health, ASG status, instance count
│
├─ Step 2: CPU Strategy Experiment (30 min)
│  └─ Command: python experiments/02_run_cpu_experiment.py
│     Output: cpu_strategy_metrics.json (~18,000 requests)
│     Monitors: CPU util, request rate, scaling events
│
├─ Step 3: Request-Rate Strategy Experiment (30 min)
│  └─ Command: python experiments/03_run_request_rate_experiment.py
│     Output: request_rate_experiment_metrics.json (~18,000 requests)
│     Monitors: Request rate, scaling behavior, latency
│
└─ Step 4: Aggregate & Compare Results (10 min)
   └─ Command: python experiments/04_aggregate_results.py
      Outputs: comparison_report.json, metrics_comparison.csv
      Analysis: Scaling efficiency, responsiveness, resource utilization
```

### Critical Success Requirements

For valid experiment results:
1. ✅ Load generator must maintain exactly 10 requests/second (±0.5 req/s)
2. ✅ No network interruptions during 30-minute periods
3. ✅ No manual ASG changes during experiments (hands-off)
4. ✅ CloudWatch metrics available for collection (5-minute lag acceptable)
5. ✅ Output files contain real AWS metrics, not mock data

---

## 🚀 Detailed Step-by-Step Execution

### STEP 1: Verify Infrastructure (5 minutes)

**Purpose**: Confirm all AWS resources are healthy before running experiments

**Command**:
```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
python experiments/01_verify_infrastructure.py
```

**Expected Output**:
```json
{
  "timestamp": "2026-04-17T17:30:45Z",
  "alb_health": {
    "status": "healthy",
    "dns": "experiment-alb-1466294824.us-east-1.elb.amazonaws.com",
    "http_status": 200
  },
  "asg_cpu": {
    "name": "asg-cpu",
    "desired": 1,
    "current": 1,
    "min": 1,
    "max": 5,
    "instances": [
      {"id": "i-0123456789abcdef0", "state": "running", "cpu": 2.3}
    ]
  },
  "asg_request": {
    "name": "asg-request",
    "desired": 2,
    "current": 2,
    "min": 1,
    "max": 5,
    "instances": [
      {"id": "i-0abcdef0123456789", "state": "running", "cpu": 1.5},
      {"id": "i-0fedcba9876543210", "state": "running", "cpu": 1.8}
    ]
  }
}
```

**What to Check**:
- ✅ `alb_health.status` = `"healthy"` (must be true)
- ✅ All instances show `"state": "running"`
- ✅ `asg_cpu.current` matches `asg_cpu.desired`
- ✅ `asg_request.current` matches `asg_request.desired`
- ❌ **STOP if**: Any instance is `"stopped"` or `"terminated"`

**Troubleshooting**:
- If ALB returns 502/503: instances may not be fully booted. Wait 2 minutes, retry.
- If instance count mismatch: ASG may be scaling. Wait for stability, retry.

---

### STEP 2: Run CPU Strategy Experiment (30 minutes)

**Purpose**: Generate metrics for CPU-based autoscaling strategy

**Command**:
```bash
python experiments/02_run_cpu_experiment.py
```

**What Happens During Experiment**:
1. Script connects to ALB and begins sending exactly 10 requests/second
2. CloudWatch metrics collection starts (background)
3. System monitors:
   - CPU utilization of each instance
   - Request count and response times
   - Scaling activities (scale-out/scale-in events)
   - Instance lifecycle changes
4. After 30 minutes, script collects final metrics and saves to `experiments/results/cpu_strategy_metrics.json`

**Console Output** (real-time monitoring):
```
[17:30:45] CPU Strategy Experiment Started
[17:30:45] Target: 50% CPU utilization | ASG: asg-cpu | Duration: 1800 seconds
[17:30:45] Sending load to ALB: experiment-alb-1466294824.us-east-1.elb.amazonaws.com

[17:31:15] Elapsed: 0:00:30 | Requests: 300 | Success: 100% | Avg Response: 0.659s
[17:31:45] Elapsed: 0:01:00 | Requests: 600 | Success: 100% | Avg Response: 0.651s
[17:32:15] Elapsed: 0:01:30 | Requests: 900 | Success: 100% | Avg Response: 0.658s
...
[18:00:15] Elapsed: 0:29:30 | Requests: 17700 | Success: 100% | Avg Response: 0.660s
[18:00:45] Elapsed: 0:30:00 | Requests: 18000 | Success: 100% | Avg Response: 0.662s

[18:00:45] Collecting final CloudWatch metrics...
[18:00:50] Analyzing scaling events...
[18:00:55] CPU Strategy Experiment Complete!

✅ Results saved to: experiments/results/cpu_strategy_metrics.json
   - Total requests: 18,000
   - Success rate: 100%
   - Average response time: 0.659s
   - Max instances used: 3
   - Scaling events: 4
```

**Critical Monitoring** (Keep terminal open):
- Response time should remain stable (~0.65s)
- Success rate should be 100%
- Requests/second should be consistently 10±0.5
- No timeouts or errors

**If Experiment Fails**:
- Check ALB is still responding: `curl http://<ALB_DNS>/health`
- Check EC2 instances haven't terminated
- Check internet connection is stable
- **DO NOT RESTART** - if connection is broken, results are invalid. Continue to Step 4 and note the failure.

**After This Step Completes**:
- Output file: `experiments/results/cpu_strategy_metrics.json` (15-20 KB)
- Contains: Real CloudWatch metrics, request statistics, scaling timeline

---

### STEP 3: Run Request-Rate Strategy Experiment (30 minutes)

**Purpose**: Generate metrics for request-rate-based autoscaling strategy

**Command**:
```bash
python experiments/03_run_request_rate_experiment.py
```

**What Happens During Experiment**:
1. Script resets ASG to request-rate strategy (`asg-request`)
2. Begins sending exactly 10 requests/second (same as CPU experiment)
3. System monitors:
   - Request count per instance
   - Request rate metrics
   - Scaling activities (how many instances added/removed)
   - Response latency
4. After 30 minutes, collects final metrics and saves to `experiments/results/request_rate_experiment_metrics.json`

**Console Output** (similar to CPU experiment):
```
[18:01:00] Request-Rate Strategy Experiment Started
[18:01:00] Target: 10 req/s per instance | ASG: asg-request | Duration: 1800 seconds
[18:01:00] Sending load to ALB: experiment-alb-1466294824.us-east-1.elb.amazonaws.com

[18:01:30] Elapsed: 0:00:30 | Requests: 300 | Success: 100% | Avg Response: 0.655s
[18:01:60] Elapsed: 0:01:00 | Requests: 600 | Success: 100% | Avg Response: 0.659s
...
[18:30:45] Elapsed: 0:30:00 | Requests: 18000 | Success: 100% | Avg Response: 0.661s

✅ Results saved to: experiments/results/request_rate_experiment_metrics.json
   - Total requests: 18,000
   - Success rate: 100%
   - Average response time: 0.661s
   - Max instances used: 2
   - Scaling events: 2
```

**Key Difference vs CPU Experiment**:
- Request-rate strategy may use fewer instances (more efficient)
- Scaling should be faster (responds to actual request load)
- Response times may be more consistent

**After This Step Completes**:
- Output file: `experiments/results/request_rate_experiment_metrics.json` (15-20 KB)
- Total experiment time elapsed: ~60 minutes

---

### STEP 4: Aggregate & Compare Results (10 minutes)

**Purpose**: Combine both experiment results and generate comparison analysis

**Command**:
```bash
python experiments/04_aggregate_results.py
```

**What This Script Does**:
1. Reads both JSON files from Step 2 and Step 3
2. Calculates comparative metrics:
   - Average response time comparison
   - Success rate comparison
   - Resource utilization (CPU vs Request-rate)
   - Scaling efficiency
   - Cost estimate (instances × 30 min)
3. Identifies which strategy performed better
4. Generates two output files

**Expected Output**:
```
[18:31:00] Loading experiment results...
[18:31:01] Analyzing CPU strategy metrics...
[18:31:02] Analyzing request-rate strategy metrics...
[18:31:03] Generating comparison report...
[18:31:04] Calculating efficiency metrics...

✅ Comparison Report Generated:
   - CPU Strategy:
     * Avg Response Time: 0.659s
     * Max Instances: 3
     * Total Cost: $0.12 (3 instances × 30 min)
     * Scaling Events: 4
   
   - Request-Rate Strategy:
     * Avg Response Time: 0.661s
     * Max Instances: 2
     * Total Cost: $0.08 (2 instances × 30 min)
     * Scaling Events: 2
   
   - Recommendation: Request-rate strategy is 33% more cost-efficient
              and has faster scaling response.

✅ Files generated:
   - experiments/results/comparison_report.json
   - experiments/results/metrics_comparison.csv
```

**Output Files**:

1. **`comparison_report.json`** (1-2 KB):
```json
{
  "comparison": {
    "cpu_strategy": {
      "avg_response_time": 0.659,
      "max_instances": 3,
      "total_instances_hours": 1.5,
      "scaling_events": 4,
      "estimated_cost": 0.12
    },
    "request_rate_strategy": {
      "avg_response_time": 0.661,
      "max_instances": 2,
      "total_instances_hours": 1.0,
      "scaling_events": 2,
      "estimated_cost": 0.08
    },
    "winner": "request_rate_strategy",
    "efficiency_gain": "33%",
    "reasoning": "Fewer instances required, better scaling precision"
  }
}
```

2. **`metrics_comparison.csv`** (plaintext):
```
Metric,CPU Strategy,Request-Rate Strategy
Avg Response Time,0.659s,0.661s
Max Instances,3,2
Cost Estimate,$0.12,$0.08
Scaling Events,4,2
Winner,❌,✅
```

---

## 📊 Monitoring During Experiments

### Real-Time Checks (Every 5 minutes)

While experiments are running, verify:

**1. Load Generator Health**:
```bash
# In separate terminal - check requests are being sent
tail -f experiments/experiment.log
```
Look for: `Elapsed: X:XX | Requests: YYYY | Success: 100%`

**2. ALB Health**:
```bash
curl http://<ALB_DNS>/health
```
Expected: `{"status": "healthy"}` with HTTP 200

**3. AWS CloudWatch Metrics** (optional):
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=app/experiment-alb/xxxxx \
  --start-time 2026-04-17T17:30:00Z \
  --end-time 2026-04-17T17:35:00Z \
  --period 60 \
  --statistics Sum
```

**4. ASG Status**:
```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names asg-cpu \
  --region us-east-1
```
Check: `DesiredCapacity`, `Instances[].HealthStatus`, recent `Activities`

### Expected Metrics Over Time

| Minute | Requests | Avg Response | CPU Util | Instances (CPU) | Instances (ReqRate) |
|--------|----------|--------------|----------|-----------------|-------------------|
| 0-1    | 600      | 0.65s        | 40%      | 1               | 2                 |
| 5      | 3000     | 0.66s        | 55%      | 1→2             | 2                 |
| 10     | 6000     | 0.66s        | 60%      | 2→3             | 2                 |
| 15     | 9000     | 0.67s        | 52%      | 3               | 2                 |
| 20     | 12000    | 0.66s        | 48%      | 3→2             | 2                 |
| 25     | 15000    | 0.66s        | 45%      | 2               | 2                 |
| 30     | 18000    | 0.66s        | 42%      | 1→2             | 2                 |

**Note**: Actual scaling may vary based on CloudWatch metric lag (5-minute intervals)

---

## 📁 Understanding Output Files

### File Locations
```
experiments/results/
├── cpu_strategy_metrics.json                 ← Output from Step 2
├── request_rate_experiment_metrics.json      ← Output from Step 3
├── comparison_report.json                    ← Output from Step 4
└── metrics_comparison.csv                    ← Output from Step 4
```

### cpu_strategy_metrics.json Structure
```json
{
  "experiment": "cpu_strategy",
  "asg_name": "asg-cpu",
  "timestamp_start": "2026-04-17T18:00:00Z",
  "timestamp_end": "2026-04-17T18:30:00Z",
  "duration_seconds": 1800,
  "load_results": {
    "total_requests": 18000,
    "successful_requests": 18000,
    "failed_requests": 0,
    "success_rate": 1.0,
    "avg_response_time": 0.659,
    "min_response_time": 0.210,
    "max_response_time": 1.850,
    "p50_response_time": 0.630,
    "p95_response_time": 0.890,
    "p99_response_time": 1.120
  },
  "cloudwatch_metrics": {
    "cpu_utilization": {
      "average": 48.3,
      "minimum": 5.2,
      "maximum": 72.5,
      "samples": 6
    },
    "request_count": {
      "total": 18000,
      "average_per_minute": 600
    }
  },
  "scaling_timeline": [
    {
      "timestamp": "2026-04-17T18:05:00Z",
      "event": "scale_out",
      "previous_count": 1,
      "new_count": 2,
      "reason": "CPU > 50%"
    },
    {
      "timestamp": "2026-04-17T18:10:00Z",
      "event": "scale_out",
      "previous_count": 2,
      "new_count": 3,
      "reason": "CPU > 60%"
    },
    {
      "timestamp": "2026-04-17T18:20:00Z",
      "event": "scale_in",
      "previous_count": 3,
      "new_count": 2,
      "reason": "CPU < 50%"
    }
  ],
  "final_state": {
    "instance_count": 2,
    "total_instances_hours": 1.42,
    "estimated_cost": 0.11
  }
}
```

### Data Interpretation Guide

**Response Time Metrics**:
- `avg_response_time`: Overall average (should be ~0.66s)
- `p95`: 95% of requests complete within this time (acceptable < 1.0s)
- `p99`: 99% of requests complete within this time (shows tail latency)

**Scaling Events**:
- Count events to understand scaling frequency
- `timestamp` helps determine when scaling occurred
- CPU strategy should have 3-5 events; request-rate should have 1-3

**Cost Estimation**:
- `total_instances_hours`: Sum of (instance count × hours active)
- For 30-min experiment with 2 avg instances: 1.0 instance-hours
- AWS t3.medium ~$0.04/hour → $0.04 per experiment

---

## 🔧 Troubleshooting

### Problem 1: "Connection refused" to ALB

**Symptom**:
```
requests.exceptions.ConnectionError: Connection refused
```

**Causes & Solutions**:
1. ALB is down:
   ```bash
   curl -v http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
   ```
   - If no response: ALB may need to be restarted (contact infrastructure team)

2. Wrong ALB DNS:
   - Check `infrastructure/alb-config.json` for correct DNS
   - Verify DNS resolves: `nslookup experiment-alb-1466294824.us-east-1.elb.amazonaws.com`

3. Security group blocks traffic:
   - Verify port 80 is open: Check AWS Console → Security Groups

**Recovery**:
- Fix the issue and restart experiment from STEP 1

---

### Problem 2: "No module named 'boto3'"

**Symptom**:
```
ModuleNotFoundError: No module named 'boto3'
```

**Solution**:
```bash
pip install -r requirements.txt
```

---

### Problem 3: "InvalidClientTokenId" AWS error

**Symptom**:
```
botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId)
```

**Causes**:
- AWS credentials expired or invalid
- Environment variables not set

**Solution**:
```bash
aws sts get-caller-identity  # Verify credentials work
aws configure                # Reconfigure if needed
```

---

### Problem 4: Experiment stops after 5 minutes

**Symptom**:
```
[17:35:00] Elapsed: 0:05:00 | Requests: 3000
[17:35:05] ERROR: Connection timeout
```

**Causes**:
- Internet connection dropped
- ALB became unhealthy
- EC2 instances crashed

**Recovery**:
1. Check ALB: `curl http://<ALB_DNS>/health`
2. Check instances in AWS Console
3. If infrastructure is broken, report to infrastructure team
4. **Results are INVALID** - do not continue to Step 4

---

### Problem 5: "results directory does not exist"

**Symptom**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'experiments/results/...'
```

**Solution**:
```bash
mkdir -p experiments/results
python experiments/02_run_cpu_experiment.py
```

---

### Problem 6: High response times (>1.5s)

**Possible Causes**:
- ALB is overloaded (instances may be insufficient)
- Network latency between your machine and AWS
- Instances are underpowered or have high CPU

**This is Normal IF**:
- You're running from outside AWS region
- Scaling hasn't happened yet

**Recovery**:
- Let experiment continue (scaling will kick in)
- Results are still valid even with higher latency

---

## ✅ Post-Experiment Verification

### Verify Output Files Exist

```bash
# Should all exist after experiments complete
ls -lh experiments/results/
```

Expected output:
```
-rw-r--r-- cpu_strategy_metrics.json              (15 KB)
-rw-r--r-- request_rate_experiment_metrics.json   (15 KB)
-rw-r--r-- comparison_report.json                 (1 KB)
-rw-r--r-- metrics_comparison.csv                 (200 B)
```

### Verify File Contents Are Valid JSON

```bash
# Verify JSON is valid (should output "OK")
python -c "import json; json.load(open('experiments/results/cpu_strategy_metrics.json')); print('OK')"
python -c "import json; json.load(open('experiments/results/request_rate_experiment_metrics.json')); print('OK')"
```

### Review Comparison Report

```bash
cat experiments/results/comparison_report.json | python -m json.tool
```

You should see winner clearly indicated.

---

## 🎯 Next Steps (Phase 6)

Once experiments complete successfully:

1. **Commit Results to Git**:
```bash
git add experiments/results/
git commit -m "test: Phase 4-5 real experiment results - CPU vs Request-rate strategy comparison"
git push origin main
```

2. **Begin Phase 6 Analysis**:
   - Parse `comparison_report.json` for key findings
   - Generate visualization charts (response time, scaling timeline, cost)
   - Analyze why one strategy outperformed the other
   - Write findings in final report (≤9 pages)

3. **Create Demonstration Video** (≤10 minutes):
   - Show infrastructure architecture
   - Demonstrate autoscaling behavior from both experiments
   - Present comparative results
   - Make recommendations

4. **Submit to Blackboard** before April 24, 2026, 23:59 HKT

---

## ❓ Quick Reference Commands

```bash
# Verify prerequisites
python --version
aws sts get-caller-identity
curl http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health

# Run all experiments
python experiments/01_verify_infrastructure.py      # 5 min
python experiments/02_run_cpu_experiment.py         # 30 min
python experiments/03_run_request_rate_experiment.py # 30 min
python experiments/04_aggregate_results.py          # 10 min

# Verify results
ls -lh experiments/results/
python -c "import json; json.load(open('experiments/results/comparison_report.json')); print('✅ Valid')"

# Commit results
git add experiments/results/
git commit -m "test: Phase 4-5 real experiment results"
git push origin main
```

---

**Ready to run experiments? Start with Step 1: Infrastructure Verification!**
