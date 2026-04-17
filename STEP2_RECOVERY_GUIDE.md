# Phase 4-5 Experiments: Recovery & Continuation Guide

## Current Status

**Time**: 2026-04-17 ~10:05 UTC  
**Step 2 Status**: 🔄 RUNNING (started fresh after Flask app fix)

---

## What Happened

### The Problem
- Initial Step 2 run failed: **All 2,268 requests returned HTTP 404** (0% success)
- Root cause: Flask app was **missing the `/request` endpoint**

### The Fix
1. ✅ Added `/request` endpoint to Flask app (`apps/test_app/app.py`)
2. ✅ Re-deployed to all EC2 instances in ASG
3. ✅ Verified endpoint works: `HTTP 200 - success`
4. ✅ Started fresh Step 2 run

---

## Timeline for Experiments

Assuming Step 2 started at **10:05 UTC**:

| Time | Task | Status |
|------|------|--------|
| 10:05 - 10:35 UTC | Step 2 (30 min) | 🔄 RUNNING |
| 10:35 - 11:05 UTC | Step 3 (30 min) | ⏳ START AFTER Step 2 |
| 11:05 - 11:10 UTC | Step 4 (5 min) | ⏳ START AFTER Step 3 |
| 11:10 UTC+ | Phase 6 Analysis | ⏳ START AFTER Step 4 |

---

## What You Should Do

### ⏸️ For the Next 30 Minutes (While Step 2 Runs)

**DO NOT INTERRUPT** the Step 2 experiment. The script will:
- Generate 10 requests/second for 30 minutes
- Each request includes 0.3s delay (to trigger CPU scaling)
- Collect CloudWatch metrics every 30 seconds
- Display progress output every 60 seconds (as we fixed earlier)

You should see output like:
```
======================================================================
CPU Strategy Experiment Starting
======================================================================
ASG: asg-cpu
ALB: experiment-alb-1466294824.us-east-1.elb.amazonaws.com
...

[60s/1800s] Requests: 600 | Success: 100.0% | Avg time: 660ms
[120s/1800s] Requests: 1200 | Success: 100.0% | Avg time: 661ms
[180s/1800s] Requests: 1800 | Success: 100.0% | Avg time: 660ms
...
```

### ✅ When Step 2 Completes (~10:35 UTC)

The script will:
1. Finish the 30-minute load generation
2. Print `"Experiment Complete! Collecting final results..."`
3. Display final summary statistics
4. Save results to: `experiments/results/cpu_strategy_metrics.json`
5. Print: `"Saved: C:\...\cpu_strategy_metrics.json"`

Then **immediately run**:
```cmd
python experiments/03_run_request_rate_experiment.py
```

This will take another 30 minutes (same process, different ASG strategy).

### ✅ When Step 3 Completes (~11:05 UTC)

Run:
```cmd
python experiments/04_aggregate_results.py
```

This will:
- Combine results from Step 2 and Step 3
- Create: `experiments/results/comparison_report.json`
- Create: `experiments/results/metrics_comparison.csv`
- Determine the winner strategy

---

## File Locations & Verification

After all experiments complete, verify:

```bash
# Check all output files exist
ls -lh experiments/results/
  cpu_strategy_metrics.json          (~15-20 KB)
  request_rate_experiment_metrics.json (~15-20 KB)
  comparison_report.json             (~1-2 KB)
  metrics_comparison.csv             (~300-500 B)
```

### Verify Data Validity

Each JSON file should contain:
- ✅ `"load_summary"` with `"success_rate": 1.0` (or close to it)
- ✅ `"metric_samples"` array with timestamps from CloudWatch
- ✅ `"scaling_summary"` with actual scale-out/scale-in events

**NOT** like the failed attempt:
- ❌ `"success_rate": 0.0` (all failed)
- ❌ `"load_errors"` full of HTTP 404s

---

## Next Phase: Phase 6 (After All Experiments)

Once Step 4 completes and you have valid data:

1. **Analyze Results**
   - Compare CPU strategy vs Request-rate strategy
   - Extract winner based on cost-per-request or response time

2. **Generate Visualizations** (I'll handle this)
   - Scaling timeline charts
   - Response time trends
   - CPU utilization comparisons

3. **Write Report** (≤9 pages)
   - Executive summary
   - Methodology
   - Results & analysis
   - Conclusion

4. **Create Demo Video** (≤10 minutes)
   - Show infrastructure setup
   - Show experiment execution
   - Show final results

5. **Submit** before April 24, 23:59 HKT

---

## Important Notes

### Real AWS Data
✅ This time, you'll get **real CloudWatch metrics**, not mock data
✅ Real scaling events from AutoScaling Service
✅ Real EC2 instance behavior
✅ Meets academic integrity requirements ✓

### No More 404 Errors
✅ Flask app now has `/request` endpoint
✅ ALB properly routes traffic
✅ Instances are healthy and deployed
✅ Expected success rate: **~100%**

### Git Commits Made
```
1. 17f12ec: fix: add /request endpoint to Flask app
2. [next]: docs: diagnostic report for Step 2 failure
```

---

## Troubleshooting

**Q: I see timeout errors or connection refused?**
- Wait 2-3 minutes for instances to fully boot after the redeployment
- The `/request` endpoint now works - you tested it ✓

**Q: How do I know when Step 2 finishes?**
- Look for: `"Saved: C:\...\cpu_strategy_metrics.json"`
- Or check: `ls experiments/results/cpu_strategy_metrics.json` (if it exists, Step 2 is done)

**Q: Can I run Steps 2 & 3 in parallel?**
- No - they use the same ALB listener
- Step 2 must complete, then Step 3 starts
- They're sequential by design

**Q: What if an experiment crashes?**
- Stop the process (Ctrl+C)
- Check the error message
- Let me know - we'll fix and retry

---

## Contact / Questions

If you have questions while waiting:
- Check the output for progress messages
- Each experiment prints progress every 60 seconds
- Final results save automatically to `experiments/results/`

Good luck! You're now collecting **real AWS data** for your academic submission. 🚀
