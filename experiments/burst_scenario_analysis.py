#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Burst Scenario Analysis Report - One-Click Analysis
Generates intuitive comparison report from burst_scenario_*.json files
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Fix Windows encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def load_burst_scenario(json_file: Path) -> Dict[str, Any]:
    """Load burst scenario JSON file."""
    with open(json_file) as f:
        return json.load(f)


def extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from burst scenario data."""
    summary = data.get("summary", {})
    phase_metrics = data.get("phase_metrics", {})
    raw_samples = data.get("raw_samples", [])
    scale_out_stats = data.get("scale_out_latency_stats", {})

    # Calculate phase-specific metrics
    phases_analysis = {}
    for phase_name, phase_data in phase_metrics.items():
        phases_analysis[phase_name] = {
            "duration_sec": phase_data.get("duration_seconds"),
            "target_rate": phase_data.get("target_request_rate"),
            "avg_response_ms": phase_data.get("avg_response_time_ms"),
            "avg_capacity": phase_data.get("avg_desired_capacity"),
            "avg_cpu": phase_data.get("avg_cpu_utilization"),
            "samples": phase_data.get("sample_count"),
        }

    # Calculate max capacity from raw samples
    max_capacity = max([s.get("desired_capacity", 0) for s in raw_samples], default=0)

    # Count scaling events
    capacities = [s.get("desired_capacity", 0) for s in raw_samples]
    scale_out_events = sum(
        1 for i in range(1, len(capacities)) if capacities[i] > capacities[i - 1]
    )
    scale_in_events = sum(
        1 for i in range(1, len(capacities)) if capacities[i] < capacities[i - 1]
    )

    # Extract scale-out latency statistics (from experiment script output)
    scale_out_latency_stats = {
        "count": scale_out_stats.get("count", 0),
        "mean": scale_out_stats.get("mean", 0),
        "median": scale_out_stats.get("median", 0),
        "min": scale_out_stats.get("min", 0),
        "max": scale_out_stats.get("max", 0),
        "stdev": scale_out_stats.get("stdev", 0),
    }

    return {
        "strategy": data.get("strategy", "unknown"),
        "total_requests": summary.get("total_requests"),
        "successful_requests": summary.get("successful_requests"),
        "failed_requests": summary.get("failed_requests"),
        "success_rate": summary.get("success_rate"),
        "avg_response_ms": summary.get("avg_response_time_ms"),
        "p95_response_ms": summary.get("p95_response_time_ms"),
        "p99_response_ms": summary.get("p99_response_time_ms"),
        "max_capacity": max_capacity,
        "scale_out_events": scale_out_events,
        "scale_in_events": scale_in_events,
        "scale_out_latency_stats": scale_out_latency_stats,
        "phases": phases_analysis,
        "timestamp": data.get("timestamp_utc"),
    }


def calculate_improvements(cpu_metrics: Dict, req_metrics: Dict) -> Dict[str, Any]:
    """Calculate percentage improvements."""
    return {
        "avg_response_improvement_pct": (
            (cpu_metrics["avg_response_ms"] - req_metrics["avg_response_ms"])
            / cpu_metrics["avg_response_ms"]
            * 100
        )
        if cpu_metrics["avg_response_ms"] > 0
        else 0,
        "p95_response_improvement_pct": (
            (cpu_metrics["p95_response_ms"] - req_metrics["p95_response_ms"])
            / cpu_metrics["p95_response_ms"]
            * 100
        )
        if cpu_metrics["p95_response_ms"] > 0
        else 0,
        "p99_response_improvement_pct": (
            (cpu_metrics["p99_response_ms"] - req_metrics["p99_response_ms"])
            / cpu_metrics["p99_response_ms"]
            * 100
        )
        if cpu_metrics["p99_response_ms"] > 0
        else 0,
    }


def determine_winner(
    cpu_metrics: Dict, req_metrics: Dict, improvements: Dict
) -> Dict[str, Any]:
    """Determine winner based on key metrics."""

    # Scoring system
    cpu_score = 0
    req_score = 0
    reasoning = []

    # Latency comparison (most important)
    if req_metrics["p95_response_ms"] < cpu_metrics["p95_response_ms"]:
        req_score += 30
        reasoning.append(
            f"✅ Request-rate: P95 latency {improvements['p95_response_improvement_pct']:.1f}% better "
            f"({req_metrics['p95_response_ms']:.0f}ms vs {cpu_metrics['p95_response_ms']:.0f}ms)"
        )
    else:
        cpu_score += 30
        reasoning.append(
            f"✅ CPU: P95 latency better ({cpu_metrics['p95_response_ms']:.0f}ms vs {req_metrics['p95_response_ms']:.0f}ms)"
        )

    # Scaling behavior (crucial for burst)
    if req_metrics["max_capacity"] > cpu_metrics["max_capacity"]:
        req_score += 20
        reasoning.append(
            f"✅ Request-rate: Better burst response - scales to {req_metrics['max_capacity']} instances "
            f"vs CPU's {cpu_metrics['max_capacity']}"
        )
    elif req_metrics["max_capacity"] < cpu_metrics["max_capacity"]:
        cpu_score += 20
        reasoning.append(
            f"✅ CPU: More cost-efficient - uses {cpu_metrics['max_capacity']} instances "
            f"vs Request-rate's {req_metrics['max_capacity']}"
        )
    else:
        cpu_score += 10
        req_score += 10
        reasoning.append(
            f"⚪ Same capacity scaling: Both use {cpu_metrics['max_capacity']} instances"
        )

    # Success rate
    if req_metrics["success_rate"] >= cpu_metrics["success_rate"]:
        req_score += 10
        if req_metrics["success_rate"] > cpu_metrics["success_rate"]:
            reasoning.append(
                f"✅ Request-rate: Higher success rate ({req_metrics['success_rate'] * 100:.1f}% vs {cpu_metrics['success_rate'] * 100:.1f}%)"
            )
        else:
            reasoning.append(
                f"⚪ Same success rate: Both {cpu_metrics['success_rate'] * 100:.1f}%"
            )
    else:
        cpu_score += 10
        reasoning.append(
            f"✅ CPU: Higher success rate ({cpu_metrics['success_rate'] * 100:.1f}% vs {req_metrics['success_rate'] * 100:.1f}%)"
        )

    # Throughput
    if cpu_metrics["total_requests"] > req_metrics["total_requests"]:
        cpu_score += 5
        reasoning.append(
            f"✅ CPU: Higher throughput ({cpu_metrics['total_requests']} requests vs {req_metrics['total_requests']})"
        )
    else:
        req_score += 5
        reasoning.append(
            f"✅ Request-rate: Higher throughput ({req_metrics['total_requests']} requests vs {cpu_metrics['total_requests']})"
        )

    # Determine winner
    if req_score > cpu_score:
        winner = "Request-Rate Strategy"
        confidence = req_score / (cpu_score + req_score) * 100
    elif cpu_score > req_score:
        winner = "CPU Strategy"
        confidence = cpu_score / (cpu_score + req_score) * 100
    else:
        winner = "Tie"
        confidence = 50.0

    return {
        "winner": winner,
        "cpu_score": cpu_score,
        "req_score": req_score,
        "confidence_pct": confidence,
        "reasoning": reasoning,
    }


def format_phase_comparison(cpu_metrics: Dict, req_metrics: Dict) -> str:
    """Format phase-by-phase comparison."""
    output = "\n" + "=" * 80 + "\n"
    output += "📊 PHASE-BY-PHASE ANALYSIS\n"
    output += "=" * 80 + "\n\n"

    phases = ["Preheating", "Baseline", "Burst", "Recovery"]

    for phase in phases:
        cpu_phase = cpu_metrics["phases"].get(phase, {})
        req_phase = req_metrics["phases"].get(phase, {})

        output += f"▶ {phase.upper()}\n"
        output += "-" * 80 + "\n"

        # Capacity comparison
        cpu_cap = cpu_phase.get("avg_capacity", 0)
        req_cap = req_phase.get("avg_capacity", 0)
        output += f"  Avg Capacity:     CPU={cpu_cap:.1f}  | Request-Rate={req_cap:.1f}"
        if phase == "Burst":
            if req_cap > cpu_cap:
                output += "  ✅ Request-rate scales better!"
            elif cpu_cap > req_cap:
                output += "  ✅ CPU scales more aggressively"
        output += "\n"

        # Response time
        cpu_resp = cpu_phase.get("avg_response_ms", 0)
        req_resp = req_phase.get("avg_response_ms", 0)
        output += (
            f"  Avg Response:     CPU={cpu_resp:.2f}ms  | Request-Rate={req_resp:.2f}ms"
        )
        if req_resp < cpu_resp:
            output += f"  ✅ {((cpu_resp - req_resp) / cpu_resp * 100):.1f}% faster"
        output += "\n"

        # CPU utilization
        cpu_util = cpu_phase.get("avg_cpu", 0)
        req_util = req_phase.get("avg_cpu", 0)
        output += (
            f"  Avg CPU:          CPU={cpu_util:.2f}%  | Request-Rate={req_util:.2f}%\n"
        )

        output += "\n"

    return output


def format_report(
    cpu_metrics: Dict, req_metrics: Dict, winner_analysis: Dict, improvements: Dict
) -> str:
    """Format complete analysis report."""

    output = "\n" + "=" * 80 + "\n"
    output += "🔬 BURST SCENARIO EXPERIMENT ANALYSIS REPORT\n"
    output += "=" * 80 + "\n\n"

    # Summary metrics table
    output += "📈 SUMMARY METRICS COMPARISON\n"
    output += "-" * 80 + "\n"
    output += f"{'Metric':<30} {'CPU Strategy':<20} {'Request-Rate':<20}\n"
    output += "-" * 80 + "\n"

    # Helper to format scale-out latency string
    def fmt_latency(stats: Dict) -> str:
        if stats.get("count", 0) == 0:
            return "N/A"
        return f"avg {stats['mean']:.1f}s | min {stats['min']:.1f}s | max {stats['max']:.1f}s"

    metrics_rows = [
        (
            "Total Requests",
            f"{cpu_metrics['total_requests']}",
            f"{req_metrics['total_requests']}",
        ),
        (
            "Success Rate",
            f"{cpu_metrics['success_rate'] * 100:.1f}%",
            f"{req_metrics['success_rate'] * 100:.1f}%",
        ),
        (
            "Avg Response Time",
            f"{cpu_metrics['avg_response_ms']:.0f}ms",
            f"{req_metrics['avg_response_ms']:.0f}ms",
        ),
        (
            "P95 Response Time",
            f"{cpu_metrics['p95_response_ms']:.0f}ms",
            f"{req_metrics['p95_response_ms']:.0f}ms",
        ),
        (
            "P99 Response Time",
            f"{cpu_metrics['p99_response_ms']:.0f}ms",
            f"{req_metrics['p99_response_ms']:.0f}ms",
        ),
        (
            "Max Instances",
            f"{cpu_metrics['max_capacity']}",
            f"{req_metrics['max_capacity']}",
        ),
        (
            "Scale-Out Events",
            f"{cpu_metrics['scale_out_events']}",
            f"{req_metrics['scale_out_events']}",
        ),
        (
            "Scale-In Events",
            f"{cpu_metrics['scale_in_events']}",
            f"{req_metrics['scale_in_events']}",
        ),
        (
            "Scale-Out Latency",
            fmt_latency(cpu_metrics["scale_out_latency_stats"]),
            fmt_latency(req_metrics["scale_out_latency_stats"]),
        ),
    ]

    for metric, cpu_val, req_val in metrics_rows:
        output += f"{metric:<30} {cpu_val:<20} {req_val:<20}\n"

    output += "\n"

    # Improvements
    output += "📊 PERFORMANCE IMPROVEMENTS (Request-Rate vs CPU)\n"
    output += "-" * 80 + "\n"
    output += f"  Average Response Time:  {improvements['avg_response_improvement_pct']:+.1f}%\n"
    output += f"  P95 Response Time:      {improvements['p95_response_improvement_pct']:+.1f}%\n"
    output += f"  P99 Response Time:      {improvements['p99_response_improvement_pct']:+.1f}%\n"
    output += "\n"

    # Phase-by-phase
    output += format_phase_comparison(cpu_metrics, req_metrics)

    # Winner
    output += "🏆 WINNER ANALYSIS\n"
    output += "=" * 80 + "\n"
    output += f"Winner:      {winner_analysis['winner']}\n"
    output += f"Confidence:  {winner_analysis['confidence_pct']:.1f}%\n"
    output += f"Score:       CPU {winner_analysis['cpu_score']} vs Request-Rate {winner_analysis['req_score']}\n"
    output += "\n"

    output += "📋 REASONING:\n"
    output += "-" * 80 + "\n"
    for i, reason in enumerate(winner_analysis["reasoning"], 1):
        output += f"{i}. {reason}\n"

    output += "\n"

    # Recommendations
    output += "💡 RECOMMENDATIONS\n"
    output += "=" * 80 + "\n"

    if "Request-Rate" in winner_analysis["winner"]:
        output += "✅ Use Request-Rate Strategy for Production\n"
        output += "   • Better P95 latency = improved user experience\n"
        output += "   • Properly scales during burst scenarios\n"
        output += "   • Trade-off: Higher infrastructure cost (more instances)\n"
        output += "   • Consider for: Services where latency SLO matters\n"
    else:
        output += "✅ Use CPU Strategy for Production\n"
        output += "   • More cost-efficient (fewer instances)\n"
        output += "   • Better resource utilization\n"
        output += "   • Trade-off: Higher latency during burst\n"
        output += "   • Consider for: Cost-sensitive services\n"

    output += "\n"

    return output


def main():
    """Execute analysis."""
    results_dir = Path("experiments/results")

    cpu_file = results_dir / "burst_scenario_cpu_results.json"
    req_file = results_dir / "burst_scenario_request_rate_results.json"

    # Check files exist
    if not cpu_file.exists() or not req_file.exists():
        print("❌ Error: Input files not found")
        print(f"   Looking for: {cpu_file} and {req_file}")
        return 1

    print("📂 Loading burst scenario results...")

    # Load and extract
    cpu_data = load_burst_scenario(cpu_file)
    req_data = load_burst_scenario(req_file)

    cpu_metrics = extract_metrics(cpu_data)
    req_metrics = extract_metrics(req_data)

    print("✅ Loaded")
    print(f"   CPU Strategy: {cpu_metrics['total_requests']} requests")
    print(f"   Request-Rate Strategy: {req_metrics['total_requests']} requests")

    # Calculate
    improvements = calculate_improvements(cpu_metrics, req_metrics)
    winner_analysis = determine_winner(cpu_metrics, req_metrics, improvements)

    # Format and print
    report = format_report(cpu_metrics, req_metrics, winner_analysis, improvements)
    print(report)

    # Save to file
    output_file = results_dir / "burst_scenario_analysis_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Report saved to: {output_file}")

    # Also save JSON
    json_output = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cpu_metrics": cpu_metrics,
        "request_rate_metrics": req_metrics,
        "improvements": improvements,
        "winner_analysis": winner_analysis,
    }
    json_file = results_dir / "burst_scenario_analysis.json"
    with open(json_file, "w") as f:
        json.dump(json_output, f, indent=2)

    print(f"✅ JSON saved to: {json_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())