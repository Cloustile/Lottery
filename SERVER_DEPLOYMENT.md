# 服务器自动部署配置指南

## 概述
本文档说明如何配置 GitHub Actions 自动部署 Lottery 项目到服务器 `139.196.201.114`。

## 服务器配置完成项

### 1. SSH 密钥认证
- ✅ 公钥已添加到 `/root/.ssh/authorized_keys`
- ✅ 私钥路径: `C:\Users\骏马奔腾\.ssh\github_actions_deploy`
- ✅ 目录权限: `.ssh` (700), `authorized_keys` (600)

### 2. Python 环境
- ✅ Python 3.8.12 已编译安装到 `/usr/local/python3.8/`
- ✅ 项目依赖已安装 (fastapi, uvicorn, jinja2 等)
- ✅ 使用命令: `/usr/local/python3.8/bin/python3.8`

### 3. Nginx 配置
- ✅ 配置文件: `/usr/local/nginx/conf/nginx.conf`
- ✅ 静态文件根目录: `/home/admin/nginx-1.29.3/Lottery`
- ✅ API 反向代理: `/api/*` → `http://127.0.0.1:8000`
- ✅ 静态文件缓存: HTML/CSS/JS 等文件缓存 1 天

### 4. Systemd 服务
- ✅ 服务文件: `/etc/systemd/system/lottery.service`
- ✅ 服务名称: `lottery.service`
- ✅ 运行用户: `admin`
- ✅ 监听地址: `127.0.0.1:8000`
- ✅ 自动重启: 启用 (Restart=always)

### 5. 项目目录
- ✅ 部署路径: `/home/admin/nginx-1.29.3/Lottery`
- ✅ 目录所有者: `admin:admin`
- ✅ 目录权限: `755`

## GitHub Actions 配置

### 1. 添加 Secret
在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加:
- **Secret 名称**: `FirstKey`
- **Secret 值**: SSH 私钥的完整内容 (包含 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`)

### 2. 工作流文件
工作流文件位于: `.github/workflows/deploy.yml`

触发条件:
- 推送到 `main` 或 `master` 分支
- 手动触发 (workflow_dispatch)

部署流程:
1. 检出代码
2. 设置 SSH 代理
3. 使用 rsync 同步文件到服务器 (排除不必要的文件)
4. 在服务器上安装依赖
5. 重启 systemd 服务
6. 验证服务状态

### 3. 排除的文件
以下文件不会被同步到服务器:
- `.git/` - Git 版本控制
- `__pycache__/` - Python 缓存
- `*.pyc` - Python 编译文件
- `.vercel/` - Vercel 配置
- `node_modules/` - Node 模块
- `.env` - 环境变量
- `.github/` - GitHub 配置
- `*.md` - 文档文件
- `deploy-vercel.bat` - Vercel 部署脚本
- `start.bat`, `start.sh` - 本地启动脚本
- `Python-3.8.12/` - Python 源码
- `Python-3.8.12.tgz` - Python 压缩包
- `nginx.conf` - Nginx 配置 (已在服务器配置)
- `lottery.service` - Systemd 服务 (已在服务器配置)

## 常用管理命令

### 服务管理
```bash
# 查看服务状态
systemctl status lottery.service

# 重启服务
systemctl restart lottery.service

# 停止服务
systemctl stop lottery.service

# 启动服务
systemctl start lottery.service

# 查看日志
journalctl -u lottery.service -f

# 查看最近 50 行日志
journalctl -u lottery.service -n 50 --no-pager
```

### Nginx 管理
```bash
# 测试配置
/usr/local/nginx/sbin/nginx -t

# 重新加载配置
/usr/local/nginx/sbin/nginx -s reload

# 重启 Nginx
/usr/local/nginx/sbin/nginx -s stop && /usr/local/nginx/sbin/nginx

# 查看 Nginx 进程
ps aux | grep nginx
```

### 手动部署
```bash
# 在服务器上手动更新
cd /home/admin/nginx-1.29.3/Lottery
git pull
/usr/local/python3.8/bin/pip3.8 install -r requirements.txt
systemctl restart lottery.service
```

## 访问地址
- **前端页面**: http://139.196.201.114
- **管理后台**: http://139.196.201.114/admin.html
- **API 文档**: http://139.196.201.114/docs (通过 Nginx 反向代理)

## 故障排查

### 1. 服务无法启动
```bash
# 查看详细日志
journalctl -u lottery.service -n 100 --no-pager

# 检查端口占用
netstat -tlnp | grep 8000

# 手动启动测试
cd /home/admin/nginx-1.29.3/Lottery
/usr/local/python3.8/bin/python3.8 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### 2. Nginx 返回 502 错误
```bash
# 检查 FastAPI 服务是否运行
systemctl status lottery.service

# 检查 Nginx 配置
/usr/local/nginx/sbin/nginx -t

# 查看 Nginx 错误日志
tail -f /usr/local/nginx/logs/error.log
```

### 3. 权限问题
```bash
# 修复目录所有权
chown -R admin:admin /home/admin/nginx-1.29.3/Lottery

# 修复目录权限
chmod -R 755 /home/admin/nginx-1.29.3/Lottery
```

### 4. SSH 连接失败
```bash
# 测试 SSH 连接
ssh -i "C:\Users\骏马奔腾\.ssh\github_actions_deploy" -v root@139.196.201.114

# 检查 authorized_keys
cat /root/.ssh/authorized_keys

# 检查权限
ls -la /root/.ssh/
```

## 注意事项

1. **数据持久化**: `lottery_data.json` 文件存储在服务器上,GitHub Actions 部署时会保留该文件 (因为使用了 rsync --delete,但排除了数据文件)

2. **依赖更新**: 如果 `requirements.txt` 有变化,GitHub Actions 会自动安装新依赖

3. **服务中断**: 部署过程中会有短暂的服务中断 (通常 3-5 秒)

4. **备份建议**: 定期备份 `lottery_data.json` 文件
   ```bash
   cp /home/admin/nginx-1.29.3/Lottery/lottery_data.json /backup/lottery_data_$(date +%Y%m%d).json
   ```

5. **监控建议**: 定期检查服务状态和磁盘空间
   ```bash
   df -h
   systemctl status lottery.service
   ```

## 更新历史
- 2026-04-06: 初始配置完成
  - 编译安装 Python 3.8.12
  - 配置 Nginx 反向代理
  - 创建 systemd 服务
  - 配置 GitHub Actions 自动部署
