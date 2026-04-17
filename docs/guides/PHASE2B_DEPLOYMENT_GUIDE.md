# Phase 2B: Application Development & Deployment Guide

## Overview

Phase 2B is the application development phase where you build the core components needed to run autoscaling experiments. This phase creates three main components:

1. **Load Generator** - HTTP load generation tool with configurable traffic patterns
2. **Metrics Collector** - Real-time AWS CloudWatch metrics polling and export
3. **Experiment Runner** - Orchestration layer that coordinates load tests and metrics collection
4. **Flask Test Application** - Lightweight test application that responds to load with configurable behavior

**Duration**: Estimated 6-10 hours  
**Prerequisites**: Phase 1 (AWS infrastructure) must be completed  
**Output**: Functional load generation and metrics collection tools ready for Phase 3 deployment

---

## Architecture Overview

```
Phase 2B Components
├── Load Generator (scripts/load_generator.py)
│   ├── Constant rate load generation
│   ├── Ramp-up patterns
│   └── Wave patterns
│
├── Metrics Collector (scripts/metrics_collector.py)
│   ├── CloudWatch API integration
│   ├── Real-time metric polling
│   └── CSV export functionality
│
├── Experiment Runner (scripts/experiment_runner.py)
│   ├── Coordinates load generation
│   ├── Collects metrics in parallel
│   └── Aggregates results
│
└── Flask Test Application (apps/test_app/app.py)
    ├── Health check endpoint
    ├── CPU-intensive endpoints
    └── Data processing endpoints
```

---

## Prerequisites

### System Requirements

- **Python**: 3.9+ (upgrade to 3.10+ recommended)
- **AWS CLI**: v2 configured with credentials
- **Virtual Environment**: Already created and activated (see README.md)

### Python Dependencies

Verify all dependencies are installed:

```bash
pip install -r requirements.txt
```

Required packages:
- `boto3` - AWS SDK for Python
- `requests` - HTTP client library
- `flask` - Web framework for test application
- `pandas` - Data analysis and export
- `matplotlib` - Visualization (optional, for charts)

### AWS Prerequisites

1. **AWS Account Access**: Already configured from Phase 1
2. **Infrastructure Deployed**: Phase 1 deployment must be complete
3. **ALB Endpoint**: Note the ALB DNS name from Phase 1
   ```bash
   # Get ALB DNS from Phase 1 config
   cat infrastructure/alb-config.json | grep dns_name
   ```

### Verify Prerequisites

```bash
# Check Python version
python --version
# Expected: Python 3.9.x or higher

# Verify AWS credentials
aws sts get-caller-identity
# Expected: Shows your AWS account ID and user

# Check boto3 is installed
python -c "import boto3; print(boto3.__version__)"
# Expected: Version 1.26+
```

---

## Quick Start

### Option 1: Automated Setup (Recommended)

Phase 2B setup is typically handled by the setup.py script:

```bash
python scripts/setup.py
```

This automatically:
- Creates project directories
- Validates all dependencies
- Sets up Flask app structure
- Tests AWS connectivity

### Option 2: Manual Step-by-Step

Follow the detailed steps below to understand each component.

---

## Detailed Implementation Steps

### Step 1: Create Load Generator (load_generator.py)

**File**: `scripts/load_generator.py`

**Purpose**: Generate HTTP requests with configurable patterns to simulate real-world traffic.

**Implementation**:

```python
import requests
import time
import threading
from datetime import datetime

class LoadGenerator:
    def __init__(self, target_url, request_rate=10, duration_seconds=300, pattern="constant"):
        """
        Initialize load generator.
        
        Args:
            target_url: Target endpoint (e.g., http://alb-dns/api/compute)
            request_rate: Requests per second
            duration_seconds: How long to generate load
            pattern: "constant", "ramp", or "wave"
        """
        self.target_url = target_url
        self.request_rate = request_rate
        self.duration_seconds = duration_seconds
        self.pattern = pattern
        self.results = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time": 0,
            "errors": []
        }
    
    def generate_constant(self):
        """Generate constant rate load."""
        start_time = time.time()
        request_interval = 1.0 / self.request_rate
        request_times = []
        
        while time.time() - start_time < self.duration_seconds:
            loop_start = time.time()
            
            try:
                response = requests.get(self.target_url, timeout=30)
                response_time = (time.time() - loop_start) * 1000
                request_times.append(response_time)
                
                if response.status_code == 200:
                    self.results["successful"] += 1
                else:
                    self.results["failed"] += 1
            except Exception as e:
                self.results["failed"] += 1
                self.results["errors"].append(str(e))
            
            self.results["total_requests"] += 1
            
            # Sleep to maintain request rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, request_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Calculate averages
        if request_times:
            self.results["avg_response_time"] = sum(request_times) / len(request_times)
        
        return self.results
    
    def generate_ramp(self):
        """Generate ramp-up pattern (rate increases over time)."""
        # Similar to constant but with increasing rate
        pass
    
    def generate_wave(self):
        """Generate wave pattern (rate peaks and valleys)."""
        # Similar to constant but with wave-like variations
        pass
    
    def run(self):
        """Execute load generation based on selected pattern."""
        if self.pattern == "constant":
            return self.generate_constant()
        elif self.pattern == "ramp":
            return self.generate_ramp()
        elif self.pattern == "wave":
            return self.generate_wave()
        else:
            raise ValueError(f"Unknown pattern: {self.pattern}")
```

**Verification**:

```bash
# Test load generator with a simple echo endpoint
python -c "
from scripts.load_generator import LoadGenerator
gen = LoadGenerator(
    target_url='http://httpbin.org/get',
    request_rate=5,
    duration_seconds=10,
    pattern='constant'
)
results = gen.run()
print(f\"Total Requests: {results['total_requests']}\")
print(f\"Successful: {results['successful']}\")
print(f\"Failed: {results['failed']}\")
print(f\"Avg Response Time: {results['avg_response_time']:.2f}ms\")
"
```

**Expected Output**:
```
Total Requests: 50
Successful: 50
Failed: 0
Avg Response Time: 245.32ms
```

---

### Step 2: Create Metrics Collector (metrics_collector.py)

**File**: `scripts/metrics_collector.py`

**Purpose**: Poll AWS CloudWatch for autoscaling metrics during experiments.

**Implementation**:

```python
import boto3
import json
import csv
from datetime import datetime, timedelta

class MetricsCollector:
    def __init__(self, region="us-east-1"):
        """Initialize CloudWatch client."""
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)
        self.autoscaling = boto3.client("autoscaling", region_name=region)
        self.metrics = []
    
    def get_asg_metrics(self, asg_name, duration_minutes=30):
        """
        Collect metrics for an Auto Scaling Group.
        
        Args:
            asg_name: Name of ASG (e.g., "asg-cpu")
            duration_minutes: How many minutes back to query
        
        Returns:
            Dictionary with metric data
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        metrics_data = {
            "asg_name": asg_name,
            "cpu_utilization": [],
            "group_desired_capacity": [],
            "group_in_service_instances": [],
            "request_count": []
        }
        
        # Collect CPU Utilization
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,  # 1-minute intervals
            Statistics=["Average"]
        )
        metrics_data["cpu_utilization"] = response["Datapoints"]
        
        # Collect Group Desired Capacity
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/AutoScaling",
            MetricName="GroupDesiredCapacity",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=["Average"]
        )
        metrics_data["group_desired_capacity"] = response["Datapoints"]
        
        # Collect In-Service Instances
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/AutoScaling",
            MetricName="GroupInServiceInstances",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=["Average"]
        )
        metrics_data["group_in_service_instances"] = response["Datapoints"]
        
        return metrics_data
    
    def export_to_csv(self, filename, metrics_dict):
        """Export metrics to CSV file."""
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "metric_name", "value"])
            writer.writeheader()
            
            for metric_name, datapoints in metrics_dict.items():
                if metric_name == "asg_name":
                    continue
                for point in datapoints:
                    writer.writerow({
                        "timestamp": point.get("Timestamp", ""),
                        "metric_name": metric_name,
                        "value": point.get("Average", "")
                    })
```

**Verification**:

```bash
# Test metrics collector
python -c "
from scripts.metrics_collector import MetricsCollector
collector = MetricsCollector()
metrics = collector.get_asg_metrics('asg-cpu', duration_minutes=5)
print(f\"CPU Data Points: {len(metrics['cpu_utilization'])}\")
print(f\"Capacity Data Points: {len(metrics['group_desired_capacity'])}\")
"
```

---

### Step 3: Create Flask Test Application

**File**: `apps/test_app/app.py`

**Purpose**: Lightweight Flask application that responds to load with CPU-intensive operations.

**Implementation**:

```python
from flask import Flask, jsonify, request
import time
import os

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route("/api/compute", methods=["GET"])
def compute():
    """CPU-intensive computation endpoint."""
    intensity = int(request.args.get("intensity", 1))
    
    # Simulate CPU work
    result = 0
    for i in range(1000000 * intensity):
        result += i ** 2
    
    return jsonify({
        "status": "success",
        "computation": result,
        "intensity": intensity
    }), 200

@app.route("/api/data", methods=["GET"])
def data():
    """Data processing endpoint."""
    size = int(request.args.get("size", 1000))
    
    # Create and process data
    data_list = list(range(size))
    processed = sum(data_list) / len(data_list)
    
    return jsonify({
        "status": "success",
        "data_size": size,
        "average": processed
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

**Test Locally**:

```bash
# Start the app
python apps/test_app/app.py &

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/compute?intensity=1
curl http://localhost:5000/api/data?size=1000

# Kill the app
pkill -f "python apps/test_app/app.py"
```

---

### Step 4: Create Experiment Runner

**File**: `scripts/experiment_runner.py`

**Purpose**: Orchestrate load generation and metrics collection.

**Implementation**:

```python
import json
import threading
from datetime import datetime
from scripts.load_generator import LoadGenerator
from scripts.metrics_collector import MetricsCollector

class ExperimentRunner:
    def __init__(self, alb_endpoint, asg_names, experiment_name):
        self.alb_endpoint = alb_endpoint
        self.asg_names = asg_names
        self.experiment_name = experiment_name
        self.results = {}
    
    def run_experiment(self, duration_seconds=300, request_rate=10):
        """Run complete experiment with load generation and metrics."""
        # Start metrics collection in background
        collector = MetricsCollector()
        metrics_thread = threading.Thread(
            target=self._collect_metrics,
            args=(collector,)
        )
        metrics_thread.start()
        
        # Run load generation
        generator = LoadGenerator(
            target_url=f"http://{self.alb_endpoint}/api/compute",
            request_rate=request_rate,
            duration_seconds=duration_seconds,
            pattern="constant"
        )
        load_results = generator.run()
        
        # Wait for metrics collection to complete
        metrics_thread.join()
        
        # Aggregate results
        self.results = {
            "experiment": self.experiment_name,
            "timestamp": datetime.utcnow().isoformat(),
            "load": load_results,
            "metrics": self.metrics
        }
        
        return self.results
    
    def _collect_metrics(self, collector):
        """Collect metrics for all ASGs."""
        self.metrics = {}
        for asg_name in self.asg_names:
            self.metrics[asg_name] = collector.get_asg_metrics(asg_name)
    
    def save_results(self, filename):
        """Save experiment results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
```

---

## Verification Checklist

Before proceeding to Phase 3, verify each component:

- [ ] Load Generator
  ```bash
  python scripts/load_generator.py --help
  # Should show no errors
  ```

- [ ] Metrics Collector
  ```bash
  python -c "from scripts.metrics_collector import MetricsCollector; print('OK')"
  # Should print: OK
  ```

- [ ] Flask App (local test)
  ```bash
  python apps/test_app/app.py &
  sleep 2
  curl http://localhost:5000/health
  pkill -f "test_app"
  # Should show: {"status":"healthy"}
  ```

- [ ] All imports in experiment_runner.py
  ```bash
  python -c "from scripts.experiment_runner import ExperimentRunner; print('OK')"
  # Should print: OK
  ```

---

## Troubleshooting

### Problem: ImportError: No module named 'boto3'

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Problem: AWS credentials not found

**Solution**: Configure AWS CLI
```bash
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)
```

### Problem: ConnectionError when connecting to ALB

**Solution**: Verify Phase 1 deployment
```bash
# Get ALB DNS
cat infrastructure/alb-config.json | grep dns_name

# Test connectivity
curl http://<ALB-DNS>/health
```

### Problem: Flask app fails to start

**Solution**: Check port availability
```bash
# Check if port 5000 is in use
lsof -i :5000

# Use different port
PORT=5001 python apps/test_app/app.py
```

---

## Next Steps

Once Phase 2B components are verified:

1. Move test app to EC2 instances (Phase 3)
2. Deploy load generator and metrics collector to separate EC2 instance (Phase 3)
3. Configure autoscaling policies for both ASGs (Phase 3)
4. Run Phase 4-5 experiments using these tools

See **Phase 3 Deployment Guide** for next steps.
