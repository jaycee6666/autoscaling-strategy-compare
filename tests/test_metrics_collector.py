import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock

from scripts.metrics_collector import MetricsCollector


def test_metrics_collector_initialization() -> None:
    """Test MetricsCollector initializes with correct parameters."""
    collector = MetricsCollector(
        asg_name="experiment-asg-cpu",
        region="us-east-1",
        poll_interval=10,
    )
    assert collector.asg_name == "experiment-asg-cpu"
    assert collector.region == "us-east-1"
    assert collector.poll_interval == 10


def test_metrics_collector_loads_infrastructure_config() -> None:
    """Test constructor can run with config defaults."""
    collector = MetricsCollector(asg_name="experiment-asg-cpu", region="us-east-1")
    assert collector.asg_name == "experiment-asg-cpu"


def test_metrics_collector_parse_cloudwatch_metric() -> None:
    """Test parsing CloudWatch metrics response."""
    collector = MetricsCollector(asg_name="experiment-asg-cpu", region="us-east-1")

    metric_data = {
        "Datapoints": [{"Timestamp": datetime(2026, 4, 17, 10, 0, 0), "Average": 45.5}]
    }

    value = collector._parse_metric_response(metric_data)
    assert value == 45.5


def test_metrics_collector_export_to_csv() -> None:
    """Test exporting collected metrics to CSV."""
    collector = MetricsCollector(asg_name="experiment-asg-cpu", region="us-east-1")

    collector.metrics_history = {
        "timestamp": ["2026-04-17T10:00:00", "2026-04-17T10:01:00"],
        "cpu_utilization": [45.5, 48.2],
        "instance_count": [2, 2],
        "request_rate": [150, 165],
        "network_in": [10.0, 12.0],
        "network_out": [20.0, 22.0],
        "healthy_instance_count": [2, 2],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "metrics.csv")
        collector.export_to_csv(output_file)

        assert os.path.exists(output_file)
        with open(output_file, "r", encoding="utf-8") as file:
            content = file.read()
            assert "timestamp" in content
            assert "cpu_utilization" in content


def test_collect_snapshot() -> None:
    """Test collect_snapshot returns expected fields."""
    cw = MagicMock()
    asg = MagicMock()

    cw.get_metric_statistics.side_effect = [
        {"Datapoints": [{"Timestamp": datetime.utcnow(), "Average": 41.0}]},
        {"Datapoints": [{"Timestamp": datetime.utcnow(), "Sum": 120.0}]},
        {"Datapoints": [{"Timestamp": datetime.utcnow(), "Sum": 11.0}]},
        {"Datapoints": [{"Timestamp": datetime.utcnow(), "Sum": 9.0}]},
    ]
    asg.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [
            {
                "DesiredCapacity": 2,
                "Instances": [{"HealthStatus": "Healthy"}, {"HealthStatus": "Healthy"}],
            }
        ]
    }

    collector = MetricsCollector(asg_name="experiment-asg-cpu", region="us-east-1")
    collector.cloudwatch = cw
    collector.autoscaling = asg
    snapshot = collector.collect_snapshot()

    assert snapshot is not None
    assert snapshot.cpu_utilization == 41.0
    assert snapshot.instance_count == 2
