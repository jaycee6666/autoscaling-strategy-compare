#!/usr/bin/env python3
"""
Task 3: AWS Security Groups Setup
==================================

Creates security groups for ALB and EC2 instances.

Dependencies:
  - Requires network-config.json (VPC ID)

Output:
  - infrastructure/security-groups-config.json

AWS Resources Created:
  - ALB Security Group (alb-sg)
    * Inbound: HTTP 80, HTTPS 443
    * Outbound: To app-sg on port 8080

  - App Security Group (app-sg)
    * Inbound: Port 8080 from ALB, Port 22 for SSH
    * Outbound: All traffic
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


class SecurityGroupsSetup:
    """Manages AWS Security Groups."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize EC2 client."""
        self.ec2 = boto3.client("ec2", region_name=region)
        self.config: Dict[str, Any] = {}

    def load_network_config(self, config_path: Path) -> Dict[str, str]:
        """Load network configuration from previous task."""
        try:
            logger.info(f"Loading network configuration from {config_path}...")
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info("✓ Network configuration loaded")
            return config
        except FileNotFoundError:
            logger.error(f"✗ Network config not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON in config: {e}")
            raise

    def create_security_group(
        self, vpc_id: str, group_name: str, description: str
    ) -> str:
        """Create a security group."""
        try:
            logger.info(f"Creating security group: {group_name}...")
            response = self.ec2.create_security_group(
                GroupName=group_name, Description=description, VpcId=vpc_id
            )
            sg_id = response["GroupId"]

            # Tag it
            self.ec2.create_tags(
                Resources=[sg_id],
                Tags=[
                    {"Key": "Name", "Value": group_name},
                    {"Key": "Environment", "Value": "experiment"},
                ],
            )

            logger.info(f"✓ Security group created: {sg_id}")
            return sg_id
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidGroup.Duplicate":
                logger.warning(f"⚠ Security group already exists: {group_name}")
                # Retrieve the existing group
                response = self.ec2.describe_security_groups(
                    Filters=[
                        {"Name": "group-name", "Values": [group_name]},
                        {"Name": "vpc-id", "Values": [vpc_id]},
                    ]
                )
                if response["SecurityGroups"]:
                    return response["SecurityGroups"][0]["GroupId"]
            logger.error(f"✗ Failed to create security group: {e}")
            raise

    def add_inbound_rule(
        self,
        sg_id: str,
        protocol: str,
        from_port: int,
        to_port: int,
        cidr_ip: Optional[str] = None,
        source_sg_id: Optional[str] = None,
    ) -> None:
        """Add inbound rule to security group."""
        try:
            kwargs = {
                "GroupId": sg_id,
                "IpProtocol": protocol,
                "FromPort": from_port,
                "ToPort": to_port,
            }

            if cidr_ip:
                kwargs["CidrIp"] = cidr_ip
                logger.info(
                    f"  Adding inbound rule: {protocol} {from_port} from {cidr_ip}"
                )
            elif source_sg_id:
                kwargs["SourceSecurityGroupId"] = source_sg_id
                logger.info(
                    f"  Adding inbound rule: {protocol} {from_port} from SG {source_sg_id}"
                )

            self.ec2.authorize_security_group_ingress(**kwargs)
            logger.info(f"  ✓ Inbound rule added")
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidPermission.Duplicate":
                logger.warning(f"  ⚠ Rule already exists")
            else:
                logger.error(f"  ✗ Failed to add inbound rule: {e}")
                raise

    def add_outbound_rule(
        self,
        sg_id: str,
        protocol: str,
        from_port: int,
        to_port: int,
        cidr_ip: Optional[str] = None,
        dest_sg_id: Optional[str] = None,
    ) -> None:
        """Add outbound rule to security group."""
        try:
            kwargs = {
                "GroupId": sg_id,
                "IpProtocol": protocol,
                "FromPort": from_port,
                "ToPort": to_port,
            }

            if cidr_ip:
                kwargs["CidrIp"] = cidr_ip
                logger.info(
                    f"  Adding outbound rule: {protocol} {from_port} to {cidr_ip}"
                )
            elif dest_sg_id:
                kwargs["DestinationSecurityGroupId"] = dest_sg_id
                logger.info(
                    f"  Adding outbound rule: {protocol} {from_port} to SG {dest_sg_id}"
                )

            self.ec2.authorize_security_group_egress(**kwargs)
            logger.info(f"  ✓ Outbound rule added")
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidPermission.Duplicate":
                logger.warning(f"  ⚠ Rule already exists")
            else:
                logger.error(f"  ✗ Failed to add outbound rule: {e}")
                raise

    def setup(self, network_config: Dict[str, str]) -> Dict[str, Any]:
        """Execute full security groups setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS Security Groups Setup")
            logger.info("=" * 60)

            vpc_id = network_config["vpc_id"]

            # Create ALB security group
            logger.info("\n[1/2] Creating ALB Security Group...")
            alb_sg_id = self.create_security_group(
                vpc_id, "alb-sg", "Security group for Application Load Balancer"
            )
            self.config["alb_sg_id"] = alb_sg_id

            # ALB inbound rules
            self.add_inbound_rule(alb_sg_id, "tcp", 80, 80, cidr_ip="0.0.0.0/0")
            self.add_inbound_rule(alb_sg_id, "tcp", 443, 443, cidr_ip="0.0.0.0/0")

            # Create App security group
            logger.info("\n[2/2] Creating App Security Group...")
            app_sg_id = self.create_security_group(
                vpc_id, "app-sg", "Security group for EC2 application instances"
            )
            self.config["app_sg_id"] = app_sg_id

            # App inbound rules
            # Allow from ALB on port 8080
            self.add_inbound_rule(app_sg_id, "tcp", 8080, 8080, source_sg_id=alb_sg_id)

            # Allow SSH (you'll need to restrict this to your IP in production)
            # For now, allowing from 0.0.0.0/0 - CHANGE THIS IN PRODUCTION
            logger.warning(
                "⚠ SSH rule allows from 0.0.0.0/0 - restrict to your IP in production"
            )
            self.add_inbound_rule(app_sg_id, "tcp", 22, 22, cidr_ip="0.0.0.0/0")

            # App outbound rules - allow all (default is set, but being explicit)
            # Allow HTTPS for package downloads, CloudWatch, etc.
            self.add_outbound_rule(app_sg_id, "tcp", 443, 443, cidr_ip="0.0.0.0/0")
            # Allow HTTP for package downloads
            self.add_outbound_rule(app_sg_id, "tcp", 80, 80, cidr_ip="0.0.0.0/0")

            # ALB outbound rule - to app SG
            self.add_outbound_rule(alb_sg_id, "tcp", 8080, 8080, dest_sg_id=app_sg_id)

            logger.info("=" * 60)
            logger.info("Security Groups Setup Complete!")
            logger.info("=" * 60)
            logger.info(f"\nConfiguration:\n{json.dumps(self.config, indent=2)}")

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
        output_file = project_root / "infrastructure" / "security-groups-config.json"

        # Load network config
        setup = SecurityGroupsSetup(region="us-east-1")
        network_config = setup.load_network_config(network_config_file)

        # Setup security groups
        config = setup.setup(network_config)
        setup.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
