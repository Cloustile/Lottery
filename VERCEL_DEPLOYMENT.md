# Vercel 部署指南

## ⚠️ 重要提示

Vercel 是**无状态平台**，这意味着：
- ❌ **无法持久化保存 `lottery_data.json`**
- ❌ 每次部署后数据会重置
- ❌ 不同请求可能在不同实例上运行

## 🎯 解决方案

### 方案 A：仅用于演示/测试（当前配置）
**适用场景：**
- ✅ 短期活动
- ✅ 功能演示
- ✅ 测试环境

**特点：**
- 数据在每次部署后重置
- 适合一次性抽奖活动
- 无需额外配置

**部署步骤：**
```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录 Vercel
vercel login

# 3. 部署项目
cd f:\0-Projects\Lottery
vercel deploy

# 4. 生产环境部署
vercel deploy --prod
```

### 方案 B：使用外部数据库（推荐生产环境）
**适用场景：**
- ✅ 长期运行的活动
- ✅ 需要数据持久化
- ✅ 生产环境

**需要的改造：**
1. 集成 MongoDB Atlas / Supabase / Firebase
2. 修改 `load_data()` 和 `save_data()` 函数
3. 配置环境变量

---

## 📋 当前配置说明

### vercel.json
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
  ],
  "env": {
    "PYTHONUNBUFFERED": "1"
  },
  "functions": {
    "app.py": {
      "maxDuration": 10
    }
  }
}
```

### 配置项说明
- `PYTHONUNBUFFERED`: 确保日志实时输出
- `maxDuration`: 函数最大执行时间（10秒）

---

## 🚀 快速部署步骤

### 方法 1：使用 Vercel CLI（推荐）

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录
vercel login

# 3. 进入项目目录
cd f:\0-Projects\Lottery

# 4. 首次部署
vercel

# 5. 部署到生产环境
vercel --prod
```

### 方法 2：通过 GitHub 集成

1. **推送代码到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **在 Vercel 网站操作**
   - 访问 https://vercel.com
   - 点击 "New Project"
   - 导入 GitHub 仓库
   - 点击 "Deploy"

3. **自动部署**
   - 每次推送到 GitHub 会自动触发部署

---

## 🔧 环境变量配置

如果需要配置敏感信息（如数据库密码），在 Vercel Dashboard 中设置：

1. 进入项目 Settings
2. 找到 "Environment Variables"
3. 添加变量：
   ```
   DATABASE_URL=mongodb+srv://...
   SECRET_KEY=your-secret-key
   ```

4. 在代码中使用：
   ```python
   import os
   db_url = os.environ.get('DATABASE_URL')
   ```

---

## ⚡ 性能优化建议

### 1. 减少冷启动时间
- 保持依赖包最小化
- 避免大型文件

### 2. 缓存策略
```python
# 在内存中缓存数据（注意：仅在单个请求周期内有效）
_data_cache = None

def load_data():
    global _data_cache
    if _data_cache is None:
        # 从文件或数据库加载
        _data_cache = ...
    return _data_cache
```

### 3. 使用 CDN
- Vercel 自动提供全球 CDN
- 静态资源自动缓存

---

## 🐛 常见问题

### Q1: 数据丢失怎么办？
**A:** Vercel 是无状态平台，建议使用外部数据库：
- MongoDB Atlas（免费）
- Supabase（免费）
- Firebase（免费额度）

### Q2: 如何查看日志？
**A:** 
```bash
vercel logs <deployment-url>
```

### Q3: 部署失败怎么办？
**A:** 检查：
1. `requirements.txt` 是否正确
2. Python 版本兼容性
3. 查看构建日志：`vercel logs`

### Q4: 自定义域名？
**A:** 在 Vercel Dashboard → Settings → Domains 中配置

---

## 📊 监控和统计

### 查看部署信息
```bash
# 列出所有部署
vercel ls

# 查看特定部署
vercel inspect <deployment-url>

# 查看日志
vercel logs <deployment-url>
```

### Vercel Dashboard
- 实时流量统计
- 错误日志
- 性能指标
- 域名管理

---

## 🔄 持续部署

### 自动部署流程
```
GitHub Push → Vercel 检测 → 自动构建 → 自动部署
```

### 分支策略
- `main` 分支 → 生产环境
- 其他分支 → 预览环境

---

## 💰 成本说明

### 免费套餐
- ✅ 个人项目完全免费
- ✅ 100 GB 带宽/月
- ✅ 1000 小时 Serverless 函数执行时间
- ✅ 自动 HTTPS

### 付费套餐
- Pro: $20/月
- Business: 联系销售

---

## 🎯 最佳实践

1. **测试后再部署**
   ```bash
   # 本地测试
   python app.py
   
   # 确认无误后部署
   vercel --prod
   ```

2. **使用预览部署**
   ```bash
   # 部署到预览环境
   vercel
   
   # 测试通过后部署到生产
   vercel --prod
   ```

3. **定期备份数据**
   - 如果使用外部数据库，定期导出备份
   - 记录重要统计数据

4. **监控错误**
   - 定期检查 Vercel Dashboard
   - 设置错误告警

---

## 📞 技术支持

- Vercel 文档: https://vercel.com/docs
- FastAPI 文档: https://fastapi.tiangolo.com
- 项目 Issue: GitHub Issues

---

## ⚠️ 重要提醒

**对于抽奖系统这种需要数据持久化的应用，强烈建议：**

1. **短期活动**：可以使用当前配置，活动结束后导出数据
2. **长期活动**：必须集成外部数据库（MongoDB/Supabase等）

如需帮助集成云数据库，请告知！
