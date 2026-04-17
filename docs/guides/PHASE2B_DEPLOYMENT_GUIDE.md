# Phase 2B: 应用开发和部署指南

## 概述

Phase 2B 是应用开发阶段，在此阶段您将构建运行自动扩缩容实验所需的核心组件。此阶段创建三个主要组件：

1. **负载生成器** - 具有可配置流量模式的 HTTP 负载生成工具
2. **指标收集器** - 实时 AWS CloudWatch 指标轮询和导出
3. **实验运行器** - 协调负载测试和指标收集的编排层
4. **Flask 测试应用** - 轻量级测试应用，具有可配置的行为响应负载

**预计时长**: 6-10 小时  
**前置要求**: Phase 1 (AWS 基础设施) 必须完成  
**输出**: 功能完整的负载生成和指标收集工具，准备用于 Phase 3 部署

---

## 架构概述

```
Phase 2B 组件
├── 负载生成器 (scripts/load_generator.py)
│   ├── 恒定速率负载生成
│   ├── 加速上升模式
│   └── 波浪模式
│
├── 指标收集器 (scripts/metrics_collector.py)
│   ├── CloudWatch API 集成
│   ├── 实时指标轮询
│   └── CSV 导出功能
│
├── 实验运行器 (scripts/experiment_runner.py)
│   ├── 协调负载生成
│   ├── 并行收集指标
│   └── 聚合结果
│
└── Flask 测试应用 (apps/test_app/app.py)
    ├── 健康检查端点
    ├── CPU 密集型端点
    └── 数据处理端点
```

---

## 前置要求

### 系统要求

- **Python**: 3.9+ (建议升级到 3.10+)
- **AWS CLI**: v2 已配置凭证
- **虚拟环境**: 已创建并激活 (参见 README.md)

### Python 依赖

验证所有依赖都已安装：

```bash
pip install -r requirements.txt
```

所需包：
- `boto3` - Python 版 AWS SDK
- `requests` - HTTP 客户端库
- `flask` - 测试应用的 Web 框架
- `pandas` - 数据分析和导出
- `matplotlib` - 可视化 (可选，用于图表)

### AWS 前置要求

1. **AWS 账户访问**: 已从 Phase 1 配置
2. **基础设施已部署**: Phase 1 部署必须完成
3. **ALB 端点**: 记下 Phase 1 中的 ALB DNS 名称
   ```bash
   # 从 Phase 1 配置获取 ALB DNS
   cat infrastructure/alb-config.json | grep dns_name
   ```

### 验证前置要求

```bash
# 检查 Python 版本
python --version
# 预期: Python 3.9.x 或更高版本

# 验证 AWS 凭证
aws sts get-caller-identity
# 预期: 显示您的 AWS 账户 ID 和用户

# 检查 boto3 是否已安装
python -c "import boto3; print(boto3.__version__)"
# 预期: 版本 1.26+
```

---

## 快速开始

### 选项 1: 自动化设置 (推荐)

Phase 2B 设置通常由 setup.py 脚本处理：

```bash
python scripts/setup.py
```

这自动执行：
- 创建项目目录
- 验证所有依赖
- 设置 Flask 应用结构
- 测试 AWS 连接

### 选项 2: 手动逐步

按照下面详细步骤来理解每个组件。

---

## 详细实现步骤

### 步骤 1: 创建负载生成器 (load_generator.py)

**文件**: `scripts/load_generator.py`

**用途**: 使用可配置的模式生成 HTTP 请求以模拟真实流量。

**实现**:

```python
import requests
import time
import threading
from datetime import datetime

class LoadGenerator:
    def __init__(self, target_url, request_rate=10, duration_seconds=300, pattern="constant"):
        """
        初始化负载生成器。
        
        Args:
            target_url: 目标端点 (例如 http://alb-dns/api/compute)
            request_rate: 每秒请求数
            duration_seconds: 生成负载的时长
            pattern: "constant"、"ramp" 或 "wave"
        """
        self.target_url = target_url
        self.request_rate = request_rate
        self.duration_seconds = duration_seconds
        self.pattern = pattern
        self.results = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time": 0,
            "errors": []
        }
    
    def generate_constant(self):
        """生成恒定速率负载。"""
        start_time = time.time()
        request_interval = 1.0 / self.request_rate
        request_times = []
        
        while time.time() - start_time < self.duration_seconds:
            loop_start = time.time()
            
            try:
                response = requests.get(self.target_url, timeout=30)
                response_time = (time.time() - loop_start) * 1000
                request_times.append(response_time)
                
                if response.status_code == 200:
                    self.results["successful"] += 1
                else:
                    self.results["failed"] += 1
            except Exception as e:
                self.results["failed"] += 1
                self.results["errors"].append(str(e))
            
            self.results["total_requests"] += 1
            
            # 休眠以保持请求速率
            elapsed = time.time() - loop_start
            sleep_time = max(0, request_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # 计算平均值
        if request_times:
            self.results["avg_response_time"] = sum(request_times) / len(request_times)
        
        return self.results
    
    def generate_ramp(self):
        """生成加速上升模式 (速率随时间增加)。"""
        # 与恒定类似但速率不断增加
        pass
    
    def generate_wave(self):
        """生成波浪模式 (速率峰值和谷值)。"""
        # 与恒定类似但具有波浪变化
        pass
    
    def run(self):
        """根据选定的模式执行负载生成。"""
        if self.pattern == "constant":
            return self.generate_constant()
        elif self.pattern == "ramp":
            return self.generate_ramp()
        elif self.pattern == "wave":
            return self.generate_wave()
        else:
            raise ValueError(f"未知模式: {self.pattern}")
```

**验证**:

```bash
# 使用简单的回显端点测试负载生成器
python -c "
from scripts.load_generator import LoadGenerator
gen = LoadGenerator(
    target_url='http://httpbin.org/get',
    request_rate=5,
    duration_seconds=10,
    pattern='constant'
)
results = gen.run()
print(f\"总请求数: {results['total_requests']}\")
print(f\"成功: {results['successful']}\")
print(f\"失败: {results['failed']}\")
print(f\"平均响应时间: {results['avg_response_time']:.2f}ms\")
"
```

**预期输出**:
```
总请求数: 50
成功: 50
失败: 0
平均响应时间: 245.32ms
```

---

### 步骤 2: 创建指标收集器 (metrics_collector.py)

**文件**: `scripts/metrics_collector.py`

**用途**: 在实验期间轮询 AWS CloudWatch 以获取自动扩展指标。

**实现**:

```python
import boto3
import json
import csv
from datetime import datetime, timedelta

class MetricsCollector:
    def __init__(self, region="us-east-1"):
        """初始化 CloudWatch 客户端。"""
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)
        self.autoscaling = boto3.client("autoscaling", region_name=region)
        self.metrics = []
    
    def get_asg_metrics(self, asg_name, duration_minutes=30):
        """
        为自动扩展组收集指标。
        
        Args:
            asg_name: ASG 的名称 (例如 "asg-cpu")
            duration_minutes: 查询多少分钟的数据
        
        Returns:
            包含指标数据的字典
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        metrics_data = {
            "asg_name": asg_name,
            "cpu_utilization": [],
            "group_desired_capacity": [],
            "group_in_service_instances": [],
            "request_count": []
        }
        
        # 收集 CPU 利用率
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,  # 1 分钟间隔
            Statistics=["Average"]
        )
        metrics_data["cpu_utilization"] = response["Datapoints"]
        
        # 收集组期望容量
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/AutoScaling",
            MetricName="GroupDesiredCapacity",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=["Average"]
        )
        metrics_data["group_desired_capacity"] = response["Datapoints"]
        
        # 收集服务中实例
        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/AutoScaling",
            MetricName="GroupInServiceInstances",
            Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=["Average"]
        )
        metrics_data["group_in_service_instances"] = response["Datapoints"]
        
        return metrics_data
    
    def export_to_csv(self, filename, metrics_dict):
        """将指标导出到 CSV 文件。"""
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "metric_name", "value"])
            writer.writeheader()
            
            for metric_name, datapoints in metrics_dict.items():
                if metric_name == "asg_name":
                    continue
                for point in datapoints:
                    writer.writerow({
                        "timestamp": point.get("Timestamp", ""),
                        "metric_name": metric_name,
                        "value": point.get("Average", "")
                    })
```

**验证**:

```bash
# 测试指标收集器
python -c "
from scripts.metrics_collector import MetricsCollector
collector = MetricsCollector()
metrics = collector.get_asg_metrics('asg-cpu', duration_minutes=5)
print(f\"CPU 数据点: {len(metrics['cpu_utilization'])}\")
print(f\"容量数据点: {len(metrics['group_desired_capacity'])}\")
"
```

---

### 步骤 3: 创建 Flask 测试应用

**文件**: `apps/test_app/app.py`

**用途**: 轻量级 Flask 应用，响应 CPU 密集操作的负载。

**实现**:

```python
from flask import Flask, jsonify, request
import time
import os

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """健康检查端点。"""
    return jsonify({"status": "healthy"}), 200

@app.route("/api/compute", methods=["GET"])
def compute():
    """CPU 密集型计算端点。"""
    intensity = int(request.args.get("intensity", 1))
    
    # 模拟 CPU 工作
    result = 0
    for i in range(1000000 * intensity):
        result += i ** 2
    
    return jsonify({
        "status": "success",
        "computation": result,
        "intensity": intensity
    }), 200

@app.route("/api/data", methods=["GET"])
def data():
    """数据处理端点。"""
    size = int(request.args.get("size", 1000))
    
    # 创建和处理数据
    data_list = list(range(size))
    processed = sum(data_list) / len(data_list)
    
    return jsonify({
        "status": "success",
        "data_size": size,
        "average": processed
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

**本地测试**:

```bash
# 启动应用
python apps/test_app/app.py &

# 测试端点
curl http://localhost:5000/health
curl http://localhost:5000/api/compute?intensity=1
curl http://localhost:5000/api/data?size=1000

# 终止应用
pkill -f "python apps/test_app/app.py"
```

---

### 步骤 4: 创建实验运行器

**文件**: `scripts/experiment_runner.py`

**用途**: 编排负载生成和指标收集。

**实现**:

```python
import json
import threading
from datetime import datetime
from scripts.load_generator import LoadGenerator
from scripts.metrics_collector import MetricsCollector

class ExperimentRunner:
    def __init__(self, alb_endpoint, asg_names, experiment_name):
        self.alb_endpoint = alb_endpoint
        self.asg_names = asg_names
        self.experiment_name = experiment_name
        self.results = {}
    
    def run_experiment(self, duration_seconds=300, request_rate=10):
        """运行带负载生成和指标收集的完整实验。"""
        # 在后台启动指标收集
        collector = MetricsCollector()
        metrics_thread = threading.Thread(
            target=self._collect_metrics,
            args=(collector,)
        )
        metrics_thread.start()
        
        # 运行负载生成
        generator = LoadGenerator(
            target_url=f"http://{self.alb_endpoint}/api/compute",
            request_rate=request_rate,
            duration_seconds=duration_seconds,
            pattern="constant"
        )
        load_results = generator.run()
        
        # 等待指标收集完成
        metrics_thread.join()
        
        # 聚合结果
        self.results = {
            "experiment": self.experiment_name,
            "timestamp": datetime.utcnow().isoformat(),
            "load": load_results,
            "metrics": self.metrics
        }
        
        return self.results
    
    def _collect_metrics(self, collector):
        """为所有 ASG 收集指标。"""
        self.metrics = {}
        for asg_name in self.asg_names:
            self.metrics[asg_name] = collector.get_asg_metrics(asg_name)
    
    def save_results(self, filename):
        """将实验结果保存到 JSON 文件。"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
```

---

## 验证检查清单

在进行 Phase 3 之前，验证每个组件：

- [ ] 负载生成器
  ```bash
  python scripts/load_generator.py --help
  # 不应显示错误
  ```

- [ ] 指标收集器
  ```bash
  python -c "from scripts.metrics_collector import MetricsCollector; print('OK')"
  # 应打印: OK
  ```

- [ ] Flask 应用 (本地测试)
  ```bash
  python apps/test_app/app.py &
  sleep 2
  curl http://localhost:5000/health
  pkill -f "test_app"
  # 应显示: {"status":"healthy"}
  ```

- [ ] experiment_runner.py 中的所有导入
  ```bash
  python -c "from scripts.experiment_runner import ExperimentRunner; print('OK')"
  # 应打印: OK
  ```

---

## 故障排查

### 问题: ImportError: 找不到 'boto3' 模块

**解决方案**: 安装依赖
```bash
pip install -r requirements.txt
```

### 问题: 未找到 AWS 凭证

**解决方案**: 配置 AWS CLI
```bash
aws configure
# 输入: 访问密钥、秘密密钥、区域 (us-east-1)、输出 (json)
```

### 问题: 连接 ALB 时连接错误

**解决方案**: 验证 Phase 1 部署
```bash
# 获取 ALB DNS
cat infrastructure/alb-config.json | grep dns_name

# 测试连接
curl http://<ALB-DNS>/health
```

### 问题: Flask 应用启动失败

**解决方案**: 检查端口可用性
```bash
# 检查端口 5000 是否被使用
lsof -i :5000

# 使用不同端口
PORT=5001 python apps/test_app/app.py
```

---

## 后续步骤

验证了 Phase 2B 组件后：

1. 将测试应用移至 EC2 实例 (Phase 3)
2. 将负载生成器和指标收集器部署到单独的 EC2 实例 (Phase 3)
3. 为两个 ASG 配置自动扩展策略 (Phase 3)
4. 使用这些工具运行 Phase 4-5 实验

请参阅 **Phase 3 部署指南**了解后续步骤。
