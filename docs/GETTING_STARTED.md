# Getting Started Guide

This guide will walk you through the initial setup of the autoscaling project.

## Quick Start (5 Minutes)

### One Command Setup
```bash
python setup.py
```

This single command will:
- ✅ Create a Python virtual environment (isolated, cross-platform)
- ✅ Install all dependencies (boto3, AWS CLI integration, utilities)
- ✅ Verify your system configuration
- ✅ Initialize project directories and configuration
- ✅ Check AWS credentials
- ✅ Display next steps

**That's it!** Your environment is ready. Skip to [Step 5](#step-5-activate-virtual-environment) below.

---

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- AWS CLI v2 installed
- AWS account with IAM access
- Git installed (for version control)

**For detailed setup of each tool, see [CROSSPLATFORM_GUIDE.md](CROSSPLATFORM_GUIDE.md)**

---

## Detailed Setup Steps

### Step 1: Automatic Setup (Recommended) ⭐

The simplest way - this creates and configures everything:

```bash
# Windows, macOS, or Linux - same command
python setup.py
```

**What happens:**
1. Creates Python virtual environment in `venv/` directory
2. Activates it automatically
3. Installs dependencies from `requirements.txt`
4. Runs environment verification
5. Initializes project configuration
6. Shows activation instructions for next time

**Skip to Step 5 below** - your environment is now ready!

---

### Step 2: Manual Setup (If Automatic Setup Fails)

If `python setup.py` has issues, follow these manual steps:

#### 2a: Create Virtual Environment

```bash
# Windows, macOS, or Linux - same command
python -m venv venv
```

#### 2b: Activate Virtual Environment

**Windows (Command Prompt):**
```batch
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Verify activation** - your prompt should show `(venv)` prefix:
```
(venv) user@machine:project$
```

#### 2c: Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2d: Verify Environment

```bash
python scripts/check_environment.py
```

This will check:
- ✓ Python version
- ✓ AWS CLI installation
- ✓ Git installation
- ✓ AWS credentials configuration
- ✓ AWS region configuration
- ✓ Required Python packages
- ✓ Directory structure
- ✓ Write permissions

---

### Step 3: Configure AWS Credentials

### Option A: Using Environment Variables (Recommended for CI/CD)

```bash
# Linux / macOS
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### Option B: Using ~/.aws/credentials (Recommended for local development)

```bash
# Run AWS CLI configure (interactive)
aws configure

# Or manually edit ~/.aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

# And ~/.aws/config
[default]
region = us-east-1
output = json
```

### Option C: Using Project .env File

Copy the template and add your credentials:

```bash
cp config/.env.template config/.env
```

Then edit `config/.env`:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

⚠️ **Important**: Never commit `.env` to Git (it's in .gitignore)

---

### Step 4: Initialize Project Structure

Run the initialization script:

```bash
python scripts/init_project.py
```

This will:
- ✓ Create config files from templates
- ✓ Set up data collection directories
- ✓ Initialize configuration manager
- ✓ Display configuration summary

**Note**: If you ran `python setup.py`, this was already done automatically.

---

### Step 5: Activate Virtual Environment (For Future Sessions)

Once the virtual environment is created (first time), you need to **activate it each time** you work on the project:

**Windows (Command Prompt):**
```batch
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Verify** - you should see `(venv)` prefix in your prompt:
```
(venv) user@machine:autoscaling-strategy-compare$
```

👉 **See [VIRTUAL_ENVIRONMENT.md](VIRTUAL_ENVIRONMENT.md)** for complete virtual environment documentation including troubleshooting.

---

### Step 6: Verify AWS Credentials

Test your AWS credentials:

```bash
aws ec2 describe-regions --output table
```

You should see a list of AWS regions. If this fails, your credentials are not configured correctly.

## Step 7: Run Initial Checks

```bash
# 1. Check environment again
python scripts/check_environment.py

# 2. Test AWS configuration
python scripts/aws_utils.py
```

## Troubleshooting

### Python not found
**Issue**: `python: command not found`

**Solution**:
- Use `python3` instead of `python` on macOS/Linux
- Or add Python to PATH on Windows

### AWS CLI not found
**Issue**: `aws: command not found`

**Solution**:
- Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- On macOS: `brew install awscli`
- On Linux: `sudo apt-get install awscli` (or appropriate package manager)
- On Windows: Use the official installer or Chocolatey: `choco install awscli`

### AWS credentials not found
**Issue**: `Unable to locate credentials`

**Solution**:
- Verify environment variables are set: `echo $AWS_ACCESS_KEY_ID`
- Check ~/.aws/credentials exists and is readable
- Verify AWS access key ID and secret access key are correct
- Check for typos in configuration

### Import errors for packages
**Issue**: `ModuleNotFoundError: No module named 'boto3'`

**Solution**:
- Verify you're in the virtual environment: `which python` (macOS/Linux) or `where python` (Windows) - should show path to `venv/`
- If not activated, activate it: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate.bat` (Windows)
- Install missing package: `pip install boto3`
- Or install all requirements: `pip install -r requirements.txt`
- See [VIRTUAL_ENVIRONMENT.md](VIRTUAL_ENVIRONMENT.md) for more details

### Virtual environment errors
**Issue**: `Permission denied`, `ModuleNotFoundError`, or activation fails

**Solution**:
- See [VIRTUAL_ENVIRONMENT.md](VIRTUAL_ENVIRONMENT.md) Troubleshooting section
- Includes detailed solutions for all common virtual environment issues

### Permission denied errors
**Issue**: `Permission denied: 'config/.env'`

**Solution**:
- On Linux/macOS: `chmod 644 config/.env`
- Make sure you have write permissions to the current directory

## Platform-Specific Notes

### Windows

1. Use `python` instead of `python3` (unless using WSL)
2. Use `set` command for environment variables (or PowerShell `$env:`)
3. Paths use backslashes (script handles this automatically)

### macOS

1. Use `python3` or `python` (depending on installation)
2. Use `export` command for environment variables
3. Install AWS CLI via Homebrew: `brew install awscli`

### Linux

1. Use `python3` or `python` (usually `python3`)
2. Use `export` command for environment variables
3. Install AWS CLI via package manager: `apt-get install awscli`

## Next Steps

Once setup is complete:

1. **Read Documentation**
   - Start with: `docs/QUICK_REFERENCE.md`
   - Virtual Environment: `docs/VIRTUAL_ENVIRONMENT.md` (especially if you're new to venv)
   - Full guide: `docs/PROJECT_EXECUTION_PLAN.md`
   - Troubleshooting: `docs/CROSSPLATFORM_GUIDE.md`

2. **Daily Workflow**
   ```bash
   # Each time you work on the project:
   source venv/bin/activate              # macOS/Linux
   venv\Scripts\activate.bat             # Windows
   
   # When done working:
   deactivate                             # All platforms
   ```

3. **Deploy Infrastructure**
   ```bash
   python scripts/deploy_all.py
   ```

4. **Start Development**
   - Refer to `docs/PROJECT_EXECUTION_PLAN.md` Phase 4

## Common Commands

```bash
# Environment Setup
python scripts/check_environment.py
python scripts/init_project.py

# AWS Operations
python scripts/setup_network.py
python scripts/setup_security_groups.py
python scripts/setup_instances.py

# Deployment
python scripts/deploy_all.py
python scripts/verify_deployment.py

# Cleanup
python scripts/cleanup_infrastructure.py
```

## Getting Help

- **Environment Issues**: See `docs/CROSSPLATFORM_GUIDE.md`
- **AWS Setup**: See `docs/PROJECT_EXECUTION_PLAN.md` Phase 1-3
- **Team Coordination**: See `docs/ADMIN_GUIDE.md`
- **Quick Lookup**: See `docs/QUICK_REFERENCE.md`

## Support Contacts

- Project Lead: [Check ADMIN_GUIDE.md]
- AWS Issues: AWS Documentation and Support
- Python Issues: Python Documentation and Stack Overflow

---

**Version**: 1.0  
**Last Updated**: April 17, 2026
