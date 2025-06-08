# ⚡ 云服务器10分钟快速部署

## 🚀 一键命令（仅需1行）

```bash
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

## 📋 部署前准备

### 1. 购买云服务器
**推荐配置**：1核1GB，Ubuntu 20.04，10GB硬盘

**推荐服务商**：
- 🆓 **Oracle Cloud** - 永久免费
- 💰 **腾讯云** - 新人特惠 
- 💰 **阿里云** - 学生价优惠

### 2. 连接服务器
```bash
ssh root@your-server-ip
```

### 3. 运行部署命令
```bash
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

## ⚙️ 部署过程（5-10分钟）

脚本会自动：
1. ✅ 检测系统环境
2. ✅ 安装Python和依赖
3. ✅ 下载项目代码  
4. ✅ 配置系统服务
5. ✅ 设置防火墙
6. ✅ 安装Nginx（可选）
7. ✅ 配置SSL证书（可选）

## 🎯 部署完成

部署成功后显示访问地址：
```
🌐 访问地址：http://your-server-ip
📱 移动访问：http://your-server-ip
🔒 HTTPS访问：https://your-domain.com（如配置域名）
```

## 💡 快速使用

1. **打开浏览器** → 访问部署完成的地址
2. **粘贴订阅链接** → 开始转换
3. **复制订阅地址** → 导入Clash客户端
4. **享受稳定代理** → 完成！

## 🛠️ 常用管理命令

```bash
# 查看服务状态
systemctl status clash-converter

# 重启服务
systemctl restart clash-converter

# 查看日志
journalctl -u clash-converter -f
```

## 🔥 Oracle Cloud永久免费部署

### 申请Oracle Cloud账户
1. 访问：https://www.oracle.com/cloud/free/
2. 注册账户（需要信用卡验证，不扣费）
3. 创建VM实例：Ubuntu 20.04，1 OCPU，1GB内存

### 配置安全组
```bash
# 开放端口（Oracle Cloud控制台）
HTTP: 80
HTTPS: 443  
Custom: 5000
```

### 连接并部署
```bash
# SSH连接（使用提供的私钥）
ssh -i private-key.pem ubuntu@public-ip

# 切换到root用户
sudo su -

# 一键部署
curl -fsSL https://raw.githubusercontent.com/ymeng98/clash-web-converter/main/deploy-cloud-server.sh | bash
```

## ❓ 常见问题

### Q: 部署失败怎么办？
A: 检查网络连接，确保服务器可以访问GitHub

### Q: 无法访问网站？
A: 检查防火墙设置，确保端口已开放

### Q: 订阅链接502错误？
A: 正常现象，服务器部署成功后会自动解决

### Q: 想更换端口？
A: 重新运行脚本，选择自定义端口

## 🎉 部署成功后的优势

- ✅ **永久在线** - 24小时稳定运行
- ✅ **高速访问** - 云服务器带宽充足  
- ✅ **移动友好** - 手机随时随地使用
- ✅ **自动更新** - 订阅链接自动刷新
- ✅ **安全稳定** - 专业级服务器环境

立即开始你的云端代理转换之旅！🚀 