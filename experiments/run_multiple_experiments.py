#!/usr/bin/env python3
"""
方案B - 多次运行实验并求平均值

通过运行实验多次（可配置），对结果求平均，消除单次噪音。
这是最稳定的解决方案。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def run_experiments(num_runs: int = 3) -> None:
    """Run experiments multiple times and average results.

    Args:
        num_runs: Number of times to run the experiments (default: 3)
    """

    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    all_cpu_metrics: List[Dict[str, Any]] = []
    all_request_metrics: List[Dict[str, Any]] = []
    all_analyses: List[Dict[str, Any]] = []

    print(f"\n{'=' * 70}")
    print(f"Running {num_runs} experiment iterations")
    print(f"{'=' * 70}\n")

    for run_num in range(1, num_runs + 1):
        print(f"\n{'=' * 70}")
        print(f"ITERATION {run_num}/{num_runs}")
        print(f"{'=' * 70}\n")

        # 运行CPU实验
        print("[Step 1/4] Running CPU strategy experiment...")
        try:
            subprocess.run(
                ["python", "experiments/02_run_cpu_experiment.py"],
                check=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ CPU experiment failed: {e}")
            sys.exit(1)

        # 运行请求率实验
        print("\n[Step 2/4] Running request-rate strategy experiment...")
        try:
            subprocess.run(
                ["python", "experiments/03_run_request_rate_experiment.py"],
                check=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Request-rate experiment failed: {e}")
            sys.exit(1)

        # 聚合结果
        print("\n[Step 3/4] Aggregating results...")
        try:
            subprocess.run(
                ["python", "experiments/04_aggregate_results.py"],
                check=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Aggregation failed: {e}")
            sys.exit(1)

        # 分析结果
        print("\n[Step 4/4] Analyzing results...")
        try:
            subprocess.run(
                ["python", "experiments/06_analyze_results.py"],
                check=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)

        # 收集结果文件
        try:
            with open(results_dir / "cpu_strategy_metrics.json") as f:
                all_cpu_metrics.append(json.load(f))
            with open(results_dir / "request_rate_experiment_metrics.json") as f:
                all_request_metrics.append(json.load(f))
            with open(results_dir / "analysis_report.json") as f:
                all_analyses.append(json.load(f))
            print(f"✓ Results collected for iteration {run_num}")
        except FileNotFoundError as e:
            print(f"❌ Failed to read results: {e}")
            sys.exit(1)

    # 计算平均分析结果
    print(f"\n{'=' * 70}")
    print(f"COMPUTING AVERAGED RESULTS")
    print(f"{'=' * 70}\n")

    cpu_response_times = [
        a["comparison"]["cpu_strategy"]["avg_response_time_ms"] for a in all_analyses
    ]
    request_response_times = [
        a["comparison"]["request_rate_strategy"]["avg_response_time_ms"]
        for a in all_analyses
    ]

    cpu_p95_times = [
        a["comparison"]["cpu_strategy"]["p95_response_time_ms"] for a in all_analyses
    ]
    request_p95_times = [
        a["comparison"]["request_rate_strategy"]["p95_response_time_ms"]
        for a in all_analyses
    ]

    cpu_success_rates = [
        a["comparison"]["cpu_strategy"]["success_rate"] for a in all_analyses
    ]
    request_success_rates = [
        a["comparison"]["request_rate_strategy"]["success_rate"] for a in all_analyses
    ]

    # 确定赢家（投票制）
    cpu_wins = sum(1 for a in all_analyses if a["winner"]["strategy"] == "CPU Strategy")
    request_wins = sum(
        1 for a in all_analyses if a["winner"]["strategy"] == "Request-Rate Strategy"
    )

    if cpu_wins > request_wins:
        final_winner = "CPU Strategy"
        winner_votes = cpu_wins
    else:
        final_winner = "Request-Rate Strategy"
        winner_votes = request_wins

    winner_confidence = (
        (max(cpu_wins, request_wins) - min(cpu_wins, request_wins)) / num_runs * 100
    )

    avg_analysis = {
        "timestamp_utc": all_analyses[-1].get("timestamp_utc", ""),
        "num_runs": num_runs,
        "individual_winners": [a["winner"]["strategy"] for a in all_analyses],
        "comparison": {
            "cpu_strategy": {
                "strategy": "CPU Utilization Target",
                "avg_response_time_ms": float(np.mean(cpu_response_times)),
                "std_response_time_ms": float(np.std(cpu_response_times)),
                "p95_response_time_ms": float(np.mean(cpu_p95_times)),
                "success_rate": float(np.mean(cpu_success_rates)),
            },
            "request_rate_strategy": {
                "strategy": "Request Rate Target",
                "avg_response_time_ms": float(np.mean(request_response_times)),
                "std_response_time_ms": float(np.std(request_response_times)),
                "p95_response_time_ms": float(np.mean(request_p95_times)),
                "success_rate": float(np.mean(request_success_rates)),
            },
        },
        "winner": {
            "strategy": final_winner,
            "confidence_pct": winner_confidence,
            "cpu_wins": cpu_wins,
            "request_wins": request_wins,
            "rationale": f"{final_winner} won {winner_votes}/{num_runs} iterations",
        },
    }

    # 保存平均结果
    output_path = results_dir / "averaged_analysis_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(avg_analysis, f, indent=2)

    print(f"✓ Saved averaged results to: {output_path}\n")
    print("=" * 70)
    print("FINAL AVERAGED RESULTS")
    print("=" * 70)
    print(json.dumps(avg_analysis, indent=2))
    print("=" * 70)


if __name__ == "__main__":
    num_runs = 3
    if len(sys.argv) > 1:
        try:
            num_runs = int(sys.argv[1])
        except ValueError:
            print(
                f"Invalid argument. Usage: python run_multiple_experiments.py [num_runs]"
            )
            sys.exit(1)

    run_experiments(num_runs=num_runs)
