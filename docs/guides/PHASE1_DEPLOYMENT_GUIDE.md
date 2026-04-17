# Phase 1: AWS 基础设施实现指南

## 概述

本指南说明如何使用 Phase 1 基础设施部署脚本为自动扩缩容策略对比实验配置完整的 AWS 基础设施。

## 架构

```
VPC (10.0.0.0/16)
├── 公有子网 (10.0.1.0/24, 10.0.2.0/24) - ALB
├── 私有子网 (10.0.11.0/24, 10.0.12.0/24) - 实例
├── 互联网网关
├── 安全组 (ALB, App)
├── 应用负载均衡器 (experiment-alb)
│   ├── 目标组: tg-cpu-asg
│   └── 目标组: tg-request-asg
├── 自动扩展组: asg-cpu
│   └── 启动模板: app-cpu-lt
└── 自动扩展组: asg-request
    └── 启动模板: app-request-lt
```

## 前置要求

1. **AWS 账户**已配置凭证
   ```bash
   aws configure
   # 输入 AWS 访问密钥 ID、秘密访问密钥、区域 (us-east-1)
   ```

2. **Python 3.8+** 和 boto3
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **AWS 权限**: 您的 IAM 用户需要以下权限：
   - EC2 (VPC、子网、安全组、实例)
   - IAM (角色、实例配置文件)
   - ELB (应用负载均衡器、目标组)
   - Auto Scaling (自动扩展组、策略)
   - CloudWatch (监控)

## 快速开始

### 选项 1: 一键部署 (推荐)

用一条命令部署整个基础设施：

```bash
python scripts/deploy_all.py
```

这将执行以下操作：
1. 创建 VPC 和网络
2. 创建 IAM 角色
3. 创建安全组
4. 创建启动模板
5. 创建 ALB
6. 创建 ASG
7. 验证一切正常工作

**预期耗时**: 5-10 分钟

### 选项 2: 逐步部署

逐个运行各个脚本：

```bash
# 1. 网络基础设施 (VPC, 子网, IGW)
python scripts/setup_network.py
# 输出: infrastructure/network-config.json

# 2. IAM 角色和策略
python scripts/setup_iam_role.py
# 输出: infrastructure/iam-config.json

# 3. 安全组
python scripts/setup_security_groups.py
# 输出: infrastructure/security-groups-config.json

# 4. 启动模板
python scripts/setup_instances.py
# 输出: infrastructure/launch-templates-config.json

# 5. 应用负载均衡器
python scripts/setup_alb.py
# 输出: infrastructure/alb-config.json

# 6. 自动扩展组
python scripts/setup_asg.py
# 输出: infrastructure/asg-config.json

# 7. 验证
python scripts/verify_infrastructure.py
# 输出: infrastructure/verification-report.json
```

### 选项 3: 验证现有基础设施

如果您已经部署了基础设施，只想验证它：

```bash
python scripts/deploy_all.py --verify-only
```

## 输出文件

所有配置文件保存到 `infrastructure/` 目录：

```
infrastructure/
├── network-config.json              # VPC、子网、IGW ID
├── iam-config.json                  # IAM 角色和实例配置文件 ARN
├── security-groups-config.json      # 安全组 ID
├── launch-templates-config.json     # 启动模板 ID
├── alb-config.json                  # 负载均衡器 DNS 和目标组 ARN
├── asg-config.json                  # 自动扩展组名称
├── verification-report.json         # 所有组件状态
└── deployment-log.json              # 部署执行日志
```

每个文件都是 JSON 格式，便于其他脚本解析。

## 将创建的资源

### 网络 (setup_network.py)
- **VPC**: 10.0.0.0/16
- **公有子网**: 10.0.1.0/24 (us-east-1a), 10.0.2.0/24 (us-east-1b)
- **私有子网**: 10.0.11.0/24 (us-east-1a), 10.0.12.0/24 (us-east-1b)
- **互联网网关**: 用于公有子网路由
- **路由表**: 公有 (到 IGW) 和私有 (隔离)

### IAM (setup_iam_role.py)
- **角色**: `EC2RoleForExperiment`
- **策略**:
  - CloudWatchAgentServerPolicy (发送指标)
  - AmazonS3ReadOnlyAccess (读取配置)
  - AmazonSSMManagedInstanceCore (远程访问)
  - CloudWatchMetrics (自定义指标)
- **实例配置文件**: `EC2InstanceProfileForExperiment`

### 安全组 (setup_security_groups.py)
- **ALB 安全组** (alb-sg):
  - 入站: HTTP 80、HTTPS 443 来自任何地方
  - 出站: 端口 8080 到 app-sg
  
- **App 安全组** (app-sg):
  - 入站: 来自 ALB 的端口 8080、来自任何地方的端口 22 (SSH)
  - 出站: HTTP 80、HTTPS 443 到任何地方

### 启动模板 (setup_instances.py)
- **app-cpu-lt**: 运行 CPU 监控应用
  - 实例类型: t3.micro (免费层)
  - 向 CloudWatch 发布 CPU 和内存指标
  
- **app-request-lt**: 运行请求率监控应用
  - 实例类型: t3.micro
  - 向 CloudWatch 发布请求率指标

### 负载均衡器 (setup_alb.py)
- **应用负载均衡器**: `experiment-alb`
  - 部署在公有子网中
  - 在 HTTP 端口 80 上监听
  
- **目标组**:
  - `tg-cpu-asg`: 用于 CPU 策略实验
  - `tg-request-asg`: 用于请求率策略实验
  - 健康检查: 在端口 8080 上获取 /health

### 自动扩展组 (setup_asg.py)
- **asg-cpu**:
  - 最小: 1, 最大: 5, 期望: 2 实例
  - 使用 app-cpu-lt 启动模板
  - 扩展策略: 目标 CPU 50%
  - 冷却时间: 60秒 扩出，300秒 扩入

- **asg-request**:
  - 最小: 1, 最大: 5, 期望: 2 实例
  - 使用 app-request-lt 启动模板
  - 扩展策略: 目标请求率每个实例 10 req/s
  - 冷却时间: 60秒 扩出，300秒 扩入

## 访问您的应用

部署完成后，您的应用可在以下地址访问：

```
http://<ALB-DNS-Name>
```

DNS 名称在 `setup_alb.py` 的末尾打印出来并保存在 `infrastructure/alb-config.json` 中。

**示例**: `http://experiment-alb-123456.us-east-1.elb.amazonaws.com`

**注意**: 允许 1-2 分钟让实例启动并通过健康检查。

## 验证

要检查所有组件的状态：

```bash
python scripts/verify_infrastructure.py
```

这将：
- ✓ 验证 VPC 和子网存在
- ✓ 检查安全组配置
- ✓ 验证 ALB 活跃且 DNS 可用
- ✓ 检查目标组有健康的实例
- ✓ 验证自动扩展组运行中
- ✓ 按状态列出所有实例
- ✓ 生成验证报告 (verification-report.json)

## 故障排查

### 实例未启动
- 检查 IAM 角色是否正确附加
- 验证安全组规则允许出站流量
- 检查 EC2 控制台查看实例启动错误
- 查看 CloudWatch 日志了解用户数据脚本错误

### ALB 显示不健康的目标
- 等待 2-3 分钟让实例启动
- 检查应用是否在端口 8080 上监听
- 验证 /health 端点返回 HTTP 200
- 检查安全组允许来自 ALB 的 8080

### 无法连接到应用
- 验证 ALB 有公有 IP
- 检查安全组允许来自 0.0.0.0/0 的入站 80
- 确保实例处于运行状态
- 检查 ALB 目标组健康状况

### 扩展不发生
- 验证 CloudWatch 自定义指标正在发布
- 检查自动扩展策略存在
- 查看应用中的 CloudWatch 日志

## 清理

要删除所有 AWS 资源：

```bash
python scripts/cleanup_infrastructure.py  # Phase 1b 中即将推出
```

或通过 AWS 控制台手动删除：
1. 删除自动扩展组
2. 删除负载均衡器
3. 删除启动模板
4. 删除安全组
5. 删除 VPC (自动删除子网和 IGW)
6. 删除 IAM 角色

## 成本考虑

**为期 1 周实验的估计成本:**
- **t3.micro 实例**: ~$1-2 (符合免费层)
- **ALB**: ~$15-20
- **数据传输**: $0-1
- **总计**: ~$15-25

**成本节省技巧:**
- 未进行实验时删除基础设施
- 使用最小实例类型 (t3.micro)
- 监控 CloudWatch 计费警报

## 后续步骤

在 Phase 1 部署后：
1. **Phase 2**: 部署负载生成工具
2. **Phase 3**: 运行自动扩展实验
3. **Phase 4**: 收集和分析指标
4. **Phase 5**: 生成报告

## 支持

如有问题：
1. 检查日志: `infrastructure/deployment-log.json`
2. 查看验证报告: `infrastructure/verification-report.json`
3. 检查 AWS CloudTrail 查看 API 错误
4. 运行 `python scripts/verify_infrastructure.py --verbose`

## 脚本参考

### deploy_all.py
编排所有部署步骤的顺序。

```bash
python scripts/deploy_all.py                    # 完整部署
python scripts/deploy_all.py --verify-only      # 仅验证
python scripts/deploy_all.py --skip setup_network.py  # 跳过一个步骤
```

### setup_network.py
创建 VPC、子网、IGW 和路由表。

### setup_iam_role.py
创建具有必要权限的 IAM 角色。

### setup_security_groups.py
创建并配置安全组。

### setup_instances.py
创建具有用户数据脚本的 EC2 启动模板。

### setup_alb.py
创建应用负载均衡器和目标组。

### setup_asg.py
创建带有扩展策略的自动扩展组。

### verify_infrastructure.py
验证所有组件已创建且健康。

---

**创建时间**: 2025年4月17日
**最后更新**: 2025年4月17日
**版本**: 1.0
