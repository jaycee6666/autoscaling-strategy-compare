# Getting Started Guide

This guide will walk you through the initial setup of the autoscaling project.

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- AWS CLI v2 installed
- AWS account with IAM access
- Git installed (for version control)

## Step 1: Verify Environment

Run the environment check script to verify all dependencies:

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

## Step 2: Install Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install boto3 python-dotenv pyyaml requests
```

## Step 3: Configure AWS Credentials

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

## Step 4: Initialize Project Structure

Run the initialization script:

```bash
python scripts/init_project.py
```

This will:
- ✓ Create config files from templates
- ✓ Set up data collection directories
- ✓ Initialize configuration manager
- ✓ Display configuration summary

## Step 5: Verify AWS Credentials

Test your AWS credentials:

```bash
aws ec2 describe-regions --output table
```

You should see a list of AWS regions. If this fails, your credentials are not configured correctly.

## Step 6: Run Initial Checks

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
- Install missing package: `pip install boto3`
- Or install all requirements: `pip install -r requirements.txt`
- Make sure you're using the correct Python interpreter: `python -m pip install boto3`

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
   - Full guide: `docs/PROJECT_EXECUTION_PLAN.md`
   - Troubleshooting: `docs/CROSSPLATFORM_GUIDE.md`

2. **Deploy Infrastructure**
   ```bash
   python scripts/deploy_all.py
   ```

3. **Start Development**
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
