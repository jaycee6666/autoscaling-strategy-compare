# 快速 GitHub 上传指南 (Quick Guide)

## 📱 5 分钟快速上传

### 前提条件
- ✅ Git 已安装
- ✅ GitHub 账户已创建
- ✅ SSH 密钥已配置

### 三个简单步骤

#### 1️⃣ 创建仓库 (在 GitHub 网站)

```
https://github.com/new
输入名称: autoscaling-strategy-compare
选择: Public (公开) 或 Private (私有)
点击: Create repository
```

#### 2️⃣ 添加远程仓库 (在本地)

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare

git remote add origin git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git
```

⚠️ **替换 `YOUR-USERNAME` 为你的 GitHub 用户名**

#### 3️⃣ 推送代码

```bash
git branch -M main
git push -u origin main
```

✅ **完成！访问 GitHub 验证**

---

## 🔗 完整 URL 参考

### 如果你的 GitHub 用户名是 `john-doe`

**SSH 方式 (推荐)**:
```
git@github.com:john-doe/autoscaling-strategy-compare.git
```

**HTTPS 方式**:
```
https://github.com/john-doe/autoscaling-strategy-compare.git
```

**GitHub 页面**:
```
https://github.com/john-doe/autoscaling-strategy-compare
```

---

## 💾 本地已经做了什么

✅ `git init` - 初始化仓库  
✅ `git add .` - 暂存所有文件  
✅ `git commit` - 创建提交  

**现在只需:**
1. 在 GitHub 创建仓库
2. `git remote add origin [URL]`
3. `git push -u origin main`

---

## 🚀 一条命令搞定 (如果安装了 GitHub CLI)

```bash
cd C:\project\CS5296\project3\autoscaling-strategy-compare
gh repo create autoscaling-strategy-compare --source=. --remote=origin --push --public
```

---

## ❓ 遇到问题?

| 问题 | 解决 |
|------|------|
| `git remote: command not found` | 安装 Git: https://git-scm.com |
| `Permission denied (publickey)` | 配置 SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh |
| `fatal: 'origin' not a repository` | 检查 `git remote -v` 输出 |
| 需要输入密码 | 使用 SSH 或 Personal Access Token |

---

## ✅ 验证成功

```bash
# 本地验证
git log --oneline
git remote -v

# 访问此 URL 验证 (替换用户名)
https://github.com/YOUR-USERNAME/autoscaling-strategy-compare
```

---

## 👥 分享给团队

### 团队成员获取项目

```bash
# Clone 仓库 (替换用户名)
git clone git@github.com:YOUR-USERNAME/autoscaling-strategy-compare.git

# 进入项目
cd autoscaling-strategy-compare

# 运行设置
python setup.py
```

---

**需要详细帮助?** 查看 `docs/GITHUB_SETUP.md`
