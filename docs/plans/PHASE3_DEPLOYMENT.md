# Phase 3: AWS 部署实现计划

> **对于 Claude**: 必需的子技能: 使用 superpowers:executing-plans 逐任务实现本计划。

**目标**: 将 AWS 基础设施、Flask 测试应用和负载生成工具部署到 AWS，进行端到端验证。

**架构**:
- 部署 Phase 2a AWS 基础设施 (VPC、ALB、ASG、EC2 实例)
- 通过用户数据/手动部署将 Flask 测试应用部署到 EC2 实例
- 将负载生成器脚本部署到控制实例或具有 AWS 凭证的本地计算机
- 验证端到端连接: 本地 → ALB → EC2 → CloudWatch

**技术栈**:
- AWS boto3, CloudFormation 等效 (基础设施即代码)
- EC2 用户数据脚本用于 Flask 应用部署
- Docker 容器用于 Flask 应用 (可选但推荐)
- CloudWatch 监控和告警

**时间表**: ~6-8 小时
- 基础设施部署: 30 分钟
- 应用部署: 1-2 小时
- 负载生成器验证: 1 小时
- 端到端测试: 1-2 小时
- 故障排查缓冲: 1-2 小时

---

## 任务 1: 部署 AWS 基础设施并验证

**文件**:
- 使用: `scripts/deploy_all.py` (来自 Phase 1)
- 验证: `scripts/verify_infrastructure.py` (来自 Phase 1)
- 输出: `infrastructure/` 目录包含 JSON 配置
- 新增: `docs/PHASE3_DEPLOYMENT_LOG.md` (部署文档)

**目标**: 部署完整的 AWS 基础设施堆栈并验证所有组件健康。

### 步骤 1: 部署前检查清单

在部署前验证前置要求：

```bash
# 1. 检查 AWS 凭证已配置
aws sts get-caller-identity

# 2. 验证 AWS 区域
echo $AWS_DEFAULT_REGION  # 应该是 us-east-1

# 3. 检查现有基础设施 (可选清理)
aws ec2 describe-instances --filters "Name=tag:Project,Values=autoscaling-experiment" --query 'Reservations[].Instances[].InstanceId'
```

### 步骤 2: 部署基础设施

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
python scripts/deploy_all.py
```

**预期输出**:
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

**创建的产物**:
- `infrastructure/network-config.json`
- `infrastructure/iam-config.json`
- `infrastructure/security-groups-config.json`
- `infrastructure/launch-templates-config.json`
- `infrastructure/alb-config.json`
- `infrastructure/asg-config.json`
- `infrastructure/deployment-log.json`

### 步骤 3: 验证基础设施健康

```bash
python scripts/verify_infrastructure.py
```

**预期输出**:
```
✅ VPC 存在且健康
✅ 子网已创建 (2 个公有, 2 个私有)
✅ 安全组已配置
✅ IAM 角色已创建且具有策略
✅ 启动模板已创建 (CPU 和请求率)
✅ ALB 活跃且监听端口 80
✅ 目标组已创建并已注册
✅ ASG-CPU: 2/2 个实例健康
✅ ASG-Request: 2/2 个实例健康
✅ CloudWatch 指标流动中
验证: 通过 (所有检查通过)
```

**如果任何检查失败**:
1. 查看特定的失败消息
2. 在 AWS 控制台检查组件状态
3. 诊断问题 (常见: 安全组规则、IAM 权限)
4. 修复并重新运行验证

### 步骤 4: 提取 ALB DNS 并记录

从配置中提取 ALB DNS 名称：

```bash
# 提取 ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")
echo "ALB DNS: $ALB_DNS"

# 测试 ALB 可访问性
curl http://$ALB_DNS/health
# 应该返回 HTTP 200 且带有健康状态
```

**在 PHASE3_DEPLOYMENT_LOG.md 中记录**:
```markdown
# Phase 3 部署日志

## 基础设施部署

**日期**: [今天日期]
**部署时间**: [耗时]
**状态**: ✅ 成功

### 已部署的组件

- VPC: experiment-vpc (10.0.0.0/16)
- 公有子网: 10.0.1.0/24, 10.0.2.0/24
- 私有子网: 10.0.11.0/24, 10.0.12.0/24
- ALB DNS: <您的_ALB_DNS>
- ASG-CPU: experiment-asg-cpu (期望: 2, 最小: 1, 最大: 5)
- ASG-Request: experiment-asg-request (期望: 2, 最小: 1, 最大: 5)

### 验证结果

所有 12 项验证检查已通过 ✅
ALB 可访问: http://<ALB_DNS>/health
```

### 步骤 5: 提交

```bash
git add infrastructure/ docs/PHASE3_DEPLOYMENT_LOG.md
git commit -m "docs: 记录 Phase 3 基础设施部署

- 部署完整的 AWS 基础设施 (VPC、ALB、ASG)
- 所有验证检查通过
- ALB 可访问且实例健康"
```

---

## 任务 2: 将 Flask 测试应用部署到 EC2

**文件**:
- 部署: `apps/test_app/app.py`
- 部署: `apps/test_app/Dockerfile`
- 新增: `deployment/deploy_app.sh` (部署脚本)
- 新增: `deployment/app-user-data.sh` (EC2 用户数据)

**目标**: 将 Flask 应用部署到 EC2 实例，使其响应 ALB 健康检查和负载测试请求。

### 步骤 1: 创建 EC2 用户数据脚本

创建 `deployment/app-user-data.sh`:

```bash
#!/bin/bash
set -e

# 更新系统
yum update -y
yum install -y python3 python3-pip git

# 安装依赖
pip3 install flask boto3

# 创建应用目录
mkdir -p /opt/test_app
cd /opt/test_app

# 克隆或复制应用代码 (为简单起见使用内联)
cat > app.py << 'APPEOF'
[粘贴完整 app.py 内容]
APPEOF

# 创建 systemd 服务
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

# 启动服务
systemctl daemon-reload
systemctl enable test-app
systemctl start test-app

# 验证应用正在运行
sleep 5
curl http://localhost:8080/health || echo "应用尚未准备好"
```

### 步骤 2: 更新启动模板以包含用户数据

**选项 A: 手动 (如果在 Phase 1 中尚未完成)**:

更新 `setup_instances.py` 以在启动模板中包含用户数据：

```python
user_data = """#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install flask boto3
mkdir -p /opt/test_app
# ... [上述用户数据的其余部分]
"""

response = ec2_client.create_launch_template(
    LaunchTemplateName='experiment-launch-template-cpu',
    LaunchTemplateData={
        'ImageId': ami_id,
        'InstanceType': 't3.micro',
        'UserData': base64.b64encode(user_data.encode()).decode(),
        # ... 其他配置
    }
)
```

### 步骤 3: 终止旧实例并使用用户数据创建新实例

```bash
# 获取 ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")

# 更新 ASG 以应用新的启动模板 (如果已修改)
# AWS 将逐步用新实例替换旧实例

# 等待实例健康
echo "等待实例健康..."
for i in {1..30}; do
  HEALTHY=$(aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names experiment-asg-cpu \
    --query 'AutoScalingGroups[0].Instances[?HealthStatus==`Healthy`]' \
    --output text | wc -w)
  
  if [ "$HEALTHY" -ge 2 ]; then
    echo "✅ 实例已健康"
    break
  fi
  echo "等待中... ($i/30)"
  sleep 10
done
```

### 步骤 4: 验证应用正在响应

```bash
# 测试健康端点
curl http://$ALB_DNS/health
# 预期: {"status": "healthy", "timestamp": "...", "version": "1.0"}

# 测试数据端点
curl http://$ALB_DNS/data?size=10
# 预期: {"data": "...", "size_kb": 10, "timestamp": "..."}

# 测试指标端点
curl http://$ALB_DNS/metrics
# 预期: {"total_requests": N, "elapsed_seconds": X, ...}
```

### 步骤 5: 创建部署验证脚本

创建 `deployment/verify_app_deployment.py`:

```python
"""验证 Flask 应用到 AWS 的部署。"""

import requests
import json
import sys
from pathlib import Path

def verify_app_deployment(alb_dns):
    """验证 Flask 应用可访问且响应正确。"""
    
    tests_passed = 0
    tests_total = 0
    
    endpoints = [
        {
            'name': '健康检查',
            'method': 'GET',
            'endpoint': '/health',
            'expected_keys': ['status', 'timestamp']
        },
        {
            'name': '数据端点',
            'method': 'GET',
            'endpoint': '/data?size=10',
            'expected_keys': ['data', 'size_kb']
        },
        {
            'name': '指标端点',
            'method': 'GET',
            'endpoint': '/metrics',
            'expected_keys': ['total_requests', 'request_rate_per_second']
        },
        {
            'name': 'CPU 密集型 (POST)',
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
            
            # 检查必需的键
            missing_keys = [k for k in test['expected_keys'] if k not in data]
            if missing_keys:
                print(f"❌ {test['name']}: 缺少键 {missing_keys}")
                continue
            
            print(f"✅ {test['name']}: 通过")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ {test['name']}: {str(e)}")
    
    print(f"\n结果: {tests_passed}/{tests_total} 个测试通过")
    return tests_passed == tests_total

if __name__ == '__main__':
    # 从配置获取 ALB DNS
    config_path = Path('infrastructure/alb-config.json')
    if not config_path.exists():
        print("❌ infrastructure/alb-config.json 未找到")
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    alb_dns = config['alb_dns_name']
    print(f"验证部署到 ALB: {alb_dns}\n")
    
    success = verify_app_deployment(alb_dns)
    sys.exit(0 if success else 1)
```

### 步骤 6: 运行验证

```bash
python deployment/verify_app_deployment.py
```

**预期输出**:
```
验证部署到 ALB: experiment-alb-xxx.us-east-1.elb.amazonaws.com

✅ 健康检查: 通过
✅ 数据端点: 通过
✅ 指标端点: 通过
✅ CPU 密集型 (POST): 通过

结果: 4/4 个测试通过
```

### 步骤 7: 提交

```bash
git add deployment/deploy_app.sh deployment/app-user-data.sh deployment/verify_app_deployment.py
git commit -m "feat: 添加 Flask 应用部署脚本

- 创建 EC2 用户数据脚本用于应用部署
- 添加应用验证脚本
- 记录部署流程"
```

---

## 任务 3: 验证负载生成器可连接

**文件**:
- 使用: `scripts/load_generator.py` (来自 Phase 2b)
- 使用: `scripts/metrics_collector.py` (来自 Phase 2b)
- 新增: `deployment/test_load_generator.py` (快速验证)

**目标**: 验证负载生成器可连接到 ALB 并成功生成流量。

### 步骤 1: 创建快速测试脚本

创建 `deployment/test_load_generator.py`:

```python
"""针对已部署 ALB 的负载生成器快速测试。"""

import json
from pathlib import Path
import sys

# 将脚本添加到路径
sys.path.insert(0, 'scripts')

from load_generator import LoadGenerator

def test_load_generator():
    """针对 ALB 运行简短负载测试。"""
    
    # 获取 ALB DNS
    config_path = Path('infrastructure/alb-config.json')
    with open(config_path) as f:
        config = json.load(f)
    
    alb_dns = f"http://{config['alb_dns_name']}"
    
    print(f"针对以下目标测试负载生成器: {alb_dns}\n")
    
    # 使用最小负载创建负载生成器
    gen = LoadGenerator(
        target_url=alb_dns,
        request_rate=5,  # 每秒 5 个请求
        duration_seconds=10,  # 10 秒测试
        pattern='constant',
        endpoint='/health'
    )
    
    print("运行 10 秒负载测试 (5 req/s)...")
    stats = gen.generate_load()
    
    print(f"\n✅ 测试完成!")
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功: {stats['successful_requests']}")
    print(f"失败: {stats['failed_requests']}")
    print(f"成功率: {stats['successful_requests']/stats['total_requests']*100:.1f}%")
    print(f"平均响应时间: {stats['average_response_time']:.3f}s")
    print(f"P95 响应时间: {stats['p95_response_time']:.3f}s")
    
    return stats['successful_requests'] > 0

if __name__ == '__main__':
    try:
        success = test_load_generator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### 步骤 2: 运行测试

```bash
python deployment/test_load_generator.py
```

**预期输出**:
```
针对以下目标测试负载生成器: http://experiment-alb-xxx.us-east-1.elb.amazonaws.com

运行 10 秒负载测试 (5 req/s)...

✅ 测试完成!
总请求数: 50
成功: 48
失败: 2
成功率: 96.0%
平均响应时间: 0.045s
P95 响应时间: 0.089s
```

### 步骤 3: 如果测试失败的故障排查

**如果所有请求都失败**:
1. 检查 ALB 是否可访问: `curl http://$ALB_DNS/health`
2. 检查安全组是否允许端口 80 入站
3. 检查 EC2 实例是否正在运行且 ASG 中健康

**如果响应时间缓慢**:
1. 可能表示实例仍在启动
2. 等待 2-3 分钟后重试

**如果某些请求失败**:
1. 这在初始部署期间是正常的
2. 如果成功率 > 90% 则可接受

### 步骤 4: 提交

```bash
git add deployment/test_load_generator.py
git commit -m "test: 添加负载生成器验证脚本

- 针对已部署 ALB 的负载生成器快速测试
- 验证连接和基本性能指标"
```

---

## 任务 4: 记录部署并创建部署指南

**文件**:
- 创建: `docs/PHASE3_DEPLOYMENT_GUIDE.md`
- 更新: `docs/PHASE3_DEPLOYMENT_LOG.md` (来自任务 1)

**目标**: 记录完整部署流程以便重现。

### 步骤 1: 创建部署指南

创建 `docs/PHASE3_DEPLOYMENT_GUIDE.md`:

```markdown
# Phase 3: AWS 部署指南

## 概述

本指南覆盖将自动扩缩容对比基础设施和应用部署到 AWS。

## 前置要求

1. **AWS 账户** 且本地配置了凭证
2. **boto3** 已安装: `pip install boto3`
3. **Python 3.8+**
4. **curl** 用于测试 (或 requests 库)

## 部署步骤

### 1. 部署基础设施 (30 分钟)

```bash
# 验证 AWS 凭证
aws sts get-caller-identity

# 部署所有基础设施
python scripts/deploy_all.py

# 验证部署
python scripts/verify_infrastructure.py
```

### 2. 部署 Flask 应用 (20-30 分钟)

Flask 应用通过 EC2 用户数据脚本部署。

**选项 A: 自动 (通过用户数据)**

如果启动模板包含用户数据，实例将自动启动 Flask 应用。

**选项 B: 手动**

SSH 进入每个实例并：
```bash
yum update -y
yum install -y python3 python3-pip
pip3 install flask boto3
# 将 app.py 复制到 /opt/test_app/
python3 /opt/test_app/app.py
```

### 3. 验证部署 (15 分钟)

```bash
# 提取 ALB DNS
ALB_DNS=$(python -c "import json; print(json.load(open('infrastructure/alb-config.json'))['alb_dns_name'])")

# 测试端点
curl http://$ALB_DNS/health
curl http://$ALB_DNS/data?size=10
curl http://$ALB_DNS/metrics

# 运行验证脚本
python deployment/verify_app_deployment.py

# 测试负载生成器
python deployment/test_load_generator.py
```

## 故障排查

### ALB 无法访问
- 检查安全组是否允许端口 80 入站
- 验证 ALB 处于 "活跃" 状态
- 部署后等待 2-3 分钟

### 实例不健康
- 检查 CloudWatch 日志中的错误
- 验证 IAM 角色具有必需的权限
- 检查实例安全组是否允许 CloudWatch 出站

### 负载测试失败
- 验证应用响应健康检查
- 检查 ALB 目标组健康状态
- 等待实例预热 (2-3 分钟)

## 成本管理

**重要**: 此基础设施会产生 AWS 费用!

为避免意外费用：
1. **仅在测试时保持资源运行**
2. **实验后删除资源** 使用：
   ```bash
   # 删除 ASG (移除 EC2 实例)
   aws autoscaling delete-auto-scaling-group --auto-scaling-group-name experiment-asg-cpu --force-delete
   
   # 删除 ALB
   aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN>
   
   # 删除 VPC (移除所有相关资源)
   aws ec2 delete-vpc --vpc-id <VPC_ID>
   ```

## 后续步骤

部署验证后：
1. 运行 Phase 4-5 实验
2. 从 CloudWatch 收集指标
3. 分析结果并生成报告
```

### 步骤 2: 更新部署日志

追加到 `docs/PHASE3_DEPLOYMENT_LOG.md`:

```markdown
## 应用部署

**日期**: [今天日期]
**状态**: ✅ 成功

### Flask 应用

- 通过用户数据部署到所有 ASG 实例
- 健康检查端点响应中
- 指标端点可访问

### 验证结果

- 健康检查: ✅ 通过
- 数据端点: ✅ 通过  
- 指标端点: ✅ 通过
- CPU 密集型: ✅ 通过
- 负载生成器测试: ✅ 通过 (96% 成功率)

## 成本

- 估计月成本: $3-5 USD (t3.micro 实例 + ALB)
- 当前部署: 活跃
- 预期持续时间: 至 2026 年 4 月 24 日
```

### 步骤 3: 提交

```bash
git add docs/PHASE3_DEPLOYMENT_GUIDE.md docs/PHASE3_DEPLOYMENT_LOG.md
git commit -m "docs: 添加 Phase 3 部署指南和日志

- 完整部署说明
- 故障排查指南
- 成本管理说明
- 部署验证结果"
```

---

## 总结

**Phase 3 实现计划完成**

| 任务 | 组件 | 估计时间 |
|------|-----------|-----------|
| 1 | 基础设施部署 | 1-1.5h |
| 2 | Flask 应用部署 | 1-1.5h |
| 3 | 负载生成器验证 | 0.5h |
| 4 | 文档编写 | 0.5h |
| **总计** | **所有部署任务** | **4-5h** |

**成功标准**:
- ✅ 所有基础设施组件已部署且健康
- ✅ Flask 应用响应健康检查
- ✅ ALB 从本地计算机可访问
- ✅ 负载生成器可成功发送流量
- ✅ 部署已完全记录

**Phase 3 完成后**:
- 准备开始 Phase 4-5: 运行实验
- 准备从 CloudWatch 收集指标
- 准备分析结果
