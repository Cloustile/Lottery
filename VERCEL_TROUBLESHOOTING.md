# Vercel 部署故障排查指南

## 🔍 常见部署失败原因及解决方案

### 问题 1：构建失败 - "Build Failed"

**症状：**
```
Error: Build failed with exit code 1
```

**可能原因：**
1. requirements.txt 中有无效的包
2. Python 版本不兼容
3. 依赖包安装失败

**解决方案：**

#### 检查 requirements.txt
```txt
# 确保格式正确，每行一个包
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
requests>=2.28.0
```

#### 指定 Python 版本
已创建以下文件：
- `.python-version` → `3.11`
- `runtime.txt` → `python-3.11`

#### 查看构建日志
```bash
vercel logs <deployment-url>
```

---

### 问题 2：运行时错误 - "Internal Server Error"

**症状：**
页面显示 500 错误

**可能原因：**
1. app.py 有语法错误
2. 导入模块失败
3. 初始化代码出错

**解决方案：**

#### 本地测试
```bash
# 确保本地可以正常运行
python app.py

# 访问 http://localhost:8000 测试
```

#### 检查导入
```bash
python -c "from app import app; print('OK')"
```

---

### 问题 3：文件写入失败

**症状：**
```
PermissionError: [Errno 13] Permission denied: 'lottery_data.json'
```

**原因：**
Vercel 文件系统在运行时是**只读**的

**解决方案：**
✅ 已修复！修改了 `save_data()` 函数，添加异常处理：
```python
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告：保存失败（Vercel 环境正常）: {e}")
        pass
```

⚠️ **重要提示：** 
- Vercel 上数据无法持久化
- 每次部署后数据会重置
- 适合短期演示，不适合长期运行

---

### 问题 4：路由配置错误

**症状：**
访问页面显示 404

**检查 vercel.json：**
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

---

### 问题 5：依赖冲突

**症状：**
```
ERROR: Cannot install ...
```

**解决方案：**

#### 清理并重新安装
```bash
# 删除虚拟环境（如果有）
rm -rf venv/

# 重新安装
pip install -r requirements.txt
```

#### 检查包兼容性
```bash
pip check
```

---

## 🛠️ 调试步骤

### 步骤 1：本地验证

```bash
# 1. 检查 Python 版本
python --version
# 应该是 3.8+

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试导入
python -c "from app import app; print('✅ 导入成功')"

# 4. 启动服务
python app.py

# 5. 测试所有功能
# - 访问 http://localhost:8000/
# - 访问 http://localhost:8000/admin
# - 访问 http://localhost:8000/docs
```

### 步骤 2：检查文件完整性

确保以下文件存在：
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `vercel.json`
- ✅ `.python-version` 或 `runtime.txt`
- ✅ `index.html`
- ✅ `admin.html`
- ✅ `lottery_data.json`

### 步骤 3：查看 Vercel 日志

```bash
# 获取最新的部署 URL
vercel ls

# 查看构建日志
vercel logs <deployment-url>

# 实时查看日志
vercel logs <deployment-url> --follow
```

### 步骤 4：使用预览部署测试

```bash
# 不要直接部署到生产环境
vercel

# 测试预览部署
# 如果成功，再部署到生产
vercel --prod
```

---

## 📋 部署检查清单

部署前确认：

- [ ] Python 版本 >= 3.8
- [ ] 所有依赖在 requirements.txt 中
- [ ] 本地可以正常运行 `python app.py`
- [ ] vercel.json 配置正确
- [ ] .python-version 或 runtime.txt 存在
- [ ] lottery_data.json 存在且格式正确
- [ ] 没有语法错误（`python -m py_compile app.py`）

---

## 🔧 快速修复命令

### 重新部署
```bash
# 清除缓存并重新部署
vercel --force

# 或者
rm -rf .vercel
vercel --prod
```

### 回滚到上一个版本
```bash
vercel rollback
```

### 查看项目信息
```bash
vercel inspect
```

---

## 💡 最佳实践

### 1. 使用预览环境测试
```bash
# 先部署到预览
vercel

# 测试通过后
vercel --prod
```

### 2. 分支策略
- `main` 分支 → 生产环境
- `dev` 分支 → 预览环境

### 3. 环境变量
敏感信息使用 Vercel Dashboard 配置：
```
Settings → Environment Variables
```

### 4. 监控部署
```bash
# 设置别名
vercel alias set <deployment-url> my-lottery.vercel.app
```

---

## 🆘 仍然失败？

### 收集以下信息：

1. **完整的错误日志**
   ```bash
   vercel logs <deployment-url> > error.log
   ```

2. **Python 版本**
   ```bash
   python --version
   ```

3. **依赖列表**
   ```bash
   pip list
   ```

4. **项目结构**
   ```bash
   tree -L 2
   ```

5. **vercel.json 内容**
   ```bash
   cat vercel.json
   ```

### 联系支持

- Vercel Discord: https://vercel.community
- GitHub Issues: 提交详细错误信息

---

## ✅ 成功标志

部署成功后应该看到：

```
🔍  Inspect: https://vercel.com/...
✅  Production: https://your-project.vercel.app
```

访问以下地址测试：
- ✅ https://your-project.vercel.app/
- ✅ https://your-project.vercel.app/admin
- ✅ https://your-project.vercel.app/docs

---

## 🎯 针对本项目的特殊说明

### Vercel 的限制

由于 Vercel 是无状态平台：

1. **数据不会持久化**
   - 每次部署后数据重置
   - 不同请求可能在不同实例

2. **文件系统只读**
   - 可以读取 lottery_data.json
   - 无法写入修改

3. **适用场景**
   - ✅ 短期活动（1-7天）
   - ✅ 功能演示
   - ✅ 测试环境
   - ❌ 长期运行的生产环境

### 如果需要数据持久化

建议迁移到：
- **Render.com**（推荐，免费，支持文件存储）
- **Railway.app**（简单，提供数据库）
- **传统云服务器**（完全控制）

需要帮助迁移吗？请告知！
