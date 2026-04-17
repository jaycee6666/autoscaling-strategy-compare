# 项目验收标准

**项目名称**: Comparative Analysis of Autoscaling Strategies: Resource-Based CPU Utilization vs. Workload-Based Request Rate

**项目类型**: Research

**截止日期**: 2026年4月24日 23:59 HKT

---

## 1. 最终报告验收标准 (15分)

### 1.1 内容标准 (13分)

#### 必须包含的章节:

- [ ] **标题和作者信息** - 包含Group ID、所有成员名字和学生ID
- [ ] **摘要** (Abstract) 
  - [ ] 不超过250字
  - [ ] 清晰总结项目目标、方法和主要发现
  
- [ ] **引言** (Introduction)
  - [ ] 介绍Cloud Elasticity和Autoscaling的背景
  - [ ] 陈述问题：为什么CPU-based scaling不够好
  - [ ] 阐述研究假设：Request Count能更快地触发扩展
  - [ ] 阐明主要发现和贡献
  
- [ ] **相关工作/背景** (Related Work/Background)
  - [ ] 介绍现有的autoscaling方案
  - [ ] 说明本项目的创新点（与现有方案的区别）
  
- [ ] **方法论** (Methodology)
  - [ ] 详细描述实验设计：
    - [ ] 基础设施架构（EC2、ALB、ASG配置）
    - [ ] Scenario A: CPU-based scaling配置详情
    - [ ] Scenario B: Request-based scaling配置详情
    - [ ] 负载生成工具和参数
    - [ ] 监测方法（CloudWatch指标）
  
- [ ] **实验结果与分析** (Experimental Results & Analysis)
  - [ ] 呈现性能对比数据：
    - [ ] P95响应延迟对比（图表）
    - [ ] Scale-out延迟对比（图表）
    - [ ] 错误率对比（图表）
  - [ ] 各个指标的详细分析和解释
  - [ ] 发现与讨论：哪个策略更优以及为什么
  
- [ ] **结论** (Conclusion)
  - [ ] 3-4句总结项目发现
  - [ ] 说明对实际云应用的指导意义
  - [ ] 未来改进方向（可选）
  
- [ ] **参考文献** (References)
  - [ ] IEEE格式引用
  - [ ] 至少包含AWS官方文档、学术论文或技术博客

#### 质量标准:

- [ ] 深度：实验设计合理且全面，数据分析充分
- [ ] 广度：涵盖多个负载模式（如突发流量、渐进上升）
- [ ] 创新性：清晰阐述相比CPU-based的改进和新见解
- [ ] 工作量：项目复杂度适中且投入充分

### 1.2 写作标准 (2分)

- [ ] 英文表达清晰准确，无重大语法错误
- [ ] 逻辑结构清晰：各部分之间逻辑连贯
- [ ] 专业性：使用正确的技术术语
- [ ] 格式规范：
  - [ ] A4或US Letter纸张
  - [ ] PDF格式
  - [ ] 12pt Times New Roman
  - [ ] 单栏单倍行距
  - [ ] 文件名：`GroupID_report.pdf`

### 1.3 页数限制

- [ ] **总页数不超过9页**（包含参考文献，不包括产品附录）

---

## 2. 软件产品验收标准 (4分)

### 2.1 产品构成

#### 必须包含的组件:

- [ ] **Python Flask应用**
  - [ ] 实现简单的HTTP端点（如`GET /api/health`, `POST /api/request`）
  - [ ] 能够处理并模拟不同的处理延迟
  - [ ] 代码结构清晰，有基本注释
  
- [ ] **AWS基础设施代码**
  - [ ] Terraform或CloudFormation脚本自动化部署
  - [ ] 包含EC2配置、ALB配置、ASG配置
  - [ ] Scenario A: CPU-based scaling policy
  - [ ] Scenario B: Request-based scaling policy
  
- [ ] **负载生成脚本**
  - [ ] 使用Locust或Apache JMeter
  - [ ] 能生成至少3种负载模式：
    - [ ] 突发流量（spike）
    - [ ] 渐进上升（ramp-up）
    - [ ] 持续高负载（sustained）
  
- [ ] **数据收集脚本**
  - [ ] 从CloudWatch获取指标
  - [ ] 计算P95延迟、Scale-out延迟、错误率
  - [ ] 输出结构化结果（CSV或JSON）

### 2.2 GitHub仓库要求

- [ ] **公开仓库**（必须Public，不能Private）
- [ ] **目录结构清晰**
  ```
  project-root/
  ├── README.md                 # 项目概述和快速开始
  ├── infrastructure/           # Terraform/CloudFormation脚本
  │   ├── main.tf              # 主基础设施配置
  │   ├── variables.tf
  │   └── terraform.tfvars
  ├── application/             # Flask应用代码
  │   ├── app.py
  │   ├── requirements.txt
  │   └── Dockerfile
  ├── load-testing/            # 负载测试脚本
  │   ├── locustfile.py
  │   └── load-scenarios.yaml
  ├── data-collection/         # 数据收集脚本
  │   ├── collect_metrics.py
  │   └── analyze_results.py
  ├── results/                 # 实验结果数据
  │   ├── scenario_a_results.csv
  │   ├── scenario_b_results.csv
  │   └── comparison.json
  ├── docker-compose.yml       # 本地测试环境（可选）
  └── Artifact_Appendix.md     # 产品附录
  ```

- [ ] **完整的提交历史**
  - [ ] 多个成员的提交跨越长时间段
  - [ ] 不能是最后一刻的一次大提交
  - [ ] 每个阶段有有意义的提交信息

### 2.3 产品附录 (Artifact Appendix)

**必须包含以下内容（不计入报告页数）：**

- [ ] **系统依赖**
  - [ ] Python版本、Flask版本
  - [ ] AWS账户要求、IAM权限
  - [ ] Terraform/CloudFormation版本
  - [ ] Locust版本
  
- [ ] **准备和安装步骤**
  - [ ] 环境变量配置（AWS credentials等）
  - [ ] 如何部署基础设施：
    ```bash
    cd infrastructure
    terraform init
    terraform apply
    ```
  - [ ] 如何部署应用：Docker或直接运行步骤
  
- [ ] **运行实验的详细步骤**
  - [ ] 启动Scenario A的步骤
  - [ ] 启动Scenario B的步骤
  - [ ] 运行负载测试的命令
  - [ ] 预计运行时间
  
- [ ] **预期输出**
  - [ ] 运行成功后会生成的文件
  - [ ] 预期的CloudWatch指标值范围
  - [ ] 如何验证结果
  
- [ ] **费用估算**
  - [ ] AWS资源的预计成本
  - [ ] 如何清理资源以停止费用

- [ ] **可重复性验证**
  - [ ] 任何人按照步骤能否复现结果
  - [ ] 预期结果的定量定性描述

### 2.4 产品质量标准 (0.5 + 0.5 + 2 + 1 = 4分)

#### 清晰完整的文档 (0.5分)
- [ ] Artifact Appendix清晰易懂
- [ ] README详细，包含项目概述和快速开始
- [ ] 代码注释充分

#### 可移植和自动化 (0.5分)
- [ ] 使用Docker容器或VM镜像
- [ ] 提供自动化脚本（bash或Python）一键部署
- [ ] 代码能在不同环境中运行

#### 一致性、完整性、可运行性 (2分)
- [ ] 代码与报告中描述一致
- [ ] 所有依赖和配置都包含
- [ ] 能够成功运行和生成结果
- [ ] 结果与报告中的数据一致

#### 提交历史 (1分)
- [ ] 完整的git历史，包含所有成员的多次提交
- [ ] 提交跨越项目执行期间
- [ ] 提交信息有意义

---

## 3. 演示视频验收标准 (4分)

### 3.1 必须包含的内容

- [ ] **项目简介** (30-60秒)
  - [ ] 清晰阐述解决的问题
  - [ ] 为什么这个问题重要
  
- [ ] **解决方案说明** (1-2分钟)
  - [ ] Scenario A和Scenario B的区别
  - [ ] 技术架构概览
  
- [ ] **现场演示** (3-5分钟)
  - [ ] 运行负载测试的过程
  - [ ] 展示CloudWatch监控面板
  - [ ] 展示性能数据对比
  
- [ ] **关键发现** (1-2分钟)
  - [ ] 主要结果和对比
  - [ ] 1-2个重要发现
  - [ ] 实际意义

### 3.2 演示质量标准 (Content: 1.5分)

- [ ] 包含所有必需组件
- [ ] 提供清晰的运行说明
- [ ] 实际可运行的解决方案
- [ ] 容易让观众理解和复现

### 3.3 视频质量标准 (Quality: 2.5分)

- [ ] 分辨率不低于640×480
- [ ] 总时长不超过10分钟
- [ ] 音频清晰，英文讲解
- [ ] 关键点用字幕或文字说明
- [ ] 视频编辑专业（过渡平滑、字幕清晰）
- [ ] 屏幕录制清晰易读

### 3.4 提交要求

- [ ] 上传到YouTube或B站（公开可见）
- [ ] 通过Canvas提交链接
- [ ] 链接格式：`https://www.youtube.com/watch?v=xxx` 或 `https://www.bilibili.com/video/BVxxx`

---

## 4. 整体项目检查清单

### 文件和提交

- [ ] `GroupID_report.pdf` - 9页以内，12pt Times New Roman
- [ ] GitHub公开仓库 - 包含完整提交历史
- [ ] `Artifact_Appendix.md` - 作为报告附录或单独文档
- [ ] 演示视频链接 - YouTube或B站

### 技术验收

- [ ] Infrastructure代码可成功运行
- [ ] 应用能在所有实例上成功部署
- [ ] 负载测试能生成预期的流量模式
- [ ] 数据收集脚本能正确获取CloudWatch指标
- [ ] 实验结果数据完整且可解释

### 研究验收

- [ ] 有清晰的对照组设计（CPU vs Request Count）
- [ ] 实验覆盖多个负载模式
- [ ] 数据分析深入，结论有根据
- [ ] 发现具有实际指导意义

### 文档验收

- [ ] 报告逻辑清晰、结构完整
- [ ] 英文表达正确
- [ ] README和Artifact Appendix清晰完整
- [ ] 代码有注释和说明

---

## 5. 常见扣分点（要避免）

- ❌ 报告超过9页
- ❌ 使用ChatGPT/LLM生成报告内容
- ❌ GitHub仓库为Private
- ❌ GitHub只有最后一次提交
- ❌ 代码无法运行或缺少依赖信息
- ❌ 演示视频超过10分钟
- ❌ 演示视频上传到Baidu Netdisk等其他网站
- ❌ 没有清晰的Artifact Appendix
- ❌ 实验结果数据不完整
- ❌ 没有对CPU vs Request Count的定量对比

---

## 6. 理想验收结果

✅ **报告** (15分)
- 完整的研究报告，5-7种负载模式下的实验数据
- 深入分析为什么Request-based更优
- 清晰阐述实际应用价值

✅ **产品** (4分)
- 完全自动化的基础设施部署（Terraform）
- Docker化的应用和完整的数据收集流程
- 多个成员跨时间的有意义提交

✅ **演示** (4分)
- 5-8分钟的清晰演示
- 实时展示两个Scenario的性能差异
- 专业的视频编辑和字幕

---

**总分**: 23分（满分）

