from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "experiments"
    / "01_verify_infrastructure.py"
)
_SPEC = importlib.util.spec_from_file_location("verify_infra_mod", MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Failed to load experiments/01_verify_infrastructure.py")
verify_module = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = verify_module
_SPEC.loader.exec_module(verify_module)


def _fake_config(
    cpu_asg_name: str = "asg-cpu",
    request_asg_name: str = "asg-request",
    alb_dns: str = "example-alb.us-east-1.elb.amazonaws.com",
) -> Dict[str, Any]:
    return {
        "cpu_asg_name": cpu_asg_name,
        "request_asg_name": request_asg_name,
        "alb_dns": alb_dns,
        "alb_arn": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/test/1",
        "cpu_target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123:targetgroup/cpu/1",
        "request_target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123:targetgroup/request/1",
    }


@pytest.fixture
def verifier(monkeypatch: pytest.MonkeyPatch) -> Any:
    if verify_module.boto3 is not None:
        monkeypatch.setattr(
            verify_module.boto3, "client", lambda *_a, **_k: MagicMock()
        )
    else:
        monkeypatch.setattr(
            verify_module._UnavailableBoto3, "client", lambda *_a, **_k: MagicMock()
        )
    return verify_module.InfrastructureHealthVerifier(region="us-east-1")


def test_verify_success(monkeypatch: pytest.MonkeyPatch, verifier: Any) -> None:
    monkeypatch.setattr(verifier, "_resolve_config", lambda: _fake_config())
    monkeypatch.setattr(
        verifier, "_check_asg", lambda _n: verify_module.CheckResult("asg", True, {})
    )
    monkeypatch.setattr(
        verifier, "_check_alb", lambda _a: verify_module.CheckResult("alb", True, {})
    )
    monkeypatch.setattr(
        verifier,
        "_check_target_group_health",
        lambda _a: verify_module.CheckResult("tg", True, {}),
    )
    monkeypatch.setattr(
        verifier,
        "_check_application_health",
        lambda _d: verify_module.CheckResult("health", True, {}),
    )

    report = verifier.verify()
    assert report["summary"]["all_passed"] is True
    assert report["summary"]["failed_checks"] == 0


def test_check_asg_not_found(verifier: Any) -> None:
    verifier.autoscaling.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": []
    }
    result = verifier._check_asg("asg-missing")
    assert result.passed is False
    assert "not found" in result.details["reason"].lower()


def test_check_asg_found_healthy(verifier: Any) -> None:
    verifier.autoscaling.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [
            {
                "MinSize": 1,
                "MaxSize": 4,
                "DesiredCapacity": 2,
                "Instances": [
                    {"HealthStatus": "Healthy"},
                    {"HealthStatus": "Healthy"},
                ],
            }
        ]
    }
    result = verifier._check_asg("asg-cpu")
    assert result.passed is True
    assert result.details["healthy_instance_count"] == 2


def test_check_application_health_ok(
    monkeypatch: pytest.MonkeyPatch, verifier: Any
) -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"status": "healthy"}
    monkeypatch.setattr(verify_module.requests, "get", lambda *_a, **_k: response)

    result = verifier._check_application_health("example-alb")
    assert result.passed is True
    assert result.details["status_code"] == 200


def test_check_target_group_health_unused_ok(verifier: Any) -> None:
    verifier.elbv2.describe_target_health.return_value = {
        "TargetHealthDescriptions": [
            {
                "TargetHealth": {
                    "State": "unused",
                    "Reason": "Target.NotInUse",
                }
            }
        ]
    }

    result = verifier._check_target_group_health("arn:aws:elasticloadbalancing:us-east-1:123:targetgroup/cpu/1")
    assert result.passed is True
    assert result.details["unused_count"] == 1
