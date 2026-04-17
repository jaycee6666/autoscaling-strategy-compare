# Phase 1: AWS Infrastructure Implementation Guide

## Overview

This guide explains how to use the Phase 1 infrastructure deployment scripts to provision the complete AWS infrastructure for the autoscaling strategy comparison experiment.

## Architecture

```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24) - ALB
├── Private Subnets (10.0.11.0/24, 10.0.12.0/24) - Instances
├── Internet Gateway
├── Security Groups (ALB, App)
├── Application Load Balancer (experiment-alb)
│   ├── Target Group: tg-cpu-asg
│   └── Target Group: tg-request-asg
├── Auto Scaling Group: asg-cpu
│   └── Launch Template: app-cpu-lt
└── Auto Scaling Group: asg-request
    └── Launch Template: app-request-lt
```

## Prerequisites

1. **AWS Account** with credentials configured
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, region (us-east-1)
   ```

2. **Python 3.8+** with boto3 installed
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **AWS Permissions**: Your IAM user needs permissions for:
   - EC2 (VPC, subnets, security groups, instances)
   - IAM (roles, instance profiles)
   - ELB (Application Load Balancer, target groups)
   - Auto Scaling (Auto Scaling groups, policies)
   - CloudWatch (monitoring)

## Quick Start

### Option 1: One-Click Deployment (Recommended)

Deploy the entire infrastructure in one command:

```bash
python scripts/deploy_all.py
```

This will:
1. Create VPC and networking
2. Create IAM roles
3. Create security groups
4. Create launch templates
5. Create ALB
6. Create ASGs
7. Verify everything is working

**Expected time:** 5-10 minutes

### Option 2: Step-by-Step Deployment

Run each script individually:

```bash
# 1. Network infrastructure (VPC, subnets, IGW)
python scripts/setup_network.py
# Output: infrastructure/network-config.json

# 2. IAM role and policies
python scripts/setup_iam_role.py
# Output: infrastructure/iam-config.json

# 3. Security groups
python scripts/setup_security_groups.py
# Output: infrastructure/security-groups-config.json

# 4. Launch templates
python scripts/setup_instances.py
# Output: infrastructure/launch-templates-config.json

# 5. Application Load Balancer
python scripts/setup_alb.py
# Output: infrastructure/alb-config.json

# 6. Auto Scaling Groups
python scripts/setup_asg.py
# Output: infrastructure/asg-config.json

# 7. Verification
python scripts/verify_infrastructure.py
# Output: infrastructure/verification-report.json
```

### Option 3: Verify Existing Infrastructure

If you already have infrastructure deployed and just want to verify it:

```bash
python scripts/deploy_all.py --verify-only
```

## Output Files

All configuration files are saved to `infrastructure/` directory:

```
infrastructure/
├── network-config.json              # VPC, subnets, IGW IDs
├── iam-config.json                  # IAM role and instance profile ARNs
├── security-groups-config.json      # Security group IDs
├── launch-templates-config.json     # Launch template IDs
├── alb-config.json                  # Load balancer DNS and target group ARNs
├── asg-config.json                  # Auto Scaling Group names
├── verification-report.json         # Status of all components
└── deployment-log.json              # Deployment execution log
```

Each file is JSON format for easy parsing by other scripts.

## What Gets Created

### Network (setup_network.py)
- **VPC**: 10.0.0.0/16
- **Public Subnets**: 10.0.1.0/24 (us-east-1a), 10.0.2.0/24 (us-east-1b)
- **Private Subnets**: 10.0.11.0/24 (us-east-1a), 10.0.12.0/24 (us-east-1b)
- **Internet Gateway**: For public subnet routing
- **Route Tables**: Public (to IGW) and private (isolated)

### IAM (setup_iam_role.py)
- **Role**: `EC2RoleForExperiment`
- **Policies**:
  - CloudWatchAgentServerPolicy (send metrics)
  - AmazonS3ReadOnlyAccess (read config)
  - AmazonSSMManagedInstanceCore (remote access)
  - CloudWatchMetrics (custom metrics)
- **Instance Profile**: `EC2InstanceProfileForExperiment`

### Security Groups (setup_security_groups.py)
- **ALB Security Group** (alb-sg):
  - Inbound: HTTP 80, HTTPS 443 from anywhere
  - Outbound: Port 8080 to app-sg
  
- **App Security Group** (app-sg):
  - Inbound: Port 8080 from ALB, Port 22 (SSH) from anywhere
  - Outbound: HTTP 80, HTTPS 443 to anywhere

### Launch Templates (setup_instances.py)
- **app-cpu-lt**: Runs CPU monitoring app
  - Instance type: t3.micro (free tier)
  - Publishes CPU and memory metrics to CloudWatch
  
- **app-request-lt**: Runs request-rate monitoring app
  - Instance type: t3.micro
  - Publishes request rate metrics to CloudWatch

### Load Balancer (setup_alb.py)
- **Application Load Balancer**: `experiment-alb`
  - Deployed in public subnets
  - Listens on HTTP port 80
  
- **Target Groups**:
  - `tg-cpu-asg`: For CPU strategy experiments
  - `tg-request-asg`: For request-rate strategy experiments
  - Health checks: GET /health on port 8080

### Auto Scaling Groups (setup_asg.py)
- **asg-cpu**:
  - Min: 1, Max: 5, Desired: 2 instances
  - Uses app-cpu-lt launch template
  - Scaling policy: Target CPU 50%
  - Cooldown: 60s scale-out, 300s scale-in

- **asg-request**:
  - Min: 1, Max: 5, Desired: 2 instances
  - Uses app-request-lt launch template
  - Scaling policy: Target request rate 10 req/s per instance
  - Cooldown: 60s scale-out, 300s scale-in

## Accessing Your Application

After deployment completes, your application is accessible at:

```
http://<ALB-DNS-Name>
```

The DNS name is printed at the end of `setup_alb.py` and saved in `infrastructure/alb-config.json`.

**Example**: `http://experiment-alb-123456.us-east-1.elb.amazonaws.com`

**Note**: Allow 1-2 minutes for instances to launch and health checks to pass.

## Verification

To check the status of all components:

```bash
python scripts/verify_infrastructure.py
```

This will:
- ✓ Verify VPC and subnets exist
- ✓ Check security groups are configured
- ✓ Verify ALB is active and DNS is available
- ✓ Check target groups have healthy instances
- ✓ Verify Auto Scaling Groups are running
- ✓ List all instances by state
- ✓ Generate verification report (verification-report.json)

## Troubleshooting

### Instances not launching
- Check IAM role is correctly attached
- Verify security group rules allow outbound traffic
- Check EC2 console for instance launch errors
- Review CloudWatch logs for user data script errors

### ALB showing unhealthy targets
- Wait 2-3 minutes for instances to boot
- Check application is listening on port 8080
- Verify /health endpoint returns HTTP 200
- Check security group allows 8080 from ALB

### Can't connect to application
- Verify ALB has a public IP
- Check security group allows inbound 80 from 0.0.0.0/0
- Ensure instances are in running state
- Check ALB target group health

### Scaling not happening
- Verify CloudWatch custom metrics are being published
- Check Auto Scaling policies exist
- Review CloudWatch logs in the application

## Cleanup

To delete all AWS resources:

```bash
python scripts/cleanup_infrastructure.py  # Coming in Phase 1b
```

Or manually through AWS Console:
1. Delete Auto Scaling Groups
2. Delete Load Balancer
3. Delete Launch Templates
4. Delete Security Groups
5. Delete VPC (deletes subnets and IGW automatically)
6. Delete IAM Role

## Cost Considerations

**Estimate for 1 week of experimentation:**
- **t3.micro instances**: ~$1-2 (free tier eligible)
- **ALB**: ~$15-20
- **Data transfer**: $0-1
- **Total**: ~$15-25

**Cost-saving tips:**
- Delete infrastructure when not experimenting
- Use smallest instance type (t3.micro)
- Monitor CloudWatch billing alerts

## Next Steps

After Phase 1 deployment:
1. **Phase 2**: Deploy load generation tool
2. **Phase 3**: Run autoscaling experiments
3. **Phase 4**: Collect and analyze metrics
4. **Phase 5**: Generate report

## Support

For issues:
1. Check logs: `infrastructure/deployment-log.json`
2. Review verification report: `infrastructure/verification-report.json`
3. Check AWS CloudTrail for API errors
4. Run `python scripts/verify_infrastructure.py --verbose`

## Script Reference

### deploy_all.py
Orchestrates all deployment steps in sequence.

```bash
python scripts/deploy_all.py                    # Full deployment
python scripts/deploy_all.py --verify-only      # Verify only
python scripts/deploy_all.py --skip setup_network.py  # Skip a step
```

### setup_network.py
Creates VPC, subnets, IGW, and route tables.

### setup_iam_role.py
Creates IAM role with necessary permissions.

### setup_security_groups.py
Creates and configures security groups.

### setup_instances.py
Creates EC2 launch templates with user data scripts.

### setup_alb.py
Creates Application Load Balancer and target groups.

### setup_asg.py
Creates Auto Scaling Groups with scaling policies.

### verify_infrastructure.py
Verifies all components are created and healthy.

---

**Created**: April 17, 2025
**Last Updated**: April 17, 2025
**Version**: 1.0
