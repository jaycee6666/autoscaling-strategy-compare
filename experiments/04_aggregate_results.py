"""Task 4 - Aggregate experiment outputs into JSON + CSV comparison report."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
CPU_FILE = RESULTS_DIR / "cpu_strategy_metrics.json"
REQ_FILE = RESULTS_DIR / "request_rate_experiment_metrics.json"
REPORT_FILE = RESULTS_DIR / "comparison_report.json"
CSV_FILE = RESULTS_DIR / "metrics_comparison.csv"


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _pct_improvement(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return 0.0
    return (baseline - candidate) / baseline * 100.0


def build_report(cpu: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
    cpu_load = cpu.get("load_summary", {})
    req_load = request.get("load_summary", {})
    cpu_scale = cpu.get("scaling_summary", {})
    req_scale = request.get("scaling_summary", {})

    comparison_metrics = {
        "success_rate_cpu": _safe_float(cpu_load.get("success_rate")),
        "success_rate_request": _safe_float(req_load.get("success_rate")),
        "avg_response_time_ms_cpu": _safe_float(cpu_load.get("avg_response_time_ms")),
        "avg_response_time_ms_request": _safe_float(
            req_load.get("avg_response_time_ms")
        ),
        "p95_response_time_ms_cpu": _safe_float(cpu_load.get("p95_response_time_ms")),
        "p95_response_time_ms_request": _safe_float(
            req_load.get("p95_response_time_ms")
        ),
        "p99_response_time_ms_cpu": _safe_float(cpu_load.get("p99_response_time_ms")),
        "p99_response_time_ms_request": _safe_float(
            req_load.get("p99_response_time_ms")
        ),
        "avg_cpu_utilization_cpu": _safe_float(cpu_scale.get("avg_cpu_utilization")),
        "avg_cpu_utilization_request": _safe_float(
            req_scale.get("avg_cpu_utilization")
        ),
        "max_desired_capacity_cpu": _safe_float(cpu_scale.get("max_desired_capacity")),
        "max_desired_capacity_request": _safe_float(
            req_scale.get("max_desired_capacity")
        ),
        "scale_out_events_cpu": _safe_float(cpu_scale.get("scale_out_events")),
        "scale_out_events_request": _safe_float(req_scale.get("scale_out_events")),
    }

    findings = {
        "better_success_rate": (
            "request_rate"
            if comparison_metrics["success_rate_request"]
            >= comparison_metrics["success_rate_cpu"]
            else "cpu"
        ),
        "better_p95_latency": (
            "request_rate"
            if comparison_metrics["p95_response_time_ms_request"]
            <= comparison_metrics["p95_response_time_ms_cpu"]
            else "cpu"
        ),
        "p95_latency_improvement_percent_request_vs_cpu": _pct_improvement(
            comparison_metrics["p95_response_time_ms_cpu"],
            comparison_metrics["p95_response_time_ms_request"],
        ),
        "avg_latency_improvement_percent_request_vs_cpu": _pct_improvement(
            comparison_metrics["avg_response_time_ms_cpu"],
            comparison_metrics["avg_response_time_ms_request"],
        ),
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "cpu_metrics_file": str(CPU_FILE),
            "request_metrics_file": str(REQ_FILE),
        },
        "comparison_metrics": comparison_metrics,
        "findings": findings,
        "notes": [
            "At least 8 comparison metrics are included for Phase 6 analysis.",
            "Values default to 0.0 if missing in source files.",
        ],
    }


def write_csv(report: Dict[str, Any], csv_path: Path) -> None:
    metrics = report["comparison_metrics"]
    rows = [
        ["metric", "cpu_strategy", "request_rate_strategy"],
        [
            "success_rate",
            metrics["success_rate_cpu"],
            metrics["success_rate_request"],
        ],
        [
            "avg_response_time_ms",
            metrics["avg_response_time_ms_cpu"],
            metrics["avg_response_time_ms_request"],
        ],
        [
            "p95_response_time_ms",
            metrics["p95_response_time_ms_cpu"],
            metrics["p95_response_time_ms_request"],
        ],
        [
            "p99_response_time_ms",
            metrics["p99_response_time_ms_cpu"],
            metrics["p99_response_time_ms_request"],
        ],
        [
            "avg_cpu_utilization",
            metrics["avg_cpu_utilization_cpu"],
            metrics["avg_cpu_utilization_request"],
        ],
        [
            "max_desired_capacity",
            metrics["max_desired_capacity_cpu"],
            metrics["max_desired_capacity_request"],
        ],
        [
            "scale_out_events",
            metrics["scale_out_events_cpu"],
            metrics["scale_out_events_request"],
        ],
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def main() -> int:
    cpu = _read_json(CPU_FILE)
    request = _read_json(REQ_FILE)
    report = build_report(cpu, request)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    write_csv(report, CSV_FILE)

    print(f"Saved: {REPORT_FILE}")
    print(f"Saved: {CSV_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
