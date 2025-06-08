# 🌐 云服务器一键部署指南

## 🚀 一键部署（推荐）

### 快速开始
```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

### 手动下载运行
```bash
# 下载脚本
wget https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh

# 添加执行权限
chmod +x deploy-cloud-server.sh

# 运行部署脚本
sudo ./deploy-cloud-server.sh
```

## 📋 支持的云服务器

### ✅ 已测试支持
- **阿里云ECS** (Ubuntu 20.04+)
- **腾讯云CVM** (Ubuntu 20.04+) 
- **华为云ECS** (Ubuntu 20.04+)
- **AWS EC2** (Ubuntu 20.04+)
- **Google Cloud** (Ubuntu 20.04+)
- **DigitalOcean** (Ubuntu 20.04+)
- **Vultr** (Ubuntu 20.04+)
- **Linode** (Ubuntu 20.04+)

### 🖥️ 支持的操作系统
- Ubuntu 18.04+
- Debian 9+
- CentOS 7+
- RHEL 7+

## ⚙️ 服务器配置要求

### 最低配置
- **CPU**: 1核
- **内存**: 512MB
- **硬盘**: 10GB
- **带宽**: 1Mbps

### 推荐配置
- **CPU**: 1核
- **内存**: 1GB
- **硬盘**: 20GB
- **带宽**: 5Mbps

## 🔧 部署功能特性

### 🎯 自动安装
- ✅ Python 3.8+ 环境
- ✅ 项目依赖包
- ✅ Gunicorn WSGI服务器
- ✅ Nginx 反向代理（可选）
- ✅ SSL证书（Let's Encrypt，可选）

### 🛡️ 安全配置
- ✅ 创建专用服务用户
- ✅ 配置防火墙规则
- ✅ 系统服务管理
- ✅ 日志轮转

### 🚀 生产特性
- ✅ 系统服务自启动
- ✅ 进程监控和重启
- ✅ 访问日志记录
- ✅ 错误日志记录

## 📝 部署步骤详解

### 1. 连接服务器
```bash
# SSH连接服务器
ssh root@your-server-ip
```

### 2. 运行部署脚本
```bash
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

### 3. 配置选择
脚本会询问以下配置：

#### 🌐 域名设置
```
是否配置域名？(y/n)
默认使用IP访问: 
```
- 选择 `y` 输入域名（如 `clash.example.com`）
- 选择 `n` 使用IP地址访问

#### 🔌 端口设置
```
是否修改默认端口 5000？(y/n)
回车使用默认端口:
```
- 选择 `y` 自定义端口（1000-65535）
- 选择 `n` 使用默认端口5000

#### 🔄 Nginx代理
```
是否安装 Nginx 反向代理？(推荐) (y/n)
默认: y
```
- **推荐选择 `y`** - 提供80端口访问和SSL支持
- 选择 `n` - 仅使用直接端口访问

#### 🔒 SSL证书
```
是否安装 Let's Encrypt SSL 证书？(y/n)
默认: y
```
- 需要先配置域名
- 自动配置HTTPS访问
- 自动续期证书

## 🎯 部署完成后

### 📍 访问地址
- **域名访问**: `https://your-domain.com`
- **IP访问**: `http://your-server-ip`
- **直接端口**: `http://your-server-ip:5000`

### 🛠️ 服务管理
```bash
# 查看服务状态
systemctl status clash-converter

# 启动服务
systemctl start clash-converter

# 停止服务
systemctl stop clash-converter

# 重启服务
systemctl restart clash-converter

# 查看日志
journalctl -u clash-converter -f
```

### 📁 重要文件位置
- **项目目录**: `/opt/clash-converter/`
- **日志文件**: `/var/log/clash-converter/`
- **Nginx配置**: `/etc/nginx/sites-available/clash-converter`
- **系统服务**: `/etc/systemd/system/clash-converter.service`

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看详细错误日志
journalctl -u clash-converter -n 50
```

#### 2. 端口无法访问
```bash
# 检查防火墙状态
ufw status  # Ubuntu
firewall-cmd --list-all  # CentOS

# 手动开放端口
ufw allow 5000/tcp  # Ubuntu
firewall-cmd --permanent --add-port=5000/tcp && firewall-cmd --reload  # CentOS
```

#### 3. Nginx配置错误
```bash
# 测试Nginx配置
nginx -t

# 查看Nginx日志
tail -f /var/log/nginx/error.log
```

#### 4. SSL证书问题
```bash
# 手动申请证书
certbot --nginx -d your-domain.com

# 查看证书状态
certbot certificates
```

### 重新部署
如果需要重新部署：
```bash
# 停止服务
systemctl stop clash-converter

# 删除安装目录
rm -rf /opt/clash-converter

# 重新运行部署脚本
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

## 🌟 推荐云服务商

### 🆓 免费选项
1. **Oracle Cloud Always Free**
   - 永久免费1核1GB服务器
   - 每月10TB流量
   - 适合个人使用

2. **Google Cloud Free Tier**
   - 12个月免费试用
   - $300免费额度
   - 适合测试使用

3. **AWS Free Tier**
   - 12个月免费试用
   - t2.micro实例
   - 适合学习使用

### 💰 付费推荐
1. **腾讯云** - 国内访问速度快
2. **阿里云** - 稳定性好
3. **DigitalOcean** - 性价比高
4. **Vultr** - 全球节点多

## 🔐 安全建议

### 基础安全
- 修改SSH默认端口
- 禁用root密码登录
- 配置SSH密钥登录
- 定期更新系统

### 高级安全
- 配置fail2ban防暴力破解
- 使用云服务商的安全组
- 定期备份数据
- 监控异常访问

## 📞 技术支持

如遇到问题，请提供：
1. 服务器系统版本：`cat /etc/os-release`
2. 错误日志：`journalctl -u clash-converter -n 20`
3. 网络测试：`curl http://localhost:5000/api/ping`
4. 服务状态：`systemctl status clash-converter` 