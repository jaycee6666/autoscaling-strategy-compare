# 将项目提交到 GitHub - 完整指南

## 🎯 目标

将 `autoscaling-strategy-compare` 项目上传到 GitHub 仓库，供团队使用。

---

## 📋 前置准备

### 1. 创建 GitHub 账户 (如果还没有)
- 访问: https://github.com/signup
- 填写用户名、邮箱、密码
- 验证邮箱

### 2. 配置 Git 用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

验证配置:
```bash
git config --list | grep user
```

### 3. 生成 SSH Key (推荐，安全性更高)

在 PowerShell/Terminal 执行:
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# 或者用 RSA (老系统):
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
```

按 Enter 键接受默认位置，可以不设置密码（直接按 Enter）

查看公钥:
```bash
# Windows PowerShell:
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# macOS/Linux:
cat ~/.ssh/id_ed25519.pub
```

复制输出的公钥

### 4. 在 GitHub 添加 SSH Key

1. 登录 GitHub 账户
2. 点击右上角头像 → Settings → SSH and GPG keys
3. 点击 "New SSH key"
4. Title: 输入电脑名称 (如 "My Laptop")
5. Key type: Authentication Key
6. Key: 粘贴刚才复制的公钥
7. 点击 "Add SSH key"

---

## 🚀 方法一: 使用 Web 界面 (最简单)

### 步骤 1: 在 GitHub 创建新仓库

1. 登录 https://github.com
2. 点击右上角 + 号 → New repository
3. 填写信息:
   ```
   Repository name: autoscaling-strategy-compare
   Description: Comparative Analysis of Autoscaling Strategies
   Public: ✓ (如果要共享)
   Private: ✓ (如果只限团队)
   Initialize this repository with:
     - Add a README file: 不勾 (已有)
     - Add .gitignore: 不勾 (已有)
     - Add a license: 可选
   ```
4. 点击 "Create repository"

### 步骤 2: 复制仓库 URL

创建后，你会看到:
```
https://github.com/your-username/autoscaling-strategy-compare.git
```

或 SSH URL:
```
git@github.com:your-username/autoscaling-strategy-compare.git
```

复制其中一个

### 步骤 3: 在本地添加远程仓库

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 使用 HTTPS (需要输入密码):
git remote add origin https://github.com/your-username/autoscaling-strategy-compare.git

# 或使用 SSH (推荐，已配置密钥):
git remote add origin git@github.com:your-username/autoscaling-strategy-compare.git
```

验证:
```bash
git remote -v
```

### 步骤 4: 上传到 GitHub

```bash
git branch -M main
git push -u origin main
```

首次可能需要验证:
- HTTPS: 输入 GitHub 用户名和 Personal Access Token
- SSH: 确认 SSH Key 指纹

### 完成！✅

访问 https://github.com/your-username/autoscaling-strategy-compare 查看

---

## 🚀 方法二: 使用 GitHub CLI (推荐)

### 安装 GitHub CLI

**Windows (Chocolatey):**
```bash
choco install gh
```

**Windows (Winget):**
```bash
winget install GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh
```

### 使用 GitHub CLI 创建和推送

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 登录 GitHub
gh auth login
# 选择: GitHub.com
# 选择: SSH (推荐) 或 HTTPS
# 按提示完成认证

# 创建仓库
gh repo create autoscaling-strategy-compare \
  --source=. \
  --remote=origin \
  --push \
  --public
  # 或用 --private 创建私有仓库
```

完成！✅

---

## 🔧 步骤详解 (使用 Git 命令)

### 完整命令序列

```bash
# 1. 进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 2. 检查 git 状态
git status

# 3. 查看已有的远程
git remote -v

# 4. 添加远程仓库
# 将 your-username 替换为你的 GitHub 用户名
git remote add origin git@github.com:your-username/autoscaling-strategy-compare.git

# 5. 检查本地分支
git branch

# 6. 重命名分支为 main (如果需要)
git branch -M main

# 7. 推送到 GitHub (首次需要 -u 参数)
git push -u origin main

# 8. 以后更新只需要:
git push
```

---

## 📝 验证上传成功

### 在 GitHub 网站验证

1. 访问 https://github.com/your-username/autoscaling-strategy-compare
2. 应该看到:
   - ✓ 所有文件和文件夹
   - ✓ README.md 显示在首页
   - ✓ 提交记录显示

### 在本地验证

```bash
git log --oneline
```

应该显示:
```
8561818 Initial project setup - Phase 0 complete
```

---

## 👥 邀请团队成员

### 方法 1: 添加协作者 (付费私有仓库免费)

1. 进入仓库 Settings → Access → Collaborators
2. 点击 "Add people"
3. 输入团队成员的 GitHub 用户名
4. 选择权限: Maintain (推荐)
5. 发送邀请

### 方法 2: 创建 Organization (多人协作最佳)

1. 点击右上角 + 号 → New organization
2. 填写组织名称 (如 CS5296-Group)
3. 选择 Free 或 Pro 计划
4. 把仓库转移到 Organization
5. 邀请成员加入 Organization

### 方法 3: 分享仓库链接

如果是公开仓库，直接分享链接:
```
https://github.com/your-username/autoscaling-strategy-compare
```

团队成员可以 clone:
```bash
git clone https://github.com/your-username/autoscaling-strategy-compare.git
```

---

## 🐛 常见问题

### Q1: "Permission denied (publickey)"

**原因**: SSH 密钥未正确配置

**解决**:
```bash
# 测试 SSH 连接
ssh -T git@github.com

# 如果失败，重新生成密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 确保 SSH agent 运行
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Q2: "fatal: 'origin' does not appear to be a 'git' repository"

**原因**: 远程仓库配置错误

**解决**:
```bash
# 移除旧的远程
git remote remove origin

# 重新添加
git remote add origin git@github.com:your-username/repo-name.git

# 验证
git remote -v
```

### Q3: 如何修改已推送的代码?

```bash
# 修改本地代码后
git add .
git commit -m "Fix: description of changes"
git push
```

### Q4: 如何删除已上传的文件?

```bash
# 1. 从 git 中删除 (但保留本地文件)
git rm --cached filename
git commit -m "Remove file"
git push

# 2. 从 git 中删除 (同时删除本地文件)
git rm filename
git commit -m "Delete file"
git push
```

### Q5: 如何更新代码?

```bash
# 如果团队成员也在贡献
git pull  # 先拉取最新代码
# 解决冲突 (如果有)
git add .
git commit -m "Merge changes"
git push
```

---

## 📚 分享给团队成员的步骤

### 对于 Windows 用户

1. **安装 Git**
   ```bash
   # 如果没装过
   choco install git
   # 或从 https://git-scm.com 下载
   ```

2. **Clone 仓库**
   ```bash
   git clone git@github.com:your-username/autoscaling-strategy-compare.git
   # 或用 HTTPS:
   git clone https://github.com/your-username/autoscaling-strategy-compare.git
   ```

3. **进入项目**
   ```bash
   cd autoscaling-strategy-compare
   python setup.py
   ```

4. **完成！**

### 对于 macOS/Linux 用户

```bash
git clone git@github.com:your-username/autoscaling-strategy-compare.git
cd autoscaling-strategy-compare
python setup.py
```

---

## 🔐 安全最佳实践

### ✅ 确保做了这些

- [x] `.env` 在 `.gitignore` 中 (不上传凭证)
- [x] 没有硬编码的密钥
- [x] 已配置 SSH 密钥
- [x] 定期更新依赖

### ❌ 确保没做这些

- [x] 不要 push `.env` 文件
- [x] 不要 push AWS 凭证
- [x] 不要 push 个人密钥
- [x] 不要 force push 到 main

---

## 📊 项目状态检查

```bash
# 查看当前状态
git status

# 查看提交历史
git log --oneline

# 查看远程配置
git remote -v

# 查看分支
git branch -a
```

---

## 🎓 常用 Git 命令速查

```bash
# 查看更改
git diff

# 暂存所有更改
git add .

# 提交
git commit -m "message"

# 推送到远程
git push

# 拉取最新
git pull

# 创建新分支
git checkout -b feature-name

# 切换分支
git checkout main

# 合并分支
git merge feature-name

# 删除本地分支
git branch -d branch-name

# 查看标签
git tag

# 创建标签
git tag -a v1.0 -m "Version 1.0"
git push origin v1.0
```

---

## ✅ 最终检查清单

- [ ] GitHub 账户已创建
- [ ] SSH 密钥已配置
- [ ] 在 GitHub 创建了仓库
- [ ] 本地 git 已初始化并提交
- [ ] 远程仓库已添加
- [ ] 代码已推送到 GitHub
- [ ] 可以在 GitHub 网站看到项目
- [ ] 团队成员已被邀请 (可选)
- [ ] 团队成员能成功 clone 仓库

---

## 🚀 后续工作

### 团队成员每日工作流

```bash
# 1. 开始工作前，拉取最新代码
git pull

# 2. 创建新分支 (可选但推荐)
git checkout -b feature/phase1-network

# 3. 做出更改
# ... 编辑文件 ...

# 4. 查看更改
git diff

# 5. 暂存更改
git add .

# 6. 提交
git commit -m "Feature: Implement network setup script"

# 7. 推送
git push origin feature/phase1-network

# 8. 在 GitHub 上创建 Pull Request
# (可选，用于代码审查)
```

---

## 📞 支持

- **GitHub 帮助**: https://docs.github.com
- **Git 教程**: https://git-scm.com/doc
- **SSH 配置**: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

**版本**: 1.0  
**创建时间**: 2026-04-17  
**项目**: Autoscaling Strategy Comparison  
**团队**: WU Wanpeng, CHEN Sijie
