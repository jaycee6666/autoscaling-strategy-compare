# 🎯 快速参考卡 - 跨平台执行计划

## ⚡ 最常用命令（复制粘贴）

### 新成员入门
```bash
# 1. 克隆
git clone <repo-url>
cd autoscaling-project

# 2. 环境检查
python scripts/check_environment.py

# 3. 项目初始化
python scripts/init_project.py

# 4. 安装依赖
pip install -r requirements.txt
```

### 基础设施部署
```bash
# 一键部署所有
python scripts/deploy_all.py

# 或分阶段部署
python scripts/setup_network.py
python scripts/setup_security_groups.py
python scripts/setup_iam_role.py
python scripts/setup_alb.py
python scripts/create_ami.py
python scripts/setup_asg.py
```

### 验证部署
```bash
# 检查所有资源
python scripts/verify_deployment.py

# 或手动检查
aws ec2 describe-vpcs
aws ec2 describe-security-groups
aws elbv2 describe-load-balancers
aws autoscaling describe-auto-scaling-groups
```

### 实验执行
```bash
# 运行实验
python load-testing/run_experiment.py

# 收集数据
python data-collection/collect_metrics.py

# 分析数据
python data-collection/analyze_results.py
```

### 清理资源（实验完后执行！）
```bash
python scripts/cleanup_infrastructure.py
```

### Git工作流
```bash
# 提交代码
git add .
git commit -m "message"
git push origin main

# 获取最新
git pull origin main

# 创建分支
git checkout -b feature/your-feature
```

---

## 📊 文件结构速查

```
project-root/
├─ scripts/              # 所有可执行脚本
│  ├─ check_environment.py      # 环境检查
│  ├─ init_project.py           # 项目初始化
│  ├─ deploy_all.py             # 一键部署
│  ├─ setup_*.py                # 各个模块安装
│  ├─ verify_deployment.py      # 验证部署
│  └─ cleanup_infrastructure.py # 清理
│
├─ config/              # 配置文件
│  ├─ project_config.json       # 项目配置
│  └─ .env                       # 环境变量（勿提交）
│
├─ infrastructure/      # AWS配置和资源ID
│  ├─ network-config.json
│  ├─ security-group-config.json
│  └─ ...
│
├─ application/         # Flask应用
│  ├─ app.py
│  ├─ requirements.txt
│  └─ Dockerfile
│
├─ load-testing/        # Locust负载测试
│  ├─ locustfile.py
│  └─ run_experiment.py
│
├─ data-collection/     # 数据收集和分析
│  ├─ collect_metrics.py
│  └─ analyze_results.py
│
├─ results/            # 实验结果
│  ├─ scenario_a_spike_metrics.json
│  ├─ scenario_b_spike_metrics.json
│  └─ summary.json
│
├─ report/             # 最终报告
│  └─ GroupID_report.pdf
│
├─ PROJECT_EXECUTION_PLAN.md      # 完整执行计划
├─ CROSSPLATFORM_GUIDE.md         # 跨平台指南
├─ ACCEPTANCE_CRITERIA.md         # 验收标准
└─ OPTIMIZATION_SUMMARY.md        # 优化总结
```

---

## ⏰ 时间表速查

| 周数 | 任务 | 关键命令 |
|-----|-----|--------|
| 1-2 | 环境+基础设施 | `python scripts/deploy_all.py` |
| 2-3 | 应用开发 | `python application/app.py` |
| 4 | 部署验证 | `python scripts/verify_deployment.py` |
| 5-6 | 实验执行 | `python load-testing/run_experiment.py` |
| 7 | 数据分析 | `python data-collection/analyze_results.py` |
| 8-9 | 报告+视频 | 手动完成 |
| 10 | 最终提交 | `git push` + Canvas提交 |

---

## 🔧 故障排除速查

### 问题：环境检查失败
```bash
# 解决
python scripts/check_environment.py  # 查看具体错误
# 根据错误信息安装缺失的工具
```

### 问题：AWS CLI报错
```bash
# 检查凭证
aws sts get-caller-identity

# 重新配置
aws configure
```

### 问题：VPC创建失败
```bash
# 检查quota限制
aws service-quotas list-service-quotas \
  --service-code ec2 \
  --region us-east-1
```

### 问题：实例无法启动
```bash
# 检查安全组
aws ec2 describe-security-groups

# 检查子网
aws ec2 describe-subnets
```

### 问题：Locust连接失败
```bash
# 检查ALB
aws elbv2 describe-load-balancers

# 测试ALB
curl http://<ALB_DNS>/health
```

---

## 💰 成本优化速查

| 操作 | 成本 | 优化建议 |
|-----|------|---------|
| EC2 t2.micro | $0.01/hr | ✓ 用了 |
| ALB | $0.0225/hr | 配置时间 |
| Data出站 | $0.02/GB | 在VPC内测试 |
| CloudWatch | $0.10/指标 | 用了合理数量 |
| **总计** | **$50-100** | 实验后立即删除 |

**节省方法:**
```bash
# 1. 实验后立即清理
python scripts/cleanup_infrastructure.py

# 2. 使用Free Tier
# - 750小时/月 t2.micro（12个月）
# - 15GB数据传出（12个月）

# 3. 监控费用
aws ce get-cost-and-usage ...
```

---

## 🐍 Python常用片段

### 运行AWS CLI命令
```python
import subprocess
import json

result = subprocess.run(
    ['aws', 'ec2', 'describe-vpcs', '--output', 'json'],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
```

### 处理路径（跨平台）
```python
from pathlib import Path

# 自动适配所有OS
config_path = Path('config') / 'project_config.json'
results_dir = Path('results')
results_dir.mkdir(exist_ok=True)

# 不要用字符串拼接！
# ❌ path = "results\data.json"  # Windows only
# ✅ path = Path('results') / 'data.json'  # All OS
```

### 加载环境变量
```python
from dotenv import load_dotenv
import os

load_dotenv()
aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
```

### 日志记录
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting deployment...")
logger.error("Deployment failed!")
```

---

## 📋 检查清单（使用前）

### 部署前
- [ ] `python scripts/check_environment.py` ✓
- [ ] `python scripts/init_project.py` ✓
- [ ] 编辑 `config/project_config.json` ✓
- [ ] AWS凭证配置完成 ✓

### 部署中
- [ ] 网络资源创建 ✓
- [ ] 安全组配置 ✓
- [ ] IAM角色创建 ✓
- [ ] ALB创建 ✓
- [ ] AMI创建 ✓
- [ ] ASG创建 ✓

### 部署后
- [ ] `python scripts/verify_deployment.py` ✓
- [ ] ALB可访问 ✓
- [ ] CloudWatch指标可见 ✓
- [ ] 实例状态正常 ✓

### 实验前
- [ ] Locust安装 ✓
- [ ] 负载生成脚本就绪 ✓
- [ ] 数据收集脚本就绪 ✓
- [ ] 输出目录创建 ✓

### 实验后
- [ ] 数据文件检查 ✓
- [ ] 数据完整性验证 ✓
- [ ] 分析脚本运行 ✓
- [ ] 图表和表格生成 ✓

### 提交前
- [ ] 报告完成且在9页以内 ✓
- [ ] 演示视频完成且≤10分钟 ✓
- [ ] GitHub提交历史完整 ✓
- [ ] 资源已清理 ✓

---

## 🎓 学习资源链接

| 资源 | 链接 |
|-----|-----|
| AWS CLI 官方文档 | https://docs.aws.amazon.com/cli/ |
| Python 官方文档 | https://docs.python.org/3/ |
| Git 官方文档 | https://git-scm.com/doc |
| Locust 文档 | https://locust.io/docs/ |
| Boto3 文档 | https://boto3.amazonaws.com/v1/documentation/ |
| IAM 最佳实践 | https://docs.aws.amazon.com/IAM/latest/UserGuide/ |

---

## 🎯 成功标志

✅ **环境就绪**
- 所有检查通过

✅ **基础设施部署**
- 一键部署成功

✅ **应用运行**
- 本地测试通过

✅ **实验执行**
- 数据收集完成

✅ **分析完成**
- 图表和表格生成

✅ **报告提交**
- PDF上传成功

✅ **视频上传**
- YouTube/B站公开

✅ **项目完成**
- 所有资源清理

---

**印记**: 按照这个快速参考卡，即使是新手也能顺利完成项目！📚

