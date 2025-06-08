#!/bin/bash

# =================================================================
# 🌐 Clash稳定中转SOCKS代理转换器 - 云服务器一键部署脚本
# 支持：Ubuntu 18.04+, CentOS 7+, Debian 9+
# 作者：ymeng98
# 版本：v1.0
# =================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="clash-web-converter"
GITHUB_REPO="https://github.com/ymeng98/clash-web-converter.git"
INSTALL_DIR="/opt/clash-converter"
SERVICE_USER="clash-converter"
SERVICE_PORT="5000"
DOMAIN=""

# 日志函数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════╗
    ║         🌐 Clash稳定中转SOCKS代理转换器                     ║
    ║              云服务器一键部署脚本 v1.0                       ║
    ╠══════════════════════════════════════════════════════════╣
    ║  📦 自动安装所有依赖                                        ║
    ║  🔧 自动配置系统服务                                        ║
    ║  🌍 自动配置防火墙和端口                                     ║
    ║  🔒 自动配置SSL证书（可选）                                  ║
    ║  🚀 开机自启动                                              ║
    ╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检测系统类型
detect_system() {
    log_step "检测系统环境"
    
    if [[ -f /etc/redhat-release ]]; then
        OS="centos"
        log_info "检测到 CentOS/RHEL 系统"
    elif [[ -f /etc/lsb-release ]]; then
        OS="ubuntu"
        log_info "检测到 Ubuntu 系统"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        log_info "检测到 Debian 系统"
    else
        log_error "不支持的操作系统，请使用 Ubuntu/CentOS/Debian"
        exit 1
    fi
    
    # 检查是否为root用户
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用 root 用户运行此脚本"
        exit 1
    fi
    
    log_success "系统检测完成"
}

# 获取用户配置
get_user_config() {
    log_step "配置部署参数"
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "未知")
    log_info "服务器IP: $SERVER_IP"
    
    # 询问域名
    echo -e "${YELLOW}是否配置域名？(y/n)${NC}"
    read -p "默认使用IP访问: " use_domain
    
    if [[ $use_domain =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}请输入域名 (例如: clash.example.com):${NC}"
        read -p "域名: " DOMAIN
        if [[ -n $DOMAIN ]]; then
            log_info "将使用域名: $DOMAIN"
        fi
    fi
    
    # 询问端口
    echo -e "${YELLOW}是否修改默认端口 5000？(y/n)${NC}"
    read -p "回车使用默认端口: " change_port
    
    if [[ $change_port =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}请输入端口号 (1000-65535):${NC}"
        read -p "端口: " custom_port
        if [[ $custom_port =~ ^[0-9]+$ ]] && [[ $custom_port -ge 1000 ]] && [[ $custom_port -le 65535 ]]; then
            SERVICE_PORT=$custom_port
            log_info "将使用端口: $SERVICE_PORT"
        else
            log_warning "端口无效，使用默认端口 5000"
        fi
    fi
}

# 更新系统
update_system() {
    log_step "更新系统软件包"
    
    case $OS in
        "ubuntu"|"debian")
            apt update
            apt upgrade -y
            apt install -y curl wget git unzip software-properties-common
            ;;
        "centos")
            yum update -y
            yum install -y curl wget git unzip epel-release
            ;;
    esac
    
    log_success "系统更新完成"
}

# 安装Python 3.8+
install_python() {
    log_step "安装 Python 3.8+"
    
    case $OS in
        "ubuntu"|"debian")
            apt install -y python3 python3-pip python3-venv python3-dev
            ;;
        "centos")
            yum install -y python3 python3-pip python3-devel
            ;;
    esac
    
    # 验证Python版本
    python3_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    if [[ $(echo "$python3_version >= 3.7" | bc) -eq 1 ]]; then
        log_success "Python $python3_version 安装成功"
    else
        log_error "Python 版本过低，需要 3.7+"
        exit 1
    fi
}

# 创建服务用户
create_service_user() {
    log_step "创建服务用户"
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d $INSTALL_DIR $SERVICE_USER
        log_success "创建用户: $SERVICE_USER"
    else
        log_info "用户 $SERVICE_USER 已存在"
    fi
}

# 下载项目代码
download_project() {
    log_step "下载项目代码"
    
    # 删除旧目录
    if [[ -d $INSTALL_DIR ]]; then
        log_warning "删除旧安装目录"
        rm -rf $INSTALL_DIR
    fi
    
    # 克隆代码
    git clone $GITHUB_REPO $INSTALL_DIR
    cd $INSTALL_DIR
    
    # 设置权限
    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
    
    log_success "项目代码下载完成"
}

# 安装Python依赖
install_dependencies() {
    log_step "安装 Python 依赖"
    
    cd $INSTALL_DIR
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    pip install gunicorn supervisor
    
    # 设置权限
    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/venv
    
    log_success "Python 依赖安装完成"
}

# 创建生产配置文件
create_production_config() {
    log_step "创建生产配置"
    
    cat > $INSTALL_DIR/gunicorn.conf.py << EOF
# Gunicorn 生产配置
bind = "0.0.0.0:$SERVICE_PORT"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2
user = "$SERVICE_USER"
group = "$SERVICE_USER"
tmp_upload_dir = None
errorlog = "/var/log/clash-converter/error.log"
accesslog = "/var/log/clash-converter/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
EOF

    # 创建日志目录
    mkdir -p /var/log/clash-converter
    chown -R $SERVICE_USER:$SERVICE_USER /var/log/clash-converter
    
    log_success "生产配置创建完成"
}

# 创建系统服务
create_systemd_service() {
    log_step "创建系统服务"
    
    cat > /etc/systemd/system/clash-converter.service << EOF
[Unit]
Description=Clash Web Converter
After=network.target
Wants=network.target

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=clash-converter

[Install]
WantedBy=multi-user.target
EOF

    # 重载系统服务
    systemctl daemon-reload
    systemctl enable clash-converter
    
    log_success "系统服务创建完成"
}

# 配置防火墙
setup_firewall() {
    log_step "配置防火墙"
    
    case $OS in
        "ubuntu"|"debian")
            if command -v ufw &> /dev/null; then
                ufw allow $SERVICE_PORT/tcp
                ufw allow ssh
                log_info "UFW 防火墙规则已添加"
            fi
            ;;
        "centos")
            if command -v firewalld &> /dev/null; then
                firewall-cmd --permanent --add-port=$SERVICE_PORT/tcp
                firewall-cmd --reload
                log_info "Firewalld 防火墙规则已添加"
            fi
            ;;
    esac
    
    log_success "防火墙配置完成"
}

# 安装Nginx（可选）
install_nginx() {
    log_step "安装 Nginx 反向代理"
    
    echo -e "${YELLOW}是否安装 Nginx 反向代理？(推荐) (y/n)${NC}"
    read -p "默认: y " install_nginx_choice
    
    if [[ $install_nginx_choice =~ ^[Nn]$ ]]; then
        log_info "跳过 Nginx 安装"
        return
    fi
    
    case $OS in
        "ubuntu"|"debian")
            apt install -y nginx
            ;;
        "centos")
            yum install -y nginx
            ;;
    esac
    
    # 创建Nginx配置
    NGINX_CONF="/etc/nginx/sites-available/clash-converter"
    if [[ $OS == "centos" ]]; then
        NGINX_CONF="/etc/nginx/conf.d/clash-converter.conf"
    fi
    
    SERVER_NAME=$SERVER_IP
    if [[ -n $DOMAIN ]]; then
        SERVER_NAME=$DOMAIN
    fi
    
    cat > $NGINX_CONF << EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://127.0.0.1:$SERVICE_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static/ {
        alias $INSTALL_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # 启用站点
    if [[ $OS != "centos" ]]; then
        ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
    fi
    
    # 测试Nginx配置
    nginx -t
    systemctl enable nginx
    systemctl restart nginx
    
    # 配置防火墙HTTP端口
    case $OS in
        "ubuntu"|"debian")
            if command -v ufw &> /dev/null; then
                ufw allow 80/tcp
                ufw allow 443/tcp
            fi
            ;;
        "centos")
            if command -v firewalld &> /dev/null; then
                firewall-cmd --permanent --add-service=http
                firewall-cmd --permanent --add-service=https
                firewall-cmd --reload
            fi
            ;;
    esac
    
    log_success "Nginx 安装配置完成"
}

# 配置SSL证书（可选）
setup_ssl() {
    if [[ -z $DOMAIN ]]; then
        log_info "未配置域名，跳过SSL设置"
        return
    fi
    
    log_step "配置 SSL 证书"
    
    echo -e "${YELLOW}是否安装 Let's Encrypt SSL 证书？(y/n)${NC}"
    read -p "默认: y " install_ssl_choice
    
    if [[ $install_ssl_choice =~ ^[Nn]$ ]]; then
        log_info "跳过 SSL 证书安装"
        return
    fi
    
    # 安装 Certbot
    case $OS in
        "ubuntu"|"debian")
            apt install -y certbot python3-certbot-nginx
            ;;
        "centos")
            yum install -y certbot python3-certbot-nginx
            ;;
    esac
    
    # 获取证书
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    
    # 设置自动续期
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
    
    log_success "SSL 证书配置完成"
}

# 启动服务
start_services() {
    log_step "启动服务"
    
    # 启动应用服务
    systemctl start clash-converter
    systemctl status clash-converter --no-pager
    
    if systemctl is-active --quiet clash-converter; then
        log_success "Clash Converter 服务启动成功"
    else
        log_error "Clash Converter 服务启动失败"
        journalctl -u clash-converter --no-pager -n 20
        exit 1
    fi
}

# 显示部署结果
show_result() {
    log_step "部署完成"
    
    echo -e "${GREEN}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════╗
    ║                   🎉 部署成功！                          ║
    ╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${WHITE}访问地址：${NC}"
    if [[ -n $DOMAIN ]]; then
        if command -v nginx &> /dev/null; then
            echo -e "  🌐 ${CYAN}https://$DOMAIN${NC} (主要访问地址)"
            echo -e "  🌐 ${CYAN}http://$DOMAIN${NC} (HTTP访问)"
        fi
        echo -e "  🌐 ${CYAN}http://$DOMAIN:$SERVICE_PORT${NC} (直接访问)"
    else
        if command -v nginx &> /dev/null; then
            echo -e "  🌐 ${CYAN}http://$SERVER_IP${NC} (主要访问地址)"
        fi
        echo -e "  🌐 ${CYAN}http://$SERVER_IP:$SERVICE_PORT${NC} (直接访问)"
    fi
    
    echo -e "\n${WHITE}服务管理命令：${NC}"
    echo -e "  启动服务: ${YELLOW}systemctl start clash-converter${NC}"
    echo -e "  停止服务: ${YELLOW}systemctl stop clash-converter${NC}"
    echo -e "  重启服务: ${YELLOW}systemctl restart clash-converter${NC}"
    echo -e "  查看状态: ${YELLOW}systemctl status clash-converter${NC}"
    echo -e "  查看日志: ${YELLOW}journalctl -u clash-converter -f${NC}"
    
    echo -e "\n${WHITE}文件位置：${NC}"
    echo -e "  项目目录: ${YELLOW}$INSTALL_DIR${NC}"
    echo -e "  日志目录: ${YELLOW}/var/log/clash-converter/${NC}"
    echo -e "  配置文件: ${YELLOW}$INSTALL_DIR/gunicorn.conf.py${NC}"
    
    if command -v nginx &> /dev/null; then
        echo -e "\n${WHITE}Nginx 管理：${NC}"
        echo -e "  重启 Nginx: ${YELLOW}systemctl restart nginx${NC}"
        echo -e "  Nginx 配置: ${YELLOW}$NGINX_CONF${NC}"
    fi
    
    echo -e "\n${GREEN}🚀 现在可以开始使用 Clash 代理转换器了！${NC}"
}

# 清理函数
cleanup() {
    if [[ $? -ne 0 ]]; then
        log_error "部署过程中发生错误"
        log_info "清理临时文件..."
        # 这里可以添加清理逻辑
    fi
}

# 主函数
main() {
    trap cleanup EXIT
    
    show_welcome
    detect_system
    get_user_config
    update_system
    install_python
    create_service_user
    download_project
    install_dependencies
    create_production_config
    create_systemd_service
    setup_firewall
    install_nginx
    setup_ssl
    start_services
    show_result
}

# 执行主函数
main "$@" 