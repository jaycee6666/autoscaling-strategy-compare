# ✨ 项目上传到 GitHub - 完整步骤指南

## 📍 当前状态

✅ 本地 Git 仓库已初始化  
✅ 所有文件已提交  
✅ 共 2 个提交:
- Initial project setup - Phase 0 complete
- Add GitHub setup guides for team distribution

现在需要连接到 GitHub 远程仓库并推送代码。

---

## 🚀 三个简单步骤上传到 GitHub

### ⚠️ 重要提示

下面用 `YOUR-USERNAME` 代表你的 GitHub 用户名。替换为实际的用户名！

例子：
- 如果你的 GitHub 用户名是 `john-doe`
- URL 应该是: `git@github.com:john-doe/autoscaling-strategy-compare.git`

---

## 步骤 1️⃣: 创建 GitHub 仓库

### 方法 A: 使用网页界面 (最简单)

1. **登录 GitHub**
   ```
   https://github.com/login
   ```

2. **创建新仓库**
   ```
   https://github.com/new
   ```

3. **填写仓库信息**
   - **Repository name**: `autoscaling-strategy-compare`
   - **Description**: `Comparative Analysis of Autoscaling Strategies`
   - **Visibility**: 
     - 选择 `Public` (公开，任何人可见)
     - 或 `Private` (私有，仅邀请的人可见)
   - **Initialize this repository with**:
     - ❌ 不勾选任何选项 (我们已有本地仓库)

4. **点击 "Create repository"**

5. **复制 GitHub 给出的 SSH URL**
   - 应该看到这样的信息:
   ```
   git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git
   ```
   - 复制这个 URL

### 方法 B: 使用 GitHub CLI (如果已安装)

```bash
# 登录
gh auth login
# 按提示完成

# 创建仓库并直接推送
gh repo create autoscaling-strategy-compare \
  --source=. \
  --remote=origin \
  --push \
  --public
```

✅ 如果用这个方法，跳到步骤 3️⃣

---

## 步骤 2️⃣: 连接到 GitHub (本地操作)

在你的电脑上执行:

```bash
# 进入项目目录
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 添加远程仓库
# ⚠️ 替换 YOUR-USERNAME 为你的 GitHub 用户名
git remote add origin git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git

# 验证连接
git remote -v
```

应该输出:
```
origin  git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git (fetch)
origin  git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git (push)
```

---

## 步骤 3️⃣: 推送到 GitHub

```bash
# 重命名分支为 main (可选但推荐)
git branch -M main

# 推送代码
git push -u origin main
```

✅ **完成！** 代码已上传到 GitHub

---

## ✅ 验证成功

### 方法 1: 访问 GitHub 网站

打开浏览器访问:
```
https://github.com/YOUR-USERNAME/autoscaling-strategy-compare
```

应该看到:
- ✓ 所有文件和文件夹
- ✓ README.md 显示在首页
- ✓ 提交历史记录 (2 commits)

### 方法 2: 在本地验证

```bash
# 查看提交历史
git log --oneline

# 查看分支
git branch -a

# 查看远程配置
git remote -v
```

---

## 👥 分享给团队成员

### 分享步骤

1. 告诉团队仓库 URL:
   ```
   https://github.com/YOUR-USERNAME/autoscaling-strategy-compare
   ```

2. 如果是私有仓库，邀请团队成员:
   - 进入 Settings → Collaborators
   - 点击 "Add people"
   - 输入团队成员的 GitHub 用户名

### 团队成员获取项目

```bash
# Clone 仓库
git clone git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git

# 或用 HTTPS (不需要 SSH 配置)
git clone https://github.com/YOUR-USERNAME/autoscaling-strategy-compare.git

# 进入项目
cd autoscaling-strategy-compare

# 运行设置
python setup.py
```

---

## 🔐 使用 SSH 还是 HTTPS?

| 方式 | 优点 | 缺点 |
|------|------|------|
| **SSH** (推荐) | 安全、无需输入密码 | 需要配置 SSH 密钥 |
| **HTTPS** | 简单、开箱即用 | 每次需要输入用户名/密码 |

### 我已经配置了 SSH，用 SSH ✅

### 我没配置 SSH，用 HTTPS:

```bash
# 替换 SSH URL
git remote set-url origin https://github.com/YOUR-USERNAME/autoscaling-strategy-compare.git

# 推送
git push -u origin main
```

---

## ❓ 遇到问题?

### 问题 1: Permission denied (publickey)

**原因**: SSH 密钥未配置

**解决**:
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub  # macOS/Linux
type $env:USERPROFILE\.ssh\id_ed25519.pub  # Windows PowerShell

# 复制公钥，在 GitHub Settings → SSH keys 中添加
```

或者用 HTTPS:
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/autoscaling-strategy-compare.git
git push -u origin main
```

### 问题 2: fatal: 'origin' does not appear to be 'git' repository

**原因**: URL 配置错误

**解决**:
```bash
# 移除旧的
git remote remove origin

# 重新添加 (替换 YOUR-USERNAME)
git remote add origin git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git

# 验证
git remote -v
```

### 问题 3: refused to merge unrelated histories

**原因**: GitHub 上的仓库与本地不匹配

**解决**:
```bash
# 直接强制推送 (谨慎使用!)
git push -u origin main --force
```

### 问题 4: 需要输入密码

**原因**: 可能是 HTTPS 方式或 Personal Access Token

**解决**:
- 如果是 HTTPS: 输入 GitHub 用户名 + Personal Access Token (不是密码)
- 如果是 SSH: 确保 SSH 密钥已配置

---

## 📋 完整命令参考

```bash
# 1. 进入项目
cd C:\project\CS5296\project3\autoscaling-strategy-compare

# 2. 添加远程仓库 (替换 YOUR-USERNAME)
git remote add origin git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git

# 3. 查看状态
git status
git log --oneline
git remote -v

# 4. 推送到 GitHub
git branch -M main
git push -u origin main

# 5. 验证 (访问此 URL)
# https://github.com/YOUR-USERNAME/autoscaling-strategy-compare
```

---

## 🎯 下一步

### 对于项目协调者

1. ✅ 推送项目到 GitHub
2. 📧 发送仓库链接给团队
3. 👥 邀请团队成员加入 (如果是私有仓库)
4. 📝 分享 `docs/GITHUB_SETUP.md` 给团队参考

### 对于团队成员

1. ✅ Clone 仓库
2. ✅ 运行 `python setup.py`
3. ✅ 开始开发!

---

## 💡 最佳实践

### 日常工作流程

```bash
# 开始工作
git pull  # 拉取最新代码

# 做出更改
# ... 编辑文件 ...

# 提交更改
git add .
git commit -m "Feature: Brief description"

# 推送到 GitHub
git push
```

### 创建 Pull Request (代码审查)

```bash
# 创建新分支
git checkout -b feature/my-feature

# 做出更改并提交
git add .
git commit -m "Feature: Description"

# 推送分支
git push origin feature/my-feature

# 在 GitHub 上创建 Pull Request
# (GitHub 网站上操作)
```

---

## 📚 更多帮助

- **完整指南**: `docs/GITHUB_SETUP.md`
- **快速参考**: `GITHUB_QUICK_SETUP.md`
- **GitHub 文档**: https://docs.github.com
- **Git 教程**: https://git-scm.com/doc

---

## ✨ 总结

| 步骤 | 内容 | 状态 |
|------|------|------|
| 1 | 创建 GitHub 仓库 | ⏳ 待做 |
| 2 | 连接远程仓库 | ⏳ 待做 |
| 3 | 推送代码 | ⏳ 待做 |
| 4 | 验证 | ⏳ 待做 |
| 5 | 分享给团队 | ⏳ 待做 |

---

**版本**: 2.0  
**创建**: 2026-04-17  
**项目**: Autoscaling Strategy Comparison  
**下一步**: 按照上面的 3 个步骤上传到 GitHub!
