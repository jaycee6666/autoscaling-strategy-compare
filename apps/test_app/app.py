"""Test Flask application for autoscaling experiments."""

from __future__ import annotations

import logging
import os
import random
import string
import time
from datetime import datetime
from typing import Any, Dict, Tuple

from flask import Flask, jsonify, request

try:  # pragma: no cover - import environment dependent
    import boto3  # type: ignore
except Exception:  # pragma: no cover - import environment dependent
    boto3 = None  # type: ignore[assignment]

app = Flask(__name__)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REGION = os.getenv("AWS_REGION", "us-east-1")

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

cloudwatch = (
    boto3.client("cloudwatch", region_name=REGION) if boto3 is not None else None
)

request_count = 0
request_start_time = datetime.now()


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Any, int]:
    """Health check endpoint."""
    global request_count
    request_count += 1

    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
            }
        ),
        200,
    )


@app.route("/data", methods=["GET"])
def get_data() -> Tuple[Any, int]:
    """Return random payload."""
    global request_count
    request_count += 1

    size_kb = request.args.get("size", 10, type=int)
    payload = "".join(
        random.choices(string.ascii_letters + string.digits, k=max(size_kb, 0) * 1024)
    )

    return (
        jsonify(
            {
                "data": payload,
                "size_kb": size_kb,
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.route("/cpu-intensive", methods=["POST"])
def cpu_intensive() -> Tuple[Any, int]:
    """CPU-intensive endpoint for autoscaling tests."""
    global request_count
    request_count += 1

    duration_seconds = 1
    if request.is_json and isinstance(request.json, dict):
        duration_seconds = int(request.json.get("duration", 1))

    start_time = time.monotonic()
    result = 0
    while time.monotonic() - start_time < max(duration_seconds, 0):
        for value in range(10000):
            result += (value**2) % 1000

    return (
        jsonify(
            {
                "cpu_duration_seconds": duration_seconds,
                "operations": result,
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.route("/metrics", methods=["GET"])
def get_metrics() -> Tuple[Any, int]:
    """Application-level request metrics."""
    elapsed = (datetime.now() - request_start_time).total_seconds()
    rate = request_count / elapsed if elapsed > 0 else 0

    response: Dict[str, Any] = {
        "total_requests": request_count,
        "elapsed_seconds": elapsed,
        "request_rate_per_second": rate,
        "timestamp": datetime.now().isoformat(),
    }

    if cloudwatch is None:
        response["cloudwatch"] = "unavailable"

    return jsonify(response), 200


@app.route("/reset", methods=["POST"])
def reset_metrics() -> Tuple[Any, int]:
    """Reset in-memory metrics counters."""
    global request_count, request_start_time
    request_count = 0
    request_start_time = datetime.now()

    return jsonify({"status": "reset", "timestamp": datetime.now().isoformat()}), 200


@app.errorhandler(404)
def not_found(_error: Exception) -> Tuple[Any, int]:
    """404 handler."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error: Exception) -> Tuple[Any, int]:
    """500 handler."""
    logger.error("Internal error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting test application...")
    app.run(host="0.0.0.0", port=8080, debug=False)
