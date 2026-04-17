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
├─ Step 3: Request-Rate Strategy Experiment (30 min)
│  └─ Command: python experiments/03_run_request_rate_experiment.py
│     Output: request_rate_experiment_metrics.json (~18,000 requests)
│     Monitors: Request rate, scaling behavior, latency
│
└─ Step 4: Aggregate & Compare Results (10 min)
   └─ Command: python experiments/04_aggregate_results.py
      Outputs: comparison_report.json, metrics_comparison.csv
      Analysis: Scaling efficiency, responsiveness, resource utilization
```

### Critical Success Requirements

For valid experiment results:
1. ✅ Load generator must maintain exactly 10 requests/second (±0.5 req/s)
2. ✅ No network interruptions during 30-minute periods
3. ✅ No manual ASG changes during experiments (hands-off)
4. ✅ CloudWatch metrics available for collection (5-minute lag acceptable)
5. ✅ Output files contain real AWS metrics, not mock data

### 🚀 Detailed Step-by-Step Execution

#### STEP 1: Verify Infrastructure (5 minutes)

**Purpose**: Confirm all AWS resources are healthy before running experiments

**Command**:
```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
python experiments/01_verify_infrastructure.py
```

**Expected Output**:
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

**What to Check**:
- ✅ `alb_health.status` = `"healthy"` (must be true)
- ✅ All instances show running state
- ✅ `asg_cpu.current` matches `asg_cpu.desired`
- ✅ `asg_request.current` matches `asg_request.desired`
- ❌ **STOP if**: Any instance is stopped or terminated

**Troubleshooting**:
- If ALB returns 502/503: instances may not be fully booted. Wait 2 minutes, retry.
- If instance count mismatch: ASG may be scaling. Wait for stability, retry.

---

#### STEP 2: Run CPU Strategy Experiment (30 minutes)

**Purpose**: Generate metrics for CPU-based autoscaling strategy

**Command**:
```bash
python experiments/02_run_cpu_experiment.py
```

**What Happens During Experiment**:
1. Script connects to ALB and begins sending exactly 10 requests/second
2. CloudWatch metrics collection starts (background)
3. System monitors:
   - CPU utilization of each instance
   - Request count and response times
   - Scaling activities (scale-out/scale-in events)
   - Instance lifecycle changes
4. After 30 minutes, script collects final metrics and saves to `experiments/results/cpu_strategy_metrics.json`

**Console Output** (real-time monitoring):
```
[17:30:45] CPU Strategy Experiment Started
[17:30:45] Target: 50% CPU utilization | ASG: asg-cpu | Duration: 1800 seconds
[17:30:45] Sending load to ALB: experiment-alb-1466294824.us-east-1.elb.amazonaws.com

[17:31:15] Elapsed: 0:00:30 | Requests: 300 | Success: 100% | Avg Response: 0.659s
[17:31:45] Elapsed: 0:01:00 | Requests: 600 | Success: 100% | Avg Response: 0.651s
...
[18:00:45] Elapsed: 0:30:00 | Requests: 18000 | Success: 100% | Avg Response: 0.662s

[18:00:45] Collecting final CloudWatch metrics...
[18:00:50] Analyzing scaling events...
[18:00:55] CPU Strategy Experiment Complete!

✅ Results saved to: experiments/results/cpu_strategy_metrics.json
```

**Critical Monitoring** (Keep terminal open):
- Response time should remain stable (~0.65s)
- Success rate should be 100%
- Requests/second should be consistently 10±0.5
- No timeouts or errors

---

#### STEP 3: Run Request-Rate Strategy Experiment (30 minutes)

**Purpose**: Generate metrics for request-rate-based autoscaling strategy

**Command**:
```bash
python experiments/03_run_request_rate_experiment.py
```

**What Happens During Experiment**:
1. Script resets ASG to request-rate strategy (`asg-request`)
2. Begins sending exactly 10 requests/second (same as CPU experiment)
3. System monitors:
   - Request count per instance
   - Request rate metrics
   - Scaling activities
   - Response latency
4. After 30 minutes, collects final metrics and saves to `experiments/results/request_rate_experiment_metrics.json`

**Key Difference vs CPU Experiment**:
- Request-rate strategy may use fewer instances (more efficient)
- Scaling should be faster (responds to actual request load)
- Response times may be more consistent

**After This Step Completes**:
- Output file: `experiments/results/request_rate_experiment_metrics.json` (15-20 KB)
- Total experiment time elapsed: ~60 minutes

---

#### STEP 4: Aggregate & Compare Results (10 minutes)

**Purpose**: Combine both experiment results and generate comparison analysis

**Command**:
```bash
python experiments/04_aggregate_results.py
```

**What This Script Does**:
1. Reads both JSON files from Step 2 and Step 3
2. Calculates comparative metrics:
   - Average response time comparison
   - Success rate comparison
   - Resource utilization (CPU vs Request-rate)
   - Scaling efficiency
   - Cost estimate (instances × 30 min)
3. Identifies which strategy performed better
4. Generates two output files: `comparison_report.json` and `metrics_comparison.csv`

**Expected Output**:
```
[18:31:00] Loading experiment results...
[18:31:01] Analyzing CPU strategy metrics...
[18:31:02] Analyzing request-rate strategy metrics...
[18:31:03] Generating comparison report...
[18:31:04] Calculating efficiency metrics...

✅ Comparison Report Generated:
   - CPU Strategy:
     * Avg Response Time: 0.659s
     * Max Instances: 3
     * Scaling Events: 4
   
   - Request-Rate Strategy:
     * Avg Response Time: 0.661s
     * Max Instances: 2
     * Scaling Events: 2
   
   - Recommendation: Request-rate strategy is more efficient
```

**Output Files**:
- `experiments/results/comparison_report.json` (1-2 KB)
- `experiments/results/metrics_comparison.csv` (plaintext)

---

## Phase 6: Analysis & Winner Determination

### Overview

Phase 6 processes the experimental results from Steps 2-4 and performs sophisticated multi-factor analysis to determine the optimal strategy. This phase reads the raw AWS metrics collected from both autoscaling strategies and performs:

1. **Data validation** - Ensures all metrics are present and valid
2. **Comparative metrics calculation** - Cost factors, latency scores, efficiency metrics
3. **Winner determination** - Composite scoring algorithm (50/50 latency + cost weighting)
4. **Confidence scoring** - Quantifies how clear the winner is
5. **Rationale generation** - Human-readable explanation of decision

### ⏱️ Timeline for Phase 6

```
Phase 6 Total: ~10 minutes

├─ Input validation (1 min)
│  └─ Verify both metric files exist and are valid JSON
│
├─ Analysis execution (2 min)
│  ├─ Load experiment results
│  ├─ Calculate cost factors and latency scores
│  ├─ Apply composite scoring algorithm
│  └─ Generate winner determination
│
└─ Output generation (2 min)
   └─ Write analysis_report.json with complete analysis
```

### Quick Start - Phase 6

#### Option 1: Automated Analysis (Recommended)

The `scripts/run_all_experiments.py` orchestration script handles Phase 6 automatically after Phase 4-5:

```bash
# From project root
python scripts/run_all_experiments.py

# Output includes:
# ✅ Phase 6: Analysis completed
# Winner: Request-Rate Strategy
# Confidence: 2.37%
```

#### Option 2: Manual Analysis Execution

Run Phase 6 analysis directly (after Phase 4-5 is complete):

```bash
# From project root
python experiments/06_analyze_results.py

# Console output:
# Phase 6: Analyzing experiment results...
# Loading CPU strategy results...
# Loading Request-Rate strategy results...
# Analyzing results...
# Winner determined: Request-Rate Strategy (confidence: 2.37%)
# Analysis report written to experiments/results/analysis_report.json
```

#### Option 3: Programmatic Analysis

```python
from experiments.analysis_06 import load_experiment_results, analyze_results

# Load both experiment results
cpu_results = load_experiment_results('experiments/results/cpu_strategy_metrics.json')
req_results = load_experiment_results('experiments/results/request_rate_experiment_metrics.json')

# Perform analysis
analysis = analyze_results(cpu_results, req_results)

# Use the results
print(f"Winner: {analysis['winner']['strategy']}")
print(f"Confidence: {analysis['winner']['confidence_pct']:.2f}%")
```

### Phase 6 Detailed Steps

#### Step 1: Verify Input Data

Before running analysis, validate that input files are complete and valid:

```bash
# Check file sizes (should be 20-30 KB each)
ls -lh experiments/results/*_metrics.json

# Verify JSON validity
python -c "
import json
for file in ['experiments/results/cpu_strategy_metrics.json', 
             'experiments/results/request_rate_experiment_metrics.json']:
    with open(file) as f:
        data = json.load(f)
        print(f'{file}: Valid JSON')
        print(f'  - Total requests: {data.get(\"load_summary\", {}).get(\"total_requests\")}')
        print(f'  - Success rate: {data.get(\"load_summary\", {}).get(\"success_rate\", 0)*100:.1f}%')
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
