# GitHub Actions 自动部署指南

## 📋 概述

本项目已配置 GitHub Actions 工作流，实现代码推送到 GitHub 后自动部署到您的服务器（139.196.201.114）。

---

## 🔧 配置步骤

### 步骤 1: 在服务器上生成 SSH 密钥对

在您的**本地电脑**上执行：

```bash
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "github-actions@lottery" -f ~/.ssh/github_actions_deploy

# 这会生成两个文件：
# - ~/.ssh/github_actions_deploy     (私钥)
# - ~/.ssh/github_actions_deploy.pub (公钥)
```

### 步骤 2: 将公钥添加到服务器

```bash
# 复制公钥到服务器
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub admin@139.196.201.114

# 或者手动添加
cat ~/.ssh/github_actions_deploy.pub | ssh admin@139.196.201.114 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

测试连接：
```bash
ssh -i ~/.ssh/github_actions_deploy admin@139.196.201.114
```

### 步骤 3: 在 GitHub 仓库中配置 Secret

1. **访问 GitHub 仓库**
   - 打开您的 Lottery 项目
   - 点击 "Settings" → "Secrets and variables" → "Actions"

2. **添加 Secret**
   - 点击 "New repository secret"
   - Name: `SERVER_SSH_KEY`
   - Value: 粘贴私钥内容（`~/.ssh/github_actions_deploy` 的完整内容）

   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
   ...（完整的私钥内容）...
   -----END OPENSSH PRIVATE KEY-----
   ```

3. **保存**

### 步骤 4: 首次部署到服务器

#### 方法 A: 使用初始化脚本（推荐）

```bash
# 1. 上传初始化脚本到服务器
scp setup-server.sh admin@139.196.201.114:/home/admin/

# 2. SSH 连接到服务器
ssh admin@139.196.201.114

# 3. 运行初始化脚本
chmod +x /home/admin/setup-server.sh
sudo /home/admin/setup-server.sh
```

#### 方法 B: 手动配置

```bash
# 1. SSH 连接到服务器
ssh admin@139.196.201.114

# 2. 创建部署目录
mkdir -p /home/admin/lottery
cd /home/admin/lottery

# 3. 安装 Python
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 4. 配置 systemd 服务（可选但推荐）
sudo cp lottery.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lottery.service

# 5. 开放端口
sudo ufw allow 8000/tcp
```

### 步骤 5: 推送代码触发自动部署

```bash
# 提交并推送代码
git add .
git commit -m "Configure GitHub Actions deployment"
git push origin main
```

GitHub Actions 会自动触发部署！

---

## 🚀 工作流程

### 自动触发
- ✅ 推送到 `main` 或 `master` 分支时自动部署
- ✅ Pull Request 合并到主分支时自动部署

### 手动触发
1. 访问 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Deploy to Server" 工作流
4. 点击 "Run workflow" → "Run workflow"

---

## 📊 监控部署

### 查看部署状态

1. **GitHub Actions**
   - 访问: https://github.com/your-username/Lottery/actions
   - 查看最新的工作流运行状态

2. **服务器日志**
   ```bash
   # SSH 到服务器
   ssh admin@139.196.201.114
   
   # 查看应用日志
   tail -f /home/admin/lottery/lottery.log
   
   # 如果使用 systemd
   sudo journalctl -u lottery.service -f
   ```

3. **检查服务状态**
   ```bash
   # 检查进程
   ps aux | grep app.py
   
   # 如果使用 systemd
   sudo systemctl status lottery.service
   ```

---

## 🔍 故障排查

### 问题 1: 部署失败 - SSH 连接错误

**症状:**
```
Host key verification failed
```

**解决:**
```bash
# 在 GitHub Actions 工作流中已自动处理
# 确保服务器 IP 正确且可访问
```

### 问题 2: 权限被拒绝

**症状:**
```
Permission denied (publickey)
```

**解决:**
1. 确认公钥已正确添加到服务器的 `~/.ssh/authorized_keys`
2. 确认私钥已正确配置为 GitHub Secret
3. 测试本地连接: `ssh -i 私钥文件 admin@139.196.201.114`

### 问题 3: 服务启动失败

**症状:**
```
Service failed to start
```

**解决:**
```bash
# SSH 到服务器查看日志
ssh admin@139.196.201.114
tail -n 100 /home/admin/lottery/lottery.log

# 检查依赖是否安装
pip3 list | grep fastapi

# 手动启动测试
cd /home/admin/lottery
python3 app.py
```

### 问题 4: 端口被占用

**症状:**
```
Address already in use
```

**解决:**
```bash
# 查找占用端口的进程
sudo lsof -i :8000

# 杀死旧进程
sudo kill -9 <PID>

# 重启服务
sudo systemctl restart lottery.service
```

---

## 🛠️ 管理命令

### 服务管理（使用 systemd）

```bash
# 查看状态
sudo systemctl status lottery.service

# 启动服务
sudo systemctl start lottery.service

# 停止服务
sudo systemctl stop lottery.service

# 重启服务
sudo systemctl restart lottery.service

# 查看日志
sudo journalctl -u lottery.service -f

# 开机自启
sudo systemctl enable lottery.service
```

### 服务管理（不使用 systemd）

```bash
# 启动
cd /home/admin/lottery
nohup python3 app.py > lottery.log 2>&1 &
echo $! > lottery.pid

# 停止
kill $(cat lottery.pid)

# 查看日志
tail -f lottery.log

# 查看进程
ps aux | grep app.py
```

---

## 📝 自定义配置

### 修改部署路径

编辑 `.github/workflows/deploy.yml`:
```yaml
env:
  DEPLOY_PATH: /your/custom/path
```

### 修改端口

编辑 `app.py`:
```python
uvicorn.run(app, host='0.0.0.0', port=YOUR_PORT)
```

同时更新防火墙规则和服务配置。

### 添加环境变量

在 `.github/workflows/deploy.yml` 中添加:
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

然后在服务器上创建 `.env` 文件。

---

## 🔒 安全建议

1. **使用专用部署用户**
   ```bash
   # 创建专用用户
   sudo useradd -m -s /bin/bash deploy
   sudo usermod -aG sudo deploy
   ```

2. **限制 SSH 密钥权限**
   ```bash
   chmod 600 ~/.ssh/github_actions_deploy
   ```

3. **定期更新密钥**
   - 每 3-6 个月轮换一次 SSH 密钥
   - 删除不再使用的密钥

4. **使用防火墙**
   ```bash
   sudo ufw enable
   sudo ufw allow 8000/tcp
   sudo ufw allow 22/tcp
   ```

5. **启用 HTTPS**（推荐）
   - 使用 Nginx 反向代理
   - 配置 Let's Encrypt SSL 证书

---

## 📊 性能优化

### 使用 Gunicorn（生产环境推荐）

修改 `requirements.txt`:
```txt
gunicorn==21.2.0
```

修改 systemd 服务文件:
```ini
ExecStart=/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app -b 0.0.0.0:8000
```

### 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🎯 最佳实践

1. **始终在测试环境验证**
   - 先在本地测试所有功能
   - 使用 staging 分支测试部署流程

2. **保持依赖最新**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

3. **定期备份数据**
   ```bash
   # 备份 lottery_data.json
   cp lottery_data.json lottery_data.backup.$(date +%Y%m%d).json
   ```

4. **监控服务状态**
   - 设置健康检查端点
   - 配置告警通知

5. **使用版本控制**
   - 所有配置变更都通过 Git 管理
   - 使用标签标记发布版本

---

## 📞 获取帮助

- **GitHub Actions 文档**: https://docs.github.com/en/actions
- **systemd 文档**: https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **项目 Issue**: GitHub Issues

---

## ✅ 检查清单

部署前确认：

- [ ] SSH 密钥对已生成
- [ ] 公钥已添加到服务器
- [ ] 私钥已配置为 GitHub Secret (`SERVER_SSH_KEY`)
- [ ] 服务器已安装 Python 3.8+
- [ ] 部署目录已创建 (`/home/admin/lottery`)
- [ ] 防火墙已开放端口 8000
- [ ] systemd 服务已配置（可选但推荐）
- [ ] 首次部署已完成

**完成以上步骤后，每次推送到 main 分支都会自动部署！** 🎉
