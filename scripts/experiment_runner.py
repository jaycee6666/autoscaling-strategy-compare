"""Experiment orchestration for autoscaling comparison."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from scripts.load_generator import LoadGenerator
from scripts.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Coordinate load generation and metrics collection."""

    def __init__(
        self,
        experiment_name: str,
        asg_name: str,
        alb_dns: str,
        region: str = "us-east-1",
        request_rate: float = 10,
        duration_seconds: int = 300,
        load_pattern: str = "constant",
        output_dir: str = "experiments",
    ) -> None:
        if request_rate <= 0:
            raise ValueError("request_rate must be positive")
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if load_pattern not in ["constant", "ramp", "wave"]:
            raise ValueError(f"Invalid load_pattern: {load_pattern}")

        self.experiment_name = experiment_name
        self.asg_name = asg_name
        self.alb_dns = alb_dns
        self.region = region
        self.request_rate = request_rate
        self.duration_seconds = duration_seconds
        self.load_pattern = load_pattern

        self.output_dir = os.path.join(output_dir, experiment_name)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        self.load_generator = LoadGenerator(
            target_url=alb_dns,
            request_rate=request_rate,
            duration_seconds=duration_seconds,
            pattern=load_pattern,
            endpoint="/health",
        )
        self.metrics_collector = MetricsCollector(asg_name=asg_name, region=region)

        self.experiment_log: Dict[str, Any] = {
            "name": experiment_name,
            "asg_name": asg_name,
            "alb_dns": alb_dns,
            "start_time": None,
            "end_time": None,
            "duration": duration_seconds,
            "request_rate": request_rate,
            "load_pattern": load_pattern,
            "load_stats": None,
            "metrics_summary": None,
        }

    def run(self) -> Dict[str, Any]:
        """Run complete experiment and persist result artifacts."""
        self.experiment_log["start_time"] = datetime.now().isoformat()
        try:
            self.metrics_collector.start_collection()
            load_stats = self.load_generator.generate_load()
            self.experiment_log["load_stats"] = load_stats
            self.metrics_collector.stop_collection()
            self.experiment_log["metrics_summary"] = (
                self.metrics_collector.get_summary_stats()
            )
            self.experiment_log["end_time"] = datetime.now().isoformat()
            self._export_results()
            return self.experiment_log
        except Exception as exc:
            self.experiment_log["error"] = str(exc)
            self.experiment_log["end_time"] = datetime.now().isoformat()
            self._export_results()
            raise

    def _export_results(self) -> None:
        log_file = os.path.join(self.output_dir, "experiment_log.json")
        with open(log_file, "w", encoding="utf-8") as file:
            json.dump(self.experiment_log, file, indent=2, default=str)

        if self.experiment_log.get("load_stats"):
            stats_file = os.path.join(self.output_dir, "load_stats.csv")
            self.load_generator.export_stats_to_csv(
                stats_file, self.experiment_log["load_stats"]
            )

        metrics_file = os.path.join(self.output_dir, "metrics.csv")
        self.metrics_collector.export_to_csv(metrics_file)

    def get_results_summary(self) -> Dict[str, Any]:
        return {
            "experiment": self.experiment_name,
            "status": "success" if "error" not in self.experiment_log else "failed",
            "load_stats": self.experiment_log.get("load_stats"),
            "metrics_summary": self.experiment_log.get("metrics_summary"),
        }
