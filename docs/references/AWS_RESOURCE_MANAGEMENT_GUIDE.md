# 🔍 AWS 资源管理完整指南

## 现状分析

你的项目使用了以下 AWS 资源（Phase 1-6）：

```
✅ 已部署的资源：
├── VPC (Virtual Private Cloud)
├── 公网/私网子网
├── Internet Gateway
├── 2 个 Auto Scaling Groups (ASG)
│   ├── asg-cpu (CPU利用率策略)
│   └── asg-request (请求率策略)
├── Application Load Balancer (ALB)
├── 4 个 EC2 实例 (t3.micro)
│   └── 自动扩展管理
├── IAM 角色和权限
└── Security Groups (防火墙规则)
```

---

## 💰 成本分析

### 当前成本（t3.micro 示例）

| 资源 | 单价/小时 | 4 小时成本 | 8 小时成本 | 说明 |
|------|---------|---------|---------|------|
| **EC2 (t3.micro)** | $0.0104/小时 | $0.042 | $0.083 | x4 实例 |
| **ALB** | $0.0225/小时 | $0.090 | $0.180 | 负载均衡器 |
| **EBS 存储** | ~$0.1/月 | ~$0.003 | ~0.005 | 每个实例 |
| **数据传输** | 较小 | ~$0.01 | ~0.02 | 通常免费或很少 |
| **总计** | - | **~$0.15** | **~$0.30** | 4小时/8小时 |

**结论**: 十几个小时的成本约 **$0.50-1.00** USD (2-5 RMB)，实际上很便宜。

---

## 🛑 删除后重建的时间成本

### 如果完全删除资源

**重建时间估计：**

| 步骤 | 所需时间 | 备注 |
|------|--------|------|
| 创建 VPC + 网络 | 3-5 分钟 | 自动化脚本 |
| 创建 IAM 角色 | 1-2 分钟 | 快速 |
| 创建安全组 | 2-3 分钟 | 快速 |
| 创建 ALB | 3-5 分钟 | 需要等待激活 |
| 创建 Launch Template | 1-2 分钟 | 快速 |
| 创建 ASG | 5-10 分钟 | 等待实例启动 |
| 部署 Flask 应用 | 5-10 分钟 | 实例启动 + 健康检查 |
| **总计** | **20-37 分钟** | 完全重建 |

**问题：** 
- ❌ 重建很费时
- ❌ 你的项目 Phase 1-6 都依赖于这些资源
- ❌ 重建会重新初始化数据

---

## ✅ 更好的方案：暂停而不是删除

### 方案 1️⃣ : 停止实例（最推荐）

**优点：**
- ✅ 保留所有配置
- ✅ 保留数据和状态
- ✅ 快速重启（1-2 分钟）
- ✅ **ASG 停止后不再扩展，成本大幅降低**

**成本对比：**
```
运行中:      $0.015/小时 (EC2) + $0.0225/小时 (ALB) = $0.0375/小时
停止后:      $0 (EC2) + $0.0225/小时 (ALB) = $0.0225/小时
节省:        40% 的成本
```

**如何操作：**

```bash
# 停止 ASG 中的所有实例
python scripts/stop_instances.py

# 或手动停止
aws ec2 stop-instances --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e --region us-east-1

# 查看实例状态
aws ec2 describe-instances --region us-east-1 --query 'Reservations[].Instances[].{ID:InstanceId, State:State.Name}'
```

**重启（快速恢复）：**
```bash
# 启动实例
aws ec2 start-instances --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e --region us-east-1

# 等待健康检查
python scripts/verify_infrastructure.py
```

---

### 方案 2️⃣ : 缩小 ASG（折中方案）

**操作：** 将 ASG 的最小实例数设为 0

```bash
# 缩小 CPU ASG 到 0
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name asg-cpu \
  --min-size 0 \
  --desired-capacity 0 \
  --region us-east-1

# 缩小 Request ASG 到 0
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name asg-request \
  --min-size 0 \
  --desired-capacity 0 \
  --region us-east-1
```

**恢复：**
```bash
# 恢复到原状态（2 个实例）
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name asg-cpu \
  --min-size 1 \
  --desired-capacity 2 \
  --region us-east-1
```

---

### 方案 3️⃣ : 保持 ALB，停止实例

这是最实用的方案：

```bash
# Step 1: 停止所有 EC2 实例
aws ec2 stop-instances --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e --region us-east-1

# Step 2: 验证状态
aws ec2 describe-instances --region us-east-1 --instance-ids i-0f15b92f0d225b987

# 输出应该显示: "State": "stopped"

# Step 3: 十几小时后，快速启动
aws ec2 start-instances --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e --region us-east-1

# 等待实例启动和健康检查通过（约 2-3 分钟）
```

---

## 📋 对比表：各种方案

| 方案 | 停止时间 | 重启时间 | 数据保留 | 成本节省 | 对项目影响 |
|------|--------|--------|--------|--------|----------|
| 完全删除 | 即时 | **20-37 分钟** | ❌ 丢失 | 100% | ❌ 需重建 |
| 停止实例 | 2-3 分钟 | **1-2 分钟** | ✅ 保留 | **60%** | ✅ 无影响 |
| 缩小 ASG | 2-3 分钟 | **5-10 分钟** | ✅ 保留 | 40% | ✅ 无影响 |
| 什么都不做 | - | - | ✅ 保留 | 0% | ✅ 继续运行 |

---

## 🎯 我的建议

### 对你的情况最优方案：

```bash
# 离开前（十几小时前）
aws ec2 stop-instances \
  --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e \
  --region us-east-1

# 成本: 只需支付 ALB ($0.18-0.27) + 存储 (~$0.01)
# 总计: 约 $0.20 (1 RMB)

# 回来后（快速恢复）
aws ec2 start-instances \
  --instance-ids i-0f15b92f0d225b987 i-0105de960c2b06f2e i-0b753c4faa63e14ac i-0bd201ef2a892ea3e \
  --region us-east-1

# 等待 2-3 分钟后，所有东西恢复如初，继续做实验
```

### 成本对比（10 小时离开）：

```
方案A - 什么都不做:
  成本 = $0.0375/小时 × 10 小时 = $0.375 (~2 RMB)

方案B - 停止实例（推荐）:
  成本 = ($0.0225 ALB + 存储) × 10 小时 ≈ $0.25 (~1.25 RMB)
  
  节省: $0.125 (省钱不多，但恢复快)
```

---

## ⚠️ 注意事项

1. **EBS 存储费用** - 停止实例后，存储仍会收费（很便宜）
2. **Elastic IP** - 如果你有绑定弹性 IP，也会继续收费
3. **ALB** - 负载均衡器无论如何都会收费，除非删除
4. **快照** - 如果需要长期保存，考虑创建 AMI 快照

---

## 🔧 快速命令参考

### 查看所有实例状态
```bash
aws ec2 describe-instances --region us-east-1 \
  --query 'Reservations[].Instances[].{ID:InstanceId, Type:InstanceType, State:State.Name, LaunchTime:LaunchTime}' \
  --output table
```

### 查看 ASG 配置
```bash
aws autoscaling describe-auto-scaling-groups --region us-east-1 \
  --query 'AutoScalingGroups[].{Name:AutoScalingGroupName, MinSize:MinSize, MaxSize:MaxSize, DesiredCapacity:DesiredCapacity, Instances:Instances[].{InstanceId:InstanceId, HealthStatus:HealthStatus}}' \
  --output table
```

### 查看 ALB 状态
```bash
aws elbv2 describe-load-balancers --region us-east-1 \
  --query 'LoadBalancers[].{Name:LoadBalancerName, DNSName:DNSName, State:State.Code}' \
  --output table
```

### 查看 EC2 成本预估
```bash
# 估算当前运行成本（十几小时）
echo "当前运行成本估算（t3.micro x4 + ALB）:"
echo "10 小时: 约 \$0.375 (2 RMB)"
echo "20 小时: 约 \$0.75  (4 RMB)"
echo "停止后 10 小时: 约 \$0.25 (1.25 RMB)"
```

---

## 📚 相关文档

- `docs/guides/PHASE2A_DEPLOYMENT_GUIDE.md` - 基础设施部署指南
- `docs/plans/PHASE2A_INFRASTRUCTURE_SETUP.md` - 基础设施设置计划
- `docs/plans/PROJECT_EXECUTION_PLAN.md` - 项目执行计划
- `infrastructure/` - AWS 配置文件（VPC、ALB、ASG 等）
- `scripts/aws_utils.py` - AWS 工具类和命令

---

**最后更新**: 2026-04-18  
**适用阶段**: Phase 1-6  
**作者**: CHEN Sijie (jaycee6666)
