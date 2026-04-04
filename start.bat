@echo off
chcp 65001 >nul
echo ========================================
echo   Lottery 抽奖系统 - FastAPI 版本
echo ========================================
echo.
echo 正在启动服务器...
echo.
echo 访问地址:
echo   - 用户抽奖页: http://localhost:8000/
echo   - 管理后台: http://localhost:8000/admin
echo   - API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python app.py

pause
