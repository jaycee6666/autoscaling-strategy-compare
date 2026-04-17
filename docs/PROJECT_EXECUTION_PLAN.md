# 项目执行计划 (跨平台版本)

> ⚠️ **注意**: 这是项目开始时制定的**原始执行计划**。
> 
> 有关**当前执行计划**，请参阅 [`PROJECT_EXECUTION_ROADMAP.md`](./PROJECT_EXECUTION_ROADMAP.md)。
> 
> 新的执行路线图基于 Phase 1 完成情况进行了优化，但仍保持 2026 年 4 月 24 日的截止日期。此文档保留供参考和审计跟踪。

---

**项目名称**: Comparative Analysis of Autoscaling Strategies: Resource-Based CPU Utilization vs. Workload-Based Request Rate

**执行方式**: 本地 AWS CLI（Windows/macOS/Linux）

**总时长**: 约8-10周（从现在到2026年4月24日）

**平台支持**: ✅ Windows ✅ macOS ✅ Linux

---

## ⚡ 快速开始（所有平台通用）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd autoscaling-project

# 2. 运行环境检查脚本
python scripts/check_environment.py

# 3. 运行初始化脚本
python scripts/init_project.py

# 4. 按照Phase 1开始工作
```

---

## 总体时间轴

```
Week 1-2:   环境准备 & AWS基础设施代码
Week 3:     应用开发 & 本地测试
Week 4:     部署到AWS & 验证
Week 5-6:   实验执行 & 数据收集
Week 7:     数据分析 & 报告撰写
Week 8-9:   报告完善 & 演示视频制作
Week 10:    最终检查 & 提交
```

---

## Phase 0: 跨平台环境检查与初始化 (必做) ⭐

**现在已经完全自动化！**只需一个命令启动整个项目。

### 0.0 快速启动（推荐）

所有平台使用相同的命令：

```bash
python setup.py
```

**会自动执行以下所有步骤:**
- ✅ 创建 Python 虚拟环境（隔离的Python环境）
- ✅ 安装项目依赖包（boto3, AWS CLI集成等）
- ✅ 验证系统环境（Python版本、AWS CLI、Git等）
- ✅ 初始化项目配置文件
- ✅ 检查AWS凭证
- ✅ 显示激活说明

**就这样!** 环境已准备好，跳到 Phase 1

**了解更多**: 详见 `docs/VIRTUAL_ENVIRONMENT.md` 和 `docs/GETTING_STARTED.md`

---

### 0.1 虚拟环境设置（自动创建）

`setup.py` 会为你创建虚拟环境，但你需要了解它是什么：

#### 什么是虚拟环境？
- 隔离的 Python 环境，与系统 Python 完全分离
- 项目特定的依赖包不会影响其他项目
- 每个团队成员有自己的环境副本
- 跨平台一致性（Windows/macOS/Linux 行为完全相同）

#### 虚拟环境位置
```
autoscaling-strategy-compare/
├── venv/                    # 虚拟环境目录（已在 .gitignore 中）
│   ├── bin/                 # macOS/Linux 可执行文件
│   │   ├── python
│   │   ├── pip
│   │   ├── activate         # 激活脚本
│   │   └── ...
│   ├── Scripts/             # Windows 可执行文件
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   ├── activate.bat
│   │   └── ...
│   ├── lib/                 # Python 包安装目录
│   └── pyvenv.cfg
├── setup.py                 # 自动创建虚拟环境的脚本
├── requirements.txt         # 项目依赖列表
└── ...
```

#### 依赖包（安装在虚拟环境中）
```txt
boto3>=1.18.0               # AWS SDK for Python
botocore>=1.21.0            # boto3 依赖
python-dotenv>=0.19.0       # 环境变量管理
pyyaml>=5.4                 # YAML 文件解析
requests>=2.26.0            # HTTP 请求库
```

---

### 0.2 环境检查脚本

```python
# scripts/check_environment.py
"""
跨平台环境检查脚本
适用于: Windows, macOS, Linux
"""

import platform
import subprocess
import sys
import json
from pathlib import Path

class EnvironmentChecker:
    def __init__(self):
        self.results = {}
        self.os_type = platform.system()
        self.failures = []
    
    def check_python(self):
        """检查Python版本"""
        version = platform.python_version()
        major, minor, _ = map(int, version.split('.'))
        
        if major == 3 and minor >= 9:
            self.results['Python'] = {'status': '✓', 'version': version}
        else:
            self.failures.append(f"Python 3.9+ required, found {version}")
            self.results['Python'] = {'status': '✗', 'version': version}
    
    def check_command(self, cmd, name):
        """检查命令是否可用"""
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                self.results[name] = {'status': '✓', 'version': version}
                return True
            else:
                self.results[name] = {'status': '✗', 'reason': 'Command failed'}
                self.failures.append(f"{name} not available or version check failed")
                return False
        except FileNotFoundError:
            self.results[name] = {'status': '✗', 'reason': 'Not found'}
            self.failures.append(f"{name} not installed")
            return False
        except Exception as e:
            self.results[name] = {'status': '✗', 'reason': str(e)}
            self.failures.append(f"Error checking {name}: {e}")
            return False
    
    def check_aws_credentials(self):
        """检查AWS凭证"""
        try:
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity', '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                identity = json.loads(result.stdout)
                self.results['AWS Credentials'] = {
                    'status': '✓',
                    'account': identity.get('Account'),
                    'user': identity.get('UserId')
                }
                return True
            else:
                self.results['AWS Credentials'] = {'status': '✗', 'reason': 'Not configured'}
                self.failures.append("AWS credentials not configured. Run: aws configure")
                return False
        except Exception as e:
            self.results['AWS Credentials'] = {'status': '✗', 'reason': str(e)}
            self.failures.append(f"Error checking AWS credentials: {e}")
            return False
    
    def check_git(self):
        """检查Git配置"""
        try:
            # 检查git命令
            self.check_command('git', 'Git')
            
            # 检查git配置
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.failures.append("Git user not configured. Run: git config user.name 'Your Name'")
            
            return result.returncode == 0
        except Exception as e:
            self.failures.append(f"Git check failed: {e}")
            return False
    
    def run_all_checks(self):
        """运行所有检查"""
        print(f"\n{'='*60}")
        print(f"Environment Check - {self.os_type}")
        print(f"{'='*60}\n")
        
        # 基本检查
        self.check_python()
        self.check_command('git', 'Git')
        self.check_command('aws', 'AWS CLI')
        self.check_command('python', 'Python Executable')
        self.check_command('pip', 'pip')
        
        # AWS特定检查
        self.check_aws_credentials()
        self.check_git()
        
        # 打印结果
        print("检查结果:\n")
        for name, result in self.results.items():
            status = result['status']
            print(f"{status} {name:20s} {result.get('version', result.get('reason', ''))}")
        
        # 打印失败信息和建议
        if self.failures:
            print(f"\n{'!'*60}")
            print("需要修复的问题:")
            print(f"{'!'*60}\n")
            for i, failure in enumerate(self.failures, 1):
                print(f"{i}. {failure}")
            return False
        else:
            print(f"\n{'✓'*60}")
            print("✓ 所有环境检查通过！可以开始项目")
            print(f"{'✓'*60}\n")
            return True

if __name__ == '__main__':
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
```

### 0.3 项目初始化脚本

```python
# scripts/init_project.py
"""
跨平台项目初始化脚本
创建必要的目录结构和配置文件
"""

import os
import sys
import json
from pathlib import Path

class ProjectInitializer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.dirs_to_create = [
            'infrastructure',
            'application',
            'load-testing',
            'data-collection',
            'results',
            'report',
            'docs',
            'scripts/platform-specific',
            'config',
            'logs'
        ]
    
    def create_directories(self):
        """创建项目目录结构"""
        print("Creating directory structure...")
        for dir_path in self.dirs_to_create:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {dir_path}")
    
    def create_gitignore(self):
        """创建 .gitignore 文件"""
        gitignore_content = """
# Environment variables
.env
.env.local
*.pem
autoscaling-key.pem

# AWS CLI outputs
infrastructure/*-config.sh
infrastructure/*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Results and data
results/*
!results/.gitkeep
logs/*
!logs/.gitkeep

# Report drafts
report/*
!report/.gitkeep

# Node modules (if using)
node_modules/

# OS
.DS_Store
Thumbs.db
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db

# AWS costs - DO NOT TRACK
*.cost
cost-estimates.txt
"""
        gitignore_path = self.project_root / '.gitignore'
        gitignore_path.write_text(gitignore_content.strip())
        print(f"✓ Created .gitignore")
    
    def create_config_template(self):
        """创建配置模板"""
        config_template = {
            "project": {
                "name": "Autoscaling Comparison",
                "group_id": "GROUP_X",
                "members": [
                    {"name": "Member 1", "student_id": "XXXX"}
                ]
            },
            "aws": {
                "region": "us-east-1",
                "instance_type": "t2.micro",
                "max_instances": 5,
                "min_instances": 1,
                "desired_instances": 2
            },
            "experiment": {
                "duration_seconds": 600,
                "warmup_seconds": 60,
                "cooldown_seconds": 120
            },
            "budget": {
                "estimated_cost": "50-100",
                "currency": "USD",
                "cleanup_after_experiment": True
            }
        }
        
        config_path = self.project_root / 'config' / 'project_config.json'
        with open(config_path, 'w') as f:
            json.dump(config_template, f, indent=2)
        
        print(f"✓ Created config/project_config.json (请编辑此文件)")
    
    def create_readme(self):
        """创建README"""
        readme_content = """# Autoscaling Comparison Project

## 快速开始

### 1. 环境检查
\`\`\`bash
python scripts/check_environment.py
\`\`\`

### 2. 项目初始化
\`\`\`bash
python scripts/init_project.py
\`\`\`

### 3. 配置项目
编辑 `config/project_config.json` 填入你的信息

### 4. 部署基础设施
详见 PROJECT_EXECUTION_PLAN.md Phase 1-2

## 目录结构

- `infrastructure/` - AWS基础设施脚本和配置
- `application/` - Flask应用代码
- `load-testing/` - 负载测试脚本
- `data-collection/` - 数据收集和分析脚本
- `results/` - 实验结果
- `report/` - 最终报告
- `scripts/` - 工具脚本
- `config/` - 项目配置

## 跨平台注意事项

### Windows用户
- 使用 Python 脚本而不是 bash 脚本
- 路径使用 `\\` 或在Python中使用 `pathlib`
- 使用 `cmd.exe` 或 PowerShell

### macOS/Linux用户
- 可直接使用bash脚本
- 确保脚本有执行权限: `chmod +x scripts/*.sh`

## 联系方式

如有问题，请在GitHub Issues中提出
"""
        readme_path = self.project_root / 'README.md'
        readme_path.write_text(readme_content)
        print(f"✓ Created README.md")
    
    def create_platform_specific_templates(self):
        """创建平台特定的模板"""
        import platform
        
        platform_name = platform.system()
        
        # Windows batch文件示例
        if platform_name == 'Windows' or True:  # 总是创建
            batch_template = """@echo off
REM 跨平台脚本示例 - Windows版本
REM 该脚本从Python脚本调用，保持一致性

python scripts/deploy_infrastructure.py

if %errorlevel% neq 0 (
    echo Error during deployment
    exit /b 1
)

echo Deployment successful
"""
            batch_path = self.project_root / 'scripts/platform-specific/deploy.bat'
            batch_path.write_text(batch_template)
            print(f"✓ Created scripts/platform-specific/deploy.bat")
        
        # Bash脚本示例
        bash_template = """#!/bin/bash
# 跨平台脚本示例 - Linux/macOS版本
# 该脚本从Python脚本调用，保持一致性

python scripts/deploy_infrastructure.py

if [ $? -ne 0 ]; then
    echo "Error during deployment"
    exit 1
fi

echo "Deployment successful"
"""
            bash_path = self.project_root / 'scripts/platform-specific/deploy.sh'
            bash_path.write_text(bash_template)
            bash_path.chmod(0o755)
            print(f"✓ Created scripts/platform-specific/deploy.sh")
    
    def run_init(self):
        """运行初始化"""
        print(f"\n{'='*60}")
        print("Project Initialization")
        print(f"{'='*60}\n")
        
        self.create_directories()
        self.create_gitignore()
        self.create_config_template()
        self.create_readme()
        self.create_platform_specific_templates()
        
        print(f"\n{'✓'*60}")
        print("✓ 项目初始化完成！")
        print("后续步骤:")
        print("  1. 编辑 config/project_config.json")
        print("  2. 编辑 .env 添加AWS凭证（可选）")
        print("  3. 参考 PROJECT_EXECUTION_PLAN.md Phase 1")
        print(f"{'✓'*60}\n")

if __name__ == '__main__':
    initializer = ProjectInitializer()
    initializer.run_init()
```

### 0.4 一键部署脚本（跨平台）

```python
# scripts/deploy_infrastructure.py
"""
跨平台基础设施部署脚本
自动检测平台并执行相应操作
"""

import platform
import subprocess
import sys
import os
import json
from pathlib import Path

class CrossPlatformDeployer:
    def __init__(self):
        self.os_type = platform.system()
        self.project_root = Path.cwd()
        self.config_path = self.project_root / 'config' / 'project_config.json'
        self.load_config()
    
    def load_config(self):
        """加载项目配置"""
        with open(self.config_path) as f:
            self.config = json.load(f)
    
    def run_command(self, cmd, description=""):
        """跨平台运行命令"""
        print(f"\n{'─'*60}")
        print(f"执行: {description or ' '.join(cmd)}")
        print(f"{'─'*60}")
        
        try:
            if isinstance(cmd, str):
                # Shell命令
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.project_root
                )
            else:
                # 列表命令
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root
                )
            
            if result.returncode != 0:
                print(f"✗ 命令失败: {description}")
                return False
            
            print(f"✓ 成功: {description}")
            return True
        except Exception as e:
            print(f"✗ 执行错误: {e}")
            return False
    
    def deploy(self):
        """执行部署"""
        print(f"\n{'='*60}")
        print(f"开始部署 (平台: {self.os_type})")
        print(f"{'='*60}")
        
        steps = [
            ("创建网络配置", "python scripts/setup_network.py"),
            ("创建安全组", "python scripts/setup_security_groups.py"),
            ("设置IAM角色", "python scripts/setup_iam_role.py"),
            ("创建ALB", "python scripts/setup_alb.py"),
            ("创建AMI", "python scripts/create_ami.py"),
            ("创建ASG", "python scripts/setup_asg.py"),
        ]
        
        for description, cmd in steps:
            if not self.run_command(cmd, description):
                print(f"\n✗ 部署在 '{description}' 步骤失败")
                return False
        
        print(f"\n{'✓'*60}")
        print("✓ 部署完成!")
        print(f"{'✓'*60}\n")
        return True

if __name__ == '__main__':
    deployer = CrossPlatformDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)
```

---

## Phase 1: 环境准备 (Week 1-2) - 跨平台

### 1.1 所有平台通用步骤

#### 步骤1：克隆或初始化项目
```bash
# 如果是新项目
git init autoscaling-project
cd autoscaling-project

# 如果克隆已有项目
git clone <repo-url>
cd autoscaling-project
```

#### 步骤2：运行环境检查
```bash
# 所有平台通用
python scripts/check_environment.py

# 预期输出应该都是 ✓
```

#### 步骤3：安装依赖

**使用统一的 requirements.txt（所有平台相同）**

```
# requirements.txt
boto3==1.28.0
botocore==1.31.0
locust==2.15.1
flask==2.3.2
gunicorn==21.2.0
requests==2.31.0
pandas==2.0.3
matplotlib==3.7.2
jinja2==3.1.2
click==8.1.3
pyyaml==6.0
python-dotenv==1.0.0
```

```bash
# 所有平台执行相同命令
pip install -r requirements.txt
```

#### 步骤4：项目初始化
```bash
# 所有平台通用
python scripts/init_project.py
```

#### 步骤5：配置AWS凭证

**方式A: 交互式配置（所有平台通用）**
```bash
aws configure
# 输入:
# AWS Access Key ID: xxx
# AWS Secret Access Key: xxx
# Default region: us-east-1
# Default output format: json
```

**方式B: 使用环境变量（推荐用于多人协作）**

创建 `.env` 文件（**不要提交到git**）：
```
# .env (Windows/Linux/macOS通用)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_DEFAULT_OUTPUT=json
```

或通过 Python 加载环境变量：
```python
# scripts/load_aws_credentials.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
env_file = Path.cwd() / '.env'
if env_file.exists():
    load_dotenv(env_file)

# 验证凭证
def verify_credentials():
    required = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing = [key for key in required if not os.getenv(key)]
    
    if missing:
        print(f"✗ 缺少环境变量: {', '.join(missing)}")
        return False
    
    print("✓ AWS凭证已加载")
    return True
```

#### 步骤6：编辑项目配置
```bash
# 编辑配置文件（所有平台通用）
# Windows: notepad config/project_config.json
# macOS: open config/project_config.json
# Linux: nano config/project_config.json
# 或使用任何文本编辑器
```

修改内容：
```json
{
  "project": {
    "group_id": "Group_1",
    "members": [
      {"name": "WU Wanpeng", "student_id": "1234567"},
      {"name": "CHEN Sijie", "student_id": "1234568"}
    ]
  },
  "aws": {
    "region": "us-east-1"
  }
}
```

### 1.2 平台特定的安装（仅需一次）

#### Windows用户

```powershell
# 如果还没安装Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装jq（用于JSON处理）
choco install jq

# 验证
jq --version
```

#### macOS用户

```bash
# 使用Homebrew
brew install jq

# 验证
jq --version
```

#### Linux用户

```bash
# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq

# 验证
jq --version
```

### 1.3 Git配置（每个成员执行一次）

```bash
# 所有平台通用
git config user.name "Your Full Name"
git config user.email "your.email@university.edu"

# 验证
git config user.name
git config user.email

# （可选）设置为全局配置
git config --global user.name "Your Full Name"
git config --global user.email "your.email@university.edu"
```

### 1.4 首次提交（项目管理员执行）

```bash
# 添加所有文件
git add .

# 提交
git commit -m "Initial project setup with cross-platform support"

# 推送到远程（假设已添加remote）
git push -u origin main
```

### 1.5 验证所有成员环境

**项目管理员（推荐）**：创建环境检查报告

```python
# scripts/verify_team_setup.py
"""
验证所有团队成员的环境设置
可在Google Sheets或GitHub中收集
"""

import json
from pathlib import Path

def collect_environment_info():
    """收集环境信息"""
    info = {
        'member_name': input("Name: "),
        'python_version': input("Python version (python --version): "),
        'aws_cli_version': input("AWS CLI version (aws --version): "),
        'git_version': input("Git version (git --version): "),
        'os': input("OS (Windows/macOS/Linux): "),
        'issues': input("Any issues encountered (optional): ")
    }
    
    return info

if __name__ == '__main__':
    team_info = []
    num_members = int(input("Number of team members: "))
    
    for i in range(num_members):
        print(f"\n--- Member {i+1} ---")
        team_info.append(collect_environment_info())
    
    # 保存报告
    report_path = Path('config/team_setup_report.json')
    with open(report_path, 'w') as f:
        json.dump(team_info, f, indent=2)
    
    print(f"\n✓ 报告已保存到 {report_path}")
```

### 1.6 共享脚本和工具

**所有基础设施脚本都用Python编写（跨平台兼容）**

```python
# scripts/aws_utils.py
"""
AWS CLI 包装器 - 跨平台兼容
所有AWS操作都通过Python实现，而不是Bash
"""

import subprocess
import json
import sys
import os
from typing import Dict, List, Any, Optional

class AWSCLIWrapper:
    """AWS CLI 的Python包装器"""
    
    @staticmethod
    def run_aws_command(
        service: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        region: str = None
    ) -> Dict[str, Any]:
        """
        运行AWS CLI命令 (跨平台)
        
        Args:
            service: AWS服务 (如 'ec2', 'autoscaling')
            operation: 操作名称 (如 'describe-instances')
            params: 参数字典
            region: AWS区域
        
        Returns:
            命令输出的JSON解析结果
        """
        
        cmd = ['aws', service, operation]
        
        if region:
            cmd.extend(['--region', region])
        
        # 添加参数
        if params:
            for key, value in params.items():
                if isinstance(value, list):
                    cmd.append(f'--{key}')
                    cmd.extend(value)
                elif isinstance(value, bool):
                    if value:
                        cmd.append(f'--{key}')
                else:
                    cmd.append(f'--{key}')
                    cmd.append(str(value))
        
        cmd.extend(['--output', 'json'])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            return {}
        
        except subprocess.CalledProcessError as e:
            print(f"✗ AWS CLI 错误: {e.stderr}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析错误: {e}")
            sys.exit(1)
    
    @staticmethod
    def create_vpc(cidr_block: str, region: str) -> str:
        """创建VPC"""
        result = AWSCLIWrapper.run_aws_command(
            'ec2',
            'create-vpc',
            {
                'cidr-block': cidr_block,
                'tag-specifications': f'ResourceType=vpc,Tags=[{{Key=Name,Value=autoscaling-vpc}}]'
            },
            region=region
        )
        return result['Vpc']['VpcId']
    
    @staticmethod
    def create_subnet(vpc_id: str, cidr_block: str, az: str, region: str) -> str:
        """创建子网"""
        result = AWSCLIWrapper.run_aws_command(
            'ec2',
            'create-subnet',
            {
                'vpc-id': vpc_id,
                'cidr-block': cidr_block,
                'availability-zone': az
            },
            region=region
        )
        return result['Subnet']['SubnetId']
    
    @staticmethod
    def create_security_group(name: str, description: str, vpc_id: str, region: str) -> str:
        """创建安全组"""
        result = AWSCLIWrapper.run_aws_command(
            'ec2',
            'create-security-group',
            {
                'group-name': name,
                'description': description,
                'vpc-id': vpc_id
            },
            region=region
        )
        return result['GroupId']
    
    # 更多方法...

# 使用示例
if __name__ == '__main__':
    wrapper = AWSCLIWrapper()
    
    # 创建VPC
    vpc_id = wrapper.create_vpc(
        cidr_block='10.0.0.0/16',
        region='us-east-1'
    )
    print(f"✓ VPC Created: {vpc_id}")
```

## Phase 2: AWS基础设施代码编写 (Week 1-2) - 完全跨平台

所有基础设施脚本都用 **Python** 编写，确保 Windows/macOS/Linux 完全兼容。

### 2.1 基础设施Python脚本

#### 脚本1：网络设置 (setup_network.py)

```python
# scripts/setup_network.py
"""
创建AWS VPC网络基础设施
支持: Windows, macOS, Linux
"""

import json
from pathlib import Path
from scripts.aws_utils import AWSCLIWrapper

class NetworkSetup:
    def __init__(self, config_path='config/project_config.json', region='us-east-1'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.region = region
        self.aws = AWSCLIWrapper()
        self.outputs = {}
    
    def create_vpc(self):
        """创建VPC"""
        print("创建VPC...")
        vpc_id = self.aws.create_vpc(
            cidr_block='10.0.0.0/16',
            region=self.region
        )
        self.outputs['VPC_ID'] = vpc_id
        print(f"✓ VPC Created: {vpc_id}")
        return vpc_id
    
    def create_subnets(self, vpc_id):
        """创建子网"""
        print("创建子网...")
        
        subnets = {}
        azs = ['us-east-1a', 'us-east-1b']
        
        for i, az in enumerate(azs, 1):
            subnet_id = self.aws.create_subnet(
                vpc_id=vpc_id,
                cidr_block=f'10.0.{i}.0/24',
                az=az,
                region=self.region
            )
            subnets[f'SUBNET_{i}'] = subnet_id
            print(f"✓ Subnet Created in {az}: {subnet_id}")
        
        self.outputs.update(subnets)
        return subnets
    
    def create_internet_gateway(self, vpc_id):
        """创建Internet Gateway"""
        print("创建Internet Gateway...")
        
        result = self.aws.run_aws_command(
            'ec2',
            'create-internet-gateway',
            {'tag-specifications': 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=autoscaling-igw}]'},
            region=self.region
        )
        
        igw_id = result['InternetGateway']['InternetGatewayId']
        self.outputs['IGW_ID'] = igw_id
        
        # 附加到VPC
        self.aws.run_aws_command(
            'ec2',
            'attach-internet-gateway',
            {'internet-gateway-id': igw_id, 'vpc-id': vpc_id},
            region=self.region
        )
        
        print(f"✓ IGW Created and attached: {igw_id}")
        return igw_id
    
    def setup_routing(self, vpc_id, igw_id, subnets):
        """配置路由表"""
        print("配置路由表...")
        
        result = self.aws.run_aws_command(
            'ec2',
            'create-route-table',
            {'vpc-id': vpc_id, 'tag-specifications': 'ResourceType=route-table,Tags=[{Key=Name,Value=autoscaling-rt}]'},
            region=self.region
        )
        
        rt_id = result['RouteTable']['RouteTableId']
        
        # 添加默认路由
        self.aws.run_aws_command(
            'ec2',
            'create-route',
            {
                'route-table-id': rt_id,
                'destination-cidr-block': '0.0.0.0/0',
                'gateway-id': igw_id
            },
            region=self.region
        )
        
        # 关联到所有子网
        for subnet_id in subnets.values():
            self.aws.run_aws_command(
                'ec2',
                'associate-route-table',
                {'route-table-id': rt_id, 'subnet-id': subnet_id},
                region=self.region
            )
        
        self.outputs['RT_ID'] = rt_id
        print(f"✓ Routing Table Created: {rt_id}")
    
    def save_outputs(self):
        """保存输出到文件"""
        output_path = Path('infrastructure/network-config.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.outputs, f, indent=2)
        
        print(f"\n✓ 配置已保存到: {output_path}")
        print(json.dumps(self.outputs, indent=2))
    
    def run(self):
        """执行完整设置"""
        print(f"\n{'='*60}")
        print("Network Setup (跨平台)")
        print(f"{'='*60}\n")
        
        vpc_id = self.create_vpc()
        subnets = self.create_subnets(vpc_id)
        igw_id = self.create_internet_gateway(vpc_id)
        self.setup_routing(vpc_id, igw_id, subnets)
        self.save_outputs()
        
        print(f"\n{'✓'*60}")
        print("✓ 网络设置完成!")
        print(f"{'✓'*60}\n")

if __name__ == '__main__':
    setup = NetworkSetup()
    setup.run()
```

#### 脚本2：安全组设置 (setup_security_groups.py)

```python
# scripts/setup_security_groups.py
"""
创建安全组
支持: Windows, macOS, Linux
"""

import json
from pathlib import Path
from scripts.aws_utils import AWSCLIWrapper

class SecurityGroupSetup:
    def __init__(self, config_path='infrastructure/network-config.json', region='us-east-1'):
        with open(config_path) as f:
            self.network_config = json.load(f)
        
        self.region = region
        self.aws = AWSCLIWrapper()
        self.outputs = {}
    
    def create_alb_sg(self, vpc_id):
        """创建ALB安全组"""
        print("创建ALB安全组...")
        
        sg_id = self.aws.create_security_group(
            name='autoscaling-alb-sg',
            description='Security group for ALB',
            vpc_id=vpc_id,
            region=self.region
        )
        
        # 允许HTTP
        self.aws.run_aws_command(
            'ec2',
            'authorize-security-group-ingress',
            {
                'group-id': sg_id,
                'protocol': 'tcp',
                'port': '80',
                'cidr': '0.0.0.0/0'
            },
            region=self.region
        )
        
        self.outputs['ALB_SG'] = sg_id
        print(f"✓ ALB Security Group Created: {sg_id}")
        return sg_id
    
    def create_ec2_sg(self, vpc_id, alb_sg_id):
        """创建EC2安全组"""
        print("创建EC2安全组...")
        
        sg_id = self.aws.create_security_group(
            name='autoscaling-ec2-sg',
            description='Security group for EC2 instances',
            vpc_id=vpc_id,
            region=self.region
        )
        
        # 允许来自ALB的流量
        self.aws.run_aws_command(
            'ec2',
            'authorize-security-group-ingress',
            {
                'group-id': sg_id,
                'protocol': 'tcp',
                'port': '5000',
                'source-group': alb_sg_id
            },
            region=self.region
        )
        
        self.outputs['EC2_SG'] = sg_id
        print(f"✓ EC2 Security Group Created: {sg_id}")
        return sg_id
    
    def save_outputs(self):
        """保存输出"""
        output_path = Path('infrastructure/security-group-config.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.outputs, f, indent=2)
        
        print(f"\n✓ 配置已保存到: {output_path}\n")
    
    def run(self):
        """执行"""
        print(f"\n{'='*60}")
        print("Security Group Setup (跨平台)")
        print(f"{'='*60}\n")
        
        vpc_id = self.network_config['VPC_ID']
        alb_sg = self.create_alb_sg(vpc_id)
        ec2_sg = self.create_ec2_sg(vpc_id, alb_sg)
        self.save_outputs()

if __name__ == '__main__':
    setup = SecurityGroupSetup()
    setup.run()
```

#### 脚本3：一键部署脚本

```python
# scripts/deploy_all.py
"""
一键部署所有基础设施
自动按顺序执行所有设置脚本
支持: Windows, macOS, Linux
"""

import sys
from pathlib import Path
from scripts.setup_network import NetworkSetup
from scripts.setup_security_groups import SecurityGroupSetup
from scripts.setup_iam_role import IAMSetup
from scripts.setup_alb import ALBSetup
from scripts.create_ami import AMICreation
from scripts.setup_asg import ASGSetup

class InfrastructureDeployer:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.steps = [
            ('Network Setup', NetworkSetup),
            ('Security Groups', SecurityGroupSetup),
            ('IAM Roles', IAMSetup),
            ('ALB Setup', ALBSetup),
            ('AMI Creation', AMICreation),
            ('ASG Setup', ASGSetup),
        ]
    
    def deploy(self):
        """执行完整部署"""
        print(f"\n{'='*60}")
        print("🚀 Infrastructure Deployment (跨平台)")
        print(f"{'='*60}\n")
        
        for i, (name, SetupClass) in enumerate(self.steps, 1):
            print(f"\n[{i}/{len(self.steps)}] {name}")
            print(f"{'─'*60}")
            
            try:
                setup = SetupClass(region=self.region)
                setup.run()
            except Exception as e:
                print(f"\n✗ 部署失败: {name}")
                print(f"错误: {e}")
                return False
        
        print(f"\n{'✓'*60}")
        print("✓ 所有基础设施部署完成!")
        print(f"{'✓'*60}\n")
        
        # 生成总结报告
        self.generate_summary()
        return True
    
    def generate_summary(self):
        """生成部署总结"""
        config_files = [
            'infrastructure/network-config.json',
            'infrastructure/security-group-config.json',
            'infrastructure/iam-config.json',
            'infrastructure/alb-config.json',
            'infrastructure/asg-config.json',
        ]
        
        print("\n配置文件已生成:")
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"  ✓ {config_file}")
        
        print("\n下一步:")
        print("  1. 验证所有资源: aws ec2 describe-vpcs")
        print("  2. 获取ALB DNS: cat infrastructure/alb-config.json")
        print("  3. 运行负载测试: python load-testing/run_experiment.py")

if __name__ == '__main__':
    deployer = InfrastructureDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)
```

### 2.2 共享配置管理

```python
# scripts/config_manager.py
"""
集中配置管理 - 避免重复定义
所有环境变量和配置都在这里管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigManager:
    """配置管理器 - 跨平台"""
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 项目配置
        self.project_config = self._load_json('config/project_config.json')
        
        # AWS配置
        self.aws_config = {
            'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        }
        
        # 实验配置
        self.experiment_config = self._load_json('config/project_config.json').get('experiment', {})
    
    @staticmethod
    def _load_json(path: str) -> Dict[str, Any]:
        """跨平台加载JSON"""
        config_path = Path(path)
        if not config_path.exists():
            print(f"✗ Config file not found: {path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_aws_region(self) -> str:
        """获取AWS区域"""
        return self.aws_config['region']
    
    def get_experiment_duration(self) -> int:
        """获取实验时长"""
        return self.experiment_config.get('duration_seconds', 600)
    
    def get_group_info(self) -> Dict[str, Any]:
        """获取小组信息"""
        return self.project_config.get('project', {})
    
    def print_config(self):
        """打印配置概览"""
        print("\n📋 配置概览")
        print(f"{'─'*60}")
        print(f"Group ID: {self.get_group_info().get('group_id')}")
        print(f"Members: {len(self.get_group_info().get('members', []))}")
        print(f"AWS Region: {self.get_aws_region()}")
        print(f"Experiment Duration: {self.get_experiment_duration()}s")
        print(f"{'─'*60}\n")

# 全局配置实例
CONFIG = ConfigManager()
```

---

## Phase 3: 应用开发 & 本地测试 (Week 2-3) - 跨平台

### 3.1 跨平台Flask应用

```python
# application/app.py
"""
Flask应用 - 完全跨平台
支持: Windows, macOS, Linux
"""

from flask import Flask, jsonify, request
import time
import threading
import os
import logging
from datetime import datetime
from pathlib import Path

# 配置日志 (跨平台)
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

class WorkloadSimulator:
    def __init__(self):
        self.processing_time = float(os.getenv('PROCESSING_TIME', '0.5'))
        self.request_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        logger.info(f"WorkloadSimulator initialized with processing_time={self.processing_time}")
    
    def process(self, delay=None):
        """处理请求"""
        if delay is None:
            delay = self.processing_time
        
        time.sleep(float(delay))
        
        with self.lock:
            self.request_count += 1
        
        return self.request_count
    
    def record_error(self):
        """记录错误"""
        with self.lock:
            self.error_count += 1

simulator = WorkloadSimulator()

@app.route('/health', methods=['GET'])
def health():
    """健康检查 - ALB使用"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'requests': simulator.request_count
    }), 200

@app.route('/request', methods=['POST'])
def handle_request():
    """处理请求"""
    try:
        data = request.get_json() or {}
        delay = data.get('delay', simulator.processing_time)
        
        count = simulator.process(delay)
        
        logger.info(f"Request processed: #{count}")
        
        return jsonify({
            'status': 'success',
            'request_count': count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        simulator.record_error()
        logger.error(f"Error processing request: {e}")
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'errors': simulator.error_count
        }), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """返回应用指标"""
    return jsonify({
        'total_requests': simulator.request_count,
        'total_errors': simulator.error_count,
        'processing_time': simulator.processing_time,
        'error_rate': simulator.error_count / max(simulator.request_count, 1) * 100
    }), 200

if __name__ == '__main__':
    # 跨平台运行
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask app on port {port} (debug={debug})")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 3.2 跨平台本地测试

```bash
# 所有平台执行相同命令

# 1. 安装依赖
pip install -r requirements.txt

# 2. 本地测试
cd application
export PROCESSING_TIME=0.3  # Windows: set PROCESSING_TIME=0.3
python app.py

# 3. 另一个终端测试端点
curl http://localhost:5000/health
curl -X POST http://localhost:5000/request -H "Content-Type: application/json" -d '{"delay": 0.5}'
curl http://localhost:5000/metrics
```

---

## Phase 4: 部署到AWS (Week 4) - 跨平台

### 4.1 一键部署

```bash
# 所有平台执行相同命令
python scripts/deploy_all.py
```

### 4.2 验证部署

```python
# scripts/verify_deployment.py
"""
验证部署 - 跨平台
"""

import subprocess
import json
import sys

class DeploymentVerifier:
    def __init__(self, region='us-east-1'):
        self.region = region
    
    def verify_resources(self):
        """验证所有资源"""
        checks = [
            ('VPC', 'aws ec2 describe-vpcs'),
            ('Subnets', 'aws ec2 describe-subnets'),
            ('Security Groups', 'aws ec2 describe-security-groups'),
            ('Load Balancers', 'aws elbv2 describe-load-balancers'),
            ('ASG', 'aws autoscaling describe-auto-scaling-groups'),
            ('Instances', 'aws ec2 describe-instances'),
        ]
        
        print("\n验证AWS资源:")
        print("─" * 60)
        
        for name, cmd in checks:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    count = len(data.get(list(data.keys())[0], []))
                    print(f"✓ {name}: {count} resources")
                else:
                    print(f"✗ {name}: Failed")
            except Exception as e:
                print(f"✗ {name}: {e}")

if __name__ == '__main__':
    verifier = DeploymentVerifier()
    verifier.verify_resources()
```

---

## Phase 5-10: 实验、分析、报告 (Week 5-10) - 跨平台

所有测试脚本都使用 Python + Locust（跨平台支持）

```bash
# 所有平台执行相同命令
python load-testing/run_experiment.py
python data-collection/analyze_results.py
```

### 6.1 数据分析

- [ ] **生成对比图表**
  ```python
  # data-collection/generate_charts.py
  
  import matplotlib.pyplot as plt
  import json
  import pandas as pd
  
  # 读取总结数据
  with open('results/summary.json', 'r') as f:
      data = json.load(f)
  
  # 创建对比图表
  scenarios = ['spike', 'ramp_up', 'sustained', 'burst']
  
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))
  fig.suptitle('Autoscaling Performance Comparison: CPU vs Request-Based', fontsize=16)
  
  for idx, scenario in enumerate(scenarios):
      ax = axes[idx // 2, idx % 2]
      
      a_key = f'scenario_a_{scenario}'
      b_key = f'scenario_b_{scenario}'
      
      cpu_p95 = data[a_key]['p95_response_time']
      req_p95 = data[b_key]['p95_response_time']
      
      metrics = ['P50', 'P95', 'P99', 'Error Rate']
      cpu_values = [
          data[a_key]['p50_response_time'],
          data[a_key]['p95_response_time'],
          data[a_key]['p99_response_time'],
          data[a_key]['error_rate']
      ]
      req_values = [
          data[b_key]['p50_response_time'],
          data[b_key]['p95_response_time'],
          data[b_key]['p99_response_time'],
          data[b_key]['error_rate']
      ]
      
      x = range(len(metrics))
      width = 0.35
      
      ax.bar([i - width/2 for i in x], cpu_values, width, label='CPU-Based')
      ax.bar([i + width/2 for i in x], req_values, width, label='Request-Based')
      
      ax.set_ylabel('Time (ms) / Error Rate (%)')
      ax.set_title(f'{scenario.replace("_", " ").title()}')
      ax.set_xticks(x)
      ax.set_xticklabels(metrics)
      ax.legend()
  
  plt.tight_layout()
  plt.savefig('results/comparison_charts.png', dpi=300)
  print("Charts saved to results/comparison_charts.png")
  ```

- [ ] **生成详细数据表**
  ```python
  # data-collection/generate_tables.py
  
  import json
  import pandas as pd
  
  with open('results/summary.json', 'r') as f:
      data = json.load(f)
  
  # 创建对比表格
  scenarios = ['spike', 'ramp_up', 'sustained', 'burst']
  
  comparison_data = []
  
  for scenario in scenarios:
      a_key = f'scenario_a_{scenario}'
      b_key = f'scenario_b_{scenario}'
      
      improvement = ((data[a_key]['p95_response_time'] - data[b_key]['p95_response_time']) 
                     / data[a_key]['p95_response_time'] * 100)
      
      comparison_data.append({
          'Scenario': scenario.replace('_', ' ').title(),
          'CPU P95 (ms)': f"{data[a_key]['p95_response_time']:.2f}",
          'Request P95 (ms)': f"{data[b_key]['p95_response_time']:.2f}",
          'Improvement (%)': f"{improvement:.1f}%",
          'CPU Error Rate (%)': f"{data[a_key]['error_rate']:.2f}",
          'Request Error Rate (%)': f"{data[b_key]['error_rate']:.2f}"
      })
  
  df = pd.DataFrame(comparison_data)
  print(df.to_string(index=False))
  
  # 保存为CSV
  df.to_csv('results/comparison_table.csv', index=False)
  ```

- [ ] **运行分析脚本**
  ```bash
  python data-collection/summarize_results.py
  python data-collection/generate_charts.py
  python data-collection/generate_tables.py
  ```

### 6.2 报告结构准备

- [ ] **创建报告大纲**
  ```markdown
  # Comparative Analysis of Autoscaling Strategies
  
  ## 1. Abstract (< 250 words)
  
  ## 2. Introduction
     - Cloud elasticity and autoscaling background
     - Problem statement: CPU-based scaling limitations
     - Hypothesis: Request-based scaling is faster
     - Paper structure
  
  ## 3. Related Work
     - Existing autoscaling approaches
     - AWS autoscaling features
     - Research gaps
  
  ## 4. Methodology
     - Infrastructure setup (VPC, EC2, ALB, ASG)
     - Scenario A: CPU-based configuration
     - Scenario B: Request-based configuration
     - Load generation and metrics collection
  
  ## 5. Experimental Results
     - Scenario A results (CPU-based)
     - Scenario B results (Request-based)
     - Comparison across 4 load patterns
     - Statistical analysis
  
  ## 6. Discussion
     - Why Request-based performs better
     - Trade-offs and limitations
     - Practical implications
  
  ## 7. Conclusion
  
  ## 8. References
  
  ## Artifact Appendix (no page limit)
  ```

- [ ] **开始撰写报告**
  ```bash
  # 创建LaTeX模板或Word文档
  mkdir -p report
  touch report/main.tex  # 如果使用LaTeX
  # 或
  touch report/main.docx  # 如果使用Word
  ```

- [ ] **Git提交**
  ```bash
  git add data-collection/
  git add results/
  git commit -m "Add data analysis and visualization scripts with experimental results"
  git push
  ```

---

## Phase 7: 报告完善 & 演示制作 (Week 8-9)

### 7.1 最终报告撰写

- [ ] **完成报告所有章节**
  - 确保内容完整、逻辑清晰
  - 合并所有数据、图表、表格
  - 页数控制在9页以内

- [ ] **Artifact Appendix准备**
  ```markdown
  # Artifact Appendix
  
  ## System Dependencies
  - Python 3.9+
  - AWS CLI v2
  - Terraform (可选)
  
  ## Installation Steps
  1. Clone repository
  2. Configure AWS credentials
  3. Run infrastructure setup
  4. Deploy application
  5. Run experiments
  
  ## Reproduction Instructions
  1. Step by step to run experiments
  2. Expected outputs
  3. Validation methods
  
  ## Cost Estimation
  - Estimated AWS cost: $50-100
  - How to clean up resources
  ```

- [ ] **转换为PDF**
  ```bash
  # 使用LaTeX编译
  pdflatex main.tex
  
  # 或使用Word另存为PDF
  ```

- [ ] **最终质量检查**
  - [ ] 拼写和语法检查
  - [ ] 所有引用和链接有效
  - [ ] 图表清晰可读
  - [ ] 页数符合要求
  - [ ] 文件名正确: `GroupID_report.pdf`

### 7.2 演示视频制作

- [ ] **准备演示脚本**
  ```
  [0:00-1:00] 项目介绍
  - 云计算中的Autoscaling问题
  - CPU-based vs Request-based对比
  
  [1:00-2:00] 技术架构
  - 基础设施架构图
  - 两个Scenario的配置
  
  [2:00-7:00] 现场演示
  - 启动ALB和ASG
  - 运行Locust负载测试
  - 展示CloudWatch监控面板
  - 展示实时性能数据
  
  [7:00-9:00] 关键发现
  - P95延迟对比
  - 错误率对比
  - 实际意义
  
  [9:00-10:00] 总结和建议
  ```

- [ ] **录制视频**
  ```bash
  # Windows: 使用CamStudio
  # 或使用OBS Studio (免费)
  
  # 录制内容:
  # 1. 屏幕+声音
  # 2. 清晰展示代码和输出
  # 3. 英文讲解
  ```

- [ ] **后期编辑**
  - 添加字幕
  - 添加必要的图形和说明
  - 调整音量
  - 确保时长不超过10分钟

- [ ] **上传视频**
  ```bash
  # 上传到YouTube或B站
  # 设置为公开可见
  # 记录视频链接
  ```

- [ ] **Git提交**
  ```bash
  git add report/
  git commit -m "Add final report (9 pages) with all data and analysis"
  git push
  ```

---

## Phase 8: 最终检查 & 提交 (Week 10)

### 8.1 检查清单

- [ ] **报告检查**
  - [ ] 文件名: `GroupID_report.pdf`
  - [ ] 页数: 9页以内
  - [ ] 格式: 12pt Times New Roman, 单栏单倍行距
  - [ ] 内容: 所有必须章节完整
  - [ ] 质量: 无明显语法错误

- [ ] **产品检查**
  - [ ] GitHub仓库公开
  - [ ] 完整的提交历史（多人多次）
  - [ ] 所有代码可运行
  - [ ] Artifact Appendix清晰完整
  - [ ] README详细

- [ ] **演示视频检查**
  - [ ] 视频分辨率 >= 640x480
  - [ ] 时长 <= 10分钟
  - [ ] 英文讲解
  - [ ] 公开可见（YouTube/B站）
  - [ ] 链接正确

- [ ] **数据检查**
  - [ ] 实验结果完整
  - [ ] 数据与报告一致
  - [ ] 可重复性说明完整

### 8.2 最后一次Git提交

```bash
# 确保所有文件都已提交
git status

# 最后的提交
git commit -m "Final project submission: Report, video link, and complete artifact"
git push
```

### 8.3 通过Canvas提交

- [ ] **提交报告**
  - Canvas -> Assignments -> Group projects -> Report
  - 上传: `GroupID_report.pdf`
  - 截止: 2026年4月24日 23:59 HKT

- [ ] **提交演示视频链接**
  - Canvas -> Assignments -> Group projects -> Demo
  - 上传: 视频链接（YouTube或B站URL）
  - 截止: 2026年4月24日 23:59 HKT

### 8.4 资源清理（实验完成后）

```bash
# 清理AWS资源以避免持续费用
bash scripts/cleanup_infrastructure.sh

# 验证清理
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].AutoScalingGroupName'
aws ec2 describe-instances --filters "Name=tag:Project,Values=Autoscaling" --query 'Reservations[0].Instances[*].InstanceId'
```

---

## 项目成果物清单

### 交付物

```
✓ 最终报告 (9页)
  └─ GroupID_report.pdf

✓ 软件产品
  ├─ GitHub仓库 (公开)
  │  ├─ application/      (Flask应用)
  │  ├─ infrastructure/   (AWS CLI脚本)
  │  ├─ load-testing/     (Locust脚本)
  │  ├─ data-collection/  (指标收集脚本)
  │  ├─ results/          (实验数据和分析)
  │  └─ README.md         (项目概述)
  └─ Artifact Appendix    (在报告中或单独)

✓ 演示视频 (<=10分钟)
  └─ YouTube/B站链接

✓ 完整提交历史
  └─ 多个成员的多次提交
```

### 预期成果

```
✓ 4种负载模式下的完整实验数据
✓ CPU vs Request-based的定量对比
✓ 性能改进的深度分析
✓ 可完全复现的产品和代码
✓ 专业的演示视频
```

---

## 常见问题 & 故障排除

### AWS成本控制

**Q: 如何避免高额费用？**
- A: 1) 设置AWS预算告警
  2) 实验完成立即清理资源
  3) 使用t2.micro (Free Tier)
  4) 考虑使用Spot实例

### CLI命令失败

**Q: AWS CLI命令报权限错误？**
- A: 1) 检查IAM权限
  2) 检查AWS credentials配置
  3) 确认Region正确

### 负载测试不如预期

**Q: 负载测试没有触发扩展？**
- A: 1) 检查ASG缩放策略配置
  2) 检查CloudWatch指标
  3) 调整目标值 (CPU 50% -> 30%)
  4) 增加负载强度

---

## 时间管理建议

| 周数 | 任务 | 预计小时 |
|-----|-----|---------|
| 1-2 | 环境+基础设施 | 20 |
| 2-3 | 应用开发 | 15 |
| 4 | 部署+验证 | 10 |
| 5-6 | 实验执行 | 25 |
| 7 | 数据分析 | 15 |
| 8-9 | 报告+视频 | 30 |
| 10 | 最终检查+提交 | 5 |
| **总计** | | **120小时** |

**建议**: 每周投入15-20小时，分散在周一至周五，周末进行测试和数据收集。

---

## 🌍 完整的跨平台支持总结

### ✅ Python脚本优势

所有核心脚本都用**Python**编写：

| 方面 | Bash | Python |
|-----|------|--------|
| Windows | ❌ 需要WSL | ✅ 原生支持 |
| macOS | ✅ 原生支持 | ✅ 原生支持 |
| Linux | ✅ 原生支持 | ✅ 原生支持 |
| 路径处理 | ❌ 复杂 | ✅ pathlib简单 |
| 错误处理 | ❌ 基础 | ✅ 完整 |
| 日志记录 | ❌ 手动 | ✅ 内置 |
| 单元测试 | ❌ 困难 | ✅ unittest/pytest |
| 依赖管理 | ❌ 手动 | ✅ pip/requirements.txt |
| 版本控制 | ❌ 全局 | ✅ 虚拟环境 |

### 📝 文件清单

```
✓ Phase 0 必需脚本:
  - scripts/check_environment.py        # 环境检查
  - scripts/init_project.py             # 项目初始化
  - scripts/config_manager.py           # 配置管理
  - scripts/aws_utils.py                # AWS CLI包装

✓ Phase 1-2 基础设施脚本:
  - scripts/setup_network.py            # 创建VPC
  - scripts/setup_security_groups.py    # 安全组
  - scripts/setup_iam_role.py           # IAM角色
  - scripts/setup_alb.py                # 负载均衡器
  - scripts/create_ami.py               # AMI创建
  - scripts/setup_asg.py                # Auto Scaling
  - scripts/deploy_all.py               # 一键部署

✓ Phase 3 应用脚本:
  - application/app.py                  # Flask应用
  - application/Dockerfile              # Docker镜像
  - application/requirements.txt        # Python依赖

✓ Phase 5-6 实验脚本:
  - load-testing/locustfile.py          # 负载测试
  - load-testing/run_experiment.py      # 实验运行器
  - data-collection/collect_metrics.py  # 指标收集
  - data-collection/analyze_results.py  # 数据分析

✓ 工具脚本:
  - scripts/verify_deployment.py        # 验证部署
  - scripts/cleanup_infrastructure.py   # 清理资源
  - scripts/cache_manager.py            # 缓存管理
  - scripts/secure_config.py            # 安全检查
```

### 🔄 团队协作工作流

```
Week 1: 并行工作（无冲突）
├─ Member A: 网络和VPC
├─ Member B: 安全组和IAM
└─ Member C: 学习AWS CLI和Python

Week 2-3: 继续并行
├─ Member A: Flask应用开发
├─ Member B: Docker化
└─ Member C: 部署脚本

Week 4: 同步并部署
├─ 所有人: 执行 python scripts/deploy_all.py
└─ 一起验证: python scripts/verify_deployment.py

Week 5-6: 并行实验
├─ Member A: Scenario A 实验
├─ Member B: Scenario B 实验
└─ Member C: 监控和数据收集

Week 7: 数据分析
├─ Member A: 运行分析脚本
├─ Member B: 生成图表
└─ Member C: 编写报告初稿

Week 8-9: 报告和视频
├─ Member A: 撰写方法论和结果
├─ Member B: 制作演示视频
└─ Member C: 编辑和校对

Week 10: 最后冲刺
└─ 所有人: 最终检查和提交
```

### 🎯 成功指标

**所有成员都能在自己的机器上成功运行：**

✅ `python scripts/check_environment.py` → 全部通过
✅ `python scripts/init_project.py` → 目录结构完整
✅ `python scripts/deploy_all.py` → 基础设施部署成功
✅ `python load-testing/run_experiment.py` → 实验数据生成
✅ `python data-collection/analyze_results.py` → 分析完成

**最后提交的内容：**

✅ GitHub仓库：所有成员都有提交
✅ 报告PDF：9页以内，格式符合要求
✅ 演示视频：≤10分钟，公开可见
✅ 产品附录：清晰完整

---

**开始日期**: 现在
**截止日期**: 2026年4月24日 23:59 HKT

**关键: 使用Python脚本而不是Bash，确保真正的跨平台兼容性！** 🚀

