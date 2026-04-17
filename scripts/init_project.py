#!/usr/bin/env python3
"""
Phase 0: Project Initialization Script
Sets up project structure, configuration, and validates environment.
"""

import os
import sys
from pathlib import Path
from config_manager import ConfigManager


def create_env_template():
    """Create .env.template file."""
    template_content = """# AWS Configuration
# Get these from AWS IAM console
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Project Configuration
PROJECT_NAME=autoscaling-strategy-compare
PROJECT_ENV=development

# EC2 Configuration
EC2_KEY_PAIR_NAME=autoscaling-project-key
EC2_IMAGE_ID=ami-0c55b159cbfafe1f0
EC2_INSTANCE_TYPE=t3.medium

# VPC Configuration
VPC_CIDR_BLOCK=10.0.0.0/16
SUBNET_CIDR_BLOCK=10.0.1.0/24

# Auto Scaling Configuration
ASG_MIN_SIZE=1
ASG_MAX_SIZE=5
ASG_DESIRED_CAPACITY=2

# Experiment Configuration
EXPERIMENT_DURATION=300
METRIC_COLLECTION_INTERVAL=60
"""

    env_template = Path("config/.env.template")
    env_template.parent.mkdir(parents=True, exist_ok=True)

    if not env_template.exists():
        env_template.write_text(template_content)
        print(f"✓ Created {env_template}")
    else:
        print(f"ℹ️  {env_template} already exists")


def create_yaml_config():
    """Create config.yaml template."""
    yaml_content = """# Project Configuration
project:
  name: autoscaling-strategy-compare
  description: Comparative Analysis of Autoscaling Strategies
  team:
    - WU Wanpeng
    - CHEN Sijie
  deadline: 2026-04-24

# Infrastructure Configuration
infrastructure:
  vpc:
    cidr: "10.0.0.0/16"
    name: "autoscaling-vpc"
  
  subnets:
    - name: "public-subnet-1"
      cidr: "10.0.1.0/24"
      az: "us-east-1a"
    - name: "public-subnet-2"
      cidr: "10.0.2.0/24"
      az: "us-east-1b"
  
  security_groups:
    - name: "alb-sg"
      description: "Security group for ALB"
      ingress_rules:
        - protocol: tcp
          from_port: 80
          to_port: 80
          cidr: "0.0.0.0/0"
        - protocol: tcp
          from_port: 443
          to_port: 443
          cidr: "0.0.0.0/0"
    
    - name: "app-sg"
      description: "Security group for application"
      ingress_rules:
        - protocol: tcp
          from_port: 5000
          to_port: 5000
          source_group: "alb-sg"

# Application Configuration
application:
  name: flask-autoscaling-app
  port: 5000
  workers: 4

# Experiment Configuration
experiments:
  scenario_a:
    name: "Resource-Based CPU Utilization"
    duration: 600
    load_pattern: "gradual_increase"
  
  scenario_b:
    name: "Workload-Based Request Rate"
    duration: 600
    load_pattern: "spike_pattern"

# Monitoring Configuration
monitoring:
  cloudwatch:
    enabled: true
    metrics_collection_interval: 60
  
  custom_metrics:
    - name: "RequestCount"
      unit: "Count"
    - name: "ResponseTime"
      unit: "Milliseconds"
    - name: "CPUUtilization"
      unit: "Percent"

# Data Collection Configuration
data:
  output_dir: "data"
  experiment_results_dir: "data/experiments"
  metrics_dir: "data/metrics"
  analysis_dir: "data/analysis"
  retention_days: 30
"""

    config_file = Path("config/config.yaml")
    config_file.parent.mkdir(parents=True, exist_ok=True)

    if not config_file.exists():
        config_file.write_text(yaml_content)
        print(f"✓ Created {config_file}")
    else:
        print(f"ℹ️  {config_file} already exists")


def create_data_directories():
    """Create data collection directories."""
    data_dirs = ["data/experiments", "data/metrics", "data/analysis", "logs"]

    for directory in data_dirs:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")


def setup_gitkeep():
    """Add .gitkeep files to preserve empty directories."""
    keep_dirs = ["data/experiments", "data/metrics", "data/analysis", "logs"]

    for directory in keep_dirs:
        gitkeep = Path(directory) / ".gitkeep"
        gitkeep.parent.mkdir(parents=True, exist_ok=True)
        gitkeep.touch()
        print(f"✓ Created {gitkeep}")


def initialize_project():
    """Run all initialization steps."""
    print("\n" + "=" * 60)
    print("PROJECT INITIALIZATION")
    print("=" * 60 + "\n")

    print("📋 Setting up configuration...")
    create_env_template()
    create_yaml_config()

    print("\n📁 Creating data directories...")
    create_data_directories()
    setup_gitkeep()

    print("\n✨ Initializing configuration manager...")
    config = ConfigManager()
    config.print_summary()

    print("\n" + "=" * 60)
    print("✅ PROJECT INITIALIZATION COMPLETE")
    print("=" * 60)

    print("\n📝 Next Steps:")
    print("  1. Edit config/.env with your AWS credentials")
    print("  2. Run: python scripts/check_environment.py")
    print("  3. Run: python scripts/deploy_all.py")
    print("\n")


if __name__ == "__main__":
    try:
        initialize_project()
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
