#!/usr/bin/env python3
"""
Task 1: AWS Network Infrastructure Setup
=========================================

Creates VPC, subnets, Internet Gateway, and route tables.

Output:
  - infrastructure/network-config.json

AWS Resources Created:
  - VPC (10.0.0.0/16)
  - Public Subnets (10.0.1.0/24, 10.0.2.0/24)
  - Private Subnets (10.0.11.0/24, 10.0.12.0/24)
  - Internet Gateway (IGW)
  - Route Tables (public and private)
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


class NetworkInfrastructure:
    """Manages AWS VPC and networking resources."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS EC2 client."""
        self.ec2 = boto3.client("ec2", region_name=region)
        self.region = region
        self.config: Dict[str, Any] = {}

    def create_vpc(self) -> str:
        """Create VPC with CIDR 10.0.0.0/16, or reuse existing if at limit."""
        try:
            # First, try to find an existing experiment VPC
            existing_vpcs = self.ec2.describe_vpcs(
                Filters=[
                    {"Name": "tag:Environment", "Values": ["experiment"]},
                    {"Name": "cidr", "Values": ["10.0.0.0/16"]},
                ]
            )

            if existing_vpcs.get("Vpcs"):
                vpc_id = existing_vpcs["Vpcs"][0]["VpcId"]
                logger.warning(f"⚠ Found existing VPC: {vpc_id}, reusing it")
                return vpc_id

            logger.info("Creating VPC (10.0.0.0/16)...")
            response = self.ec2.create_vpc(CidrBlock="10.0.0.0/16")
            vpc_id = response["Vpc"]["VpcId"]

            # Tag the VPC
            self.ec2.create_tags(
                Resources=[vpc_id],
                Tags=[
                    {"Key": "Name", "Value": "autoscaling-experiment-vpc"},
                    {"Key": "Environment", "Value": "experiment"},
                ],
            )

            logger.info(f"✓ VPC created: {vpc_id}")
            return vpc_id
        except ClientError as e:
            if "VpcLimitExceeded" in str(e):
                # Try to reuse any existing experiment VPC
                logger.warning("⚠ VPC limit reached, trying to reuse existing VPC...")
                existing_vpcs = self.ec2.describe_vpcs(
                    Filters=[{"Name": "tag:Environment", "Values": ["experiment"]}]
                )
                if existing_vpcs.get("Vpcs"):
                    vpc_id = existing_vpcs["Vpcs"][0]["VpcId"]
                    logger.info(f"✓ Reusing existing VPC: {vpc_id}")
                    return vpc_id
                logger.error("No existing experiment VPC found to reuse")
            logger.error(f"✗ Failed to create VPC: {e}")
            raise

    def create_public_subnet(self, vpc_id: str, cidr: str, az_index: int) -> str:
        """Create a public subnet or reuse existing."""
        try:
            # Try to find existing subnet with same CIDR
            existing_subnets = self.ec2.describe_subnets(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "cidr-block", "Values": [cidr]},
                ]
            )

            if existing_subnets.get("Subnets"):
                subnet_id = existing_subnets["Subnets"][0]["SubnetId"]
                logger.warning(
                    f"⚠ Found existing public subnet: {subnet_id}, reusing it"
                )
                return subnet_id

            logger.info(f"Creating public subnet ({cidr})...")

            # Get availability zones
            azs = self.ec2.describe_availability_zones()["AvailabilityZones"]
            az = azs[az_index % len(azs)]["ZoneName"]

            response = self.ec2.create_subnet(
                VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az
            )
            subnet_id = response["Subnet"]["SubnetId"]

            # Tag the subnet
            self.ec2.create_tags(
                Resources=[subnet_id],
                Tags=[
                    {"Key": "Name", "Value": f"public-subnet-{az_index + 1}"},
                    {"Key": "Type", "Value": "Public"},
                ],
            )

            # Enable public IP assignment
            self.ec2.modify_subnet_attribute(
                SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": True}
            )

            logger.info(f"✓ Public subnet created: {subnet_id} in {az}")
            return subnet_id
        except ClientError as e:
            logger.error(f"✗ Failed to create public subnet: {e}")
            raise

    def create_private_subnet(self, vpc_id: str, cidr: str, az_index: int) -> str:
        """Create a private subnet or reuse existing."""
        try:
            # Try to find existing subnet with same CIDR
            existing_subnets = self.ec2.describe_subnets(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "cidr-block", "Values": [cidr]},
                ]
            )

            if existing_subnets.get("Subnets"):
                subnet_id = existing_subnets["Subnets"][0]["SubnetId"]
                logger.warning(
                    f"⚠ Found existing private subnet: {subnet_id}, reusing it"
                )
                return subnet_id

            logger.info(f"Creating private subnet ({cidr})...")

            # Get availability zones
            azs = self.ec2.describe_availability_zones()["AvailabilityZones"]
            az = azs[az_index % len(azs)]["ZoneName"]

            response = self.ec2.create_subnet(
                VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az
            )
            subnet_id = response["Subnet"]["SubnetId"]

            # Tag the subnet
            self.ec2.create_tags(
                Resources=[subnet_id],
                Tags=[
                    {"Key": "Name", "Value": f"private-subnet-{az_index + 1}"},
                    {"Key": "Type", "Value": "Private"},
                ],
            )

            logger.info(f"✓ Private subnet created: {subnet_id} in {az}")
            return subnet_id
        except ClientError as e:
            logger.error(f"✗ Failed to create private subnet: {e}")
            raise

    def create_internet_gateway(self, vpc_id: str) -> str:
        """Create and attach Internet Gateway or reuse existing."""
        try:
            # Try to find existing IGW attached to VPC
            existing_igws = self.ec2.describe_internet_gateways(
                Filters=[
                    {"Name": "attachment.vpc-id", "Values": [vpc_id]},
                    {"Name": "tag:Environment", "Values": ["experiment"]},
                ]
            )

            if existing_igws.get("InternetGateways"):
                igw_id = existing_igws["InternetGateways"][0]["InternetGatewayId"]
                logger.warning(f"⚠ Found existing IGW: {igw_id}, reusing it")
                return igw_id

            logger.info("Creating Internet Gateway...")

            # Create IGW
            response = self.ec2.create_internet_gateway()
            igw_id = response["InternetGateway"]["InternetGatewayId"]

            # Tag the IGW
            self.ec2.create_tags(
                Resources=[igw_id],
                Tags=[
                    {"Key": "Name", "Value": "experiment-igw"},
                    {"Key": "Environment", "Value": "experiment"},
                ],
            )

            # Attach to VPC
            self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            logger.info(f"✓ Internet Gateway created and attached: {igw_id}")
            return igw_id
        except ClientError as e:
            logger.error(f"✗ Failed to create Internet Gateway: {e}")
            raise

    def create_route_tables(
        self, vpc_id: str, igw_id: str, public_subnets: list, private_subnets: list
    ) -> tuple:
        """Create and configure public and private route tables, or reuse existing."""
        try:
            # Try to find existing route tables
            public_rt_id = None
            private_rt_id = None

            existing_rts = self.ec2.describe_route_tables(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "tag:Type", "Values": ["Public"]},
                ]
            )
            if existing_rts.get("RouteTables"):
                public_rt_id = existing_rts["RouteTables"][0]["RouteTableId"]
                logger.warning(
                    f"⚠ Found existing public route table: {public_rt_id}, reusing it"
                )

            existing_rts = self.ec2.describe_route_tables(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "tag:Type", "Values": ["Private"]},
                ]
            )
            if existing_rts.get("RouteTables"):
                private_rt_id = existing_rts["RouteTables"][0]["RouteTableId"]
                logger.warning(
                    f"⚠ Found existing private route table: {private_rt_id}, reusing it"
                )

            # Create public route table if needed
            if not public_rt_id:
                logger.info("Creating public route table...")
                public_rt_response = self.ec2.create_route_table(VpcId=vpc_id)
                public_rt_id = public_rt_response["RouteTable"]["RouteTableId"]

                # Tag it
                self.ec2.create_tags(
                    Resources=[public_rt_id],
                    Tags=[
                        {"Key": "Name", "Value": "public-route-table"},
                        {"Key": "Type", "Value": "Public"},
                    ],
                )

                # Add route to IGW (0.0.0.0/0 -> IGW)
                self.ec2.create_route(
                    RouteTableId=public_rt_id,
                    DestinationCidrBlock="0.0.0.0/0",
                    GatewayId=igw_id,
                )
                logger.info(f"✓ Public route table created: {public_rt_id}")

                # Associate public subnets
                for i, subnet_id in enumerate(public_subnets):
                    try:
                        self.ec2.associate_route_table(
                            RouteTableId=public_rt_id, SubnetId=subnet_id
                        )
                        logger.info(f"✓ Associated public subnet {i + 1}: {subnet_id}")
                    except ClientError as e:
                        if "Resource.AlreadyAssociated" not in str(e):
                            raise
                        logger.warning(f"⚠ Subnet {subnet_id} already associated")

            # Create private route table if needed
            if not private_rt_id:
                logger.info("Creating private route table...")
                private_rt_response = self.ec2.create_route_table(VpcId=vpc_id)
                private_rt_id = private_rt_response["RouteTable"]["RouteTableId"]

                # Tag it
                self.ec2.create_tags(
                    Resources=[private_rt_id],
                    Tags=[
                        {"Key": "Name", "Value": "private-route-table"},
                        {"Key": "Type", "Value": "Private"},
                    ],
                )
                logger.info(f"✓ Private route table created: {private_rt_id}")

                # Associate private subnets
                for i, subnet_id in enumerate(private_subnets):
                    try:
                        self.ec2.associate_route_table(
                            RouteTableId=private_rt_id, SubnetId=subnet_id
                        )
                        logger.info(f"✓ Associated private subnet {i + 1}: {subnet_id}")
                    except ClientError as e:
                        if "Resource.AlreadyAssociated" not in str(e):
                            raise
                        logger.warning(f"⚠ Subnet {subnet_id} already associated")

            return public_rt_id, private_rt_id
        except ClientError as e:
            logger.error(f"✗ Failed to create route tables: {e}")
            raise

    def setup(self) -> Dict[str, str]:
        """Execute full network setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS Network Infrastructure Setup")
            logger.info("=" * 60)

            # Create VPC
            vpc_id = self.create_vpc()
            self.config["vpc_id"] = vpc_id

            # Create public subnets
            public_subnet_1 = self.create_public_subnet(vpc_id, "10.0.1.0/24", 0)
            public_subnet_2 = self.create_public_subnet(vpc_id, "10.0.2.0/24", 1)
            self.config["public_subnet_1_id"] = public_subnet_1
            self.config["public_subnet_2_id"] = public_subnet_2

            # Create private subnets
            private_subnet_1 = self.create_private_subnet(vpc_id, "10.0.11.0/24", 0)
            private_subnet_2 = self.create_private_subnet(vpc_id, "10.0.12.0/24", 1)
            self.config["private_subnet_1_id"] = private_subnet_1
            self.config["private_subnet_2_id"] = private_subnet_2

            # Create Internet Gateway
            igw_id = self.create_internet_gateway(vpc_id)
            self.config["internet_gateway_id"] = igw_id

            # Create route tables
            public_rt_id, private_rt_id = self.create_route_tables(
                vpc_id,
                igw_id,
                [public_subnet_1, public_subnet_2],
                [private_subnet_1, private_subnet_2],
            )
            self.config["route_table_public_id"] = public_rt_id
            self.config["route_table_private_id"] = private_rt_id

            logger.info("=" * 60)
            logger.info("Network Infrastructure Setup Complete!")
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
        output_file = project_root / "infrastructure" / "network-config.json"

        # Setup network infrastructure
        network = NetworkInfrastructure(region="us-east-1")
        config = network.setup()
        network.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
