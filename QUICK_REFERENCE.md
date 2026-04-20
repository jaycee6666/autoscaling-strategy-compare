# 快速参考卡片 - Phase 0-6 一页纸指南

## 🎯 核心步骤一览表

| 阶段 | 描述 | 命令 | 时长 | 文件输出 |
|------|------|------|------|---------|
| **Phase 0** | 环境准备 | `python scripts/check_environment.py` | 10 min | - |
| **Phase 1** | 基础设施代码验证 | `python -m pytest tests/` | 5 min | - |
| **Phase 2A** | 部署基础设施 | `python scripts/deploy_all.py` | 20 min | `infrastructure/*.json` |
| **Phase 2B** | 验证应用 | `curl http://$ALB_DNS/health` | 5 min | - |
| **Phase 3** | 部署验证 | `python scripts/verify_infrastructure.py` | 5 min | `verification-report.json` |
| **Phase 4-5.1** | 基础设施验证 | `python experiments/01_verify_infrastructure.py` | 5 min | `infrastructure_health_report.json` |
| **Phase 4-5.2** | CPU实验 | `python experiments/02_run_cpu_experiment.py` | 30 min | `cpu_strategy_metrics.json` |
| **Phase 4-5.3** | 请求率实验 | `python experiments/03_run_request_rate_experiment.py` | 30 min | `request_rate_experiment_metrics.json` |
| **Phase 4-5.4** | 结果聚合 | `python experiments/04_aggregate_results.py` | 5 min | `comparison_report.json` + `metrics_comparison.csv` |
| **Phase 6** | 分析赢家 | `python experiments/06_analyze_results.py` | 2 min | `analysis_report.json` |

**总时间**: 75-85 分钟

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
# 一键部署
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

### Phase 2B: 验证应用

```bash
# 获取ALB名称
python -c "import boto3; elb = boto3.client('elbv2'); albs = elb.describe_load_balancers()['LoadBalancers']; print([alb['LoadBalancerName'] for alb in albs])"
['experiment-alb']
# 获取DNS名称
python -c "import boto3; elb = boto3.client('elbv2'); albs = elb.describe_load_balancers()['LoadBalancers']; print(albs[0]['DNSName'])"
experiment-alb-1466294824.us-east-1.elb.amazonaws.com


# 测试健康检查
curl http://<ALB_DNS>/health
curl http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health

# 测试其他端点
curl http://<ALB_DNS>/data
curl http://<ALB_DNS>/metrics
```

### Phase 3: 部署验证

```bash
python scripts/verify_infrastructure.py
cat infrastructure/verification-report.json | python -m json.tool
```

### Phase 4-6: 实验执行&分析

一键执行

```
python run_all_experiments.py
```

分步执行

```bash
# 基础设施验证 (5 min)
python experiments/01_verify_infrastructure.py

# CPU策略实验 (30 min) - 不要中断！
python experiments/02_run_cpu_experiment.py

# 请求率策略实验 (30 min) - 不要中断！
python experiments/03_run_request_rate_experiment.py

# 结果聚合 (5 min)
python experiments/04_aggregate_results.py

# 查看对比结果
cat experiments/results/comparison_report.json | python -m json.tool
cat experiments/results/metrics_comparison.csv

# 执行分析
python experiments/06_analyze_results.py

# 查看分析结果
cat experiments/results/analysis_report.json | python -m json.tool
```

#### 

### 最终验证

```bash
# 检查所有文件
ls -lh experiments/results/

# 验证JSON有效性
python -c "import json; json.load(open('experiments/results/cpu_strategy_metrics.json')); print('✓ CPU文件有效')"
python -c "import json; json.load(open('experiments/results/request_rate_experiment_metrics.json')); print('✓ 请求率文件有效')"
python -c "import json; json.load(open('experiments/results/analysis_report.json')); print('✓ 分析文件有效')"
python -c "import json; json.load(open('experiments/results/comparison_report.json')); print('✓ 对比文件有效')"
```

---

## ⚠️ 关键提示

### 必须记住的事项

| 项目 | 说明 |
|------|------|
| **Git提交** | ✋ **禁止**提交到Git - 仅保存本地 |
| **AWS成本** | 💰 完整Phase 4-6约 $0.20-0.30 |
| **实验中断** | 🚫 不要中断CPU和请求率实验（各30分钟） |
| **ALB等待** | ⏳ EC2启动需要2-3分钟，先不要测试 |
| **AWS凭证** | 🔑 需要有效的AWS Access Key和Secret Key |
| **网络连接** | 📡 需要稳定的网络（特别是实验期间） |

### 文件清单

```
结果文件位置: experiments/results/

✓ infrastructure_health_report.json         (~2 KB)   - Phase 4-5.1输出
✓ cpu_strategy_metrics.json                 (~24 KB)  - Phase 4-5.2输出
✓ request_rate_experiment_metrics.json      (~25 KB)  - Phase 4-5.3输出
✓ comparison_report.json                    (~1.5 KB) - Phase 4-5.4输出
✓ metrics_comparison.csv                    (388 B)   - Phase 4-5.4输出
✓ analysis_report.json                      (~1.7 KB) - Phase 6输出

基础设施配置: infrastructure/

✓ iam-config.json                           - IAM角色配置
✓ network-config.json                       - VPC和网络配置
✓ security-groups-config.json               - 安全组配置
✓ alb-config.json                           - ALB配置
✓ launch-templates-config.json              - EC2启动模板配置
✓ asg-config.json                           - ASG配置
✓ deployment-log.json                       - 部署日志
✓ verification-report.json                  - 验证报告
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

### CPU策略实验关键指标
- 成功率: 92.95%
- 平均响应时间: 970ms
- P95延迟: 1175ms
- 平均CPU: 65.2%
- 扩展事件: 1

### 请求率策略实验关键指标
- 成功率: 93.74%
- 平均响应时间: 960ms
- P95延迟: 1026ms
- 平均CPU: 19.9%
- 扩展事件: 0

### 分析赢家结果
```
Winner: Request-Rate Strategy
Confidence Score: 2.37%
Reason: Request-rate strategy achieved better response time (960ms vs 971ms)
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

Phase 4-5：
- [ ] 基础设施验证通过
- [ ] CPU实验运行30分钟
- [ ] 请求率实验运行30分钟
- [ ] 结果文件生成（6个文件）

Phase 6：
- [ ] 分析脚本执行完成
- [ ] 赢家已确定
- [ ] 置信度得分 > 1%
- [ ] 所有JSON文件有效

---

## 💡 实用技巧

### 监控实验进度

```bash
# 实时查看日志
tail -f logs/experiment.log

# 监控AWS CloudWatch
# 打开浏览器 -> AWS Console -> CloudWatch
# 选择你的EC2实例和ALB
# 查看实时的CPU、网络、请求等指标
```

### 清理资源

```bash
# 查看所有AWS资源
aws ec2 describe-instances --query "Reservations[].Instances[].[InstanceId,State.Name]"
aws ec2 describe-load-balancers --query "LoadBalancers[].[LoadBalancerName,State.Code]"

# 删除资源（谨慎！）
python scripts/cleanup_infrastructure.py
```

### 备份结果

```bash
# 复制所有结果文件
cp -r experiments/results/ backup_results_$(date +%Y%m%d_%H%M%S)/

# 或打包
tar -czf experiment_results_backup.tar.gz experiments/results/
```

---

## 📞 需要帮助？

提供以下信息获得更快的帮助：

1. 正在执行哪个Phase和步骤
2. 完整的错误信息（复制粘贴）
3. 相关的命令和输出
4. 已尝试的解决方案

---

**最后更新**: 2026年4月19日  
**文档版本**: 快速参考 v1.0
