# Phase 1: AWS基础设施代码 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 使用本地AWS CLI创建完整的云基础设施(VPC、安全组、IAM、实例模板、ALB)，支持后续自动扩展实验

**Architecture:** 采用模块化设计，每个基础设施组件由独立Python脚本管理，通过AWS CLI执行，输出配置文件供后续使用

**Tech Stack:** AWS CLI v2, Python 3.8+, boto3, JSON配置

**Timeline:** Week 1-2 (8-14天)

**Team:** 可并行工作，通过Git分支隔离

---

## 📐 AWS基础设施架构

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Account                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │              VPC (vpc-xxxxx)                         │   │
│  │  CIDR: 10.0.0.0/16                                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  ┌─────────────────┐  ┌─────────────────┐           │   │
│  │  │ Public Subnet 1 │  │ Public Subnet 2 │           │   │
│  │  │ 10.0.1.0/24     │  │ 10.0.2.0/24     │           │   │
│  │  └─────────────────┘  └─────────────────┘           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐           │   │
│  │  │ Private Sub. 1  │  │ Private Sub. 2  │           │   │
│  │  │ 10.0.11.0/24    │  │ 10.0.12.0/24    │           │   │
│  │  └─────────────────┘  └─────────────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↑                                                │
│        Internet Gateway                                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Auto Scaling Group (基于CPU)                        │   │
│  │  └─ EC2实例 (t3.micro - 测试用)                      │   │
│  │  └─ Launch Template (app-cpu-lt)                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Auto Scaling Group (基于请求率)                     │   │
│  │  └─ EC2实例 (t3.micro - 测试用)                      │   │
│  │  └─ Launch Template (app-request-lt)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Application Load Balancer (ALB)                     │   │
│  │  └─ 目标组(CPU ASG)                                  │   │
│  │  └─ 目标组(Request ASG)                              │   │
│  │  └─ 监听器:80 → 目标组                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  IAM Role: EC2RoleForExperiment                              │
│  ├─ Policy: CloudWatch写权限 (发送指标)                     │
│  ├─ Policy: S3读写权限 (存储数据)                          │
│  └─ Policy: Systems Manager权限 (远程管理)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 实现顺序 (关键依赖链)

```
Step 1: setup_network.py
    ↓ (创建VPC、子网、IGW)
    ├─→ Step 2: setup_iam_role.py
    │       ↓ (创建IAM角色)
    │       ├─→ Step 3: setup_security_groups.py
    │               ↓ (创建安全组)
    │               ├─→ Step 4: setup_instances.py
    │               │       ↓ (创建启动模板)
    │               │       └─→ Step 5: setup_alb.py
    │               │               ↓ (创建ALB)
    │               │               └─→ Step 6: setup_asg.py
    │               │                       ↓ (创建Auto Scaling Groups)
    │               │                       └─→ Step 7: verify_infrastructure.py
    │               │                               ↓ (验证所有组件)
    │               └───────────────────────────────┘
    └───────────────────────────────────────────────────────┘

说明: 绿色箭头表示依赖关系
     某些步骤可以并行(如IAM和网络并行)
     但大多数步骤需要等前一步完成
```

---

## 📋 详细任务分解

### Task 1: 创建网络基础设施 (VPC、子网、IGW)

**文件:**
- Create: `scripts/setup_network.py` (300行)
- Output: `infrastructure/network-config.json` (保存VPC/子网ID)
- Reference: `docs/ARCHITECTURE.md` (新建)

**需要输出的配置:**
```json
{
  "vpc_id": "vpc-xxxxx",
  "public_subnet_1_id": "subnet-xxxxx",
  "public_subnet_2_id": "subnet-xxxxx",
  "private_subnet_1_id": "subnet-xxxxx",
  "private_subnet_2_id": "subnet-xxxxx",
  "internet_gateway_id": "igw-xxxxx",
  "route_table_public_id": "rtb-xxxxx",
  "route_table_private_id": "rtb-xxxxx"
}
```

**实现要点:**
- VPC CIDR: 10.0.0.0/16
- 2个公网子网: 10.0.1.0/24, 10.0.2.0/24
- 2个私网子网: 10.0.11.0/24, 10.0.12.0/24
- 创建Internet Gateway
- 创建路由表(公网和私网)
- 关联子网到路由表

**预期耗时:** 2-3小时

---

### Task 2: 创建IAM角色和策略

**文件:**
- Create: `scripts/setup_iam_role.py` (250行)
- Output: `infrastructure/iam-config.json`

**需要创建的角色:**
```
EC2RoleForExperiment
├─ AssumeRolePolicyDocument: EC2服务可以假设此角色
├─ CloudWatchAgentServerPolicy: 发送CloudWatch指标
├─ AmazonS3ReadOnlyAccess: 读S3配置
└─ AmazonSSMManagedInstanceCore: Systems Manager远程访问
```

**实现要点:**
- 创建IAM角色
- 附加策略
- 创建实例配置文件(Instance Profile)

**预期耗时:** 1-2小时

---

### Task 3: 创建安全组

**文件:**
- Create: `scripts/setup_security_groups.py` (250行)
- Output: `infrastructure/security-groups-config.json`

**需要创建的安全组:**

1. **ALB安全组** (alb-sg)
   - 入站: HTTP 80 (0.0.0.0/0)
   - 入站: HTTPS 443 (0.0.0.0/0)
   - 出站: 所有流量到EC2安全组

2. **EC2应用安全组** (app-sg)
   - 入站: 8080 (来自ALB安全组)
   - 入站: 22 (来自你的IP用于调试)
   - 出站: 所有流量(443用于下载包、CloudWatch等)

3. **可选: 测试用安全组** (test-sg)
   - 用于从你的机器运行测试

**实现要点:**
- 使用VPC ID(从Task 1输出)
- 创建入站/出站规则
- 安全组间引用

**预期耗时:** 1-2小时

---

### Task 4: 创建EC2启动模板

**文件:**
- Create: `scripts/setup_instances.py` (400行)
- Output: `infrastructure/launch-templates-config.json`

**需要创建的启动模板:**

1. **CPU监控应用模板** (app-cpu-lt)
   ```
   - AMI: Amazon Linux 2 (最新)
   - 实例类型: t3.micro (免费套餐/便宜)
   - IAM Role: EC2RoleForExperiment
   - 安全组: app-sg
   - User Data脚本:
     * 安装Docker
     * 拉取/运行测试应用
     * 配置CloudWatch代理(发送CPU指标)
   ```

2. **请求率监控应用模板** (app-request-lt)
   ```
   - 类似CPU模板,但配置不同的应用或指标
   ```

**实现要点:**
- 获取最新Amazon Linux 2 AMI ID
- 编写User Data脚本(启动应用)
- 标签: Environment=experiment, Strategy=cpu/request
- 设置根卷配置(20GB gp3)

**预期耗时:** 2-3小时

---

### Task 5: 创建应用负载均衡器(ALB)

**文件:**
- Create: `scripts/setup_alb.py` (300行)
- Output: `infrastructure/alb-config.json`

**需要创建:**

1. **ALB本身**
   - 名称: experiment-alb
   - Scheme: internet-facing
   - 子网: 公网子网1, 公网子网2
   - 安全组: ALB安全组

2. **目标组1** (tg-cpu-asg)
   - 协议: HTTP:8080
   - 健康检查: GET /health (HTTP 200)
   - 粘性: 禁用(用于测试)

3. **目标组2** (tg-request-asg)
   - 协议: HTTP:8080
   - 健康检查: GET /health

4. **监听器**
   - 端口80 → 转发到目标组1(先用CPU)
   - 后续可修改规则转到目标组2

**实现要点:**
- 使用VPC和子网ID(从Task 1)
- 目标组配置健康检查超时
- 为ALB标签记录

**预期耗时:** 1-2小时

---

### Task 6: 创建Auto Scaling Groups (ASG)

**文件:**
- Create: `scripts/setup_asg.py` (350行)
- Output: `infrastructure/asg-config.json`

**需要创建的ASG:**

1. **ASG-CPU** (experiment-asg-cpu)
   ```
   - 启动模板: app-cpu-lt
   - 最小大小: 1
   - 所需大小: 2
   - 最大大小: 5
   - 子网: 私网子网1, 私网子网2
   - 目标组: tg-cpu-asg
   - 策略: 基于CPU利用率 (≥70% 扩展, ≤30% 缩容)
   ```

2. **ASG-Request** (experiment-asg-request)
   ```
   - 启动模板: app-request-lt
   - 最小大小: 1
   - 所需大小: 2
   - 最大大小: 5
   - 子网: 私网子网1, 私网子网2
   - 目标组: tg-request-asg
   - 策略: 基于请求数 (≥1000req/min 扩展, ≤200req/min 缩容)
   ```

**实现要点:**
- 使用启动模板ID(从Task 4)
- 设置扩展策略(Target Tracking)
- 配置健康检查(ELB, 300秒宽限期)
- 记录ASG名称供后续使用

**预期耗时:** 2-3小时

---

### Task 7: 验证基础设施

**文件:**
- Create: `scripts/verify_infrastructure.py` (200行)
- Output: `infrastructure/verification-report.json`

**需要验证的内容:**

```
✓ VPC和子网创建成功
✓ Internet Gateway连接到VPC
✓ 路由表正确配置
✓ 安全组规则正确
✓ IAM角色创建成功
✓ EC2启动模板有效
✓ ALB已创建并在活跃状态
✓ 目标组健康状态正常
✓ ASG创建并有正确的实例
✓ 实例通过健康检查
✓ ALB DNS名称可访问
```

**实现要点:**
- 查询每个资源的状态
- 生成HTML报告(便于查看)
- 输出所有重要ID和端点

**预期耗时:** 1-2小时

---

### Task 8: 一键部署脚本

**文件:**
- Create: `scripts/deploy_all.py` (150行)

**功能:**
- 按顺序调用所有setup脚本
- 处理错误和依赖检查
- 生成最终配置汇总

**实现要点:**
- 检查AWS凭证
- 检查前置条件
- 捕获每个脚本的输出
- 最后显示成功摘要

**预期耗时:** 1小时

---

## 📁 文件结构

```
autoscaling-strategy-compare/
├── scripts/
│   ├── setup_network.py           [NEW - Task 1]
│   ├── setup_iam_role.py          [NEW - Task 2]
│   ├── setup_security_groups.py   [NEW - Task 3]
│   ├── setup_instances.py         [NEW - Task 4]
│   ├── setup_alb.py               [NEW - Task 5]
│   ├── setup_asg.py               [NEW - Task 6]
│   ├── verify_infrastructure.py   [NEW - Task 7]
│   └── deploy_all.py              [NEW - Task 8]
│
├── infrastructure/                 [NEW - 输出目录]
│   ├── network-config.json        [Task 1输出]
│   ├── iam-config.json            [Task 2输出]
│   ├── security-groups-config.json [Task 3输出]
│   ├── launch-templates-config.json [Task 4输出]
│   ├── alb-config.json            [Task 5输出]
│   ├── asg-config.json            [Task 6输出]
│   └── verification-report.json   [Task 7输出]
│
└── docs/
    ├── ARCHITECTURE.md            [NEW - 架构设计]
    └── PHASE1_PROGRESS.md         [NEW - 进度追踪]
```

---

## 🔑 关键设计决策

| 决策 | 选择 | 原因 |
|-----|------|------|
| 实例类型 | t3.micro | 免费套餐/成本低，适合测试 |
| 子网数量 | 4个(2公网+2私网) | 高可用性，跨AZ分布 |
| ALB vs NLB | ALB | HTTP应用更合适 |
| 配置管理 | JSON文件 | 简单，易于版本控制，可读性强 |
| ASG策略 | Target Tracking | 自动调整，无需手动调参 |
| VPC CIDR | 10.0.0.0/16 | RFC1918标准，足够灵活 |

---

## 👥 团队并行工作建议

由于大多数任务有依赖关系，不能完全并行，但可以：

**方案A: 顺序完成(安全)**
```
Day 1: Task 1-2 (网络+IAM)
Day 2: Task 3-4 (安全组+实例模板)
Day 3: Task 5-6 (ALB+ASG)
Day 4: Task 7-8 (验证+一键部署)
```

**方案B: 局部并行**
```
成员A: Task 1 (网络)          | 成员B: 学习/准备文档
成员A: Task 3 (安全组)        | 成员B: Task 2 (IAM) [可并行]
成员A: Task 4 (实例模板)      | 成员B: 编写测试应用
成员A: Task 5 (ALB)           | 成员B: 准备监控脚本
成员A: Task 6 (ASG)           | 成员B: 准备数据收集脚本
合并: Task 7-8 (验证+部署)
```

---

## ✅ 完成标准

每个Task完成后，需要验证:

```
□ 代码已编写并测试
□ 生成了正确的JSON配置文件
□ AWS资源已创建(aws ec2/elbv2等命令验证)
□ 输出已提交到git
□ 文档已更新
□ 下一个Task可以使用上一步的输出
```

---

## 📊 预期时间分配

| Task | 预计时长 | 实际 | 备注 |
|------|---------|------|------|
| 1. 网络基础设施 | 2-3h | | VPC、子网、IGW |
| 2. IAM角色 | 1-2h | | 创建角色和策略 |
| 3. 安全组 | 1-2h | | 入站/出站规则 |
| 4. 启动模板 | 2-3h | | AMI、User Data脚本 |
| 5. ALB | 1-2h | | 目标组、监听器 |
| 6. ASG | 2-3h | | 扩展策略配置 |
| 7. 验证 | 1-2h | | 检查所有资源 |
| 8. 一键部署 | 1h | | 整合所有脚本 |
| **总计** | **11-18h** | | Week 1完成 |

---

## 🎯 成功标志

Phase 1完成时:

✅ 所有8个Python脚本已编写并测试
✅ AWS基础设施已部署(可通过AWS控制台验证)
✅ ALB DNS名称可访问应用
✅ ASG正常运行2个实例
✅ 所有配置已保存到JSON文件
✅ 一键部署脚本正常工作
✅ 所有代码已推送到GitHub
✅ 文档已更新

**此时可以进入Phase 2: 测试应用开发**

---

## 📚 参考资源

- AWS VPC文档: https://docs.aws.amazon.com/vpc/
- AWS EC2文档: https://docs.aws.amazon.com/ec2/
- AWS ALB文档: https://docs.aws.amazon.com/elasticloadbalancing/
- AWS ASG文档: https://docs.aws.amazon.com/autoscaling/

---

**Plan Version:** 1.0
**Created:** April 17, 2026
**Status:** Ready for Implementation
