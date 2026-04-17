"""Phase 6: Analyze experimental results and generate comparison report.

This script reads output from experiments/results/ and produces:
1. Detailed metrics comparison
2. Winner determination
3. Visualization-ready data structures
4. Formatted comparison tables
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentResults:
    """Container for parsed experiment results."""

    strategy: str
    total_requests: int
    success_rate: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_capacity: int
    avg_capacity: float
    scale_out_events: int
    scale_in_events: int
    avg_cpu_utilization: float
    collection_errors: List[str]


def load_experiment_results(json_file: Path) -> ExperimentResults:
    """Load and parse experiment results from JSON file."""
    with open(json_file) as f:
        data = json.load(f)

    load_summary = data.get("load_summary", {})
    scaling_summary = data.get("scaling_summary", {})
    metric_samples = data.get("metric_samples", [])
    load_errors = data.get("load_errors", [])

    return ExperimentResults(
        strategy=data.get("experiment", {}).get("strategy", "unknown"),
        total_requests=load_summary.get("total_requests", 0),
        success_rate=load_summary.get("success_rate", 0.0),
        avg_response_time_ms=load_summary.get("avg_response_time_ms", 0.0),
        p95_response_time_ms=load_summary.get("p95_response_time_ms", 0.0),
        p99_response_time_ms=load_summary.get("p99_response_time_ms", 0.0),
        max_capacity=scaling_summary.get("max_desired_capacity", 0),
        avg_capacity=scaling_summary.get("avg_desired_capacity", 0.0),
        scale_out_events=scaling_summary.get("scale_out_events", 0),
        scale_in_events=scaling_summary.get("scale_in_events", 0),
        avg_cpu_utilization=scaling_summary.get("avg_cpu_utilization", 0.0),
        collection_errors=load_errors,
    )


def analyze_results(
    cpu_results: ExperimentResults, request_results: ExperimentResults
) -> Dict[str, Any]:
    """Compare two experiment results and determine winner."""

    analysis = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "comparison": {
            "cpu_strategy": {
                "strategy": "CPU Utilization Target",
                "total_requests": cpu_results.total_requests,
                "success_rate": cpu_results.success_rate,
                "avg_response_time_ms": cpu_results.avg_response_time_ms,
                "p95_response_time_ms": cpu_results.p95_response_time_ms,
                "p99_response_time_ms": cpu_results.p99_response_time_ms,
                "max_instances": cpu_results.max_capacity,
                "avg_instances": cpu_results.avg_capacity,
                "scale_out_events": cpu_results.scale_out_events,
                "scale_in_events": cpu_results.scale_in_events,
                "avg_cpu_utilization": cpu_results.avg_cpu_utilization,
            },
            "request_rate_strategy": {
                "strategy": "Request Rate Target",
                "total_requests": request_results.total_requests,
                "success_rate": request_results.success_rate,
                "avg_response_time_ms": request_results.avg_response_time_ms,
                "p95_response_time_ms": request_results.p95_response_time_ms,
                "p99_response_time_ms": request_results.p99_response_time_ms,
                "max_instances": request_results.max_capacity,
                "avg_instances": request_results.avg_capacity,
                "scale_out_events": request_results.scale_out_events,
                "scale_in_events": request_results.scale_in_events,
                "avg_cpu_utilization": request_results.avg_cpu_utilization,
            },
        },
        "metrics": {},
    }

    # Calculate comparative metrics
    cpu_cost_factor = cpu_results.max_capacity * 3600  # instance-seconds
    req_cost_factor = request_results.max_capacity * 3600

    cpu_latency_score = (
        cpu_results.avg_response_time_ms * 0.4
        + cpu_results.p95_response_time_ms * 0.4
        + cpu_results.p99_response_time_ms * 0.2
    )
    req_latency_score = (
        request_results.avg_response_time_ms * 0.4
        + request_results.p95_response_time_ms * 0.4
        + request_results.p99_response_time_ms * 0.2
    )

    analysis["metrics"]["cpu_strategy"] = {
        "cost_factor": cpu_cost_factor,
        "cost_per_request": cpu_cost_factor / cpu_results.total_requests
        if cpu_results.total_requests
        else 0,
        "latency_score": cpu_latency_score,
        "success_rate_pct": cpu_results.success_rate * 100,
    }
    analysis["metrics"]["request_rate_strategy"] = {
        "cost_factor": req_cost_factor,
        "cost_per_request": req_cost_factor / request_results.total_requests
        if request_results.total_requests
        else 0,
        "latency_score": req_latency_score,
        "success_rate_pct": request_results.success_rate * 100,
    }

    # Determine winner
    cpu_score = (
        1 - (cpu_latency_score / (cpu_latency_score + req_latency_score + 0.001))
    ) * 50 + (1 - (cpu_cost_factor / (cpu_cost_factor + req_cost_factor + 1))) * 50
    req_score = 100 - cpu_score

    if cpu_score > req_score:
        winner = "CPU Strategy"
        winner_margin = cpu_score - req_score
    else:
        winner = "Request-Rate Strategy"
        winner_margin = req_score - cpu_score

    analysis["winner"] = {
        "strategy": winner,
        "confidence_pct": winner_margin,
        "rationale": _generate_rationale(winner, cpu_results, request_results),
    }

    return analysis


def _generate_rationale(
    winner: str, cpu_results: ExperimentResults, request_results: ExperimentResults
) -> str:
    """Generate human-readable explanation for winner."""

    if "CPU" in winner:
        if cpu_results.max_capacity < request_results.max_capacity:
            reason = f"CPU strategy used fewer instances ({cpu_results.max_capacity} vs {request_results.max_capacity}), reducing costs"
        elif cpu_results.avg_response_time_ms < request_results.avg_response_time_ms:
            reason = f"CPU strategy achieved better response time ({cpu_results.avg_response_time_ms:.0f}ms vs {request_results.avg_response_time_ms:.0f}ms)"
        else:
            reason = "CPU strategy provided better overall efficiency and response characteristics"
    else:
        if request_results.max_capacity < cpu_results.max_capacity:
            reason = f"Request-rate strategy used fewer instances ({request_results.max_capacity} vs {cpu_results.max_capacity}), reducing costs"
        elif request_results.avg_response_time_ms < cpu_results.avg_response_time_ms:
            reason = f"Request-rate strategy achieved better response time ({request_results.avg_response_time_ms:.0f}ms vs {cpu_results.avg_response_time_ms:.0f}ms)"
        else:
            reason = "Request-rate strategy provided better overall efficiency and response characteristics"

    return reason


def main() -> int:
    """Execute Phase 6 analysis."""
    results_dir = Path("experiments/results")

    # Input files
    cpu_file = results_dir / "cpu_strategy_metrics.json"
    request_file = results_dir / "request_rate_experiment_metrics.json"

    # Output files
    analysis_file = results_dir / "analysis_report.json"

    # Check input files exist
    if not cpu_file.exists():
        print(f"ERROR: {cpu_file} not found")
        return 1
    if not request_file.exists():
        print(f"ERROR: {request_file} not found")
        return 1

    print("Phase 6: Analyzing experimental results...")
    print()

    # Load results
    cpu_results = load_experiment_results(cpu_file)
    request_results = load_experiment_results(request_file)

    print(f"CPU Strategy Results:")
    print(f"  Total Requests: {cpu_results.total_requests}")
    print(f"  Success Rate: {cpu_results.success_rate * 100:.1f}%")
    print(f"  Avg Response Time: {cpu_results.avg_response_time_ms:.0f}ms")
    print(f"  Max Capacity: {cpu_results.max_capacity} instances")
    print()

    print(f"Request-Rate Strategy Results:")
    print(f"  Total Requests: {request_results.total_requests}")
    print(f"  Success Rate: {request_results.success_rate * 100:.1f}%")
    print(f"  Avg Response Time: {request_results.avg_response_time_ms:.0f}ms")
    print(f"  Max Capacity: {request_results.max_capacity} instances")
    print()

    # Analyze
    analysis = analyze_results(cpu_results, request_results)

    # Output
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)

    winner = analysis["winner"]["strategy"]
    confidence = analysis["winner"]["confidence_pct"]
    rationale = analysis["winner"]["rationale"]

    print(f"WINNER: {winner} (Confidence: {confidence:.1f}%)")
    print(f"Reason: {rationale}")
    print()
    print(f"Analysis saved to: {analysis_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
