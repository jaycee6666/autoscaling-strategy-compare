"""CloudWatch metrics collector for autoscaling experiments."""

from __future__ import annotations

import csv
import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - import environment dependent
    import boto3  # type: ignore
except Exception:  # pragma: no cover - import environment dependent
    boto3 = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Single point-in-time metrics snapshot."""

    timestamp: datetime
    cpu_utilization: Optional[float] = None
    instance_count: Optional[int] = None
    request_rate: Optional[float] = None
    network_in: Optional[float] = None
    network_out: Optional[float] = None
    healthy_instance_count: Optional[int] = None


class MetricsCollector:
    """Collect ASG related metrics from CloudWatch and Auto Scaling APIs."""

    def __init__(
        self,
        asg_name: str,
        region: str = "us-east-1",
        poll_interval: int = 10,
        config_path: str = "infrastructure/asg-config.json",
    ) -> None:
        self.asg_name = asg_name
        self.region = region
        self.poll_interval = poll_interval
        self.config_path = config_path
        self.cloudwatch: Any
        self.autoscaling: Any

        if boto3 is None:
            self.cloudwatch = _UnavailableAwsClient("cloudwatch")
            self.autoscaling = _UnavailableAwsClient("autoscaling")
        else:
            self.cloudwatch = boto3.client("cloudwatch", region_name=region)
            self.autoscaling = boto3.client("autoscaling", region_name=region)

        self.metrics_history: Dict[str, List[Any]] = {
            "timestamp": [],
            "cpu_utilization": [],
            "instance_count": [],
            "request_rate": [],
            "network_in": [],
            "network_out": [],
            "healthy_instance_count": [],
        }

        self.is_collecting = False
        self.collection_thread: Optional[threading.Thread] = None

    def start_collection(self) -> None:
        if self.is_collecting:
            logger.warning("Collection already in progress")
            return

        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, daemon=True
        )
        self.collection_thread.start()

    def stop_collection(self) -> None:
        self.is_collecting = False
        if self.collection_thread is not None:
            self.collection_thread.join(timeout=max(self.poll_interval + 2, 3))

    def _collection_loop(self) -> None:
        while self.is_collecting:
            try:
                snapshot = self.collect_snapshot()
                if snapshot is not None:
                    self._store_snapshot(snapshot)
            except Exception as exc:  # pragma: no cover - guardrail
                logger.error("Error collecting metrics: %s", exc)
            time.sleep(self.poll_interval)

    def collect_snapshot(self) -> Optional[MetricsSnapshot]:
        try:
            snapshot = MetricsSnapshot(
                timestamp=datetime.utcnow(),
                cpu_utilization=self._get_cpu_utilization(),
            )
            asg_info = self._get_asg_info()
            snapshot.instance_count = asg_info["desired_capacity"]
            snapshot.healthy_instance_count = asg_info["healthy_instance_count"]
            snapshot.request_rate = self._get_request_rate()
            snapshot.network_in, snapshot.network_out = self._get_network_metrics()
            return snapshot
        except Exception as exc:
            logger.error("Error in collect_snapshot: %s", exc)
            return None

    def _get_cpu_utilization(self) -> Optional[float]:
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": self.asg_name}],
            StartTime=datetime.utcnow() - timedelta(minutes=5),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=["Average"],
        )
        return self._parse_metric_response(response)

    def _get_asg_info(self) -> Dict[str, int]:
        response = self.autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[self.asg_name]
        )
        groups = response.get("AutoScalingGroups", [])
        if not groups:
            return {"desired_capacity": 0, "healthy_instance_count": 0}

        asg = groups[0]
        healthy_count = len(
            [
                instance
                for instance in asg.get("Instances", [])
                if instance.get("HealthStatus") == "Healthy"
            ]
        )
        return {
            "desired_capacity": int(asg.get("DesiredCapacity", 0)),
            "healthy_instance_count": healthy_count,
        }

    def _get_request_rate(self) -> Optional[float]:
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace="AutoscaleExperiment",
                MetricName="RequestRate",
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow(),
                Period=60,
                Statistics=["Sum"],
            )
            return self._parse_metric_response(response)
        except Exception:
            return None

    def _get_network_metrics(self) -> Tuple[Optional[float], Optional[float]]:
        net_in = self._get_network_metric("NetworkIn")
        net_out = self._get_network_metric("NetworkOut")
        return net_in, net_out

    def _get_network_metric(self, metric_name: str) -> Optional[float]:
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName=metric_name,
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": self.asg_name}],
            StartTime=datetime.utcnow() - timedelta(minutes=5),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=["Sum"],
        )
        return self._parse_metric_response(response)

    def _store_snapshot(self, snapshot: MetricsSnapshot) -> None:
        self.metrics_history["timestamp"].append(snapshot.timestamp.isoformat())
        self.metrics_history["cpu_utilization"].append(snapshot.cpu_utilization)
        self.metrics_history["instance_count"].append(snapshot.instance_count)
        self.metrics_history["request_rate"].append(snapshot.request_rate)
        self.metrics_history["network_in"].append(snapshot.network_in)
        self.metrics_history["network_out"].append(snapshot.network_out)
        self.metrics_history["healthy_instance_count"].append(
            snapshot.healthy_instance_count
        )

    def export_to_csv(self, filename: str) -> None:
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as file:
            if not self.metrics_history["timestamp"]:
                file.write("No metrics collected\n")
                return

            fieldnames = [
                "timestamp",
                "cpu_utilization",
                "instance_count",
                "healthy_instance_count",
                "request_rate",
                "network_in",
                "network_out",
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for index in range(len(self.metrics_history["timestamp"])):
                writer.writerow(
                    {
                        "timestamp": self.metrics_history["timestamp"][index],
                        "cpu_utilization": self.metrics_history["cpu_utilization"][
                            index
                        ],
                        "instance_count": self.metrics_history["instance_count"][index],
                        "healthy_instance_count": self.metrics_history[
                            "healthy_instance_count"
                        ][index],
                        "request_rate": self.metrics_history["request_rate"][index],
                        "network_in": self.metrics_history["network_in"][index],
                        "network_out": self.metrics_history["network_out"][index],
                    }
                )

    def _parse_metric_response(self, response: Dict[str, Any]) -> Optional[float]:
        datapoints = response.get("Datapoints", [])
        if not datapoints:
            return None

        latest = sorted(datapoints, key=lambda item: item["Timestamp"])[-1]
        value = latest.get("Average")
        if value is None:
            value = latest.get("Sum")
        return float(value) if value is not None else None

    def get_summary_stats(self) -> Dict[str, Any]:
        cpu_values = [
            v for v in self.metrics_history["cpu_utilization"] if v is not None
        ]
        instance_values = [
            v for v in self.metrics_history["instance_count"] if v is not None
        ]

        return {
            "total_samples": len(self.metrics_history["timestamp"]),
            "avg_cpu_utilization": sum(cpu_values) / len(cpu_values)
            if cpu_values
            else 0,
            "max_cpu_utilization": max(cpu_values) if cpu_values else 0,
            "min_cpu_utilization": min(cpu_values) if cpu_values else 0,
            "avg_instance_count": sum(instance_values) / len(instance_values)
            if instance_values
            else 0,
            "max_instance_count": max(instance_values) if instance_values else 0,
            "min_instance_count": min(instance_values) if instance_values else 0,
        }


class _UnavailableAwsClient:
    """Fallback object when boto3 import is unavailable locally."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name

    def __getattr__(self, method_name: str) -> Any:
        def _raiser(*_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError(
                f"boto3 unavailable: cannot call {self.service_name}.{method_name}"
            )

        return _raiser
