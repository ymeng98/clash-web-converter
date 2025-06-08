@echo off
echo 正在启动 Clash 转换器...
echo.

REM 检查ngrok是否存在
if not exist "ngrok.exe" (
    echo [错误] 未找到ngrok.exe文件
    echo 请从 https://ngrok.com/ 下载 ngrok 并放到此目录
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装Python依赖...
pip install -r requirements.txt

REM 启动Flask应用（后台）
echo 正在启动Web服务...
start /B python app.py

REM 等待Flask启动
echo 等待Flask启动...
timeout /t 8 /nobreak >nul

REM 启动ngrok内网穿透
echo 正在启动内网穿透...
echo.
echo =====================================================
echo 🌐 即将启动公网访问通道
echo 📱 手机和任何设备都可以通过公网地址访问
echo 🔗 订阅链接将使用公网地址，不会有502错误
echo 💡 复制显示的公网地址，用它访问网页
echo =====================================================
echo.

.\ngrok.exe http 5000 