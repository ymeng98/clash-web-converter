#!/bin/bash

echo "🚀 Clash转换器 - 云服务器部署脚本"
echo "=================================="

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
echo "🐍 安装Python环境..."
sudo apt install -y python3 python3-pip python3-venv

# 安装Git
echo "📥 安装Git..."
sudo apt install -y git

# 克隆项目（如果不存在）
if [ ! -d "clash-web-converter" ]; then
    echo "📁 克隆项目..."
    git clone [你的仓库地址] clash-web-converter
fi

cd clash-web-converter

# 创建虚拟环境
echo "🏗️ 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📚 安装项目依赖..."
pip install -r requirements.txt

# 安装Gunicorn
echo "🔧 安装Gunicorn生产服务器..."
pip install gunicorn

# 创建systemd服务文件
echo "⚙️ 配置系统服务..."
sudo tee /etc/systemd/system/clash-converter.service > /dev/null <<EOF
[Unit]
Description=Clash Web Converter
After=network.target

[Service]
User=$USER
WorkingDirectory=$PWD
Environment=PATH=$PWD/venv/bin
ExecStart=$PWD/venv/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
echo "🎯 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable clash-converter
sudo systemctl start clash-converter

# 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow 5000
sudo ufw --force enable

# 获取公网IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com)

echo ""
echo "=================================="
echo "🎉 部署完成!"
echo "=================================="
echo "🌐 公网访问地址: http://$PUBLIC_IP:5000"
echo "📱 订阅链接将使用: http://$PUBLIC_IP:5000/sub/配置文件"
echo "🔧 服务状态检查: sudo systemctl status clash-converter"
echo "📋 查看日志: sudo journalctl -u clash-converter -f"
echo "==================================" 