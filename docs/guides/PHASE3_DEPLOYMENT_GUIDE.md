# Phase 3 部署指南

本指南涵盖 Phase 3 的任务 2-4：

1. 将 Flask 测试应用部署到现有 EC2/ASG 基础设施
2. 验证负载生成器连接到 ALB
3. 记录部署操作和故障排查工作流程

以下所有步骤使用 **Python + boto3**，无需 AWS CLI 子流程。

---

## 1) 前置要求

- Python 3.9+ 可用
- 虚拟环境已准备在 `venv/`
- boto3/requests/flask 已安装在 venv 中
- Phase 3 任务 1 基础设施已部署
- 工作目录:

```text
C:\project\CS5296\project3\autoscaling-strategy-compare
```

---

## 2) 关键输入

需要这些配置文件：

- `infrastructure/alb-config.json`
- `infrastructure/asg-config.json`
- `infrastructure/launch-templates-config.json`
- `infrastructure/network-config.json`
- `apps/test_app/app.py`

主要 ALB 端点:

- `experiment-alb-1466294824.us-east-1.elb.amazonaws.com`

---

## 3) 通过 ASG 启动模板将 Flask 应用部署到 EC2

运行:

```bash
venv/Scripts/python.exe deployment/deploy_app.py --region us-east-1
```

此脚本执行的操作：

1. 读取基础设施配置 + Flask 应用源代码
2. 构建安装依赖并启动 `test-app.service` 的用户数据
3. 为 CPU/请求 ASG 创建新的启动模板版本
4. 更新 ASG 为新的启动模板版本
5. 触发实例刷新并等待健康的服务中实例
6. 等待活跃监听器目标组的目标健康
7. 重复探测 `http://{ALB_DNS}/health` 并写入 JSON 报告

输出工件:

- `deployment/deploy_app_report.json`

### 重要环境行为

如果私有子网没有出站路由，脚本会自动回退，更新 ASG 子网放置到 `network-config.json` 中的现有公有子网，以便引导程序包安装可以完成。

---

## 4) 通过 ALB 验证应用健康状态

最小检查:

```text
GET http://experiment-alb-1466294824.us-east-1.elb.amazonaws.com/health
```

成功标准:

- HTTP 状态 `200`
- JSON 正文包含 `status: healthy`

---

## 5) 验证负载生成器连接

运行:

```bash
venv/Scripts/python.exe deployment/test_load_generator.py --request-rate 6 --duration-seconds 30 --success-threshold 0.8
```

此脚本执行的操作：

1. 从 `infrastructure/alb-config.json` 加载 ALB DNS
2. 针对 `/health` 运行 `scripts.load_generator.LoadGenerator`
3. 计算成功率和阈值通过/失败
4. 写入报告 JSON

输出工件:

- `deployment/load_generator_test_report.json`

接受阈值:

- 初始要求: >80% 成功率
- 观察到的运行: 100% (180/180)

---

## 6) Python 验证和类型安全工作流程

在最终确定前，运行:

```bash
venv/Scripts/python.exe -m py_compile deployment/deploy_app.py deployment/test_load_generator.py apps/test_app/app.py
```

可选的有针对性的测试:

```bash
python -m pytest tests/test_deploy_app.py tests/test_phase3_load_generator_check.py -q
```

---

## 7) 故障排查

### A) ALB 返回 502

可能原因:

- 实例用户数据在应用启动前失败
- 目标组没有健康的注册目标

操作:

1. 检查 `deployment/deploy_app_report.json` (`target_group_health`, `alb_health_probe`)
2. 检查 ASG 详情报告中的实例生命周期和健康状态
3. 启动模板更新后重新运行部署脚本

### B) 用户数据引导失败，出现包存储库超时

症状:

- 控制台日志显示 `Cannot find a valid baseurl for repo` / 镜像超时

原因:

- 子网没有出站互联网路径 (私有路由表缺少默认路由/NAT)

此阶段使用的操作:

- 脚本自动将 ASG 子网映射移至公有子网 (对于实验阶段是安全的)

### C) `InstanceRefreshInProgress` 错误

操作:

- 脚本现在检测正在进行的刷新并重用当前刷新 ID，而不是硬失败

### D) 负载生成器脚本无法导入项目模块

操作:

- 脚本为跨平台直接执行将项目根预置到 `sys.path`

---

## 8) 成本意识 (保持运行以进行实验)

基础设施应保持活跃以进行 Phase 4-5 实验。

此阶段期间的大约活跃成本范围:

- ALB + 3x t3.micro + 存储/指标: `~$0.06 - $0.09` 每小时 (粗略)

实验后，清理所有资源以避免持续费用。

---

## 9) 清理步骤 (实验后)

推荐顺序:

1. 将 ASG 缩放到 0 / 删除 ASG
2. 删除 ALB 监听器和 ALB
3. 删除目标组
4. 删除启动模板
5. 删除安全组
6. 删除路由表/子网/IGW/VPC

优先使用 boto3 脚本进行清理以确保一致性和可重现性。
