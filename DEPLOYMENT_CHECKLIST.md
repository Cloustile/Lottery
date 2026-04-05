# Vercel 部署检查清单

## ✅ 部署前检查

### 1. 文件完整性
- [x] `app.py` - FastAPI 应用主文件
- [x] `requirements.txt` - Python 依赖包
- [x] `vercel.json` - Vercel 配置文件
- [x] `.vercelignore` - 忽略文件配置
- [x] `index.html` - 用户端页面
- [x] `admin.html` - 管理后台页面
- [x] `lottery_data.json` - 数据文件（会自动生成）

### 2. 依赖检查
```bash
# 确保所有依赖已安装
pip install -r requirements.txt

# 验证 FastAPI 可正常导入
python -c "from app import app; print('✅ FastAPI 应用加载成功')"
```

### 3. 本地测试
```bash
# 启动本地服务器
python app.py

# 在浏览器中测试
# - http://localhost:8000/
# - http://localhost:8000/admin
# - http://localhost:8000/docs
```

---

## 🚀 部署步骤

### 方法 1：使用部署脚本（最简单）
```bash
# Windows 用户
双击运行 deploy-vercel.bat

# 按照提示操作即可
```

### 方法 2：手动部署
```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录 Vercel
vercel login

# 3. 进入项目目录
cd f:\0-Projects\Lottery

# 4. 预览部署（测试）
vercel

# 5. 生产部署
vercel --prod
```

### 方法 3：GitHub 集成
```bash
# 1. 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit for Vercel deployment"

# 2. 推送到 GitHub
git remote add origin <your-repo-url>
git push -u origin main

# 3. 在 Vercel.com 导入 GitHub 仓库
# 4. 点击 Deploy 按钮
```

---

## ⚙️ 配置说明

### vercel.json 关键配置
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

**说明：**
- `@vercel/python`: 使用 Vercel 的 Python 构建器
- `routes`: 将所有路由指向 app.py

---

## 🔍 部署后验证

### 1. 检查部署状态
```bash
# 查看部署列表
vercel ls

# 查看最新部署日志
vercel logs <deployment-url>
```

### 2. 功能测试
访问部署后的 URL，测试以下功能：

- [ ] 首页可以正常访问
- [ ] 管理后台可以打开
- [ ] API 文档页面正常显示
- [ ] 用户可以登录
- [ ] 抽奖功能正常工作
- [ ] 管理后台数据显示正常

### 3. API 测试
```bash
# 测试奖项接口
curl https://your-domain.vercel.app/api/prizes

# 测试用户列表
curl https://your-domain.vercel.app/api/users
```

---

## ⚠️ 重要注意事项

### 数据持久化问题

**Vercel 的限制：**
- ❌ 无法保存 `lottery_data.json` 到文件系统
- ❌ 每次部署后数据会重置
- ❌ 不同请求可能在不同实例上运行

**解决方案：**

#### 方案 A：短期活动（当前配置）
- ✅ 适合一次性抽奖活动
- ✅ 活动结束后导出数据即可
- ✅ 无需额外配置

**数据导出方法：**
```bash
# 在活动结束后，通过 API 导出数据
curl https://your-domain.vercel.app/api/winners > winners.json
curl https://your-domain.vercel.app/api/users > users.json
```

#### 方案 B：长期运行（需要改造）
如需长期运行且保持数据，需要：

1. **集成云数据库**
   - MongoDB Atlas（推荐，免费）
   - Supabase（PostgreSQL，免费）
   - Firebase（NoSQL，免费额度）

2. **修改数据存储逻辑**
   ```python
   # 从本地文件改为云数据库
   from pymongo import MongoClient
   
   client = MongoClient(os.environ.get('MONGODB_URI'))
   db = client['lottery_db']
   ```

3. **配置环境变量**
   - 在 Vercel Dashboard 设置 `MONGODB_URI`

---

## 🐛 常见问题排查

### 问题 1：部署失败
**症状：** 构建错误

**解决：**
```bash
# 1. 检查 requirements.txt
cat requirements.txt

# 2. 查看构建日志
vercel logs <deployment-url>

# 3. 确保没有语法错误
python -m py_compile app.py
```

### 问题 2：502 Bad Gateway
**症状：** 页面无法访问

**解决：**
- 检查 app.py 是否有运行时错误
- 查看 Vercel 函数日志
- 确保所有依赖都在 requirements.txt 中

### 问题 3：数据丢失
**症状：** 刷新后数据消失

**原因：** Vercel 无状态特性

**解决：**
- 短期活动：接受此限制，活动后导出数据
- 长期活动：集成外部数据库

### 问题 4：冷启动慢
**症状：** 首次访问很慢

**解决：**
- 这是 Serverless 的正常现象
- 可以使用 Vercel Pro 计划的预热功能
- 或考虑迁移到 Render/Railway

---

## 📊 监控和维护

### 查看实时日志
```bash
vercel logs <deployment-url> --follow
```

### 查看部署统计
- 访问 Vercel Dashboard
- 查看 Analytics 标签页
- 监控流量和错误率

### 更新部署
```bash
# 修改代码后
git add .
git commit -m "Update description"
git push

# Vercel 会自动重新部署（如果使用 GitHub 集成）
# 或手动部署
vercel --prod
```

---

## 💡 优化建议

### 1. 减少包体积
- 只保留必要的依赖
- 移除测试文件和文档（已在 .vercelignore 中配置）

### 2. 环境变量
- 敏感信息使用环境变量
- 在 Vercel Dashboard 中配置

### 3. 自定义域名
- 在 Vercel Dashboard → Settings → Domains
- 添加自己的域名

### 4. HTTPS
- Vercel 自动提供 SSL 证书
- 无需额外配置

---

## 📞 获取帮助

- **Vercel 文档**: https://vercel.com/docs
- **FastAPI 文档**: https://fastapi.tiangolo.com
- **项目 Issue**: GitHub Issues
- **社区论坛**: Vercel Community

---

## ✅ 部署成功标志

部署成功后，您应该能够：

1. ✅ 访问分配的 Vercel URL
2. ✅ 看到抽奖系统首页
3. ✅ 登录并执行抽奖
4. ✅ 访问管理后台查看数据
5. ✅ API 文档页面正常显示

**恭喜！您的抽奖系统已成功部署到 Vercel！** 🎉
