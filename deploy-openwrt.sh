#!/bin/bash

# 🌐 OpenWrt软路由SOCKS多出口一键部署脚本
# 适用于 OpenWrt 21.02+ / ImmortalWrt

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
CLASH_VERSION="v1.17.0"
CLASH_DIR="/etc/clash"
CONFIG_URL=""
ROUTER_IP="192.168.1.1"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# 显示Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║               🌐 OpenWrt SOCKS多出口部署脚本                 ║
║                                                              ║
║  🎯 功能：                                                   ║
║     • 自动安装Clash Meta内核                                 ║
║     • 配置SOCKS多端口代理                                    ║
║     • 设置透明代理和DNS劫持                                  ║
║     • 开放防火墙端口                                         ║
║     • 配置自动启动服务                                       ║
║                                                              ║
║  📦 支持系统：OpenWrt 21.02+ / ImmortalWrt                   ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查是否为OpenWrt
    if [ ! -f /etc/openwrt_release ]; then
        log_error "此脚本仅支持OpenWrt系统"
        exit 1
    fi
    
    # 检查架构
    ARCH=$(uname -m)
    case $ARCH in
        aarch64|arm64)
            CLASH_ARCH="arm64"
            ;;
        armv7l|armv6l)
            CLASH_ARCH="armv7"
            ;;
        x86_64)
            CLASH_ARCH="amd64"
            ;;
        *)
            log_error "不支持的架构: $ARCH"
            exit 1
            ;;
    esac
    
    log_success "系统检查通过，架构: $ARCH"
    
    # 检查内存
    MEMORY=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEMORY_MB=$((MEMORY / 1024))
    
    if [ $MEMORY_MB -lt 512 ]; then
        log_warning "内存不足512MB，可能影响性能"
    else
        log_success "内存充足: ${MEMORY_MB}MB"
    fi
}

# 获取用户配置
get_config() {
    echo -e "${PURPLE}请提供配置信息：${NC}"
    
    # 获取配置文件路径或URL
    echo -n "请输入配置文件路径或URL: "
    read CONFIG_INPUT
    
    if [ -z "$CONFIG_INPUT" ]; then
        log_error "配置文件路径不能为空"
        exit 1
    fi
    
    # 检查是否为URL
    if [[ $CONFIG_INPUT =~ ^https?:// ]]; then
        CONFIG_URL="$CONFIG_INPUT"
        log_info "将从URL下载配置文件"
    elif [ -f "$CONFIG_INPUT" ]; then
        CONFIG_FILE="$CONFIG_INPUT"
        log_info "将使用本地配置文件"
    else
        log_error "配置文件不存在: $CONFIG_INPUT"
        exit 1
    fi
    
    # 获取路由器IP
    echo -n "请输入路由器IP地址 [默认: 192.168.1.1]: "
    read INPUT_IP
    if [ ! -z "$INPUT_IP" ]; then
        ROUTER_IP="$INPUT_IP"
    fi
    
    log_success "配置获取完成"
}

# 安装依赖
install_dependencies() {
    log_info "更新软件包列表..."
    opkg update
    
    log_info "安装必要依赖..."
    opkg install curl wget ca-certificates iptables-mod-nat-extra kmod-tun
    
    # 检查是否需要安装unzip
    if ! command -v unzip &> /dev/null; then
        opkg install unzip
    fi
    
    log_success "依赖安装完成"
}

# 安装Clash
install_clash() {
    log_info "安装Clash Meta内核..."
    
    # 尝试从软件源安装
    if opkg list | grep -q "clash-meta"; then
        log_info "从软件源安装Clash Meta..."
        opkg install clash-meta
        CLASH_BINARY="/usr/bin/clash"
    else
        log_info "手动下载安装Clash Meta..."
        
        # 下载Clash
        CLASH_URL="https://github.com/MetaCubeX/mihomo/releases/download/${CLASH_VERSION}/mihomo-linux-${CLASH_ARCH}.gz"
        
        cd /tmp
        wget -O clash.gz "$CLASH_URL" || {
            log_error "下载Clash失败"
            exit 1
        }
        
        # 解压安装
        gunzip clash.gz
        chmod +x clash
        mv clash /usr/bin/clash
        CLASH_BINARY="/usr/bin/clash"
    fi
    
    # 验证安装
    if $CLASH_BINARY -v &> /dev/null; then
        log_success "Clash安装成功"
        $CLASH_BINARY -v
    else
        log_error "Clash安装失败"
        exit 1
    fi
}

# 配置系统环境
setup_environment() {
    log_info "配置系统环境..."
    
    # 创建目录
    mkdir -p $CLASH_DIR
    mkdir -p $CLASH_DIR/configs
    mkdir -p /var/log/clash
    
    # 设置权限
    chown -R root:root $CLASH_DIR
    chmod 755 $CLASH_DIR
    
    log_success "系统环境配置完成"
}

# 部署配置文件
deploy_config() {
    log_info "部署配置文件..."
    
    if [ ! -z "$CONFIG_URL" ]; then
        # 从URL下载
        wget -O $CLASH_DIR/config.yaml "$CONFIG_URL" || {
            log_error "下载配置文件失败"
            exit 1
        }
    else
        # 复制本地文件
        cp "$CONFIG_FILE" $CLASH_DIR/config.yaml || {
            log_error "复制配置文件失败"
            exit 1
        }
    fi
    
    # 验证配置文件
    if $CLASH_BINARY -t -d $CLASH_DIR; then
        log_success "配置文件验证通过"
    else
        log_error "配置文件验证失败"
        exit 1
    fi
}

# 创建系统服务
create_service() {
    log_info "创建系统服务..."
    
    # 创建init.d脚本（OpenWrt使用init.d而不是systemd）
    cat > /etc/init.d/clash << 'EOF'
#!/bin/sh /etc/rc.common

START=99
STOP=10

USE_PROCD=1
PROG=/usr/bin/clash
CONF_DIR=/etc/clash

start_service() {
    procd_open_instance
    procd_set_param command $PROG -d $CONF_DIR
    procd_set_param respawn ${respawn_threshold:-3600} ${respawn_timeout:-5} ${respawn_retry:-5}
    procd_set_param file /etc/clash/config.yaml
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}

reload_service() {
    stop
    start
}
EOF
    
    chmod +x /etc/init.d/clash
    
    # 启用服务
    /etc/init.d/clash enable
    
    log_success "系统服务创建完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙规则..."
    
    # 开放Clash端口
    ports="7890 7891 7892 7893 7894 7895 9090"
    
    for port in $ports; do
        # 检查规则是否已存在
        if ! uci show firewall | grep -q "dest_port='$port'"; then
            uci add firewall rule
            uci set firewall.@rule[-1].name="Allow-Clash-$port"
            uci set firewall.@rule[-1].src='lan'
            uci set firewall.@rule[-1].dest_port="$port"
            uci set firewall.@rule[-1].proto='tcp'
            uci set firewall.@rule[-1].target='ACCEPT'
            log_info "添加端口规则: $port"
        fi
    done
    
    # 应用配置
    uci commit firewall
    /etc/init.d/firewall restart
    
    log_success "防火墙配置完成"
}

# 配置透明代理
setup_transparent_proxy() {
    log_info "配置透明代理..."
    
    # 创建透明代理脚本
    cat > $CLASH_DIR/transparent-proxy.sh << 'EOF'
#!/bin/bash

# 清除已有规则
iptables -t nat -F CLASH 2>/dev/null
iptables -t nat -X CLASH 2>/dev/null

# 创建新链
iptables -t nat -N CLASH

# 跳过本地地址
iptables -t nat -A CLASH -d 0.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 10.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 127.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 169.254.0.0/16 -j RETURN
iptables -t nat -A CLASH -d 172.16.0.0/12 -j RETURN
iptables -t nat -A CLASH -d 192.168.0.0/16 -j RETURN
iptables -t nat -A CLASH -d 224.0.0.0/4 -j RETURN
iptables -t nat -A CLASH -d 240.0.0.0/4 -j RETURN

# 重定向TCP流量到Clash
iptables -t nat -A CLASH -p tcp -j REDIRECT --to-ports 7890

# 应用规则到PREROUTING
iptables -t nat -A PREROUTING -p tcp -j CLASH

echo "透明代理规则已应用"
EOF
    
    chmod +x $CLASH_DIR/transparent-proxy.sh
    
    # 添加到启动脚本
    if ! grep -q "transparent-proxy.sh" /etc/rc.local; then
        sed -i '/exit 0/i\/etc/clash/transparent-proxy.sh' /etc/rc.local
    fi
    
    log_success "透明代理配置完成"
}

# 配置DNS
setup_dns() {
    log_info "配置DNS设置..."
    
    # 备份原配置
    cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
    
    # 添加Clash DNS配置
    if ! grep -q "server=127.0.0.1#1053" /etc/dnsmasq.conf; then
        cat >> /etc/dnsmasq.conf << 'EOF'

# Clash DNS配置
server=127.0.0.1#1053
no-resolv
EOF
    fi
    
    # 重启dnsmasq
    /etc/init.d/dnsmasq restart
    
    log_success "DNS配置完成"
}

# 启动服务
start_services() {
    log_info "启动Clash服务..."
    
    # 启动Clash
    /etc/init.d/clash start
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if pgrep clash > /dev/null; then
        log_success "Clash服务启动成功"
    else
        log_error "Clash服务启动失败"
        exit 1
    fi
    
    # 应用透明代理
    $CLASH_DIR/transparent-proxy.sh
    
    log_success "所有服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署结果..."
    
    # 检查端口监听
    sleep 2
    
    echo -e "${CYAN}端口监听状态：${NC}"
    for port in 7890 7891 7892 7893 7894 7895 9090; do
        if netstat -tln | grep -q ":$port "; then
            echo -e "  ✅ 端口 $port: ${GREEN}正常${NC}"
        else
            echo -e "  ❌ 端口 $port: ${RED}未监听${NC}"
        fi
    done
    
    # 测试连接
    echo -e "\n${CYAN}连接测试：${NC}"
    if curl --connect-timeout 5 -s http://127.0.0.1:9090 > /dev/null; then
        echo -e "  ✅ Web管理界面: ${GREEN}可访问${NC}"
    else
        echo -e "  ❌ Web管理界面: ${RED}无法访问${NC}"
    fi
    
    log_success "部署验证完成"
}

# 显示使用说明
show_usage() {
    echo -e "\n${GREEN}🎉 OpenWrt SOCKS多出口部署完成！${NC}\n"
    
    echo -e "${CYAN}📊 端口配置：${NC}"
    echo -e "  🌟 混合代理: ${ROUTER_IP}:7890 (HTTP+SOCKS)"
    echo -e "  🇭🇰 香港专线: ${ROUTER_IP}:7891 (SOCKS5)"
    echo -e "  🇺🇸 美国专线: ${ROUTER_IP}:7892 (SOCKS5)"
    echo -e "  🇯🇵 日本专线: ${ROUTER_IP}:7893 (SOCKS5)"
    echo -e "  🇸🇬 新加坡专线: ${ROUTER_IP}:7894 (SOCKS5)"
    echo -e "  🇹🇼 台湾专线: ${ROUTER_IP}:7895 (SOCKS5)"
    
    echo -e "\n${CYAN}🔧 管理界面：${NC}"
    echo -e "  访问地址: http://${ROUTER_IP}:9090"
    
    echo -e "\n${CYAN}📱 客户端配置示例：${NC}"
    echo -e "  浏览器代理: ${ROUTER_IP}:7890"
    echo -e "  游戏加速: ${ROUTER_IP}:7893 (日本)"
    echo -e "  流媒体解锁: ${ROUTER_IP}:7892 (美国)"
    
    echo -e "\n${CYAN}🛠️ 管理命令：${NC}"
    echo -e "  启动服务: /etc/init.d/clash start"
    echo -e "  停止服务: /etc/init.d/clash stop"
    echo -e "  重启服务: /etc/init.d/clash restart"
    echo -e "  查看日志: logread | grep clash"
    echo -e "  测试配置: clash -t -d /etc/clash"
    
    echo -e "\n${YELLOW}💡 注意事项：${NC}"
    echo -e "  • 透明代理已启用，局域网设备自动走代理"
    echo -e "  • DNS已配置为Clash接管"
    echo -e "  • 防火墙已开放相应端口"
    echo -e "  • 服务已设置开机自启"
}

# 主函数
main() {
    show_banner
    
    # 检查root权限
    if [ "$(id -u)" != "0" ]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
    
    echo -e "${PURPLE}开始部署OpenWrt SOCKS多出口功能...${NC}\n"
    
    check_system
    get_config
    install_dependencies
    install_clash
    setup_environment
    deploy_config
    create_service
    setup_firewall
    setup_transparent_proxy
    setup_dns
    start_services
    verify_deployment
    show_usage
    
    echo -e "\n${GREEN}🚀 部署完成！享受你的SOCKS多出口软路由吧！${NC}"
}

# 错误处理
trap 'log_error "脚本执行失败，请检查错误信息"; exit 1' ERR

# 运行主函数
main "$@" 