"""Deploy Flask test application to existing ASG instances via boto3.

This script updates launch template user data, triggers ASG instance refresh,
waits for healthy targets, and verifies ALB health endpoint connectivity.
"""

from __future__ import annotations

import argparse
import base64
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

import requests


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_alb_dns(config: Dict[str, Any]) -> str:
    for key in ("alb_dns", "alb_dns_name"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise KeyError("ALB DNS not found in alb-config.json (expected alb_dns)")


def build_asg_subnet_identifier(subnet_ids: Sequence[str]) -> str:
    return ",".join(subnet_ids)


def build_user_data(app_source: str) -> str:
    return f"""#!/bin/bash
set -euo pipefail

yum update -y
yum install -y python3 python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install flask boto3 requests

mkdir -p /opt/test_app
cat > /opt/test_app/app.py <<'PYAPP'
{app_source}
PYAPP

cat > /etc/systemd/system/test-app.service <<'SERVICE'
[Unit]
Description=Autoscaling Experiment Flask Test App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/test_app
ExecStart=/usr/bin/python3 /opt/test_app/app.py
Restart=always
RestartSec=5
Environment=AWS_REGION=us-east-1

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable test-app.service
systemctl restart test-app.service

for _ in {{1..30}}; do
  if curl -sf http://127.0.0.1:8080/health >/dev/null; then
    exit 0
  fi
  sleep 2
done

exit 1
"""


@dataclass
class HealthProbeResult:
    success: bool
    attempts: int
    successes: int
    status_codes: List[int]
    last_body: str


class FlaskAppDeployer:
    def __init__(self, region: str, project_root: Path) -> None:
        self.region = region
        self.project_root = project_root
        self.infrastructure_dir = project_root / "infrastructure"
        self.app_source_path = project_root / "apps" / "test_app" / "app.py"
        self.output_path = project_root / "deployment" / "deploy_app_report.json"

        import boto3

        self.ec2 = boto3.client("ec2", region_name=region)
        self.autoscaling = boto3.client("autoscaling", region_name=region)
        self.elbv2 = boto3.client("elbv2", region_name=region)

    def _load_inputs(self) -> Dict[str, Any]:
        alb_config = read_json(self.infrastructure_dir / "alb-config.json")
        asg_config = read_json(self.infrastructure_dir / "asg-config.json")
        lt_config = read_json(self.infrastructure_dir / "launch-templates-config.json")
        network_config = read_json(self.infrastructure_dir / "network-config.json")

        app_source = self.app_source_path.read_text(encoding="utf-8")

        return {
            "alb_dns": extract_alb_dns(alb_config),
            "listener_arn": alb_config["listener_arn"],
            "cpu_asg_name": asg_config["cpu_asg_name"],
            "request_asg_name": asg_config["request_asg_name"],
            "cpu_template_id": lt_config["cpu_template_id"],
            "request_template_id": lt_config["request_template_id"],
            "cpu_target_group_arn": alb_config["cpu_target_group_arn"],
            "request_target_group_arn": alb_config["request_target_group_arn"],
            "public_subnets": [
                network_config["public_subnet_1_id"],
                network_config["public_subnet_2_id"],
            ],
            "private_route_table_id": network_config["route_table_private_id"],
            "app_source": app_source,
        }

    def _private_route_has_default_egress(self, route_table_id: str) -> bool:
        response = self.ec2.describe_route_tables(RouteTableIds=[route_table_id])
        route_tables = response.get("RouteTables", [])
        if not route_tables:
            return False

        for route in route_tables[0].get("Routes", []):
            if (
                route.get("DestinationCidrBlock") == "0.0.0.0/0"
                and route.get("State") == "active"
            ):
                return True
        return False

    def _update_asg_subnets(self, asg_name: str, subnet_ids: Sequence[str]) -> None:
        self.autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            VPCZoneIdentifier=build_asg_subnet_identifier(subnet_ids),
        )

    def _describe_asgs(self, asg_names: Sequence[str]) -> Dict[str, Any]:
        response = self.autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=list(asg_names)
        )
        groups = response.get("AutoScalingGroups", [])
        return {group["AutoScalingGroupName"]: group for group in groups}

    def _create_launch_template_version(self, template_id: str, user_data: str) -> str:
        encoded_user_data = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")
        response = self.ec2.create_launch_template_version(
            LaunchTemplateId=template_id,
            SourceVersion="$Latest",
            VersionDescription=f"phase3-flask-deploy-{int(time.time())}",
            LaunchTemplateData={"UserData": encoded_user_data},
        )
        return str(response["LaunchTemplateVersion"]["VersionNumber"])

    def _update_asg_launch_template(
        self, asg_name: str, template_id: str, template_version: str
    ) -> None:
        self.autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                "LaunchTemplateId": template_id,
                "Version": template_version,
            },
        )

    def _start_instance_refresh(self, asg_name: str) -> str:
        try:
            response = self.autoscaling.start_instance_refresh(
                AutoScalingGroupName=asg_name,
                Preferences={"InstanceWarmup": 120, "MinHealthyPercentage": 50},
                Strategy="Rolling",
            )
            return str(response["InstanceRefreshId"])
        except Exception as error:
            # Botocore is not imported at module load to keep tests import-safe.
            if not hasattr(error, "response"):
                raise
            response = getattr(error, "response", {})
            code = response.get("Error", {}).get("Code", "")
            if code in {"InstanceRefreshInProgressFault", "InstanceRefreshInProgress"}:
                refreshes = self.autoscaling.describe_instance_refreshes(
                    AutoScalingGroupName=asg_name,
                    MaxRecords=10,
                ).get("InstanceRefreshes", [])
                for refresh in refreshes:
                    if refresh.get("Status") in {
                        "Pending",
                        "InProgress",
                        "Cancelling",
                    }:
                        return str(
                            refresh.get("InstanceRefreshId", "already-in-progress")
                        )
                return "already-in-progress"
            raise

    def _wait_for_asg_health(
        self, asg_names: Sequence[str], timeout_seconds: int = 1800
    ) -> Dict[str, Any]:
        start = time.monotonic()
        while time.monotonic() - start < timeout_seconds:
            details = self._describe_asgs(asg_names)
            all_healthy = True

            for name in asg_names:
                group = details.get(name)
                if not group:
                    all_healthy = False
                    continue

                desired = int(group.get("DesiredCapacity", 0))
                instances = group.get("Instances", [])
                healthy = [
                    inst
                    for inst in instances
                    if inst.get("HealthStatus") == "Healthy"
                    and inst.get("LifecycleState") == "InService"
                ]
                if len(healthy) < max(1, desired):
                    all_healthy = False

            if all_healthy:
                return {"ready": True, "details": details}

            time.sleep(20)

        return {"ready": False, "details": self._describe_asgs(asg_names)}

    def _wait_for_target_group_health(
        self, target_group_arns: Sequence[str], timeout_seconds: int = 900
    ) -> Dict[str, Any]:
        start = time.monotonic()
        latest: Dict[str, Any] = {}

        while time.monotonic() - start < timeout_seconds:
            all_ok = True
            for arn in target_group_arns:
                response = self.elbv2.describe_target_health(TargetGroupArn=arn)
                health = response.get("TargetHealthDescriptions", [])
                healthy_count = sum(
                    1
                    for item in health
                    if item.get("TargetHealth", {}).get("State") == "healthy"
                )
                latest[arn] = {
                    "total": len(health),
                    "healthy": healthy_count,
                }
                if healthy_count < 1:
                    all_ok = False

            if all_ok:
                return {"ready": True, "target_groups": latest}

            time.sleep(15)

        return {"ready": False, "target_groups": latest}

    def _get_listener_forward_target_group(self, listener_arn: str) -> str | None:
        response = self.elbv2.describe_listeners(ListenerArns=[listener_arn])
        listeners = response.get("Listeners", [])
        if not listeners:
            return None
        actions = listeners[0].get("DefaultActions", [])
        for action in actions:
            if action.get("Type") == "forward" and action.get("TargetGroupArn"):
                return str(action["TargetGroupArn"])
        return None

    def _probe_alb_health(
        self, alb_dns: str, attempts: int = 20, interval_seconds: int = 5
    ) -> HealthProbeResult:
        url = f"http://{alb_dns}/health"
        successes = 0
        status_codes: List[int] = []
        last_body = ""

        for _ in range(attempts):
            try:
                response = requests.get(url, timeout=10)
                status_codes.append(response.status_code)
                last_body = response.text[:300]
                if response.status_code == 200:
                    successes += 1
            except requests.RequestException:
                status_codes.append(0)
            time.sleep(interval_seconds)

        return HealthProbeResult(
            success=successes > 0,
            attempts=attempts,
            successes=successes,
            status_codes=status_codes,
            last_body=last_body,
        )

    def deploy(self) -> Dict[str, Any]:
        inputs = self._load_inputs()
        app_user_data = build_user_data(inputs["app_source"])

        asg_pairs = [
            {
                "asg": inputs["cpu_asg_name"],
                "template_id": inputs["cpu_template_id"],
            },
            {
                "asg": inputs["request_asg_name"],
                "template_id": inputs["request_template_id"],
            },
        ]

        existing_asgs = self._describe_asgs([p["asg"] for p in asg_pairs])
        running_instances_before = {
            name: len(
                [
                    inst
                    for inst in group.get("Instances", [])
                    if inst.get("LifecycleState") in {"InService", "Pending"}
                ]
            )
            for name, group in existing_asgs.items()
        }

        template_updates: Dict[str, str] = {}
        refresh_ids: Dict[str, str] = {}
        subnet_updates: Dict[str, str] = {}

        has_private_egress = self._private_route_has_default_egress(
            inputs["private_route_table_id"]
        )
        if not has_private_egress:
            public_identifier = build_asg_subnet_identifier(inputs["public_subnets"])
            for pair in asg_pairs:
                self._update_asg_subnets(pair["asg"], inputs["public_subnets"])
                subnet_updates[pair["asg"]] = public_identifier

        for pair in asg_pairs:
            version = self._create_launch_template_version(
                template_id=pair["template_id"], user_data=app_user_data
            )
            template_updates[pair["asg"]] = version
            self._update_asg_launch_template(pair["asg"], pair["template_id"], version)
            refresh_ids[pair["asg"]] = self._start_instance_refresh(pair["asg"])

        asg_health = self._wait_for_asg_health([p["asg"] for p in asg_pairs])
        active_listener_tg = self._get_listener_forward_target_group(
            inputs["listener_arn"]
        )
        target_arns_for_success = (
            [active_listener_tg]
            if active_listener_tg
            else [inputs["cpu_target_group_arn"], inputs["request_target_group_arn"]]
        )
        target_health = self._wait_for_target_group_health(target_arns_for_success)
        all_target_snapshot = self._wait_for_target_group_health(
            [inputs["cpu_target_group_arn"], inputs["request_target_group_arn"]],
            timeout_seconds=5,
        )
        probe = self._probe_alb_health(inputs["alb_dns"])

        report: Dict[str, Any] = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "region": self.region,
            "alb_dns": inputs["alb_dns"],
            "running_instances_before": running_instances_before,
            "launch_template_versions": template_updates,
            "instance_refresh_ids": refresh_ids,
            "subnet_updates": subnet_updates,
            "private_route_has_default_egress": has_private_egress,
            "asg_health": {
                "ready": asg_health["ready"],
                "details": {
                    name: {
                        "desired": detail.get("DesiredCapacity"),
                        "instances": [
                            {
                                "instance_id": inst.get("InstanceId"),
                                "health": inst.get("HealthStatus"),
                                "lifecycle": inst.get("LifecycleState"),
                            }
                            for inst in detail.get("Instances", [])
                        ],
                    }
                    for name, detail in asg_health["details"].items()
                },
            },
            "target_group_health": target_health,
            "all_target_group_snapshot": all_target_snapshot,
            "active_listener_target_group": active_listener_tg,
            "alb_health_probe": asdict(probe),
            "success": bool(
                asg_health["ready"] and target_health["ready"] and probe.success
            ),
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2)

        return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy Flask app to ASG instances")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    deployer = FlaskAppDeployer(region=args.region, project_root=args.project_root)
    report = deployer.deploy()
    print(json.dumps(report, indent=2))
    return 0 if report.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
