# -*- coding: utf-8 -*-
"""
抽奖系统自动化测试脚本
用于模拟大量用户登录并验证实际概率是否符合设定概率
"""

import requests
import random
from collections import Counter
import sys


BASE_URL = 'http://localhost:5000'


class LotteryTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.test_users = []
        
    def get_all_users_from_db(self):
        """从数据库获取所有用户"""
        try:
            response = self.session.get(f'{BASE_URL}/api/users')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('users', [])
        except Exception as e:
            print(f"获取用户列表失败：{e}")
        return []
    
    def generate_test_user(self, index):
        """生成测试用户数据（备用方案）"""
        id_card = f'{random.randint(100000000000000000, 999999999999999999)}'
        name = f'测试用户{index}'
        return {
            'identifier': id_card,
            'name': name
        }
    
    def login_and_draw(self, user_index):
        """模拟用户登录并抽奖"""
        # 优先使用数据库中的真实用户
        if self.test_users and user_index <= len(self.test_users):
            user = {
                'identifier': self.test_users[user_index - 1]['identifier'],
                'name': self.test_users[user_index - 1]['name']
            }
        else:
            # 备用方案：生成测试用户
            user = self.generate_test_user(user_index)
        
        try:
            # 登录
            login_response = self.session.post(f'{BASE_URL}/api/login', json=user)
            login_data = login_response.json()
            
            if not login_data.get('success'):
                return None, f"登录失败：{login_data.get('message')}"
            
            # 检查是否已抽奖
            if login_data.get('has_drawn'):
                return None, f"用户已抽奖，跳过（奖项：{login_data.get('prize')})"
            
            # 抽奖
            draw_response = self.session.post(f'{BASE_URL}/api/draw')
            draw_data = draw_response.json()
            
            if not draw_data.get('success'):
                return None, f"抽奖失败：{draw_data.get('message')}"
            
            return draw_data.get('prize'), None
            
        except Exception as e:
            return None, f"请求异常：{str(e)}"
    
    def get_prizes_config(self):
        """获取当前奖项配置"""
        try:
            response = self.session.get(f'{BASE_URL}/api/prizes')
            if response.status_code == 200:
                data = response.json()
                return data.get('prizes', [])
        except Exception as e:
            print(f"获取奖项配置失败：{e}")
        return []
    
    def run_test(self, num_users):
        """执行测试"""
        print(f"\n🚀 开始测试，模拟 {num_users} 个用户登录抽奖...\n")
        
        # 从数据库获取所有用户
        all_users = self.get_all_users_from_db()
        
        if not all_users:
            print("❌ 数据库中没有用户，请先通过管理后台导入用户")
            print("\n💡 操作提示：")
            print("   1. 访问 http://localhost:5000/admin")
            print("   2. 点击'批量导入用户'按钮")
            print("   3. 输入用户数据（格式：身份证号，姓名）")
            print("   4. 确认导入后重新运行测试")
            return
        
        print(f"📊 数据库中共有 {len(all_users)} 个用户")
        
        # 筛选未抽奖的用户
        available_users = [u for u in all_users if not u.get('has_drawn')]
        print(f"✅ 可用未抽奖用户：{len(available_users)} 个")
        
        if len(available_users) == 0:
            print("\n⚠️  所有用户都已参与过抽奖！")
            print("💡 解决方案：")
            print("   1. 重置系统（管理后台 -> 重置抽奖系统）")
            print("   2. 或删除部分已抽奖用户（点击删除按钮）")
            print("   3. 或导入更多新用户")
            return
        
        # 确定实际测试的用户数量
        actual_num = min(num_users, len(available_users))
        if actual_num < num_users:
            print(f"\n⚠️  指定用户数 ({num_users}) 超过可用用户数 ({len(available_users)})，将使用全部可用用户")
        
        # 随机选择用户（如果需要的数量少于可用数量）
        if len(available_users) > actual_num:
            selected_users = random.sample(available_users, actual_num)
        else:
            selected_users = available_users
        
        self.test_users = selected_users
        
        # 获取当前奖项配置
        prizes = self.get_prizes_config()
        if not prizes:
            print("❌ 无法获取奖项配置，请确保服务已启动")
            return
        
        print("\n📋 当前奖项配置：")
        for prize in prizes:
            remaining = prize['max_count'] - prize.get('current_count', 0)
            print(f"   - {prize['name']}: 概率={prize['rate']*100:.1f}%, "
                  f"总数={prize['max_count']}, 已中={prize.get('current_count', 0)}, "
                  f"剩余={remaining}")
        print()
        
        # 执行抽奖
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        for i in range(actual_num):
            prize, error = self.login_and_draw(i + 1)
            
            if error:
                if "已抽奖" in error or "跳过" in error:
                    skip_count += 1
                    if i < 10 or i % 100 == 0:
                        print(f"⏭️  用户{i+1}: {error}")
                else:
                    fail_count += 1
                    if i < 10 or i % 100 == 0:
                        print(f"❌ 用户{i+1}: {error}")
            else:
                success_count += 1
                self.results.append(prize)
                if i < 10:
                    print(f"✅ 用户{i+1} ({selected_users[i]['name']}): 获得 [{prize}]")
            
            # 进度显示
            if (i + 1) % 100 == 0:
                print(f"⏳ 已完成 {i+1}/{actual_num} 个用户...")
        
        print(f"\n✅ 测试完成！成功：{success_count}, 失败：{fail_count}, 跳过：{skip_count}\n")
        
        # 统计分析
        self.analyze_results(prizes)
    
    def analyze_results(self, prizes):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有有效的抽奖结果")
            return
        
        result_counter = Counter(self.results)
        total = len(self.results)
        
        print("=" * 80)
        print("📈 测试结果统计分析")
        print("=" * 80)
        print(f"{'奖项名称':<15} {'设定概率':<12} {'实际概率':<12} {'中奖次数':<10} {'理论次数':<10} {'偏差率':<10}")
        print("-" * 80)
        
        total_theoretical_rate = sum(p['rate'] for p in prizes)
        
        for prize in prizes:
            name = prize['name']
            theoretical_rate = prize['rate'] / total_theoretical_rate * 100 if total_theoretical_rate > 0 else 0
            actual_count = result_counter.get(name, 0)
            actual_rate = (actual_count / total * 100) if total > 0 else 0
            theoretical_count = total * theoretical_rate / 100
            deviation = ((actual_rate - theoretical_rate) / theoretical_rate * 100) if theoretical_rate > 0 else 0
            
            print(f"{name:<15} {theoretical_rate:>10.2f}%  {actual_rate:>10.2f}%  {actual_count:>8}   {theoretical_count:>8.1f}   {deviation:>+8.2f}%")
        
        print("-" * 80)
        print(f"{'总计':<15} {'100.00%':<12} {'100.00%':<12} {total:>8}   {total:>8.1f}   {'--':<10}")
        print("=" * 80)
        
        # 边界情况分析
        print("\n🔍 边界情况分析:")
        
        for prize in prizes:
            actual_count = result_counter.get(prize['name'], 0)
            if actual_count > prize['max_count']:
                print(f"   ⚠️  {prize['name']} 超出最大限制！实际：{actual_count}, 限制：{prize['max_count']}")
        
        zero_rate_prizes = [p for p in prizes if p['rate'] == 0]
        if zero_rate_prizes:
            for prize in zero_rate_prizes:
                actual_count = result_counter.get(prize['name'], 0)
                if actual_count > 0:
                    print(f"   ⚠️  {prize['name']} 概率为 0 但仍有中奖！实际中奖：{actual_count}次")
                else:
                    print(f"   ✅ {prize['name']} 概率为 0，未中奖（符合预期）")
        
        # 卡方检验
        print("\n📊 概率拟合度评估（卡方检验简化版）:")
        chi_square = 0
        for prize in prizes:
            name = prize['name']
            theoretical_rate = prize['rate'] / total_theoretical_rate * 100 if total_theoretical_rate > 0 else 0
            actual_count = result_counter.get(name, 0)
            expected_count = total * theoretical_rate / 100
            if expected_count > 0:
                chi_square += ((actual_count - expected_count) ** 2) / expected_count
        
        degrees_of_freedom = len(prizes) - 1
        critical_value = 7.815 if degrees_of_freedom >= 3 else 5.991
        
        if chi_square < critical_value:
            print(f"   ✅ 卡方值={chi_square:.2f} < {critical_value}，实际概率与设定概率吻合度良好！")
        else:
            print(f"   ⚠️  卡方值={chi_square:.2f} > {critical_value}，实际概率与设定概率存在显著差异！")
        
        print()


def main():
    print("=" * 80)
    print("🎰 抽奖系统自动化概率测试工具")
    print("=" * 80)
    
    tester = LotteryTester()
    
    # 检查服务是否可用
    try:
        response = requests.get(f'{BASE_URL}/api/prizes', timeout=5)
        if response.status_code != 200:
            print(f"❌ 服务响应异常：{response.status_code}")
            print("请确保 Flask 服务已启动：python app.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到抽奖服务")
        print("请确保 Flask 服务已启动：python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        sys.exit(1)
    
    print("\n✅ 服务连接成功")
    
    # 显示数据库用户统计
    all_users = tester.get_all_users_from_db()
    if all_users:
        total_users = len(all_users)
        available_users = sum(1 for u in all_users if not u.get('has_drawn'))
        print(f"\n📊 数据库用户统计:")
        print(f"   - 总用户数：{total_users}")
        print(f"   - 未抽奖用户：{available_users}")
        print(f"   - 已抽奖用户：{total_users - available_users}")
    else:
        print("\n⚠️  数据库中暂无用户，请先导入用户后再进行测试")
    
    while True:
        try:
            user_input = input("\n请输入要模拟的用户数量 (输入 q 退出): ")
            if user_input.lower() == 'q':
                print("👋 退出测试")
                sys.exit(0)
            
            num_users = int(user_input)
            if num_users <= 0:
                print("❌ 用户数量必须大于 0")
                continue
            
            break
        except ValueError:
            print("❌ 请输入有效的整数")
    
    tester.run_test(num_users)
    
    while True:
        cont = input("\n是否继续测试？(y/n): ").lower()
        if cont == 'y':
            while True:
                try:
                    user_input = input("请输入要模拟的用户数量：")
                    num_users = int(user_input)
                    if num_users <= 0:
                        print("❌ 用户数量必须大于 0")
                        continue
                    tester.run_test(num_users)
                    break
                except ValueError:
                    print("❌ 请输入有效的整数")
        elif cont == 'n':
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("❌ 请输入 y 或 n")


if __name__ == '__main__':
    main()
