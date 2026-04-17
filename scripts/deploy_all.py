#!/usr/bin/env python3
"""
Task 8: One-Click Infrastructure Deployment
=============================================

Orchestrates running all infrastructure setup scripts in sequence.

Execution Order:
  1. setup_network.py           - VPC, subnets, IGW
  2. setup_iam_role.py          - IAM role and policies
  3. setup_security_groups.py   - Security groups
  4. setup_instances.py         - Launch templates
  5. setup_alb.py               - Application Load Balancer
  6. setup_asg.py               - Auto Scaling Groups
  7. verify_infrastructure.py   - Verification
  (8. cleanup_infrastructure.py - Optional cleanup)

Usage:
  python scripts/deploy_all.py        # Deploy everything
  python scripts/deploy_all.py --verify-only  # Skip setup, just verify
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates infrastructure deployment."""

    DEPLOYMENT_STEPS = [
        ("setup_network.py", "Network Infrastructure"),
        ("setup_iam_role.py", "IAM Role & Policies"),
        ("setup_security_groups.py", "Security Groups"),
        ("setup_instances.py", "EC2 Launch Templates"),
        ("setup_alb.py", "Application Load Balancer"),
        ("setup_asg.py", "Auto Scaling Groups"),
        ("verify_infrastructure.py", "Infrastructure Verification"),
    ]

    def __init__(self, project_root: Path):
        """Initialize orchestrator."""
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts"
        self.infrastructure_dir = project_root / "infrastructure"
        self.infrastructure_dir.mkdir(exist_ok=True)

        self.deployment_log = {
            "start_time": datetime.utcnow().isoformat(),
            "steps": {},
            "summary": {},
        }

    def run_script(self, script_name: str, step_name: str) -> Tuple[bool, str]:
        """Run a deployment script."""
        try:
            script_path = self.scripts_dir / script_name

            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")

            logger.info(f"\n{'=' * 60}")
            logger.info(f"[STEP] {step_name}")
            logger.info(f"{'=' * 60}")
            logger.info(f"Running: {script_name}")

            start_time = time.time()

            # Run script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout per script
            )

            elapsed_time = time.time() - start_time

            if result.returncode == 0:
                logger.info(
                    f"✓ {step_name} completed successfully ({elapsed_time:.1f}s)"
                )

                self.deployment_log["steps"][script_name] = {
                    "status": "SUCCESS",
                    "elapsed_seconds": elapsed_time,
                    "output": result.stdout[-500:],  # Last 500 chars
                }

                return True, result.stdout
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"✗ {step_name} failed")
                logger.error(f"Error output:\n{error_msg}")

                self.deployment_log["steps"][script_name] = {
                    "status": "FAILED",
                    "elapsed_seconds": elapsed_time,
                    "error": error_msg[-1000:],  # Last 1000 chars of error
                }

                return False, error_msg
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {step_name} timed out (exceeded 10 minutes)")
            self.deployment_log["steps"][script_name] = {
                "status": "TIMEOUT",
                "error": "Script execution exceeded 10 minute timeout",
            }
            return False, "Script timeout"
        except Exception as e:
            logger.error(f"✗ {step_name} failed with exception: {e}")
            self.deployment_log["steps"][script_name] = {
                "status": "ERROR",
                "error": str(e),
            }
            return False, str(e)

    def deploy(
        self, skip_steps: Optional[List[str]] = None, verify_only: bool = False
    ) -> bool:
        """Execute full deployment."""
        skip_steps = skip_steps or []

        logger.info("=" * 60)
        logger.info("AWS Infrastructure Deployment Orchestrator")
        logger.info("=" * 60)
        logger.info(f"Project Root: {self.project_root}")
        logger.info(f"Region: us-east-1")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")

        if verify_only:
            logger.info("\n⚙ Mode: VERIFY ONLY")
            steps_to_run = [self.DEPLOYMENT_STEPS[-1]]  # Only verification
        else:
            logger.info(
                f"\n⚙ Mode: FULL DEPLOYMENT ({len(self.DEPLOYMENT_STEPS)} steps)"
            )
            steps_to_run = [
                step for step in self.DEPLOYMENT_STEPS if step[0] not in skip_steps
            ]

        logger.info(f"Steps to execute: {len(steps_to_run)}")

        failed_steps = []
        successful_steps = []

        try:
            for i, (script_name, step_name) in enumerate(steps_to_run, 1):
                logger.info(f"\n[{i}/{len(steps_to_run)}] {step_name}...")

                success, output = self.run_script(script_name, step_name)

                if success:
                    successful_steps.append((script_name, step_name))
                else:
                    failed_steps.append((script_name, step_name, output))

                    # Don't stop on verification failures
                    if script_name == "verify_infrastructure.py":
                        logger.warning("⚠ Verification found issues, but continuing...")
                    else:
                        # Stop on setup failures
                        logger.error(
                            f"\n✗ Deployment halted due to failure in {step_name}"
                        )
                        break

                # Wait between steps for AWS eventual consistency
                if i < len(steps_to_run):
                    logger.info(f"Waiting 5 seconds before next step...")
                    time.sleep(5)

            # Generate summary
            self.deployment_log["end_time"] = datetime.utcnow().isoformat()
            self.deployment_log["summary"] = {
                "total_steps": len(steps_to_run),
                "successful_steps": len(successful_steps),
                "failed_steps": len(failed_steps),
                "status": "SUCCESS" if not failed_steps else "FAILED",
            }

            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("DEPLOYMENT SUMMARY")
            logger.info("=" * 60)

            logger.info(
                f"\nSuccessful Steps ({len(successful_steps)}/{len(steps_to_run)}):"
            )
            for script_name, step_name in successful_steps:
                logger.info(f"  ✓ {step_name}")

            if failed_steps:
                logger.error(f"\nFailed Steps ({len(failed_steps)}):")
                for script_name, step_name, error in failed_steps:
                    logger.error(f"  ✗ {step_name}")

            # Final status
            if not failed_steps:
                logger.info("\n" + "=" * 60)
                logger.info("✓ DEPLOYMENT SUCCESSFUL!")
                logger.info("=" * 60)
                logger.info("\nYour infrastructure is ready!")
                logger.info("Check infrastructure/ directory for configuration files.")
                return True
            else:
                logger.error("\n" + "=" * 60)
                logger.error("✗ DEPLOYMENT FAILED")
                logger.error("=" * 60)
                return False

        except KeyboardInterrupt:
            logger.warning("\n\n⚠ Deployment interrupted by user")
            self.deployment_log["summary"]["status"] = "INTERRUPTED"
            return False
        except Exception as e:
            logger.error(f"\n✗ Unexpected error during deployment: {e}")
            self.deployment_log["summary"]["status"] = "ERROR"
            return False
        finally:
            # Save deployment log
            self.save_deployment_log()

    def save_deployment_log(self) -> None:
        """Save deployment log to file."""
        try:
            log_file = self.infrastructure_dir / "deployment-log.json"
            with open(log_file, "w") as f:
                json.dump(self.deployment_log, f, indent=2)
            logger.info(f"\n✓ Deployment log saved to: {log_file}")
        except Exception as e:
            logger.error(f"✗ Failed to save deployment log: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy AWS infrastructure for autoscaling experiments"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Run verification only (skip infrastructure setup)",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=[],
        help="Scripts to skip (e.g., --skip setup_network.py setup_iam_role.py)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory",
    )

    args = parser.parse_args()

    try:
        orchestrator = DeploymentOrchestrator(args.project_root)
        success = orchestrator.deploy(
            skip_steps=args.skip, verify_only=args.verify_only
        )

        return 0 if success else 1
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
