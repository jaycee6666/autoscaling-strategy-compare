"""Task 2 - Run CPU strategy autoscaling experiment (default 30 minutes)."""

from __future__ import annotations

import argparse
import json
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INFRA_DIR = PROJECT_ROOT / "infrastructure"
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"


@dataclass(frozen=True)
class ExperimentConfig:
    strategy: str
    asg_name: str
    target_group_arn: str
    listener_arn: str
    alb_arn: str
    alb_dns: str
    region: str
    duration_seconds: int
    request_rate_per_second: int
    request_delay_seconds: float
    sample_interval_seconds: int


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _alb_dimension_value(alb_arn: str) -> str:
    # arn:...:loadbalancer/app/name/id -> app/name/id
    return alb_arn.split("loadbalancer/")[-1]


def _target_group_dimension_value(tg_arn: str) -> str:
    # arn:...:targetgroup/name/id -> targetgroup/name/id
    if "targetgroup/" in tg_arn:
        return f"targetgroup/{tg_arn.split('targetgroup/')[-1]}"
    return tg_arn


def _parse_latest_datapoint(response: Dict[str, Any], key: str) -> Optional[float]:
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return None
    latest = sorted(datapoints, key=lambda row: row["Timestamp"])[-1]
    value = latest.get(key)
    return float(value) if value is not None else None


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = min(len(sorted_values) - 1, int(len(sorted_values) * pct))
    return sorted_values[idx]


def _load_config(duration_seconds: int) -> ExperimentConfig:
    asg_config = _read_json(INFRA_DIR / "asg-config.json")
    alb_config = _read_json(INFRA_DIR / "alb-config.json")
    return ExperimentConfig(
        strategy="cpu",
        asg_name=asg_config["cpu_asg_name"],
        target_group_arn=alb_config["cpu_target_group_arn"],
        listener_arn=alb_config["listener_arn"],
        alb_arn=alb_config["alb_arn"],
        alb_dns=alb_config["alb_dns"],
        region="us-east-1",
        duration_seconds=duration_seconds,
        request_rate_per_second=10,
        request_delay_seconds=0.3,
        sample_interval_seconds=30,
    )


class CpuExperimentRunner:
    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.autoscaling = boto3.client("autoscaling", region_name=config.region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=config.region)
        self.elbv2 = boto3.client("elbv2", region_name=config.region)

        self.load_results: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times_ms": [],
            "errors": [],
        }
        self.metric_samples: List[Dict[str, Any]] = []

    def _route_listener(self) -> None:
        self.elbv2.modify_listener(
            ListenerArn=self.config.listener_arn,
            DefaultActions=[
                {
                    "Type": "forward",
                    "TargetGroupArn": self.config.target_group_arn,
                }
            ],
        )

    def _set_desired_capacity(self) -> None:
        self.autoscaling.set_desired_capacity(
            AutoScalingGroupName=self.config.asg_name,
            DesiredCapacity=2,
            HonorCooldown=False,
        )

    def _run_load(self, stop_time: float) -> None:
        url = f"http://{self.config.alb_dns}/request"
        interval = 1.0 / self.config.request_rate_per_second
        progress_interval = 60  # Print progress every 60 seconds
        last_progress = time.time()

        print(f"[{datetime.now(timezone.utc).isoformat()}] Load generation started")
        print(f"  Target: {self.config.request_rate_per_second} req/s")
        print(
            f"  Duration: {self.config.duration_seconds} seconds ({self.config.duration_seconds // 60} min)"
        )
        print(f"  URL: http://{self.config.alb_dns}/request")
        print()

        while time.time() < stop_time:
            request_started = time.perf_counter()
            try:
                response = requests.post(
                    url,
                    json={"delay": self.config.request_delay_seconds},
                    timeout=5,
                )
                elapsed_ms = (time.perf_counter() - request_started) * 1000.0
                self.load_results["total_requests"] += 1
                self.load_results["response_times_ms"].append(elapsed_ms)
                if 200 <= response.status_code < 300:
                    self.load_results["successful_requests"] += 1
                else:
                    self.load_results["failed_requests"] += 1
                    self.load_results["errors"].append(f"HTTP {response.status_code}")
            except Exception as exc:  # pragma: no cover - depends on runtime network
                self.load_results["total_requests"] += 1
                self.load_results["failed_requests"] += 1
                self.load_results["errors"].append(str(exc))

            # Print progress every 60 seconds
            now = time.time()
            if now - last_progress >= progress_interval:
                elapsed = now - (stop_time - self.config.duration_seconds)
                success_rate = (
                    self.load_results["successful_requests"]
                    / self.load_results["total_requests"]
                    if self.load_results["total_requests"]
                    else 0.0
                )
                avg_time = (
                    sum(self.load_results["response_times_ms"])
                    / len(self.load_results["response_times_ms"])
                    if self.load_results["response_times_ms"]
                    else 0.0
                )
                print(
                    f"[{elapsed:.0f}s/{self.config.duration_seconds}s] "
                    f"Requests: {self.load_results['total_requests']} | "
                    f"Success: {success_rate * 100:.1f}% | "
                    f"Avg time: {avg_time:.0f}ms"
                )
                last_progress = now

            remaining = interval - (time.perf_counter() - request_started)
            if remaining > 0:
                time.sleep(remaining)

    def _collect_sample(self) -> Dict[str, Any]:
        asg_resp = self.autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[self.config.asg_name]
        )
        groups = asg_resp.get("AutoScalingGroups", [])
        desired = 0
        in_service = 0
        if groups:
            asg = groups[0]
            desired = int(asg.get("DesiredCapacity", 0))
            in_service = sum(
                1
                for instance in asg.get("Instances", [])
                if instance.get("LifecycleState") == "InService"
            )

        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=5)
        cpu_resp = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[
                {"Name": "AutoScalingGroupName", "Value": self.config.asg_name}
            ],
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Average"],
        )
        cpu_avg = _parse_latest_datapoint(cpu_resp, "Average")

        alb_resp = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/ApplicationELB",
            MetricName="TargetResponseTime",
            Dimensions=[
                {
                    "Name": "LoadBalancer",
                    "Value": _alb_dimension_value(self.config.alb_arn),
                },
                {
                    "Name": "TargetGroup",
                    "Value": _target_group_dimension_value(
                        self.config.target_group_arn
                    ),
                },
            ],
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Average"],
        )
        alb_target_response_time = _parse_latest_datapoint(alb_resp, "Average")

        request_count_resp = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/ApplicationELB",
            MetricName="RequestCount",
            Dimensions=[
                {
                    "Name": "LoadBalancer",
                    "Value": _alb_dimension_value(self.config.alb_arn),
                }
            ],
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Sum"],
        )
        alb_request_count = _parse_latest_datapoint(request_count_resp, "Sum")

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "desired_capacity": desired,
            "in_service_instances": in_service,
            "cpu_utilization_avg": cpu_avg,
            "alb_target_response_time_seconds": alb_target_response_time,
            "alb_request_count_sum_1m": alb_request_count,
        }

    def _collect_metrics_loop(self, stop_time: float) -> None:
        while time.time() < stop_time:
            try:
                self.metric_samples.append(self._collect_sample())
            except Exception as exc:  # pragma: no cover - runtime AWS variance
                self.metric_samples.append(
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "collection_error": str(exc),
                    }
                )
            time.sleep(self.config.sample_interval_seconds)

    def run(self) -> Dict[str, Any]:
        print(f"\n{'=' * 70}")
        print(f"CPU Strategy Experiment Starting")
        print(f"{'=' * 70}")
        print(f"ASG: {self.config.asg_name}")
        print(f"ALB: {self.config.alb_dns}")
        print(f"Region: {self.config.region}")
        print(f"Target: {self.config.request_rate_per_second} requests/second")
        print(f"Duration: {self.config.duration_seconds // 60} minutes")
        print(f"{'=' * 70}\n")

        self._route_listener()
        self._set_desired_capacity()

        started_at = datetime.now(timezone.utc)
        stop_time = time.time() + self.config.duration_seconds

        load_thread = threading.Thread(target=self._run_load, args=(stop_time,))
        metrics_thread = threading.Thread(
            target=self._collect_metrics_loop, args=(stop_time,)
        )

        load_thread.start()
        metrics_thread.start()
        load_thread.join()
        metrics_thread.join()

        print(f"\n{'=' * 70}")
        print(f"Experiment Complete! Collecting final results...")
        print(f"{'=' * 70}\n")

        ended_at = datetime.now(timezone.utc)
        times = [float(v) for v in self.load_results["response_times_ms"]]
        success_rate = (
            self.load_results["successful_requests"]
            / self.load_results["total_requests"]
            if self.load_results["total_requests"]
            else 0.0
        )

        capacities = [
            sample["desired_capacity"]
            for sample in self.metric_samples
            if "desired_capacity" in sample
        ]
        cpus = [
            float(sample["cpu_utilization_avg"])
            for sample in self.metric_samples
            if sample.get("cpu_utilization_avg") is not None
        ]
        scale_out_events = sum(
            1
            for index in range(1, len(capacities))
            if capacities[index] > capacities[index - 1]
        )
        scale_in_events = sum(
            1
            for index in range(1, len(capacities))
            if capacities[index] < capacities[index - 1]
        )

        return {
            "experiment": {
                "strategy": self.config.strategy,
                "asg_name": self.config.asg_name,
                "alb_dns": self.config.alb_dns,
                "region": self.config.region,
                "duration_seconds": self.config.duration_seconds,
                "request_rate_per_second": self.config.request_rate_per_second,
                "request_delay_seconds": self.config.request_delay_seconds,
                "started_at_utc": started_at.isoformat(),
                "ended_at_utc": ended_at.isoformat(),
            },
            "load_summary": {
                "total_requests": self.load_results["total_requests"],
                "successful_requests": self.load_results["successful_requests"],
                "failed_requests": self.load_results["failed_requests"],
                "success_rate": success_rate,
                "avg_response_time_ms": statistics.mean(times) if times else 0.0,
                "p95_response_time_ms": _percentile(times, 0.95),
                "p99_response_time_ms": _percentile(times, 0.99),
            },
            "scaling_summary": {
                "sample_count": len(self.metric_samples),
                "avg_desired_capacity": statistics.mean(capacities)
                if capacities
                else 0.0,
                "max_desired_capacity": max(capacities) if capacities else 0,
                "min_desired_capacity": min(capacities) if capacities else 0,
                "scale_out_events": scale_out_events,
                "scale_in_events": scale_in_events,
                "avg_cpu_utilization": statistics.mean(cpus) if cpus else 0.0,
                "max_cpu_utilization": max(cpus) if cpus else 0.0,
            },
            "metric_samples": self.metric_samples,
            "load_errors": self.load_results["errors"][:100],
            "notes": [
                "No AWS CLI subprocess used; boto3-only implementation.",
                "If CloudWatch datapoints are delayed, some sample values may be null.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-seconds", type=int, default=1800)
    args = parser.parse_args()

    config = _load_config(duration_seconds=args.duration_seconds)
    runner = CpuExperimentRunner(config)
    result = runner.run()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "cpu_strategy_metrics.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(f"Saved: {output_path}")
    print(json.dumps(result["load_summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
