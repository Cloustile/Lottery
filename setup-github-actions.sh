#!/bin/bash
# GitHub Actions 快速配置脚本

set -e

echo "========================================="
echo "  GitHub Actions 部署配置助手"
echo "========================================="
echo ""

# 检查参数
if [ $# -lt 2 ]; then
    echo "用法: $0 <服务器IP> <用户名>"
    echo "示例: $0 139.196.201.114 admin"
    exit 1
fi

SERVER_IP=$1
SERVER_USER=$2
SSH_KEY_FILE=~/.ssh/github_actions_deploy

echo "📋 配置信息:"
echo "   服务器: $SERVER_IP"
echo "   用户: $SERVER_USER"
echo "   SSH密钥: $SSH_KEY_FILE"
echo ""

# 步骤 1: 生成 SSH 密钥
if [ ! -f "$SSH_KEY_FILE" ]; then
    echo "🔑 步骤 1: 生成 SSH 密钥对"
    ssh-keygen -t ed25519 -C "github-actions@lottery" -f $SSH_KEY_FILE -N ""
    echo "✅ SSH 密钥已生成"
else
    echo "✅ SSH 密钥已存在"
fi

echo ""

# 步骤 2: 复制公钥到服务器
echo "📤 步骤 2: 将公钥复制到服务器"
echo "请输入 $SERVER_USER@$SERVER_IP 的密码："
ssh-copy-id -i ${SSH_KEY_FILE}.pub ${SERVER_USER}@${SERVER_IP}

if [ $? -eq 0 ]; then
    echo "✅ 公钥已成功添加到服务器"
else
    echo "❌ 公钥添加失败"
    exit 1
fi

echo ""

# 步骤 3: 测试连接
echo "🧪 步骤 3: 测试 SSH 连接"
if ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "echo 'Connection successful'" 2>/dev/null; then
    echo "✅ SSH 连接测试成功"
else
    echo "❌ SSH 连接测试失败"
    exit 1
fi

echo ""

# 步骤 4: 显示私钥内容
echo "📋 步骤 4: 获取私钥内容（用于配置 GitHub Secret）"
echo ""
echo "请复制以下内容，并在 GitHub 仓库设置中添加为 Secret："
echo "Secret 名称: SERVER_SSH_KEY"
echo ""
echo "----------------------------------------"
cat $SSH_KEY_FILE
echo "----------------------------------------"
echo ""

echo "⚠️  重要提示："
echo "1. 妥善保管上述私钥内容"
echo "2. 不要将其分享给他人"
echo "3. 在 GitHub Secrets 中粘贴时，包含完整的 BEGIN 和 END 行"
echo ""

# 步骤 5: 上传初始化脚本
echo "📤 步骤 5: 上传服务器初始化脚本"
scp setup-server.sh ${SERVER_USER}@${SERVER_IP}:/home/admin/

if [ $? -eq 0 ]; then
    echo "✅ 初始化脚本已上传"
    echo ""
    echo "现在请执行以下命令完成服务器初始化："
    echo ""
    echo "ssh ${SERVER_USER}@${SERVER_IP}"
    echo "chmod +x /home/admin/setup-server.sh"
    echo "sudo /home/admin/setup-server.sh"
    echo ""
else
    echo "⚠️  初始化脚本上传失败，请手动上传"
fi

echo ""
echo "========================================="
echo "  ✅ 配置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加 Secret"
echo "   - Name: SERVER_SSH_KEY"
echo "   - Value: (上面显示的私钥内容)"
echo ""
echo "2. 推送代码到 main 分支触发自动部署"
echo "   git add ."
echo "   git commit -m 'Configure auto deployment'"
echo "   git push origin main"
echo ""
echo "3. 在 GitHub Actions 标签页查看部署状态"
echo ""
