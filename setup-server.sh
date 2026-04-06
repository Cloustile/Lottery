#!/bin/bash
# 服务器初始化脚本 - 在服务器上首次部署时运行

set -e

echo "========================================="
echo "  Lottery 项目服务器初始化"
echo "========================================="
echo ""

# 配置变量
DEPLOY_USER="root"
DEPLOY_PATH="/usr/local/nginx/html"
APP_PORT=8000

echo "📋 步骤 1: 创建部署目录"
mkdir -p $DEPLOY_PATH
cd $DEPLOY_PATH

echo "📋 步骤 2: 安装系统依赖"
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv rsync

echo "📋 步骤 3: 安装 Python 依赖"
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
else
    echo "⚠️  warning: requirements.txt not found"
fi

echo "📋 步骤 4: 配置 systemd 服务"
# 复制服务文件
if [ -f lottery.service ]; then
    sudo cp lottery.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable lottery.service
    echo "✅ Systemd service configured"
else
    echo "⚠️  Warning: lottery.service not found, skipping systemd setup"
fi

echo "📋 步骤 5: 配置防火墙"
sudo ufw allow $APP_PORT/tcp 2>/dev/null || true
echo "✅ Port $APP_PORT opened"

echo "📋 步骤 6: 启动服务"
if systemctl is-active --quiet lottery.service 2>/dev/null; then
    sudo systemctl restart lottery.service
    echo "✅ Service restarted"
else
    sudo systemctl start lottery.service
    echo "✅ Service started"
fi

echo ""
echo "========================================="
echo "  ✅ 初始化完成！"
echo "========================================="
echo ""
echo "📊 服务状态:"
systemctl status lottery.service --no-pager -l || true
echo ""
echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}'):$APP_PORT"
echo "📝 日志文件: $DEPLOY_PATH/lottery.log"
echo "🔧 管理命令:"
echo "   - 查看状态: sudo systemctl status lottery.service"
echo "   - 重启服务: sudo systemctl restart lottery.service"
echo "   - 查看日志: tail -f $DEPLOY_PATH/lottery.log"
echo ""
