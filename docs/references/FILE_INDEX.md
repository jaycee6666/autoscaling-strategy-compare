# 项目文件索引

## 📁 目录结构

```
autoscaling-strategy-compare/
├── .github/
│   └── CROSSPLATFORM_GUIDE.md           # Windows/Mac/Linux 设置指南
├── docs/                              # 文档 (1500+ 行)
│   ├── guides/
│   │   ├── PHASE4_6_EXECUTION_GUIDE.md # ⭐ Phase 4-6 执行指南
│   │   ├── PHASE1_DEPLOYMENT_GUIDE.md  # Phase 1 部署
│   │   ├── PHASE3_DEPLOYMENT_GUIDE.md  # Phase 3 部署
│   │   └── ...
│   ├── plans/
│   │   ├── PROJECT_EXECUTION_PLAN.md # 完整 10 周执行计划
│   │   └── ...
│   ├── references/
│   │   ├── ACCEPTANCE_CRITERIA.md    # 评分要求
│   │   ├── FILE_INDEX.md             # 本文件
│   │   └── ...
│   └── README.md
├── scripts/                           # Python 自动化 (500+ 行)
│   ├── check_environment.py          # ⭐ 环境验证
│   ├── init_project.py               # ⭐ 项目初始化
│   ├── config_manager.py             # 配置管理
│   ├── aws_utils.py                  # AWS CLI 包装器
│   ├── setup_network.py              # [待创建] VPC 设置
│   ├── setup_security_groups.py      # [待创建] 安全组
│   ├── setup_iam_role.py             # [待创建] IAM 设置
│   ├── setup_instances.py            # [待创建] EC2 设置
│   ├── setup_asg.py                  # [待创建] ASG 设置
│   ├── deploy_all.py                 # [待创建] 一键部署
│   └── cleanup_infrastructure.py      # [待创建] 清理
│
├── config/                            # 配置
│   ├── .env.template                 # 环境模板
│   ├── .env                          # [由 init_project.py 创建]
│   ├── config.yaml                   # [由 init_project.py 创建]
│   └── check_environment_results.json # [由 check_environment.py 创建]
│
├── data/                              # 数据收集
│   ├── experiments/                  # 实验结果
│   ├── metrics/                      # 性能指标
│   └── analysis/                     # 分析输出
│
├── logs/                              # 应用日志
│   └── [运行时生成]
│
├── README.md                          # ⭐ 项目概述
├── setup.py                           # 快速设置脚本
├── requirements.txt                   # Python 依赖
├── .gitignore                         # Git 忽略规则
└── FILE_INDEX.md                      # 本文件
```

## 📄 文件描述

### 文档 (docs/)

| 文件 | 大小 | 用途 | 适合 |
|------|------|---------|----------|
| **guides/PHASE4_6_EXECUTION_GUIDE.md** | 22KB | 完整 Phase 4-6 执行指南 | 所有人 |
| **plans/PROJECT_EXECUTION_PLAN.md** | 56KB | 完整 10 周计划及所有阶段 | 技术主管、实施者 |
| **guides/PHASE4_6_EXECUTION_GUIDE.md** | 22KB | Phase 4-6 执行参考 | 日常工作 |
| **.github/CROSSPLATFORM_GUIDE.md** | 11KB | Windows/Mac/Linux 兼容指南 | 故障排查 |
| **references/ACCEPTANCE_CRITERIA.md** | 9.6KB | 课程评分要求 | 质量保证 |
| **references/ACCEPTANCE_CRITERIA.md** | 9.6KB | 评分清单 | 质量保证/评分 |
| **references/ACCEPTANCE_CRITERIA.md** | 9.6KB | 项目指南 | 概述读者 |
| **README.md** | 6KB | 项目概述 | 快速上下文 |

**总文档**: 110+ KB, 5500+ 行

### 脚本 (scripts/)

#### ✅ 准备好使用 (Phase 0)

| 脚本 | 行数 | 用途 |
|--------|-------|---------|
| **check_environment.py** | 280 | 验证 Python、AWS CLI、凭证、包、权限 |
| **init_project.py** | 140 | 创建配置文件、目录、初始化项目 |
| **config_manager.py** | 320 | 通过 YAML、ENV、JSON 的集中配置 |
| **aws_utils.py** | 480 | AWS CLI 包装器，带错误处理、VPC、EC2、ASG、CloudWatch |

**总 Phase 0**: 1220 行

#### 🔄 待创建 (Phases 1-7)

| 脚本 | 用途 | Phase |
|--------|---------|-------|
| setup_network.py | VPC、子网、互联网网关 | 1 |
| setup_security_groups.py | 安全组配置 | 2 |
| setup_iam_role.py | IAM 角色和策略 | 3 |
| setup_instances.py | EC2 实例模板 | 4 |
| setup_alb.py | 负载均衡器配置 | 5 |
| setup_asg.py | 自动扩展组 | 6 |
| deploy_all.py | 一键部署 | 6 |
| verify_infrastructure.py | 健康检查和验证 | 7 |
| cleanup_infrastructure.py | 资源清理 | 8 |

### 配置 (config/)

| 文件 | 创建者 | 用途 |
|------|-----------|---------|
| .env.template | 手动 | .env 值的模板 |
| .env | init_project.py | 实际配置 (git 忽略) |
| config.yaml | init_project.py | 项目 YAML 配置 |
| check_environment_results.json | check_environment.py | 环境检查结果 |

### 数据目录 (data/)

| 目录 | 用途 |
|-----------|---------|
| experiments/ | 实验结果文件 |
| metrics/ | CloudWatch 指标导出 |
| analysis/ | 数据分析输出 |

### 根目录文件

| 文件 | 用途 |
|------|---------|
| **README.md** | 项目概述和快速开始 |
| **setup.py** | 自动设置脚本 (运行 Phase 0 脚本) |
| **requirements.txt** | Python 包依赖 |
| **.gitignore** | Git 忽略规则 (排除 .env、日志、数据) |

## 🚀 执行流程

### 首次运行 (完整设置)

```
1. setup.py                 # 首先运行我! 自动化一切
   ↓
2. check_environment.py     # 验证环境
   ↓
3. init_project.py          # 初始化项目
   ↓
4. [手动] 编辑 config/.env
   ↓
5. check_environment.py     # 验证配置
   ↓
6. aws_utils.py             # 测试 AWS 连接
```

### 日常开发

```
1. 阅读: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
   ↓
2. 运行 scripts/ 中的适当脚本
   ↓
3. 参考: docs/plans/PROJECT_EXECUTION_PLAN.md 获取上下文
   ↓
4. 故障排查: 如需要，参考 .github/CROSSPLATFORM_GUIDE.md
```

## 📊 文件统计

### 文档
- 总文件: 8
- 总大小: ~110 KB
- 总行数: 5500+
- 准备好阅读: ✅ 是 (全部完成)

### 脚本
- Phase 0 (准备好): 4 个脚本, 1220 行, ~45 KB
- Phase 1-7 (待创建): 9 个脚本, ~2000+ 行估计

### 配置
- 模板: 1 (.env.template)
- 生成: 3 (.env, config.yaml, check_environment_results.json)

## 🎯 使用路径

### 新团队成员 (第一天)
```
1. 阅读: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
2. 运行: python scripts/setup.py
3. 阅读: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
```

### 开发人员 (日常工作)
```
1. 检查: docs/guides/PHASE4_6_EXECUTION_GUIDE.md
2. 遵循: docs/plans/PROJECT_EXECUTION_PLAN.md
3. 故障排查: .github/CROSSPLATFORM_GUIDE.md
```

### 项目经理
```
1. 阅读: docs/references/ACCEPTANCE_CRITERIA.md
2. 监控: docs/plans/PROJECT_EXECUTION_PLAN.md 中的进度
3. 使用: ACCEPTANCE_CRITERIA.md 进行验证
```

### DevOps/基础设施
```
1. 研究: docs/plans/PROJECT_EXECUTION_PLAN.md (Phase 1-3)
2. 使用: scripts/aws_utils.py 作为参考
3. 创建: Phase 1-7 基础设施脚本
```

## ✅ 实现状态

### 已完成 ✅
- [x] 文档 (8 个指南, 5500+ 行)
- [x] Phase 0 脚本 (检查、初始化、配置、aws)
- [x] 项目结构和组织
- [x] 跨平台兼容性 (Python/YAML/路径)
- [x] 需求和设置自动化

### 准备实现 🔄
- [ ] Phase 1 基础设施脚本 (网络设置)
- [ ] Phase 2-3 基础设施脚本 (安全性、IAM)
- [ ] Phase 4 基础设施脚本 (EC2、ALB)
- [ ] Phase 5-6 基础设施脚本 (ASG、部署)
- [ ] Phase 7 部署验证
- [ ] Phase 8 应用开发 (Flask)
- [ ] Phase 9 实验执行
- [ ] Phase 10 数据分析和报告

## 📚 推荐阅读顺序

1. **首次**: `docs/guides/PHASE4_6_EXECUTION_GUIDE.md` (15 分钟)
2. **设置**: 运行 `python scripts/setup.py` (5 分钟)
3. **概述**: `README.md` (5 分钟)
4. **日常参考**: `docs/guides/PHASE4_6_EXECUTION_GUIDE.md` (持续)
5. **深入了解**: `docs/plans/PROJECT_EXECUTION_PLAN.md` (1 小时)
6. **故障排查**: `.github/CROSSPLATFORM_GUIDE.md` (按需)
7. **团队主管**: `docs/references/ACCEPTANCE_CRITERIA.md` (如适用)

## 🔗 文件依赖

```
setup.py
├── requirements.txt
├── check_environment.py
│   └── [无依赖]
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

## 🎓 学习路径

1. **理解**: 阅读 docs/plans/PROJECT_EXECUTION_PLAN.md (所有 10 个阶段)
2. **设置**: 在您的计算机上运行 setup.py
3. **测试**: 运行 check_environment.py 和 aws_utils.py
4. **实施**: 按照 aws_utils.py 模式创建 Phase 1-7 脚本
5. **部署**: 使用 deploy_all.py 协调基础设施
6. **开发**: 构建 Flask 应用 (Phase 8)
7. **执行**: 运行实验 (Phase 9)
8. **分析**: 收集和分析数据 (Phase 10)

## 🆘 快速故障排查

| 问题 | 文件 |
|-------|--------------|
| 设置失败 | docs/guides/PHASE4_6_EXECUTION_GUIDE.md |
| Python 错误 | .github/CROSSPLATFORM_GUIDE.md |
| AWS CLI 问题 | docs/guides/PHASE4_6_EXECUTION_GUIDE.md |
| 环境验证失败 | check_environment.py 输出 |
| 团队协调 | docs/references/ACCEPTANCE_CRITERIA.md |
| 评分要求 | docs/references/ACCEPTANCE_CRITERIA.md |

---

**版本**: 1.0  
**最后更新**: 2026 年 4 月 17 日  
**总项目文件**: 30+  
**总行数**: 8000+  
**总文档**: 5500+ 行  
**就绪状态**: Phase 0 ✅ | Phase 1-10 🔄
