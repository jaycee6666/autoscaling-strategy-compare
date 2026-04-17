"""Load generator for autoscaling experiments."""

from __future__ import annotations

import csv
import logging
import math
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


@dataclass
class LoadGeneratorStats:
    """Statistics collected during load generation."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)

    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx] if idx < len(sorted_times) else sorted_times[-1]

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class LoadGenerator:
    """Generate HTTP load using constant/ramp/wave patterns."""

    VALID_PATTERNS = ["constant", "ramp", "wave"]

    def __init__(
        self,
        target_url: str,
        request_rate: float,
        duration_seconds: int,
        pattern: str = "constant",
        method: str = "GET",
        endpoint: str = "",
        timeout: int = 5,
        max_workers: int = 10,
    ) -> None:
        if pattern not in self.VALID_PATTERNS:
            raise ValueError(
                f"Invalid pattern: {pattern}. Must be one of {self.VALID_PATTERNS}"
            )
        if request_rate <= 0:
            raise ValueError("request_rate must be positive")
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")

        self.target_url = target_url.rstrip("/")
        self.request_rate = request_rate
        self.duration_seconds = duration_seconds
        self.pattern = pattern
        self.method = method
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_workers = max_workers

        self.stats = LoadGeneratorStats()
        self._lock = threading.Lock()

    def generate_load(self) -> Dict[str, Any]:
        """Run load generation and return summarized stats."""
        self.stats = LoadGeneratorStats()
        self.stats.start_time = datetime.now()

        start = time.monotonic()
        request_times = self._build_schedule()
        threads: List[threading.Thread] = []

        for target_offset in request_times:
            while self._active_worker_count(threads) >= self.max_workers:
                time.sleep(0.001)

            elapsed = time.monotonic() - start
            if elapsed >= self.duration_seconds:
                break

            sleep_time = target_offset - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

            thread = threading.Thread(target=self._make_request)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join(timeout=self.timeout + 2)

        self.stats.end_time = datetime.now()
        return self._format_stats()

    def _active_worker_count(self, threads: List[threading.Thread]) -> int:
        alive = [t for t in threads if t.is_alive()]
        threads[:] = alive
        return len(alive)

    def _build_schedule(self) -> List[float]:
        if self.pattern == "constant":
            return self._generate_constant_pattern()
        if self.pattern == "ramp":
            return self._generate_ramp_pattern()
        return self._generate_wave_pattern()

    def _full_url(self) -> str:
        endpoint = self.endpoint or ""
        if endpoint and not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self.target_url}{endpoint}"

    def _make_request(self) -> None:
        start = time.monotonic()
        try:
            response = requests.request(
                method=self.method,
                url=self._full_url(),
                timeout=self.timeout,
            )
            response_time = time.monotonic() - start

            with self._lock:
                self.stats.total_requests += 1
                self.stats.response_times.append(response_time)
                if 200 <= response.status_code < 300:
                    self.stats.successful_requests += 1
                else:
                    self.stats.failed_requests += 1
                    self.stats.errors.append(f"HTTP {response.status_code}")
        except Exception as exc:  # pragma: no cover - network level variability
            response_time = time.monotonic() - start
            with self._lock:
                self.stats.total_requests += 1
                self.stats.failed_requests += 1
                self.stats.response_times.append(response_time)
                self.stats.errors.append(str(exc))

    def _generate_constant_pattern(self) -> List[float]:
        total_requests = int(self.request_rate * self.duration_seconds)
        if total_requests <= 0:
            return []
        interval = self.duration_seconds / total_requests
        return [i * interval for i in range(total_requests)]

    def _generate_ramp_pattern(self) -> List[float]:
        total_requests = int(self.request_rate * self.duration_seconds)
        if total_requests <= 0:
            return []

        times = [0.0]
        for i in range(1, total_requests):
            progress = i / max(total_requests - 1, 1)
            adjusted_rate = self.request_rate * (0.5 + 1.5 * progress)
            times.append(times[-1] + 1 / max(adjusted_rate, 0.001))

        return self._scale_to_duration(times)

    def _generate_wave_pattern(self) -> List[float]:
        total_requests = int(self.request_rate * self.duration_seconds)
        if total_requests <= 0:
            return []

        times = [0.0]
        for i in range(1, total_requests):
            progress = i / max(total_requests - 1, 1)
            wave_factor = 1.0 + 0.5 * math.sin(2 * math.pi * progress)
            adjusted_rate = self.request_rate * max(wave_factor, 0.1)
            times.append(times[-1] + 1 / adjusted_rate)

        return self._scale_to_duration(times)

    def _scale_to_duration(self, times: List[float]) -> List[float]:
        if len(times) < 2 or times[-1] <= 0:
            return times
        scale = self.duration_seconds / times[-1]
        return [t * scale for t in times]

    def export_stats_to_csv(
        self, filename: str, stats: Dict[str, Any] | None = None
    ) -> None:
        """Export load stats to CSV."""
        values = stats if stats is not None else self._format_stats()
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Load Generation Summary"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Requests", values["total_requests"]])
            writer.writerow(["Successful Requests", values["successful_requests"]])
            writer.writerow(["Failed Requests", values["failed_requests"]])
            writer.writerow(
                ["Average Response Time (s)", f"{values['average_response_time']:.6f}"]
            )
            writer.writerow(
                ["P95 Response Time (s)", f"{values['p95_response_time']:.6f}"]
            )
            writer.writerow(["Duration (s)", f"{values['duration']:.6f}"])
            writer.writerow(["Pattern", self.pattern])
            writer.writerow(["Target Rate (req/s)", self.request_rate])
            writer.writerow([])
            writer.writerow(["Response Times Detail"])
            writer.writerow(["Request", "Response Time (s)"])
            for idx, response_time in enumerate(values["response_times"], start=1):
                writer.writerow([idx, f"{response_time:.6f}"])

        logger.info("Statistics exported to %s", filename)

    def _format_stats(self) -> Dict[str, Any]:
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "response_times": self.stats.response_times,
            "errors": self.stats.errors,
            "average_response_time": self.stats.average_response_time,
            "p95_response_time": self.stats.p95_response_time,
            "duration": self.stats.duration_seconds,
            "pattern": self.pattern,
            "request_rate": self.request_rate,
        }
