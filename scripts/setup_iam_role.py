#!/usr/bin/env python3
"""
Task 2: AWS IAM Role Setup
==========================

Creates IAM role and instance profile for EC2 instances running the autoscaling experiment.

Output:
  - infrastructure/iam-config.json

AWS Resources Created:
  - IAM Role: EC2RoleForExperiment
  - Instance Profile: EC2InstanceProfileForExperiment
  - Attached Policies:
    * CloudWatchAgentServerPolicy (CloudWatch access)
    * AmazonS3ReadOnlyAccess (S3 access)
    * AmazonSSMManagedInstanceCore (Systems Manager)
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


class IAMRoleSetup:
    """Manages IAM roles and policies for EC2 instances."""

    def __init__(self):
        """Initialize IAM client."""
        self.iam = boto3.client("iam")
        self.config: Dict[str, Any] = {}

    def create_role(self, role_name: str) -> str:
        """Create IAM role with EC2 assume policy."""
        try:
            logger.info(f"Creating IAM role: {role_name}...")

            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description="Role for EC2 instances running autoscaling experiments",
            )

            role_arn = response["Role"]["Arn"]
            logger.info(f"✓ IAM role created: {role_arn}")
            return role_arn
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                logger.warning(f"⚠ Role already exists: {role_name}")
                response = self.iam.get_role(RoleName=role_name)
                return response["Role"]["Arn"]
            logger.error(f"✗ Failed to create role: {e}")
            raise

    def attach_policy(self, role_name: str, policy_arn: str) -> None:
        """Attach AWS managed policy to role."""
        try:
            logger.info(f"Attaching policy to {role_name}...")
            self.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            logger.info(f"✓ Policy attached: {policy_arn}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                logger.warning(f"⚠ Policy or role not found")
            else:
                logger.error(f"✗ Failed to attach policy: {e}")
                raise

    def create_inline_policy(
        self, role_name: str, policy_name: str, policy_doc: Dict
    ) -> None:
        """Create and attach inline policy to role."""
        try:
            logger.info(f"Creating inline policy {policy_name} for {role_name}...")
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_doc),
            )
            logger.info(f"✓ Inline policy created: {policy_name}")
        except ClientError as e:
            logger.error(f"✗ Failed to create inline policy: {e}")
            raise

    def create_instance_profile(self, profile_name: str, role_name: str) -> str:
        """Create instance profile and add role."""
        try:
            logger.info(f"Creating instance profile: {profile_name}...")

            # Create instance profile
            try:
                response = self.iam.create_instance_profile(
                    InstanceProfileName=profile_name
                )
                profile_arn = response["InstanceProfile"]["Arn"]
                logger.info(f"✓ Instance profile created: {profile_arn}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityAlreadyExists":
                    logger.warning(f"⚠ Instance profile already exists: {profile_name}")
                    response = self.iam.get_instance_profile(
                        InstanceProfileName=profile_name
                    )
                    profile_arn = response["InstanceProfile"]["Arn"]
                else:
                    raise

            # Add role to instance profile
            try:
                self.iam.add_role_to_instance_profile(
                    InstanceProfileName=profile_name, RoleName=role_name
                )
                logger.info(f"✓ Role added to instance profile")
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code in ("EntityAlreadyExists", "LimitExceeded"):
                    logger.warning(f"⚠ Role already in instance profile")
                else:
                    raise

            return profile_arn
        except ClientError as e:
            logger.error(f"✗ Failed to create instance profile: {e}")
            raise

    def setup(self) -> Dict[str, Any]:
        """Execute full IAM setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS IAM Role Setup")
            logger.info("=" * 60)

            role_name = "EC2RoleForExperiment"
            profile_name = "EC2InstanceProfileForExperiment"

            # Create role
            role_arn = self.create_role(role_name)
            self.config["role_name"] = role_name
            self.config["role_arn"] = role_arn

            # Attach AWS managed policies
            logger.info("\nAttaching AWS managed policies...")

            # CloudWatch agent policy (for sending metrics)
            self.attach_policy(
                role_name, "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
            )

            # S3 read-only (for accessing data/config)
            self.attach_policy(
                role_name, "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
            )

            # Systems Manager core (for SSM Session Manager)
            self.attach_policy(
                role_name, "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
            )

            # Create inline policy for CloudWatch (custom metrics)
            logger.info("\nCreating inline CloudWatch policy...")
            cloudwatch_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudwatch:PutMetricData",
                            "cloudwatch:GetMetricStatistics",
                            "cloudwatch:ListMetrics",
                        ],
                        "Resource": "*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        "Resource": "arn:aws:logs:*:*:*",
                    },
                ],
            }
            self.create_inline_policy(role_name, "CloudWatchMetrics", cloudwatch_policy)

            # Create instance profile
            logger.info("\nCreating instance profile...")
            profile_arn = self.create_instance_profile(profile_name, role_name)
            self.config["instance_profile_name"] = profile_name
            self.config["instance_profile_arn"] = profile_arn

            logger.info("=" * 60)
            logger.info("IAM Role Setup Complete!")
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
        output_file = project_root / "infrastructure" / "iam-config.json"

        # Setup IAM
        iam_setup = IAMRoleSetup()
        config = iam_setup.setup()
        iam_setup.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
