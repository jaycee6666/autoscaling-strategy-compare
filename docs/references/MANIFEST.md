# 项目清单

**项目名称**: Autoscaling Strategy Comparison  
**团队**: WU Wanpeng, CHEN Sijie  
**截止日期**: 2026年4月24日，23:59 HKT  
**状态**: ✅ Phase 0 完成 - 准备就绪  
**创建日期**: 2026年4月17日  

---

## 📦 包含的内容

### 🎯 入口点（从这里开始）

1. **README.md** - 项目概述和全面设置指南
2. **docs/guides/PHASE4_6_EXECUTION_GUIDE.md** - 详细的 Phase 4-6 执行指南

### 📚 文档（8 个文件，5,600+ 行）

| 文件 | 用途 | 受众 |
|------|---------|----------|
| docs/plans/PROJECT_EXECUTION_PLAN.md | 完整的10周执行计划 | 所有人 |
| docs/references/ACCEPTANCE_CRITERIA.md | 团队协调和管理 | 项目经理 |
| .github/CROSSPLATFORM_GUIDE.md | Windows/Mac/Linux 兼容性 | 故障排查 |
| docs/guides/PHASE4_6_EXECUTION_GUIDE.md | Phase 4-6 执行和分析 | 日常工作 |
| docs/references/ACCEPTANCE_CRITERIA.md | 评分要求清单 | QA/评分 |
| docs/guides/PHASE4_6_EXECUTION_GUIDE.md | 逐步执行指南 | 新成员 |
| docs/references/ACCEPTANCE_CRITERIA.md | 改进前后对比 | 背景/概述 |
| README.md | 详细的优化 | 参考 |

### 💻 Python 脚本（4 个准备就绪，1,220 行）

| 脚本 | 用途 | 行数 | 状态 |
|--------|---------|-------|--------|
| check_environment.py | 验证 Python、AWS、凭证 | 264 | ✅ 准备就绪 |
| init_project.py | 初始化项目结构 | 209 | ✅ 准备就绪 |
| config_manager.py | 集中式配置 | 261 | ✅ 准备就绪 |
| aws_utils.py | AWS CLI 包装器（20+ 个操作） | 487 | ✅ 准备就绪 |

### ⚙️ 配置文件

- `.env.template` - 环境变量模板
- `.gitignore` - Git 忽略规则（保护凭证）
- `requirements.txt` - Python 依赖
- `setup.py` - 自动化设置脚本

### 📁 项目目录

- `config/` - 配置文件（自动创建）
- `data/` - 数据收集和结果
  - `experiments/` - 实验结果
  - `metrics/` - 性能指标
  - `analysis/` - 分析输出
- `scripts/` - Python 自动化脚本
- `docs/` - 所有文档

### 📋 索引和参考文件

- `README.md` - 项目概述和入门指南
- `FILE_INDEX.md` - 完整文件参考
- `PROJECT_STATUS.md` - 完成报告
- `MANIFEST.md` - 此清单

---

## 🚀 快速开始

```bash
# 1. 安装依赖（仅第一次）
pip install -r requirements.txt

# 2. 运行设置（仅第一次）
python scripts/setup.py

# 3. 编辑配置
# 打开: config/.env
# 添加你的 AWS 凭证

# 4. 验证一切正常
python scripts/check_environment.py

# 5. 阅读文档
# 从以下开始: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
```

---

## 📊 项目统计

| 指标 | 数量 |
|--------|-------|
| 总文件数 | 24 |
| Python 脚本 | 4 个（1,220 行） |
| 文档文件 | 12 个（5,600+ 行） |
| 配置模板 | 2 个 |
| 总大小 | 221 KB |
| 总代码/文档行数 | 6,868+ |

---

## 🎯 执行 Phase（10 周）

```
第1周:    ✅ Phase 0 - 设置（已完成）
第2-3周:  🔄 Phase 1-3 - AWS 基础设施
第4-5周:  🔄 Phase 4 - Flask 应用  
第6-7周:  🔄 Phase 5-6 - 实验
第8周:    🔄 Phase 7 - 数据收集
第9周:    🔄 Phase 8 - 报告编写
第10周:   🔄 Phase 9-10 - 演示和提交
```

---

## ✅ 现在可用的功能

### Phase 0 组件 ✅

- ✓ 环境验证脚本
- ✓ 项目初始化脚本
- ✓ 配置管理系统
- ✓ AWS CLI 包装器，包含 20+ 个操作
- ✓ 自动化设置脚本
- ✓ 完整文档

### 经过跨平台验证 ✅

- ✓ Windows（PowerShell、Command Prompt）
- ✓ macOS（Terminal）
- ✓ Linux（Bash、Zsh）
- ✓ 所有路径使用 Python pathlib（自动处理操作系统）
- ✓ 所有命令在所有平台上相同

### 安全性 ✅

- ✓ 凭证从不提交（.env 在 .gitignore 中）
- ✓ 代码中没有硬编码的机密
- ✓ 使用前验证配置
- ✓ 错误信息不暴露敏感数据

---

## 🔄 需要实现的内容

### Phase 1-7 脚本（需要创建 9 个脚本）

```
scripts/
├── setup_network.py           # VPC、子网、互联网网关
├── setup_security_groups.py   # 安全组规则
├── setup_iam_role.py          # IAM 角色和策略
├── setup_instances.py         # EC2 模板和 AMI
├── setup_alb.py               # 应用负载均衡器
├── setup_asg.py               # 自动扩展组
├── deploy_all.py              # 协调部署
├── verify_infrastructure.py   # 健康检查
└── cleanup_infrastructure.py  # 资源清理
```

### Phase 8-10 应用

```
app/
├── flask_app.py               # 主应用
├── load_generator.py          # 负载测试
├── metrics_collector.py       # CloudWatch 集成
└── data_analyzer.py           # 结果分析
```

---

## 📖 推荐阅读顺序

### 第一天

1. **README.md**（5 分钟）- 欢迎和项目概述
2. **README.md** 中的**前置要求和设置**部分（10 分钟）- 设置说明
3. **运行 setup.py**（5 分钟）- 自动化设置
4. **README.md** 中的**运行实验**部分（5 分钟）- 执行方法

### 第一周

1. **docs/plans/PROJECT_EXECUTION_PLAN.md**（60 分钟）- 完整计划
2. **docs/guides/PHASE4_6_EXECUTION_GUIDE.md**（5 分钟）- 命令参考
3. **创建 Phase 1 基础设施脚本** - 使用 aws_utils.py 作为指南

### 按需参考

- **.github/CROSSPLATFORM_GUIDE.md** - 故障排查时
- **docs/references/ACCEPTANCE_CRITERIA.md** - 管理团队时
- **FILE_INDEX.md** - 文件导航
- **docs/references/ACCEPTANCE_CRITERIA.md** - 最终提交前

---

## 🎓 如何使用此项目

### 对于新团队成员

```bash
1. 克隆/下载项目
2. 阅读: README.md 中的"前置要求和设置"部分（10 分钟）
3. 运行: python scripts/setup.py（5 分钟）
4. 编辑: config/.env（2 分钟）
5. 验证: python experiments/01_verify_infrastructure.py（5 分钟）
6. 阅读: README.md 中的"运行实验"部分（5 分钟）
7. 继续: docs/plans/PROJECT_EXECUTION_PLAN.md
```

### 对于开发人员

```bash
1. 每天: 查看 docs/guides/PHASE4_6_EXECUTION_GUIDE.md
2. 遵循: docs/plans/PROJECT_EXECUTION_PLAN.md 各阶段
3. 参考: scripts/aws_utils.py 进行 AWS 操作
4. 遇到问题: .github/CROSSPLATFORM_GUIDE.md
```

### 对于项目负责人

```bash
1. 阅读: docs/references/ACCEPTANCE_CRITERIA.md
2. 跟踪: docs/plans/PROJECT_EXECUTION_PLAN.md 进度
3. 分配: 将 Phase 1-7 脚本分配给团队成员
4. 验证: 提交前查看 docs/references/ACCEPTANCE_CRITERIA.md
```

---

## 🔗 文件依赖关系

```
setup.py
├── requirements.txt
├── check_environment.py
└── init_project.py
    ├── config_manager.py
    │   ├── python-dotenv
    │   └── pyyaml
    └── boto3

aws_utils.py
├── subprocess
├── json
└── logging
```

---

## 🆘 故障排查

### 常见问题

| 问题 | 解决方案 | 文件 |
|-------|----------|------|
| Python 未找到 | 使用 python3 或添加到 PATH | docs/guides/PHASE4_6_EXECUTION_GUIDE.md |
| AWS CLI 未找到 | 安装 AWS CLI v2 | docs/guides/PHASE4_6_EXECUTION_GUIDE.md |
| AWS 凭证错误 | 设置环境变量 | .github/CROSSPLATFORM_GUIDE.md |
| 导入错误 | pip install -r requirements.txt | docs/guides/PHASE4_6_EXECUTION_GUIDE.md |
| 平台特定错误 | 查看 .github/CROSSPLATFORM_GUIDE.md | docs/ |

---

## ✨ 关键功能

### 跨平台 ✅

- **相同的命令** Windows、macOS、Linux
- **Windows 不需要 WSL**
- **自动路径处理** 通过 Python pathlib
- **所有脚本在任何操作系统上都可执行**

### 自动化设置 ✅

- **一键设置**: python scripts/setup.py
- **自动验证**: 环境检查
- **自动初始化**: 项目结构
- **模板准备就绪**: 只需填入凭证

### 默认安全 ✅

- **代码库中无凭证** (.gitignore)
- **集中式配置** 用于多人工作
- **错误信息安全** （无数据泄露）
- **内置验证** （检查自动运行）

### 文档完善 ✅

- **5,600+ 行** 清晰的文档
- **8 个专门指南** 适应不同需求
- **分步说明** 随处可见
- **快速参考** 用于日常工作

---

## 📞 支持资源

### 项目文档

- **入门指南**: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
- **完整计划**: docs/plans/PROJECT_EXECUTION_PLAN.md
- **快速参考**: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
- **故障排查**: .github/CROSSPLATFORM_GUIDE.md

### 外部
