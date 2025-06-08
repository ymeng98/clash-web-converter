@echo off
chcp 65001 >nul
title Clash稳定中转SOCKS代理转换器 - Web版

echo.
echo ====================================================
echo     🚀 Clash SOCKS代理转换器 - Web版
echo ====================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境
    echo 请先安装Python 3.7或以上版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 📦 正在安装/更新依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依赖包安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo ✅ 依赖包安装完成
echo 🌐 正在启动Web服务器...
echo.
echo 📖 使用说明：
echo    • Web界面：http://localhost:5000
echo    • 支持订阅链接和文件上传
echo    • 自动生成稳定SOCKS代理配置
echo.
echo 💡 提示：
echo    • 按 Ctrl+C 停止服务器
echo    • 浏览器会自动打开Web界面
echo.

REM 启动Flask应用
python app.py

echo.
echo 服务器已停止，按任意键退出...
pause >nul 