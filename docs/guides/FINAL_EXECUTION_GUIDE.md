# FINAL EXECUTION GUIDE - Steps 2-4

## 🚀 Quick Start (Copy & Paste)

Open your Windows command prompt (CMD) and run:

```cmd
cd C:\project\CS5296\project3\autoscaling-strategy-compare
venv\Scripts\activate
python run_all_experiments.py
```

This will automatically:
1. Run Step 2 (CPU Strategy, ~30 min)
2. Run Step 3 (Request-Rate Strategy, ~30 min)
3. Run Step 4 (Aggregate Results, ~5 min)
4. Display final results

**Total time**: ~65 minutes, no manual intervention needed

---

## What This Does

The `run_all_experiments.py` script:
- ✅ Executes all 3 experiment steps sequentially
- ✅ Waits for each step to complete before starting the next
- ✅ Verifies output files are created after each step
- ✅ Displays progress with timestamps
- ✅ Shows final summary when all done

---

## Expected Output Timeline

```
[10:35 UTC] Step 2 START (CPU Strategy)
[11:05 UTC] Step 2 COMPLETE → Step 3 START (Request-Rate)
[11:35 UTC] Step 3 COMPLETE → Step 4 START (Aggregation)
[11:40 UTC] Step 4 COMPLETE - ALL EXPERIMENTS DONE
```

---

## After Completion

When the script finishes, you'll have:
- ✅ `experiments/results/cpu_strategy_metrics.json` (CPU strategy data)
- ✅ `experiments/results/request_rate_experiment_metrics.json` (Request-rate strategy data)
- ✅ `experiments/results/comparison_report.json` (Comparison & winner)
- ✅ `experiments/results/metrics_comparison.csv` (Metrics table)

---

## Phase 6: Analysis (After Results Ready)

Once all experiments complete, I will:
1. Analyze the real AWS metrics
2. Generate comparison charts
3. Write the final report (≤9 pages)
4. Help create demo video

---

## If Something Goes Wrong

### Script stops unexpectedly
- Check the error message
- Restart: `python run_all_experiments.py`
- It will skip completed steps and continue

### AWS timeout during experiments
- This is normal - experiments run 30+ minutes
- Just wait, don't interrupt
- The script shows progress every 30 seconds

### Output files not appearing
- Wait longer - CloudWatch metrics take time to populate
- Check AWS console to verify instances are still running
- The script verifies output after each step

---

## Manual Alternative (If Auto-Runner Fails)

If the auto-runner doesn't work, manually run:

```cmd
# Step 2
python experiments/02_run_cpu_experiment.py
# Wait for completion...

# Step 3
python experiments/03_run_request_rate_experiment.py
# Wait for completion...

# Step 4
python experiments/04_aggregate_results.py
```

But the auto-runner handles all this for you.

---

## Now vs Later

### Option A: Run NOW (RECOMMENDED)
- Start the script immediately
- It runs for ~65 minutes automatically
- You get results by evening UTC
- Can start Phase 6 analysis sooner

### Option B: Run Later
- Come back when you have time
- Just make sure you do it before April 24 deadline

**Recommendation**: Run now so you have real data for Phase 6 as soon as possible.

---

## Git Status

All changes committed:
```
✓ Flask app with /request endpoint
✓ Diagnostic reports
✓ Recovery guide
✓ Auto-runner script
✓ This execution guide
```

Everything is ready. Just run the script and let it work.
