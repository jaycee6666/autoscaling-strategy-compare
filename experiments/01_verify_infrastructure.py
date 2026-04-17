"""Task 1 - Verify autoscaling infrastructure health.

Cross-platform Python script (Windows/macOS/Linux), boto3-only for AWS calls.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:  # pragma: no cover - depends on local Python/OpenSSL environment
    import boto3  # type: ignore
except Exception:  # pragma: no cover - fallback for broken local boto3 deps
    boto3 = None  # type: ignore[assignment]


DEFAULT_REGION = "us-east-1"
DEFAULT_TIMEOUT_SECONDS = 10
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INFRA_DIR = PROJECT_ROOT / "infrastructure"
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"


class _UnavailableBoto3:
    @staticmethod
    def client(_service_name: str, **_kwargs: Any) -> Any:
        raise RuntimeError("boto3 is unavailable in this environment")


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: Dict[str, Any]


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


class InfrastructureHealthVerifier:
    """Checks ALB, target groups, ASGs and application health endpoint."""

    def __init__(
        self,
        region: str = DEFAULT_REGION,
        alb_dns: Optional[str] = None,
        cpu_asg_name: str = "asg-cpu",
        request_asg_name: str = "asg-request",
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.region = region
        self.alb_dns = alb_dns
        self.cpu_asg_name = cpu_asg_name
        self.request_asg_name = request_asg_name
        self.timeout_seconds = timeout_seconds

        boto3_module = boto3 if boto3 is not None else _UnavailableBoto3()
        self.autoscaling = boto3_module.client("autoscaling", region_name=self.region)
        self.elbv2 = boto3_module.client("elbv2", region_name=self.region)

    def _resolve_config(self) -> Dict[str, Any]:
        asg_config = _read_json(INFRA_DIR / "asg-config.json")
        alb_config = _read_json(INFRA_DIR / "alb-config.json")

        return {
            "cpu_asg_name": asg_config.get("cpu_asg_name", self.cpu_asg_name),
            "request_asg_name": asg_config.get(
                "request_asg_name", self.request_asg_name
            ),
            "alb_dns": alb_config.get("alb_dns", self.alb_dns),
            "alb_arn": alb_config.get("alb_arn"),
            "cpu_target_group_arn": alb_config.get("cpu_target_group_arn"),
            "request_target_group_arn": alb_config.get("request_target_group_arn"),
        }

    def _check_asg(self, asg_name: str) -> CheckResult:
        response = self.autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        groups = response.get("AutoScalingGroups", [])

        if not groups:
            return CheckResult(
                name=f"asg:{asg_name}",
                passed=False,
                details={"reason": "Auto Scaling Group not found"},
            )

        asg = groups[0]
        instances = asg.get("Instances", [])
        healthy_instances = [
            instance
            for instance in instances
            if instance.get("HealthStatus") == "Healthy"
        ]

        passed = len(instances) > 0 and len(healthy_instances) > 0
        return CheckResult(
            name=f"asg:{asg_name}",
            passed=passed,
            details={
                "min_size": asg.get("MinSize"),
                "max_size": asg.get("MaxSize"),
                "desired_capacity": asg.get("DesiredCapacity"),
                "instance_count": len(instances),
                "healthy_instance_count": len(healthy_instances),
            },
        )

    def _check_alb(self, alb_arn: Optional[str]) -> CheckResult:
        if not alb_arn:
            return CheckResult(
                name="alb:state",
                passed=False,
                details={
                    "reason": "ALB ARN missing from infrastructure/alb-config.json"
                },
            )

        response = self.elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])
        balancers = response.get("LoadBalancers", [])
        if not balancers:
            return CheckResult(
                name="alb:state",
                passed=False,
                details={"reason": "Load balancer not found"},
            )

        alb = balancers[0]
        state = alb.get("State", {}).get("Code")
        return CheckResult(
            name="alb:state",
            passed=state == "active",
            details={"state": state, "dns_name": alb.get("DNSName")},
        )

    def _check_target_group_health(
        self, target_group_arn: Optional[str]
    ) -> CheckResult:
        if not target_group_arn:
            return CheckResult(
                name="target_group:health",
                passed=False,
                details={"reason": "Target group ARN missing"},
            )

        response = self.elbv2.describe_target_health(TargetGroupArn=target_group_arn)
        descriptions = response.get("TargetHealthDescriptions", [])
        healthy = [
            item
            for item in descriptions
            if item.get("TargetHealth", {}).get("State") == "healthy"
        ]

        return CheckResult(
            name=f"target_group:{target_group_arn}",
            passed=len(descriptions) > 0 and len(healthy) > 0,
            details={
                "target_count": len(descriptions),
                "healthy_count": len(healthy),
            },
        )

    def _check_application_health(self, alb_dns: Optional[str]) -> CheckResult:
        if not alb_dns:
            return CheckResult(
                name="endpoint:/health",
                passed=False,
                details={"reason": "ALB DNS missing"},
            )

        url = f"http://{alb_dns}/health"
        response = requests.get(url, timeout=self.timeout_seconds)
        passed = response.status_code == 200
        response_json: Dict[str, Any] = {}
        try:
            response_json = response.json()
        except ValueError:
            response_json = {"raw": response.text[:200]}

        return CheckResult(
            name="endpoint:/health",
            passed=passed,
            details={
                "url": url,
                "status_code": response.status_code,
                "response": response_json,
            },
        )

    def verify(self) -> Dict[str, Any]:
        config = self._resolve_config()

        checks: List[CheckResult] = [
            self._check_asg(config["cpu_asg_name"]),
            self._check_asg(config["request_asg_name"]),
            self._check_alb(config.get("alb_arn")),
            self._check_target_group_health(config.get("cpu_target_group_arn")),
            self._check_target_group_health(config.get("request_target_group_arn")),
            self._check_application_health(config.get("alb_dns")),
        ]

        passed_checks = sum(1 for check in checks if check.passed)
        total_checks = len(checks)

        report = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "region": self.region,
            "config": {
                "cpu_asg_name": config["cpu_asg_name"],
                "request_asg_name": config["request_asg_name"],
                "alb_dns": config.get("alb_dns"),
            },
            "checks": [
                {"name": check.name, "passed": check.passed, "details": check.details}
                for check in checks
            ],
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "all_passed": passed_checks == total_checks,
            },
        }
        return report


def verify_infrastructure(region: str = DEFAULT_REGION) -> Dict[str, Any]:
    verifier = InfrastructureHealthVerifier(region=region)
    return verifier.verify()


def main() -> int:
    report = verify_infrastructure()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "infrastructure_health_report.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(json.dumps(report["summary"], indent=2))
    print(f"Saved report: {output_path}")

    return 0 if report["summary"]["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
