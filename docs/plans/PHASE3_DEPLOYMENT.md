# Phase 3: Deployment to AWS Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy AWS infrastructure, Flask test application, and load generation tools to AWS, with end-to-end verification.

**Architecture:**
- Deploy Phase 2a AWS infrastructure (VPC, ALB, ASG, EC2 instances)
- Deploy Flask test application to EC2 instances via user data / manual deployment
- Deploy load generator script to a control instance or local machine with AWS credentials
- Verify end-to-end connectivity: local → ALB → EC2 → CloudWatch

**Tech Stack:**
- AWS boto3, CloudFormation-equivalent (infrastructure-as-code)
- EC2 user data scripts for Flask app deployment
- Docker containers for Flask app (optional but recommended)
- CloudWatch monitoring and alarms

**Timeline:** ~6-8 hours
- Infrastructure deployment: 30 min
- Application deployment: 1-2 hours
- Load generator verification: 1 hour
- End-to-end testing: 1-2 hours
- Buffer for troubleshooting: 1-2 hours

---

## Task 1: Deploy AWS Infrastructure with Verification

**Files:**
- Use: `scripts/deploy_all.py` (from Phase 1)
- Verify: `scripts/verify_infrastructure.py` (from Phase 1)
- Output: `infrastructure/` directory with JSON configs
- New: `docs/PHASE3_DEPLOYMENT_LOG.md` (document deployment)

**Objective:** Deploy complete AWS infrastructure stack and verify all components are healthy.

### Step 1: Pre-deployment checklist

Verify prerequisites before deployment:

```bash
# 1. Check AWS credentials are configured
aws sts get-caller-identity

# 2. Verify AWS region
echo $AWS_DEFAULT_REGION  # Should be us-east-1

# 3. Check for existing infrastructure (optional cleanup)
aws ec2 describe-instances --filters "Name=tag:Project,Values=autoscaling-experiment" --query 'Reservations[].Instances[].InstanceId'
```

### Step 2: Deploy infrastructure

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
python scripts/deploy_all.py
```

**Expected output:**
```
Creating VPC...
Creating subnets...
Creating security groups...
Creating IAM role...
Creating launch templates...
Creating Application Load Balancer...
Creating Auto Scaling Groups...
Deployment completed successfully!
```

**Artifacts created:**
- `infrastructure/network-config.json`
- `infrastructure/iam-config.json`
- `infrastructure/security-groups-config.json`
- `infrastructure/launch-templates-config.json`
- `infrastructure/alb-config.json`
- `infrastructure/asg-config.json`
- `infrastructure/deployment-log.json`

### Step 3: Verify infrastructure health

```bash
python scripts/verify_infrastructure.py
```

**Expected output:**
```
✅ VPC exists and is healthy
✅ Subnets created (2 public, 2 private)
✅ Security groups configured
✅ IAM role created with policies
✅ Launch templates created (CPU and request-rate)
✅ ALB is active and listening on port 80
✅ Target groups created and registered
✅ ASG-CPU: 2/2 instances healthy
✅ ASG-Request: 2/2 instances healthy
✅ CloudWatch metrics flowing
Verification: PASS (All checks passed)
```

**If any checks fail:**
1. Review the specific failure message
2. Check AWS Console for the component status
3. Diagnose the issue (common: security group rules, IAM permissions)
4. Fix and re-run verification

### Step 4: Extract ALB DNS and document

Extract ALB DNS name from config:

```bash
# Extract ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")
echo "ALB DNS: $ALB_DNS"

# Test ALB accessibility
curl http://$ALB_DNS/health
# Should return HTTP 200 with health status
```

**Document in PHASE3_DEPLOYMENT_LOG.md:**
```markdown
# Phase 3 Deployment Log

## Infrastructure Deployment

**Date**: [Today's date]
**Deployment Time**: [Duration]
**Status**: ✅ SUCCESS

### Deployed Components

- VPC: experiment-vpc (10.0.0.0/16)
- Public Subnets: 10.0.1.0/24, 10.0.2.0/24
- Private Subnets: 10.0.11.0/24, 10.0.12.0/24
- ALB DNS: <YOUR_ALB_DNS>
- ASG-CPU: experiment-asg-cpu (desired: 2, min: 1, max: 5)
- ASG-Request: experiment-asg-request (desired: 2, min: 1, max: 5)

### Verification Results

All 12 verification checks passed ✅
ALB is accessible: http://<ALB_DNS>/health
```

### Step 5: Commit

```bash
git add infrastructure/ docs/PHASE3_DEPLOYMENT_LOG.md
git commit -m "docs: log Phase 3 infrastructure deployment

- Deployed complete AWS infrastructure (VPC, ALB, ASG)
- All verification checks passed
- ALB accessible and instances healthy"
```

---

## Task 2: Deploy Flask Test Application to EC2

**Files:**
- Deploy: `apps/test_app/app.py`
- Deploy: `apps/test_app/Dockerfile`
- New: `deployment/deploy_app.sh` (deployment script)
- New: `deployment/app-user-data.sh` (EC2 user data)

**Objective:** Deploy Flask application to EC2 instances so they respond to ALB health checks and load test requests.

### Step 1: Create EC2 user data script

Create `deployment/app-user-data.sh`:

```bash
#!/bin/bash
set -e

# Update system
yum update -y
yum install -y python3 python3-pip git

# Install dependencies
pip3 install flask boto3

# Create app directory
mkdir -p /opt/test_app
cd /opt/test_app

# Clone or copy app code (using inline for simplicity)
cat > app.py << 'APPEOF'
[PASTE FULL app.py CONTENT HERE]
APPEOF

# Create systemd service
cat > /etc/systemd/system/test-app.service << 'SERVICEEOF'
[Unit]
Description=Test Autoscaling Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/test_app
ExecStart=/usr/bin/python3 /opt/test_app/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Start service
systemctl daemon-reload
systemctl enable test-app
systemctl start test-app

# Verify app is running
sleep 5
curl http://localhost:8080/health || echo "App not ready yet"
```

### Step 2: Update launch templates to include user data

**Option A: Manual (if not already in Phase 1):**

Update `setup_instances.py` to include user data in launch templates:

```python
user_data = """#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install flask boto3
mkdir -p /opt/test_app
# ... [rest of user data above]
"""

response = ec2_client.create_launch_template(
    LaunchTemplateName='experiment-launch-template-cpu',
    LaunchTemplateData={
        'ImageId': ami_id,
        'InstanceType': 't3.micro',
        'UserData': base64.b64encode(user_data.encode()).decode(),
        # ... other config
    }
)
```

### Step 3: Terminate old instances and create new ones with user data

```bash
# Get ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")

# Update ASG to apply new launch template (if modified)
# AWS will gradually replace instances with new ones

# Wait for instances to be healthy
echo "Waiting for instances to be healthy..."
for i in {1..30}; do
  HEALTHY=$(aws autoscaling describe-auto_scaling_groups \
    --auto-scaling-group-names experiment-asg-cpu \
    --query 'AutoScalingGroups[0].Instances[?HealthStatus==`Healthy`]' \
    --output text | wc -w)
  
  if [ "$HEALTHY" -ge 2 ]; then
    echo "✅ Instances are healthy"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 10
done
```

### Step 4: Verify application is responding

```bash
# Test health endpoint
curl http://$ALB_DNS/health
# Expected: {"status": "healthy", "timestamp": "...", "version": "1.0"}

# Test data endpoint
curl http://$ALB_DNS/data?size=10
# Expected: {"data": "...", "size_kb": 10, "timestamp": "..."}

# Test metrics endpoint
curl http://$ALB_DNS/metrics
# Expected: {"total_requests": N, "elapsed_seconds": X, ...}
```

### Step 5: Create deployment verification script

Create `deployment/verify_app_deployment.py`:

```python
"""Verify Flask application deployment to AWS."""

import requests
import json
import sys
from pathlib import Path

def verify_app_deployment(alb_dns):
    """Verify Flask app is accessible and responding correctly."""
    
    tests_passed = 0
    tests_total = 0
    
    endpoints = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'endpoint': '/health',
            'expected_keys': ['status', 'timestamp']
        },
        {
            'name': 'Data Endpoint',
            'method': 'GET',
            'endpoint': '/data?size=10',
            'expected_keys': ['data', 'size_kb']
        },
        {
            'name': 'Metrics Endpoint',
            'method': 'GET',
            'endpoint': '/metrics',
            'expected_keys': ['total_requests', 'request_rate_per_second']
        },
        {
            'name': 'CPU Intensive (POST)',
            'method': 'POST',
            'endpoint': '/cpu-intensive',
            'data': {'duration': 1},
            'expected_keys': ['cpu_duration_seconds']
        }
    ]
    
    for test in endpoints:
        tests_total += 1
        try:
            url = f"http://{alb_dns}{test['endpoint']}"
            
            if test['method'] == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=test.get('data'), timeout=10)
            
            if response.status_code != 200:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                continue
            
            data = response.json()
            
            # Check required keys
            missing_keys = [k for k in test['expected_keys'] if k not in data]
            if missing_keys:
                print(f"❌ {test['name']}: Missing keys {missing_keys}")
                continue
            
            print(f"✅ {test['name']}: PASS")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ {test['name']}: {str(e)}")
    
    print(f"\nResults: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total

if __name__ == '__main__':
    # Get ALB DNS from config
    config_path = Path('infrastructure/alb-config.json')
    if not config_path.exists():
        print("❌ infrastructure/alb-config.json not found")
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    alb_dns = config['alb_dns_name']
    print(f"Verifying deployment to ALB: {alb_dns}\n")
    
    success = verify_app_deployment(alb_dns)
    sys.exit(0 if success else 1)
```

### Step 6: Run verification

```bash
python deployment/verify_app_deployment.py
```

**Expected output:**
```
Verifying deployment to ALB: experiment-alb-xxx.us-east-1.elb.amazonaws.com

✅ Health Check: PASS
✅ Data Endpoint: PASS
✅ Metrics Endpoint: PASS
✅ CPU Intensive (POST): PASS

Results: 4/4 tests passed
```

### Step 7: Commit

```bash
git add deployment/deploy_app.sh deployment/app-user-data.sh deployment/verify_app_deployment.py
git commit -m "feat: add Flask application deployment scripts

- Create EC2 user data script for app deployment
- Add application verification script
- Document deployment process"
```

---

## Task 3: Verify Load Generator Can Connect

**Files:**
- Use: `scripts/load_generator.py` (from Phase 2b)
- Use: `scripts/metrics_collector.py` (from Phase 2b)
- New: `deployment/test_load_generator.py` (quick verification)

**Objective:** Verify load generator can connect to ALB and generate traffic successfully.

### Step 1: Create quick test script

Create `deployment/test_load_generator.py`:

```python
"""Quick test of load generator against deployed ALB."""

import json
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, 'scripts')

from load_generator import LoadGenerator

def test_load_generator():
    """Run short load test against ALB."""
    
    # Get ALB DNS
    config_path = Path('infrastructure/alb-config.json')
    with open(config_path) as f:
        config = json.load(f)
    
    alb_dns = f"http://{config['alb_dns_name']}"
    
    print(f"Testing load generator against: {alb_dns}\n")
    
    # Create load generator with minimal load
    gen = LoadGenerator(
        target_url=alb_dns,
        request_rate=5,  # 5 requests per second
        duration_seconds=10,  # 10 second test
        pattern='constant',
        endpoint='/health'
    )
    
    print("Running 10-second load test (5 req/s)...")
    stats = gen.generate_load()
    
    print(f"\n✅ Test completed!")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success rate: {stats['successful_requests']/stats['total_requests']*100:.1f}%")
    print(f"Avg response time: {stats['average_response_time']:.3f}s")
    print(f"P95 response time: {stats['p95_response_time']:.3f}s")
    
    return stats['successful_requests'] > 0

if __name__ == '__main__':
    try:
        success = test_load_generator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### Step 2: Run test

```bash
python deployment/test_load_generator.py
```

**Expected output:**
```
Testing load generator against: http://experiment-alb-xxx.us-east-1.elb.amazonaws.com

Running 10-second load test (5 req/s)...

✅ Test completed!
Total requests: 50
Successful: 48
Failed: 2
Success rate: 96.0%
Avg response time: 0.045s
P95 response time: 0.089s
```

### Step 3: Troubleshooting if test fails

**If all requests fail:**
1. Check ALB is accessible: `curl http://$ALB_DNS/health`
2. Check security group allows inbound on port 80
3. Check EC2 instances are running and healthy in ASG

**If response times are slow:**
1. May indicate instances are still starting up
2. Wait 2-3 minutes and retry

**If some requests fail:**
1. This is normal during initial deployment
2. Acceptable if success rate > 90%

### Step 4: Commit

```bash
git add deployment/test_load_generator.py
git commit -m "test: add load generator verification script

- Quick test of load generator against deployed ALB
- Verify connectivity and basic performance metrics"
```

---

## Task 4: Document Deployment and Create Deployment Guide

**Files:**
- Create: `docs/PHASE3_DEPLOYMENT_GUIDE.md`
- Update: `docs/PHASE3_DEPLOYMENT_LOG.md` (from Task 1)

**Objective:** Document the complete deployment process for reproducibility.

### Step 1: Create deployment guide

Create `docs/PHASE3_DEPLOYMENT_GUIDE.md`:

```markdown
# Phase 3: AWS Deployment Guide

## Overview

This guide covers deploying the autoscaling comparison infrastructure and applications to AWS.

## Prerequisites

1. **AWS Account** with credentials configured locally
2. **boto3** installed: `pip install boto3`
3. **Python 3.8+**
4. **curl** for testing (or requests library)

## Deployment Steps

### 1. Deploy Infrastructure (30 min)

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Deploy all infrastructure
python scripts/deploy_all.py

# Verify deployment
python scripts/verify_infrastructure.py
```

### 2. Deploy Flask Application (20-30 min)

The Flask app is deployed via EC2 user data scripts.

**Option A: Automatic (via user data)**

If launch templates include user data, instances will automatically start the Flask app.

**Option B: Manual**

SSH into each instance and:
```bash
yum update -y
yum install -y python3 python3-pip
pip3 install flask boto3
# Copy app.py to /opt/test_app/
python3 /opt/test_app/app.py
```

### 3. Verify Deployment (15 min)

```bash
# Extract ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")

# Test endpoints
curl http://$ALB_DNS/health
curl http://$ALB_DNS/data?size=10
curl http://$ALB_DNS/metrics

# Run verification script
python deployment/verify_app_deployment.py

# Test load generator
python deployment/test_load_generator.py
```

## Troubleshooting

### ALB not accessible
- Check security group allows port 80 inbound
- Verify ALB is in "active" state
- Wait 2-3 minutes after deployment

### Instances not healthy
- Check CloudWatch logs for errors
- Verify IAM role has required permissions
- Check instance security group allows egress to CloudWatch

### Load test fails
- Verify app is responding to health checks
- Check ALB target group health status
- Wait for instances to warm up (2-3 minutes)

## Cost Management

**Important:** This infrastructure incurs AWS charges!

To avoid unexpected costs:
1. **Keep resources running for testing only**
2. **Delete resources after experiments** using:
   ```bash
   # Delete ASG (removes EC2 instances)
   aws autoscaling delete-auto-scaling-group --auto-scaling-group-name experiment-asg-cpu --force-delete
   
   # Delete ALB
   aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN>
   
   # Delete VPC (removes all associated resources)
   aws ec2 delete-vpc --vpc-id <VPC_ID>
   ```

## Next Steps

Once deployment is verified:
1. Run Phase 4-5 experiments
2. Collect metrics from CloudWatch
3. Analyze results and generate report
```

### Step 2: Update deployment log

Append to `docs/PHASE3_DEPLOYMENT_LOG.md`:

```markdown
## Application Deployment

**Date**: [Today's date]
**Status**: ✅ SUCCESS

### Flask Application

- Deployed to all ASG instances via user data
- Health check endpoint responding
- Metrics endpoint accessible

### Verification Results

- Health Check: ✅ PASS
- Data Endpoint: ✅ PASS  
- Metrics Endpoint: ✅ PASS
- CPU Intensive: ✅ PASS
- Load Generator Test: ✅ PASS (96% success rate)

## Costs

- Estimated monthly cost: $3-5 USD (t3.micro instances + ALB)
- Current deployment: Active
- Expected duration: Through April 24, 2026
```

### Step 3: Commit

```bash
git add docs/PHASE3_DEPLOYMENT_GUIDE.md docs/PHASE3_DEPLOYMENT_LOG.md
git commit -m "docs: add Phase 3 deployment guide and logs

- Complete deployment instructions
- Troubleshooting guide
- Cost management notes
- Deployment verification results"
```

---

## Summary

**Phase 3 Implementation Plan Complete**

| Task | Component | Est. Time |
|------|-----------|-----------|
| 1 | Infrastructure Deployment | 1-1.5h |
| 2 | Flask App Deployment | 1-1.5h |
| 3 | Load Generator Verification | 0.5h |
| 4 | Documentation | 0.5h |
| **Total** | **All deployment tasks** | **4-5h** |

**Success Criteria:**
- ✅ All infrastructure components deployed and healthy
- ✅ Flask app responding to health checks
- ✅ ALB accessible from local machine
- ✅ Load generator can send traffic successfully
- ✅ Deployment fully documented

**After Phase 3 is complete:**
- Ready to start Phase 4-5: Run experiments
- Ready to collect metrics from CloudWatch
- Ready to analyze results
