from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import json
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(title="幸运大抽奖系统")

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="."), name="static")
templates = Jinja2Templates(directory=".")

# 数据文件路径
DATA_FILE = 'lottery_data.json'

# Pydantic 模型定义
class LoginRequest(BaseModel):
    identifier: str
    name: Optional[str] = None

class PrizeUpdate(BaseModel):
    name: str
    rate: float
    max_count: int
    current_count: Optional[int] = 0

class PrizesUpdateRequest(BaseModel):
    prizes: List[PrizeUpdate]

class UserImportRequest(BaseModel):
    users: List[dict]

class UserDeleteRequest(BaseModel):
    identifier: str

# 加载数据
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"警告：读取数据文件失败: {e}")
    
    # 返回默认数据结构
    return {
        'users': {},  # 用户数据 {身份证号/手机号：{name, login_type, has_drawn, prize}}
        'prizes': [],  # 奖项配置 [{name, rate, max_count, current_count}]
        'total_draws': 0
    }

# 保存数据
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Vercel 环境文件系统只读，忽略写入错误
        print(f"警告：保存数据文件失败（这在 Vercel 等无状态平台是正常的）: {e}")
        pass

# 初始化数据
def init_data():
    data = load_data()
    if not data['prizes']:
        # 默认奖项配置
        data['prizes'] = [
            {'name': '一等奖', 'rate': 0.01, 'max_count': 10, 'current_count': 0},
            {'name': '二等奖', 'rate': 0.05, 'max_count': 50, 'current_count': 0},
            {'name': '三等奖', 'rate': 0.10, 'max_count': 100, 'current_count': 0},
            {'name': '参与奖', 'rate': 0.84, 'max_count': 1000, 'current_count': 0}
        ]
    save_data(data)
    return data

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/login")
async def login(login_request: LoginRequest):
    data = load_data()
    identifier = login_request.identifier
    
    # 验证证件号码格式（简化验证，只要求非空）
    if not identifier or len(identifier) == 0:
        return JSONResponse(content={'success': False, 'message': '请输入证件号码'})
    
    # 检查用户是否已存在
    if identifier not in data['users']:
        return JSONResponse(content={
            'success': False, 
            'message': '信息不匹配，该用户不存在'
        })
    
    user_info = data['users'][identifier]
    
    # 创建响应并设置 Cookie
    response = JSONResponse(content={
        'success': True, 
        'message': '登录成功',
        'has_drawn': user_info['has_drawn'],
        'prize': user_info.get('prize')
    })
    response.set_cookie(key="user_id", value=identifier, httponly=True)
    
    return response

@app.post("/api/draw")
async def draw(request: Request):
    data = load_data()
    
    # 从 Cookie 中获取 user_id
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        return JSONResponse(content={'success': False, 'message': '请先登录'})
    
    user = data['users'].get(user_id)
    if not user:
        return JSONResponse(content={'success': False, 'message': '用户不存在'})
    
    if user['has_drawn']:
        return JSONResponse(content={'success': False, 'message': '您已经抽过奖了'})
    
    # 执行抽奖
    prizes = data['prizes']
    
    # 检查是否还有名额
    available_prizes = [p for p in prizes if p['current_count'] < p['max_count']]
    if not available_prizes:
        return JSONResponse(content={'success': False, 'message': '所有奖项已抽完'})
    
    # 智能抽奖逻辑：如果随机到的奖项已抽完，则自动重抽
    won_prize = None
    max_attempts = 100  # 最多尝试 100 次，防止死循环
    
    for attempt in range(max_attempts):
        # 计算当前可用奖项的总概率
        total_rate = sum(p['rate'] for p in available_prizes)
        
        if total_rate == 0:
            # 如果所有可用奖项概率都为 0，则平均分配
            won_prize = available_prizes[attempt % len(available_prizes)]
            break
        
        # 根据概率抽取
        rand = random.random() * total_rate
        cumulative = 0
        
        for prize in available_prizes:
            cumulative += prize['rate']
            if rand <= cumulative:
                # 检查该奖项是否还有名额
                if prize['current_count'] < prize['max_count']:
                    won_prize = prize
                    break
        
        # 如果成功分配到奖项，退出循环
        if won_prize:
            break
        
        # 如果没有分配到奖项（理论上不应该发生），继续下一次尝试
    
    # 如果多次尝试后仍未分配，强制分配一个可用奖项
    if not won_prize and available_prizes:
        won_prize = available_prizes[-1]
    
    # 更新用户状态
    user['has_drawn'] = True
    user['prize'] = won_prize['name']
    user['draw_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    won_prize['current_count'] += 1
    data['total_draws'] += 1
    
    save_data(data)
    
    return JSONResponse(content={
        'success': True,
        'prize': won_prize['name'],
        'message': f'恭喜您获得{won_prize["name"]}！'
    })

@app.get("/api/prizes")
async def get_prizes():
    data = load_data()
    
    # 计算统计数据
    total_users = len(data['users'])  # 总用户数
    participated_users = sum(1 for user in data['users'].values() if user.get('has_drawn'))  # 已参与用户数
    
    return JSONResponse(content={
        'success': True,
        'prizes': data['prizes'],
        'total_draws': data['total_draws'],
        'total_users': total_users,
        'participated_users': participated_users
    })

@app.post("/api/prizes")
async def update_prizes(prizes_request: PrizesUpdateRequest):
    data = load_data()
    new_prizes = prizes_request.prizes
    
    # 更新奖项配置
    for i, prize in enumerate(new_prizes):
        if i < len(data['prizes']):
            data['prizes'][i]['name'] = prize.name
            data['prizes'][i]['rate'] = float(prize.rate)
            data['prizes'][i]['max_count'] = int(prize.max_count)
            # 保持 current_count 不变
    
    save_data(data)
    return JSONResponse(content={'success': True, 'message': '奖项配置已更新'})

@app.get("/api/winners")
async def get_winners():
    data = load_data()
    
    # 获取所有已抽奖的用户
    winners = []
    for user_id, user_info in data['users'].items():
        if user_info['has_drawn'] and user_info['prize']:
            winners.append({
                'identifier': user_id,
                'name': user_info['name'],
                'prize': user_info['prize'],
                'draw_time': user_info['draw_time']
            })
    
    # 按抽奖时间正序排序（最早的在前）
    winners.sort(key=lambda x: x['draw_time'] if x['draw_time'] else '')
    
    return JSONResponse(content={
        'success': True,
        'winners': winners,
        'total': len(winners)
    })

@app.post("/api/reset")
async def reset_lottery():
    data = load_data()
    # 重置所有用户抽奖状态
    for user_id in data['users']:
        data['users'][user_id]['has_drawn'] = False
        data['users'][user_id]['prize'] = None
        data['users'][user_id]['draw_time'] = None
    
    # 重置奖项计数
    for prize in data['prizes']:
        prize['current_count'] = 0
    
    data['total_draws'] = 0
    save_data(data)
    
    return JSONResponse(content={'success': True, 'message': '抽奖系统已重置'})

@app.post("/api/users/import")
async def import_users(user_import: UserImportRequest):
    """批量导入用户"""
    data = load_data()
    users_data = user_import.users
    
    if not users_data:
        return JSONResponse(content={'success': False, 'message': '请提供用户数据'})
    
    success_count = 0
    skip_count = 0
    error_list = []
    
    for user_info in users_data:
        identifier = user_info.get('identifier', '').strip()
        name = user_info.get('name', '').strip()
        
        # 验证必填字段
        if not identifier or not name:
            error_list.append(f"跳过无效数据：{user_info}")
            continue
        
        # 检查是否已存在
        if identifier in data['users']:
            skip_count += 1
            continue
        
        # 添加新用户
        data['users'][identifier] = {
            'name': name,
            'has_drawn': False,
            'prize': None,
            'draw_time': None
        }
        success_count += 1
    
    save_data(data)
    
    message = f"成功导入 {success_count} 个用户"
    if skip_count > 0:
        message += f"，跳过 {skip_count} 个已存在的用户"
    if error_list:
        message += f"，{len(error_list)} 个错误"
    
    return JSONResponse(content={
        'success': True,
        'message': message,
        'success_count': success_count,
        'skip_count': skip_count
    })

@app.get("/api/users")
async def get_users():
    """获取所有用户列表"""
    data = load_data()
    
    users_list = []
    for user_id, user_info in data['users'].items():
        users_list.append({
            'identifier': user_id,
            'name': user_info['name'],
            'has_drawn': user_info.get('has_drawn', False),
            'prize': user_info.get('prize'),
            'draw_time': user_info.get('draw_time')
        })
    
    # 按姓名排序
    users_list.sort(key=lambda x: x['name'])
    
    return JSONResponse(content={
        'success': True,
        'users': users_list,
        'total': len(users_list)
    })

@app.post("/api/users/delete")
async def delete_user(user_delete: UserDeleteRequest):
    """删除指定用户"""
    data = load_data()
    identifier = user_delete.identifier.strip()
    
    if not identifier:
        return JSONResponse(content={'success': False, 'message': '请提供证件号码'})
    
    # 检查用户是否存在
    if identifier not in data['users']:
        return JSONResponse(content={'success': False, 'message': '用户不存在'})
    
    user = data['users'][identifier]
    
    # 检查用户是否已抽奖
    if user.get('has_drawn'):
        return JSONResponse(content={
            'success': False, 
            'message': '该用户已参与抽奖，不能删除'
        })
    
    # 删除用户
    user_name = user['name']
    del data['users'][identifier]
    save_data(data)
    
    return JSONResponse(content={
        'success': True,
        'message': f'用户 {user_name} 已成功删除'
    })

if __name__ == '__main__':
    init_data()
    print('抽奖系统已启动！')
    print('用户抽奖页面：http://localhost:8000/')
    print('管理后台：http://localhost:8000/admin')
    print('API 文档：http://localhost:8000/docs')
    print('\n提示：终端会显示请求日志，200 OK 表示正常运行')
    print('按 Ctrl+C 停止服务器\n')
    
    import logging
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
else:
    # Vercel 部署时使用
    init_data()
