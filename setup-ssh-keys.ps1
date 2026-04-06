# SSH 公钥配置助手 - Windows PowerShell 版本

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  SSH 公钥配置助手" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$SSH_KEY_PATH = "$env:USERPROFILE\.ssh\github_actions_deploy"
$PUB_KEY_PATH = "$SSH_KEY_PATH.pub"
$SERVER_IP = "139.196.201.114"
$SERVER_USER = "admin"

# 检查密钥文件是否存在
if (-not (Test-Path $SSH_KEY_PATH)) {
    Write-Host "错误: 私钥文件不存在: $SSH_KEY_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "找到 SSH 密钥文件" -ForegroundColor Green
Write-Host "   私钥: $SSH_KEY_PATH" -ForegroundColor Gray
Write-Host "   公钥: $PUB_KEY_PATH" -ForegroundColor Gray
Write-Host ""

# 显示公钥内容
$pubKey = Get-Content $PUB_KEY_PATH
Write-Host "公钥内容:" -ForegroundColor Cyan
Write-Host $pubKey -ForegroundColor White
Write-Host ""

Write-Host "由于服务器禁用了密码登录，请按照以下步骤手动配置：" -ForegroundColor Yellow
Write-Host ""
Write-Host "方法 1: 通过其他已配置的 SSH 方式登录服务器" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "1. 使用您现有的 SSH 密钥或密码登录服务器" -ForegroundColor White
Write-Host "2. 执行以下命令：" -ForegroundColor White
Write-Host ""
Write-Host "   mkdir -p ~/.ssh" -ForegroundColor Cyan
Write-Host "   echo '$pubKey' >> ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "   chmod 700 ~/.ssh" -ForegroundColor Cyan
Write-Host "   chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "   exit" -ForegroundColor Cyan
Write-Host ""

Write-Host "方法 2: 临时启用密码登录" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "1. 在服务器上编辑 SSH 配置：" -ForegroundColor White
Write-Host "   sudo nano /etc/ssh/sshd_config" -ForegroundColor Cyan
Write-Host "2. 找到并修改：" -ForegroundColor White
Write-Host "   PasswordAuthentication yes" -ForegroundColor Cyan
Write-Host "3. 重启 SSH 服务：" -ForegroundColor White
Write-Host "   sudo systemctl restart sshd" -ForegroundColor Cyan
Write-Host ""

Write-Host "测试连接命令：" -ForegroundColor Yellow
Write-Host "ssh -i $SSH_KEY_PATH ${SERVER_USER}@${SERVER_IP}" -ForegroundColor Cyan
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  GitHub Secret 配置" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Secret 名称: FirstKey" -ForegroundColor Yellow
Write-Host ""
Write-Host "私钥内容（复制以下内容）：" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Get-Content $SSH_KEY_PATH | ForEach-Object { Write-Host $_ -ForegroundColor White }
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ""
Write-Host "重要提示：" -ForegroundColor Red
Write-Host "1. 复制完整的私钥内容（包括 BEGIN 和 END 行）" -ForegroundColor White
Write-Host "2. 在 GitHub 仓库 Settings -> Secrets and variables -> Actions 中添加" -ForegroundColor White
Write-Host "3. Secret 名称必须是: FirstKey" -ForegroundColor White
