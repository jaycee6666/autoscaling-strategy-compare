#!/usr/bin/env python3
"""
Task 4: AWS EC2 Launch Templates Setup
=======================================

Creates EC2 launch templates for CPU-based and request-rate-based autoscaling experiments.

Dependencies:
  - Requires iam-config.json (Instance Profile)
  - Requires security-groups-config.json (Security Group IDs)

Output:
  - infrastructure/launch-templates-config.json

AWS Resources Created:
  - Launch Template: app-cpu-lt (CPU monitoring)
  - Launch Template: app-request-lt (Request-rate monitoring)
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# User data script for CPU monitoring application
USER_DATA_CPU = """#!/bin/bash
set -e
echo "=== Starting CPU Monitoring App Setup ==="

# Update system
yum update -y
yum install -y docker aws-cli awslogs

# Start Docker
systemctl start docker
systemctl enable docker

# Create app directory
mkdir -p /opt/app
cd /opt/app

# Create Python app for CPU monitoring
cat > app_cpu.py << 'EOF'
#!/usr/bin/env python3
import os
import json
import time
import psutil
import boto3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

# CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text

# Start server
server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
print("Health check server started on port 8080")

# Metrics publishing loop
def publish_metrics():
    while True:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            cloudwatch.put_metric_data(
                Namespace='AutoscaleExperiment',
                MetricData=[
                    {
                        'MetricName': 'CPUUsage',
                        'Value': cpu_percent,
                        'Unit': 'Percent',
                        'Dimensions': [
                            {'Name': 'InstanceId', 'Value': instance_id},
                            {'Name': 'Strategy', 'Value': 'CPU'}
                        ]
                    },
                    {
                        'MetricName': 'MemoryUsage',
                        'Value': memory_percent,
                        'Unit': 'Percent',
                        'Dimensions': [
                            {'Name': 'InstanceId', 'Value': instance_id},
                            {'Name': 'Strategy', 'Value': 'CPU'}
                        ]
                    }
                ]
            )
            time.sleep(30)  # Publish every 30 seconds
        except Exception as e:
            print(f"Error publishing metrics: {e}")
            time.sleep(60)

import threading
import requests
metrics_thread = threading.Thread(target=publish_metrics, daemon=True)
metrics_thread.start()

server.serve_forever()
EOF

# Install dependencies
pip3 install psutil requests boto3

# Start app
python3 app_cpu.py &

echo "=== CPU Monitoring App Setup Complete ==="
"""

# User data script for request-rate monitoring
USER_DATA_REQUEST = """#!/bin/bash
set -e
echo "=== Starting Request-Rate Monitoring App Setup ==="

# Update system
yum update -y
yum install -y docker aws-cli awslogs

# Start Docker
systemctl start docker
systemctl enable docker

# Create app directory
mkdir -p /opt/app
cd /opt/app

# Create Python app for request-rate monitoring
cat > app_request.py << 'EOF'
#!/usr/bin/env python3
import os
import json
import time
import threading
import boto3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

request_count = deque(maxlen=60)  # Last 60 seconds
lock = threading.Lock()

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
            self.wfile.write(json.dumps(response).encode())
            
            # Record request
            with lock:
                request_count.append(1)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

# CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
import requests
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text

# Start server
server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
print("Health check server started on port 8080")

# Metrics publishing loop
def publish_metrics():
    while True:
        try:
            with lock:
                request_rate = sum(request_count) / 60.0 if request_count else 0
            
            cloudwatch.put_metric_data(
                Namespace='AutoscaleExperiment',
                MetricData=[
                    {
                        'MetricName': 'RequestRate',
                        'Value': request_rate,
                        'Unit': 'Count/Second',
                        'Dimensions': [
                            {'Name': 'InstanceId', 'Value': instance_id},
                            {'Name': 'Strategy', 'Value': 'RequestRate'}
                        ]
                    }
                ]
            )
            time.sleep(30)  # Publish every 30 seconds
        except Exception as e:
            print(f"Error publishing metrics: {e}")
            time.sleep(60)

metrics_thread = threading.Thread(target=publish_metrics, daemon=True)
metrics_thread.start()

server.serve_forever()
EOF

# Install dependencies
pip3 install requests boto3

# Start app
python3 app_request.py &

echo "=== Request-Rate Monitoring App Setup Complete ==="
"""


class LaunchTemplatesSetup:
    """Manages AWS EC2 Launch Templates."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize EC2 client."""
        self.ec2 = boto3.client("ec2", region_name=region)
        self.region = region
        self.config: Dict[str, Any] = {}

    def load_config(self, config_path: Path) -> Dict[str, str]:
        """Load configuration from JSON file."""
        try:
            logger.info(f"Loading configuration from {config_path}...")
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info("✓ Configuration loaded")
            return config
        except FileNotFoundError:
            logger.error(f"✗ Config not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON: {e}")
            raise

    def get_latest_ami(self) -> str:
        """Get latest Amazon Linux 2 AMI ID."""
        try:
            logger.info("Fetching latest Amazon Linux 2 AMI...")
            response = self.ec2.describe_images(
                Owners=["amazon"],
                Filters=[
                    {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "root-device-type", "Values": ["ebs"]},
                ],
            )

            # Get most recent
            images = sorted(
                response["Images"], key=lambda x: x["CreationDate"], reverse=True
            )

            if not images:
                raise Exception("No Amazon Linux 2 AMI found")

            ami_id = images[0]["ImageId"]
            logger.info(f"✓ Latest AMI: {ami_id}")
            return ami_id
        except ClientError as e:
            logger.error(f"✗ Failed to fetch AMI: {e}")
            raise

    def create_launch_template(
        self,
        template_name: str,
        ami_id: str,
        instance_profile_arn: str,
        security_group_id: str,
        user_data: str,
        strategy: str,
    ) -> str:
        """Create EC2 launch template."""
        try:
            logger.info(f"Creating launch template: {template_name}...")

            # Encode user data (base64)
            import base64

            user_data_encoded = base64.b64encode(user_data.encode()).decode()

            response = self.ec2.create_launch_template(
                LaunchTemplateName=template_name,
                LaunchTemplateData={
                    "ImageId": ami_id,
                    "InstanceType": "t3.micro",
                    "IamInstanceProfile": {"Arn": instance_profile_arn},
                    "SecurityGroupIds": [security_group_id],
                    "UserData": user_data_encoded,
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "VolumeSize": 20,
                                "VolumeType": "gp3",
                                "DeleteOnTermination": True,
                            },
                        }
                    ],
                    "TagSpecifications": [
                        {
                            "ResourceType": "instance",
                            "Tags": [
                                {
                                    "Key": "Name",
                                    "Value": f"autoscale-{strategy}-instance",
                                },
                                {"Key": "Environment", "Value": "experiment"},
                                {"Key": "Strategy", "Value": strategy},
                            ],
                        },
                        {
                            "ResourceType": "volume",
                            "Tags": [
                                {"Key": "Environment", "Value": "experiment"},
                            ],
                        },
                    ],
                    "Monitoring": {
                        "Enabled": True  # Enable detailed CloudWatch monitoring
                    },
                },
            )

            template_id = response["LaunchTemplate"]["LaunchTemplateId"]
            logger.info(f"✓ Launch template created: {template_id}")
            return template_id
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if "AlreadyExists" in error_code or "AlreadyExistsException" in error_code:
                logger.warning(f"⚠ Launch template already exists: {template_name}")
                response = self.ec2.describe_launch_templates(
                    LaunchTemplateNames=[template_name]
                )
                return response["LaunchTemplates"][0]["LaunchTemplateId"]
            logger.error(f"✗ Failed to create launch template: {e}")
            raise

    def setup(self, iam_config: Dict, sg_config: Dict) -> Dict[str, Any]:
        """Execute full launch templates setup."""
        try:
            logger.info("=" * 60)
            logger.info("Starting AWS Launch Templates Setup")
            logger.info("=" * 60)

            # Get latest AMI
            ami_id = self.get_latest_ami()

            instance_profile_arn = iam_config["instance_profile_arn"]
            app_sg_id = sg_config["app_sg_id"]

            # Create CPU monitoring template
            logger.info("\n[1/2] Creating CPU monitoring template...")
            cpu_template_id = self.create_launch_template(
                "app-cpu-lt",
                ami_id,
                instance_profile_arn,
                app_sg_id,
                USER_DATA_CPU,
                "CPU",
            )
            self.config["cpu_template_id"] = cpu_template_id
            self.config["cpu_template_name"] = "app-cpu-lt"

            # Create request-rate monitoring template
            logger.info("\n[2/2] Creating request-rate monitoring template...")
            request_template_id = self.create_launch_template(
                "app-request-lt",
                ami_id,
                instance_profile_arn,
                app_sg_id,
                USER_DATA_REQUEST,
                "RequestRate",
            )
            self.config["request_template_id"] = request_template_id
            self.config["request_template_name"] = "app-request-lt"

            logger.info("=" * 60)
            logger.info("Launch Templates Setup Complete!")
            logger.info("=" * 60)
            logger.info(f"\nConfiguration:\n{json.dumps(self.config, indent=2)}")

            return self.config
        except Exception as e:
            logger.error(f"✗ Setup failed: {e}")
            raise

    def save_config(self, output_path: Path) -> None:
        """Save configuration to JSON file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✓ Configuration saved to: {output_path}")
        except IOError as e:
            logger.error(f"✗ Failed to save configuration: {e}")
            raise


def main():
    """Main entry point."""
    try:
        # Get project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        iam_config_file = project_root / "infrastructure" / "iam-config.json"
        sg_config_file = project_root / "infrastructure" / "security-groups-config.json"
        output_file = project_root / "infrastructure" / "launch-templates-config.json"

        # Load dependencies
        setup = LaunchTemplatesSetup(region="us-east-1")
        iam_config = setup.load_config(iam_config_file)
        sg_config = setup.load_config(sg_config_file)

        # Setup launch templates
        config = setup.setup(iam_config, sg_config)
        setup.save_config(output_file)

        logger.info(f"\n✓ All tasks completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
