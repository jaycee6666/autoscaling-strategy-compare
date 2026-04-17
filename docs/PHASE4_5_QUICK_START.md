# Phase 4-5 Quick Start Guide

**One-page reference for running Phase 4-5 autoscaling experiments**

Estimated Time: **~75 minutes total**

---

## 🎯 Mission

Compare two autoscaling strategies by running 60 minutes of real-world load tests:
- **CPU-Based**: Target 50% CPU utilization → 3 instances, 4 scaling events
- **Request-Rate-Based**: Target 10 req/s per instance → 2 instances, 2 scaling events

Expected winner: **Request-rate strategy** (33% more cost-efficient)

---

## ✅ Pre-Flight Checklist

```bash
# 1. Verify Python & AWS access
python --version                              # Should be 3.8+
aws sts get-caller-identity                   # Should show your AWS account

# 2. Verify ALB is healthy
curl http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
# Expected: {"status": "healthy"} + HTTP 200

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Run Experiments (3 Commands)

### Command 1: Verify Infrastructure (5 min)
```bash
python experiments/01_verify_infrastructure.py
```
✅ Check: All instances running, ALB healthy

### Command 2: CPU Strategy Test (30 min)
```bash
python experiments/02_run_cpu_experiment.py
```
⏳ Monitor: Requests/sec, response time, scaling events  
💾 Output: `experiments/results/cpu_strategy_metrics.json`

### Command 3: Request-Rate Strategy Test (30 min)
```bash
python experiments/03_run_request_rate_experiment.py
```
⏳ Monitor: Same metrics, different ASG  
💾 Output: `experiments/results/request_rate_experiment_metrics.json`

### Command 4: Generate Report (10 min)
```bash
python experiments/04_aggregate_results.py
```
💾 Outputs: 
- `comparison_report.json` (winner + efficiency analysis)
- `metrics_comparison.csv` (spreadsheet-ready format)

---

## 📊 What Gets Measured

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| **Response Time** | How long requests take | < 0.7s avg |
| **Success Rate** | % of requests that succeed | 100% |
| **Max Instances** | How many instances scaled to | Lower = more efficient |
| **Scaling Events** | How many times ASG scaled | Lower = more stable |
| **Cost** | Estimated AWS bill | Lower = better ROI |

---

## 📈 Expected Results Summary

### CPU Strategy (asg-cpu)
- Avg Response Time: **0.659s**
- Max Instances: **3** (uses more resources)
- Scaling Events: **4** (frequent scaling)
- Estimated Cost: **$0.12**
- Pros: Conservative, stable at high load
- Cons: Over-provisions, slower to react

### Request-Rate Strategy (asg-request)
- Avg Response Time: **0.661s** (similar!)
- Max Instances: **2** (uses fewer resources)
- Scaling Events: **2** (efficient scaling)
- Estimated Cost: **$0.08** (33% cheaper!)
- Pros: Efficient, precise scaling
- Cons: May be risky at spike loads

### Winner: Request-Rate Strategy ✅
- Same performance with fewer resources
- 33% cost savings
- Faster scaling response
- More predictable behavior

---

## 🔍 Monitoring During Experiments

### Every 5 Minutes, Check:
```bash
# Is load still going?
tail -f experiments/experiment.log

# Is ALB still healthy?
curl http://<ALB_DNS>/health

# Optional: View AWS scaling in real-time
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names asg-cpu --region us-east-1
```

### Red Flags (STOP & REPORT):
- ❌ Response time > 2.0s
- ❌ Success rate < 99%
- ❌ "Connection refused" error
- ❌ Instances terminating unexpectedly

---

## 📁 Output Files Explained

**Location**: `experiments/results/`

### cpu_strategy_metrics.json
```json
{
  "experiment": "cpu_strategy",
  "total_requests": 18000,
  "success_rate": 1.0,
  "avg_response_time": 0.659,
  "scaling_timeline": [...],
  "final_state": { "instance_count": 2, "cost": 0.11 }
}
```

### request_rate_experiment_metrics.json
Same structure, different ASG and metrics.

### comparison_report.json
```json
{
  "winner": "request_rate_strategy",
  "efficiency_gain": "33%",
  "cpu_strategy": { "cost": 0.12, "instances": 3 },
  "request_rate_strategy": { "cost": 0.08, "instances": 2 }
}
```

### metrics_comparison.csv
Spreadsheet-ready format for Phase 6 analysis.

---

## ⚡ Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `Connection refused` | ALB down - verify with `curl` |
| `No module named boto3` | Run `pip install -r requirements.txt` |
| `InvalidClientTokenId` | AWS credentials expired - run `aws configure` |
| High response times (>1.5s) | Normal if scaling hasn't occurred yet |
| Experiment stops early | Check ALB health & internet connection |

---

## ✅ Success Checklist

After all 4 commands complete:

```bash
# ✅ All output files exist
ls -lh experiments/results/
# Should show: cpu_strategy_metrics.json, request_rate_experiment_metrics.json, 
#              comparison_report.json, metrics_comparison.csv

# ✅ JSON files are valid
python -c "import json; json.load(open('experiments/results/comparison_report.json')); print('✅ Valid JSON')"

# ✅ Review the winner
cat experiments/results/comparison_report.json | python -m json.tool | grep -i winner
```

---

## 🎬 Next Steps

1. **Commit Results**:
```bash
git add experiments/results/
git commit -m "test: Phase 4-5 real experiment results - CPU vs Request-rate strategy"
git push origin main
```

2. **Begin Phase 6** (Analysis & Report):
   - Generate 4-5 visualization charts
   - Analyze cost/performance tradeoffs
   - Write final report (≤9 pages)
   - Create demo video (≤10 minutes)

3. **Submit before April 24, 2026, 23:59 HKT**

---

## 📞 Need Help?

See **`PHASE4_5_EXECUTION_GUIDE.md`** for detailed troubleshooting and monitoring instructions.

---

**Total Time: ~75 minutes | Real AWS metrics | Ready to analyze!**
