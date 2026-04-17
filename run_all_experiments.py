#!/usr/bin/env python
"""
Auto-runner for Phase 4-5 experiments (Steps 2-4).

This script automatically:
1. Runs Step 2: CPU Strategy Experiment (30 min)
2. Runs Step 3: Request-Rate Strategy Experiment (30 min)
3. Runs Step 4: Aggregate Results (5 min)

Total time: ~65 minutes
No manual intervention needed between steps.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def log(msg: str) -> None:
    """Print timestamped log message."""
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] {msg}", flush=True)


def run_step(step_num: int, script_name: str, description: str) -> bool:
    """
    Run a single experiment step.

    Args:
        step_num: Step number (2, 3, or 4)
        script_name: Name of Python script to run
        description: Human-readable description

    Returns:
        True if successful, False otherwise
    """
    log(f"\n{'=' * 80}")
    log(f"STARTING STEP {step_num}: {description}")
    log(f"{'=' * 80}\n")

    script_path = Path(__file__).parent / "experiments" / script_name

    if not script_path.exists():
        log(f"ERROR: Script not found: {script_path}")
        return False

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False,
            text=True,
        )

        log(f"\nSTEP {step_num}: SUCCESS")
        return True

    except subprocess.CalledProcessError as e:
        log(f"ERROR: Step {step_num} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        log(f"ERROR: Step {step_num} failed: {e}")
        return False


def verify_step_output(step_num: int, expected_file: str) -> bool:
    """
    Verify that a step produced output.

    Args:
        step_num: Step number
        expected_file: Expected output filename in experiments/results/

    Returns:
        True if output file exists
    """
    results_dir = Path(__file__).parent / "experiments" / "results"
    output_file = results_dir / expected_file

    if output_file.exists():
        file_size = output_file.stat().st_size
        log(f"✓ Step {step_num} output verified: {expected_file} ({file_size} bytes)")
        return True
    else:
        log(f"✗ Step {step_num} output missing: {expected_file}")
        return False


def main() -> int:
    """Run all experiment steps sequentially."""
    parser = argparse.ArgumentParser(
        description="Auto-run Phase 4-5 experiments (Steps 2-4) + Phase 6 Analysis"
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip output file verification after each step",
    )
    parser.add_argument(
        "--skip-phase-6",
        action="store_true",
        help="Skip Phase 6 analysis (just run Steps 2-4)",
    )
    args = parser.parse_args()

    log("\n")
    log("╔" + "=" * 78 + "╗")
    log("║" + " " * 78 + "║")
    log(
        "║"
        + "Phase 4-6: Autoscaling Strategy Comparison (Complete Pipeline)".center(78)
        + "║"
    )
    log("║" + "Steps 2-4 Experiments + Phase 6 Analysis".center(78) + "║")
    log("║" + " " * 78 + "║")
    log("╚" + "=" * 78 + "╝")
    log("")

    start_time = datetime.now(timezone.utc)
    log(f"Start time: {start_time.isoformat()}")
    log(f"Expected total duration: ~75 minutes (65 min experiments + 10 min analysis)")
    log("")

    # Step 2: CPU Strategy Experiment
    log("Running Step 2 (CPU Strategy, 30 min)...")
    if not run_step(
        2,
        "02_run_cpu_experiment.py",
        "CPU Strategy Experiment (30 minutes)",
    ):
        return 1

    if not args.skip_verification:
        if not verify_step_output(2, "cpu_strategy_metrics.json"):
            return 1

    # Step 3: Request-Rate Strategy Experiment
    log("\nRunning Step 3 (Request-Rate Strategy, 30 min)...")
    if not run_step(
        3,
        "03_run_request_rate_experiment.py",
        "Request-Rate Strategy Experiment (30 minutes)",
    ):
        return 1

    if not args.skip_verification:
        if not verify_step_output(3, "request_rate_experiment_metrics.json"):
            return 1

    # Step 4: Aggregate Results
    log("\nRunning Step 4 (Aggregate Results, ~5 min)...")
    if not run_step(
        4,
        "04_aggregate_results.py",
        "Aggregate & Compare Results",
    ):
        return 1

    if not args.skip_verification:
        if not verify_step_output(4, "comparison_report.json"):
            return 1
        if not verify_step_output(4, "metrics_comparison.csv"):
            return 1

    # Phase 6: Analysis
    if not args.skip_phase_6:
        log("\nRunning Phase 6 (Analysis, ~2 min)...")
        if not run_step(
            6,
            "06_analyze_results.py",
            "Phase 6 Analysis: Compare Strategies & Determine Winner",
        ):
            log("⚠ Phase 6 analysis failed, but experiments completed successfully")

    # Summary
    end_time = datetime.now(timezone.utc)
    elapsed = (end_time - start_time).total_seconds()
    elapsed_min = elapsed / 60

    log(f"\n{'=' * 80}")
    log(f"ALL STEPS COMPLETED SUCCESSFULLY!")
    log(f"{'=' * 80}")
    log(f"Start time: {start_time.isoformat()}")
    log(f"End time: {end_time.isoformat()}")
    log(f"Total duration: {elapsed_min:.1f} minutes ({elapsed:.0f} seconds)")
    log("")
    log("Output files created:")
    results_dir = Path(__file__).parent / "experiments" / "results"
    for file in sorted(results_dir.glob("*.json")):
        size = file.stat().st_size
        log(f"  ✓ {file.name} ({size} bytes)")
    for file in sorted(results_dir.glob("*.csv")):
        size = file.stat().st_size
        log(f"  ✓ {file.name} ({size} bytes)")

    log("")
    if not args.skip_phase_6:
        log("All experiments and analysis complete! Ready for report generation.")
    else:
        log(
            "Experiments complete. Run 'python experiments/06_analyze_results.py' for analysis."
        )
    log("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
