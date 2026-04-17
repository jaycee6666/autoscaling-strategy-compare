# 项目执行计划 (Project Execution Plan)

> ⚠️ **注意**: 这是**最新版执行计划**，采用 Phase 1, 2A, 2B, 3, 4-6, 7 结构。
> 
> 此文档定义了从基础设施准备到最终报告的完整项目周期。详细的实施指南和计划请参考 `docs/plans/PLANS_INDEX.md`。

---

## 📋 项目概览

**项目名称**: Comparative Analysis of Autoscaling Strategies: Resource-Based CPU Utilization vs. Workload-Based Request Rate

**执行方式**: 本地 AWS CLI（Windows/macOS/Linux）跨平台

**总时长**: 约 8-10 周（从现在到 2026 年 4 月 24 日）

**平台支持**: ✅ Windows ✅ macOS ✅ Linux

**Deadline**: 2026 年 4 月 24 日 23:59 HKT

---

## ⏰ 总体时间轴

```
Week 1-2:   Phase 1 - AWS 基础设施代码编写
            Phase 2A - 基础设施配置脚本
            
Week 2-3:   Phase 2B - 应用工具开发 (负载生成器、指标收集器)
            
Week 3-4:   Phase 3 - 部署到 AWS & 验证
            
Week 5-6:   Phase 4-6 - 实验执行 & 数据分析
            (4-5: Autoscaling Experiments, 6: Analysis & Winner Determination)
            
Week 7-8:   Phase 7 - 最终报告撰写 & 演示视频制作
            
Week 9-10:  最终检查 & 项目提交
```

---

## 🚀 快速开始

```bash
# 1. 克隆或进入项目
cd autoscaling-strategy-compare

# 2. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 查看具体Phase的执行指南
# Phase 1: docs/plans/PHASE1_IMPLEMENTATION_PLAN.md
# Phase 2A: docs/plans/PHASE2A_INFRASTRUCTURE_SETUP.md
# Phase 2B: docs/plans/PHASE2B_APPLICATION_DEVELOPMENT.md
# Phase 3: docs/plans/PHASE3_DEPLOYMENT.md
# Phase 4-6: docs/plans/PHASE4_6_EXECUTION_PLAN.md
```

---

## 📍 Phase 结构说明

### Phase 1: AWS 基础设施代码编写
**文件**: `docs/plans/PHASE1_IMPLEMENTATION_PLAN.md`

**目标**: 编写和测试所有 AWS 基础设施代码 (IaC)

**交付物**:
- ✅ VPC、子网、Internet Gateway、路由表 Python 脚本
- ✅ 安全组配置脚本
- ✅ IAM 角色和权限脚本
- ✅ ALB (Application Load Balancer) 配置脚本
- ✅ EC2 实例和 AMI 创建脚本
- ✅ ASG (Auto Scaling Group) 配置脚本
- ✅ 所有脚本的单元测试
- ✅ 跨平台兼容性验证 (Windows/macOS/Linux)

**时间**: Week 1-2

**关键输出**:
- `scripts/` - 所有基础设施脚本
- `tests/` - 单元测试
- `infrastructure/` - 配置输出 (*.json)

---

### Phase 2A: 基础设施配置脚本
**文件**: `docs/plans/PHASE2A_INFRASTRUCTURE_SETUP.md`

**目标**: 执行和验证 AWS 基础设施部署

**主要脚本**:
- `scripts/setup_iam_role.py` - 创建 IAM 角色
- `scripts/setup_network.py` - 创建 VPC 和网络
- `scripts/setup_security_groups.py` - 配置安全组
- `scripts/setup_alb.py` - 配置 ALB
- `scripts/setup_instances.py` - 创建 EC2 实例和 AMI
- `scripts/setup_asg.py` - 配置 ASG
- `scripts/deploy_all.py` - 一键部署所有
- `scripts/verify_infrastructure.py` - 验证部署成功

**交付物**:
- ✅ 完整的 VPC 网络 (包含 2 个公有子网)
- ✅ ALB (Application Load Balancer)
- ✅ 两个 ASG (Auto Scaling Group) 配置:
  - ASG-A: CPU-based autoscaling (75% CPU threshold)
  - ASG-B: Request-based autoscaling (1000 requests/min threshold)
- ✅ 配置文件输出 (`infrastructure/*.json`)
- ✅ 部署验证报告

**时间**: Week 2 (与 Phase 1 并行执行部分内容)

---

### Phase 2B: 应用工具开发
**文件**: `docs/plans/PHASE2B_APPLICATION_DEVELOPMENT.md` | **实施指南**: `docs/guides/PHASE2B_DEPLOYMENT_GUIDE.md`

**目标**: 开发负载测试和指标收集工具

**关键工具**:
1. **负载生成器** (`scripts/load_generator.py`)
   - 支持多种负载模式: constant (恒定), ramp (渐增), wave (波动)
   - 并发请求执行，带完整的响应时间统计
   - 导出负载统计 (CSV 格式)

2. **指标收集器** (`scripts/metrics_collector.py`)
   - 实时轮询 CloudWatch 指标 (CPU 利用率、网络流量等)
   - 自动扩展组 (ASG) 指标: 实例数、健康状态
   - 导出指标历史 (CSV 格式)

3. **实验编排器** (`scripts/experiment_runner.py`)
   - 协调负载生成和指标收集
   - 自动输出目录管理
   - 生成实验日志和结果总结

4. **测试 Flask 应用** (`apps/test_app/app.py`)
   - `/health` - 健康检查
   - `/data` - 数据端点
   - `/cpu-intensive` - CPU 密集操作
   - `/metrics` - 应用指标
   - Dockerfile 支持

**交付物**:
- ✅ `scripts/load_generator.py` - 负载生成器
- ✅ `scripts/metrics_collector.py` - 指标收集器
- ✅ `scripts/experiment_runner.py` - 实验编排
- ✅ `apps/test_app/app.py` - Flask 应用
- ✅ `apps/test_app/Dockerfile` - 容器配置
- ✅ 完整单元测试套件
- ✅ 本地验证和集成测试

**时间**: Week 2-3

---

### Phase 3: 部署到 AWS & 验证
**文件**: `docs/plans/PHASE3_DEPLOYMENT.md` | **实施指南**: `docs/guides/PHASE3_DEPLOYMENT_GUIDE.md`

**目标**: 将应用部署到 AWS 基础设施并验证可用性

**部署步骤**:
1. ✅ 构建 Docker 镜像 (测试 Flask 应用)
2. ✅ 推送镜像到 ECR (AWS Elastic Container Registry) 或使用本地 AMI
3. ✅ 配置 ALB 目标组
4. ✅ 将 EC2 实例加入 ASG
5. ✅ 配置 ASG 缩放策略:
   - **Scenario A**: CPU-based scaling (≥75% CPU → scale up)
   - **Scenario B**: Request-based scaling (≥1000 req/min → scale up)
6. ✅ 验证 ALB 健康检查
7. ✅ 验证应用端点可访问

**验证清单**:
- ✅ ALB 是否已配置并健康
- ✅ EC2 实例是否在 ASG 中注册
- ✅ `/health` 端点返回 200 OK
- ✅ 应用日志正常
- ✅ CloudWatch 指标正常收集

**交付物**:
- ✅ 部署验证报告
- ✅ ALB DNS 名称和端点
- ✅ 应用可达性证明
- ✅ 健康检查日志

**时间**: Week 3-4

---

### Phase 4-6: 实验执行 & 数据分析
**文件**: `docs/plans/PHASE4_6_EXECUTION_PLAN.md` | **实施指南**: `docs/guides/PHASE4_6_EXECUTION_GUIDE.md`

#### Phase 4-5: Autoscaling Experiments

**目标**: 在 AWS 上运行对比实验，收集性能数据

**实验场景** (4 种负载模式):

1. **Spike Load** (尖峰负载)
   - 突然的请求峰值，测试自动扩展反应时间
   - 监控指标: 实例增加延迟、P95 响应时间、错误率

2. **Ramp-Up Load** (渐进负载)
   - 逐步增加请求负载，测试逐步扩展
   - 监控指标: 扩展效率、资源利用率

3. **Sustained Load** (持续负载)
   - 长期稳定负载，测试稳定性和成本
   - 监控指标: 平均响应时间、CPU 利用率、实例稳定性

4. **Burst+Cooldown** (突发+冷静)
   - 短突发 + 静止期，测试缩放事件
   - 监控指标: 缩减延迟、级联效应

**对于每个场景，执行**:

- **Scenario A**: CPU-based autoscaling (75% CPU threshold)
  - 配置 ASG 以 CPU 平均利用率为指标
  - 运行负载生成器
  - 收集指标 (CPU、实例数、响应时间等)

- **Scenario B**: Request-based autoscaling (1000 req/min)
  - 配置 ASG 以请求率为指标
  - 运行相同的负载生成器
  - 收集相同的指标集

**数据收集**:
- `experiments/<exp_name>/experiment_log.json` - 实验元数据
- `experiments/<exp_name>/load_stats.csv` - 负载统计
- `experiments/<exp_name>/metrics.csv` - CloudWatch 指标

**时间**: Week 5-6

#### Phase 6: Analysis & Winner Determination

**目标**: 分析实验数据并确定最优的自动扩展策略

**分析内容**:

1. **性能对比**:
   - P50, P95, P99 响应时间对比
   - 错误率对比
   - 吞吐量对比

2. **成本分析**:
   - 每个 Scenario 的实例小时数
   - 总成本估计

3. **扩展行为分析**:
   - 扩展延迟 (Scale-up time)
   - 缩减延迟 (Scale-down time)
   - 实例稳定性

4. **统计显著性**:
   - 对比差异的统计检验
   - 置信区间

**输出**:
- `results/analysis_summary.json` - 分析总结
- `results/comparison_charts.png` - 对比图表 (4 个并行子图)
- `results/comparison_table.csv` - 对比表格
- 建议和结论

**时间**: Week 6-7 (与 Phase 5 并行)

---

### Phase 7: 最终报告撰写 & 演示
**文件**: 最终报告 (PDF 格式)

**目标**: 撰写学术报告并制作演示视频

**报告结构** (9 页以内):

1. **Title Page** - 标题页
2. **Abstract** - 摘要 (<250 words)
3. **Introduction** - 介绍 (云计算、Autoscaling、问题陈述)
4. **Related Work** - 相关工作
5. **Methodology** - 方法 (架构、场景配置、实验设计)
6. **Results** - 结果 (4 个场景的对比数据)
7. **Discussion** - 讨论 (为什么 Scenario B 更优、权衡与限制)
8. **Conclusion** - 结论
9. **References** - 参考文献

**Artifact Appendix** (不限页数):
- 系统依赖列表
- 安装和部署步骤
- 实验重现指南
- 成本估计
- 代码清单

**演示视频** (≤10 分钟):
- [0:00-1:00] 项目介绍
- [1:00-2:00] 技术架构
- [2:00-7:00] 现场演示 (ALB、ASG、CloudWatch)
- [7:00-9:00] 关键发现
- [9:00-10:00] 总结

**交付物**:
- ✅ `GroupID_report.pdf` - 最终报告 (9 页以内)
- ✅ 视频链接 (YouTube/B站)
- ✅ 所有代码和脚本在 GitHub

**时间**: Week 8-9

---

## 📁 文档索引

详细的 Phase 执行指南和计划:

| Phase | 计划文档 | 实施指南 | 状态 |
|-------|---------|--------|------|
| Phase 1 | [PHASE1_IMPLEMENTATION_PLAN.md](./PHASE1_IMPLEMENTATION_PLAN.md) | [PHASE1_DEPLOYMENT_GUIDE.md](../guides/PHASE1_DEPLOYMENT_GUIDE.md) | ✅ |
| Phase 2A | [PHASE2A_INFRASTRUCTURE_SETUP.md](./PHASE2A_INFRASTRUCTURE_SETUP.md) | - | ✅ |
| Phase 2B | [PHASE2B_APPLICATION_DEVELOPMENT.md](./PHASE2B_APPLICATION_DEVELOPMENT.md) | [PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) | ✅ |
| Phase 3 | [PHASE3_DEPLOYMENT.md](./PHASE3_DEPLOYMENT.md) | [PHASE3_DEPLOYMENT_GUIDE.md](../guides/PHASE3_DEPLOYMENT_GUIDE.md) | ✅ |
| Phase 4-6 | [PHASE4_6_EXECUTION_PLAN.md](./PHASE4_6_EXECUTION_PLAN.md) | [PHASE4_6_EXECUTION_GUIDE.md](../guides/PHASE4_6_EXECUTION_GUIDE.md) | ✅ |

**索引文档**:
- [PLANS_INDEX.md](./PLANS_INDEX.md) - 所有 Phase 计划的完整索引
- [PROJECT_EXECUTION_ROADMAP.md](./PROJECT_EXECUTION_ROADMAP.md) - 优化版本执行路线图

---

## 🎯 关键里程碑

- ✅ **Week 1-2**: Phase 1 & 2A 完成 - 基础设施代码和部署脚本
- ✅ **Week 2-3**: Phase 2B 完成 - 应用工具开发
- ✅ **Week 3-4**: Phase 3 完成 - 部署验证
- ✅ **Week 5-6**: Phase 4-6 完成 - 实验和分析
- ✅ **Week 7-9**: Phase 7 完成 - 报告和演示
- ✅ **Week 10**: 最终检查和提交

---

## ⚙️ 技术堆栈

**语言**: Python 3.9+ (跨平台)

**AWS 服务**:
- EC2 (Elastic Compute Cloud)
- VPC (Virtual Private Cloud)
- ALB (Application Load Balancer)
- ASG (Auto Scaling Group)
- CloudWatch (监控和指标)
- IAM (身份和访问管理)

**主要库**:
- `boto3` - AWS SDK
- `requests` - HTTP 请求
- `flask` - Web 框架
- `pandas` - 数据分析
- `matplotlib` - 数据可视化
- `locust` (可选) - 负载测试

**工具**:
- Git - 版本控制
- Docker - 容器化
- AWS CLI v2 - AWS 命令行工具

---

## 📝 执行指南

### 开始前准备

1. **AWS 账户设置**
   ```bash
   aws configure
   # 输入: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
   ```

2. **Git 配置**
   ```bash
   git config user.name "Your Full Name"
   git config user.email "your.email@university.edu"
   ```

3. **虚拟环境**
   ```bash
   python -m venv venv
   # macOS/Linux: source venv/bin/activate
   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### 执行流程

**对于每个 Phase**:

1. **查看计划文档** - 了解目标和交付物
2. **查看实施指南** (如有) - 获取详细步骤
3. **执行实施** - 按步骤实现
4. **验证结果** - 确保成功
5. **提交代码** - 原子 git 提交

### 代码提交规范

```bash
# Phase 1 示例
git add scripts/setup_network.py tests/test_setup_network.py
git commit -m "feat: implement network setup script (Phase 1)

- Create VPC with 10.0.0.0/16 CIDR block
- Create 2 public subnets in us-east-1a, us-east-1b
- Create and attach Internet Gateway
- Configure route table

Author: jaycee6666 <sijiechan2-c@my.cityu.edu.hk>"

git push origin main
```

---

## ✅ 质量检查清单

- [ ] 所有 Phase 目标完成
- [ ] 代码通过 linting 和 type checking
- [ ] 所有单元测试通过
- [ ] 跨平台兼容性验证
- [ ] 文档完整清晰
- [ ] Git 历史干净有条理
- [ ] 最终报告格式正确
- [ ] 演示视频已上传

---

## 📞 故障排查

**常见问题**:

1. **AWS 凭证错误**
   ```bash
   # 验证凭证
   aws sts get-caller-identity
   ```

2. **Python 版本问题**
   ```bash
   python --version  # 应该是 3.9 或更高
   ```

3. **跨平台路径问题**
   - 使用 `pathlib.Path` 而不是硬编码路径
   - Windows 使用 `\\` 或让 Python 处理路径

4. **AWS 资源已存在**
   ```bash
   # 清理旧资源
   python scripts/cleanup.py
   ```

---

## 📚 参考资源

- [AWS 官方文档 - Autoscaling](https://docs.aws.amazon.com/autoscaling/)
- [boto3 文档](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS Best Practices](https://docs.aws.amazon.com/whitepapers/)

---

**Last Updated**: 2026-04-18  
**Version**: 2.0 (Phase-structured)  
**Author**: Project Team  
**Status**: Active
