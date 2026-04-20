#!/usr/bin/env python3
"""
Phase 0: Environment Validation Script
Checks that all required tools and dependencies are installed and configured.
Compatible with Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Union


class EnvironmentChecker:
    """Validates project environment across all platforms."""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.critical_failures = []

    def check_python_version(self) -> Tuple[bool, str]:
        """Verify Python 3.8 or higher is installed."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, f"Python {version.major}.{version.minor} (requires 3.8+)"

    def check_command_exists(self, command: str) -> Tuple[bool, str]:
        """Check if a command is available in PATH."""
        try:
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", command],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, result.stdout.strip().split("\n")[0]
            return False, "Not found in PATH"
        except Exception as e:
            return False, str(e)

    def check_aws_cli(self) -> Tuple[bool, str]:
        """Verify AWS CLI is installed and get version."""
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version_info = (
                    result.stdout.strip() if result.stdout else result.stderr.strip()
                )
                return True, version_info
            return False, "AWS CLI command failed"
        except FileNotFoundError:
            return False, "AWS CLI not found"
        except Exception as e:
            return False, str(e)

    def check_aws_credentials(self) -> Tuple[bool, str]:
        """Check if AWS credentials are configured."""
        # Check via environment variables
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            return True, "Credentials set via environment variables"

        # Check via AWS config file
        aws_dir = Path.home() / ".aws"
        if (aws_dir / "credentials").exists():
            return True, f"Credentials file found at {aws_dir / 'credentials'}"

        return (
            False,
            "No AWS credentials found (set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, or configure ~/.aws/credentials)",
        )

    def check_aws_config(self) -> Tuple[bool, str]:
        """Check if AWS region is configured."""
        region = os.environ.get("AWS_DEFAULT_REGION")
        if region:
            return True, f"Region set to {region}"

        aws_dir = Path.home() / ".aws"
        if (aws_dir / "config").exists():
            return True, f"Config file found at {aws_dir / 'config'}"

        return (
            False,
            "No AWS region configured (set AWS_DEFAULT_REGION or configure ~/.aws/config)",
        )

    def check_git(self) -> Tuple[bool, str]:
        """Verify Git is installed."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, "Git command failed"
        except FileNotFoundError:
            return False, "Git not found"
        except Exception as e:
            return False, str(e)

    def check_pip_packages(self, packages: List[str]) -> Tuple[bool, Dict[str, Any]]:
        """Check if required pip packages are installed."""
        missing = {}
        installed = {}

        for package in packages:
            try:
                # Try to import the package
                __import__(package)
                installed[package] = "[OK]"
            except ImportError:
                missing[package] = "[ERROR]"

        return len(missing) == 0, {"installed": installed, "missing": missing}

    def check_directory_structure(self) -> Tuple[bool, List[str]]:
        """Verify required directories exist."""
        required_dirs = ["scripts", "config", "data", "docs"]
        missing = []

        for directory in required_dirs:
            if not Path(directory).exists():
                missing.append(directory)

        return len(missing) == 0, missing

    def check_write_permissions(self) -> Tuple[bool, str]:
        """Verify write permissions in current directory."""
        test_file = Path("._write_test")
        try:
            test_file.write_text("test")
            test_file.unlink()
            return True, "Write permissions OK"
        except Exception as e:
            return False, str(e)

    def run_all_checks(self):
        """Run all environment checks."""
        print("\n" + "=" * 60)
        print("ENVIRONMENT VALIDATION REPORT")
        print("=" * 60 + "\n")

        # Python
        print("[PKG] PYTHON ENVIRONMENT")
        print("-" * 60)
        status, info = self.check_python_version()
        self.results["Python"] = {"status": status, "info": info}
        print(f"  Python Version: {'[OK]' if status else '[ERROR]'} {info}")

        # Required Commands
        print("\n[SETUP] REQUIRED COMMANDS")
        print("-" * 60)
        commands = ["aws", "git"]
        for cmd in commands:
            status, info = self.check_command_exists(cmd)
            self.results[f"Command: {cmd}"] = {"status": status, "info": info}
            print(f"  {cmd:15} {'[OK]' if status else '[ERROR]'} {info}")

        # AWS Configuration
        print("\n[...]  AWS CONFIGURATION")
        print("-" * 60)

        status, info = self.check_aws_cli()
        self.results["AWS CLI"] = {"status": status, "info": info}
        print(f"  AWS CLI:       {'[OK]' if status else '[ERROR]'} {info}")
        if not status:
            self.critical_failures.append("AWS CLI not found")

        status, info = self.check_aws_credentials()
        self.results["AWS Credentials"] = {"status": status, "info": info}
        print(f"  Credentials:   {'[OK]' if status else '[ERROR]'} {info}")
        if not status:
            self.critical_failures.append("AWS credentials not configured")

        status, info = self.check_aws_config()
        self.results["AWS Region"] = {"status": status, "info": info}
        print(f"  Region Config: {'[OK]' if status else '[ERROR]'} {info}")

        # Python Packages
        print("\n[...] PYTHON PACKAGES")
        print("-" * 60)
        required_packages = ["boto3", "dotenv", "yaml", "requests"]
        status, packages_info = self.check_pip_packages(required_packages)
        self.results["Python Packages"] = {"status": status, "details": packages_info}

        for pkg, result in packages_info["installed"].items():
            print(f"  {pkg:20} {result} installed")

        for pkg, result in packages_info["missing"].items():
            print(f"  {pkg:20} {result} MISSING (install: pip install {pkg})")

        # Directory Structure
        print("\n[...] DIRECTORY STRUCTURE")
        print("-" * 60)
        status, missing = self.check_directory_structure()
        self.results["Directories"] = {"status": status, "missing": missing}
        if status:
            print(f"  All required directories: [OK] Found")
        else:
            print(f"  Missing directories: [ERROR]")
            for d in missing:
                print(f"    - {d}")

        # File Permissions
        print("\n[...] FILE PERMISSIONS")
        print("-" * 60)
        status, info = self.check_write_permissions()
        self.results["Write Permissions"] = {"status": status, "info": info}
        print(f"  Current directory: {'[OK]' if status else '[ERROR]'} {info}")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results.values() if r.get("status", False))

        print(f"\nPassed: {passed_checks}/{total_checks}")

        if self.critical_failures:
            print(f"\n[WARN]  CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"  - {failure}")
            print("\n[...] ENVIRONMENT CHECK FAILED")
            print("Please fix the critical issues above before proceeding.\n")
            return False
        else:
            print("\n[...] ENVIRONMENT CHECK PASSED")
            print("You can proceed with project setup!\n")
            return True


def main():
    """Run environment checker."""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()

    # Save results to file
    results_file = Path("config/check_environment_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(checker.results, indent=2, default=str))
    print(f"[...] Results saved to: {results_file}\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
