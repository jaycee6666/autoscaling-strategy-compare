#!/usr/bin/env python3
"""
Task 6: AWS Auto Scaling Groups (ASG) Setup
============================================

Creates two Auto Scaling Groups with different scaling policies:
  1. CPU-based: Scales based on CPU utilization
  2. Request-rate-based: Scales based on request rate

Dependencies:
  - Requires network-config.json (Subnets)
  - Requires launch-templates-config.json (Launch template IDs)
  - Requires alb-config.json (Target group ARNs)

Output:
  - infrastructure/asg-config.json

AWS Resources Created:
  - Auto Scaling Group: asg-cpu
  - Auto Scaling Group: asg-request
  - Scaling Policies for each (Target Tracking)
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ASGSetup:
    """Manages AWS Auto Scaling Groups."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize autoscaling client."""
        self.autoscaling = boto3.client("autoscaling", region_name=region)
        self.region = region
        self.config: Dict[str, Any] = {}

    def load_config(self, config_path: Path) -> Dict[str, str]:
        """Load configuration from JSON file."""
        try:
            logger.info(f"Loading configuration from {config_path}...")
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info("✓ Configuration loaded")
            return config
        except FileNotFoundError:
            logger.error(f"✗ Config not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON: {e}")
            raise

    def create_asg(
        self,
        asg_name: str,
        launch_template_id: str,
        launch_template_version: str,
        target_group_arn: str,
        subnets: list,
        min_size: int = 1,
        max_size: int = 5,
        desired_capacity: int = 2,
        health_check_type: str = "ELB",
        health_check_grace_period: int = 300,
    ) -> str:
        """Create Auto Scaling Group."""
        try:
            logger.info(f"Creating Auto Scaling Group: {asg_name}...")

            self.autoscaling.create_auto_scaling_group(
                AutoScalingGroupName=asg_name,
                LaunchTemplate={
                    "LaunchTemplateId": launch_template_id,
                    "Version": launch_template_version,
                },
                MinSize=min_size,
                MaxSize=max_size,
                DesiredCapacity=desired_capacity,
                VPCZoneIdentifier=",".join(subnets),
                TargetGroupARNs=[target_group_arn],
                HealthCheckType=health_check_type,
                HealthCheckGracePeriod=health_check_grace_period,
                Tags=[
                    {
                        "Key": "Name",
                        "Value": asg_name,
                        "PropagateAtLaunch": True,
                    },
                    {
                        "Key": "Environment",
                        "Value": "experiment",
                        "PropagateAtLaunch": True,
                    },
                ],
            )

            logger.info(f"✓ Auto Scaling Group created: {asg_name}")
            return asg_name
        except ClientError as e:
            if e.response["Error"]["Code"] == "AlreadyExists":
                logger.warning(f"⚠ ASG already exists: {asg_name}")
                return asg_name
            logger.error(f"✗ Failed to create ASG: {e}")
            raise

    def create_cpu_scaling_policy(
        self, asg_name: str, target_cpu: float = 50.0
    ) -> None:
        """Create target tracking scaling policy for CPU."""
        try:
            logger.info(f"Creating CPU target tracking policy for {asg_name}...")

            policy_name = f"{asg_name}-cpu-policy"

            self.autoscaling.put_scaling_policy(
                AutoScalingGroupName=asg_name,
                PolicyName=policy_name,
                PolicyType="TargetTrackingScaling",
                TargetTrackingConfiguration={
                    "TargetValue": target_cpu,
                    "PredefinedMetricSpecification": {
                        "PredefinedMetricType": "ASGAverageCPUUtilization",
                    },
                    "ScaleOutCooldown": 60,  # 1 minute
                    "ScaleInCooldown": 300,  # 5 minutes
                },
            )

            logger.info(f"✓ CPU scaling policy created (target: {target_cpu}%)")
        except ClientError as e:
            logger.error(f"✗ Failed to create scaling policy: {e}")
            raise

    def create_custom_metric_scaling_policy(
        self,
        asg_name: str,
        metric_name: str,
        metric_namespace: str,
        target_value: float,
        scale_out_cooldown: int = 60,
        scale_in_cooldown: int = 300,
    ) -> None:
        """Create target tracking policy for custom metrics."""
        try:
            logger.info(
                f"Creating {metric_name} target tracking policy for {asg_name}..."
            )

            policy_name = f"{asg_name}-{metric_name.lower()}-policy"

            self.autoscaling.put_scaling_policy(
                AutoScalingGroupName=asg_name,
                PolicyName=policy_name,
                PolicyType="TargetTrackingScaling",
                TargetTrackingConfiguration={
                    "TargetValue": target_value,
                    "CustomizedMetricSpecification": {
                        "MetricName": metric_name,
                        "Namespace": metric_namespace,
                        "Statistic": "Average",
                        "Unit": "Count/Second"
                        if metric_name == "RequestRate"
                        else "None",
                    },
                    "ScaleOutCooldown": scale_out_cooldown,
                    "ScaleInCooldown": scale_in_cooldown,
                },
            )

            logger.info(
                f"✓ {metric_name} scaling policy created (target: {target_value})"
            )
        except ClientError as e:
            logger.error(f"✗ Failed to create scaling policy: {e}")
            raise

    def setup(
        self, network_config: Dict, launch_template_config: Dict, alb_config: Dict
    ) -> Dict[str, Any]:
        """Execute full ASG setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS Auto Scaling Groups Setup")
            logger.info("=" * 60)

            # Get configuration values
            private_subnet_1 = network_config["private_subnet_1_id"]
            private_subnet_2 = network_config["private_subnet_2_id"]
            subnets = [private_subnet_1, private_subnet_2]

            cpu_template_id = launch_template_config["cpu_template_id"]
            request_template_id = launch_template_config["request_template_id"]

            cpu_tg_arn = alb_config["cpu_target_group_arn"]
            request_tg_arn = alb_config["request_target_group_arn"]

            # Create CPU-based ASG
            logger.info("\n[1/4] Creating CPU-based Auto Scaling Group...")
            cpu_asg_name = self.create_asg(
                "asg-cpu",
                cpu_template_id,
                "$Latest",
                cpu_tg_arn,
                subnets,
                min_size=1,
                max_size=5,
                desired_capacity=2,
                health_check_type="ELB",
                health_check_grace_period=300,
            )
            self.config["cpu_asg_name"] = cpu_asg_name

            # Create request-rate-based ASG
            logger.info("\n[2/4] Creating request-rate-based Auto Scaling Group...")
            request_asg_name = self.create_asg(
                "asg-request",
                request_template_id,
                "$Latest",
                request_tg_arn,
                subnets,
                min_size=1,
                max_size=5,
                desired_capacity=2,
                health_check_type="ELB",
                health_check_grace_period=300,
            )
            self.config["request_asg_name"] = request_asg_name

            # Create scaling policies
            logger.info("\n[3/4] Creating CPU scaling policy...")
            self.create_cpu_scaling_policy(cpu_asg_name, target_cpu=50.0)

            logger.info("\n[4/4] Creating request-rate scaling policy...")
            self.create_custom_metric_scaling_policy(
                request_asg_name,
                metric_name="RequestRate",
                metric_namespace="AutoscaleExperiment",
                target_value=10.0,  # 10 requests/second per instance
                scale_out_cooldown=60,
                scale_in_cooldown=300,
            )

            logger.info("=" * 60)
            logger.info("Auto Scaling Groups Setup Complete!")
            logger.info("=" * 60)
            logger.info(f"\nConfiguration:\n{json.dumps(self.config, indent=2)}")
            logger.info("\n✓ Instances should be launching now...")
            logger.info("  Check EC2 console in 1-2 minutes for running instances")

            return self.config
        except Exception as e:
            logger.error(f"✗ Setup failed: {e}")
            raise

    def save_config(self, output_path: Path) -> None:
        """Save configuration to JSON file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✓ Configuration saved to: {output_path}")
        except IOError as e:
            logger.error(f"✗ Failed to save configuration: {e}")
            raise


def main():
    """Main entry point."""
    try:
        # Get project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        network_config_file = project_root / "infrastructure" / "network-config.json"
        launch_template_config_file = (
            project_root / "infrastructure" / "launch-templates-config.json"
        )
        alb_config_file = project_root / "infrastructure" / "alb-config.json"
        output_file = project_root / "infrastructure" / "asg-config.json"

        # Load dependencies
        setup = ASGSetup(region="us-east-1")
        network_config = setup.load_config(network_config_file)
        launch_template_config = setup.load_config(launch_template_config_file)
        alb_config = setup.load_config(alb_config_file)

        # Setup ASGs
        config = setup.setup(network_config, launch_template_config, alb_config)
        setup.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
