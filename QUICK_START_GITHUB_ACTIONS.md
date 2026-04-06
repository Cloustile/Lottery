# GitHub Actions 自动部署 - 快速开始

## ✅ 已完成的服务器配置

### 1. SSH 密钥认证
- 私钥位置: `C:\Users\骏马奔腾\.ssh\github_actions_deploy`
- 公钥已添加到服务器的 `/root/.ssh/authorized_keys`
- 权限设置正确 (目录 700, 文件 600)

### 2. Python 环境
- Python 3.8.12 已编译安装到 `/usr/local/python3.8/`
- 所有项目依赖已安装 (fastapi, uvicorn, jinja2, python-multipart 等)

### 3. Nginx 反向代理
- 静态文件服务: `/home/admin/nginx-1.29.3/Lottery`
- API 反向代理: `/api/*` → `http://127.0.0.1:8000`
- 配置文件: `/usr/local/nginx/conf/nginx.conf`

### 4. Systemd 服务管理
- 服务名称: `lottery.service`
- 运行用户: `admin`
- 监听端口: `127.0.0.1:8000`
- 自动重启: 已启用

### 5. GitHub Actions 工作流
- 工作流文件: `.github/workflows/deploy.yml`
- 触发条件: 推送到 main/master 分支或手动触发
- Secret 名称: `FirstKey`

## 🚀 如何启用自动部署

### 步骤 1: 添加 SSH 私钥到 GitHub Secrets

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写以下信息:
   - **Name**: `FirstKey`
   - **Value**: 复制 `C:\Users\骏马奔腾\.ssh\github_actions_deploy` 文件的**完整内容**
   
   > ⚠️ **重要**: 必须包含完整的 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 标记

5. 点击 **Add secret**

### 步骤 2: 验证 Secret 格式

确保 Secret 值包含换行符,格式如下:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBs/fHSEuuVnD7iL85WfqKaEnzlKTDYz3rvY2cdsm62dwAAAJh...
-----END OPENSSH PRIVATE KEY-----
```

### 步骤 3: 测试部署

#### 方法 1: 推送代码触发
```bash
git add .
git commit -m "Test auto deployment"
git push origin main
```

#### 方法 2: 手动触发
1. 进入 GitHub 仓库的 **Actions** 标签
2. 选择 **Deploy to Server** 工作流
3. 点击 **Run workflow**
4. 选择分支 (main 或 master)
5. 点击 **Run workflow**

### 步骤 4: 监控部署过程

1. 在 **Actions** 标签中查看运行状态
2. 点击具体的运行记录查看详细日志
3. 部署成功后会显示: `🎉 Deployment completed successfully!`

## 📊 部署流程说明

GitHub Actions 执行以下步骤:

1. **Checkout code**: 检出最新代码
2. **Setup SSH**: 配置 SSH 代理
3. **Add server to known hosts**: 添加服务器到已知主机
4. **Deploy to server**: 
   - 使用 rsync 同步文件 (排除不必要的文件)
   - 在服务器上安装 Python 依赖
   - 重启 systemd 服务
   - 验证服务状态

## 🔍 验证部署成功

部署完成后,访问以下地址验证:

- **前端页面**: http://139.196.201.114
- **管理后台**: http://139.196.201.114/admin.html
- **API 文档**: http://139.196.201.114/docs

## 🛠️ 常用管理命令

连接到服务器后可以使用以下命令:

```bash
# 查看服务状态
systemctl status lottery.service

# 查看实时日志
journalctl -u lottery.service -f

# 重启服务
systemctl restart lottery.service

# 查看 Nginx 状态
/usr/local/nginx/sbin/nginx -t

# 重新加载 Nginx
/usr/local/nginx/sbin/nginx -s reload
```

## ⚠️ 注意事项

1. **数据保护**: `lottery_data.json` 已被排除在同步之外,不会被覆盖
2. **服务中断**: 部署过程中会有 3-5 秒的服务中断
3. **依赖更新**: 修改 `requirements.txt` 后会自动安装新依赖
4. **备份建议**: 定期备份 `lottery_data.json` 文件

## 🐛 故障排查

### 问题 1: SSH 连接失败
**症状**: `Permission denied (publickey)`

**解决**:
1. 检查 Secret `FirstKey` 是否正确添加
2. 确保私钥格式完整,包含 BEGIN/END 标记
3. 本地测试: `ssh -i "C:\Users\骏马奔腾\.ssh\github_actions_deploy" root@139.196.201.114`

### 问题 2: 服务启动失败
**症状**: GitHub Actions 显示部署成功,但网站无法访问

**解决**:
```bash
# 查看服务日志
journalctl -u lottery.service -n 50 --no-pager

# 检查端口占用
netstat -tlnp | grep 8000

# 手动测试启动
cd /home/admin/nginx-1.29.3/Lottery
/usr/local/python3.8/bin/python3.8 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### 问题 3: Nginx 返回 502 错误
**症状**: 访问网站显示 502 Bad Gateway

**解决**:
```bash
# 检查 FastAPI 服务是否运行
systemctl status lottery.service

# 检查 Nginx 配置
/usr/local/nginx/sbin/nginx -t

# 重启 Nginx
/usr/local/nginx/sbin/nginx -s reload
```

## 📝 下一步建议

1. **设置监控**: 配置服务健康检查和告警
2. **定期备份**: 设置 cron 任务自动备份数据文件
3. **HTTPS 配置**: 申请 SSL 证书并配置 HTTPS
4. **域名绑定**: 绑定自定义域名并配置 DNS

## 📞 技术支持

如遇到问题,请检查:
1. GitHub Actions 运行日志
2. 服务器系统日志 (`journalctl`)
3. Nginx 错误日志 (`/usr/local/nginx/logs/error.log`)
4. 应用日志 (`journalctl -u lottery.service`)

---

**最后更新**: 2026-04-06
**配置版本**: v1.0
