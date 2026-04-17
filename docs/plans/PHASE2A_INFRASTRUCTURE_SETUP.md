# Phase 2A: AWS 基础设施设置及配置指南

**项目**: autoscaling-strategy-compare  
**Phase**: 2A - 基础设施脚本及工具  
**状态**: ✅ 完成  
**产物**: Python 脚本、JSON 配置文件、AWS CloudFormation 模板 (可选)

---

## 概述

Phase 2A 为自动扩缩容实验环境建立基础设施配置工具。本阶段创建可重用的跨平台脚本，用于：

1. **配置 AWS 资源** - VPC、子网、安全组、EC2 实例、应用负载均衡器、自动扩展组
2. **生成配置** - 记录基础设施状态的 JSON 文件，供下游阶段使用
3. **验证部署** - 健康检查和基础设施验证
4. **提供基础设施产物** - Phase 2B (应用开发) 和 Phase 3 (部署) 使用的配置文件

---

## Phase 2A 范围及目标

### Phase 2A 覆盖的内容

- AWS 账户设置和凭证配置
- VPC 和网络基础设施
- 安全组和 IAM 角色配置
- EC2 实例模板
- 应用负载均衡器 (ALB) 设置
- 自动扩展组 (ASG) 配置
- CloudWatch 监控设置
- 基础设施验证和健康检查

### Phase 2A 不覆盖的内容

- **应用代码** (Phase 2B 覆盖)
- **EC2 部署** (Phase 3 覆盖)
- **实验执行** (Phase 4-5 覆盖)
- **分析** (Phase 6-7 覆盖)

### 成功标准

- ✅ 所有 AWS 资源已部署并验证
- ✅ 基础设施配置文件已创建 (JSON)
- ✅ 安全组已正确配置
- ✅ EC2 实例已启动并验证
- ✅ ALB 和 ASG 准备好接收流量
- ✅ CloudWatch 监控已激活

---

## Phase 2A 脚本

所有脚本位于 `scripts/` 目录，使用 **boto3** (不使用 AWS CLI 子进程调用)。

### 1. IAM 角色设置
**文件**: `scripts/setup_iam_role.py`

**用途**: 为 EC2 实例创建 IAM 角色和实例配置文件

**它的作用**:
- 使用 EC2 信任策略创建 IAM 角色
- 附加 CloudWatch 监控策略
- 附加 S3 访问策略 (如果需要)
- 为 EC2 启动创建实例配置文件

**前置要求**:
- AWS 凭证已配置
- IAM 权限创建角色和附加策略

**使用**:
```bash
python scripts/setup_iam_role.py
```

**输出**:
- IAM 角色: `autoscaling-experiment-role`
- 实例配置文件: `autoscaling-experiment-instance-profile`

**验证**:
```bash
aws iam get-role --role-name autoscaling-experiment-role
aws iam list-instance-profiles --query 'InstanceProfiles[*].InstanceProfileName'
```

---

### 2. 安全组设置
**文件**: `scripts/setup_security_groups.py`

**用途**: 创建 VPC 和安全组，配置适当的防火墙规则

**它的作用**:
- 使用可配置的 CIDR 块创建 VPC
- 创建公有/私有子网
- 为出站流量创建 NAT 网关
- 为 ALB 创建安全组 (入站: HTTP 80, HTTPS 443)
- 为 EC2 实例创建安全组 (入站: 来自 ALB)
- 创建 bastion/SSH 安全组 (可选)

**前置要求**:
- AWS 凭证已配置
- EC2 权限创建 VPC 和安全组

**使用**:
```bash
python scripts/setup_security_groups.py
```

**输出**:
- VPC 和子网
- 已配置的安全组
- 配置保存到 `infrastructure/security-config.json`

**验证**:
```bash
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,Tags]'
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,GroupName]'
```

---

### 3. ALB 设置
**文件**: `scripts/setup_alb.py`

**用途**: 创建和配置应用负载均衡器

**它的作用**:
- 在公有子网中创建 ALB
- 为 EC2 实例创建目标组
- 配置健康检查参数
- 为 HTTP 流量设置监听器 (端口 80)
- 生成 ALB DNS 名称供后续使用

**前置要求**:
- VPC 和子网已创建 (来自 setup_security_groups.py)
- 安全组已创建

**使用**:
```bash
python scripts/setup_alb.py
```

**输出**:
- 应用负载均衡器已创建
- 目标组已配置
- DNS 名称保存到 `infrastructure/alb-config.json`

**验证**:
```bash
aws elbv2 describe-load-balancers --query 'LoadBalancers[*].[LoadBalancerName,DNSName]'
aws elbv2 describe-target-groups --query 'TargetGroups[*].[TargetGroupName,HealthCheckPath]'
```

---

### 4. EC2 实例设置
**文件**: `scripts/setup_instances.py`

**用途**: 使用适当配置启动 EC2 实例

**它的作用**:
- 从启动模板或 AMI 创建 EC2 实例
- 附加 IAM 实例配置文件以进行 CloudWatch 访问
- 配置安全组
- 标记实例以便管理
- 配置 CloudWatch 代理 (可选)
- 将实例 ID 和详情保存到配置

**前置要求**:
- VPC、子网和安全组已创建
- IAM 角色已创建
- AMI 选择

**使用**:
```bash
python scripts/setup_instances.py --count 2 --instance-type t3.micro
```

**输出**:
- EC2 实例已启动
- 实例详情保存到 `infrastructure/instances-config.json`

**验证**:
```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PrivateIpAddress]'
aws ec2 describe-instance-status --query 'InstanceStatuses[*].[InstanceId,InstanceStatus.Status]'
```

---

### 5. 自动扩展组 (ASG) 设置
**文件**: `scripts/setup_asg.py`

**用途**: 为 CPU 和请求率策略创建自动扩展组

**它的作用**:
- 为 EC2 实例创建启动模板
- 创建两个 ASG (每个自动扩缩容策略一个)
- 配置期望容量和扩展策略
- 将 ASG 附加到 ALB 目标组
- 配置扩展指标 (CPU 利用率和自定义请求率)
- 为扩展事件设置 CloudWatch 告警

**前置要求**:
- EC2 实例正在运行 (或使用启动模板)
- ALB 设置创建的目标组

**使用**:
```bash
python scripts/setup_asg.py
```

**输出**:
- 自动扩展组已创建：
  - `experiment-asg-cpu` (基于 CPU 的扩展)
  - `experiment-asg-request` (基于请求率的扩展)
- ASG 配置保存到 `infrastructure/asg-config.json`

**验证**:
```bash
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity,MinSize,MaxSize]'
aws autoscaling describe-scaling-activities --auto-scaling-group-name experiment-asg-cpu --query 'Activities[*].[StartTime,Description,Cause]'
```

---

### 6. 网络配置
**文件**: `scripts/setup_network.py`

**用途**: 配置网络级资源 (子网、NAT、路由表)

**它的作用**:
- 创建 VPC
- 创建公有和私有子网
- 配置路由表
- 为 EC2 出站流量设置 NAT 网关
- 配置 DNS 解析

**前置要求**:
- AWS 凭证已配置
- EC2 权限

**使用**:
```bash
python scripts/setup_network.py
```

**输出**:
- VPC 和子网已配置
- 路由表已创建
- NAT 网关已部署

**验证**:
```bash
aws ec2 describe-subnets --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone]'
aws ec2 describe-route-tables --query 'RouteTables[*].[RouteTableId,Routes[*].[DestinationCidrBlock,GatewayId]]'
aws ec2 describe-nat-gateways --query 'NatGateways[*].[NatGatewayId,State]'
```

---

### 7. 基础设施验证
**文件**: `scripts/verify_infrastructure.py`

**用途**: 验证所有基础设施组件已部署且健康

**它的作用**:
- 检查 VPC 是否存在及配置
- 验证安全组和防火墙规则
- 验证 EC2 实例正在运行
- 检查 ALB 是否活跃且健康检查通过
- 验证 ASG 配置
- 测试 ALB 端点的连接
- 验证 IAM 角色和权限

**前置要求**:
- 所有基础设施设置脚本已执行

**使用**:
```bash
python scripts/verify_infrastructure.py
```

**输出**:
- 每个组件状态的验证报告
- 测试连接的示例 curl 命令
- 如果发现问题，提供修复建议

**示例验证输出**:
```
✅ VPC: vpc-12345 (CIDR: 10.0.0.0/16)
✅ 子网: 4 个子网已配置
✅ 安全组: 3 个组已配置
✅ IAM 角色: autoscaling-experiment-role 存在
✅ EC2 实例: 2 个正在运行 (i-111, i-222)
✅ ALB: ALB 活跃 (DNS: experiment-alb-xxx.us-east-1.elb.amazonaws.com)
✅ 目标组: 2 个健康目标
✅ ASG: 2 个 ASG 已配置 (CPU, 请求率)
✅ CloudWatch: 监控已激活
```

---

### 8. 主部署脚本
**文件**: `scripts/deploy_all.py`

**用途**: 按正确顺序协调所有基础设施设置脚本

**它的作用**:
- 按适当的顺序执行脚本
- 处理错误并提供回滚选项
- 在继续前验证每一步
- 生成最终基础设施报告

**前置要求**:
- AWS 凭证已配置
- 具有适当权限

**使用**:
```bash
# 完整部署
python scripts/deploy_all.py

# 试运行 (无变更)
python scripts/deploy_all.py --dry-run

# 跳到特定步骤
python scripts/deploy_all.py --start-step setup_instances
```

**执行顺序**:
1. `setup_iam_role.py` - 创建 IAM 角色
2. `setup_network.py` - 创建 VPC 和网络
3. `setup_security_groups.py` - 创建安全组
4. `setup_alb.py` - 创建 ALB
5. `setup_instances.py` - 启动 EC2 实例
6. `setup_asg.py` - 创建 ASG
7. `verify_infrastructure.py` - 验证所有内容

**输出**:
- `infrastructure/` 目录包含所有 JSON 配置文件
- 部署日志文件
- 基础设施报告

---

## 基础设施配置文件

所有脚本在 `infrastructure/` 目录中生成 JSON 配置文件：

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

## 部署流程

### 快速开始

```bash
# 1. 导航到项目目录
cd autoscaling-strategy-compare

# 2. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 3. 运行主部署脚本
python scripts/deploy_all.py

# 4. 验证基础设施
python scripts/verify_infrastructure.py

# 5. 记录 ALB DNS 名称供 Phase 2B 和 Phase 3 使用
cat infrastructure/alb-config.json | grep alb_dns_name
```

### 预期输出

Phase 2A 部署成功后：

```
✅ Phase 2A: 基础设施设置完成
- VPC 已创建 (包含公有/私有子网)
- 安全组已配置
- 2 个 EC2 实例正在运行
- ALB 已部署且激活
- 2 个 ASG 已配置 (CPU 和请求率)
- 所有配置文件已保存到 infrastructure/

下一步: Phase 2B (应用开发)
- 使用 ALB DNS: experiment-alb-1234567890.us-east-1.elb.amazonaws.com
- 实现负载生成器、指标收集器、实验运行程序
- 开发 Flask 测试应用
```

---

## 故障排查

### 常见问题

**问题**: IAM 角色创建失败，报 "AccessDenied"
- **解决方案**: 验证您的 AWS 凭证具有 IAM 权限
- **命令**: `aws iam list-roles` (应该成功)

**问题**: VPC 创建失败，报 "InsufficientAddressSpace"
- **解决方案**: 调整 setup_network.py 中的 CIDR 块 (默认: 10.0.0.0/16)
- **备用 CIDR**: 10.1.0.0/16, 10.2.0.0/16, 等等

**问题**: ALB 健康检查显示 "不健康" 的目标
- **解决方案**: Flask 应用尚未部署 (Phase 3 任务)
- **下一步**: Phase 2B 完成后，Phase 3 将部署应用

**问题**: ASG 创建失败，报 "ValidationError"
- **解决方案**: 验证 EC2 实例和目标组创建成功
- **命令**: `python scripts/verify_infrastructure.py`

### 调试命令

```bash
# 检查所有基础设施资源
python scripts/verify_infrastructure.py

# 测试 ALB 连接
ALB_DNS=$(cat infrastructure/alb-config.json | python -c "import sys, json; print(json.load(sys.stdin)['alb_dns_name'])")
curl http://$ALB_DNS/health  # 在 Phase 3 前将失败 (预期)

# 查看部署日志
cat logs/deployment.log

# 检查 CloudWatch 错误
aws logs describe-log-groups --query 'logGroups[*].logGroupName'
```

---

## 下一步: Phase 2B

Phase 2A 完成后，进行 Phase 2B (应用开发)：

1. **创建负载生成器** (`scripts/load_generator.py`)
2. **创建指标收集器** (`scripts/metrics_collector.py`)
3. **创建实验运行程序** (`scripts/experiment_runner.py`)
4. **创建 Flask 测试应用** (`apps/test_app/app.py`)

**Phase 2B 输出**:
- 用于负载测试的功能性 Python 工具
- 具有自动扩缩容友好端点的 Flask 应用
- 测试应用的 Docker 镜像

**Phase 2B 为 Phase 3 需要的产物**:
- `scripts/load_generator.py` - 用于负载生成
- `scripts/metrics_collector.py` - 用于指标收集
- `scripts/experiment_runner.py` - 用于协调
- `apps/test_app/app.py` - 部署到 EC2 实例
- `apps/test_app/Dockerfile` - 用于部署的 Docker 镜像

---

## 跨平台兼容性

所有 Phase 2A 脚本设计用于在以下平台上工作：
- ✅ Windows
- ✅ macOS
- ✅ Linux

**关键兼容性措施**:
- 使用 `pathlib.Path` 而不是字符串路径
- 使用 boto3 (不使用 AWS CLI 子进程调用)
- 为文件 I/O 使用 UTF-8 编码
- 处理 `/` 和 `\` 路径分隔符
- 不使用特定平台的二进制文件

---

## 成本估算

Phase 2A 的估计 AWS 成本 (小时费率, 约值)：

| 资源 | 实例类型 | 数量 | 小时成本 |
|----------|--------------|-----|------------|
| EC2 实例 | t3.micro | 2 | $0.0104 |
| ALB | 标准 | 1 | $0.0225 |
| NAT 网关 | - | 1 | $0.045 |
| **总计** | | | **~$0.08/小时** |

**注意**: Phase 4-5 期间成本因活动扩展而增加，Phase 6-7 期间因持续监控而增加。

---

## Git 提交

Phase 2A 基础设施脚本应提交为：

```bash
git add scripts/setup_*.py scripts/deploy_all.py scripts/verify_infrastructure.py
git commit -m "feat: Phase 2A 基础设施配置脚本

- 添加 IAM 角色设置 (setup_iam_role.py)
- 添加网络配置 (setup_network.py)
- 添加安全组设置 (setup_security_groups.py)
- 添加 ALB 配置 (setup_alb.py)
- 添加 EC2 实例启动 (setup_instances.py)
- 添加 ASG 配置 (setup_asg.py)
- 添加主部署协调 (deploy_all.py)
- 添加基础设施验证 (verify_infrastructure.py)
- 所有脚本使用 boto3 (跨平台兼容)
- 生成基础设施 JSON 配置文件"
```

---

## 参考资料

- **AWS 文档**: https://docs.aws.amazon.com/
- **boto3 参考**: https://boto3.amazonaws.com/v1/documentation/
- **CloudFormation 备选方案**: 基础设施也可通过 CloudFormation 模板部署 (可选)
- **Phase 2B**: 应用开发指南
- **Phase 3**: AWS 部署指南

---

**状态**: ✅ Phase 2A 完成

所有基础设施脚本已创建并验证。准备好进行 Phase 2B (应用开发)。
