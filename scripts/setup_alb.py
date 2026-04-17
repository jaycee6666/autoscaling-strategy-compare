#!/usr/bin/env python3
"""
Task 5: AWS Application Load Balancer (ALB) Setup
==================================================

Creates Application Load Balancer, target groups, and listeners.

Dependencies:
  - Requires network-config.json (VPC ID, subnet IDs)
  - Requires security-groups-config.json (ALB security group ID)

Output:
  - infrastructure/alb-config.json

AWS Resources Created:
  - Application Load Balancer (experiment-alb)
  - Target Group: tg-cpu-asg (for CPU strategy)
  - Target Group: tg-request-asg (for request-rate strategy)
  - Listener: Port 80 → Target Group
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ALBSetup:
    """Manages AWS Application Load Balancer."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize ELB client."""
        self.elbv2 = boto3.client("elbv2", region_name=region)
        self.ec2 = boto3.client("ec2", region_name=region)
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

    def create_alb(
        self, name: str, subnets: list, security_group_id: str, vpc_id: str
    ) -> str:
        """Create Application Load Balancer."""
        try:
            logger.info(f"Creating ALB: {name}...")

            response = self.elbv2.create_load_balancer(
                Name=name,
                Subnets=subnets,
                SecurityGroups=[security_group_id],
                Scheme="internet-facing",
                Type="application",
                IpAddressType="ipv4",
                Tags=[
                    {"Key": "Name", "Value": name},
                    {"Key": "Environment", "Value": "experiment"},
                ],
            )

            alb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
            alb_dns = response["LoadBalancers"][0]["DNSName"]

            logger.info(f"✓ ALB created: {alb_arn}")
            logger.info(f"  DNS: {alb_dns}")

            return alb_arn
        except ClientError as e:
            if e.response["Error"]["Code"] == "DuplicateLoadBalancerName":
                logger.warning(f"⚠ ALB already exists: {name}")
                response = self.elbv2.describe_load_balancers(Names=[name])
                if response["LoadBalancers"]:
                    return response["LoadBalancers"][0]["LoadBalancerArn"]
            logger.error(f"✗ Failed to create ALB: {e}")
            raise

    def create_target_group(
        self,
        name: str,
        vpc_id: str,
        protocol: str = "HTTP",
        port: int = 8080,
        health_check_path: str = "/health",
    ) -> str:
        """Create target group."""
        try:
            logger.info(f"Creating target group: {name}...")

            response = self.elbv2.create_target_group(
                Name=name,
                Protocol=protocol,
                Port=port,
                VpcId=vpc_id,
                TargetType="instance",
                HealthCheckEnabled=True,
                HealthCheckProtocol=protocol,
                HealthCheckPath=health_check_path,
                HealthCheckIntervalSeconds=30,
                HealthCheckTimeoutSeconds=5,
                HealthyThresholdCount=2,
                UnhealthyThresholdCount=3,
                Matcher={"HttpCode": "200"},
                Tags=[
                    {"Key": "Name", "Value": name},
                    {"Key": "Environment", "Value": "experiment"},
                ],
            )

            tg_arn = response["TargetGroups"][0]["TargetGroupArn"]
            logger.info(f"✓ Target group created: {tg_arn}")

            return tg_arn
        except ClientError as e:
            logger.error(f"✗ Failed to create target group: {e}")
            raise

    def create_listener(
        self,
        alb_arn: str,
        target_group_arn: str,
        port: int = 80,
        protocol: str = "HTTP",
    ) -> str:
        """Create ALB listener."""
        try:
            logger.info(f"Creating listener on port {port}...")

            response = self.elbv2.create_listener(
                LoadBalancerArn=alb_arn,
                Protocol=protocol,
                Port=port,
                DefaultActions=[
                    {
                        "Type": "forward",
                        "TargetGroupArn": target_group_arn,
                    }
                ],
            )

            listener_arn = response["Listeners"][0]["ListenerArn"]
            logger.info(f"✓ Listener created: {listener_arn}")

            return listener_arn
        except ClientError as e:
            if e.response["Error"]["Code"] == "DuplicateListener":
                logger.warning(f"⚠ Listener already exists on port {port}")
                # Get existing listener
                response = self.elbv2.describe_listeners(LoadBalancerArn=alb_arn)
                for listener in response["Listeners"]:
                    if listener["Port"] == port:
                        return listener["ListenerArn"]
            logger.error(f"✗ Failed to create listener: {e}")
            raise

    def get_alb_dns(self, alb_arn: str) -> str:
        """Get ALB DNS name."""
        try:
            response = self.elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])
            if response["LoadBalancers"]:
                return response["LoadBalancers"][0]["DNSName"]
            raise Exception("ALB not found")
        except ClientError as e:
            logger.error(f"✗ Failed to get ALB DNS: {e}")
            raise

    def setup(self, network_config: Dict, sg_config: Dict) -> Dict[str, Any]:
        """Execute full ALB setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS ALB Setup")
            logger.info("=" * 60)

            vpc_id = network_config["vpc_id"]
            public_subnet_1 = network_config["public_subnet_1_id"]
            public_subnet_2 = network_config["public_subnet_2_id"]
            alb_sg_id = sg_config["alb_sg_id"]

            # Create ALB
            logger.info("\n[1/5] Creating Application Load Balancer...")
            alb_arn = self.create_alb(
                "experiment-alb", [public_subnet_1, public_subnet_2], alb_sg_id, vpc_id
            )
            self.config["alb_arn"] = alb_arn
            self.config["alb_dns"] = self.get_alb_dns(alb_arn)

            # Create target groups
            logger.info("\n[2/5] Creating CPU strategy target group...")
            cpu_tg_arn = self.create_target_group(
                "tg-cpu-asg",
                vpc_id,
                protocol="HTTP",
                port=8080,
                health_check_path="/health",
            )
            self.config["cpu_target_group_arn"] = cpu_tg_arn

            logger.info("\n[3/5] Creating request-rate strategy target group...")
            request_tg_arn = self.create_target_group(
                "tg-request-asg",
                vpc_id,
                protocol="HTTP",
                port=8080,
                health_check_path="/health",
            )
            self.config["request_target_group_arn"] = request_tg_arn

            # Create listener (initially pointing to CPU target group)
            logger.info("\n[4/5] Creating listener...")
            listener_arn = self.create_listener(
                alb_arn, cpu_tg_arn, port=80, protocol="HTTP"
            )
            self.config["listener_arn"] = listener_arn

            logger.info("=" * 60)
            logger.info("ALB Setup Complete!")
            logger.info("=" * 60)
            logger.info(f"\nConfiguration:\n{json.dumps(self.config, indent=2)}")
            logger.info(f"\n✓ ALB DNS: {self.config['alb_dns']}")
            logger.info("  (Wait 1-2 minutes for health checks to pass)")

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
        sg_config_file = project_root / "infrastructure" / "security-groups-config.json"
        output_file = project_root / "infrastructure" / "alb-config.json"

        # Load dependencies
        setup = ALBSetup(region="us-east-1")
        network_config = setup.load_config(network_config_file)
        sg_config = setup.load_config(sg_config_file)

        # Setup ALB
        config = setup.setup(network_config, sg_config)
        setup.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
