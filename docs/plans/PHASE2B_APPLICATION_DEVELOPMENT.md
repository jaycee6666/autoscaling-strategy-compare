# Phase 2B: 应用开发实现计划

> **对于 Claude**: 必需的子技能：使用 superpowers:subagent-driven-development 或 superpowers:executing-plans 逐任务实现本计划。

**目标**: 创建负载生成工具、指标收集实用程序和测试 Flask 应用以支持自动扩缩容实验。

**架构**: 
- **load_generator.py**: 具有可配置模式的 HTTP 负载生成（恒定/加速/波浪）
- **metrics_collector.py**: 实时 CloudWatch 指标轮询和 CSV 导出
- **experiment_runner.py**: 协调负载测试和指标收集的编排层
- **apps/test_app/app.py**: 轻量级 Flask 应用，包含健康检查、数据端点和 CPU 密集型操作

**技术栈**: 
- Python 3.8+、boto3、requests、Flask、pandas、matplotlib
- AWS CloudWatch API
- HTTP/REST 协议

> ⚠️ **规范指南**: 有关分步实现说明，请参阅 **[../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)**。本文档包含规划任务和验证步骤；部署指南包含详细的代码和设置说明。

---

## 实现任务

**有关完整的分步实现说明、代码示例和验证流程，请参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md)**

此计划文档概述了任务结构和验证标准。规范执行指南位于 guides/ 目录中。

### 任务 1: 创建负载生成器核心

**文件**:
- 创建: `scripts/load_generator.py`
- 测试: `tests/test_load_generator.py`

**目标**: 实现具有可配置模式的 HTTP 负载生成（恒定速率、加速、波浪）。

**交付物**:
- ✅ LoadGenerator 类，支持恒定/加速/波浪模式
- ✅ 基于线程的请求执行，支持可配置的并发
- ✅ 响应时间跟踪和统计分析（平均值、P95）
- ✅ 负载统计的 CSV 导出功能
- ✅ 全面的测试套件（≥4 个测试用例）

**成功标准**:
- `pytest tests/test_load_generator.py` 返回全部通过
- LoadGenerator 生成正确的请求速率，容差在 ±10% 以内
- 响应时间以微秒精度捕获

**实现**: 参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) 中的任务 1

---

### 任务 2: 创建指标收集器

**文件**:
- 创建: `scripts/metrics_collector.py`
- 测试: `tests/test_metrics_collector.py`

**目标**: 轮询 CloudWatch 指标以了解 ASG 健康状况、实例计数和 CPU 利用率。

**交付物**:
- ✅ MetricsCollector 类，支持后台轮询线程
- ✅ CPU 利用率、网络指标的 CloudWatch 集成
- ✅ ASG 集成，用于实例计数和健康状态
- ✅ CSV 导出，包含时间戳、CPU、instance_count、request_rate 列
- ✅ 摘要统计（所有指标的平均值、最小值、最大值）
- ✅ 全面的测试套件（≥3 个测试用例）

**成功标准**:
- `pytest tests/test_metrics_collector.py` 返回全部通过
- 指标在可配置的间隔（默认 10 秒）收集
- CSV 导出包含有效的时间戳和数值数据

**实现**: 参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) 中的任务 2

---

### 任务 3: 创建实验运行器编排器

**文件**:
- 创建: `scripts/experiment_runner.py`
- 测试: `tests/test_experiment_runner.py`

**目标**: 协调负载生成和指标收集以进行实验。

**交付物**:
- ✅ ExperimentRunner 类，协调负载 + 指标
- ✅ 每个实验的自动输出目录创建
- ✅ 负载和指标收集的并行执行
- ✅ 包含元数据和结果的 JSON 实验日志
- ✅ 结果导出：experiment_log.json、load_stats.csv、metrics.csv
- ✅ 包含状态、负载统计、指标摘要的结果摘要
- ✅ 全面的测试套件（≥3 个测试用例）

**成功标准**:
- `pytest tests/test_experiment_runner.py` 返回全部通过
- ExperimentRunner 验证参数（正数请求速率、持续时间、有效模式）
- 在 experiments/<experiment_name>/ 下成功创建输出目录
- 成功运行后生成所有三个输出文件

**实现**: 参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) 中的任务 3

---

### 任务 4: 创建测试 Flask 应用

**文件**:
- 创建: `apps/test_app/app.py`
- 创建: `apps/test_app/Dockerfile`
- 测试: `tests/test_app_endpoints.py`

**目标**: 用于测试自动扩缩容策略的轻量级 HTTP 服务。

**交付物**:
- ✅ Flask 应用监听 0.0.0.0:8080
- ✅ `/health` 端点 (GET): 简单的健康检查
- ✅ `/data` 端点 (GET): 返回可配置的随机负载
- ✅ `/cpu-intensive` 端点 (POST): CPU 密集型工作负载模拟
- ✅ `/metrics` 端点 (GET): 进程内请求跟踪
- ✅ `/reset` 端点 (POST): 重置指标计数器
- ✅ Dockerfile，使用 Python 3.9 基础、健康检查、自动重启
- ✅ 全面的端点测试（≥5 个测试用例）

**成功标准**:
- `pytest tests/test_app_endpoints.py` 返回全部通过
- Flask 应用独立运行: `python apps/test_app/app.py`
- Docker 构建成功: `docker build -t test-app:latest apps/test_app`
- 所有端点对有效请求的响应均为 200 OK
- 容器中的 HEALTHCHECK curl 命令成功

**实现**: 参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) 中的任务 4

---

### 任务 5: 项目结构和文档

**文件**:
- 更新: `README.md` (添加 Phase 2B 参考)
- 更新: 文档交叉引用

**目标**: 记录 Phase 2B 组件和用法。

**交付物**:
- ✅ README.md 更新，包含 Phase 2B 快速开始
- ✅ 从规划文档到规范部署指南的清晰参考
- ✅ Phase 2B 输出整合到 Phase 3 的说明

**成功标准**:
- README.md 包含 Phase 2B 部分，包含组件概述
- 用户可以从本文档找到部署指南
- 计划和指南文档之间没有破损的链接

**实现**: 参阅 [../guides/PHASE2B_DEPLOYMENT_GUIDE.md](../guides/PHASE2B_DEPLOYMENT_GUIDE.md) 中的任务 5

---

## 提交指南

实现此计划时，请使用描述性消息进行原子提交：

```bash
# 任务 1 提交
git add scripts/load_generator.py tests/test_load_generator.py
git commit -m "feat: 实现具有恒定/加速/波浪模式的 LoadGenerator

- 添加具有可配置 HTTP 负载生成的 LoadGenerator 类
- 支持恒定、加速和波浪负载模式
- 跟踪响应时间、成功率和错误
- 将统计信息导出到 CSV 格式
- 添加全面的测试套件"

# 任务 2 提交
git add scripts/metrics_collector.py tests/test_metrics_collector.py
git commit -m "feat: 实现用于 CloudWatch 监控的 MetricsCollector

- 添加后台指标收集线程
- 轮询 ASG 指标：CPU、实例计数、健康状态
- 支持网络指标（进出字节）
- 将指标历史导出到 CSV 格式
- 添加全面的测试套件"

# 任务 3 提交
git add scripts/experiment_runner.py tests/test_experiment_runner.py
git commit -m "feat: 实现 ExperimentRunner 编排

- 协调负载生成和指标收集
- 运行带有验证的完整实验
- 导出结果（日志、统计、指标）
- 提供实验结果摘要"

# 任务 4 提交
git add apps/test_app/app.py apps/test_app/Dockerfile tests/test_app_endpoints.py
git commit -m "feat: 为自动扩缩容创建测试 Flask 应用

- 添加 /health 端点用于 ALB 健康检查
- 添加 /data 端点用于负载测试
- 添加 /cpu-intensive 端点用于 CPU 策略测试
- 添加 /metrics 端点用于应用指标
- Dockerize 应用用于 AWS 部署
- 添加全面的端点测试"
```

---

## 验证清单

- [ ] 所有任务均按部署指南实现
- [ ] 所有测试通过: `pytest tests/test_*.py -v`
- [ ] 类型检查清晰: `mypy scripts apps tests` (如果可用)
- [ ] 所有文件使用 boto3（无 AWS CLI 子流程调用）
- [ ] 跨平台兼容（Windows/macOS/Linux）
- [ ] Git 提交使用作者: jaycee6666 <sijiechan2-c@my.cityu.edu.hk>
- [ ] README.md 更新，包含 Phase 2B 概述
- [ ] 所有交付物正常工作
- [ ] 输出目录结构: experiments/<name>/{experiment_log.json, load_stats.csv, metrics.csv}

---

## 后续步骤 (Phase 3)

完成 Phase 2B 实现和验证后：
1. 将测试 Flask 应用部署到 AWS EC2 实例
2. 配置 ALB 以将流量路由到应用
3. 验证应用健康检查成功
4. 继续进行 Phase 4-5 实验执行
