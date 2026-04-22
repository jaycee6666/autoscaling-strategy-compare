"""Task 5 - Run burst/spike scenario experiment (45-50 minutes total).

This experiment tests autoscaling strategies under real-world burst traffic patterns.

Phases:
- Preheating (5 min):  Stabilize at baseline request rate
- Baseline (10 min):   Normal load (10 req/s) - observe behavior
- Burst (15 min):      High load (50 req/s) - observe scaling response
- Recovery (10 min):   Back to baseline - observe scale-down

Expected outcome: Shows which strategy responds faster to burst traffic and scales down more efficiently.
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
import requests

# Fix Windows encoding (GBK -> UTF-8) and enable line buffering for real-time output
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", line_buffering=True
    )


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INFRA_DIR = PROJECT_ROOT / "infrastructure"
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"


@dataclass(frozen=True)
class BurstPhaseConfig:
    """Configuration for a single phase in the burst scenario."""

    phase_name: str
    duration_seconds: int
    request_rate_per_second: int
    request_delay_seconds: float


@dataclass(frozen=True)
class BurstExperimentConfig:
    """Configuration for burst scenario experiment."""

    strategy: str
    asg_name: str
    target_group_arn: str
    listener_arn: str
    alb_arn: str
    alb_dns: str
    region: str
    sample_interval_seconds: int
    phases: List[BurstPhaseConfig]


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _alb_dimension_value(alb_arn: str) -> str:
    return alb_arn.split("loadbalancer/")[-1]


def _target_group_dimension_value(tg_arn: str) -> str:
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


def _load_config_cpu() -> BurstExperimentConfig:
    """Load configuration for CPU strategy burst scenario."""
    asg_config = _read_json(INFRA_DIR / "asg-config.json")
    alb_config = _read_json(INFRA_DIR / "alb-config.json")

    # phases = [
    #     BurstPhaseConfig("Preheating", 300, 10, 0.3),  # 5 min: warm up
    #     BurstPhaseConfig("Baseline", 600, 10, 0.3),  # 10 min: normal load
    #     BurstPhaseConfig("Burst", 900, 50, 0.3),  # 15 min: 5x traffic spike
    #     BurstPhaseConfig("Recovery", 600, 10, 0.3),  # 10 min: back to normal
    # ]
    phases = [
        BurstPhaseConfig(
            "Preheating", 300, 15, 0.3
        ),  # 5 min: warm up (15 req/s - exceeds 10.0 target)
        BurstPhaseConfig("Baseline", 600, 15, 0.3),  # 10 min: normal load
        BurstPhaseConfig(
            "Burst", 900, 50, 0.05
        ),  # 15 min: heavy burst (50 req/s - should trigger scaling)
        BurstPhaseConfig("Recovery", 600, 15, 0.3),  # 10 min: back to normal
    ]

    return BurstExperimentConfig(
        strategy="cpu",
        asg_name=asg_config["cpu_asg_name"],
        target_group_arn=alb_config["cpu_target_group_arn"],
        listener_arn=alb_config["listener_arn"],
        alb_arn=alb_config["alb_arn"],
        alb_dns=alb_config["alb_dns"],
        region="us-east-1",
        # sample_interval_seconds=30,
        sample_interval_seconds=15,
        phases=phases,
    )


def _load_config_request_rate() -> BurstExperimentConfig:
    """Load configuration for Request-Rate strategy burst scenario."""
    asg_config = _read_json(INFRA_DIR / "asg-config.json")
    alb_config = _read_json(INFRA_DIR / "alb-config.json")

    # phases = [
    #     BurstPhaseConfig("Preheating", 300, 10, 0.3),  # 5 min: warm up
    #     BurstPhaseConfig("Baseline", 600, 10, 0.3),  # 10 min: normal load
    #     BurstPhaseConfig("Burst", 900, 50, 0.3),  # 15 min: 5x traffic spike
    #     BurstPhaseConfig("Recovery", 600, 10, 0.3),  # 10 min: back to normal
    # ]
    phases = [
        BurstPhaseConfig(
            "Preheating", 300, 15, 0.3
        ),  # 5 min: warm up (15 req/s - exceeds 10.0 target)
        BurstPhaseConfig("Baseline", 600, 15, 0.3),  # 10 min: normal load
        BurstPhaseConfig(
            "Burst", 900, 50, 0.05
        ),  # 15 min: heavy burst (50 req/s - should trigger scaling)
        BurstPhaseConfig("Recovery", 600, 15, 0.3),  # 10 min: back to normal
    ]

    return BurstExperimentConfig(
        strategy="request_rate",
        asg_name=asg_config["request_asg_name"],
        target_group_arn=alb_config["request_target_group_arn"],
        listener_arn=alb_config["listener_arn"],
        alb_arn=alb_config["alb_arn"],
        alb_dns=alb_config["alb_dns"],
        region="us-east-1",
        sample_interval_seconds=15,  # P0 Fix: Unified sampling interval (was 30s, now 15s like CPU)
        phases=phases,
    )


class BurstScenarioRunner:
    """Run burst scenario experiment for a given autoscaling strategy."""

    def __init__(self, config: BurstExperimentConfig) -> None:
        self.config = config
        self.autoscaling = boto3.client("autoscaling", region_name=config.region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=config.region)
        self.elbv2 = boto3.client("elbv2", region_name=config.region)

        self.load_results: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times_ms": [],
            "phase_results": {},
            "errors": [],
        }
        self.metric_samples: List[Dict[str, Any]] = []
        self.phase_metric_samples: Dict[str, List[Dict[str, Any]]] = {
            phase.phase_name: [] for phase in config.phases
        }

        # Scale-out latency tracking (for Burst phase)
        self.baseline_capacity: Optional[int] = None
        # RPS tracking via deque
        self._request_timestamps: deque = deque()  # timestamps of completed requests
        self.burst_start_time: Optional[float] = None
        self.scale_out_events: List[
            Dict[str, Any]
        ] = []  # Track scale-out events with timestamps
        self.previous_capacity: Optional[int] = None
        self.previous_healthy_count: Optional[int] = (
            None  # Track healthy target count for precise latency measurement
        )

        # User Fix: Set cooldown to 0 for fast scaling response in burst scenario
        try:
            self.autoscaling.update_auto_scaling_group(
                AutoScalingGroupName=self.config.asg_name, DefaultCooldown=0
            )
            print(f"✓ Set ASG {self.config.asg_name} cooldown to 0 seconds")
        except Exception as e:
            print(f"⚠️ Failed to set cooldown for {self.config.asg_name}: {e}")

    def _check_target_group_health(self) -> int:
        """P0 Fix #1: Check ALB target group health to detect instance readiness.

        Returns the count of targets currently in 'healthy' state.
        Used to detect when new instances become available (not just desired_capacity).
        """
        try:
            response = self.elbv2.describe_target_health(
                TargetGroupArn=self.config.target_group_arn
            )
            healthy_count = sum(
                1
                for target in response.get("TargetHealthDescriptions", [])
                if target.get("TargetHealth", {}).get("State") == "healthy"
            )
            return healthy_count
        except Exception as e:
            print(f"  [Warning] Failed to check target group health: {e}")
            return 0

    def _route_listener(self) -> None:
        """Route ALB listener to this strategy's target group."""
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
        """Initialize ASG to 1 instance."""
        self.autoscaling.set_desired_capacity(
            AutoScalingGroupName=self.config.asg_name,
            DesiredCapacity=1,
            HonorCooldown=False,
        )

    def _wait_for_target_capacity(
        self,
        max_wait_seconds: int = 300,
        check_interval: int = 5,
    ) -> bool:
        """
        等待 ASG 中的所有实例都变为 Healthy 且 InService

        Args:
            max_wait_seconds: 最长等待时间（秒）
            check_interval: 检查间隔（秒）

        Returns:
            True 如果在时间内全部 healthy，False 如果超时
        """
        print(
            f"\n[Setup] Waiting for ASG '{self.config.asg_name}' "
            f"to reach target capacity with all instances Healthy + InService..."
        )

        start_time = time.time()
        target_count = 1  # initial_capacity=1

        while time.time() - start_time < max_wait_seconds:
            try:
                asg = self.autoscaling.describe_auto_scaling_groups(
                    AutoScalingGroupNames=[self.config.asg_name]
                )
                if not asg.get("AutoScalingGroups"):
                    print(f"  [X] ASG '{self.config.asg_name}' not found")
                    time.sleep(check_interval)
                    continue

                asg_info = asg["AutoScalingGroups"][0]
                instances = asg_info.get("Instances", [])
                current_count = len(instances)
                desired = asg_info.get("DesiredCapacity", 0)

                # 筛选 Healthy + InService
                healthy_instances = [
                    inst
                    for inst in instances
                    if inst.get("HealthStatus") == "Healthy"
                    and inst.get("LifecycleState") == "InService"
                ]
                healthy_count = len(healthy_instances)

                elapsed = int(time.time() - start_time)
                print(
                    f"  [{elapsed}s] Total: {current_count}, "
                    f"Healthy+InService: {healthy_count}/{target_count}, "
                    f"Desired: {desired}"
                )

                # 成功条件：实例数达到目标 AND 全部 healthy
                if current_count == target_count and healthy_count == target_count:
                    print(
                        f"  [OK] All {target_count} instance(s) are Healthy and InService!"
                    )
                    return True

                time.sleep(check_interval)

            except Exception as e:
                print(f"  [X] Error checking ASG status: {e}")
                time.sleep(check_interval)

        # 超时
        print(f"  [X] Timeout after {max_wait_seconds}s - not all instances healthy")
        return False

    def _make_single_request(self, url: str, phase: BurstPhaseConfig) -> None:
        """Make a single HTTP request and record results."""
        request_started = time.perf_counter()

        try:
            # CPU duration varies by strategy:
            # - CPU strategy: 1 second (to generate high CPU utilization)
            # - Request Rate strategy: 0.01 seconds (to maximize request throughput)
            cpu_duration = 0.01 if self.config.strategy == "request_rate" else 1

            response = requests.post(
                url,
                json={"duration": cpu_duration},
                timeout=10,
            )
            elapsed_ms = (time.perf_counter() - request_started) * 1000.0
            self.load_results["total_requests"] += 1
            self.load_results["response_times_ms"].append(elapsed_ms)

            # Track timestamp for RPS calculation
            self._request_timestamps.append(time.perf_counter())

            if 200 <= response.status_code < 300:
                self.load_results["successful_requests"] += 1
            else:
                self.load_results["failed_requests"] += 1
                self.load_results["errors"].append(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status_code": response.status_code,
                    }
                )
        except Exception as e:
            self.load_results["failed_requests"] += 1
            self.load_results["errors"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                }
            )

    def _run_load_phase(
        self,
        phase: BurstPhaseConfig,
        stop_time: float,
    ) -> None:
        """Generate load for a single phase using dynamic concurrent requests."""
        url = f"http://{self.config.alb_dns}/cpu-intensive"
        progress_interval = 60
        rps_report_interval = 3  # Report actual RPS every 3 seconds
        last_progress = time.perf_counter()
        last_rps_report = time.perf_counter()
        # Clear timestamps at phase start
        self._request_timestamps.clear()

        # User Fix: Record precise burst start time for accurate latency measurement
        if phase.phase_name == "Burst" and self.burst_start_time is None:
            self.burst_start_time = time.time()
            print(f"  [Burst] Precise start time recorded: {self.burst_start_time}")

        # Initial concurrent requests: target_rps * request_delay * 2 (buffer)
        current_concurrent = int(
            phase.request_rate_per_second * phase.request_delay_seconds * 2
        )
        # P0 Fix: Ensure minimum 50 concurrent workers to reliably reach 50 req/s target
        current_concurrent = max(50, current_concurrent)
        MAX_CONCURRENT = (
            500  # Maximum concurrency limit (increased for high request rates)
        )

        print(
            f"[{datetime.now(timezone.utc).isoformat()}] {phase.phase_name} phase started"
        )
        print(f"  Target: {phase.request_rate_per_second} req/s")
        print(f"  Initial Concurrent: {current_concurrent} workers")
        print(f"  Duration: {phase.duration_seconds} seconds")
        print()

        # Run in batches of 3-5 seconds, adjusting concurrency after each batch
        batch_duration = 3  # seconds
        next_batch_start = time.perf_counter()

        while time.time() < stop_time:
            # Record RPS at batch start for calculation
            batch_start_rps = 0
            if len(self._request_timestamps) > 0:
                window_start = time.perf_counter() - rps_report_interval
                while (
                    self._request_timestamps
                    and self._request_timestamps[0] < window_start
                ):
                    self._request_timestamps.popleft()
                batch_start_rps = len(self._request_timestamps) / rps_report_interval

            # Run a batch of requests with current concurrency
            batch_start = time.perf_counter()
            requests_in_batch = current_concurrent * 2  # 2x concurrency per batch

            with ThreadPoolExecutor(max_workers=current_concurrent) as executor:
                futures = [
                    executor.submit(self._make_single_request, url, phase)
                    for _ in range(requests_in_batch)
                ]
                # Wait for all futures to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        pass  # Exception already recorded

            # Calculate actual RPS after batch
            now = time.perf_counter()
            window_start = now - rps_report_interval
            while (
                self._request_timestamps and self._request_timestamps[0] < window_start
            ):
                self._request_timestamps.popleft()
            actual_rps = len(self._request_timestamps) / rps_report_interval

            # Dynamic concurrency adjustment
            error_pct = (
                phase.request_rate_per_second - actual_rps
            ) / phase.request_rate_per_second

            if error_pct > 0.2:  # Actual RPS is >20% below target
                # Increase concurrency
                current_concurrent = min(int(current_concurrent * 1.5), MAX_CONCURRENT)
            elif error_pct < -0.2:  # Actual RPS is >20% above target
                # Decrease concurrency
                current_concurrent = max(int(current_concurrent * 0.8), 1)

            # Report RPS every 3 seconds
            if now - last_rps_report >= rps_report_interval:
                print(
                    f"  {datetime.now(timezone.utc).isoformat()} | "
                    f"Target: {phase.request_rate_per_second} req/s | "
                    f"Actual: {actual_rps:.1f} req/s | "
                    f"Concurrent: {current_concurrent} | "
                    f"Total: {self.load_results['total_requests']}"
                )
                # Publish RequestRate metric to CloudWatch for ASG scaling
                if self.config.strategy == "request_rate":
                    try:
                        self.cloudwatch.put_metric_data(
                            Namespace="AutoscaleExperiment",
                            MetricData=[
                                {
                                    "MetricName": "RequestRate",
                                    "Value": actual_rps,
                                    "Unit": "Count/Second",
                                    "Timestamp": datetime.now(timezone.utc),
                                }
                            ],
                        )
                    except Exception as e:
                        print(f"  [Warning] Failed to publish RequestRate metric: {e}")
                last_rps_report = now

            # Show progress every 60 seconds
            if now - last_progress >= progress_interval:
                print(
                    f"  {datetime.now(timezone.utc).isoformat()} - "
                    f"Total: {self.load_results['total_requests']} requests, "
                    f"Success: {self.load_results['successful_requests']}, "
                    f"Failed: {self.load_results['failed_requests']}"
                )
                last_progress = now

            # Wait until next batch
            elapsed = now - batch_start
            if elapsed < batch_duration:
                time.sleep(batch_duration - elapsed)

    def _collect_metrics(self, phase: BurstPhaseConfig) -> None:
        """Collect CloudWatch metrics for a phase."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(
            minutes=5
        )  # Fixed 5-minute window for metric queries

        alb_dim = _alb_dimension_value(self.config.alb_arn)
        tg_dim = _target_group_dimension_value(self.config.target_group_arn)

        try:
            # Get response time from ALB (use Period=60 for standard AWS metrics)
            response = self.cloudwatch.get_metric_statistics(
                Namespace="AWS/ApplicationELB",
                MetricName="TargetResponseTime",
                Dimensions=[
                    {"Name": "LoadBalancer", "Value": alb_dim},
                    {"Name": "TargetGroup", "Value": tg_dim},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=60,  # Standard AWS metrics are at 60-second resolution
                Statistics=["Average"],
            )
            response_time = _parse_latest_datapoint(response, "Average")

            # Get ASG desired capacity via AutoScaling API (not CloudWatch)
            try:
                asg_resp = self.autoscaling.describe_auto_scaling_groups(
                    AutoScalingGroupNames=[self.config.asg_name]
                )
                if asg_resp.get("AutoScalingGroups"):
                    desired_capacity = asg_resp["AutoScalingGroups"][0].get(
                        "DesiredCapacity"
                    )
                else:
                    desired_capacity = None
            except Exception:
                desired_capacity = None

            # Track scale-out events during Burst phase - USER FIX: precise latency measurement
            if phase.phase_name == "Burst":
                current_time = time.time()

                # Record baseline capacity on first Burst sample (for backward compatibility)
                if self.baseline_capacity is None and desired_capacity is not None:
                    self.baseline_capacity = desired_capacity
                    # Only set burst_start_time if not already set in _run_load_phase
                    if self.burst_start_time is None:
                        self.burst_start_time = current_time
                    self.previous_capacity = desired_capacity

                # Get current healthy target count
                healthy_count = self._check_target_group_health()

                # Initialize previous_healthy_count on first Burst sample
                if self.previous_healthy_count is None:
                    self.previous_healthy_count = healthy_count
                    print(f"  [Burst] Initial healthy targets: {healthy_count}")

                # User Fix: Record scale-out event only when healthy count increases from 1 to 2+
                # AND only record the first scale-out event (proposal requirement: time to first instance ready)
                if (
                    self.previous_healthy_count == 1
                    and healthy_count >= 2
                    and self.burst_start_time is not None
                    and not self.scale_out_events
                ):  # Only record first scale-out
                    latency_seconds = current_time - self.burst_start_time
                    self.scale_out_events.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "latency_seconds": latency_seconds,
                            "desired_capacity": desired_capacity,
                            "healthy_targets": healthy_count,
                            "previous_healthy_targets": self.previous_healthy_count,
                            "new_healthy_targets": healthy_count,
                        }
                    )
                    print(
                        f"  [Burst] Scale-out detected! Latency: {latency_seconds:.1f}s, "
                        f"Healthy targets: {self.previous_healthy_count} → {healthy_count}"
                    )
                    # Also update previous_capacity for backward compatibility
                    self.previous_capacity = desired_capacity

                # Update previous_healthy_count for next iteration
                self.previous_healthy_count = healthy_count

            # Get CPU utilization from EC2 (query per instance and aggregate)
            cpu_util = None
            try:
                asg_resp = self.autoscaling.describe_auto_scaling_groups(
                    AutoScalingGroupNames=[self.config.asg_name]
                )
                if asg_resp.get("AutoScalingGroups"):
                    instances = asg_resp["AutoScalingGroups"][0].get("Instances", [])
                    cpu_values = []
                    for instance in instances:
                        instance_id = instance.get("InstanceId")
                        response = self.cloudwatch.get_metric_statistics(
                            Namespace="AWS/EC2",
                            MetricName="CPUUtilization",
                            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=60,  # Standard AWS metrics are at 60-second resolution
                            Statistics=["Average"],
                        )
                        latest = _parse_latest_datapoint(response, "Average")
                        if latest is not None:
                            cpu_values.append(latest)

                    if cpu_values:
                        cpu_util = statistics.mean(cpu_values)
            except Exception:
                cpu_util = None

            # Diagnostic logging for debugging metric collection issues
            if not response_time and not desired_capacity and not cpu_util:
                # Silent on first collection, metrics take time to appear in CloudWatch
                pass
            elif response_time is None or desired_capacity is None or cpu_util is None:
                # Log when we have partial data (one metric available but others missing)
                # This can indicate permissions or metric availability issues
                if response_time:
                    capacity_str = (
                        f"{desired_capacity:.1f}"
                        if desired_capacity is not None
                        else "N/A"
                    )
                    cpu_str = (
                        f"{cpu_util * 100:.1f}%" if cpu_util is not None else "N/A"
                    )
                    print(
                        f"  [Metrics] {phase.phase_name}: response_time={response_time:.1f}ms, "
                        f"capacity={capacity_str}, cpu={cpu_str}"
                    )

            sample = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": phase.phase_name,
                "response_time_ms": response_time,
                "desired_capacity": desired_capacity,
                "cpu_utilization": cpu_util,
            }

            self.metric_samples.append(sample)
            self.phase_metric_samples[phase.phase_name].append(sample)

        except Exception as e:
            print(f"  [Warning] Error collecting metrics in {phase.phase_name}: {e}")

    def run(self) -> None:
        """Run the complete burst scenario experiment."""
        print("=" * 80)
        print(f"Burst Scenario Experiment - {self.config.strategy.upper()} Strategy")
        print("=" * 80)
        print()

        # Setup
        self._route_listener()
        self._set_desired_capacity()

        # 关键改进：等待实例真正健康再开始负载
        if not self._wait_for_target_capacity():
            print(
                "⚠️  WARNING: Timeout waiting for instances to become healthy. "
                "Experiment may have data quality issues."
            )
            # 继续进行实验，但标记此警告

        print()

        # Run all phases
        total_duration = sum(phase.duration_seconds for phase in self.config.phases)
        experiment_end = time.time() + total_duration

        for phase in self.config.phases:
            phase_end = time.time() + phase.duration_seconds

            # Run load generation and metric collection in parallel
            load_thread = threading.Thread(
                target=self._run_load_phase,
                args=(phase, phase_end),
            )
            load_thread.start()

            # Collect metrics periodically during the phase
            metric_end = phase_end
            while time.time() < metric_end:
                time.sleep(self.config.sample_interval_seconds)
                self._collect_metrics(phase)

            load_thread.join()
            print(f"{phase.phase_name} phase completed\n")

        print("=" * 80)
        print("Experiment completed. Generating report...")
        print("=" * 80)

    def save_results(self, strategy: str) -> Path:
        """Save results to JSON file."""
        # Calculate aggregate metrics
        if self.load_results["response_times_ms"]:
            avg_response_time = statistics.mean(self.load_results["response_times_ms"])
            p95_response_time = _percentile(
                self.load_results["response_times_ms"], 0.95
            )
            p99_response_time = _percentile(
                self.load_results["response_times_ms"], 0.99
            )
        else:
            avg_response_time = 0
            p95_response_time = 0
            p99_response_time = 0

        success_rate = (
            self.load_results["successful_requests"]
            / self.load_results["total_requests"]
            if self.load_results["total_requests"] > 0
            else 0
        )

        # Calculate phase-specific metrics
        phase_results = {}
        for phase in self.config.phases:
            phase_samples = self.phase_metric_samples[phase.phase_name]
            if phase_samples:
                # Safely extract and filter values, with fallback to empty list
                response_times = [
                    s["response_time_ms"]
                    for s in phase_samples
                    if s["response_time_ms"] is not None
                ]
                capacities = [
                    s["desired_capacity"]
                    for s in phase_samples
                    if s["desired_capacity"] is not None
                ]
                cpu_utils = [
                    s["cpu_utilization"]
                    for s in phase_samples
                    if s["cpu_utilization"] is not None
                ]

                phase_results[phase.phase_name] = {
                    "duration_seconds": phase.duration_seconds,
                    "target_request_rate": phase.request_rate_per_second,
                    "sample_count": len(phase_samples),
                    "avg_response_time_ms": statistics.mean(response_times)
                    if response_times
                    else 0,
                    "avg_desired_capacity": statistics.mean(capacities)
                    if capacities
                    else 0,
                    "avg_cpu_utilization": statistics.mean(cpu_utils)
                    if cpu_utils
                    else 0,
                }

        # Calculate scale-out latency statistics
        scale_out_latencies = [
            event["latency_seconds"] for event in self.scale_out_events
        ]

        if scale_out_latencies:
            scale_out_latency_stats = {
                "count": len(scale_out_latencies),
                "mean": statistics.mean(scale_out_latencies),
                "median": statistics.median(scale_out_latencies),
                "stdev": statistics.stdev(scale_out_latencies)
                if len(scale_out_latencies) > 1
                else 0,
                "min": min(scale_out_latencies),
                "max": max(scale_out_latencies),
            }
        else:
            scale_out_latency_stats = {
                "count": 0,
                "mean": 0,
                "median": 0,
                "stdev": 0,
                "min": 0,
                "max": 0,
            }

        report = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "experiment_type": "burst_scenario",
            "strategy": strategy,
            "summary": {
                "total_requests": self.load_results["total_requests"],
                "successful_requests": self.load_results["successful_requests"],
                "failed_requests": self.load_results["failed_requests"],
                "success_rate": success_rate,
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "p99_response_time_ms": p99_response_time,
            },
            "scale_out_latencies": scale_out_latencies,
            "scale_out_latency_stats": scale_out_latency_stats,
            "phase_metrics": phase_results,
            "raw_samples": self.metric_samples,
            "scale_out_events": self.scale_out_events,
        }

        filename = f"burst_scenario_{strategy}_results.json"
        filepath = RESULTS_DIR / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Results saved to {filepath}")
        return filepath


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run burst scenario experiment for autoscaling strategies"
    )
    parser.add_argument(
        "--strategy",
        choices=["cpu", "request_rate", "both"],
        default="both",
        help="Which strategy to test",
    )

    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.strategy in ("cpu", "both"):
        print("\n" + "=" * 80)
        print("RUNNING CPU STRATEGY BURST SCENARIO")
        print("=" * 80 + "\n")
        config = _load_config_cpu()
        runner = BurstScenarioRunner(config)
        runner.run()
        runner.save_results("cpu")
        print("\n[OK] CPU strategy burst scenario completed\n")

        if args.strategy == "both":
            time.sleep(5)  # Brief pause between experiments

    if args.strategy in ("request_rate", "both"):
        print("\n" + "=" * 80)
        print("RUNNING REQUEST-RATE STRATEGY BURST SCENARIO")
        print("=" * 80 + "\n")
        config = _load_config_request_rate()
        runner = BurstScenarioRunner(config)
        runner.run()
        runner.save_results("request_rate")
        print("\n[OK] Request-rate strategy burst scenario completed\n")

    print("\n" + "=" * 80)
    print("BURST SCENARIO EXPERIMENTS COMPLETED")
    print("=" * 80)
    print("\nResults saved to experiments/results/")
    print("  - burst_scenario_cpu_results.json")
    print("  - burst_scenario_request_rate_results.json")


if __name__ == "__main__":
    main()
