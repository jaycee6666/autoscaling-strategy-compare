# Phase 4-5 实验执行 - 清晰指南

**针对你的三个问题的明确答案**

---

## ❓ 问题1：参考哪个文档？

### 推荐顺序：

1. **先读这个文件** (你现在读的) - 3分钟
   - 告诉你如何设置环境、用哪个shell、是否需要venv
   
2. **然后参考** `PHASE4_5_QUICK_START.md` - 5分钟快速了解
   - 实验的目的、预期结果、基本命令
   
3. **遇到问题时** 参考 `PHASE4_5_EXECUTION_GUIDE.md`
   - 详细的故障排除、监控方法、输出文件解释
   - 有问题？先搜索这个文件的 Troubleshooting 部分

### 简单版本
```
不想看太多文档？ → 只读下面的三个部分就行
```

---

## ❓ 问题2：CMD 还是 PowerShell？

### 推荐方案 (优先级排序)

#### ✅ 方案A：CMD (推荐 - 最简单)
```bash
# 1. 打开 CMD (命令提示符)
#    Win + R → 输入 "cmd" → 回车

# 2. 进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 3. 激活虚拟环境
venv\Scripts\activate.bat

# 4. 运行实验脚本
python experiments/01_verify_infrastructure.py
python experiments/02_run_cpu_experiment.py
python experiments/03_run_request_rate_experiment.py
python experiments/04_aggregate_results.py
```

#### ✅ 方案B：PowerShell (也可以，稍微复杂一点)
```powershell
# 1. 打开 PowerShell (以管理员身份推荐)
#    Win + X → 选 "Windows PowerShell (Admin)"

# 2. 进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 注意: 如果出现错误 "不能加载文件...脚本在此系统上被禁用"
# 执行这条命令一次:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. 运行实验脚本
python experiments/01_verify_infrastructure.py
python experiments/02_run_cpu_experiment.py
python experiments/03_run_request_rate_experiment.py
python experiments/04_aggregate_results.py
```

#### ❌ 不推荐方案C：Git Bash
- 虽然可以用，但在 Windows 上有路径转换问题
- 如果你已经用了也没问题，但推荐用 CMD 或 PowerShell

### 我的建议
**用 CMD** - 最稳定，没有特殊问题，命令最少

---

## ❓ 问题3：是否需要在 venv 中运行？

### 短答案
**是的，需要。** 必须先激活 venv，然后再运行脚本。

### 为什么需要 venv？
- 项目依赖在 `requirements.txt` 中定义 (boto3, requests 等)
- venv 隔离这些依赖，防止版本冲突
- 在 venv 外运行脚本会导致 `ModuleNotFoundError`

### 完整流程 (使用 CMD - 推荐)

```bash
# 1️⃣ 打开 CMD，进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 2️⃣ 检查 venv 是否存在
# 应该看到 venv 目录存在
dir venv

# 3️⃣ 激活虚拟环境
venv\Scripts\activate.bat

# ✅ 如果激活成功，命令行前面会显示 (venv) 标记:
# (venv) C:\project\CS5296\project3\autoscaling-strategy-compare>

# 4️⃣ (可选) 验证 Python 版本
python --version
# 应该显示 3.8+

# 5️⃣ (可选) 验证依赖已安装
pip list | findstr boto3
# 应该显示 boto3 的版本

# 6️⃣ 现在可以运行实验了！
python experiments/01_verify_infrastructure.py

# 7️⃣ 运行完成后，如果想退出 venv (可选)
deactivate
```

---

## 🎯 简化版：三步快速开始

如果你只想快速开始，就这样做：

### 步骤 1: 打开 CMD
```
Win + R → 输入 cmd → 回车
```

### 步骤 2: 复制这三行命令，一行一行在 CMD 中运行
```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
venv\Scripts\activate.bat
python experiments/01_verify_infrastructure.py
```

### 步骤 3: 验证输出
应该看到类似这样的 JSON 输出:
```json
{
  "timestamp": "2026-04-17T17:30:45Z",
  "alb_health": {
    "status": "healthy",
    "dns": "experiment-alb-1466294824.us-east-1.elb.amazonaws.com"
  },
  ...
}
```

如果看到这个，说明环境正确配置了！然后继续运行其他三个脚本。

---

## ⚠️ 常见问题

### Q: "激活虚拟环境后看不到 (venv) 标记？"
**A**: 这很正常。关键是没有错误消息就表示激活成功。

### Q: "ModuleNotFoundError: No module named 'boto3'"？
**A**: 说明虚拟环境没有激活。
```bash
# 确保执行了这条:
venv\Scripts\activate.bat

# 然后重新运行脚本
python experiments/01_verify_infrastructure.py
```

### Q: "python: command not found (or 'python' is not recognized)"？
**A**: Python 没有添加到 PATH。两种解决方案：
```bash
# 方案1: 使用完整路径
venv\Scripts\python.exe experiments/01_verify_infrastructure.py

# 方案2: 检查是否安装了 Python
python --version
```

### Q: "venv 目录不存在？"
**A**: 需要创建虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Q: "curl: command not found"？
**A**: 这是 PowerShell 的问题。解决方案：
```powershell
# 使用 PowerShell 的 Invoke-WebRequest 替代:
Invoke-WebRequest -Uri "http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health"

# 或者用 Python:
python -c "import requests; print(requests.get('http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health').status_code)"
```

---

## ✅ 最终清单 - 开始实验前

在运行实验前，检查这些：

- [ ] 打开了 CMD (或 PowerShell)
- [ ] 进入了正确的目录: `C:\project\CS5296\project3\autoscaling-strategy-compare`
- [ ] 激活了虚拟环境 (看到 `(venv)` 前缀或没有错误)
- [ ] Python 版本 ≥ 3.8: `python --version`
- [ ] 依赖已安装: `pip list` 看到 boto3, requests 等
- [ ] AWS 凭证已配置: `aws sts get-caller-identity` 返回你的账户
- [ ] ALB 可访问: `curl http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health` 或 PowerShell 版本

---

## 📖 参考顺序

```
开始 ↓
  ↓
这个文件 (现在读的) ← 学会怎么激活 venv、用什么 shell
  ↓
PHASE4_5_QUICK_START.md ← 了解实验目标
  ↓
运行 4 个命令 (见下面)
  ↓
遇到问题时 → 查阅 PHASE4_5_EXECUTION_GUIDE.md 的 Troubleshooting 部分
```

---

## 🚀 实验命令 (完整)

```bash
# 确保在 venv 中 (已激活)
# 确保在项目目录: C:\project\CS5296\project3\autoscaling-strategy-compare

# 命令 1: 验证基础设施 (5 分钟)
python experiments/01_verify_infrastructure.py

# 如果上一条成功，继续:

# 命令 2: CPU 策略实验 (30 分钟)
python experiments/02_run_cpu_experiment.py

# 命令 3: 请求率策略实验 (30 分钟)
python experiments/03_run_request_rate_experiment.py

# 命令 4: 生成报告 (10 分钟)
python experiments/04_aggregate_results.py

# 完成！检查输出:
dir experiments\results
```

---

## 总结

| 问题 | 答案 |
|------|------|
| **参考哪个文档？** | 1️⃣ 这个文件 2️⃣ QUICK_START 3️⃣ EXECUTION_GUIDE (有问题时) |
| **CMD 还是 PowerShell？** | ✅ CMD 推荐 (简单) / ✅ PowerShell 也可以 |
| **需要 venv？** | ✅ **是的，必须需要** 先激活 venv 再运行脚本 |

**准备好了？** → 打开 CMD，复制粘贴命令，让它跑 75 分钟，生成真实数据！

---

**最后一个建议**: 在运行命令 2、3 时，**保持 CMD 窗口打开**。30 分钟的实验过程中不要关闭。脚本会每隔几秒输出一行进度。
