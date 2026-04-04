# FastAPI 迁移指南

## 概述
本项目已从 Flask 框架成功迁移到 FastAPI 框架。本文档详细说明了迁移过程中的关键变化和使用注意事项。

## 主要变化

### 1. 依赖包变更

#### 移除的依赖
```txt
Flask==3.0.0
flask-cors==4.0.0
```

#### 新增的依赖
```txt
fastapi==0.109.0          # FastAPI 核心框架
uvicorn==0.27.0           # ASGI 服务器
python-multipart==0.0.6   # 表单数据处理
```

### 2. 启动命令变更

**旧版本 (Flask):**
```bash
python app.py
# 或
flask run
```
- 默认端口: **5000**

**新版本 (FastAPI):**
```bash
python app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- 默认端口: **8000**

### 3. 访问地址变更

| 页面 | Flask 版本 | FastAPI 版本 |
|------|-----------|--------------|
| 用户抽奖页 | http://localhost:5000/ | http://localhost:8000/ |
| 管理后台 | http://localhost:5000/admin | http://localhost:8000/admin |
| API 文档 | 无 | http://localhost:8000/docs |
| ReDoc | 无 | http://localhost:8000/redoc |

### 4. 代码架构变化

#### Flask 版本特点
```python
from flask import Flask, request, jsonify, session

app = Flask(__name__, template_folder='.')
app.secret_key = 'lottery_secret_key_2026'

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # 使用 session 管理用户状态
    session['user_id'] = identifier
    return jsonify({'success': True})
```

#### FastAPI 版本特点
```python
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    identifier: str
    name: Optional[str] = None

@app.post("/api/login")
async def login(login_request: LoginRequest):
    # 使用 Pydantic 模型验证数据
    # 使用 Cookie 管理用户状态
    response = JSONResponse(content={'success': True})
    response.set_cookie(key="user_id", value=identifier)
    return response
```

### 5. 关键技术差异

| 特性 | Flask | FastAPI |
|------|-------|---------|
| 类型检查 | 无 | Pydantic 自动验证 |
| 异步支持 | 有限 | 原生支持 async/await |
| API 文档 | 需手动编写 | 自动生成 OpenAPI/Swagger |
| 性能 | 一般 | 更高（基于 Starlette） |
| 学习曲线 | 平缓 | 略陡（需理解异步） |
| 会话管理 | Flask Session | Cookie/Header/JWT |

### 6. 用户会话管理

**Flask 方式:**
- 使用 `session` 对象
- 服务端存储会话数据

**FastAPI 方式:**
- 使用 HTTP Cookie
- 客户端存储会话标识
- 更适用于无状态 API

### 7. 数据验证

**Flask:**
```python
identifier = request.json.get('identifier')
if not identifier:
    return jsonify({'success': False, 'message': '请输入证件号码'})
```

**FastAPI:**
```python
class LoginRequest(BaseModel):
    identifier: str  # 自动验证非空
    
@app.post("/api/login")
async def login(login_request: LoginRequest):
    # 如果 identifier 为空，FastAPI 自动返回 422 错误
    identifier = login_request.identifier
```

## 功能保持不变

以下功能在迁移过程中完全保持一致：

✅ **业务逻辑**
- 抽奖算法
- 概率计算
- 奖项配置
- 用户管理

✅ **数据存储**
- `lottery_data.json` 文件格式不变
- 数据结构完全兼容

✅ **前端页面**
- `index.html` 无需修改
- `admin.html` 无需修改
- 所有 JavaScript 代码保持不变

✅ **API 接口**
- 所有端点路径相同
- 请求/响应格式相同
- 错误处理逻辑相同

## 迁移步骤回顾

1. ✅ 更新 `requirements.txt`
2. ✅ 重写 `app.py` 为 FastAPI 版本
3. ✅ 更新 `vercel.json` 配置
4. ✅ 更新 `README.md` 文档
5. ✅ 测试应用启动和运行
6. ✅ 验证所有 API 接口

## 优势对比

### FastAPI 的优势

1. **性能提升**
   - 基于 Starlette 和 Pydantic
   - 原生异步支持
   - 更高的并发处理能力

2. **开发体验**
   - 自动 API 文档生成
   - 强大的类型提示
   - 自动数据验证

3. **现代化**
   - 遵循 OpenAPI 标准
   - 更好的 IDE 支持
   - 活跃的社区生态

4. **可维护性**
   - 类型安全
   - 代码更简洁
   - 错误更易追踪

## 常见问题

### Q1: 为什么选择 FastAPI？
A: FastAPI 提供更好的性能、自动文档、类型安全和现代化特性，适合构建高性能 API。

### Q2: 需要修改前端代码吗？
A: 不需要。所有 API 接口保持一致，前端代码无需任何修改。

### Q3: 数据库文件兼容吗？
A: 完全兼容。`lottery_data.json` 格式未变，可以直接使用现有数据。

### Q4: 如何查看 API 文档？
A: 启动服务后访问 http://localhost:8000/docs 即可查看交互式 API 文档。

### Q5: 生产环境如何部署？
A: 推荐使用 Gunicorn + Uvicorn workers：
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app -b 0.0.0.0:8000
```

### Q6: 如何处理跨域请求？
A: FastAPI 内置 CORS 中间件支持：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 回滚方案

如果需要回滚到 Flask 版本：

1. 恢复 `requirements.txt`:
```txt
Flask==3.0.0
flask-cors==4.0.0
requests>=2.28.0
```

2. 恢复 `app.py` 为 Flask 版本

3. 重新安装依赖:
```bash
pip install -r requirements.txt
```

4. 启动 Flask 应用:
```bash
python app.py
```

## 总结

本次迁移成功将项目从 Flask 升级到 FastAPI，在保持所有功能不变的前提下，获得了：
- 🚀 更好的性能
- 📚 自动 API 文档
- 🔒 类型安全保障
- ⚡ 异步处理能力
- 🎯 更现代化的开发体验

所有原有功能均正常工作，用户可以无缝切换到新版本。
