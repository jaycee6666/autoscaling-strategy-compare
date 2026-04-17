# Phase 2b: Application Development - Implementation Guide

## Overview

Phase 2b introduces four application-layer components for autoscaling experiments:

1. **Load Generator** (`scripts/load_generator.py`) - HTTP load generation with constant/ramp/wave patterns
2. **Metrics Collector** (`scripts/metrics_collector.py`) - CloudWatch + ASG metrics polling and CSV export
3. **Experiment Runner** (`scripts/experiment_runner.py`) - Orchestration for load + metrics workflows
4. **Test Application** (`apps/test_app/app.py`) - Flask application providing autoscaling-friendly endpoints

All AWS integrations use **boto3** (no AWS CLI subprocess calls), and implementation is cross-platform for Windows/macOS/Linux.

---

## 1) Load Generator

```python
from scripts.load_generator import LoadGenerator

generator = LoadGenerator(
    target_url="http://example-alb.us-east-1.elb.amazonaws.com",
    request_rate=15,
    duration_seconds=120,
    pattern="ramp",  # constant | ramp | wave
    endpoint="/health",
)

stats = generator.generate_load()
generator.export_stats_to_csv("experiments/load_stats.csv", stats)
print(stats)
```

### Patterns
- `constant`: stable request rate over test duration
- `ramp`: gradually increases request pressure
- `wave`: sinusoidal request variation to simulate burst/recovery cycles

---

## 2) Metrics Collector

```python
from scripts.metrics_collector import MetricsCollector

collector = MetricsCollector(
    asg_name="experiment-asg-cpu",
    region="us-east-1",
    poll_interval=10,
)

collector.start_collection()
# ... execute load test ...
collector.stop_collection()

collector.export_to_csv("experiments/metrics.csv")
print(collector.get_summary_stats())
```

### Collected fields
- `cpu_utilization`
- `instance_count`
- `healthy_instance_count`
- `request_rate` (custom metric when available)
- `network_in` / `network_out`

---

## 3) Experiment Runner

```python
from scripts.experiment_runner import ExperimentRunner

runner = ExperimentRunner(
    experiment_name="cpu_strategy_test_1",
    asg_name="experiment-asg-cpu",
    alb_dns="http://example-alb.us-east-1.elb.amazonaws.com",
    request_rate=20,
    duration_seconds=180,
    load_pattern="wave",
)

result = runner.run()
summary = runner.get_results_summary()
print(summary)
```

### Output artifacts
By default, each run writes into:

`experiments/<experiment_name>/`

- `experiment_log.json`
- `load_stats.csv`
- `metrics.csv`

---

## 4) Test Flask Application

### Endpoints
- `GET /health` - service health
- `GET /data?size=<kb>` - random payload
- `POST /cpu-intensive` - CPU-bound workload simulation
- `GET /metrics` - in-process request metrics
- `POST /reset` - reset in-process counters

### Local run

```bash
python apps/test_app/app.py
```

Service listens on `http://localhost:8080`.

### Docker run

```bash
docker build -t test-app:latest apps/test_app
docker run -p 8080:8080 test-app:latest
```

---

## Test Commands

```bash
python -m pytest tests/test_load_generator.py -v
python -m pytest tests/test_metrics_collector.py -v
python -m pytest tests/test_experiment_runner.py -v
python -m pytest tests/test_app_endpoints.py -v
```

---

## Type Checking

```bash
mypy scripts apps tests
```

If your environment has dependency version mismatches, first run project setup and install requirements, then rerun mypy.
