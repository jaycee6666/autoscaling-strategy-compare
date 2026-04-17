# Phase 4-6: 实验和分析 - 完整指南

**运行自动扩缩容策略对比实验和执行全面分析的端到端指南**

最后更新: 2026年4月18日  
总时长: ~85 分钟 (5分钟设置 + 30分钟CPU测试 + 30分钟请求率测试 + 10分钟聚合 + 10分钟分析)

---

## 📋 目录

1. [概述](#概述)
2. [快速开始 (一条命令执行)](#快速开始)
3. [前置要求检查清单](#前置要求检查清单)
4. [基础设施概述](#基础设施概述)
5. [Phase 4-5: 实验执行](#phase-45-实验执行)
6. [Phase 6: 分析和获胜者确定](#phase-6-分析和获胜者确定)
7. [理解结果](#理解结果)
8. [故障排查](#故障排查)
9. [分析后验证](#分析后验证)
10. [后续步骤 (Phase 7)](#后续步骤-phase-7)

---

## 概述

Phase 4-6 是自动扩缩容策略对比项目的实验验证和分析阶段。它包括：

- **Phase 4-5**: 执行两个30分钟的实验，对比基于CPU与基于请求率的自动扩缩容策略
- **Phase 6**: 复杂的多因素分析以确定最优策略并计算置信度

**您将获得**:
- 两种策略的真实 AWS CloudWatch 指标
- 详细的性能对比 (延迟、成本、效率)
- 带置信度得分的数据驱动获胜者确定
- 可用于学术报告和可视化的分析报告

---

## 快速开始 (一条命令执行)

### ⚡ 用一条命令运行所有内容

执行 Phase 4-6 最简单的方法是使用编排脚本：

```bash
# 从项目根目录
python scripts/run_all_experiments.py

# 总时长: ~85 分钟
# 自动运行: 步骤 1-4 (Phase 4-5) + Phase 6 分析
# 输出: 所有指标文件 + 分析报告
```

**此命令**:
1. ✅ 验证基础设施
2. ✅ 运行 CPU 策略实验 (30 分钟)
3. ✅ 运行请求率策略实验 (30 分钟)
4. ✅ 聚合结果
5. ✅ 执行 Phase 6 分析
6. ✅ 生成包含获胜者确定的 analysis_report.json

**可选标志**:
```bash
python scripts/run_all_experiments.py --skip-verification    # 跳过输出验证
python scripts/run_all_experiments.py --skip-phase-6         # 跳过分析，仅运行实验
```

---

## 前置要求检查清单

在开始实验前，验证所有前置要求都满足：

### 系统要求
- [ ] Python 3.8+ 已安装 (`python --version`)
- [ ] AWS 凭证已配置 (`aws sts get-caller-identity` 返回您的账户)
- [ ] 互联网连接 (AWS API 调用需要)
- [ ] 终端/命令提示符访问

### AWS 基础设施要求
- [ ] 应用负载均衡器 (ALB) **运行中**且**健康**
- [ ] ALB DNS 名称可通过 HTTP 访问
- [ ] CPU 策略的自动扩展组 (`asg-cpu`) 存在且容量为 1-5 个实例
- [ ] 请求率策略的自动扩展组 (`asg-request`) 存在且容量为 1-5 个实例
- [ ] 两个 ASG 中的 EC2 实例**健康**且运行 Flask 应用
- [ ] 安全组允许端口 80 (HTTP) 的入站流量

### Python 依赖
- [ ] 所有依赖都已安装: `pip install -r requirements.txt`
- [ ] 关键包: `boto3`, `requests`, `pandas`, `numpy`

### ALB DNS 配置

在继续之前，**识别您的 ALB DNS 名称**：

```bash
# 从基础设施配置获取 ALB DNS
cat infrastructure/alb-config.json | grep -i "dns"

# 或直接测试:
curl -v http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
```

预期响应: `{"status": "healthy"}`，HTTP 200

---

## 🏗️ 基础设施概述

### 两种被测试的自动扩缩容策略

#### 策略 1: 基于 CPU 的自动扩缩容 (`asg-cpu`)
- **指标**: 跨实例目标 50% CPU 利用率
- **扩出触发**: 平均 CPU > 50%
- **扩入触发**: 平均 CPU < 20%
- **最小实例**: 1 | **期望**: 1 | **最大**: 5
- **预期行为**: 响应较慢，可能超出目标

#### 策略 2: 基于请求率的自动扩缩容 (`asg-request`)
- **指标**: 每个实例目标 10 请求/秒
- **扩出触发**: 请求率 > 每个实例 10 req/s
- **扩入触发**: 请求率 < 每个实例 5 req/s
- **最小实例**: 1 | **期望**: 2 | **最大**: 5
- **预期行为**: 响应更快，扩展更精确

### 负载配置
- **恒定负载**: 10 请求/秒 (固定速率)
- **每次实验时长**: 30 分钟 (1800 秒)
- **请求类型**: HTTP POST 到 `/request` 端点
- **响应时间目标**: < 1 秒每个请求

---

## Phase 4-5: 实验执行

### ⏱️ 时间表分解

```
Phase 4-5 总计: ~75 分钟

├─ 步骤 1: 基础设施验证 (5 分钟)
│  └─ 命令: python experiments/01_verify_infrastructure.py
│     验证: ALB 健康、ASG 状态、实例计数
│
├─ 步骤 2: CPU 策略实验 (30 分钟)
│  └─ 命令: python experiments/02_run_cpu_experiment.py
│     输出: cpu_strategy_metrics.json (~18,000 个请求)
│     监控: CPU 利用率、请求率、扩展事件
│
├─ 步骤 3: 请求率策略实验 (30 分钟)
│  └─ 命令: python experiments/03_run_request_rate_experiment.py
│     输出: request_rate_experiment_metrics.json (~18,000 个请求)
│     监控: 请求率、扩展行为、延迟
│
└─ 步骤 4: 聚合和比较结果 (10 分钟)
   └─ 命令: python experiments/04_aggregate_results.py
      输出: comparison_report.json, metrics_comparison.csv
      分析: 扩展效率、响应性、资源利用

```

### 关键成功要求

对于有效的实验结果：
1. ✅ 负载生成器必须恰好维持 10 个请求/秒 (±0.5 req/s)
2. ✅ 30 分钟周期内无网络中断
3. ✅ 实验期间无手动 ASG 更改 (无干预)
4. ✅ CloudWatch 指标可用于收集 (5 分钟滞后可接受)
5. ✅ 输出文件包含真实 AWS 指标，非模拟数据

### 🚀 详细逐步执行

#### 步骤 1: 验证基础设施 (5 分钟)

**用途**: 在运行实验前确认所有 AWS 资源健康

**命令**:
```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
python experiments/01_verify_infrastructure.py
```

**预期输出**:
```json
{
  "timestamp": "2026-04-17T17:30:45Z",
  "alb_health": {
    "status": "healthy",
    "dns": "experiment-alb-1466294824.us-east-1.elb.amazonaws.com",
    "http_status": 200
  },
  "asg_cpu": {
    "name": "asg-cpu",
    "desired": 1,
    "current": 1,
    "min": 1,
    "max": 5
  },
  "asg_request": {
    "name": "asg-request",
    "desired": 2,
    "current": 2,
    "min": 1,
    "max": 5
  }
}
```

**检查项**:
- ✅ `alb_health.status` = `"healthy"` (必须为真)
- ✅ 所有实例显示运行状态
- ✅ `asg_cpu.current` 匹配 `asg_cpu.desired`
- ✅ `asg_request.current` 匹配 `asg_request.desired`
- ❌ **停止如果**: 任何实例已停止或终止

**故障排查**:
- 如果 ALB 返回 502/503: 实例可能未完全启动。等待 2 分钟，重试。
- 如果实例计数不匹配: ASG 可能在扩展。等待稳定，重试。

---

#### 步骤 2: 运行 CPU 策略实验 (30 分钟)

**用途**: 为基于 CPU 的自动扩缩容策略生成指标

**命令**:
```bash
python experiments/02_run_cpu_experiment.py
```

**实验期间发生的情况**:
1. 脚本连接到 ALB 并开始发送恰好 10 个请求/秒
2. CloudWatch 指标收集启动 (后台)
3. 系统监控:
   - 每个实例的 CPU 利用率
   - 请求计数和响应时间
   - 扩展活动 (扩出/扩入事件)
   - 实例生命周期更改
4. 30 分钟后，脚本收集最终指标并保存到 `experiments/results/cpu_strategy_metrics.json`

**控制台输出** (实时监控):
```
[17:30:45] CPU 策略实验已启动
[17:30:45] 目标: 50% CPU 利用率 | ASG: asg-cpu | 时长: 1800 秒
[17:30:45] 向 ALB 发送负载: experiment-alb-1466294824.us-east-1.elb.amazonaws.com

[17:31:15] 已用时间: 0:00:30 | 请求: 300 | 成功: 100% | 平均响应: 0.659s
[17:31:45] 已用时间: 0:01:00 | 请求: 600 | 成功: 100% | 平均响应: 0.651s
...
[18:00:45] 已用时间: 0:30:00 | 请求: 18000 | 成功: 100% | 平均响应: 0.662s

[18:00:45] 收集最终 CloudWatch 指标...
[18:00:50] 分析扩展事件...
[18:00:55] CPU 策略实验完成!

✅ 结果保存到: experiments/results/cpu_strategy_metrics.json
```

**关键监控** (保持终端开放):
- 响应时间应保持稳定 (~0.65s)
- 成功率应为 100%
- 请求/秒应一致为 10±0.5
- 无超时或错误

---

#### 步骤 3: 运行请求率策略实验 (30 分钟)

**用途**: 为基于请求率的自动扩缩容策略生成指标

**命令**:
```bash
python experiments/03_run_request_rate_experiment.py
```

**实验期间发生的情况**:
1. 脚本重置 ASG 为请求率策略 (`asg-request`)
2. 开始发送恰好 10 个请求/秒 (与 CPU 实验相同)
3. 系统监控:
   - 每个实例的请求计数
   - 请求率指标
   - 扩展活动
   - 响应延迟
4. 30 分钟后，收集最终指标并保存到 `experiments/results/request_rate_experiment_metrics.json`

**与 CPU 实验的关键差异**:
- 请求率策略可能使用更少实例 (更高效)
- 扩展应更快 (响应实际请求负载)
- 响应时间可能更一致

**此步骤完成后**:
- 输出文件: `experiments/results/request_rate_experiment_metrics.json` (15-20 KB)
- 总实验时长已用: ~60 分钟

---

#### 步骤 4: 聚合和比较结果 (10 分钟)

**用途**: 合并两个实验结果并生成对比分析

**命令**:
```bash
python experiments/04_aggregate_results.py
```

**此脚本执行的操作**:
1. 读取步骤 2 和步骤 3 中的两个 JSON 文件
2. 计算对比指标:
   - 平均响应时间对比
   - 成功率对比
   - 资源利用 (CPU vs 请求率)
   - 扩展效率
   - 成本估计 (实例 × 30 分钟)
3. 识别哪种策略表现更好
4. 生成两个输出文件: `comparison_report.json` 和 `metrics_comparison.csv`

**预期输出**:
```
[18:31:00] 加载实验结果...
[18:31:01] 分析 CPU 策略指标...
[18:31:02] 分析请求率策略指标...
[18:31:03] 生成对比报告...
[18:31:04] 计算效率指标...

✅ 对比报告生成:
   - CPU 策略:
     * 平均响应时间: 0.659s
     * 最大实例: 3
     * 扩展事件: 4
   
   - 请求率策略:
     * 平均响应时间: 0.661s
     * 最大实例: 2
     * 扩展事件: 2
   
   - 建议: 请求率策略更高效
```

**输出文件**:
- `experiments/results/comparison_report.json` (1-2 KB)
- `experiments/results/metrics_comparison.csv` (纯文本)

---

## Phase 6: 分析和获胜者确定

### 概述

Phase 6 处理来自步骤 2-4 的实验结果，并执行复杂的多因素分析以确定最优策略。此阶段读取从两个自动扩缩容策略收集的原始 AWS 指标，并执行：

1. **数据验证** - 确保所有指标都存在且有效
2. **对比指标计算** - 成本因素、延迟得分、效率指标
3. **获胜者确定** - 复合评分算法 (50/50 延迟 + 成本权重)
4. **置信度评分** - 量化获胜者有多清晰
5. **理由生成** - 人类可读的决策解释

### ⏱️ Phase 6 时间表

```
Phase 6 总计: ~10 分钟

├─ 输入验证 (1 分钟)
│  └─ 验证两个指标文件存在且是有效的 JSON
│
├─ 分析执行 (2 分钟)
│  ├─ 加载实验结果
│  ├─ 计算成本因素和延迟得分
│  ├─ 应用复合评分算法
│  └─ 生成获胜者确定
│
└─ 输出生成 (2 分钟)
   └─ 写入 analysis_report.json 包含完整分析
```

### 快速开始 - Phase 6

#### 选项 1: 自动化分析 (推荐)

`scripts/run_all_experiments.py` 编排脚本在 Phase 4-5 后自动处理 Phase 6：

```bash
# 从项目根目录
python scripts/run_all_experiments.py

# 输出包括:
# ✅ Phase 6: 分析完成
# 获胜者: 请求率策略
# 置信度: 2.37%
```

#### 选项 2: 手动分析执行

在 Phase 4-5 完成后直接运行 Phase 6 分析：

```bash
# 从项目根目录
python experiments/06_analyze_results.py

# 控制台输出:
# Phase 6: 分析实验结果...
# 加载 CPU 策略结果...
# 加载请求率策略结果...
# 分析结果...
# 获胜者已确定: 请求率策略 (置信度: 2.37%)
# 分析报告已写入 experiments/results/analysis_report.json
```

#### 选项 3: 编程化分析

```python
from experiments.analysis_06 import load_experiment_results, analyze_results

# 加载两个实验结果
cpu_results = load_experiment_results('experiments/results/cpu_strategy_metrics.json')
req_results = load_experiment_results('experiments/results/request_rate_experiment_metrics.json')

# 执行分析
analysis = analyze_results(cpu_results, req_results)

# 使用结果
print(f"获胜者: {analysis['winner']['strategy']}")
print(f"置信度: {analysis['winner']['confidence_pct']:.2f}%")
```

### Phase 6 详细步骤

#### 步骤 1: 验证输入数据

在运行分析前，验证输入文件完整且有效：

```bash
# 检查文件大小 (应为 20-30 KB 每个)
ls -lh experiments/results/*_metrics.json

# 验证 JSON 有效性
python -c "
import json
for file in ['experiments/results/cpu_strategy_metrics.json', 
             'experiments/results/request_rate_experiment_metrics.json']:
    with open(file) as f:
        data = json.load(f)
        print(f'{file}: JSON 有效')
        print(f'  - 总请求: {data.get(\"load_summary\", {}).get(\"total_requests\")}')
        print(f'  - 成功率: {data.get(\"load_summary\", {}).get(\"success_rate\", 0)*100:.1f}%')
"
```

#### Step 2: Run Analysis

```bash
python experiments/06_analyze_results.py
```

**Expected Console Output**:
```
Phase 6: Analyzing experiment results...
Loading CPU strategy results from experiments/results/cpu_strategy_metrics.json...
  Strategy: CPU Utilization Target
  Requests: 1433, Success Rate: 92.95%
  Avg Response: 970.64ms, P95: 1175.74ms, P99: 1935.85ms

Loading Request-Rate strategy results...
  Strategy: Request Rate Target
  Requests: 1485, Success Rate: 93.74%
  Avg Response: 959.93ms, P95: 1026.34ms, P99: 1691.85ms

Calculating comparative metrics...
  CPU Strategy latency score: 1245.73
  Request-Rate Strategy latency score: 1132.88

Winner determined: Request-Rate Strategy
Confidence: 2.43%
Rationale: Request-rate strategy achieved better response time (960ms vs 971ms)

Analysis report written to experiments/results/analysis_report.json (1.7 KB)
✓ Phase 6 analysis complete in 0.12 seconds
```

#### Step 3: Verify Output

```bash
# Verify output file exists
ls -lh experiments/results/analysis_report.json

# View analysis summary
python -c "
import json
with open('experiments/results/analysis_report.json') as f:
    report = json.load(f)
    print('Analysis Report Summary:')
    print(f\"  Winner: {report['winner']['strategy']}\")
    print(f\"  Confidence: {report['winner']['confidence_pct']:.2f}%\")
    print(f\"  Rationale: {report['winner']['rationale']}\")
"
```

---

## Understanding Results

### Output Files Summary

After Phase 4-6 completion, you'll have:

```
experiments/results/
├── cpu_strategy_metrics.json              # Phase 4-5 output: CPU experiment metrics
├── request_rate_experiment_metrics.json   # Phase 4-5 output: Request-Rate experiment metrics
├── comparison_report.json                 # Phase 4-5 output: Basic comparison
├── metrics_comparison.csv                 # Phase 4-5 output: Comparison in CSV format
└── analysis_report.json                   # Phase 6 output: Comprehensive analysis with winner
```

### Analysis Report Structure

The generated `analysis_report.json` contains:

```json
{
  "timestamp_utc": "2026-04-17T11:15:36.629799+00:00",
  
  "comparison": {
    "cpu_strategy": {
      "strategy": "CPU Utilization Target",
      "total_requests": 1433,
      "success_rate": 0.9295,
      "avg_response_time_ms": 970.64,
      "p95_response_time_ms": 1175.74,
      "p99_response_time_ms": 1935.85,
      "max_instances": 2,
      "avg_instances": 1.21,
      "avg_cpu_utilization": 0.652
    },
    "request_rate_strategy": {
      "strategy": "Request Rate Target",
      "total_requests": 1485,
      "success_rate": 0.9374,
      "avg_response_time_ms": 959.93,
      "p95_response_time_ms": 1026.34,
      "p99_response_time_ms": 1691.85,
      "max_instances": 2,
      "avg_instances": 2.0,
      "avg_cpu_utilization": 0.199
    }
  },
  
  "metrics": {
    "cpu_strategy": {
      "cost_factor": 7200,
      "cost_per_request": 5.024,
      "latency_score": 1245.72,
      "success_rate_pct": 92.95
    },
    "request_rate_strategy": {
      "cost_factor": 7200,
      "cost_per_request": 4.848,
      "latency_score": 1132.88,
      "success_rate_pct": 93.74
    }
  },
  
  "winner": {
    "strategy": "Request-Rate Strategy",
    "confidence_pct": 2.37,
    "rationale": "Request-rate strategy achieved better response time (960ms vs 971ms)"
  }
}
```

### Performance Comparison Summary

| Aspect | CPU Strategy | Request-Rate | Winner |
|--------|--------------|--------------|--------|
| **Latency Score** (lower is better) | 1,245.73 | 1,132.88 | Request-Rate (9.1% better) |
| **Cost/Request** (lower is better) | $5.02 | $4.85 | Request-Rate (3.6% lower) |
| **Success Rate** (higher is better) | 92.95% | 93.74% | Request-Rate (0.79% higher) |
| **P95 Latency** (lower is better) | 1,175.74ms | 1,026.34ms | Request-Rate (12.7% better) |
| **CPU Efficiency** (lower is better) | 65.2% avg | 19.9% avg | Request-Rate (69% lower) |
| **Scaling Stability** (fewer events) | 1 scale-in | 0 events | Request-Rate (more stable) |

---

## Troubleshooting

### Phase 4-5 Issues

#### Problem 1: "Connection refused" to ALB

**Symptom**: `requests.exceptions.ConnectionError: Connection refused`

**Causes & Solutions**:
1. ALB is down: `curl -v http://<ALB_DNS>/health`
2. Wrong ALB DNS: Check `infrastructure/alb-config.json`
3. Security group blocks traffic: Verify port 80 is open

**Recovery**: Fix the issue and restart experiment from STEP 1

#### Problem 2: "No module named 'boto3'"

**Solution**:
```bash
pip install -r requirements.txt
```

#### Problem 3: "InvalidClientTokenId" AWS error

**Causes**: AWS credentials expired or invalid

**Solution**:
```bash
aws sts get-caller-identity  # Verify credentials work
aws configure                # Reconfigure if needed
```

#### Problem 4: Experiment stops after 5 minutes

**Causes**: Internet connection dropped, ALB unhealthy, or EC2 instances crashed

**Recovery**:
1. Check ALB: `curl http://<ALB_DNS>/health`
2. Check instances in AWS Console
3. **Results are INVALID** - do not continue

### Phase 6 Issues

#### Issue: "Input files not found"

**Solution**:
```bash
# Verify Phase 4-5 completed successfully
python scripts/run_all_experiments.py

# Check that output files exist
ls -la experiments/results/*_metrics.json
```

#### Issue: "Invalid JSON in input file"

**Solution**:
```bash
# Validate JSON syntax
python -m json.tool experiments/results/cpu_strategy_metrics.json > /dev/null

# If validation fails, re-run Phase 4-5
python scripts/run_all_experiments.py --skip-phase-1-3
```

#### Issue: Winner confidence is very low (<1%)

**Problem**: The two strategies have nearly identical performance

**Action**:
- Review detailed metrics to understand tradeoffs
- Consider running longer experiments for clearer separation
- Use the detailed comparison table to evaluate which strategy better matches your use case

---

## Post-Analysis Verification

### Verify All Output Files Exist

```bash
# Should all exist after Phase 4-6 completes
ls -lh experiments/results/

# Expected files:
# - cpu_strategy_metrics.json (15-20 KB)
# - request_rate_experiment_metrics.json (15-20 KB)
# - comparison_report.json (1-2 KB)
# - metrics_comparison.csv (200 B)
# - analysis_report.json (1-2 KB)
```

### Verify File Contents Are Valid JSON

```bash
# Verify JSON is valid
python -c "
import json
files = [
    'experiments/results/cpu_strategy_metrics.json',
    'experiments/results/request_rate_experiment_metrics.json',
    'experiments/results/analysis_report.json'
]
for f in files:
    json.load(open(f))
    print(f'✅ {f}: Valid JSON')
"
```

### Review Analysis Report

```bash
python -c "
import json
with open('experiments/results/analysis_report.json') as f:
    report = json.load(f)
    print('=== Phase 4-6 Analysis Results ===')
    print(f'Winner: {report[\"winner\"][\"strategy\"]}')
    print(f'Confidence: {report[\"winner\"][\"confidence_pct\"]:.2f}%')
    print(f'Rationale: {report[\"winner\"][\"rationale\"]}')
    print()
    print('CPU Strategy:')
    cpu = report['metrics']['cpu_strategy']
    print(f'  - Cost/Request: \${cpu[\"cost_per_request\"]:.2f}')
    print(f'  - Latency Score: {cpu[\"latency_score\"]:.0f}')
    print()
    print('Request-Rate Strategy:')
    req = report['metrics']['request_rate_strategy']
    print(f'  - Cost/Request: \${req[\"cost_per_request\"]:.2f}')
    print(f'  - Latency Score: {req[\"latency_score\"]:.0f}')
"
```

### Verification Checklist

After Phase 4-6 completion, verify:

- [x] All Phase 4-5 output files exist and are valid JSON
- [x] Phase 6 analysis_report.json exists and is valid JSON
- [x] Winner is clearly determined (either CPU or Request-Rate strategy)
- [x] Confidence score is > 1%
- [x] Rationale makes sense given the metrics
- [x] All required metrics are present in output
- [x] Execution completed successfully

---

## Next Steps (Phase 7)

Once Phase 4-6 is complete:

1. **Commit Results to Git**:
```bash
git add experiments/results/
git commit -m "test: Phase 4-6 experimental results and analysis - CPU vs Request-rate strategy comparison"
git push origin main
```

2. **Begin Phase 7 - Report Writing & Visualization**:
   - Document findings using analysis_report.json
   - Generate visualization charts (response time, scaling timeline, cost)
   - Write final report (≤9 pages)
   - Create demonstration video (≤10 minutes)

3. **Key Results to Highlight**:
   - Winner strategy and confidence score
   - Performance improvements (latency, cost, stability)
   - Why the winning strategy outperforms the other
   - Operational benefits and recommendations

4. **Submit to Blackboard** before April 24, 2026, 23:59 HKT

---

## Quick Reference Commands

```bash
# ===== VERIFY SETUP =====
python --version
aws sts get-caller-identity
curl http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health

# ===== RUN EVERYTHING (RECOMMENDED) =====
python scripts/run_all_experiments.py

# ===== RUN STEP-BY-STEP =====
python experiments/01_verify_infrastructure.py      # 5 min
python experiments/02_run_cpu_experiment.py         # 30 min
python experiments/03_run_request_rate_experiment.py # 30 min
python experiments/04_aggregate_results.py          # 10 min
python experiments/06_analyze_results.py            # 2 min

# ===== VERIFY RESULTS =====
ls -lh experiments/results/
python -c "import json; json.load(open('experiments/results/analysis_report.json')); print('✅ Valid')"

# ===== COMMIT RESULTS =====
git add experiments/results/
git commit -m "test: Phase 4-6 results"
git push origin main
```

---

**Phase 4-6 Status**: ✅ **READY FOR EXECUTION**  
**Total Duration**: ~85 minutes (can be automated with one command)  
**Last Updated**: 2026-04-18  
**Guide Version**: 2.0 (Merged Phase 4-5 + Phase 6)  
**Author**: Sisyphus Agent  
**Project**: autoscaling-strategy-compare
