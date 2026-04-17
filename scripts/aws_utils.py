#!/usr/bin/env python3
"""
Phase 0: AWS CLI Wrapper
Simplified interface for AWS CLI operations with error handling and logging.
Compatible with all platforms (Windows, macOS, Linux).
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AWSCommandError(Exception):
    """Raised when AWS CLI command fails."""

    pass


class AWSUtils:
    """Wrapper for AWS CLI operations."""

    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """
        Initialize AWS utilities.

        Args:
            region: AWS region (e.g., 'us-east-1')
            profile: AWS profile to use
        """
        self.region = region
        self.profile = profile
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

    def _build_command(self, *args: str) -> List[str]:
        """Build AWS CLI command with region and profile."""
        cmd = ["aws"]

        if self.profile:
            cmd.extend(["--profile", self.profile])

        if self.region:
            cmd.extend(["--region", self.region])

        cmd.extend(args)
        return cmd

    def _run_command(
        self, *args: str, check: bool = True, json_output: bool = False
    ) -> Tuple[int, str, str]:
        """
        Run an AWS CLI command.

        Args:
            *args: Command arguments
            check: Raise exception on non-zero exit
            json_output: Parse output as JSON

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            AWSCommandError: If command fails and check=True
        """
        cmd = self._build_command(*args)

        if json_output:
            cmd.append("--output")
            cmd.append("json")

        logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            stdout = result.stdout
            stderr = result.stderr

            if result.returncode != 0 and check:
                error_msg = stderr or stdout
                logger.error(f"Command failed: {error_msg}")
                raise AWSCommandError(f"AWS CLI error: {error_msg}")

            return result.returncode, stdout, stderr

        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            raise AWSCommandError("AWS CLI command timed out")
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise AWSCommandError(f"Failed to run AWS CLI: {e}")

    def run_raw(self, *args: str, **kwargs) -> Tuple[int, str, str]:
        """Run raw AWS CLI command."""
        return self._run_command(*args, **kwargs)

    # VPC Operations
    def create_vpc(self, cidr_block: str, name: str) -> Dict[str, Any]:
        """Create a VPC."""
        code, stdout, stderr = self._run_command(
            "ec2", "create-vpc", "--cidr-block", cidr_block, json_output=True
        )
        result = json.loads(stdout)
        vpc_id = result["Vpc"]["VpcId"]

        # Add Name tag
        self._run_command(
            "ec2",
            "create-tags",
            "--resources",
            vpc_id,
            "--tags",
            f"Key=Name,Value={name}",
        )

        logger.info(f"Created VPC: {vpc_id}")
        return result

    def describe_vpcs(self, filters: Optional[List[Dict]] = None) -> List[Dict]:
        """Describe VPCs."""
        cmd = ["ec2", "describe-vpcs"]

        if filters:
            filter_str = " ".join(
                [f"Name={f['Name']},Values={','.join(f['Values'])}" for f in filters]
            )
            cmd.extend(["--filters", filter_str])

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)
        return result.get("Vpcs", [])

    def delete_vpc(self, vpc_id: str):
        """Delete a VPC."""
        self._run_command("ec2", "delete-vpc", "--vpc-id", vpc_id)
        logger.info(f"Deleted VPC: {vpc_id}")

    # Subnet Operations
    def create_subnet(
        self,
        vpc_id: str,
        cidr_block: str,
        availability_zone: Optional[str] = None,
        name: str = "",
    ) -> Dict[str, Any]:
        """Create a subnet."""
        cmd = ["ec2", "create-subnet", "--vpc-id", vpc_id, "--cidr-block", cidr_block]

        if availability_zone:
            cmd.extend(["--availability-zone", availability_zone])

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)
        subnet_id = result["Subnet"]["SubnetId"]

        # Add Name tag
        if name:
            self._run_command(
                "ec2",
                "create-tags",
                "--resources",
                subnet_id,
                "--tags",
                f"Key=Name,Value={name}",
            )

        logger.info(f"Created Subnet: {subnet_id}")
        return result

    def describe_subnets(self, vpc_id: str) -> List[Dict]:
        """Describe subnets in a VPC."""
        code, stdout, stderr = self._run_command(
            "ec2",
            "describe-subnets",
            "--filters",
            f"Name=vpc-id,Values={vpc_id}",
            json_output=True,
        )
        result = json.loads(stdout)
        return result.get("Subnets", [])

    # Security Group Operations
    def create_security_group(
        self, group_name: str, description: str, vpc_id: str
    ) -> Dict[str, Any]:
        """Create a security group."""
        code, stdout, stderr = self._run_command(
            "ec2",
            "create-security-group",
            "--group-name",
            group_name,
            "--description",
            description,
            "--vpc-id",
            vpc_id,
            json_output=True,
        )
        result = json.loads(stdout)
        logger.info(f"Created Security Group: {result['GroupId']}")
        return result

    def authorize_security_group_ingress(
        self,
        group_id: str,
        protocol: str,
        from_port: int,
        to_port: int,
        cidr: Optional[str] = None,
        source_group: Optional[str] = None,
    ):
        """Authorize inbound traffic on security group."""
        cmd = [
            "ec2",
            "authorize-security-group-ingress",
            "--group-id",
            group_id,
            "--protocol",
            protocol,
            "--port",
            f"{from_port}-{to_port}",
        ]

        if cidr:
            cmd.extend(["--cidr", cidr])
        elif source_group:
            cmd.extend(["--source-group", source_group])

        self._run_command(*cmd)
        logger.info(
            f"Authorized ingress on {group_id}: {protocol} {from_port}-{to_port}"
        )

    def describe_security_groups(self, vpc_id: str) -> List[Dict]:
        """Describe security groups in a VPC."""
        code, stdout, stderr = self._run_command(
            "ec2",
            "describe-security-groups",
            "--filters",
            f"Name=vpc-id,Values={vpc_id}",
            json_output=True,
        )
        result = json.loads(stdout)
        return result.get("SecurityGroups", [])

    # EC2 Instance Operations
    def run_instances(
        self,
        image_id: str,
        instance_type: str,
        key_name: str,
        subnet_id: str,
        security_group_ids: List[str],
        min_count: int = 1,
        max_count: int = 1,
        name: str = "",
    ) -> Dict[str, Any]:
        """Launch EC2 instances."""
        cmd = [
            "ec2",
            "run-instances",
            "--image-id",
            image_id,
            "--instance-type",
            instance_type,
            "--key-name",
            key_name,
            "--subnet-id",
            subnet_id,
            "--security-group-ids",
            *security_group_ids,
            "--min-count",
            str(min_count),
            "--max-count",
            str(max_count),
        ]

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)

        # Add Name tag if provided
        if name and result.get("Instances"):
            instance_id = result["Instances"][0]["InstanceId"]
            self._run_command(
                "ec2",
                "create-tags",
                "--resources",
                instance_id,
                "--tags",
                f"Key=Name,Value={name}",
            )

        logger.info(f"Launched {len(result.get('Instances', []))} instance(s)")
        return result

    def describe_instances(self, filters: Optional[List[Dict]] = None) -> List[Dict]:
        """Describe EC2 instances."""
        cmd = ["ec2", "describe-instances"]

        if filters:
            filter_str = " ".join(
                [f"Name={f['Name']},Values={','.join(f['Values'])}" for f in filters]
            )
            cmd.extend(["--filters", filter_str])

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)

        instances = []
        for reservation in result.get("Reservations", []):
            instances.extend(reservation.get("Instances", []))
        return instances

    def terminate_instances(self, instance_ids: List[str]):
        """Terminate EC2 instances."""
        self._run_command("ec2", "terminate-instances", "--instance-ids", *instance_ids)
        logger.info(f"Terminated {len(instance_ids)} instance(s)")

    # Auto Scaling Group Operations
    def create_auto_scaling_group(
        self,
        group_name: str,
        launch_template_id: str,
        min_size: int,
        max_size: int,
        desired_capacity: int,
        vpc_zone_identifier: str,
    ) -> Dict[str, Any]:
        """Create an Auto Scaling Group."""
        cmd = [
            "autoscaling",
            "create-auto-scaling-group",
            "--auto-scaling-group-name",
            group_name,
            "--launch-template",
            f"LaunchTemplateId={launch_template_id}",
            "--min-size",
            str(min_size),
            "--max-size",
            str(max_size),
            "--desired-capacity",
            str(desired_capacity),
            "--vpc-zone-identifier",
            vpc_zone_identifier,
        ]

        self._run_command(*cmd)
        logger.info(f"Created ASG: {group_name}")
        return {"GroupName": group_name}

    def describe_auto_scaling_groups(
        self, group_names: Optional[List[str]] = None
    ) -> List[Dict]:
        """Describe Auto Scaling Groups."""
        cmd = ["autoscaling", "describe-auto-scaling-groups"]

        if group_names:
            cmd.extend(["--auto-scaling-group-names", *group_names])

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)
        return result.get("AutoScalingGroups", [])

    def delete_auto_scaling_group(self, group_name: str, force: bool = False):
        """Delete an Auto Scaling Group."""
        cmd = [
            "autoscaling",
            "delete-auto-scaling-group",
            "--auto-scaling-group-name",
            group_name,
        ]

        if force:
            cmd.append("--force-delete")

        self._run_command(*cmd)
        logger.info(f"Deleted ASG: {group_name}")

    # CloudWatch Metrics
    def get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: Dict[str, str],
        start_time: str,
        end_time: str,
        period: int,
        statistics: List[str],
    ) -> List[Dict]:
        """Get CloudWatch metric statistics."""
        dimensions_str = " ".join(
            [f"Name={k},Value={v}" for k, v in dimensions.items()]
        )
        statistics_str = " ".join(statistics)

        cmd = [
            "cloudwatch",
            "get-metric-statistics",
            "--namespace",
            namespace,
            "--metric-name",
            metric_name,
            "--dimensions",
            dimensions_str,
            "--start-time",
            start_time,
            "--end-time",
            end_time,
            "--period",
            str(period),
            "--statistics",
            statistics_str,
        ]

        code, stdout, stderr = self._run_command(*cmd, json_output=True)
        result = json.loads(stdout)
        return result.get("Datapoints", [])

    def put_metric_alarm(
        self,
        alarm_name: str,
        metric_name: str,
        namespace: str,
        statistic: str,
        period: int,
        threshold: float,
        comparison_operator: str,
        evaluation_periods: int,
    ):
        """Create a CloudWatch alarm."""
        cmd = [
            "cloudwatch",
            "put-metric-alarm",
            "--alarm-name",
            alarm_name,
            "--metric-name",
            metric_name,
            "--namespace",
            namespace,
            "--statistic",
            statistic,
            "--period",
            str(period),
            "--threshold",
            str(threshold),
            "--comparison-operator",
            comparison_operator,
            "--evaluation-periods",
            str(evaluation_periods),
        ]

        self._run_command(*cmd)
        logger.info(f"Created alarm: {alarm_name}")


def main():
    """Test AWS utilities."""
    aws = AWSUtils(region="us-east-1")

    try:
        # Test by describing VPCs
        vpcs = aws.describe_vpcs()
        print(f"Found {len(vpcs)} VPC(s)")
        for vpc in vpcs:
            print(f"  - {vpc['VpcId']}: {vpc['CidrBlock']}")
    except AWSCommandError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
