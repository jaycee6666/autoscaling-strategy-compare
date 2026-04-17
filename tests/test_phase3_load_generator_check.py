from __future__ import annotations

from deployment.test_load_generator import evaluate_success_rate, load_alb_dns


def test_evaluate_success_rate_passes_threshold() -> None:
    stats = {"total_requests": 10, "successful_requests": 8}
    assert evaluate_success_rate(stats, threshold=0.8)


def test_evaluate_success_rate_handles_zero_requests() -> None:
    stats = {"total_requests": 0, "successful_requests": 0}
    assert not evaluate_success_rate(stats, threshold=0.8)


def test_load_alb_dns_reads_existing_config_key() -> None:
    value = load_alb_dns({"alb_dns": "example-alb.us-east-1.elb.amazonaws.com"})
    assert value == "example-alb.us-east-1.elb.amazonaws.com"
