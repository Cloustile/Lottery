@echo off
chcp 65001 >nul
echo ========================================
echo   Lottery 抽奖系统 - Vercel 部署工具
echo ========================================
echo.

REM 检查是否安装 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未检测到 Node.js，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js 已安装
echo.

REM 检查是否安装 Vercel CLI
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 正在安装 Vercel CLI...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo ❌ Vercel CLI 安装失败
        pause
        exit /b 1
    )
    echo ✅ Vercel CLI 安装成功
) else (
    echo ✅ Vercel CLI 已安装
)

echo.
echo ========================================
echo   开始部署到 Vercel
echo ========================================
echo.
echo 提示：
echo 1. 首次部署需要登录 Vercel 账号
echo 2. 按照提示选择项目配置
echo 3. 部署完成后会显示访问地址
echo.
pause

echo.
echo 🚀 正在部署...
echo.

vercel --prod

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 请在上方查看部署地址
echo.
pause
