# 🌐 OpenWrt软路由SOCKS多出口部署指南

一份完整的软路由SOCKS多端口代理实施方案，实现智能分流和多地区出口。

## 📋 系统要求

### 🔧 硬件要求
- **CPU**: ARM64/x86_64架构
- **内存**: 建议2GB以上（最低1GB）
- **存储**: 16GB以上可用空间
- **网络**: 双网口（WAN/LAN）

### 💿 固件要求
- **OpenWrt 21.02+** 或 **ImmortalWrt**
- **内核版本**: 5.4+ 
- **支持TUN/TAP**: 必须
- **iptables**: 完整版本

## 🚀 第一步：安装Clash内核

### 方法1：官方软件源安装（推荐）
```bash
# 更新软件包列表
opkg update

# 安装Clash Meta内核
opkg install clash-meta

# 安装LuCI界面（可选）
opkg install luci-app-clash
```

### 方法2：手动安装最新版本
```bash
# 下载Clash Meta最新版本
cd /tmp
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.17.0/mihomo-linux-arm64.gz

# 解压并安装
gunzip mihomo-linux-arm64.gz
chmod +x mihomo-linux-arm64
mv mihomo-linux-arm64 /usr/bin/clash
```

### 验证安装
```bash
# 检查版本
clash -v

# 预期输出：
# Clash Meta v1.17.0 linux arm64...
```

## 🔧 第二步：配置系统环境

### 创建配置目录
```bash
# 创建Clash配置目录
mkdir -p /etc/clash
mkdir -p /etc/clash/configs
mkdir -p /var/log/clash

# 设置权限
chown -R root:root /etc/clash
chmod 755 /etc/clash
```

### 配置系统服务
```bash
# 创建systemd服务文件
cat > /etc/systemd/system/clash.service << 'EOF'
[Unit]
Description=Clash Meta Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/clash -d /etc/clash
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=10
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

# 重载系统服务
systemctl daemon-reload
```

## 📁 第三步：部署配置文件

### 上传配置文件
将从Web转换器生成的`clash-openwrt-*.yaml`配置文件上传到软路由：

```bash
# 方法1：SCP上传
scp clash-openwrt-20241206_143022.yaml root@192.168.1.1:/etc/clash/config.yaml

# 方法2：通过LuCI界面上传
# 系统 -> 文件传输 -> 上传到 /etc/clash/
```

### 验证配置文件
```bash
# 检查配置文件语法
clash -t -d /etc/clash

# 预期输出：
# Configuration file is valid
```

## 🌐 第四步：网络配置

### 配置透明代理
```bash
# 创建透明代理规则脚本
cat > /etc/clash/transparent-proxy.sh << 'EOF'
#!/bin/bash

# 清除已有规则
iptables -t nat -F CLASH
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

# 重定向TCP流量到Clash TUN
iptables -t nat -A CLASH -p tcp -j REDIRECT --to-ports 7890

# 应用规则到PREROUTING
iptables -t nat -A PREROUTING -p tcp -j CLASH

echo "透明代理规则已应用"
EOF

# 设置执行权限
chmod +x /etc/clash/transparent-proxy.sh
```

### 配置DNS劫持
```bash
# 修改dnsmasq配置
cat >> /etc/dnsmasq.conf << 'EOF'
# Clash DNS重定向
server=127.0.0.1#1053
# 禁用上游DNS查询
no-resolv
EOF

# 重启dnsmasq
/etc/init.d/dnsmasq restart
```

## 🎯 第五步：SOCKS多出口配置

### 端口分配方案
```bash
# 查看生成的SOCKS端口配置
cat /etc/clash/config.yaml | grep -A 5 "listeners:"

# 标准端口分配：
# 7890: 混合代理（HTTP+SOCKS）- 智能选择
# 7891: 香港专线SOCKS
# 7892: 美国专线SOCKS  
# 7893: 日本专线SOCKS
# 7894: 新加坡专线SOCKS
# 7895: 台湾专线SOCKS
```

### 配置防火墙开放端口
```bash
# 开放Clash相关端口
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-Clash-Mixed'
uci set firewall.@rule[-1].src='lan'
uci set firewall.@rule[-1].dest_port='7890'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# 开放各地区SOCKS端口
for port in 7891 7892 7893 7894 7895; do
    uci add firewall rule
    uci set firewall.@rule[-1].name="Allow-Clash-SOCKS-$port"
    uci set firewall.@rule[-1].src='lan'
    uci set firewall.@rule[-1].dest_port="$port"
    uci set firewall.@rule[-1].proto='tcp'
    uci set firewall.@rule[-1].target='ACCEPT'
done

# 开放管理端口
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-Clash-Control'
uci set firewall.@rule[-1].src='lan'
uci set firewall.@rule[-1].dest_port='9090'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# 应用配置
uci commit firewall
/etc/init.d/firewall restart
```

## 🔄 第六步：启动服务

### 启动Clash服务
```bash
# 启动服务
systemctl start clash

# 设置开机自启
systemctl enable clash

# 检查运行状态
systemctl status clash

# 查看日志
journalctl -u clash -f
```

### 应用透明代理
```bash
# 执行透明代理脚本
/etc/clash/transparent-proxy.sh

# 添加到开机启动
cat >> /etc/rc.local << 'EOF'
# 启动Clash透明代理
/etc/clash/transparent-proxy.sh
EOF
```

## 📱 第七步：客户端配置

### 🖥️ 电脑配置示例

#### Windows代理设置
```powershell
# 设置系统代理
netsh winhttp set proxy 192.168.1.1:7890

# 或者在浏览器中设置：
# HTTP代理: 192.168.1.1:7890
# SOCKS代理: 192.168.1.1:7891-7895
```

#### macOS/Linux代理设置
```bash
# 设置环境变量
export http_proxy=http://192.168.1.1:7890
export https_proxy=http://192.168.1.1:7890

# 或使用SOCKS代理
export http_proxy=socks5://192.168.1.1:7891
export https_proxy=socks5://192.168.1.1:7891
```

### 📱 移动设备配置

#### Android设置
```
网络设置 -> WiFi -> 长按网络 -> 修改网络
高级选项 -> 代理 -> 手动
代理主机名: 192.168.1.1
代理端口: 7890
```

#### iOS设置
```
设置 -> WiFi -> 点击网络名称后的 (i)
配置代理 -> 手动
服务器: 192.168.1.1
端口: 7890
```

### 🎮 应用专用配置

#### 游戏加速（日本专线）
```bash
# 配置游戏客户端使用日本SOCKS
# 代理地址: 192.168.1.1:7893
# 协议: SOCKS5
```

#### 流媒体解锁（美国专线）
```bash
# 配置视频应用使用美国SOCKS
# 代理地址: 192.168.1.1:7892
# 协议: SOCKS5
```

## 🔍 第八步：验证和监控

### 检查服务状态
```bash
# 检查端口监听
netstat -tlnp | grep clash

# 预期输出：
# tcp 0.0.0.0:7890 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:7891 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:7892 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:7893 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:7894 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:7895 0.0.0.0:* LISTEN clash
# tcp 0.0.0.0:9090 0.0.0.0:* LISTEN clash
```

### 测试连接
```bash
# 测试各端口连通性
for port in 7890 7891 7892 7893 7894 7895; do
    echo "测试端口 $port:"
    curl --proxy socks5://127.0.0.1:$port --connect-timeout 5 http://ipinfo.io/country
done
```

### Web管理界面
```
访问地址: http://192.168.1.1:9090
- 查看节点状态
- 切换代理组
- 监控流量统计
- 查看连接日志
```

## 🛠️ 高级配置

### 分流规则优化
```yaml
# 编辑 /etc/clash/config.yaml 
rules:
  # 游戏加速 - 强制日本线路
  - DOMAIN-SUFFIX,mihoyo.com,日本出口
  - DOMAIN-SUFFIX,nintendo.com,日本出口
  
  # 流媒体解锁 - 强制美国线路  
  - DOMAIN-SUFFIX,netflix.com,美国出口
  - DOMAIN-SUFFIX,hulu.com,美国出口
  
  # 办公应用 - 香港线路
  - DOMAIN-SUFFIX,github.com,香港出口
  - DOMAIN-SUFFIX,telegram.org,香港出口
  
  # 其他流量 - 智能选择
  - MATCH,🌟 主选择
```

### 负载均衡配置
```yaml
proxy-groups:
  - name: 香港负载均衡
    type: load-balance
    url: http://www.gstatic.com/generate_204
    interval: 300
    strategy: round-robin
    proxies:
      - 🇭🇰 香港中转
      - 🇭🇰 香港中转 - 东莞
      - 🇭🇰 香港中转 - 广州
```

### 故障转移配置
```yaml
proxy-groups:
  - name: 美国故障转移
    type: fallback
    url: http://www.gstatic.com/generate_204
    interval: 300
    tolerance: 500
    proxies:
      - 🇺🇸 美国中转
      - 🇺🇸 美国中转 - 广州  
      - 🇺🇸 美国中转 - 东莞
      - 🇺🇸 美国中转原生
```

## 🔧 故障排除

### 常见问题解决

#### 1. 服务无法启动
```bash
# 检查配置文件语法
clash -t -d /etc/clash

# 查看详细错误
journalctl -u clash -n 50
```

#### 2. 端口无法访问
```bash
# 检查防火墙规则
iptables -L -n | grep 789

# 检查端口监听
ss -tlnp | grep clash
```

#### 3. DNS解析问题
```bash
# 检查DNS配置
nslookup google.com 127.0.0.1

# 重启DNS服务
/etc/init.d/dnsmasq restart
```

#### 4. 透明代理失效
```bash
# 重新应用iptables规则
/etc/clash/transparent-proxy.sh

# 检查NAT规则
iptables -t nat -L CLASH -n
```

### 性能优化建议

#### 内存优化
```bash
# 限制Clash内存使用
systemctl edit clash

# 添加内容：
[Service]
MemoryMax=512M
```

#### CPU优化
```bash
# 设置CPU亲和性
taskset -c 0,1 clash -d /etc/clash
```

## 📊 监控和维护

### 日志管理
```bash
# 配置日志轮转
cat > /etc/logrotate.d/clash << 'EOF'
/var/log/clash/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 root root
    postrotate
        systemctl reload clash
    endscript
}
EOF
```

### 自动更新脚本
```bash
# 创建配置更新脚本
cat > /etc/clash/update-config.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/etc/clash/backup"
CONFIG_FILE="/etc/clash/config.yaml"

# 创建备份
mkdir -p $BACKUP_DIR
cp $CONFIG_FILE $BACKUP_DIR/config.yaml.$(date +%Y%m%d_%H%M%S)

# 重启服务
systemctl restart clash

echo "配置已更新并重启服务"
EOF

chmod +x /etc/clash/update-config.sh
```

---

## 🎯 总结

通过以上配置，你的软路由将提供：

✅ **7个代理端口**：混合代理 + 5个地区专线SOCKS  
✅ **透明代理**：局域网设备自动走代理  
✅ **智能分流**：根据域名/IP自动选择线路  
✅ **Web管理**：直观的管理界面  
✅ **故障转移**：自动切换失效节点  
✅ **负载均衡**：多节点分担流量  

现在你的软路由已经具备了专业级的SOCKS多出口功能！ 🚀 