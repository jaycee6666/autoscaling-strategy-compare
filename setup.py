#!/usr/bin/env python3
"""
Quick Setup Script - Automates Phase 0 initial setup
Run this first on a new machine to set everything up!
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command."""
    if description:
        print(f"\n▶️  {description}")

    try:
        result = subprocess.run(cmd, shell=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print(" AUTOSCALING PROJECT - QUICK SETUP")
    print("=" * 70)

    # Step 1: Check Python
    print("\n📋 Step 1: Checking Python installation...")
    if run_command("python --version", "Getting Python version"):
        print("✓ Python found")
    else:
        print("✗ Python not found. Please install Python 3.8+")
        sys.exit(1)

    # Step 2: Install dependencies
    print("\n📦 Step 2: Installing Python dependencies...")
    if run_command(
        "pip install -r requirements.txt", "Installing packages from requirements.txt"
    ):
        print("✓ Dependencies installed")
    else:
        print("✗ Failed to install dependencies")
        sys.exit(1)

    # Step 3: Check AWS CLI
    print("\n☁️  Step 3: Checking AWS CLI...")
    if run_command("aws --version", "Getting AWS CLI version"):
        print("✓ AWS CLI found")
    else:
        print("✗ AWS CLI not found. Please install it:")
        print("   macOS: brew install awscli")
        print("   Linux: sudo apt-get install awscli")
        print("   Windows: Download from https://aws.amazon.com/cli/")
        sys.exit(1)

    # Step 4: Check environment
    print("\n🔍 Step 4: Running environment checks...")
    run_command("python scripts/check_environment.py", "Running environment validation")

    # Step 5: Initialize project
    print("\n⚙️  Step 5: Initializing project structure...")
    run_command("python scripts/init_project.py", "Initializing project")

    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)

    print("\n📝 Next Steps:")
    print("  1. Edit config/.env with your AWS credentials")
    print("  2. Run: python scripts/check_environment.py")
    print("  3. Read: docs/GETTING_STARTED.md")
    print("  4. Deploy: python scripts/deploy_all.py")
    print("\n📚 Documentation:")
    print("  - Quick Start: docs/GETTING_STARTED.md")
    print("  - Full Plan: docs/PROJECT_EXECUTION_PLAN.md")
    print("  - Reference: docs/QUICK_REFERENCE.md")
    print("\n")


if __name__ == "__main__":
    main()
