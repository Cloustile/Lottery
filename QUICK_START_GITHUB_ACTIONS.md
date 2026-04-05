# GitHub Actions 部署 - 快速参考

## 🚀 5分钟快速配置

### 1️⃣ 生成并配置 SSH 密钥（本地执行）

```bash
# 运行配置脚本
chmod +x setup-github-actions.sh
./setup-github-actions.sh 139.196.201.114 admin
```

或手动执行：

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "github-actions@lottery" -f ~/.ssh/github_actions_deploy

# 复制到服务器
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub admin@139.196.201.114

# 查看私钥（复制内容）
cat ~/.ssh/github_actions_deploy
```

### 2️⃣ 配置 GitHub Secret

1. 访问: https://github.com/your-username/Lottery/settings/secrets/actions
2. 点击 "New repository secret"
3. Name: `SERVER_SSH_KEY`
4. Value: 粘贴私钥的**完整内容**
5. 点击 "Add secret"

### 3️⃣ 首次服务器初始化

```bash
# SSH 到服务器
ssh admin@139.196.201.114

# 运行初始化脚本
chmod +x /home/admin/setup-server.sh
sudo /home/admin/setup-server.sh
```

### 4️⃣ 触发自动部署

```bash
git add .
git commit -m "Configure auto deployment"
git push origin main
```

完成！🎉

---

## 📊 常用命令

### 查看部署状态
```bash
# GitHub Actions
访问: https://github.com/your-username/Lottery/actions

# 服务器日志
ssh admin@139.196.201.114
tail -f /home/admin/lottery/lottery.log
```

### 服务管理
```bash
# 重启服务
sudo systemctl restart lottery.service

# 查看状态
sudo systemctl status lottery.service

# 查看日志
sudo journalctl -u lottery.service -f
```

### 手动触发部署
1. GitHub → Actions → Deploy to Server
2. 点击 "Run workflow"

---

## 🔧 故障排查

| 问题 | 解决方案 |
|------|---------|
| SSH 连接失败 | 检查公钥是否正确添加到服务器 |
| 权限被拒绝 | 确认 GitHub Secret 配置正确 |
| 服务启动失败 | 查看 `/home/admin/lottery/lottery.log` |
| 端口被占用 | `sudo lsof -i :8000` 查找并杀死进程 |

---

## 📝 配置文件位置

- **工作流**: `.github/workflows/deploy.yml`
- **服务配置**: `lottery.service`
- **初始化脚本**: `setup-server.sh`
- **详细文档**: `GITHUB_ACTIONS_DEPLOY.md`

---

## 🌐 访问地址

- **应用**: http://139.196.201.114:8000
- **管理后台**: http://139.196.201.114:8000/admin
- **API 文档**: http://139.196.201.114:8000/docs

---

## ⚠️ 重要提醒

1. **不要提交私钥** - `.gitignore` 已配置排除
2. **定期备份数据** - `lottery_data.json` 需要手动备份
3. **监控服务状态** - 设置告警通知
4. **保持系统更新** - 定期更新 Python 依赖

---

**需要帮助？** 查看 [GITHUB_ACTIONS_DEPLOY.md](GITHUB_ACTIONS_DEPLOY.md) 获取完整文档。
