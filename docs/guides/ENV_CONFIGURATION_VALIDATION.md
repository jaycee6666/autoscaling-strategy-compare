# 🔐 .env 配置验证完整指南

## 📋 快速验证（3 种方法）

### 方法 1️⃣ : 运行官方验证脚本（推荐）⭐

这是最快和最全面的方式。

```bash
# 进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 激活虚拟环境
venv\Scripts\activate.bat

# 运行验证脚本
python scripts/check_environment.py
```

**预期输出：**
```
=== Environment Check Report ===

✓ Python Version
  Status: PASS
  Info: Python 3.9.0

✓ Git Installation
  Status: PASS
  Info: git version 2.xx.x

✓ Python Dependencies
  Status: PASS
  Packages verified: boto3, requests, python-dotenv, pyyaml

✓ AWS Credentials
  Status: PASS
  Info: Credentials set via environment variables

✓ AWS Region
  Status: PASS
  Info: Region set to us-east-1

✓ Environment File
  Status: PASS
  Info: config/.env found

✓ AWS Connection Test
  Status: PASS
  Info: Successfully connected to AWS

=== Summary ===
Total Checks: 8
Passed: 8
Failed: 0
Status: ✓ ALL SYSTEMS GO!
```

**失败情况下会显示具体问题和解决方案。**

---

### 方法 2️⃣ : 运行快速 Python 测试脚本

创建一个临时测试脚本：

```bash
cat > test_aws_config.py << 'EOF'
#!/usr/bin/env python3
"""Quick AWS configuration test."""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("🔍 AWS Configuration Test")
print("=" * 50)

# Check 1: .env file exists
env_path = Path("config/.env")
print(f"\n1. .env 文件检查")
if env_path.exists():
    print(f"   ✓ 文件存在: {env_path.absolute()}")
else:
    print(f"   ✗ 文件不存在: {env_path}")
    sys.exit(1)

# Check 2: Environment variables loaded
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_DEFAULT_REGION")

print(f"\n2. 环境变量检查")
if access_key:
    print(f"   ✓ AWS_ACCESS_KEY_ID: {access_key[:10]}...{access_key[-4:]}")
else:
    print(f"   ✗ AWS_ACCESS_KEY_ID: 未设置")
    sys.exit(1)

if secret_key:
    print(f"   ✓ AWS_SECRET_ACCESS_KEY: {'*' * 20}")
else:
    print(f"   ✗ AWS_SECRET_ACCESS_KEY: 未设置")
    sys.exit(1)

if region:
    print(f"   ✓ AWS_DEFAULT_REGION: {region}")
else:
    print(f"   ✗ AWS_DEFAULT_REGION: 未设置")
    sys.exit(1)

# Check 3: Try to import boto3
print(f"\n3. boto3 库检查")
try:
    import boto3
    print(f"   ✓ boto3 已安装: {boto3.__version__}")
except ImportError:
    print(f"   ✗ boto3 未安装")
    sys.exit(1)

# Check 4: Test AWS connection
print(f"\n4. AWS 连接测试")
try:
    client = boto3.client(
        'sts',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    identity = client.get_caller_identity()
    print(f"   ✓ AWS 连接成功！")
    print(f"   Account ID: {identity['Account']}")
    print(f"   User ARN: {identity['Arn']}")
except Exception as e:
    print(f"   ✗ AWS 连接失败: {str(e)}")
    sys.exit(1)

print(f"\n✅ 所有检查通过！.env 配置有效！")
EOF

python test_aws_config.py
```

**预期输出：**
```
🔍 AWS Configuration Test
==================================================

1. .env 文件检查
   ✓ 文件存在: C:\...\config\.env

2. 环境变量检查
   ✓ AWS_ACCESS_KEY_ID: AKIA...EXAMPLE
   ✓ AWS_SECRET_ACCESS_KEY: ********************
   ✓ AWS_DEFAULT_REGION: us-east-1

3. boto3 库检查
   ✓ boto3 已安装: 1.26.50

4. AWS 连接测试
   ✓ AWS 连接成功！
   Account ID: 503280397333
   User ARN: arn:aws:iam::503280397333:user/your-username

✅ 所有检查通过！.env 配置有效！
```

---

### 方法 3️⃣ : 手动逐步检查

如果上面两个方法失败，用这个方法逐步调试：

#### Step 1: 检查 .env 文件是否存在
```bash
# Windows
dir config\.env

# Mac/Linux
ls -la config/.env
```

**应该显示：**
```
-rw-r--r--  1 user  group  xxx Apr 18 10:30 config/.env
```

#### Step 2: 查看 .env 内容（检查格式）
```bash
# Windows
type config\.env

# Mac/Linux
cat config/.env
```

**应该显示类似：**
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

**⚠️ 注意：**
- ❌ 不应该有空格在 `=` 周围
- ❌ 不应该有引号围绕值
- ✅ 每行一个变量

#### Step 3: 检查环境变量是否已加载
```python
# 在 Python 交互式终端测试
python

>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()  # 加载 .env 文件
>>> os.getenv("AWS_ACCESS_KEY_ID")
'AKIA...'
>>> os.getenv("AWS_SECRET_ACCESS_KEY")
'wJal...'
>>> os.getenv("AWS_DEFAULT_REGION")
'us-east-1'
```

**应该显示你的凭证信息。**

#### Step 4: 测试 boto3 连接
```python
import boto3

# 创建 STS 客户端（最轻量的 AWS 服务）
client = boto3.client('sts')

# 获取调用者身份
response = client.get_caller_identity()
print(response)
```

**成功输出：**
```python
{
    'UserId': 'AIDAI...',
    'Account': '503280397333',
    'Arn': 'arn:aws:iam::503280397333:user/your-username',
    'ResponseMetadata': {...}
}
```

---

## 🚨 常见错误及解决方案

### 错误 1: "No such file or directory: config/.env"

**原因：** .env 文件不存在

**解决方案：**
```bash
# 从模板创建
cp config/.env.template config/.env

# 编辑并填入你的凭证
# Windows - 用记事本或 VSCode 打开
code config/.env
```

---

### 错误 2: "Unable to locate credentials"

**原因：** 环境变量没有被正确加载

**解决方案：**

```python
# 检查是否正确加载
import os
from dotenv import load_dotenv

# 确保显式调用 load_dotenv()
load_dotenv('config/.env')  # 指定具体路径

# 验证变量
print(os.getenv('AWS_ACCESS_KEY_ID'))
print(os.getenv('AWS_SECRET_ACCESS_KEY'))
print(os.getenv('AWS_DEFAULT_REGION'))
```

---

### 错误 3: "Invalid Access Key or Secret Key"

**原因：** 凭证无效或已过期

**解决方案：**
1. 检查 AWS IAM 控制台是否凭证仍然有效
2. 确认没有拷贝错误（特别是特殊字符）
3. 重新生成新的访问密钥

```bash
# 在 AWS IAM 控制台中：
# 1. 进入 "Access Keys"
# 2. 删除旧的密钥
# 3. 创建新的密钥
# 4. 复制到 .env
```

---

### 错误 4: "ModuleNotFoundError: No module named 'dotenv'"

**原因：** python-dotenv 未安装

**解决方案：**
```bash
pip install python-dotenv
```

---

### 错误 5: "An error occurred (AuthFailure) ... not authorized to perform"

**原因：** IAM 用户权限不足

**解决方案：**
1. 确认 IAM 用户有以下权限：
   - EC2FullAccess
   - ElasticLoadBalancingFullAccess
   - AutoScalingFullAccess
   - IAMReadOnlyAccess（至少）

2. 在 AWS IAM 控制台中添加策略

---

## ✅ 完整验证清单

运行以下所有检查确保配置完全有效：

```bash
# □ 检查 .env 文件存在
ls config/.env

# □ 检查 Python 3.8+
python --version

# □ 检查虚拟环境激活
which python  # Mac/Linux 应该显示 venv/bin/python

# □ 安装依赖
pip install -r requirements.txt

# □ 运行官方验证脚本
python scripts/check_environment.py

# □ 快速连接测试
python -c "import boto3; print(boto3.client('sts').get_caller_identity())"

# □ 验证基础设施状态
python scripts/verify_infrastructure.py
```

---

## 🎯 验证成功的标志

✅ **你会看到以下信息：**

1. **所有 Python 检查通过**
   ```
   ✓ Python Version: PASS
   ✓ Python Dependencies: PASS
   ```

2. **AWS 凭证被识别**
   ```
   ✓ AWS Credentials: PASS
   Info: Credentials set via environment variables
   ```

3. **AWS 连接成功**
   ```
   ✓ AWS Connection Test: PASS
   Info: Successfully connected to AWS
   ```

4. **基础设施验证成功**
   ```
   ✓ EC2 instances: 4 instances found
   ✓ ALB: Active
   ✓ ASG: 2 groups configured
   ```

---

## 🔒 安全提示

### ⚠️ 保护你的凭证

1. **确保 .env 在 .gitignore 中**
   ```bash
   # 检查 .gitignore
   cat .gitignore | grep .env
   # 应该显示: config/.env
   ```

2. **不要提交 .env 到 Git**
   ```bash
   # 验证 .env 未被追踪
   git status | grep ".env"
   # 不应该出现任何结果
   ```

3. **定期轮换凭证**
   - 每 90 天在 AWS IAM 控制台生成新密钥
   - 删除旧的访问密钥

4. **使用最小权限原则**
   - 只授予脚本需要的权限
   - 避免使用 AdministratorAccess

---

## 📞 如果仍然有问题

### 收集诊断信息：

```bash
# 1. 导出诊断信息
python scripts/check_environment.py > diagnostics.txt 2>&1

# 2. 检查日志
cat logs/*.log

# 3. 验证权限
aws iam get-user

# 4. 测试各个 AWS 服务
python -c "import boto3; boto3.client('ec2').describe_instances(MaxResults=1)"
```

### 常用命令参考：

```bash
# 查看所有环境变量（包括 AWS）
env | grep AWS

# 查看当前 AWS 账户信息
aws sts get-caller-identity

# 列出 EC2 实例
aws ec2 describe-instances --region us-east-1

# 列出 ALB
aws elbv2 describe-load-balancers --region us-east-1
```

---

**最后更新**: 2026-04-18  
**适用阶段**: Phase 0-6  
**作者**: CHEN Sijie (jaycee6666)
