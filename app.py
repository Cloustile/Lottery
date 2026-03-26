from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import random
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__, template_folder='.')
app.secret_key = 'lottery_secret_key_2026'  # 生产环境请修改为随机密钥
CORS(app)

# 数据文件路径
DATA_FILE = 'lottery_data.json'

# 加载数据
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': {},  # 用户数据 {身份证号/手机号：{name, login_type, has_drawn, prize}}
        'prizes': [],  # 奖项配置 [{name, rate, max_count, current_count}]
        'total_draws': 0
    }

# 保存数据
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# 验证身份证号（简化版，去掉长度限制以支持国际证件）
def validate_id_card(id_card):
    # 只要求非空即可
    if id_card and len(id_card) > 0:
        return True
    return False

# 验证手机号（简化版）
def validate_phone(phone):
    if len(phone) == 11 and phone.startswith('1'):
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = load_data()
    req_data = request.json
    identifier = req_data.get('identifier')
    
    # 验证证件号码格式（简化验证，只要求非空）
    if not identifier or len(identifier) == 0:
        return jsonify({'success': False, 'message': '请输入证件号码'})
    
    # 检查用户是否已存在
    if identifier not in data['users']:
        return jsonify({
            'success': False, 
            'message': '信息不匹配，该用户不存在'
        })
    
    session['user_id'] = identifier
    return jsonify({
        'success': True, 
        'message': '登录成功',
        'has_drawn': data['users'][identifier]['has_drawn'],
        'prize': data['users'][identifier]['prize']
    })

@app.route('/api/draw', methods=['POST'])
def draw():
    data = load_data()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'})
    
    user = data['users'].get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    if user['has_drawn']:
        return jsonify({'success': False, 'message': '您已经抽过奖了'})
    
    # 执行抽奖
    prizes = data['prizes']
    total_rate = sum(p['rate'] for p in prizes)
    
    # 检查是否还有名额
    available_prizes = [p for p in prizes if p['current_count'] < p['max_count']]
    if not available_prizes:
        return jsonify({'success': False, 'message': '所有奖项已抽完'})
    
    # 根据概率抽取
    rand = random.random() * total_rate
    cumulative = 0
    won_prize = None
    
    for prize in available_prizes:
        cumulative += prize['rate']
        if rand <= cumulative and prize['current_count'] < prize['max_count']:
            won_prize = prize
            break
    
    if not won_prize:
        won_prize = available_prizes[-1]  # 默认给最后一个奖项
    
    # 更新用户状态
    user['has_drawn'] = True
    user['prize'] = won_prize['name']
    user['draw_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    won_prize['current_count'] += 1
    data['total_draws'] += 1
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'prize': won_prize['name'],
        'message': f'恭喜您获得{won_prize["name"]}！'
    })

@app.route('/api/prizes', methods=['GET'])
def get_prizes():
    data = load_data()
    
    # 计算统计数据
    total_users = len(data['users'])  # 总用户数
    participated_users = sum(1 for user in data['users'].values() if user.get('has_drawn'))  # 已参与用户数
    
    return jsonify({
        'success': True,
        'prizes': data['prizes'],
        'total_draws': data['total_draws'],
        'total_users': total_users,
        'participated_users': participated_users
    })

@app.route('/api/prizes', methods=['POST'])
def update_prizes():
    data = load_data()
    new_prizes = request.json.get('prizes')
    
    # 更新奖项配置
    for i, prize in enumerate(new_prizes):
        if i < len(data['prizes']):
            data['prizes'][i]['name'] = prize['name']
            data['prizes'][i]['rate'] = float(prize['rate'])
            data['prizes'][i]['max_count'] = int(prize['max_count'])
    
    save_data(data)
    return jsonify({'success': True, 'message': '奖项配置已更新'})

@app.route('/api/winners', methods=['GET'])
def get_winners():
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
    winners.sort(key=lambda x: x['draw_time'])
    
    return jsonify({
        'success': True,
        'winners': winners,
        'total': len(winners)
    })

@app.route('/api/reset', methods=['POST'])
def reset_lottery():
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
    
    return jsonify({'success': True, 'message': '抽奖系统已重置'})

@app.route('/api/users/import', methods=['POST'])
def import_users():
    """批量导入用户"""
    data = load_data()
    req_data = request.json
    users_data = req_data.get('users', [])
    
    if not users_data:
        return jsonify({'success': False, 'message': '请提供用户数据'})
    
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
    
    return jsonify({
        'success': True,
        'message': message,
        'success_count': success_count,
        'skip_count': skip_count
    })

@app.route('/api/users', methods=['GET'])
def get_users():
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
    
    return jsonify({
        'success': True,
        'users': users_list,
        'total': len(users_list)
    })

if __name__ == '__main__':
    init_data()
    print('抽奖系统已启动！')
    print('用户抽奖页面：http://localhost:5000/')
    print('管理后台：http://localhost:5000/admin')
    app.run(debug=True, host='0.0.0.0', port=5000)
