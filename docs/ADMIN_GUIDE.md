# 👨‍💼 项目管理员指南

**对象**: 小组项目负责人 / 项目协调员

---

## 📌 你的职责

### 1️⃣ **项目初始化** (Week 1)
- [ ] 创建GitHub仓库（Public）
- [ ] 添加团队成员为协作者
- [ ] 设置基本的分支策略
- [ ] 创建初始文件结构

### 2️⃣ **团队协调** (整个项目)
- [ ] 每周召开同步会议（15分钟）
- [ ] 解决成员之间的冲突
- [ ] 跟踪进度和里程碑
- [ ] 确保没有人掉队

### 3️⃣ **质量控制** (整个项目)
- [ ] 审查所有Pull Request
- [ ] 检查代码质量和风格
- [ ] 验证测试通过
- [ ] 检查安全问题

### 4️⃣ **最终交付** (Week 10)
- [ ] 检查所有文件完整
- [ ] 验证格式符合要求
- [ ] 准备最终提交
- [ ] 确保资源清理

---

## 🛠️ 快速设置指南

### GitHub仓库初始化

```bash
# 1. 创建GitHub仓库 (Web界面)
# - 名称: autoscaling-project
# - 描述: Comparative Analysis of Autoscaling Strategies
# - Public
# - Initialize with README (可选)

# 2. 克隆到本地
git clone https://github.com/<your-org>/autoscaling-project.git
cd autoscaling-project

# 3. 创建初始结构
mkdir -p scripts infrastructure application load-testing data-collection results report config docs

# 4. 添加.gitignore
cat > .gitignore << 'EOF'
# 环境变量
.env
*.pem
*.key

# AWS输出
infrastructure/*-config.json
infrastructure/*-config.sh

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# 结果
results/*
!results/.gitkeep
logs/*
!logs/.gitkeep

# OS
.DS_Store
Thumbs.db
EOF

# 5. 添加README.md（基础版）
cat > README.md << 'EOF'
# Autoscaling Comparison Project

## 快速开始

```bash
python scripts/check_environment.py
python scripts/init_project.py
python scripts/deploy_all.py
```

## 项目信息

- **项目**: Comparative Analysis of Autoscaling Strategies
- **成员**: [列出成员]
- **截止日期**: 2026年4月24日

## 文档

- [执行计划](PROJECT_EXECUTION_PLAN.md)
- [跨平台指南](CROSSPLATFORM_GUIDE.md)
- [验收标准](ACCEPTANCE_CRITERIA.md)
- [快速参考](QUICK_REFERENCE.md)

EOF

# 6. 初始提交
git add .
git commit -m "Initial project setup"
git push -u origin main
```

### 添加团队成员到GitHub

```bash
# 通过GitHub Web界面:
# Settings -> Collaborators -> Add people
# 邀请所有成员
```

---

## 👥 团队管理

### 成员分工表

```markdown
| 成员 | 角色 | 主要任务 | 周期 |
|-----|------|--------|-----|
| WU Wanpeng | 项目管理员 | 整体协调 | 全程 |
| CHEN Sijie | 技术主管 | 代码审查 | 全程 |
| [Member 3] | 工程师 | 实现 | 全程 |
```

### 每周同步会议议程

**时长**: 15分钟
**频率**: 每周一次

```markdown
## 议程

1. **进度汇报** (5分钟)
   - 上周完成了什么？
   - 是否按计划进行？
   - 有什么阻碍吗？

2. **本周计划** (5分钟)
   - 本周目标是什么？
   - 谁负责什么？
   - 预计需要多长时间？

3. **问题解决** (5分钟)
   - 有什么需要讨论的吗？
   - 是否需要帮助？
   - 下周是否有重要截止日期？

## 记录

- 日期: YYYY-MM-DD
- 参与者: 
- 完成: 
- 下周计划: 
```

---

## 🔍 代码审查检查清单

当成员提交Pull Request时，检查:

### 环境和配置
- [ ] 文件结构符合要求
- [ ] 没有敏感信息(.env, *.pem)
- [ ] .gitignore正确配置
- [ ] requirements.txt已更新

### 代码质量
- [ ] Python脚本有注释
- [ ] 遵循PEP 8风格指南
- [ ] 变量名清晰易读
- [ ] 没有硬编码的路径

### 功能性
- [ ] 代码逻辑清晰
- [ ] 错误处理完整
- [ ] 本地测试通过
- [ ] 日志记录充分

### AWS相关
- [ ] 使用了正确的AWS服务
- [ ] IAM权限最小化
- [ ] 成本优化考虑
- [ ] 安全最佳实践

### 文档
- [ ] README已更新
- [ ] 函数有docstring
- [ ] 有使用示例
- [ ] 记录了任何新依赖

---

## 📊 进度跟踪

### Gantt图模板

```
Week 1-2:  [███████] 环境+基础设施
           ├─ 检查环境 [██████]
           ├─ 初始化 [████]
           └─ 部署 [███████]

Week 3:    [█████   ] 应用开发
           ├─ Flask [████]
           ├─ 测试 [█]
           └─ Docker []

Week 4:    [        ] 验证 (待开始)

Week 5-6:  [        ] 实验 (待开始)

Week 7:    [        ] 分析 (待开始)

Week 8-9:  [        ] 报告+视频 (待开始)

Week 10:   [        ] 提交 (待开始)
```

### 关键里程碑

```markdown
[ ] Feb 6: 项目提案截止
[ ] Feb 20: 基础设施部署完成
[ ] Mar 6: 应用部署完成
[ ] Mar 20: Scenario A 实验完成
[ ] Apr 3: Scenario B 实验完成
[ ] Apr 10: 报告初稿完成
[ ] Apr 17: 演示视频完成
[ ] Apr 24: 最终提交截止
```

---

## 🎯 风险管理

### 常见风险

| 风险 | 影响 | 应对方案 |
|-----|-----|--------|
| 团队成员缺席 | 进度延误 | 建立备份计划，平衡工作量 |
| AWS成本超支 | 预算溢出 | 及时清理资源，监控费用 |
| 技术问题卡住 | 项目阻塞 | 提前学习，建立技术支持 |
| 数据收集失败 | 结果无效 | 多次实验，保存中间结果 |
| 报告质量不足 | 分数低 | 提前审查，多次修改 |

### 应急计划

**如果无法按时完成:**

```markdown
1. 立即通知教授
2. 确定延迟的原因
3. 制定补救方案
4. 更新交付内容范围（如果允许）
5. 获得新的截止日期

优先级:
1. 功能性实验（不能删减）
2. 完整的数据（不能删减）
3. 美化报告和视频（可以简化）
```

---

## 📋 最终检查清单

### 提交前 (Week 10)

#### 代码检查
- [ ] 所有Python脚本都运行过
- [ ] 没有调试代码或TODO注释
- [ ] 所有依赖都在requirements.txt
- [ ] .gitignore正确配置

#### 文档检查
- [ ] README.md完整
- [ ] PROJECT_EXECUTION_PLAN.md完整
- [ ] ACCEPTANCE_CRITERIA.md完整
- [ ] CROSSPLATFORM_GUIDE.md完整
- [ ] 所有脚本都有注释

#### 数据检查
- [ ] 所有实验数据完整
- [ ] 结果符合预期
- [ ] 分析图表生成
- [ ] 数据文件在git中

#### 报告检查
- [ ] 文件名: `GroupID_report.pdf`
- [ ] 页数: ≤9页
- [ ] 格式: 12pt Times New Roman
- [ ] 包含所有必需章节
- [ ] 引用和图表都有

#### 视频检查
- [ ] 分辨率: ≥640x480
- [ ] 时长: ≤10分钟
- [ ] 语言: 英文
- [ ] 上传: YouTube/B站（公开）
- [ ] 包含所有必需内容

#### 提交检查
- [ ] 报告PDF: Canvas提交
- [ ] 视频链接: Canvas提交
- [ ] GitHub仓库: Public + 完整历史
- [ ] 所有资源已清理

---

## 🚀 模板和工具

### 会议记录模板

```markdown
# 会议记录 - Week X

**日期**: YYYY-MM-DD
**参与者**: [列表]
**时长**: 15分钟

## 进度汇报

### 完成的工作
- [任务1]: 完成
- [任务2]: 完成
- [任务3]: 50% 进度

### 遇到的问题
- [问题1]: [解决方案]
- [问题2]: [需要帮助的地方]

## 本周计划

- [任务1] (Member A) - 预计3小时
- [任务2] (Member B) - 预计2小时
- [任务3] (Member C) - 预计5小时

## 下周检查点

- [ ] 基础设施部署完成
- [ ] 所有成员通过环境检查
- [ ] 第一批数据收集

## 行动项

| 任务 | 负责人 | 截止日期 |
|-----|-------|--------|
| 解决VPC问题 | Member A | 下周二 |
| 准备AMI | Member B | 下周三 |
| 编写测试脚本 | Member C | 下周四 |
```

### 困难问题升级流程

```
Level 1: 团队内部讨论 (15分钟)
  ↓
Level 2: 查阅文档和教程 (30分钟)
  ↓
Level 3: GitHub Issues讨论 (1小时)
  ↓
Level 4: 请求教授帮助 (联系教授)
```

---

## 📞 沟通模板

### 当有成员掉队时

```markdown
Hi [成员名字],

我注意到你这周[具体任务]的进度可能慢于预期。
有什么我可以帮忙的吗？

几个选项:
1. 我们一起调试这个问题
2. 我可以帮助分解任务
3. 我们可以在团队会议上讨论

让我知道你的想法。

Best regards,
[你的名字]
```

### 当有技术问题时

```markdown
问题: [清晰描述问题]
环境: [操作系统/Python版本/AWS区域]
错误信息: [完整的错误堆栈]
已尝试: [列出已尝试的解决方案]
期望结果: [应该发生什么]

谢谢帮助!
```

---

## 🎓 额外资源

### 给团队的学习资源列表

```markdown
## 必读
- [AWS EC2官方文档](https://docs.aws.amazon.com/ec2/)
- [Auto Scaling最佳实践](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-best-practices.html)
- [Git工作流](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)

## 推荐
- [Python最佳实践](https://pep8.org/)
- [Locust性能测试](https://locust.io/)
- [boto3教程](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

## 可选
- [AWS架构设计](https://aws.amazon.com/architecture/)
- [DevOps最佳实践](https://www.aws.training/)
- [学术论文写作](https://www.ieee-dataport.org/sites/default/files/analysis/27/IEEE%20Citation%20Guidelines.pdf)
```

---

## ✅ 成功标志

当以下所有条件都满足时，你的项目就成功了:

✅ **所有成员**都:
- 能在自己的机器上运行所有脚本
- 理解项目的整个流程
- 对最终结果感到满意

✅ **GitHub仓库**有:
- 所有成员的提交
- 清晰的提交历史
- 完整的文档

✅ **最终交付物**包括:
- 9页优质PDF报告
- ≤10分钟的清晰演示视频
- 完整的Artifact Appendix

✅ **AWS账户**:
- 所有临时资源已清理
- 费用在预算内
- 没有遗留的成本

---

**记住**: 作为项目管理员，你的工作是确保团队顺畅合作，而不是做所有的工作。委派任务，支持团队，确保进度。

祝项目顺利！🎉

