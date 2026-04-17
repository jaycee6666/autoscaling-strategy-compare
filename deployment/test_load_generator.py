"""Phase 3 connectivity check for load generator against ALB."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.load_generator import LoadGenerator


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_alb_dns(alb_config: Dict[str, Any]) -> str:
    for key in ("alb_dns", "alb_dns_name"):
        value = alb_config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise KeyError("Missing ALB DNS in infrastructure/alb-config.json")


def evaluate_success_rate(stats: Dict[str, Any], threshold: float) -> bool:
    total = int(stats.get("total_requests", 0))
    success = int(stats.get("successful_requests", 0))
    if total <= 0:
        return False
    return (success / total) >= threshold


def run_check(
    project_root: Path,
    request_rate: float,
    duration_seconds: int,
    success_threshold: float,
) -> Dict[str, Any]:
    alb_config = read_json(project_root / "infrastructure" / "alb-config.json")
    alb_dns = load_alb_dns(alb_config)
    target_url = f"http://{alb_dns}"

    generator = LoadGenerator(
        target_url=target_url,
        request_rate=request_rate,
        duration_seconds=duration_seconds,
        pattern="constant",
        endpoint="/health",
        method="GET",
        timeout=10,
        max_workers=25,
    )

    stats = generator.generate_load()
    total = int(stats.get("total_requests", 0))
    successful = int(stats.get("successful_requests", 0))
    success_rate = (successful / total) if total > 0 else 0.0
    meets = evaluate_success_rate(stats, threshold=success_threshold)

    report: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_url": target_url,
        "endpoint": "/health",
        "request_rate": request_rate,
        "duration_seconds": duration_seconds,
        "threshold": success_threshold,
        "stats": stats,
        "success_rate": success_rate,
        "meets_threshold": meets,
    }

    output_path = project_root / "deployment" / "load_generator_test_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify load generator against ALB")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root directory",
    )
    parser.add_argument("--request-rate", type=float, default=5.0)
    parser.add_argument("--duration-seconds", type=int, default=20)
    parser.add_argument("--success-threshold", type=float, default=0.8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_check(
        project_root=args.project_root,
        request_rate=args.request_rate,
        duration_seconds=args.duration_seconds,
        success_threshold=args.success_threshold,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["meets_threshold"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
