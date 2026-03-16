from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import random
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
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

# 验证身份证号（简化版）
def validate_id_card(id_card):
    if len(id_card) == 18:
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
    login_type = req_data.get('type')  # 'id_card' or 'phone'
    identifier = req_data.get('identifier')
    
    # 验证格式
    if login_type == 'id_card':
        if not validate_id_card(identifier):
            return jsonify({'success': False, 'message': '身份证号格式不正确'})
    elif login_type == 'phone':
        if not validate_phone(identifier):
            return jsonify({'success': False, 'message': '手机号格式不正确'})
        # 这里可以添加短信验证码功能
        code = req_data.get('code')
        if not code:
            return jsonify({'success': False, 'message': '请输入验证码'})
        # 简化处理：验证码固定为 123456（生产环境需要对接短信服务）
        if code != '123456':
            return jsonify({'success': False, 'message': '验证码错误'})
    
    # 检查用户是否已存在
    if identifier not in data['users']:
        data['users'][identifier] = {
            'name': req_data.get('name', '用户'),
            'login_type': login_type,
            'has_drawn': False,
            'prize': None,
            'draw_time': None
        }
        save_data(data)
    
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
    return jsonify({
        'success': True,
        'prizes': data['prizes'],
        'total_draws': data['total_draws']
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

if __name__ == '__main__':
    init_data()
    print('抽奖系统已启动！')
    print('用户抽奖页面：http://localhost:5000/')
    print('管理后台：http://localhost:5000/admin')
    app.run(debug=True, host='0.0.0.0', port=5000)
