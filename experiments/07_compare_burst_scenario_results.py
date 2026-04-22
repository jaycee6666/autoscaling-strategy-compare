"""Analyze and compare burst scenario results from both strategies.

This script compares CPU and Request-Rate strategies under burst traffic conditions.
"""

import json
import statistics
from pathlib import Path
from typing import Any, Dict, Optional


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _read_results(filename: str) -> Optional[Dict[str, Any]]:
    """Read a results JSON file."""
    filepath = RESULTS_DIR / filename
    if not filepath.exists():
        print(f"Warning: {filename} not found")
        return None

    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def _calculate_metrics(phase_metrics: Dict[str, Any]) -> Dict[str, float]:
    """Calculate key metrics from phase results."""
    metrics = {}

    for phase_name, phase_data in phase_metrics.items():
        avg_response = phase_data.get("avg_response_time_ms", 0)
        avg_capacity = phase_data.get("avg_desired_capacity", 0)
        avg_cpu = phase_data.get("avg_cpu_utilization", 0)

        metrics[f"{phase_name}_response_ms"] = avg_response
        metrics[f"{phase_name}_instances"] = avg_capacity
        metrics[f"{phase_name}_cpu"] = avg_cpu

    return metrics


def _compare_strategies() -> None:
    """Compare CPU and Request-Rate strategies."""
    cpu_results = _read_results("burst_scenario_cpu_results.json")
    rr_results = _read_results("burst_scenario_request_rate_results.json")

    if not cpu_results or not rr_results:
        print("Error: Cannot find both result files")
        return

    print("\n" + "=" * 100)
    print("BURST SCENARIO COMPARISON - CPU vs Request-Rate Strategy")
    print("=" * 100 + "\n")

    # Overall comparison
    print("OVERALL RESULTS")
    print("-" * 100)
    print(f"{'Metric':<40} {'CPU Strategy':<30} {'Request-Rate Strategy':<30}")
    print("-" * 100)

    cpu_summary = cpu_results.get("summary", {})
    rr_summary = rr_results.get("summary", {})

    metrics_to_compare = [
        ("Total Requests", "total_requests"),
        ("Successful Requests", "successful_requests"),
        ("Success Rate (%)", "success_rate"),
        ("Avg Response Time (ms)", "avg_response_time_ms"),
        ("P95 Response Time (ms)", "p95_response_time_ms"),
        ("P99 Response Time (ms)", "p99_response_time_ms"),
    ]

    for display_name, key in metrics_to_compare:
        cpu_val = cpu_summary.get(key, 0)
        rr_val = rr_summary.get(key, 0)

        # Format values
        if key == "success_rate":
            cpu_str = f"{cpu_val * 100:.2f}%"
            rr_str = f"{rr_val * 100:.2f}%"
        else:
            cpu_str = f"{cpu_val:,.2f}" if isinstance(cpu_val, float) else str(cpu_val)
            rr_str = f"{rr_val:,.2f}" if isinstance(rr_val, float) else str(rr_val)

        print(f"{display_name:<40} {cpu_str:>28} {rr_str:>28}")

    # Phase-by-phase comparison
    print("\n\nPHASE-BY-PHASE ANALYSIS")
    print("-" * 100)

    cpu_phases = cpu_results.get("phase_metrics", {})
    rr_phases = rr_results.get("phase_metrics", {})

    phases = ["Preheating", "Baseline", "Burst", "Recovery"]

    for phase in phases:
        if phase not in cpu_phases or phase not in rr_phases:
            continue

        cpu_phase = cpu_phases[phase]
        rr_phase = rr_phases[phase]

        print(f"\n{phase.upper()}")
        print(
            f"  Target Load: {cpu_phase.get('target_request_rate', 0)} req/s | "
            f"Duration: {cpu_phase.get('duration_seconds', 0)}s"
        )
        print(f"  {'-' * 95}")
        print(f"  {'Metric':<35} {'CPU Strategy':<30} {'Request-Rate Strategy':<30}")
        print(f"  {'-' * 95}")

        phase_metrics = [
            ("Avg Response Time (ms)", "avg_response_time_ms"),
            ("Avg Instances", "avg_desired_capacity"),
            ("Avg CPU Utilization (%)", "avg_cpu_utilization"),
        ]

        for metric_name, key in phase_metrics:
            cpu_val = cpu_phase.get(key, 0)
            rr_val = rr_phase.get(key, 0)

            # Format values
            if key == "avg_cpu_utilization":
                cpu_str = f"{cpu_val * 100:.1f}%" if cpu_val else "N/A"
                rr_str = f"{rr_val * 100:.1f}%" if rr_val else "N/A"
            else:
                cpu_str = f"{cpu_val:.2f}" if cpu_val else "N/A"
                rr_str = f"{rr_val:.2f}" if rr_val else "N/A"

            # Highlight better performance
            if key == "avg_response_time_ms" and cpu_val and rr_val:
                winner = (
                    "CPU" if cpu_val < rr_val else "RR" if rr_val < cpu_val else "TIE"
                )
                if winner != "TIE":
                    winner_mark = " ✓" if winner == "CPU" else " ✓"
                    print(
                        f"  {metric_name:<35} {cpu_str:>28}{winner_mark if winner == 'CPU' else '':<1} {rr_str:>28}{winner_mark if winner == 'RR' else '':<1}"
                    )
                else:
                    print(f"  {metric_name:<35} {cpu_str:>28}  {rr_str:>28}")
            else:
                print(f"  {metric_name:<35} {cpu_str:>28}  {rr_str:>28}")

    # Key insights
    print("\n\n" + "=" * 100)
    print("KEY INSIGHTS")
    print("=" * 100)

    # Burst response comparison
    cpu_burst = cpu_phases.get("Burst", {})
    rr_burst = rr_phases.get("Burst", {})
    cpu_burst_instances = 0
    rr_burst_instances = 0
    cpu_burst_response = 0
    rr_burst_response = 0

    if cpu_burst and rr_burst:
        cpu_burst_response = cpu_burst.get("avg_response_time_ms", 0)
        rr_burst_response = rr_burst.get("avg_response_time_ms", 0)
        cpu_burst_instances = cpu_burst.get("avg_desired_capacity", 0)
        rr_burst_instances = rr_burst.get("avg_desired_capacity", 0)

        print("\n1. BURST TRAFFIC RESPONSE:")
        if cpu_burst_response and rr_burst_response:
            diff = abs(cpu_burst_response - rr_burst_response)
            pct_diff = (diff / max(cpu_burst_response, rr_burst_response)) * 100
            winner = (
                "CPU Strategy"
                if cpu_burst_response < rr_burst_response
                else "Request-Rate Strategy"
            )
            print(f"   Winner: {winner}")
            print(
                f"   CPU: {cpu_burst_response:.1f}ms vs Request-Rate: {rr_burst_response:.1f}ms ({pct_diff:.1f}% difference)"
            )

        if cpu_burst_instances and rr_burst_instances:
            print(f"   Instance scaling during burst:")
            print(f"     CPU Strategy: {cpu_burst_instances:.1f} instances")
            print(f"     Request-Rate Strategy: {rr_burst_instances:.1f} instances")

    # Recovery comparison
    cpu_recovery = cpu_phases.get("Recovery", {})
    rr_recovery = rr_phases.get("Recovery", {})

    if cpu_recovery and rr_recovery:
        cpu_recovery_instances = cpu_recovery.get("avg_desired_capacity", 0)
        rr_recovery_instances = rr_recovery.get("avg_desired_capacity", 0)

        print("\n2. SCALE-DOWN BEHAVIOR (Recovery Phase):")
        if (
            cpu_recovery_instances
            and rr_recovery_instances
            and cpu_burst_instances
            and rr_burst_instances
        ):
            print(
                f"   CPU Strategy: {cpu_recovery_instances:.1f} instances (scales down from {cpu_burst_instances:.1f})"
            )
            print(
                f"   Request-Rate Strategy: {rr_recovery_instances:.1f} instances (scales down from {rr_burst_instances:.1f})"
            )

            cpu_scale_down = cpu_burst_instances - cpu_recovery_instances
            rr_scale_down = rr_burst_instances - rr_recovery_instances

            if cpu_scale_down > 0 or rr_scale_down > 0:
                print(f"   Scale-down rate:")
                print(f"     CPU Strategy: {cpu_scale_down:.1f} instances removed")
                print(
                    f"     Request-Rate Strategy: {rr_scale_down:.1f} instances removed"
                )

    print("\n" + "=" * 100 + "\n")


def main() -> None:
    """Main entry point."""
    _compare_strategies()


if __name__ == "__main__":
    main()
