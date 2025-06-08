# 🌐 公网部署指南

## 问题说明

当前的502 Bad Gateway错误是因为Clash客户端无法访问运行在本地的服务。有两种解决方案：

## 🚀 方案一：内网穿透（最简单）

### 1. 使用 ngrok（推荐）

#### 下载安装
1. 访问 https://ngrok.com/download
2. 注册免费账号
3. 下载Windows版本
4. 解压 `ngrok.exe` 到项目目录

#### 获取认证令牌
1. 登录 https://dashboard.ngrok.com/
2. 复制你的认证令牌
3. 运行命令：`ngrok authtoken 你的令牌`

#### 启动服务
```bash
# 双击运行
start-with-ngrok.bat
```

#### 使用步骤
1. 启动后会显示类似：`https://abc123.ngrok.io -> http://localhost:5000`
2. 用这个公网地址访问Web界面
3. 生成的订阅链接会自动使用公网地址
4. 手机可以直接使用订阅链接

### 2. 使用 frp（免费替代）

#### 下载 frp
```bash
# 下载地址
https://github.com/fatedier/frp/releases
```

#### 配置文件 frpc.ini
```ini
[common]
server_addr = [免费frp服务器地址]
server_port = 7000
token = [服务器token]

[clash-converter]
type = http
local_ip = 127.0.0.1
local_port = 5000
custom_domains = [分配的域名]
```

## 🏗️ 方案二：云服务器部署（推荐生产环境）

### 免费云服务器选项

#### 1. Oracle Cloud（推荐）
- **优势**：永久免费，配置好
- **配置**：1 OCPU, 1GB RAM
- **注册**：https://cloud.oracle.com/
- **特点**：需要信用卡验证但不收费

#### 2. Google Cloud Platform
- **优势**：300美元免费额度
- **配置**：e2-micro 实例
- **注册**：https://cloud.google.com/
- **特点**：12个月免费

#### 3. AWS EC2
- **优势**：t2.micro 免费一年
- **配置**：1 vCPU, 1GB RAM
- **注册**：https://aws.amazon.com/
- **特点**：需要信用卡

### 部署步骤

#### 1. 创建服务器
1. 选择Ubuntu 20.04 LTS
2. 开放5000端口
3. 配置SSH密钥

#### 2. 上传代码
```bash
# 方法1：使用git
git clone https://github.com/你的用户名/clash-web-converter.git

# 方法2：使用scp上传
scp -r clash-web-converter/ user@服务器IP:/home/user/
```

#### 3. 执行部署脚本
```bash
chmod +x deploy-cloud.sh
./deploy-cloud.sh
```

#### 4. 配置域名（可选）
```bash
# 如果有域名，配置A记录指向服务器IP
# 然后修改app.py中的host配置
```

## 🔧 生产环境优化

### 1. 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. 配置HTTPS
```bash
# 使用Certbot获取免费SSL证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 配置自动重启
```bash
# 已在deploy-cloud.sh中配置
sudo systemctl enable clash-converter
```

## 📱 使用说明

### 通过公网访问
1. 访问公网地址，如：`https://abc123.ngrok.io`
2. 转换配置文件
3. 复制订阅链接
4. 在任何设备的Clash中使用

### 订阅链接格式
```
# ngrok示例
https://abc123.ngrok.io/sub/clash-stable-20241201_143022.yaml

# 云服务器示例  
http://your-server-ip:5000/sub/clash-stable-20241201_143022.yaml
```

## ⚠️ 注意事项

### 安全建议
1. **不要**在生产环境使用Debug模式
2. 配置防火墙只开放必要端口
3. 定期更新系统和依赖
4. 考虑添加访问密码保护

### 性能优化
1. 使用Gunicorn多进程
2. 配置Nginx静态文件缓存
3. 设置合理的文件上传限制

### 监控建议
1. 配置日志轮转
2. 监控服务器资源使用
3. 设置服务状态监控

## 🆘 故障排除

### ngrok相关
```bash
# 检查ngrok状态
curl http://localhost:4040/api/tunnels

# 重启ngrok
pkill ngrok
ngrok http 5000
```

### 云服务器相关
```bash
# 检查服务状态
sudo systemctl status clash-converter

# 查看日志
sudo journalctl -u clash-converter -f

# 重启服务
sudo systemctl restart clash-converter
```

### 防火墙问题
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
``` 