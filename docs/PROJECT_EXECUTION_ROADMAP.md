# 项目执行路线图（修订版）

**修订日期**: April 17, 2026  
**原始计划**: PROJECT_EXECUTION_PLAN.md  
**修订原因**: 采用 boto3 完整开发，优化时间表  
**截止日期**: April 24, 2026, 23:59 HKT  

---

## 📊 新的时间轴

```
Week 1 (Apr 17-21):     Phase 0 ✅ + Phase 1 ✅ + Phase 2a ✅
                        环境准备 + AWS 基础设施代码完成

Week 2 (Apr 21-24):     Phase 2b + Phase 3-10 (最后冲刺)
                        应用开发 + 部署 + 实验 + 报告
```

---

## 各 Phase 状态

| Phase | 名称 | 原始计划 | 当前状态 | 完成度 |
|-------|------|--------|--------|--------|
| **0** | 跨平台环境 | Week 1-2 | ✅ 完成 | 100% |
| **1** | AWS基础设施代码 | Week 2-3 | ✅ 完成 | 100% |
| **2a** | AWS 基础设施配置 | Week 3-4 | ✅ 完成 | 100% |
| **2b** | 应用开发（Load Gen） | Week 3 | ⏳ 待开始 | 0% |
| **3** | 部署到 AWS | Week 4 | ⏳ 待开始 | 0% |
| **4** | 运行实验 | Week 5-6 | ⏳ 待开始 | 0% |
| **5** | 数据收集 | Week 5-6 | ⏳ 待开始 | 0% |
| **6** | 数据分析 | Week 7 | ⏳ 待开始 | 0% |
| **7** | 报告撰写 | Week 7-8 | ⏳ 待开始 | 0% |
| **8** | 报告完善 | Week 8-9 | ⏳ 待开始 | 0% |
| **9** | 演示视频 | Week 9 | ⏳ 待开始 | 0% |
| **10** | 最终检查 & 提交 | Week 10 | ⏳ 待开始 | 0% |

---

## 🎯 即刻行动项（优先级排序）

### 立即 (今天-明天)
- [ ] **部署 AWS 基础设施**
  ```bash
  python scripts/deploy_all.py
  ```
  预期时间：5-10 分钟
  
- [ ] **验证基础设施**
  ```bash
  python scripts/verify_infrastructure.py
  ```
  
- [ ] **记录 ALB DNS 名称**
  从 `infrastructure/alb-config.json` 获取
  示例：`http://experiment-alb-123.us-east-1.elb.amazonaws.com`

### 本周 (Apr 18-21)
- [ ] **Phase 2b: 应用开发**
  - 负载生成工具 (Load Generation)
  - 实验脚本
  - 指标收集器

- [ ] **Phase 3: 部署应用到 AWS**
  - 将负载生成工具部署到 EC2 实例
  - 配置 CloudWatch 指标
  - 验证端到端流程

### 下周 (Apr 22-24)
- [ ] **Phase 4-5: 运行实验**
  - 执行 CPU 策略实验
  - 执行请求率策略实验
  - 收集数据

- [ ] **Phase 6-7: 分析和报告**
  - 分析结果
  - 生成图表
  - 撰写报告 (≤9 页)

- [ ] **Phase 8-10: 最终提交**
  - 完善报告
  - 制作演示视频 (≤10 分钟)
  - 提交到 Blackboard

---

## 📁 项目文件结构

```
autoscaling-strategy-compare/
│
├── Phase 0 (完成 ✅)
│   ├── setup.py                    # 一键环境初始化
│   ├── requirements.txt            # 依赖列表
│   └── venv/                       # 虚拟环境
│
├── Phase 1 (完成 ✅)
│   └── docs/
│       ├── PHASE1_IMPLEMENTATION_PLAN.md
│       ├── PHASE1_DEPLOYMENT_GUIDE.md
│       └── PHASE1_COMPLETION_REPORT.md
│
├── Phase 2a (完成 ✅)
│   ├── scripts/
│   │   ├── setup_network.py
│   │   ├── setup_iam_role.py
│   │   ├── setup_security_groups.py
│   │   ├── setup_instances.py
│   │   ├── setup_alb.py
│   │   ├── setup_asg.py
│   │   ├── verify_infrastructure.py
│   │   └── deploy_all.py
│   └── infrastructure/              # AWS 配置输出
│       ├── network-config.json
│       ├── iam-config.json
│       ├── security-groups-config.json
│       ├── launch-templates-config.json
│       ├── alb-config.json
│       ├── asg-config.json
│       ├── verification-report.json
│       └── deployment-log.json
│
├── Phase 2b (待开始 ⏳)
│   ├── scripts/
│   │   ├── load_generator.py      # 负载生成工具
│   │   ├── metrics_collector.py   # 指标收集
│   │   └── experiment_runner.py   # 实验执行
│   └── apps/
│       └── test_app/              # 测试应用
│
├── Phase 3 (待开始 ⏳)
│   └── deployment/
│       ├── deploy_load_gen.sh
│       └── deploy_app.sh
│
├── Phase 4-5 (待开始 ⏳)
│   ├── experiments/
│   │   ├── cpu_strategy.py
│   │   ├── request_rate_strategy.py
│   │   └── results/               # 实验数据
│   └── data/
│       └── raw_metrics.csv
│
├── Phase 6-7 (待开始 ⏳)
│   ├── analysis/
│   │   ├── analyze_results.py
│   │   └── generate_charts.py
│   └── reports/
│       ├── FINAL_REPORT.md        # 最终报告
│       └── charts/                # 图表
│
├── Phase 8-10 (待开始 ⏳)
│   ├── demos/
│   │   └── demo.mp4               # 演示视频
│   └── submission/
│       └── README.md              # 提交说明
│
└── docs/
    ├── PROJECT_EXECUTION_PLAN.md (原始)
    ├── PROJECT_EXECUTION_ROADMAP.md (本文件 - 修订版)
    ├── VIRTUAL_ENVIRONMENT.md
    ├── GETTING_STARTED.md
    ├── QUICK_REFERENCE.md
    └── ...
```

---

## 🚀 下一步：Phase 2b - 应用开发

### 2b.1 负载生成工具

**目标**: 创建可配置的负载生成工具，向 ALB 发送请求

**需要创建**:
- `scripts/load_generator.py` - 负载生成核心
- `scripts/metrics_collector.py` - 实时指标收集
- `scripts/experiment_runner.py` - 实验协调

**实现要求**:
- 支持不同的负载模式（恒定、阶梯、波形）
- 记录响应时间和错误
- 导出到 CSV 便于分析
- 与 CloudWatch 集成（读取 ASG 指标）

**估计时间**: 6-8 小时

### 2b.2 测试应用

**目标**: 创建简单的 HTTP 服务，模拟真实应用

**需要创建**:
- `apps/test_app/app.py` - Flask 应用
- `apps/test_app/Dockerfile` - 容器化

**实现要求**:
- GET `/health` - 健康检查
- GET `/data` - 返回随机数据
- POST `/cpu-intensive` - CPU 密集操作（用于测试 CPU 策略）
- 在 CloudWatch 中发布自定义指标

**估计时间**: 2-3 小时

---

## 📋 关键检查点

### ✅ 在开始 Phase 2b 前，确认：

1. AWS 基础设施已部署
   ```bash
   python scripts/verify_infrastructure.py
   ```
   所有检查都应该是 ✅

2. ALB 可以访问
   ```bash
   curl http://<ALB-DNS>/health
   ```
   应该返回 HTTP 200

3. EC2 实例正在运行
   - 检查 AWS 控制台
   - 或在 `verification-report.json` 中查看

4. CloudWatch 正在接收指标
   - 检查 CloudWatch 控制台
   - 命名空间：`AutoscaleExperiment`

---

## 🎓 关键决策点

### Q1: CPU 策略 vs 请求率策略哪个先测试？
**A**: 先测试 CPU 策略（简单、更可靠）

### Q2: 负载生成应该多强？
**A**: 开始低强度，逐步增加，避免 AWS 配额问题

### Q3: 实验应该运行多长？
**A**: 每个策略 30-60 分钟（足以看到至少 2-3 个扩缩容周期）

### Q4: 如何处理 ASG 故障？
**A**: 自动回滚：删除所有资源，重新运行 `deploy_all.py`

---

## 📞 需要帮助？

**创建 Phase 2b 脚本**：告诉我 "开始 Phase 2b"  
**调试 AWS 问题**：告诉我具体错误  
**优化时间表**：告诉我遇到的瓶颈  

---

## ⏰ 时间预算

| Phase | 计划 | 实际 | 备注 |
|-------|------|------|------|
| 0 | 2h | ✅ 1h | 超前 |
| 1 | 14h | ✅ 3h | 大幅超前 |
| 2a | 8h | ✅ 3h | 提前完成 |
| 2b | 10h | ⏳ TBD | 下一步 |
| 3 | 6h | ⏳ TBD | |
| 4-5 | 16h | ⏳ TBD | |
| 6-7 | 12h | ⏳ TBD | |
| 8-10 | 12h | ⏳ TBD | |
| **总计** | **80h** | **✅ 7h** | **可用: 73h** |

**结论**: 进度超前 7 小时，留有充足的缓冲时间用于调试和完善。

---

**修订者**: Sisyphus  
**修订日期**: April 17, 2026  
**状态**: ✅ 已批准按新路线图执行

