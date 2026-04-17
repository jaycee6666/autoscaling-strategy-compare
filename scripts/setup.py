#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Setup Script - Automates Phase 0 initial setup
Automatically creates a virtual environment and sets up the project.

Run this first on a new machine to set everything up!
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


# Color codes for terminal output
class Colors:
    """Terminal color codes"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def is_in_venv():
    """Check if we're already in a virtual environment."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def get_venv_activate_cmd():
    """Get the command to activate virtual environment based on OS."""
    if platform.system() == "Windows":
        return ".\\venv\\Scripts\\activate.bat"
    else:
        return "source venv/bin/activate"


def create_virtual_environment():
    """Create a Python virtual environment."""
    print("\n[*] Creating virtual environment...")

    venv_path = Path("venv")

    if venv_path.exists():
        print("[OK] Virtual environment already exists")
        return True

    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("[OK] Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create virtual environment: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error creating virtual environment: {e}")
        return False


def get_pip_command():
    """Get the pip command from the virtual environment."""
    if platform.system() == "Windows":
        return ".\\venv\\Scripts\\pip.exe"
    else:
        return "./venv/bin/pip"


def run_command(cmd, description="", use_venv_pip=False):
    """Run a shell command."""
    if description:
        print(f"\n[*] {description}")

    try:
        # If we need to use venv pip, replace 'pip' with the full path
        if use_venv_pip:
            pip_cmd = get_pip_command()
            cmd = cmd.replace("pip ", f"{pip_cmd} ", 1)

        result = subprocess.run(cmd, shell=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def run_python_script(script_path, description=""):
    """Run a Python script using the virtual environment Python."""
    if description:
        print(f"\n[*] {description}")

    if platform.system() == "Windows":
        python_cmd = ".\\venv\\Scripts\\python.exe"
    else:
        python_cmd = "./venv/bin/python"

    try:
        result = subprocess.run(f"{python_cmd} {script_path}", shell=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print(" AUTOSCALING PROJECT - QUICK SETUP WITH VIRTUAL ENVIRONMENT")
    print("=" * 70)

    # Step 0: Create virtual environment
    print("\n[SETUP] Step 0: Setting up virtual environment...")
    if is_in_venv():
        print("[INFO] Already running inside a virtual environment")
    else:
        if not create_virtual_environment():
            print("\n[ERROR] Failed to create virtual environment")
            print("Please create it manually:")
            print("  Windows: python -m venv venv && .\\venv\\Scripts\\activate.bat")
            print("  macOS/Linux: python3 -m venv venv && source venv/bin/activate")
            sys.exit(1)

    # Step 1: Check Python
    print("\n[SETUP] Step 1: Checking Python installation...")
    if run_command("python --version", "Getting Python version"):
        print("[OK] Python found")
    else:
        print("[ERROR] Python not found. Please install Python 3.8+")
        sys.exit(1)

    # Step 2: Install dependencies
    print("\n[SETUP] Step 2: Installing Python dependencies...")
    if run_command(
        "pip install -r requirements.txt",
        "Installing packages from requirements.txt",
        use_venv_pip=True,
    ):
        print("[OK] Dependencies installed")
    else:
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)

    # Step 3: Check AWS CLI
    print("\n[SETUP] Step 3: Checking AWS CLI...")
    if run_command("aws --version", "Getting AWS CLI version"):
        print("[OK] AWS CLI found")
    else:
        print("[WARNING] AWS CLI not found. Installing via pip...")
        if run_command("pip install awscli", "Installing AWS CLI", use_venv_pip=True):
            print("[OK] AWS CLI installed")
        else:
            print("[WARNING] Could not install AWS CLI automatically")
            print("   Please install manually:")
            print("   macOS: brew install awscli")
            print("   Linux: sudo apt-get install awscli")
            print("   Windows: choco install awscli")
            print("   Or: pip install awscli")

    # Step 4: Check environment
    print("\n[SETUP] Step 4: Running environment checks...")
    run_python_script("scripts/check_environment.py", "Running environment validation")

    # Step 5: Initialize project
    print("\n[SETUP] Step 5: Initializing project structure...")
    run_python_script("scripts/init_project.py", "Initializing project")

    print("\n" + "=" * 70)
    print("[SUCCESS] SETUP COMPLETE!")
    print("=" * 70)

    print("\n[INFO] Virtual Environment Information:")
    print(f"  Virtual environment location: {Path('venv').absolute()}")

    if platform.system() == "Windows":
        activate_cmd = ".\\venv\\Scripts\\activate.bat"
        print(f"  To activate: {activate_cmd}")
    else:
        activate_cmd = "source venv/bin/activate"
        print(f"  To activate: {activate_cmd}")

    print("\n[INFO] Next Steps:")
    print("  1. Activate virtual environment (see above)")
    print("  2. Edit config/.env with your AWS credentials")
    print("  3. Run: python scripts/check_environment.py")
    print("  4. Read: docs/guides/PHASE4_5_EXECUTION_GUIDE.md")
    print("  5. Deploy: python scripts/deploy_all.py")
    print("\n[INFO] Documentation:")
    print("  - Quick Start: docs/guides/PHASE4_5_EXECUTION_GUIDE.md")
    print("  - Full Plan: docs/plans/PROJECT_EXECUTION_PLAN.md")
    print("  - Reference: docs/guides/PHASE4_5_EXECUTION_GUIDE.md")
    print("  - Troubleshooting: .github/CROSSPLATFORM_GUIDE.md")
    print("\n")


if __name__ == "__main__":
    main()
