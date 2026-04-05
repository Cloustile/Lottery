# Lottery 幸运大抽奖系统

## 项目简介
一个功能完整的 Web 抽奖应用，采用 **FastAPI** 框架构建，提供便捷的线上抽奖活动解决方案。

## 技术栈
- **后端框架**: FastAPI v0.109.0
- **ASGI 服务器**: Uvicorn v0.27.0
- **数据验证**: Pydantic
- **依赖库**: 
  - python-multipart v0.0.6 (表单数据处理)
  - requests >= 2.28.0 (HTTP 请求)
- **数据存储**: JSON 文件 (`lottery_data.json`)
- **前端**: 原生 HTML/CSS/JS (响应式设计)

## 核心功能

### 用户端
- ✅ 证件号码登录（支持国际证件，无长度限制）
- ✅ 一次性抽奖机制
- ✅ 实时结果显示
- ✅ 响应式界面适配

### 管理端
- ✅ 奖项配置管理（名称/概率/上限）
- ✅ 数据统计看板（总次数/已发奖/人数）
- ✅ 进度监控可视化
- ✅ 用户批量导入/删除
- ✅ 系统统键重置

## 快速开始

### 1. 环境要求
- Python 3.8+
- pip (包管理工具)

### 2. 安装依赖
```bash
cd Lottery
pip install -r requirements.txt
```

### 3. 启动服务
```bash
python app.py
```

或使用 uvicorn：
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问地址
- **用户抽奖页**: http://localhost:8000/
- **管理后台**: http://localhost:8000/admin
- **API 文档**: http://localhost:8000/docs (FastAPI 自动生成)
- **ReDoc 文档**: http://localhost:8000/redoc

## ☁️ 云部署

### Vercel 部署（推荐）

项目已配置好 Vercel 部署文件，支持一键部署到云端。

**快速部署：**
```bash
# Windows 用户：双击运行
deploy-vercel.bat

# 或手动执行
npm install -g vercel
vercel --prod
```

**详细指南：** 查看 [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

⚠️ **重要提示：** Vercel 是无状态平台，数据无法持久化保存。适合短期活动或演示用途。如需长期运行，建议集成外部数据库（MongoDB/Supabase）。

### 其他云平台
- **Render.com**: 支持完整功能，包括数据持久化（推荐）
- **Railway.app**: 简单易用，提供数据库服务
- **传统云服务器**: 完全控制，需要手动配置

### 🤖 自动部署（GitHub Actions）

项目已配置 GitHub Actions 工作流，实现代码推送后自动部署到您的服务器。

**快速配置：**
1. 在服务器上配置 SSH 密钥
2. 在 GitHub Secrets 中添加 `SERVER_SSH_KEY`
3. 推送到 main 分支即可自动部署

**详细指南：** 查看 [GITHUB_ACTIONS_DEPLOY.md](GITHUB_ACTIONS_DEPLOY.md)

**服务器信息：**
- IP: `139.196.201.114`
- 用户: `admin`
- 部署路径: `/home/admin/lottery`
- 访问地址: `http://139.196.201.114:8000`

## 项目结构
```
Lottery/
├── app.py                  # FastAPI 后端主程序
├── index.html              # 用户端抽奖页面
├── admin.html              # 管理后台页面
├── lottery_data.json       # 数据持久化文件（自动生成）
├── requirements.txt        # Python 依赖包
├── test_lottery_probability.py  # 概率测试脚本
├── vercel.json             # Vercel 部署配置
└── README.md               # 项目说明文档
```

## API 接口说明

### 用户相关
- `POST /api/login` - 用户登录
- `POST /api/draw` - 执行抽奖

### 奖项管理
- `GET /api/prizes` - 获取奖项配置和统计
- `POST /api/prizes` - 更新奖项配置

### 用户管理
- `GET /api/users` - 获取所有用户列表
- `POST /api/users/import` - 批量导入用户
- `POST /api/users/delete` - 删除指定用户

### 其他
- `GET /api/winners` - 获取获奖名单
- `POST /api/reset` - 重置抽奖系统

## 注意事项

### 开发环境
- 默认端口：**8000**（原 Flask 版本为 5000）
- 调试模式已启用，代码修改后自动重载

### 生产环境
建议使用 Gunicorn + Uvicorn workers：
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app -b 0.0.0.0:8000
```

### 数据安全
- 生产环境请修改 `app.secret_key` 为强随机密钥
- 建议启用 HTTPS
- 定期备份 `lottery_data.json` 文件

### 性能优化
- FastAPI 原生支持异步处理，性能优于 Flask
- 高并发场景建议使用 Redis 替代 JSON 文件存储
- 可添加数据库连接池和缓存机制

## 测试
运行概率测试脚本：
```bash
python test_lottery_probability.py
```

## 部署

### Vercel 部署
项目已包含 `vercel.json` 配置文件，可直接部署到 Vercel：
```bash
vercel deploy
```

### Docker 部署（可选）
创建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 常见问题

### 1. 端口被占用
修改 `app.py` 中的端口号：
```python
uvicorn.run(app, host='0.0.0.0', port=8001)  # 改为其他端口
```

### 2. 页面显示异常
- 强制刷新浏览器：`Ctrl + Shift + R` (Windows) 或 `Cmd + Shift + R` (Mac)
- 清除浏览器缓存
- 检查控制台错误信息

### 3. API 请求失败
- 确认后端服务正在运行
- 检查端口是否正确（8000）
- 查看终端输出的错误日志

## 版本历史

### v2.0 (当前版本)
- 🚀 从 Flask 迁移到 FastAPI
- ⚡ 性能提升，支持异步处理
- 📚 自动生成 API 文档
- 🔧 使用 Pydantic 进行数据验证

### v1.x (Flask 版本)
- 初始版本，基于 Flask 框架

## 许可证
MIT License

## 联系方式
如有问题，请提交 Issue 或联系开发团队。
