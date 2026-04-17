# Virtual Environment Setup Guide

## Table of Contents

1. [Overview](#overview)
2. [Why Virtual Environments?](#why-virtual-environments)
3. [Quick Start](#quick-start)
4. [What setup.py Does](#what-setuppy-does)
5. [Manual Virtual Environment Setup](#manual-virtual-environment-setup)
6. [Activating the Virtual Environment](#activating-the-virtual-environment)
7. [Installing Dependencies](#installing-dependencies)
8. [Deactivating Virtual Environment](#deactivating-virtual-environment)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Overview

This project uses **Python virtual environments** to isolate project dependencies from your system Python installation. This ensures:

- ✅ **Reproducibility** - Same behavior across all team members' machines
- ✅ **Portability** - Works on Windows, macOS, and Linux identically
- ✅ **Safety** - Prevents package conflicts with other projects
- ✅ **Collaboration** - New team members can set up in <5 minutes
- ✅ **Production-Ready** - Easier deployment to AWS

### What is a Virtual Environment?

A Python virtual environment is a self-contained directory structure that contains:
- A specific Python interpreter version
- Project-specific package dependencies
- Isolated from your system Python installation

Think of it as a "sandbox" for your project - completely isolated from other Python projects on your machine.

---

## Why Virtual Environments?

### Without Virtual Environment (❌ Problem):
```
System Python 3.10
├── package-A (version 2.0) ← Project X needs this
├── package-B (version 1.0) ← Project Y needs version 2.0
└── package-C (version 3.0)

Result: Conflict! One project's requirements break the other.
```

### With Virtual Environment (✅ Solution):
```
System Python 3.10 (untouched)

Project X Virtual Environment          Project Y Virtual Environment
├── Python 3.10 (copy)                ├── Python 3.10 (copy)
├── package-A (version 2.0)           ├── package-A (version 1.0)
└── package-C (version 3.0)           ├── package-B (version 2.0)
                                      └── package-C (version 4.0)

Result: No conflicts! Each project has its own isolated dependencies.
```

### For This Project:
- AWS CLI integration requires specific boto3 version
- Python version compatibility matters for cross-platform consistency
- Team members with different project setups won't interfere

---

## Quick Start

### 1. Run the Setup Script (Recommended)
This automatically creates and initializes the virtual environment:

```bash
# Windows (Command Prompt or PowerShell)
python setup.py

# macOS / Linux
python3 setup.py
```

**What it does automatically:**
- Creates `venv/` directory
- Sets up Python interpreter
- Installs dependencies from `requirements.txt`
- Validates AWS CLI and credentials
- Shows activation instructions

### 2. Or Manual Setup (if needed)
See [Manual Virtual Environment Setup](#manual-virtual-environment-setup) section below.

---

## What setup.py Does

When you run `python setup.py`, here's the exact sequence:

### Step 0: Check Virtual Environment Status
```python
if is_in_venv():
    print("✓ Already in virtual environment - proceeding")
else:
    print("✗ Not in virtual environment")
    print("→ Creating new virtual environment...")
    create_virtual_environment()
```

- Detects if you're already in a virtual environment
- If not, creates one automatically
- If yes, skips creation and proceeds

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

Creates `venv/` directory with:
- `venv/bin/` (macOS/Linux) or `venv/Scripts/` (Windows) - Python executable and tools
- `venv/lib/python3.x/site-packages/` - Package installation directory
- `venv/pyvenv.cfg` - Configuration file

### Step 2: Activate Virtual Environment
The script automatically activates it by using the virtual environment's Python:

```bash
# Windows
.\venv\Scripts\python.exe

# macOS / Linux
./venv/bin/python
```

### Step 3: Install Dependencies
```bash
# Uses virtual environment pip (not system pip)
pip install -r requirements.txt
```

Installs:
- boto3 (AWS SDK for Python)
- botocore (boto3 dependency)
- Any other required packages

### Step 4: Validate Environment
Runs each validation script:
- `scripts/check_environment.py` - Validates Python, AWS CLI, credentials
- `scripts/init_project.py` - Creates config files and directories
- Displays warnings for missing AWS credentials

### Step 5: Display Activation Instructions
Shows you the command to manually activate if needed:

```bash
# Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

---

## Manual Virtual Environment Setup

If you prefer to set up manually or if the automatic setup doesn't work:

### Windows (Command Prompt)
```batch
REM Create virtual environment
python -m venv venv

REM Activate it
venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Verify activation (should show (venv) prefix)
python --version
```

### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv venv

# Activate it (may need to enable script execution first)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify activation
python --version
```

### macOS / Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify activation (should show (venv) prefix)
python --version
```

---

## Activating the Virtual Environment

Once created, you need to activate it each time you start working on the project.

### When to Activate

**You should activate BEFORE:**
- Running any project scripts
- Working with the project
- Opening it in an IDE/editor

**You should deactivate AFTER:**
- Finishing work on the project
- Switching to another project
- Closing the terminal

### How to Activate

#### Windows (Command Prompt)
```batch
venv\Scripts\activate.bat
```

**Expected output:**
```
(venv) C:\project\CS5296\project3\autoscaling-strategy-compare>
```

Notice the `(venv)` prefix - this indicates the virtual environment is active.

#### Windows (PowerShell)
```powershell
venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activation again.

#### macOS / Linux
```bash
source venv/bin/activate
```

**Expected output:**
```
(venv) user@machine:autoscaling-strategy-compare$
```

### Verify Activation

After activation, verify the virtual environment is active:

```bash
# Should show path inside venv directory
which python          # macOS/Linux
where python          # Windows

# Should show (venv) prefix in prompt
echo $VIRTUAL_ENV      # macOS/Linux (should show path to venv/)
```

---

## Installing Dependencies

### Using pip from Virtual Environment

Once activated, install packages using `pip`:

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install a single package
pip install boto3

# Install a specific version
pip install boto3==1.26.0

# Upgrade an installed package
pip install --upgrade boto3
```

### Requirements.txt Reference

The `requirements.txt` file lists all required packages:

```txt
boto3>=1.18.0          # AWS SDK for Python
botocore>=1.21.0       # boto3 dependency
python-dotenv>=0.19.0  # Environment variable management
pyyaml>=5.4            # YAML file parsing
```

### Checking Installed Packages

```bash
# List all installed packages
pip list

# Show details of a specific package
pip show boto3

# Check which dependencies are outdated
pip list --outdated
```

---

## Deactivating Virtual Environment

When you're done working on the project:

### All Platforms
```bash
deactivate
```

**Expected output:**
The `(venv)` prefix disappears from your prompt:

```
# Before deactivation
(venv) user@machine:project$

# After deactivation
user@machine:project$
```

You're now back to using your system Python.

---

## Troubleshooting

### Issue 1: "python: command not found" or "python.exe not found"

**Symptom:**
```
python: command not found
```

**Solutions:**

1. **Check if Python is installed:**
   ```bash
   python --version      # or
   python3 --version
   ```

2. **Add Python to PATH:**
   - **Windows**: Reinstall Python and check "Add Python to PATH" during installation
   - **macOS**: Install via Homebrew: `brew install python3`
   - **Linux**: Install via package manager: `sudo apt-get install python3`

3. **Use explicit path:**
   ```bash
   /usr/bin/python3 -m venv venv
   # or
   C:\Python310\python.exe -m venv venv
   ```

---

### Issue 2: "Permission denied" when activating (macOS/Linux)

**Symptom:**
```
bash: ./venv/bin/activate: Permission denied
```

**Solution:**
```bash
# Grant execute permission
chmod +x venv/bin/activate

# Then activate
source venv/bin/activate
```

---

### Issue 3: PowerShell script execution policy error (Windows)

**Symptom:**
```
PowerShell cannot be loaded because running scripts is disabled on this system.
```

**Solution:**
```powershell
# Allow scripts for current user only
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activation again
venv\Scripts\Activate.ps1
```

---

### Issue 4: "Module not found" after activation

**Symptom:**
```
ModuleNotFoundError: No module named 'boto3'
```

**Solution:**

1. **Verify you're in the virtual environment:**
   ```bash
   which python      # macOS/Linux - should show path to venv/
   where python      # Windows - should show path to venv\
   ```

2. **If not activated, activate first:**
   ```bash
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate.bat       # Windows
   ```

3. **Install missing package:**
   ```bash
   pip install boto3
   # or install all from requirements
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   pip list
   python -c "import boto3; print(boto3.__version__)"
   ```

---

### Issue 5: Virtual environment takes too much disk space

**Problem:**
The `venv/` directory is large (~200-500 MB depending on packages)

**Solutions:**

1. **Add to .gitignore (already done):**
   The `venv/` directory is already in `.gitignore`, so it won't be committed to git.

2. **Delete and recreate when needed:**
   ```bash
   # Remove virtual environment
   rm -rf venv              # macOS/Linux
   rmdir /s venv            # Windows

   # Recreate and reinstall
   python -m venv venv
   source venv/bin/activate              # macOS/Linux
   venv\Scripts\activate.bat             # Windows
   pip install -r requirements.txt
   ```

3. **Use storage efficiently:**
   The virtual environment is isolated to the project. Each team member has their own.

---

### Issue 6: "setup.py not found" or can't run it

**Symptom:**
```
python setup.py
error: can't open file 'setup.py': [Errno 2] No such file or directory
```

**Solution:**

1. **Navigate to project root:**
   ```bash
   cd autoscaling-strategy-compare
   ls                    # Check if setup.py exists
   ```

2. **Verify file exists:**
   ```bash
   ls -la setup.py       # macOS/Linux
   dir setup.py          # Windows
   ```

3. **Run with full path:**
   ```bash
   python ./setup.py
   python C:\path\to\autoscaling-strategy-compare\setup.py
   ```

---

### Issue 7: AWS CLI not found in virtual environment

**Symptom:**
```
aws: command not found
```

**Solution:**

1. **AWS CLI is still system-wide**, not installed in venv
   - Type: `aws --version` (should work from anywhere)
   - The scripts use subprocess to call system AWS CLI

2. **If system AWS CLI not installed:**
   ```bash
   # Install system-wide AWS CLI
   pip install awscli          # or
   brew install awscli         # macOS
   sudo apt-get install awscli  # Linux
   # Windows: Use installer from https://aws.amazon.com/cli/
   ```

3. **Verify AWS CLI is accessible:**
   ```bash
   aws --version
   aws configure list
   ```

---

## FAQ

### Q: Do I need to activate the virtual environment every time?

**A:** If you're running scripts from the command line, yes. If you're using an IDE (VS Code, PyCharm), you can configure it to use the virtual environment's Python automatically - then you don't need manual activation.

**IDE Configuration:**
- **VS Code**: Python extension detects and uses `venv/` automatically
- **PyCharm**: Project Settings → Python Interpreter → Select `venv/bin/python`
- **IDE-agnostic**: Always works from the terminal after activation

---

### Q: Can I delete the venv/ folder safely?

**A:** Yes! It's in `.gitignore` and won't affect the repository. You can delete and recreate anytime:

```bash
rm -rf venv                 # macOS/Linux
rmdir /s venv              # Windows

# Recreate
python -m venv venv
source venv/bin/activate    # or activate.bat on Windows
pip install -r requirements.txt
```

---

### Q: How do I update a package in the virtual environment?

**A:** Use pip with the `--upgrade` flag:

```bash
# Update a specific package
pip install --upgrade boto3

# Update all packages
pip install --upgrade -r requirements.txt

# Update to a specific version
pip install boto3==1.27.0
```

Then update `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

### Q: What if team members have different Python versions?

**A:** The virtual environment uses their system Python. If someone has Python 3.8 and another has 3.10:
- Both create `venv/` with their respective Python
- Both environments work correctly (within supported versions: 3.8+)
- All scripts use the same Python version (because scripts use `#!/usr/bin/env python`)

For strict version control, specify in `requirements.txt`:
```txt
; python_version >= "3.8"
boto3>=1.18.0
```

---

### Q: Can I use a different Python version for the virtual environment?

**A:** Yes! Specify the Python version when creating:

```bash
# Use Python 3.9
python3.9 -m venv venv

# Use Python 3.10
python3.10 -m venv venv

# Or find available versions
which python3.9          # macOS/Linux
where python3.9         # Windows
```

Verify after creation:
```bash
source venv/bin/activate
python --version
```

---

### Q: How do I share the setup with new team members?

**A:** New team members only need to:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/USERNAME/autoscaling-strategy-compare.git
   cd autoscaling-strategy-compare
   ```

2. **Run setup.py:**
   ```bash
   python setup.py
   ```

3. **That's it!** The virtual environment is created and configured automatically.

---

### Q: What if setup.py fails?

**A:** 
1. Check the error message for specifics
2. See [Troubleshooting](#troubleshooting) section above
3. Fall back to [Manual Virtual Environment Setup](#manual-virtual-environment-setup)
4. Report issues in team Slack/Discord with the full error output

---

### Q: Can I use different virtual environment tools (venv vs virtualenv vs conda)?

**A:** This project uses Python's built-in `venv`. Using alternatives:
- **virtualenv**: Similar to venv, but more feature-rich
- **conda**: Package and environment manager (requires Anaconda)

We recommend `venv` because:
- ✅ Built-in (no extra installation)
- ✅ Works everywhere (Windows, macOS, Linux)
- ✅ Perfect for cloud deployments
- ✅ Standard in Python community

If you prefer alternatives, you can use them - just ensure dependencies from `requirements.txt` are installed.

---

### Q: Do I need to commit venv/ to git?

**A:** No! The `.gitignore` file already excludes it. This is correct because:
- ✅ venv/ is machine-specific and large (~200-500 MB)
- ✅ Each team member creates their own
- ✅ Dependencies are captured in `requirements.txt`
- ✅ Keeps repository size small

---

## Quick Reference Card

### One-Time Setup
```bash
python setup.py              # Automatic setup (recommended)
# OR
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Daily Activation
```bash
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate.bat    # Windows (Command Prompt)
venv\Scripts\Activate.ps1    # Windows (PowerShell)
```

### Daily Deactivation
```bash
deactivate                   # All platforms
```

### Dependency Management
```bash
pip install -r requirements.txt      # Install all
pip install boto3                    # Install one
pip freeze > requirements.txt         # Update requirements.txt
```

### Troubleshooting
```bash
which python                 # Check activation (macOS/Linux)
where python                 # Check activation (Windows)
pip list                     # Check installed packages
pip show boto3              # Check package details
```

---

## Next Steps

1. ✅ **Run setup.py** to create and configure the virtual environment
2. ✅ **Activate the virtual environment** when working on the project
3. ✅ **Read GETTING_STARTED.md** for project development workflow
4. ✅ **Check AWS credentials** in the setup output

---

## Need Help?

- **Documentation**: See docs/ directory for comprehensive guides
- **Troubleshooting**: Check [Troubleshooting](#troubleshooting) section above
- **Team**: Ask in project Slack/Discord channel
- **Official Docs**: https://docs.python.org/3/tutorial/venv.html

---

**Last Updated**: April 17, 2026
**Version**: 1.0
**Status**: Ready for GitHub upload
