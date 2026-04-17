# Phase 2A: AWS 基础设施部署指南

**项目**: autoscaling-strategy-compare  
**Phase**: 2A - AWS 基础设施配置和部署  
**状态**: ✅ 部署指南  
**产物**: 已部署的 AWS 资源、配置文件、验证报告  

---

## 概述

Phase 2A 部署指南详细说明如何使用 Python 脚本和 boto3 为自动扩缩容策略对比实验配置完整的 AWS 基础设施。

本指南涵盖：
- AWS 账户设置
- 网络基础设施 (VPC、子网、路由)
- 安全组配置
- IAM 角色和权限
- EC2 实例启动
- 应用负载均衡器 (ALB) 设置
- 自动扩展组 (ASG) 配置
- CloudWatch 监控
- 基础设施验证和测试

---

## 前置要求

### 系统要求

- **Python**: 3.8+
- **boto3**: 最新版本
- **AWS CLI**: v2（可选，用于验证）
- **操作系统**: Windows、macOS、Linux（所有脚本跨平台兼容）

### AWS 要求

1. **AWS 账户**: 已激活并可访问
2. **AWS 凭证**: 已配置
   ```bash
   aws configure
   # 输入：AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
   ```
3. **IAM 权限**: 需要以下权限
   - IAM: CreateRole, AttachRolePolicy, CreateInstanceProfile
   - EC2: CreateVpc, CreateSubnet, CreateSecurityGroup, RunInstances, CreateNetworkInterface
   - ELBv2: CreateLoadBalancer, CreateTargetGroup, RegisterTargets
   - AutoScaling: CreateAutoScalingGroup, PutScalingPolicy
   - CloudWatch: PutMetricAlarm

### 项目设置

```bash
# 1. 克隆项目 (如果还没有)
git clone <repo-url>
cd autoscaling-strategy-compare

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 4. 安装依赖
pip install -r requirements.txt
```

---

## 快速开始 (5 分钟)

### 完整部署

```bash
# 运行主部署脚本 (自动执行所有步骤)
python scripts/deploy_all.py

# 脚本将按此顺序执行：
# 1. setup_iam_role.py - 创建 IAM 角色
# 2. setup_network.py - 创建 VPC 和网络
# 3. setup_security_groups.py - 配置安全组
# 4. setup_alb.py - 配置 ALB
# 5. setup_instances.py - 启动 EC2 实例
# 6. setup_asg.py - 配置 ASG
# 7. verify_infrastructure.py - 验证所有资源
```

### 试运行 (无变更)

```bash
python scripts/deploy_all.py --dry-run
```

### 验证部署

```bash
python scripts/verify_infrastructure.py
```

---

## 详细部署步骤

### 第 1 步: IAM 角色设置 (5 分钟)

创建 EC2 实例所需的 IAM 角色和实例配置文件。

**文件**: `scripts/setup_iam_role.py`

**执行**:
```bash
python scripts/setup_iam_role.py
```

**创建的资源**:
- IAM 角色: `autoscaling-experiment-role`
- 实例配置文件: `autoscaling-experiment-instance-profile`
- 附加的策略: CloudWatch、S3（如果需要）

**验证**:
```bash
aws iam get-role --role-name autoscaling-experiment-role
aws iam list-instance-profiles --query 'InstanceProfiles[*].InstanceProfileName'
```

**故障排查**:
- 如果返回 "AccessDenied"，验证 AWS 凭证具有 IAM 权限
- 运行: `aws iam list-roles` 来测试权限

---

### 第 2 步: 网络配置 (10 分钟)

创建 VPC、子网、路由表和 NAT 网关。

**文件**: `scripts/setup_network.py`

**执行**:
```bash
python scripts/setup_network.py
```

**创建的资源**:
- VPC: `10.0.0.0/16` (可配置)
- 公有子网 (2 个): `10.0.1.0/24`, `10.0.2.0/24`
- 私有子网 (2 个): `10.0.11.0/24`, `10.0.12.0/24`
- 互联网网关
- NAT 网关（用于出站流量）
- 路由表

**验证**:
```bash
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock]'
aws ec2 describe-subnets --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone]'
aws ec2 describe-nat-gateways --query 'NatGateways[*].[NatGatewayId,State]'
```

**网络架构**:
```
VPC (10.0.0.0/16)
├── 公有子网 1 (10.0.1.0/24) - ALB
├── 公有子网 2 (10.0.2.0/24) - ALB
├── 私有子网 1 (10.0.11.0/24) - EC2
├── 私有子网 2 (10.0.12.0/24) - EC2
├── 互联网网关
└── NAT 网关 (用于出站流量)
```

---

### 第 3 步: 安全组配置 (10 分钟)

创建安全组并配置防火墙规则。

**文件**: `scripts/setup_security_groups.py`

**执行**:
```bash
python scripts/setup_security_groups.py
```

**创建的资源**:
- **ALB 安全组** (`sg-alb-*`)
  - 入站: HTTP (80), HTTPS (443) 来自 0.0.0.0/0
  - 出站: 所有流量到 EC2 安全组

- **EC2 安全组** (`sg-ec2-*`)
  - 入站: 8080 端口来自 ALB
  - 入站: 22 端口（SSH，可选）
  - 出站: 所有流量（用于互联网访问）

**验证**:
```bash
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,GroupName,VpcId]'
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,IpPermissions]'
```

**输出文件**: `infrastructure/security-config.json`

---

### 第 4 步: ALB 配置 (10 分钟)

创建应用负载均衡器和目标组。

**文件**: `scripts/setup_alb.py`

**执行**:
```bash
python scripts/setup_alb.py
```

**创建的资源**:
- 应用负载均衡器 (ALB): `experiment-alb`
- 目标组 (2 个):
  - `tg-cpu-asg` - 用于基于 CPU 的扩展
  - `tg-request-asg` - 用于基于请求率的扩展
- 监听器 (端口 80)
- 健康检查规则

**ALB 配置**:
- 健康检查路径: `/health`
- 检查间隔: 30 秒
- 不健康阈值: 2
- 健康阈值: 2

**验证**:
```bash
aws elbv2 describe-load-balancers --query 'LoadBalancers[*].[LoadBalancerName,DNSName,State.Code]'
aws elbv2 describe-target-groups --query 'TargetGroups[*].[TargetGroupName,HealthCheckPath,Port]'
```

**获取 ALB DNS 名称** (用于 Phase 2B 和 Phase 3):
```bash
cat infrastructure/alb-config.json | grep alb_dns_name
# 示例输出: "experiment-alb-1234567890.us-east-1.elb.amazonaws.com"
```

**输出文件**: `infrastructure/alb-config.json`

---

### 第 5 步: EC2 实例启动 (15 分钟)

启动 EC2 实例作为 ALB 的目标。

**文件**: `scripts/setup_instances.py`

**执行**:
```bash
# 使用默认值（2 个 t3.micro 实例）
python scripts/setup_instances.py

# 或指定实例数量和类型
python scripts/setup_instances.py --count 3 --instance-type t3.small
```

**创建的资源**:
- 2 个 EC2 实例 (默认: t3.micro)
- 关联 IAM 实例配置文件（用于 CloudWatch 访问）
- 配置安全组
- 标记实例用于管理

**实例配置**:
- **AMI**: Amazon Linux 2 (或 Ubuntu)
- **实例类型**: t3.micro（可配置）
- **虚拟储存**: 8 GB
- **IAM 角色**: autoscaling-experiment-role
- **监控**: CloudWatch 详细监控已启用

**验证**:
```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PrivateIpAddress,Tags]'
aws ec2 describe-instance-status --query 'InstanceStatuses[*].[InstanceId,InstanceStatus.Status]'
```

**输出文件**: `infrastructure/instances-config.json`

---

### 第 6 步: ASG 配置 (15 分钟)

创建自动扩展组用于两种策略。

**文件**: `scripts/setup_asg.py`

**执行**:
```bash
python scripts/setup_asg.py
```

**创建的资源**:
- **启动模板** (2 个):
  - `app-cpu-lt` - 用于基于 CPU 的 ASG
  - `app-request-lt` - 用于基于请求率的 ASG

- **自动扩展组** (2 个):
  - `experiment-asg-cpu`:
    - 目标指标: CPU 利用率 50%
    - 期望容量: 2
    - 最小: 1, 最大: 5
  
  - `experiment-asg-request`:
    - 目标指标: 每个实例请求率 10 req/s
    - 期望容量: 2
    - 最小: 1, 最大: 5

- **扩展策略** (每个 ASG):
  - 目标跟踪扩展策略
  - 预热期: 300 秒
  - 冷却期: 300 秒

- **CloudWatch 告警**:
  - 扩展事件告警
  - 缩减事件告警

**验证**:
```bash
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity,MinSize,MaxSize]'
aws autoscaling describe-launch-templates --query 'LaunchTemplates[*].[LaunchTemplateName,LatestVersionNumber]'
```

**输出文件**: `infrastructure/asg-config.json`

---

### 第 7 步: 基础设施验证 (5 分钟)

验证所有资源已正确部署。

**文件**: `scripts/verify_infrastructure.py`

**执行**:
```bash
python scripts/verify_infrastructure.py
```

**检查的项目**:
- ✅ VPC 和子网配置
- ✅ 安全组和防火墙规则
- ✅ IAM 角色和权限
- ✅ EC2 实例状态
- ✅ ALB 连接性
- ✅ 目标组健康检查
- ✅ ASG 配置
- ✅ CloudWatch 监控

**预期输出**:
```
✅ VPC: vpc-12345 已部署 (CIDR: 10.0.0.0/16)
✅ 子网: 4 个已配置
✅ 安全组: 2 个已配置
✅ IAM 角色: autoscaling-experiment-role 存在
✅ EC2 实例: 2 个正在运行
✅ ALB: 活跃 (DNS: experiment-alb-xxx.elb.amazonaws.com)
✅ 目标组: 2 个
✅ 健康目标: 2/2 健康
✅ ASG: 2 个已配置
✅ CloudWatch: 监控已激活
```

---

## 故障排查

### 常见问题和解决方案

#### 问题 1: IAM 权限不足

**错误**: `AccessDenied: User is not authorized to perform: iam:CreateRole`

**解决方案**:
1. 验证 AWS 凭证: `aws sts get-caller-identity`
2. 添加必需的 IAM 权限
3. 如果使用假设角色，确保信任政策包括您的用户

#### 问题 2: VPC CIDR 冲突

**错误**: `InvalidParameterValue: The CIDR '10.0.0.0/16' conflicts with reserved address space`

**解决方案**:
1. 编辑 `scripts/setup_network.py`
2. 更改 VPC CIDR: `10.1.0.0/16`, `10.2.0.0/16` 等
3. 重新运行脚本

#### 问题 3: 实例启动超时

**错误**: 实例处于 "pending" 状态超过 5 分钟

**解决方案**:
1. 检查可用性区域: `aws ec2 describe-availability-zones`
2. 检查实例存储限制: `aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A`
3. 使用不同的实例类型或区域

#### 问题 4: ALB 健康检查失败

**错误**: 目标显示 "unhealthy"，状态 "Unhealthy"

**解决方案** (正常 - Flask 应用尚未部署):
1. 这在 Phase 3 之前是预期的
2. Phase 3 将部署 Flask 应用到 EC2 实例
3. 部署后健康检查将通过

### 调试命令

```bash
# 检查所有基础设施
python scripts/verify_infrastructure.py

# 获取特定资源状态
aws ec2 describe-instance-status --query 'InstanceStatuses[*].[InstanceId,InstanceStatus]'

# 查看 ALB 健康检查详情
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# 查看 ASG 活动
aws autoscaling describe-scaling-activities --auto-scaling-group-name experiment-asg-cpu --max-records 5

# 查看部署日志
cat logs/deployment.log
```

---

## 配置文件

所有脚本在 `infrastructure/` 目录中生成 JSON 配置文件供后续阶段使用。

### alb-config.json

```json
{
  "alb_name": "experiment-alb",
  "alb_arn": "arn:aws:elasticloadbalancing:us-east-1:xxx:loadbalancer/app/experiment-alb/xxx",
  "alb_dns_name": "experiment-alb-1234567890.us-east-1.elb.amazonaws.com",
  "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/tg-cpu-asg/xxx",
  "port": 80,
  "protocol": "HTTP"
}
```

### asg-config.json

```json
{
  "asg_cpu_name": "experiment-asg-cpu",
  "asg_cpu_arn": "arn:aws:autoscaling:us-east-1:xxx:autoScalingGroup:xxx:autoScalingGroupName/experiment-asg-cpu",
  "asg_request_name": "experiment-asg-request",
  "asg_request_arn": "arn:aws:autoscaling:us-east-1:xxx:autoScalingGroup:xxx:autoScalingGroupName/experiment-asg-request",
  "desired_capacity": 2,
  "min_size": 1,
  "max_size": 5
}
```

### instances-config.json

```json
{
  "instance_ids": ["i-0123456789abcdef0", "i-0123456789abcdef1"],
  "instance_type": "t3.micro",
  "image_id": "ami-0c55b159cbfafe1f0",
  "security_group_ids": ["sg-12345678"]
}
```

### security-config.json

```json
{
  "vpc_id": "vpc-12345678",
  "vpc_cidr": "10.0.0.0/16",
  "public_subnets": ["subnet-111", "subnet-222"],
  "private_subnets": ["subnet-333", "subnet-444"],
  "security_group_alb": "sg-alb-12345678",
  "security_group_ec2": "sg-ec2-12345678"
}
```

---

## 验证清单

部署后验证以下各项：

- [ ] VPC 已创建并配置正确的 CIDR
- [ ] 4 个子网已创建（2 个公有，2 个私有）
- [ ] 互联网网关已附加
- [ ] NAT 网关已部署
- [ ] 安全组已配置（入站/出站规则）
- [ ] IAM 角色已创建并附加权限
- [ ] EC2 实例正在运行（状态: running）
- [ ] ALB 已创建且活跃
- [ ] 目标组已创建（2 个）
- [ ] 2 个 ASG 已配置
- [ ] CloudWatch 监控已激活
- [ ] 配置文件已生成到 `infrastructure/`

---

## 成本估算

Phase 2A 的预计 AWS 成本（每小时）：

| 资源 | 类型 | 数量 | 单价 | 总计 |
|------|------|------|------|------|
| EC2 实例 | t3.micro | 2 | $0.0052/h | $0.0104 |
| ALB | 标准 | 1 | $0.0225/h | $0.0225 |
| NAT 网关 | - | 1 | $0.045/h | $0.045 |
| NAT 数据处理 | GB | - | $0.045/GB | 可变 |
| **总计** | | | | **~$0.08/小时** |

**注意**: 实际成本将取决于数据传输和流量。Phase 4-5 期间成本可能增加。

---

## 下一步: Phase 2B

Phase 2A 部署成功后，进行 Phase 2B (应用开发)：

1. **记录 ALB DNS 名称**:
   ```bash
   cat infrastructure/alb-config.json | grep alb_dns_name
   ```

2. **进行 Phase 2B**: 
   - 创建负载生成器
   - 创建指标收集器
   - 创建 Flask 测试应用

3. **参考文件**: `docs/guides/PHASE2B_DEPLOYMENT_GUIDE.md`

---

## 清理资源 (可选)

完成实验后，清理 AWS 资源以避免持续收费：

```bash
# 运行清理脚本
python scripts/cleanup_infrastructure.py

# 或手动清理：
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name experiment-asg-cpu --force-delete
aws elbv2 delete-load-balancer --load-balancer-arn <alb-arn>
aws ec2 delete-vpc --vpc-id <vpc-id>
```

---

**Phase 2A 状态**: ✅ **部署指南完成**

参考 Phase 2A 基础设施设置计划了解更多详情: `docs/plans/PHASE2A_INFRASTRUCTURE_SETUP.md`
