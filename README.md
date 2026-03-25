# 🎉 幸运大抽奖系统

一个功能完整的 Web 抽奖应用，支持证件号码登录，每个人只能抽一次奖。

## ✨ 功能特性

### 用户端功能
- ✅ **证件登录**：支持中国身份证或国际证件号码 + 姓名登录
- ✅ **一次性抽奖**：每个用户只能抽奖一次，防止重复参与
- ✅ **实时结果显示**：抽奖后立即显示获奖结果
- ✅ **响应式设计**：适配手机、平板、电脑等各种设备

### 管理后台功能
- ✅ **奖项配置**：可自定义奖项名称、中奖率、人数上限
- ✅ **数据统计**：实时查看总抽奖次数、已发出奖项、参与用户数
- ✅ **进度监控**：可视化显示各奖项的中奖进度
- ✅ **系统重置**：一键清空所有抽奖记录，重新开始

## 🚀 快速开始

### 1. 安装依赖

```bash
cd Lottery
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

### 3. 访问页面

- **用户抽奖页面**: http://localhost:5000/
- **管理后台**: http://localhost:5000/admin

## 📱 使用说明

### 用户抽奖流程

1. **输入证件信息**
   - 证件号码：支持中国 18 位身份证或其他国际证件号码
   - 姓名：输入您的真实姓名

2. **开始抽奖**
   - 登录后自动进入抽奖页面
   - 点击"开始抽奖"按钮

3. **查看结果**
   - 系统根据预设概率随机分配奖项
   - 显示获奖结果

### 管理后台操作

1. **查看统计数据**
   - 总抽奖次数
   - 已发出奖项数量
   - 参与用户数

2. **配置奖项**
   - 点击"编辑"修改奖项信息
   - 调整中奖率（0.01 = 1%）
   - 设置人数上限
   - 点击"保存配置"生效

3. **重置系统**
   - 点击"重置抽奖系统"
   - 清空所有用户抽奖记录
   - 重置奖项计数

## ⚙️ 奖项配置说明

默认奖项配置：
- **一等奖**：1% 概率，最多 10 人
- **二等奖**：5% 概率，最多 50 人
- **三等奖**：10% 概率，最多 100 人
- **参与奖**：84% 概率，最多 1000 人

## 🔧 部署到服务器

### 局域网共享

在服务器上运行：
```bash
python app.py
```

其他设备通过 `http://服务器 IP:5000` 访问

### 生产环境部署

建议使用 Gunicorn 或 uWSGI 部署：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📁 文件结构

```
Lottery/
├── app.py              # Flask 后端服务
├── index.html          # 用户抽奖页面
├── admin.html          # 管理后台页面
├── requirements.txt    # Python 依赖
├── README.md          # 使用文档
└── lottery_data.json  # 数据文件（自动生成）
```

## 📋 获奖名单

| 序号 | 姓名 | 证件号码 | 奖项 | 抽奖时间 |
|------|------|----------|------|----------|
| 1 | 张三 | 123456789012345678 | - | - |
| 2 | John Smith | A123456789 | - | - |
| 3 | 李四 | 110105199001011234 | - | - |
| 4 | Maria Garcia | X987654321 | - | - |
| 5 | 王五 | 310101198512121234 | - | - |

## 🔐 安全提示

1. **证件号码验证**：当前仅验证非空，支持中国身份证和国际证件
   - 可根据需要添加更严格的校验规则

2. **会话管理**：使用 Flask session 存储用户状态
   - 生产环境请设置复杂的 `secret_key`

3. **测试数据**：以上测试用例仅用于功能测试，实际使用时请使用真实身份信息

## 🛠️ 自定义扩展

### 添加短信验证码

在 `app.py` 的 `/api/login` 接口中集成短信服务：

```python
# 示例：阿里云短信服务
from aliyunsdkcore.client import AcsClient
from aliyunsdksms.request.v20180501 import SendSmsRequest

def send_sms(phone, code):
    client = AcsClient('AccessKey', 'Secret', 'cn-hangzhou')
    request = SendSmsRequest()
    request.set_PhoneNumbers(phone)
    request.set_SignName('您的签名')
    request.set_TemplateCode('您的模板')
    request.set_TemplateParam(f'{{"code":"{code}"}}')
    response = client.do_action_with_exception(request)
    return response
```

### 修改概率算法

在 `app.py` 的 `/api/draw` 接口中调整抽奖逻辑

## 📞 技术支持

如有问题，请检查：
1. Python 版本（建议 3.8+）
2. 依赖包是否正确安装
3. 端口 5000 是否被占用

## 📄 License

MIT License
