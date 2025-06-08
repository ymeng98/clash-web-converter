# 🚀 OpenWrt SOCKS多出口 - 快速开始

适合初学者的一键部署指南，3分钟完成软路由SOCKS多出口配置。

## 📋 前提条件

### ✅ 必需条件
- **硬件**: 任何OpenWrt软路由设备
- **固件**: OpenWrt 21.02+ 或 ImmortalWrt
- **网络**: 设备能正常上网
- **配置文件**: 从Web转换器生成的OpenWrt专用配置

### 🔧 准备工作
1. 确保软路由正常运行
2. 获取管理员权限（SSH登录）
3. 准备Clash配置文件

## 🎯 一键部署（推荐）

### 步骤1：上传部署脚本
```bash
# SSH登录到软路由
ssh root@192.168.1.1

# 下载部署脚本
wget https://your-domain.com/deploy-openwrt.sh
chmod +x deploy-openwrt.sh
```

### 步骤2：执行部署
```bash
# 运行一键部署脚本
./deploy-openwrt.sh
```

### 步骤3：提供配置信息
脚本会询问：
- **配置文件路径**: 输入从Web转换器下载的配置文件路径
- **路由器IP**: 通常是 `192.168.1.1`

### 步骤4：等待完成
脚本会自动：
- 安装Clash内核
- 配置防火墙规则
- 启动SOCKS服务
- 设置透明代理

## 🔧 手动部署

### 步骤1：安装Clash
```bash
# 更新软件包
opkg update

# 安装依赖
opkg install curl wget ca-certificates iptables-mod-nat-extra kmod-tun

# 安装Clash Meta
opkg install clash-meta
```

### 步骤2：配置目录
```bash
# 创建配置目录
mkdir -p /etc/clash
mkdir -p /var/log/clash

# 上传配置文件
# 将生成的 clash-openwrt-*.yaml 重命名为 config.yaml
# 放置到 /etc/clash/config.yaml
```

### 步骤3：创建服务
```bash
# 创建启动脚本
cat > /etc/init.d/clash << 'EOF'
#!/bin/sh /etc/rc.common

START=99
STOP=10
USE_PROCD=1

start_service() {
    procd_open_instance
    procd_set_param command /usr/bin/clash -d /etc/clash
    procd_set_param respawn
    procd_close_instance
}
EOF

# 设置权限并启用
chmod +x /etc/init.d/clash
/etc/init.d/clash enable
```

### 步骤4：配置防火墙
```bash
# 开放端口
ports="7890 7891 7892 7893 7894 7895 9090"
for port in $ports; do
    uci add firewall rule
    uci set firewall.@rule[-1].name="Allow-Clash-$port"
    uci set firewall.@rule[-1].src='lan'
    uci set firewall.@rule[-1].dest_port="$port"
    uci set firewall.@rule[-1].proto='tcp'
    uci set firewall.@rule[-1].target='ACCEPT'
done

# 应用配置
uci commit firewall
/etc/init.d/firewall restart
```

### 步骤5：启动服务
```bash
# 启动Clash
/etc/init.d/clash start

# 检查状态
/etc/init.d/clash status
```

## 📱 客户端配置

### 🖥️ 电脑设置

#### Windows
```
设置 -> 网络和Internet -> 代理
手动代理: 192.168.1.1:7890
```

#### macOS
```
系统偏好设置 -> 网络 -> 高级 -> 代理
HTTP代理: 192.168.1.1:7890
HTTPS代理: 192.168.1.1:7890
```

#### Linux
```bash
export http_proxy=http://192.168.1.1:7890
export https_proxy=http://192.168.1.1:7890
```

### 📱 移动设备

#### Android/iOS
```
WiFi设置 -> 代理配置 -> 手动
服务器: 192.168.1.1
端口: 7890
```

### 🎮 应用专用代理

#### 游戏加速（日本线路）
```
SOCKS5代理: 192.168.1.1:7893
适用于: 原神、LOL日服等
```

#### 流媒体解锁（美国线路）
```
SOCKS5代理: 192.168.1.1:7892
适用于: Netflix、Hulu等
```

#### 办公应用（香港线路）
```
SOCKS5代理: 192.168.1.1:7891
适用于: GitHub、Telegram等
```

## 🔍 验证和测试

### 检查服务状态
```bash
# 查看端口监听
netstat -tlnp | grep clash

# 查看服务日志
logread | grep clash

# 测试配置文件
clash -t -d /etc/clash
```

### 测试连接
```bash
# 测试各端口
curl --proxy socks5://127.0.0.1:7891 http://ipinfo.io/country  # 香港
curl --proxy socks5://127.0.0.1:7892 http://ipinfo.io/country  # 美国
curl --proxy socks5://127.0.0.1:7893 http://ipinfo.io/country  # 日本
```

### Web管理界面
```
访问: http://192.168.1.1:9090
- 查看节点状态
- 切换代理组
- 监控流量
```

## 🎯 端口分配一览

| 端口 | 协议 | 地区 | 用途 |
|------|------|------|------|
| 7890 | HTTP+SOCKS | 智能选择 | 通用代理 |
| 7891 | SOCKS5 | 🇭🇰 香港 | 办公、聊天 |
| 7892 | SOCKS5 | 🇺🇸 美国 | 流媒体解锁 |
| 7893 | SOCKS5 | 🇯🇵 日本 | 游戏加速 |
| 7894 | SOCKS5 | 🇸🇬 新加坡 | 备用线路 |
| 7895 | SOCKS5 | 🇹🇼 台湾 | 备用线路 |
| 9090 | HTTP | - | Web管理 |

## 🛠️ 常用管理命令

```bash
# 服务管理
/etc/init.d/clash start      # 启动
/etc/init.d/clash stop       # 停止
/etc/init.d/clash restart    # 重启
/etc/init.d/clash status     # 状态

# 配置管理
clash -t -d /etc/clash       # 测试配置
vi /etc/clash/config.yaml    # 编辑配置

# 日志查看
logread | grep clash         # 查看日志
logread -f | grep clash      # 实时日志
```

## 🔧 故障排除

### 问题1: 服务无法启动
```bash
# 检查配置文件
clash -t -d /etc/clash

# 查看错误日志
logread | grep clash | tail -20
```

### 问题2: 端口无法访问
```bash
# 检查端口监听
netstat -tlnp | grep 789

# 检查防火墙规则
iptables -L | grep 789
```

### 问题3: 网络不通
```bash
# 重启网络服务
/etc/init.d/network restart

# 检查路由表
ip route show
```

## 💡 优化建议

### 性能优化
- 关闭不需要的服务
- 调整Clash内存限制
- 使用高速存储设备

### 稳定性优化
- 定期更新配置文件
- 监控服务状态
- 设置自动重启

### 安全优化
- 修改默认管理端口
- 设置访问密码
- 限制管理界面访问

---

## 🎉 完成！

现在你的软路由已经具备了专业级的SOCKS多出口功能：

✅ **6个代理端口**：覆盖主要地区  
✅ **透明代理**：设备自动走代理  
✅ **智能分流**：自动选择最佳线路  
✅ **Web管理**：可视化管理界面  
✅ **自动启动**：开机自动运行  

享受你的多线路软路由吧！ 🚀 