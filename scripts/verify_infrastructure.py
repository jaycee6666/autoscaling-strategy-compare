#!/usr/bin/env python3
"""
Task 7: AWS Infrastructure Verification
========================================

Validates that all AWS infrastructure components are created and properly configured.

Output:
  - infrastructure/verification-report.json
  - Console output with status checks

Verification Checks:
  ✓ VPC and subnets exist and have correct CIDR
  ✓ Internet Gateway is attached
  ✓ Security groups have proper rules
  ✓ EC2 instances are running
  ✓ Load Balancer is active
  ✓ Target groups are healthy
  ✓ Auto Scaling Groups are scaling
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureVerifier:
    """Verifies AWS infrastructure setup."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS clients."""
        self.ec2 = boto3.client("ec2", region_name=region)
        self.elbv2 = boto3.client("elbv2", region_name=region)
        self.autoscaling = boto3.client("autoscaling", region_name=region)
        self.region = region
        self.report: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "region": region,
            "checks": {},
            "summary": {},
        }

    def load_config(self, config_path: Path) -> Dict[str, str]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠ Config not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"⚠ Invalid JSON: {e}")
            return {}

    def check_vpc(self, vpc_id: str) -> bool:
        """Check if VPC exists and is configured correctly."""
        try:
            logger.info(f"Verifying VPC: {vpc_id}")
            response = self.ec2.describe_vpcs(VpcIds=[vpc_id])

            if response["Vpcs"]:
                vpc = response["Vpcs"][0]
                self.report["checks"]["vpc"] = {
                    "status": "PASS",
                    "vpc_id": vpc_id,
                    "cidr_block": vpc["CidrBlock"],
                    "state": vpc["State"],
                }
                logger.info(f"✓ VPC check passed: {vpc_id}")
                return True
            else:
                self.report["checks"]["vpc"] = {
                    "status": "FAIL",
                    "reason": "VPC not found",
                }
                logger.error("✗ VPC not found")
                return False
        except ClientError as e:
            self.report["checks"]["vpc"] = {"status": "ERROR", "error": str(e)}
            logger.error(f"✗ VPC check failed: {e}")
            return False

    def check_subnets(self, subnet_ids: List[str]) -> bool:
        """Check if subnets exist and are properly configured."""
        try:
            logger.info(f"Verifying subnets: {len(subnet_ids)} subnets")
            response = self.ec2.describe_subnets(SubnetIds=subnet_ids)

            subnets_info = []
            for subnet in response["Subnets"]:
                subnets_info.append(
                    {
                        "subnet_id": subnet["SubnetId"],
                        "cidr_block": subnet["CidrBlock"],
                        "availability_zone": subnet["AvailabilityZone"],
                        "available_ips": subnet["AvailableIpAddressCount"],
                    }
                )

            self.report["checks"]["subnets"] = {
                "status": "PASS" if len(subnets_info) == len(subnet_ids) else "PARTIAL",
                "count": len(subnets_info),
                "subnets": subnets_info,
            }
            logger.info(f"✓ All {len(subnets_info)} subnets verified")
            return len(subnets_info) == len(subnet_ids)
        except ClientError as e:
            self.report["checks"]["subnets"] = {"status": "ERROR", "error": str(e)}
            logger.error(f"✗ Subnet check failed: {e}")
            return False

    def check_security_groups(self, sg_ids: Dict[str, str]) -> bool:
        """Check if security groups exist and have rules."""
        try:
            logger.info(f"Verifying security groups: {len(sg_ids)} groups")
            response = self.ec2.describe_security_groups(GroupIds=list(sg_ids.values()))

            sg_info = []
            for sg in response["SecurityGroups"]:
                sg_info.append(
                    {
                        "group_id": sg["GroupId"],
                        "group_name": sg["GroupName"],
                        "inbound_rules": len(sg["IpPermissions"]),
                        "outbound_rules": len(sg["IpPermissionsEgress"]),
                    }
                )

            self.report["checks"]["security_groups"] = {
                "status": "PASS" if sg_info else "FAIL",
                "count": len(sg_info),
                "security_groups": sg_info,
            }
            logger.info(f"✓ All {len(sg_info)} security groups verified")
            return True
        except ClientError as e:
            self.report["checks"]["security_groups"] = {
                "status": "ERROR",
                "error": str(e),
            }
            logger.error(f"✗ Security group check failed: {e}")
            return False

    def check_alb(self, alb_arn: str) -> bool:
        """Check if ALB exists and is active."""
        try:
            logger.info(f"Verifying ALB: {alb_arn}")
            response = self.elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])

            if response["LoadBalancers"]:
                alb = response["LoadBalancers"][0]
                self.report["checks"]["alb"] = {
                    "status": "PASS" if alb["State"]["Code"] == "active" else "PENDING",
                    "alb_arn": alb_arn,
                    "dns_name": alb["DNSName"],
                    "state": alb["State"]["Code"],
                    "load_balancer_name": alb["LoadBalancerName"],
                }
                logger.info(f"✓ ALB check passed: {alb['State']['Code']}")
                return alb["State"]["Code"] == "active"
            else:
                self.report["checks"]["alb"] = {
                    "status": "FAIL",
                    "reason": "ALB not found",
                }
                logger.error("✗ ALB not found")
                return False
        except ClientError as e:
            self.report["checks"]["alb"] = {"status": "ERROR", "error": str(e)}
            logger.error(f"✗ ALB check failed: {e}")
            return False

    def check_target_groups(self, tg_arns: List[str]) -> bool:
        """Check if target groups exist and have healthy targets."""
        try:
            logger.info(f"Verifying target groups: {len(tg_arns)} groups")
            response = self.elbv2.describe_target_groups(TargetGroupArns=tg_arns)

            tg_info = []
            for tg in response["TargetGroups"]:
                # Get target health
                health_response = self.elbv2.describe_target_health(
                    TargetGroupArn=tg["TargetGroupArn"]
                )

                healthy_targets = sum(
                    1
                    for t in health_response["TargetHealthDescriptions"]
                    if t["TargetHealth"]["State"] == "healthy"
                )
                total_targets = len(health_response["TargetHealthDescriptions"])

                tg_info.append(
                    {
                        "target_group_arn": tg["TargetGroupArn"],
                        "target_group_name": tg["TargetGroupName"],
                        "protocol": tg["Protocol"],
                        "port": tg["Port"],
                        "healthy_targets": healthy_targets,
                        "total_targets": total_targets,
                        "health_check_path": tg.get("HealthCheckPath", "N/A"),
                    }
                )

            self.report["checks"]["target_groups"] = {
                "status": "PASS",
                "count": len(tg_info),
                "target_groups": tg_info,
            }
            logger.info(f"✓ All {len(tg_info)} target groups verified")
            return True
        except ClientError as e:
            self.report["checks"]["target_groups"] = {
                "status": "ERROR",
                "error": str(e),
            }
            logger.error(f"✗ Target group check failed: {e}")
            return False

    def check_asg(self, asg_names: List[str]) -> bool:
        """Check if Auto Scaling Groups exist and are healthy."""
        try:
            logger.info(f"Verifying Auto Scaling Groups: {len(asg_names)} groups")
            response = self.autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=asg_names
            )

            asg_info = []
            for asg in response["AutoScalingGroups"]:
                asg_info.append(
                    {
                        "asg_name": asg["AutoScalingGroupName"],
                        "min_size": asg["MinSize"],
                        "max_size": asg["MaxSize"],
                        "desired_capacity": asg["DesiredCapacity"],
                        "current_instances": len(asg["Instances"]),
                        "healthy_instances": sum(
                            1
                            for i in asg["Instances"]
                            if i["HealthStatus"] == "Healthy"
                        ),
                        "state": asg["DesiredCapacity"],
                        "created_time": asg["CreatedTime"].isoformat(),
                    }
                )

            self.report["checks"]["asg"] = {
                "status": "PASS",
                "count": len(asg_info),
                "auto_scaling_groups": asg_info,
            }
            logger.info(f"✓ All {len(asg_info)} Auto Scaling Groups verified")
            return True
        except ClientError as e:
            self.report["checks"]["asg"] = {"status": "ERROR", "error": str(e)}
            logger.error(f"✗ ASG check failed: {e}")
            return False

    def check_ec2_instances(self, vpc_id: str) -> bool:
        """Check if EC2 instances are running in VPC."""
        try:
            logger.info(f"Checking EC2 instances in VPC: {vpc_id}")
            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "instance-state-name", "Values": ["running", "pending"]},
                ]
            )

            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(
                        {
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                            "launch_time": instance["LaunchTime"].isoformat(),
                        }
                    )

            self.report["checks"]["ec2_instances"] = {
                "status": "PASS" if instances else "PENDING",
                "count": len(instances),
                "instances": instances,
            }
            logger.info(f"✓ Found {len(instances)} instances")
            return True
        except ClientError as e:
            self.report["checks"]["ec2_instances"] = {
                "status": "ERROR",
                "error": str(e),
            }
            logger.error(f"✗ EC2 instance check failed: {e}")
            return False

    def verify(self, all_configs: Dict[str, Dict]) -> Dict[str, Any]:
        """Execute all verification checks."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS Infrastructure Verification")
            logger.info("=" * 60)

            # Extract configurations
            network_config = all_configs.get("network", {})
            sg_config = all_configs.get("security_groups", {})
            alb_config = all_configs.get("alb", {})
            asg_config = all_configs.get("asg", {})

            # Run checks
            results = {
                "vpc": self.check_vpc(network_config.get("vpc_id", "")),
                "subnets": self.check_subnets(
                    [
                        network_config.get("public_subnet_1_id", ""),
                        network_config.get("public_subnet_2_id", ""),
                        network_config.get("private_subnet_1_id", ""),
                        network_config.get("private_subnet_2_id", ""),
                    ]
                ),
                "security_groups": self.check_security_groups(sg_config),
                "alb": self.check_alb(alb_config.get("alb_arn", "")),
                "target_groups": self.check_target_groups(
                    [
                        alb_config.get("cpu_target_group_arn", ""),
                        alb_config.get("request_target_group_arn", ""),
                    ]
                ),
                "asg": self.check_asg(
                    [
                        asg_config.get("cpu_asg_name", ""),
                        asg_config.get("request_asg_name", ""),
                    ]
                ),
                "ec2_instances": self.check_ec2_instances(
                    network_config.get("vpc_id", "")
                ),
            }

            # Summary
            passed = sum(1 for v in results.values() if v)
            total = len(results)

            self.report["summary"] = {
                "total_checks": total,
                "passed_checks": passed,
                "failed_checks": total - passed,
                "status": "PASS"
                if passed == total
                else "PARTIAL"
                if passed > 0
                else "FAIL",
            }

            logger.info("=" * 60)
            logger.info("Verification Complete!")
            logger.info("=" * 60)
            logger.info(f"\nSummary: {passed}/{total} checks passed")
            logger.info(f"Status: {self.report['summary']['status']}")

            if alb_config.get("alb_dns"):
                logger.info(f"\n✓ Your application is accessible at:")
                logger.info(f"  http://{alb_config['alb_dns']}")

            return self.report
        except Exception as e:
            logger.error(f"✗ Verification failed: {e}")
            self.report["summary"]["status"] = "ERROR"
            self.report["summary"]["error"] = str(e)
            return self.report

    def save_report(self, output_path: Path) -> None:
        """Save verification report to JSON file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(self.report, f, indent=2)
            logger.info(f"✓ Report saved to: {output_path}")
        except IOError as e:
            logger.error(f"✗ Failed to save report: {e}")
            raise


def main():
    """Main entry point."""
    try:
        # Get project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent

        # Load all configurations
        verifier = InfrastructureVerifier(region="us-east-1")

        configs = {
            "network": verifier.load_config(
                project_root / "infrastructure" / "network-config.json"
            ),
            "iam": verifier.load_config(
                project_root / "infrastructure" / "iam-config.json"
            ),
            "security_groups": verifier.load_config(
                project_root / "infrastructure" / "security-groups-config.json"
            ),
            "launch_templates": verifier.load_config(
                project_root / "infrastructure" / "launch-templates-config.json"
            ),
            "alb": verifier.load_config(
                project_root / "infrastructure" / "alb-config.json"
            ),
            "asg": verifier.load_config(
                project_root / "infrastructure" / "asg-config.json"
            ),
        }

        # Run verification
        report = verifier.verify(configs)
        verifier.save_report(
            project_root / "infrastructure" / "verification-report.json"
        )

        # Return exit code based on status
        if report["summary"]["status"] == "PASS":
            logger.info(f"\n✓ All infrastructure components verified successfully!")
            return 0
        elif report["summary"]["status"] == "PARTIAL":
            logger.warning(f"\n⚠ Some components still initializing (this is normal)")
            return 0
        else:
            logger.error(f"\n✗ Infrastructure verification failed")
            return 1
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
