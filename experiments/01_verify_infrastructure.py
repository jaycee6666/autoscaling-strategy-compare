"""Task 1 - Verify autoscaling infrastructure health (Enhanced).

This enhanced version:
- Identifies active target groups (those receiving traffic from ALB listeners/rules).
- For active target groups: requires at least 1 healthy instance (matches DesiredCapacity=1).
- For standby target groups: only requires instances exist (health check deferred).
- Checks ASG, ALB, target groups, security groups, scaling policies, launch templates,
  IAM instance profile, and application health endpoint.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests

try:
    import boto3
except ImportError:
    boto3 = None

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
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class InfrastructureHealthVerifier:
    """Verifies ALB, target groups, ASGs, and application health endpoint."""

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
        self.ec2 = boto3_module.client("ec2", region_name=self.region)
        self.iam = boto3_module.client("iam")

    def _resolve_config(self) -> Dict[str, Any]:
        asg_config = _read_json(INFRA_DIR / "asg-config.json")
        alb_config = _read_json(INFRA_DIR / "alb-config.json")

        config = {
            "cpu_asg_name": asg_config.get("cpu_asg_name", self.cpu_asg_name),
            "request_asg_name": asg_config.get("request_asg_name", self.request_asg_name),
            "alb_dns": alb_config.get("alb_dns", self.alb_dns),
            "alb_arn": alb_config.get("alb_arn"),
            "cpu_target_group_arn": alb_config.get("cpu_target_group_arn"),
            "request_target_group_arn": alb_config.get("request_target_group_arn"),
            "listener_arn": alb_config.get("listener_arn"),
        }

        # Get ALB security group ID
        try:
            if config.get("alb_arn"):
                alb_resp = self.elbv2.describe_load_balancers(LoadBalancerArns=[config["alb_arn"]])
                if alb_resp.get("LoadBalancers"):
                    sg_ids = alb_resp["LoadBalancers"][0].get("SecurityGroups", [])
                    if sg_ids:
                        config["alb_sg_id"] = sg_ids[0]
        except Exception:
            pass

        # Get App security group ID from ASG instance
        try:
            asg_resp = self.autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=[config["cpu_asg_name"]]
            )
            if asg_resp.get("AutoScalingGroups"):
                instances = asg_resp["AutoScalingGroups"][0].get("Instances", [])
                if instances:
                    instance_id = instances[0].get("InstanceId")
                    if instance_id:
                        ec2_resp = self.ec2.describe_instances(InstanceIds=[instance_id])
                        if ec2_resp.get("Reservations"):
                            sgs = ec2_resp["Reservations"][0].get("Instances", [{}])[0].get("SecurityGroups", [])
                            if sgs:
                                config["app_sg_id"] = sgs[0].get("GroupId")
        except Exception:
            pass

        return config

    def _get_active_target_groups(self, alb_arn: Optional[str]) -> Set[str]:
        """Return set of target group ARNs that are currently receiving traffic from ALB."""
        if not alb_arn:
            return set()
        active = set()
        try:
            # Default listener actions
            listeners = self.elbv2.describe_listeners(LoadBalancerArn=alb_arn).get("Listeners", [])
            for listener in listeners:
                for action in listener.get("DefaultActions", []):
                    if action.get("Type") == "forward" and action.get("TargetGroupArn"):
                        active.add(action["TargetGroupArn"])
                # Also check listener rules (optional)
                try:
                    rules = self.elbv2.describe_rules(ListenerArn=listener["ListenerArn"]).get("Rules", [])
                    for rule in rules:
                        for action in rule.get("Actions", []):
                            if action.get("Type") == "forward" and action.get("TargetGroupArn"):
                                active.add(action["TargetGroupArn"])
                except Exception:
                    pass
        except Exception:
            pass
        return active

    def _check_asg(self, asg_name: str) -> CheckResult:
        try:
            resp = self.autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
            groups = resp.get("AutoScalingGroups", [])
            if not groups:
                return CheckResult(name=f"asg:{asg_name}", passed=False, details={"reason": "ASG not found"})

            asg = groups[0]
            instances = asg.get("Instances", [])
            healthy_instances = [i for i in instances if i.get("HealthStatus") == "Healthy"]
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
        except Exception as e:
            return CheckResult(name=f"asg:{asg_name}", passed=False, details={"error": str(e)})

    def _check_alb(self, alb_arn: Optional[str]) -> CheckResult:
        if not alb_arn:
            return CheckResult(name="alb:state", passed=False, details={"reason": "ALB ARN missing"})
        try:
            resp = self.elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])
            balancers = resp.get("LoadBalancers", [])
            if not balancers:
                return CheckResult(name="alb:state", passed=False, details={"reason": "ALB not found"})
            alb = balancers[0]
            state = alb.get("State", {}).get("Code")
            return CheckResult(
                name="alb:state",
                passed=(state == "active"),
                details={"state": state, "dns_name": alb.get("DNSName")},
            )
        except Exception as e:
            return CheckResult(name="alb:state", passed=False, details={"error": str(e)})

    def _check_target_group_health(
        self, target_group_arn: Optional[str], is_active: bool, tg_name: str
    ) -> CheckResult:
        if not target_group_arn:
            return CheckResult(
                name=f"target_group:{tg_name}:health",
                passed=False,
                details={"reason": "Target group ARN missing"},
            )
        try:
            resp = self.elbv2.describe_target_health(TargetGroupArn=target_group_arn)
            descriptions = resp.get("TargetHealthDescriptions", [])
            healthy = [t for t in descriptions if t.get("TargetHealth", {}).get("State") == "healthy"]
            unused = [t for t in descriptions if t.get("TargetHealth", {}).get("State") == "unused"]
            target_count = len(descriptions)

            if is_active:
                # Active target group: must have at least 1 healthy instance
                passed = target_count > 0 and len(healthy) >= 1
                status = "ACTIVE (ALB forwards traffic)"
            else:
                # Standby target group: only need registered instances, health can be deferred
                passed = target_count > 0
                status = "STANDBY (registered instances exist, health check deferred)"

            return CheckResult(
                name=f"target_group:{tg_name}:health",
                passed=passed,
                details={
                    "target_group_arn": target_group_arn,
                    "status": status,
                    "target_count": target_count,
                    "healthy_count": len(healthy),
                    "unused_count": len(unused),
                    "is_active": is_active,
                },
            )
        except Exception as e:
            return CheckResult(name=f"target_group:{tg_name}:health", passed=False, details={"error": str(e)})

    def _check_target_group_configuration(self, target_group_arn: Optional[str], tg_name: str) -> CheckResult:
        if not target_group_arn:
            return CheckResult(name=f"target_group_config:{tg_name}", passed=False, details={"reason": "ARN missing"})
        try:
            resp = self.elbv2.describe_target_groups(TargetGroupArns=[target_group_arn])
            tgs = resp.get("TargetGroups", [])
            if not tgs:
                return CheckResult(name=f"target_group_config:{tg_name}", passed=False, details={"reason": "Not found"})
            tg = tgs[0]
            path = tg.get("HealthCheckPath", "")
            interval = tg.get("HealthCheckIntervalSeconds")
            healthy_threshold = tg.get("HealthyThresholdCount")
            unhealthy_threshold = tg.get("UnhealthyThresholdCount")
            path_ok = (path == "/health")
            interval_ok = (interval == 30)
            healthy_ok = (healthy_threshold == 2)
            unhealthy_ok = (unhealthy_threshold == 3)
            passed = path_ok and interval_ok and healthy_ok and unhealthy_ok
            return CheckResult(
                name=f"target_group_config:{tg_name}",
                passed=passed,
                details={
                    "health_check_path": path,
                    "health_check_interval_seconds": interval,
                    "healthy_threshold_count": healthy_threshold,
                    "unhealthy_threshold_count": unhealthy_threshold,
                    "path_valid": path_ok,
                    "interval_valid": interval_ok,
                    "healthy_threshold_valid": healthy_ok,
                    "unhealthy_threshold_valid": unhealthy_ok,
                },
            )
        except Exception as e:
            return CheckResult(name=f"target_group_config:{tg_name}", passed=False, details={"error": str(e)})

    def _check_security_group_rules(self, sg_id: Optional[str], sg_name: str) -> CheckResult:
        if not sg_id:
            return CheckResult(name=f"security_group:{sg_name}", passed=False, details={"reason": "SG ID missing"})
        try:
            resp = self.ec2.describe_security_groups(GroupIds=[sg_id])
            sgs = resp.get("SecurityGroups", [])
            if not sgs:
                return CheckResult(name=f"security_group:{sg_name}", passed=False, details={"reason": "Not found"})
            sg = sgs[0]
            ingress = sg.get("IpPermissions", [])
            egress = sg.get("IpPermissionsEgress", [])

            required_ports = set()
            if "alb" in sg_name.lower():
                required_ports = {80, 443}
            elif "app" in sg_name.lower():
                required_ports = {8080}

            ingress_ok = True
            if required_ports:
                allowed = set()
                for rule in ingress:
                    from_port = rule.get("FromPort", 0)
                    to_port = rule.get("ToPort", 0)
                    for port in required_ports:
                        if from_port <= port <= to_port:
                            allowed.add(port)
                ingress_ok = required_ports.issubset(allowed)

            egress_ok = len(egress) > 0
            passed = ingress_ok and egress_ok
            return CheckResult(
                name=f"security_group:{sg_name}",
                passed=passed,
                details={
                    "sg_id": sg_id,
                    "ingress_rule_count": len(ingress),
                    "egress_rule_count": len(egress),
                    "ingress_ok": ingress_ok,
                    "egress_ok": egress_ok,
                    "required_ports": list(required_ports),
                },
            )
        except Exception as e:
            return CheckResult(name=f"security_group:{sg_name}", passed=False, details={"error": str(e)})

    def _check_asg_scaling_policies(self, asg_name: str) -> CheckResult:
        try:
            resp = self.autoscaling.describe_policies(AutoScalingGroupName=asg_name)
            policies = resp.get("ScalingPolicies", [])
            if not policies:
                return CheckResult(name=f"asg_policies:{asg_name}", passed=False, details={"reason": "No policies"})
            target_tracking = [p for p in policies if p.get("PolicyType") == "TargetTrackingScaling"]
            if not target_tracking:
                return CheckResult(name=f"asg_policies:{asg_name}", passed=False, details={"reason": "No target tracking"})
            policies_ok = all(p.get("TargetTrackingConfiguration", {}).get("TargetValue", 0) > 0 for p in target_tracking)
            return CheckResult(
                name=f"asg_policies:{asg_name}",
                passed=policies_ok,
                details={
                    "total_policies": len(policies),
                    "target_tracking_policies": len(target_tracking),
                    "policies_valid": policies_ok,
                },
            )
        except Exception as e:
            return CheckResult(name=f"asg_policies:{asg_name}", passed=False, details={"error": str(e)})

    def _check_launch_template(self, asg_name: str) -> CheckResult:
        try:
            asg_resp = self.autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
            groups = asg_resp.get("AutoScalingGroups", [])
            if not groups:
                return CheckResult(name=f"launch_template:{asg_name}", passed=False, details={"reason": "ASG not found"})
            lt = groups[0].get("LaunchTemplate", {})
            lt_id = lt.get("LaunchTemplateId")
            if not lt_id:
                return CheckResult(name=f"launch_template:{asg_name}", passed=False, details={"reason": "No launch template"})
            lt_resp = self.ec2.describe_launch_template_versions(LaunchTemplateId=lt_id)
            versions = lt_resp.get("LaunchTemplateVersions", [])
            if not versions:
                return CheckResult(name=f"launch_template:{asg_name}", passed=False, details={"reason": "No versions"})
            data = versions[0].get("LaunchTemplateData", {})
            instance_type = data.get("InstanceType", "")
            image_id = data.get("ImageId", "")
            user_data = data.get("UserData", "")
            passed = bool(instance_type) and bool(image_id) and bool(user_data)
            return CheckResult(
                name=f"launch_template:{asg_name}",
                passed=passed,
                details={
                    "instance_type": instance_type,
                    "image_id": image_id,
                    "user_data_present": bool(user_data),
                    "instance_type_ok": bool(instance_type),
                    "image_id_ok": bool(image_id),
                    "user_data_ok": bool(user_data),
                },
            )
        except Exception as e:
            return CheckResult(name=f"launch_template:{asg_name}", passed=False, details={"error": str(e)})

    def _check_iam_instance_profile(self, asg_name: str) -> CheckResult:
        try:
            asg_resp = self.autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
            groups = asg_resp.get("AutoScalingGroups", [])
            if not groups:
                return CheckResult(name=f"iam_instance_profile:{asg_name}", passed=False, details={"reason": "ASG not found"})
            lt = groups[0].get("LaunchTemplate", {})
            lt_id = lt.get("LaunchTemplateId")
            if not lt_id:
                return CheckResult(name=f"iam_instance_profile:{asg_name}", passed=False, details={"reason": "No launch template"})
            lt_resp = self.ec2.describe_launch_template_versions(LaunchTemplateId=lt_id)
            versions = lt_resp.get("LaunchTemplateVersions", [])
            if not versions:
                return CheckResult(name=f"iam_instance_profile:{asg_name}", passed=False, details={"reason": "No versions"})
            profile = versions[0].get("LaunchTemplateData", {}).get("IamInstanceProfile", {})
            profile_arn = profile.get("Arn", "")
            profile_name = profile.get("Name", "")
            passed = bool(profile_arn or profile_name)
            return CheckResult(
                name=f"iam_instance_profile:{asg_name}",
                passed=passed,
                details={
                    "profile_arn": profile_arn,
                    "profile_name": profile_name,
                    "profile_attached": passed,
                },
            )
        except Exception as e:
            return CheckResult(name=f"iam_instance_profile:{asg_name}", passed=False, details={"error": str(e)})

    def _check_application_health(self, alb_dns: Optional[str]) -> CheckResult:
        if not alb_dns:
            return CheckResult(name="endpoint:/health", passed=False, details={"reason": "ALB DNS missing"})
        url = f"http://{alb_dns}/health"
        try:
            # Use a session that ignores system proxy (if any)
            session = requests.Session()
            session.trust_env = False
            response = session.get(url, timeout=self.timeout_seconds)
            passed = response.status_code == 200
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
        except Exception as e:
            return CheckResult(name="endpoint:/health", passed=False, details={"url": url, "error": str(e)})

    def verify(self) -> Dict[str, Any]:
        config = self._resolve_config()
        active_tgs = self._get_active_target_groups(config.get("alb_arn"))

        cpu_tg_arn = config.get("cpu_target_group_arn")
        request_tg_arn = config.get("request_target_group_arn")
        is_cpu_active = cpu_tg_arn in active_tgs if cpu_tg_arn else False
        is_request_active = request_tg_arn in active_tgs if request_tg_arn else False

        checks: List[CheckResult] = [
            self._check_asg(config["cpu_asg_name"]),
            self._check_asg(config["request_asg_name"]),
            self._check_alb(config.get("alb_arn")),
            self._check_target_group_health(cpu_tg_arn, is_cpu_active, "cpu"),
            self._check_target_group_health(request_tg_arn, is_request_active, "request"),
            self._check_target_group_configuration(cpu_tg_arn, "cpu"),
            self._check_target_group_configuration(request_tg_arn, "request"),
            self._check_security_group_rules(config.get("alb_sg_id"), "ALB"),
            self._check_security_group_rules(config.get("app_sg_id"), "App"),
            self._check_asg_scaling_policies(config["cpu_asg_name"]),
            self._check_asg_scaling_policies(config["request_asg_name"]),
            self._check_launch_template(config["cpu_asg_name"]),
            self._check_launch_template(config["request_asg_name"]),
            self._check_iam_instance_profile(config["cpu_asg_name"]),
            self._check_iam_instance_profile(config["request_asg_name"]),
            self._check_application_health(config.get("alb_dns")),
        ]

        passed_checks = sum(1 for c in checks if c.passed)
        total_checks = len(checks)

        report = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "region": self.region,
            "config": {
                "cpu_asg_name": config["cpu_asg_name"],
                "request_asg_name": config["request_asg_name"],
                "alb_dns": config.get("alb_dns"),
            },
            "active_target_groups": list(active_tgs),
            "checks": [{"name": c.name, "passed": c.passed, "details": c.details} for c in checks],
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
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["summary"], indent=2))
    print(f"Saved report: {output_path}")
    return 0 if report["summary"]["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())