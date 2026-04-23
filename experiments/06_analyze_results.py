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
    started_at_utc: Optional[str]
    metric_samples: List[Dict[str, Any]]


def _parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _estimate_scale_out_latency_seconds(results: ExperimentResults) -> Optional[float]:
    start = _parse_timestamp(results.started_at_utc)
    if start is None:
        return None

    capacities = [
        sample.get("desired_capacity")
        for sample in results.metric_samples
        if sample.get("desired_capacity") is not None
    ]
    if len(capacities) < 2:
        return None

    baseline = capacities[0]
    for sample in results.metric_samples:
        desired = sample.get("desired_capacity")
        if desired is None:
            continue
        if desired > baseline:
            sample_time = _parse_timestamp(sample.get("timestamp_utc"))
            if sample_time is None:
                return None
            return max(0.0, (sample_time - start).total_seconds())
    return None


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
        started_at_utc=data.get("experiment", {}).get("started_at_utc"),
        metric_samples=metric_samples,
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

    # Proposal-aligned evaluation metrics
    cpu_error_rate = 1.0 - cpu_results.success_rate
    req_error_rate = 1.0 - request_results.success_rate
    cpu_scale_out_latency = _estimate_scale_out_latency_seconds(cpu_results)
    req_scale_out_latency = _estimate_scale_out_latency_seconds(request_results)

    analysis["proposal_metrics"] = {
        "cpu_strategy": {
            "error_rate_pct": cpu_error_rate * 100,
            "p95_response_time_ms": cpu_results.p95_response_time_ms,
            "scale_out_latency_seconds": cpu_scale_out_latency,
        },
        "request_rate_strategy": {
            "error_rate_pct": req_error_rate * 100,
            "p95_response_time_ms": request_results.p95_response_time_ms,
            "scale_out_latency_seconds": req_scale_out_latency,
        },
    }

    analysis["proposal_alignment"] = {
        "has_scaling_phase": bool(
            cpu_results.scale_out_events > 0 or request_results.scale_out_events > 0
        ),
        "notes": [
            "Proposal requires evaluating P95 latency, scale-out latency, and error rate during scale-out phase.",
            "If no scale-out occurs, result is marked inconclusive for proposal validation.",
        ],
    }

    # Determine winner using proposal criteria first
    if cpu_results.scale_out_events == 0 and request_results.scale_out_events == 0:
        analysis["winner"] = {
            "strategy": "Inconclusive",
            "confidence_pct": 0.0,
            "rationale": (
                "Neither strategy triggered scale-out events, so proposal hypotheses "
                "about scale-out behavior cannot be validated from this run."
            ),
        }
        return analysis

    # Weighted proposal score: lower is better
    cpu_score = cpu_results.p95_response_time_ms * 0.45 + cpu_error_rate * 10000 * 0.4
    req_score = request_results.p95_response_time_ms * 0.45 + req_error_rate * 10000 * 0.4

    if cpu_scale_out_latency is not None and req_scale_out_latency is not None:
        cpu_score += cpu_scale_out_latency * 0.15
        req_score += req_scale_out_latency * 0.15

    if cpu_score < req_score:
        winner = "CPU Strategy"
        loser_score = req_score
        winner_score = cpu_score
    else:
        winner = "Request-Rate Strategy"
        loser_score = cpu_score
        winner_score = req_score

    margin = max(0.0, loser_score - winner_score)
    confidence = (margin / max(loser_score, 1.0)) * 100

    analysis["winner"] = {
        "strategy": winner,
        "confidence_pct": confidence,
        "rationale": _generate_rationale(winner, cpu_results, request_results),
    }

    return analysis


def _generate_rationale(
    winner: str, cpu_results: ExperimentResults, request_results: ExperimentResults
) -> str:
    """Generate human-readable explanation for winner."""

    if "CPU" in winner:
        if cpu_results.p95_response_time_ms < request_results.p95_response_time_ms:
            reason = (
                f"CPU strategy achieved lower P95 latency "
                f"({cpu_results.p95_response_time_ms:.0f}ms vs {request_results.p95_response_time_ms:.0f}ms)"
            )
        elif cpu_results.success_rate > request_results.success_rate:
            reason = (
                f"CPU strategy achieved lower error rate "
                f"({(1-cpu_results.success_rate)*100:.2f}% vs {(1-request_results.success_rate)*100:.2f}%)"
            )
        else:
            reason = "CPU strategy performed better on proposal-weighted latency and reliability metrics"
    else:
        if request_results.p95_response_time_ms < cpu_results.p95_response_time_ms:
            reason = (
                f"Request-rate strategy achieved lower P95 latency "
                f"({request_results.p95_response_time_ms:.0f}ms vs {cpu_results.p95_response_time_ms:.0f}ms)"
            )
        elif request_results.success_rate > cpu_results.success_rate:
            reason = (
                f"Request-rate strategy achieved lower error rate "
                f"({(1-request_results.success_rate)*100:.2f}% vs {(1-cpu_results.success_rate)*100:.2f}%)"
            )
        else:
            reason = "Request-rate strategy performed better on proposal-weighted latency and reliability metrics"

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
