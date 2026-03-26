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
        
    def generate_test_user(self, index):
        """生成测试用户数据"""
        id_card = f'{random.randint(100000000000000000, 999999999999999999)}'
        name = f'测试用户{index}'
        return {
            'identifier': id_card,
            'name': name
        }
    
    def login_and_draw(self, user_index):
        """模拟用户登录并抽奖"""
        user = self.generate_test_user(user_index)
        
        try:
            # 登录
            login_response = self.session.post(f'{BASE_URL}/api/login', json=user)
            login_data = login_response.json()
            
            if not login_data.get('success'):
                return None, f"登录失败：{login_data.get('message')}"
            
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
        
        # 获取当前奖项配置
        prizes = self.get_prizes_config()
        if not prizes:
            print("❌ 无法获取奖项配置，请确保服务已启动")
            return
        
        print("📊 当前奖项配置：")
        for prize in prizes:
            print(f"   - {prize['name']}: 概率={prize['rate']*100:.1f}%, 总数={prize['max_count']}, 已中={prize.get('current_count', 0)}")
        print()
        
        # 执行抽奖
        success_count = 0
        fail_count = 0
        
        for i in range(num_users):
            prize, error = self.login_and_draw(i + 1)
            
            if error:
                fail_count += 1
                if i < 10 or i % 100 == 0:
                    print(f"❌ 用户{i+1}: {error}")
            else:
                success_count += 1
                self.results.append(prize)
                if i < 10:
                    print(f"✅ 用户{i+1}: 获得 [{prize}]")
            
            if (i + 1) % 100 == 0:
                print(f"⏳ 已完成 {i+1}/{num_users} 个用户...")
        
        print(f"\n✅ 测试完成！成功：{success_count}, 失败：{fail_count}\n")
        
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
    
    print("✅ 服务连接成功")
    
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
