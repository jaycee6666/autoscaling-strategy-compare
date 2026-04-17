import os
import tempfile
from unittest.mock import MagicMock

import pytest

from scripts.experiment_runner import ExperimentRunner


def test_experiment_runner_initialization() -> None:
    """Test ExperimentRunner initializes correctly."""
    runner = ExperimentRunner(
        experiment_name="cpu_strategy_test",
        asg_name="experiment-asg-cpu",
        alb_dns="http://example-alb.us-east-1.elb.amazonaws.com",
        region="us-east-1",
    )
    assert runner.experiment_name == "cpu_strategy_test"
    assert runner.asg_name == "experiment-asg-cpu"


def test_experiment_runner_creates_output_directory() -> None:
    """Test ExperimentRunner creates output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = ExperimentRunner(
            experiment_name="test",
            asg_name="test-asg",
            alb_dns="http://test.com",
            output_dir=tmpdir,
        )

        assert os.path.isdir(runner.output_dir)


def test_experiment_runner_config_validation() -> None:
    """Test ExperimentRunner validates load parameters."""
    with pytest.raises(ValueError):
        ExperimentRunner(
            experiment_name="test",
            asg_name="test-asg",
            alb_dns="http://test.com",
            request_rate=-5,
        )


def test_experiment_runner_run_success() -> None:
    """Test run executes coordination and returns result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = ExperimentRunner(
            experiment_name="test_run",
            asg_name="test-asg",
            alb_dns="http://test.com",
            output_dir=tmpdir,
            duration_seconds=1,
        )

        runner.load_generator = MagicMock()
        runner.metrics_collector = MagicMock()
        runner.load_generator.generate_load.return_value = {
            "total_requests": 10,
            "successful_requests": 10,
            "failed_requests": 0,
            "response_times": [0.1, 0.2],
            "errors": [],
            "average_response_time": 0.15,
            "p95_response_time": 0.2,
            "duration": 1.0,
            "pattern": "constant",
            "request_rate": 10,
        }
        runner.metrics_collector.get_summary_stats.return_value = {
            "total_samples": 1,
            "avg_cpu_utilization": 50.0,
            "max_cpu_utilization": 50.0,
            "min_cpu_utilization": 50.0,
            "avg_instance_count": 2.0,
            "max_instance_count": 2,
            "min_instance_count": 2,
        }

        result = runner.run()
        assert result["name"] == "test_run"
        assert result["load_stats"]["successful_requests"] == 10
