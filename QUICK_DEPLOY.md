# 🚀 解决502错误 - 快速部署指南

## ❌ 问题说明
你遇到的502 Bad Gateway错误是因为Clash客户端无法访问运行在本地(localhost)的服务。

## ✅ 两种解决方案

### 🎯 方案一：内网穿透（5分钟搞定）

#### 1. 下载 ngrok
- 访问：https://ngrok.com/download
- 注册免费账号，下载Windows版本
- 将 `ngrok.exe` 放到项目目录中

#### 2. 设置认证
```bash
# 在项目目录运行
ngrok authtoken 你的令牌
```

#### 3. 启动服务
```bash
# 双击运行
start-with-ngrok.bat
```

#### 4. 获取公网地址
启动后会显示类似：
```
https://abc123.ngrok.io -> http://localhost:5000
```

#### 5. 使用公网地址
- 用 `https://abc123.ngrok.io` 访问网页
- 生成的订阅链接会自动使用公网地址
- 手机可以直接使用订阅链接 ✅

---

### 🏗️ 方案二：免费云服务器（长期稳定）

#### 推荐：Oracle Cloud 永久免费
1. **注册**：https://cloud.oracle.com/
2. **创建实例**：Ubuntu 20.04，开放5000端口
3. **上传代码**：
   ```bash
   scp -r clash-web-converter/ user@服务器IP:/home/user/
   ```
4. **一键部署**：
   ```bash
   chmod +x deploy-cloud.sh
   ./deploy-cloud.sh
   ```

## 🎯 立即可用的解决方案

### 使用 ngrok（推荐新手）

1. **下载 ngrok**：https://ngrok.com/download
2. **解压到项目目录**
3. **获取认证令牌**：https://dashboard.ngrok.com/
4. **运行命令**：
   ```bash
   # 设置令牌
   ngrok authtoken 你的令牌
   
   # 启动Python服务（终端1）
   python app.py
   
   # 启动ngrok（终端2）
   ngrok http 5000
   ```
5. **使用公网地址访问网页**
6. **复制订阅链接到Clash** ✅

### 测试验证
- 生成订阅链接后，用手机浏览器访问订阅链接
- 应该能下载到配置文件，而不是502错误

## 💡 为什么会有502错误？

- **本地访问**：`http://localhost:5000` ✅ 电脑可以访问
- **手机访问**：`http://localhost:5000` ❌ 手机无法访问
- **订阅链接**：`http://localhost:5000/sub/file.yaml` ❌ Clash无法访问

## ✅ 解决后的效果

- **本地访问**：`https://abc123.ngrok.io` ✅ 电脑可以访问
- **手机访问**：`https://abc123.ngrok.io` ✅ 手机可以访问
- **订阅链接**：`https://abc123.ngrok.io/sub/file.yaml` ✅ Clash可以访问

## 🎉 最终效果
使用ngrok后，你的订阅链接格式会变成：
```
https://abc123.ngrok.io/sub/clash-stable-20241201_143022.yaml
```

这个链接可以在任何设备、任何网络环境下使用！🚀 