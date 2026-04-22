# 快速参考卡片 - Phase 0-6 一页纸指南

## 🎯 核心步骤一览表

| 阶段 | 描述 | 命令 | 时长 | 文件输出 |
|------|------|------|------|---------|
| **Phase 0** | 环境准备 | `python scripts/check_environment.py` | 10 min | - |
| **Phase 1** | 基础设施代码验证 | `python -m pytest tests/` | 5 min | - |
| **Phase 2A** | 部署基础设施 | `python scripts/deploy_all.py` | 20 min | `infrastructure/*.json` + 内置验证 |
| **Phase 3** | 应用健康验证 | `python experiments/01_verify_infrastructure.py` | 5 min | `infrastructure_health_report.json` |
| **Phase 4-5.1** | CPU突发场景实验 | `python experiments/05_run_burst_scenario_experiment.py --strategy cpu` | 50 min | `burst_scenario_cpu_results.json` |
| **Phase 4-5.2** | 环境清理 | `python scripts/cleanup_between_experiments.py` | 15-20 min | (日志输出) |
| **Phase 4-5.3** | 请求率突发场景实验 | `python experiments/05_run_burst_scenario_experiment.py --strategy request_rate` | 50 min | `burst_scenario_request_rate_results.json` |
| **Phase 4-5.4** | 结果对比 | `python experiments/07_compare_burst_scenario_results.py` | 5 min | `burst_scenario_comparison.json` |
| **Phase 6** | 分析赢家 | `python experiments/06_analyze_results.py` | 2 min | `analysis_report.json` |

**总时间**: 155-170 分钟（两个策略，包括环境清理）或 92 分钟（仅运行一个策略）

---

## 📝 命令速查

### Phase 0: 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate           # macOS/Linux
venv\Scripts\activate.bat          # Windows (cmd)
venv\Scripts\Activate.ps1          # Windows (PowerShell)

# 安装依赖
pip install -r requirements.txt

# 验证环境
python scripts/check_environment.py
python scripts/init_project.py

# 配置AWS (编辑 config/.env)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# 测试AWS连接
python scripts/aws_utils.py
```

### Phase 1: 代码验证

```bash
# 检查Python语法
python -m py_compile scripts/setup_iam_role.py
python -m py_compile scripts/setup_network.py
# ... 等等

# 或运行单元测试
python -m pytest tests/ -v
```

### Phase 2A: 部署基础设施

```bash
# 一键部署（包含验证）
python scripts/deploy_all.py

# 或分步部署
python scripts/setup_iam_role.py
python scripts/setup_network.py
python scripts/setup_security_groups.py
python scripts/setup_alb.py
python scripts/setup_instances.py
python scripts/setup_asg.py

# 查看配置
ls -la infrastructure/
```

### Phase 3: 应用健康验证

```bash
# 基础设施验证 (Phase 2A自动运行，结果保存在 infrastructure/verification-report.json)

# 应用健康验证（实验前必须运行）
python experiments/01_verify_infrastructure.py
cat experiments/results/infrastructure_health_report.json | python -m json.tool
```

### Phase 4-6: 实验执行&分析

#### 📌 突发流量场景实验

分步执行（CPU和请求率策略必须分开执行，中间需要清理环境）

```bash
# 应用健康验证 (5 min) - 必须运行！
python experiments/01_verify_infrastructure.py

# ① CPU策略突发场景实验 (50 min) - 不要中断！
python experiments/05_run_burst_scenario_experiment.py --strategy cpu

# ② 环境清理（必须做！否则数据污染） (15-20 min)
python scripts/cleanup_between_experiments.py

# ③ 请求率策略突发场景实验 (50 min) - 不要中断！
python experiments/05_run_burst_scenario_experiment.py --strategy request_rate

# 对比两个策略的结果 (5 min)
python experiments/07_compare_burst_scenario_results.py

# 查看对比结果
cat experiments/results/burst_scenario_comparison.json | python -m json.tool
```

**为什么要分开执行？**
- CPU实验可能扩容到8-10个实例
- 如果直接运行请求率实验，会从"脏"环境（多余实例）开始
- 清理脚本自动重置ASG容量、等待实例终止、稳定CloudWatch指标
- 确保两个策略在相同初始条件下比较


### 最终验证

```bash
# 检查所有文件
ls -lh experiments/results/

# 验证突发场景实验的JSON有效性
python -c "import json; json.load(open('experiments/results/burst_scenario_cpu_results.json')); print('✓ CPU突发场景文件有效')"
python -c "import json; json.load(open('experiments/results/burst_scenario_request_rate_results.json')); print('✓ 请求率突发场景文件有效')"
python -c "import json; json.load(open('experiments/results/burst_scenario_comparison.json')); print('✓ 对比文件有效')"
python -c "import json; json.load(open('experiments/results/analysis_report.json')); print('✓ 分析文件有效')"
```

---

## ⚠️ 关键提示

### 必须记住的事项

| 项目 | 说明 |
|------|------|
| **Git提交** | ✋ **禁止**提交到Git - 仅保存本地 |
| **AWS成本** | 💰 完整Phase 4-6约 $0.20-0.30 |
| **实验中断** | 🚫 不要中断CPU和请求率实验（各50分钟）|
| **环境清理** | 🧹 **必须**在两个策略之间运行cleanup脚本（15-20分钟），否则数据污染 |
| **ALB等待** | ⏳ EC2启动需要2-3分钟，先不要测试 |
| **AWS凭证** | 🔑 需要有效的AWS Access Key和Secret Key |
| **网络连接** | 📡 需要稳定的网络（特别是实验期间） |

### 文件清单

```
结果文件位置: experiments/results/

✓ infrastructure_health_report.json         (~2 KB)      - Phase 3输出
✓ burst_scenario_cpu_results.json           (~30-50 KB)  - Phase 4-5.1输出
✓ burst_scenario_request_rate_results.json  (~30-50 KB)  - Phase 4-5.3输出
✓ burst_scenario_comparison.json            (~2-5 KB)    - Phase 4-5.4输出
✓ analysis_report.json                      (~1.7 KB)    - Phase 6输出

基础设施配置: infrastructure/

✓ iam-config.json                           - IAM角色配置
✓ network-config.json                       - VPC和网络配置
✓ security-groups-config.json               - 安全组配置
✓ alb-config.json                           - ALB配置
✓ launch-templates-config.json              - EC2启动模板配置
✓ asg-config.json                           - ASG配置
✓ deployment-log.json                       - 部署日志（Phase 2A生成）
✓ verification-report.json                  - 基础设施验证报告（Phase 2A自动生成）
```

---

## 🚨 常见问题速解

| 问题 | 症状 | 快速解决 |
|------|------|---------|
| Python版本错误 | `ModuleNotFoundError` | `python --version` 检查，需3.9+ |
| 虚拟环境激活失败 | `command not found` | 重新运行激活命令，检查路径 |
| AWS凭证错误 | `InvalidClientTokenId` | 检查 `config/.env` 中的密钥是否正确 |
| ALB不可访问 | `Connection timeout` | 等待2-3分钟，检查安全组 |
| 实验中断 | 脚本停止 | 检查网络连接，查看logs目录中的日志 |
| 依赖安装失败 | `ModuleNotFoundError` | `pip install -r requirements.txt` 重新安装 |

---

## 📊 预期结果示例

### 突发流量场景实验

突发场景更能体现两个策略的差异，置信度会更高（15-30%+）

#### CPU策略突发场景关键指标
- 预热阶段 (50s @ 10 req/s): 建立基线
- 基线阶段 (100s @ 10 req/s): 记录正常性能
- 突发阶段 (150s @ 50 req/s): 观察扩容反应 ⭐ 关键
- 恢复阶段 (100s @ 10 req/s): 观察缩容效率
- 目标：最少80个CloudWatch指标样本

#### 请求率策略突发场景关键指标
- 预热阶段 (50s @ 10 req/s): 建立基线
- 基线阶段 (100s @ 10 req/s): 记录正常性能
- 突发阶段 (150s @ 50 req/s): 观察扩容反应 ⭐ 关键
- 恢复阶段 (100s @ 10 req/s): 观察缩容效率
- 目标：最少80个CloudWatch指标样本

#### 分析赢家结果示例
```json
{
  "winner": "request_rate_strategy",
  "confidence_score": "23.5%",
  "reason": "Request-rate strategy scaled faster and recovered more efficiently during burst traffic",
  "key_metrics": {
    "cpu_strategy": {
      "max_instances": 8,
      "avg_response_time_ms": 1250,
      "burst_recovery_time_seconds": 45
    },
    "request_rate_strategy": {
      "max_instances": 6,
      "avg_response_time_ms": 890,
      "burst_recovery_time_seconds": 25
    }
  }
```

---

## 🎯 检查清单

在开始前：
- [ ] Python 3.9+ 已安装
- [ ] AWS账户已创建，有有效凭证
- [ ] 网络连接稳定
- [ ] 有足够的AWS服务配额（EC2, ALB, ASG等）

Phase 0-1：
- [ ] 虚拟环境创建成功
- [ ] 依赖安装完成
- [ ] 环境检查通过
- [ ] AWS连接测试成功

Phase 2A-3：
- [ ] 部署命令执行完成
- [ ] 所有配置文件生成
- [ ] AWS资源在控制台可见
- [ ] 验证报告显示所有资源正常
- [ ] 应用健康验证通过

Phase 4-5：
- [ ] 应用健康验证通过
- [ ] CPU突发场景实验运行50分钟
- [ ] 环境清理完成
- [ ] 请求率突发场景实验运行50分钟
- [ ] 结果对比完成（3个文件）

Phase 6：
- [ ] 分析脚本执行完成
- [ ] 赢家已确定
- [ ] 置信度得分 > 1%
- [ ] 所有JSON文件有效

---

## 💡 实用技巧

### 监控实验进度

```bash
# 方式1：直接运行（输出到终端，实时查看）
python experiments/05_run_burst_scenario_experiment.py --strategy cpu

# 方式2：同时输出到文件和终端（推荐）
python experiments/05_run_burst_scenario_experiment.py --strategy cpu | tee logs/burst_experiment_$(date +%Y%m%d_%H%M%S).log

# 方式3：后台运行+查看日志
python experiments/05_run_burst_scenario_experiment.py --strategy cpu > logs/burst_experiment_$(date +%Y%m%d_%H%M%S).log 2>&1 &
tail -f logs/burst_experiment_*.log

# 监控AWS CloudWatch（实时查看指标）
# 打开浏览器 -> AWS Console -> CloudWatch
# 选择你的EC2实例和ALB -> 查看实时的CPU、网络、请求等指标
```

### 备份结果

```bash
# 复制所有结果文件
cp -r experiments/results/ backup_results_$(date +%Y%m%d_%H%M%S)/

# 或打包
tar -czf experiment_results_backup.tar.gz experiments/results/
```

---

## 🗑️ 实验完成后：删除所有资源

当所有实验完成后，**必须删除AWS资源以停止计费**。

### 快速删除命令

```bash
# 查看当前AWS资源
aws ec2 describe-instances --query "Reservations[].Instances[].[InstanceId,State.Name]"
aws ec2 describe-load-balancers --query "LoadBalancers[].[LoadBalancerName,State.Code]"

# 方式1：交互式确认（推荐 - 最安全）
python scripts/cleanup_infrastructure.py

# 方式2：先预览，再删除（最安全）
python scripts/cleanup_infrastructure.py --dry-run
python scripts/cleanup_infrastructure.py

# 方式3：直接删除（跳过确认）
python scripts/cleanup_infrastructure.py --force
```

### 删除的资源

脚本会自动删除：
- ✓ 自动扩展组 (Auto Scaling Groups)
- ✓ 负载均衡器 (Application Load Balancer)
- ✓ 目标组 (Target Groups)
- ✓ 启动模板 (Launch Templates)
- ✓ 安全组 (Security Groups)
- ✓ 网络资源 (VPC, Subnets, Internet Gateway)
- ✓ IAM角色 (IAM Roles)

### 成本影响

- 💰 删除后立即停止计费新实例
- ⏳ EC2实例完全终止需要 5-10 分钟
- 📄 清理报告：`infrastructure/cleanup-report.json`

**更多详情** → 查看 `docs/guides/CLEANUP_GUIDE.md`

---

## 📞 需要帮助？

提供以下信息获得更快的帮助：

1. 正在执行哪个Phase和步骤
2. 完整的错误信息（复制粘贴）
3. 相关的命令和输出
4. 已尝试的解决方案

---

**最后更新**: 2026年4月20日  
**文档版本**: 快速参考 v2.1（新增清理指南）
