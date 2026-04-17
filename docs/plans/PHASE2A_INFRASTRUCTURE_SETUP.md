# Phase 2A: AWS Infrastructure Setup & Configuration Guide

**Project**: autoscaling-strategy-compare  
**Phase**: 2A - Infrastructure Scripts & Tooling  
**Status**: ✅ COMPLETE  
**Artifacts**: Python scripts, JSON configuration files, AWS CloudFormation templates (alternative)

---

## Overview

Phase 2A establishes the infrastructure provisioning and configuration tooling for the autoscaling experiment environment. This phase creates reusable, cross-platform scripts that:

1. **Provision AWS Resources** - VPC, subnets, security groups, EC2 instances, Application Load Balancer, Auto Scaling Groups
2. **Generate Configuration** - JSON files documenting infrastructure state for downstream phases
3. **Verify Deployment** - Health checks and infrastructure validation
4. **Provide Infrastructure Artifacts** - Config files used by Phase 2B (application development) and Phase 3 (deployment)

---

## Phase 2A Scope & Objectives

### What Phase 2A Covers

- AWS account setup and credential configuration
- VPC and network infrastructure
- Security group and IAM role configuration
- EC2 instance templates
- Application Load Balancer (ALB) setup
- Auto Scaling Group (ASG) configuration
- CloudWatch monitoring setup
- Infrastructure verification and health checks

### What Phase 2A Does NOT Cover

- **Application code** (covered in Phase 2B)
- **Deployment to EC2** (covered in Phase 3)
- **Experiment execution** (covered in Phase 4-5)
- **Analysis** (covered in Phase 6-7)

### Success Criteria

- ✅ All AWS resources deployed and verified
- ✅ Infrastructure configuration files created (JSON)
- ✅ Security groups properly configured
- ✅ EC2 instances launched and verified
- ✅ ALB and ASG ready for traffic
- ✅ CloudWatch monitoring active

---

## Phase 2A Scripts

All scripts are located in `scripts/` directory and use **boto3** (no AWS CLI subprocess calls).

### 1. IAM Role Setup
**File**: `scripts/setup_iam_role.py`

**Purpose**: Create IAM role and instance profile for EC2 instances

**What it does**:
- Creates IAM role with EC2 trust policy
- Attaches policies for CloudWatch monitoring
- Attaches policies for S3 access (if needed)
- Creates instance profile for EC2 launch

**Prerequisites**:
- AWS credentials configured
- IAM permissions to create roles and attach policies

**Usage**:
```bash
python scripts/setup_iam_role.py
```

**Output**:
- IAM role: `autoscaling-experiment-role`
- Instance profile: `autoscaling-experiment-instance-profile`

**Verification**:
```bash
aws iam get-role --role-name autoscaling-experiment-role
aws iam list-instance-profiles --query 'InstanceProfiles[*].InstanceProfileName'
```

---

### 2. Security Groups Setup
**File**: `scripts/setup_security_groups.py`

**Purpose**: Create VPC and security groups with proper firewall rules

**What it does**:
- Creates VPC with configurable CIDR block
- Creates public/private subnets
- Creates NAT gateway for outbound traffic
- Creates security group for ALB (ingress: HTTP 80, HTTPS 443)
- Creates security group for EC2 instances (ingress: from ALB)
- Creates security group for bastion/SSH (optional)

**Prerequisites**:
- AWS credentials configured
- EC2 permissions to create VPC and security groups

**Usage**:
```bash
python scripts/setup_security_groups.py
```

**Output**:
- VPC with subnets
- Security groups configured
- Configuration saved to `infrastructure/security-config.json`

**Verification**:
```bash
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,Tags]'
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,GroupName]'
```

---

### 3. ALB Setup
**File**: `scripts/setup_alb.py`

**Purpose**: Create and configure Application Load Balancer

**What it does**:
- Creates ALB in public subnets
- Creates target groups for EC2 instances
- Configures health check parameters
- Sets up listener for HTTP traffic (port 80)
- Generates ALB DNS name for later reference

**Prerequisites**:
- VPC and subnets created (from setup_security_groups.py)
- Security groups created

**Usage**:
```bash
python scripts/setup_alb.py
```

**Output**:
- Application Load Balancer created
- Target groups configured
- DNS name saved to `infrastructure/alb-config.json`

**Verification**:
```bash
aws elbv2 describe-load-balancers --query 'LoadBalancers[*].[LoadBalancerName,DNSName]'
aws elbv2 describe-target-groups --query 'TargetGroups[*].[TargetGroupName,HealthCheckPath]'
```

---

### 4. EC2 Instances Setup
**File**: `scripts/setup_instances.py`

**Purpose**: Launch EC2 instances with proper configuration

**What it does**:
- Creates EC2 instances from launch template or AMI
- Attaches IAM instance profile for CloudWatch access
- Configures security groups
- Tags instances for management
- Configures CloudWatch agent (optional)
- Saves instance IDs and details to configuration

**Prerequisites**:
- VPC, subnets, and security groups created
- IAM role created
- AMI selection

**Usage**:
```bash
python scripts/setup_instances.py --count 2 --instance-type t3.micro
```

**Output**:
- EC2 instances launched
- Instance details saved to `infrastructure/instances-config.json`

**Verification**:
```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PrivateIpAddress]'
aws ec2 describe-instance-status --query 'InstanceStatuses[*].[InstanceId,InstanceStatus.Status]'
```

---

### 5. Auto Scaling Group (ASG) Setup
**File**: `scripts/setup_asg.py`

**Purpose**: Create Auto Scaling Groups for both CPU and request-rate strategies

**What it does**:
- Creates launch template for EC2 instances
- Creates two ASGs (one for each autoscaling strategy)
- Configures desired capacity and scaling policies
- Attaches ASG to ALB target group
- Configures scaling metrics (CPU utilization and custom request rate)
- Sets up CloudWatch alarms for scaling events

**Prerequisites**:
- EC2 instances running (or use launch template)
- Target groups created by ALB setup

**Usage**:
```bash
python scripts/setup_asg.py
```

**Output**:
- Auto Scaling Groups created:
  - `experiment-asg-cpu` (CPU-based scaling)
  - `experiment-asg-request` (Request-rate-based scaling)
- ASG configuration saved to `infrastructure/asg-config.json`

**Verification**:
```bash
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity,MinSize,MaxSize]'
aws autoscaling describe-scaling-activities --auto-scaling-group-name experiment-asg-cpu --query 'Activities[*].[StartTime,Description,Cause]'
```

---

### 6. Network Configuration
**File**: `scripts/setup_network.py`

**Purpose**: Configure network-level resources (subnets, NAT, route tables)

**What it does**:
- Creates VPC
- Creates public and private subnets
- Configures route tables
- Sets up NAT gateway for EC2 outbound traffic
- Configures DNS resolution

**Prerequisites**:
- AWS credentials configured
- EC2 permissions

**Usage**:
```bash
python scripts/setup_network.py
```

**Output**:
- VPC and subnets configured
- Route tables created
- NAT gateway deployed

**Verification**:
```bash
aws ec2 describe-subnets --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone]'
aws ec2 describe-route-tables --query 'RouteTables[*].[RouteTableId,Routes[*].[DestinationCidrBlock,GatewayId]]'
aws ec2 describe-nat-gateways --query 'NatGateways[*].[NatGatewayId,State]'
```

---

### 7. Infrastructure Verification
**File**: `scripts/verify_infrastructure.py`

**Purpose**: Verify all infrastructure components are deployed and healthy

**What it does**:
- Checks VPC existence and configuration
- Verifies security groups and firewall rules
- Validates EC2 instances are running
- Checks ALB is active and health checks passing
- Verifies ASG configuration
- Tests connectivity to ALB endpoint
- Validates IAM roles and permissions

**Prerequisites**:
- All infrastructure setup scripts executed

**Usage**:
```bash
python scripts/verify_infrastructure.py
```

**Output**:
- Verification report with status for each component
- Sample curl commands to test connectivity
- Remediation suggestions if issues found

**Example verification output**:
```
✅ VPC: vpc-12345 (CIDR: 10.0.0.0/16)
✅ Subnets: 4 subnets configured
✅ Security Groups: 3 groups configured
✅ IAM Role: autoscaling-experiment-role exists
✅ EC2 Instances: 2 running (i-111, i-222)
✅ ALB: ALB active (DNS: experiment-alb-xxx.us-east-1.elb.amazonaws.com)
✅ Target Group: 2 healthy targets
✅ ASGs: 2 ASGs configured (CPU, Request-Rate)
✅ CloudWatch: Monitoring active
```

---

### 8. Master Deployment Script
**File**: `scripts/deploy_all.py`

**Purpose**: Orchestrate all infrastructure setup scripts in correct order

**What it does**:
- Executes scripts in proper sequence
- Handles errors and provides rollback options
- Validates each step before proceeding
- Generates final infrastructure report

**Prerequisites**:
- AWS credentials configured
- Proper permissions

**Usage**:
```bash
# Full deployment
python scripts/deploy_all.py

# Dry-run (no changes)
python scripts/deploy_all.py --dry-run

# Skip to specific step
python scripts/deploy_all.py --start-step setup_instances
```

**Execution Order**:
1. `setup_iam_role.py` - Create IAM roles
2. `setup_network.py` - Create VPC and network
3. `setup_security_groups.py` - Create security groups
4. `setup_alb.py` - Create ALB
5. `setup_instances.py` - Launch EC2 instances
6. `setup_asg.py` - Create ASGs
7. `verify_infrastructure.py` - Verify everything

**Output**:
- `infrastructure/` directory with all JSON config files
- Deployment log file
- Infrastructure report

---

## Infrastructure Configuration Files

All scripts generate JSON configuration files in the `infrastructure/` directory:

### alb-config.json
```json
{
  "alb_name": "experiment-alb",
  "alb_arn": "arn:aws:elasticloadbalancing:...",
  "alb_dns_name": "experiment-alb-1234567890.us-east-1.elb.amazonaws.com",
  "target_group_arn": "arn:aws:elasticloadbalancing:...",
  "port": 80,
  "protocol": "HTTP"
}
```

### asg-config.json
```json
{
  "asg_cpu_name": "experiment-asg-cpu",
  "asg_cpu_arn": "arn:aws:autoscaling:...",
  "asg_request_name": "experiment-asg-request",
  "asg_request_arn": "arn:aws:autoscaling:...",
  "desired_capacity": 2,
  "min_size": 1,
  "max_size": 5,
  "health_check_type": "ELB"
}
```

### instances-config.json
```json
{
  "instance_ids": ["i-0123456789abcdef0", "i-0123456789abcdef1"],
  "instance_type": "t3.micro",
  "image_id": "ami-0c55b159cbfafe1f0",
  "key_name": "my-key-pair",
  "security_group_ids": ["sg-12345"]
}
```

### security-config.json
```json
{
  "vpc_id": "vpc-12345",
  "vpc_cidr": "10.0.0.0/16",
  "public_subnets": ["subnet-111", "subnet-222"],
  "private_subnets": ["subnet-333", "subnet-444"],
  "security_group_alb": "sg-alb-12345",
  "security_group_ec2": "sg-ec2-12345"
}
```

---

## Deployment Process

### Quick Start

```bash
# 1. Navigate to project directory
cd autoscaling-strategy-compare

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Run master deployment script
python scripts/deploy_all.py

# 4. Verify infrastructure
python scripts/verify_infrastructure.py

# 5. Note ALB DNS name for Phase 2B and Phase 3
cat infrastructure/alb-config.json | grep alb_dns_name
```

### Expected Output

After successful Phase 2A deployment:

```
✅ Phase 2A: Infrastructure Setup Complete
- VPC created with public/private subnets
- Security groups configured
- 2 EC2 instances running
- ALB deployed and active
- 2 ASGs configured (CPU and Request-Rate)
- All configuration files saved to infrastructure/

Next: Phase 2B (Application Development)
- Use ALB DNS: experiment-alb-1234567890.us-east-1.elb.amazonaws.com
- Implement load generator, metrics collector, experiment runner
- Develop Flask test application
```

---

## Troubleshooting

### Common Issues

**Issue**: IAM role creation fails with "AccessDenied"
- **Solution**: Verify your AWS credentials have IAM permissions
- **Command**: `aws iam list-roles` (should succeed)

**Issue**: VPC creation fails with "InsufficientAddressSpace"
- **Solution**: Adjust CIDR block in setup_network.py (default: 10.0.0.0/16)
- **Alternative CIDR**: 10.1.0.0/16, 10.2.0.0/16, etc.

**Issue**: ALB health checks show "unhealthy" targets
- **Solution**: Flask app not deployed yet (Phase 3 task)
- **Next Step**: After Phase 2B is complete, Phase 3 will deploy the app

**Issue**: ASG creation fails with "ValidationError"
- **Solution**: Verify EC2 instances and target groups created successfully
- **Command**: `python scripts/verify_infrastructure.py`

### Debugging Commands

```bash
# Check all infrastructure resources
python scripts/verify_infrastructure.py

# Test ALB connectivity
ALB_DNS=$(cat infrastructure/alb-config.json | python -c "import sys, json; print(json.load(sys.stdin)['alb_dns_name'])")
curl http://$ALB_DNS/health  # Will fail until Phase 3 (expected)

# View deployment logs
cat logs/deployment.log

# Check CloudWatch for errors
aws logs describe-log-groups --query 'logGroups[*].logGroupName'
```

---

## Next Steps: Phase 2B

After Phase 2A completion, proceed to Phase 2B (Application Development):

1. **Create Load Generator** (`scripts/load_generator.py`)
2. **Create Metrics Collector** (`scripts/metrics_collector.py`)
3. **Create Experiment Runner** (`scripts/experiment_runner.py`)
4. **Create Flask Test Application** (`apps/test_app/app.py`)

**Phase 2B Output**:
- Functional Python tools for load testing
- Flask application with autoscaling-friendly endpoints
- Docker image for test application

**Phase 2B Deliverables Needed for Phase 3**:
- `scripts/load_generator.py` - Used for load generation
- `scripts/metrics_collector.py` - Used for metrics collection
- `scripts/experiment_runner.py` - Used for orchestration
- `apps/test_app/app.py` - Deployed to EC2 instances
- `apps/test_app/Dockerfile` - Docker image for deployment

---

## Cross-Platform Compatibility

All Phase 2A scripts are designed to work across:
- ✅ Windows
- ✅ macOS
- ✅ Linux

**Key compatibility measures**:
- Use `pathlib.Path` instead of string paths
- Use boto3 (not AWS CLI subprocess calls)
- Use UTF-8 encoding for file I/O
- Handle both `/` and `\` path separators
- No platform-specific binaries

---

## Cost Estimation

Estimated AWS costs for Phase 2A (hourly rates, approximate):

| Resource | Instance Type | Qty | Hourly Cost |
|----------|--------------|-----|------------|
| EC2 Instances | t3.micro | 2 | $0.0104 |
| ALB | Standard | 1 | $0.0225 |
| NAT Gateway | - | 1 | $0.045 |
| **Total** | | | **~$0.08/hour** |

**Note**: Costs increase during Phase 4-5 with active scaling and Phase 6-7 with ongoing monitoring.

---

## Git Commit

Phase 2A infrastructure scripts should be committed with:

```bash
git add scripts/setup_*.py scripts/deploy_all.py scripts/verify_infrastructure.py
git commit -m "feat: Phase 2A infrastructure provisioning scripts

- Add IAM role setup (setup_iam_role.py)
- Add network configuration (setup_network.py)
- Add security group setup (setup_security_groups.py)
- Add ALB configuration (setup_alb.py)
- Add EC2 instance launch (setup_instances.py)
- Add ASG configuration (setup_asg.py)
- Add master deployment orchestration (deploy_all.py)
- Add infrastructure verification (verify_infrastructure.py)
- All scripts use boto3 (cross-platform compatible)
- Generate infrastructure JSON config files"
```

---

## References

- **AWS Documentation**: https://docs.aws.amazon.com/
- **boto3 Reference**: https://boto3.amazonaws.com/v1/documentation/
- **CloudFormation Alternative**: Infrastructure can also be deployed via CloudFormation templates (optional)
- **Phase 2B**: Application Development guide
- **Phase 3**: Deployment to AWS guide

---

**Status**: ✅ Phase 2A Complete

All infrastructure scripts created and verified. Ready for Phase 2B (Application Development).
