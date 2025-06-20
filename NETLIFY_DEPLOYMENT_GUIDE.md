# 🌐 Clash Web Converter - Netlify 部署指南

## 📋 项目概述

已为您完成clash-web-converter到Netlify的完整转换！项目已从Flask应用转换为Netlify Serverless Functions架构。

## 🏗️ 项目结构

```
clash-web-converter/
├── netlify.toml              # Netlify配置文件
├── package.json              # Node.js依赖配置
├── runtime.txt               # Python运行时版本
├── requirements.txt          # Python依赖
├── converter_cli.py          # 命令行转换器
├── public/                   # 静态文件目录
│   ├── index.html           # 主页面
│   ├── css/                 # 样式文件
│   ├── js/                  # JavaScript文件
│   └── downloads/           # 下载文件目录
├── netlify/functions/       # Serverless Functions
│   ├── convert-url.js       # URL转换API
│   ├── convert-file.js      # 文件转换API
│   ├── subscribe.js         # 订阅服务API
│   ├── download.js          # 文件下载API
│   └── ping.js              # 健康检查API
└── 原Flask文件...           # 原始Flask文件保留
```

## 🚀 部署方法

### 方法1：通过GitHub自动部署（推荐）

1. **创建GitHub仓库**
   - 登录GitHub，创建新仓库
   - 将项目代码推送到GitHub

2. **连接Netlify**
   - 登录 [Netlify Dashboard](https://app.netlify.com)
   - 点击 "New site from Git"
   - 选择GitHub并授权
   - 选择您的clash-web-converter仓库

3. **配置构建设置**
   - Build command: `echo 'Building for Netlify'`
   - Publish directory: `public`
   - Functions directory: `netlify/functions`

### 方法2：手动文件上传

1. **准备部署文件**
   - 将整个 `clash-web-converter` 目录打包为ZIP文件

2. **上传到Netlify**
   - 登录 [Netlify Dashboard](https://app.netlify.com)
   - 拖拽ZIP文件到 "Want to deploy a new site without connecting to Git?" 区域

## ⚙️ API 端点

部署完成后，您的API端点将是：

- **转换URL**: `POST /api/convert-url`
- **转换文件**: `POST /api/convert-file`  
- **订阅服务**: `GET /sub/{filename}`
- **文件下载**: `GET /download/{filename}`
- **健康检查**: `GET /api/ping`

## 🔧 功能说明

### 1. URL转换 (`/api/convert-url`)
```javascript
// 请求示例
{
  "url": "https://example.com/subscribe",
  "mode": "standard"  // 或 "openwrt"
}

// 响应示例
{
  "success": true,
  "message": "转换成功！",
  "stats": {...},
  "regions": {...},
  "download_url": "/download/clash-stable-xxx.yaml",
  "subscribe_url": "https://yoursite.netlify.app/sub/clash-stable-xxx.yaml",
  "filename": "clash-stable-xxx.yaml"
}
```

### 2. 文件转换 (`/api/convert-file`)
- 支持 multipart/form-data 上传
- 接受 .yaml, .yml, .txt 格式文件
- 返回同样的转换结果格式

### 3. 订阅服务 (`/sub/{filename}`)
- 直接返回YAML配置文件内容
- 设置适当的Content-Type和缓存头
- 支持Clash客户端自动更新

## 🎯 使用示例

部署完成后，用户可以：

1. **通过Web界面**
   - 访问您的Netlify网站主页
   - 使用原有的Web界面功能

2. **直接API调用**
   ```bash
   # 转换订阅链接
   curl -X POST https://yoursite.netlify.app/api/convert-url \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/subscribe"}'
   ```

3. **订阅链接**
   ```
   https://yoursite.netlify.app/sub/clash-stable-xxx.yaml
   ```

## 🔍 测试部署

部署完成后，访问以下地址测试：

1. **主页**: `https://yoursite.netlify.app`
2. **健康检查**: `https://yoursite.netlify.app/api/ping`
3. **API文档**: 查看返回的JSON格式

## ⚠️ 重要提示

### 限制说明
- **Netlify Functions执行时限**: 10秒（免费版）
- **文件大小限制**: 6MB上传限制
- **并发限制**: 免费版125k请求/月

### 性能优化
- 大文件转换可能需要升级到付费版本
- 考虑使用Background Functions处理长时间任务
- 静态文件已自动CDN加速

### 环境变量
如果需要配置环境变量：
1. 在Netlify Dashboard中进入站点设置
2. 选择 "Environment variables"
3. 添加所需的环境变量

## 🎉 完成！

您的clash-web-converter现在已经成功转换为Netlify部署！所有原有功能都得到保留，并且获得了：

- ✅ **全球CDN加速**
- ✅ **自动HTTPS**
- ✅ **无服务器架构**
- ✅ **自动扩展**
- ✅ **免费托管**

## 📞 需要帮助？

如果在部署过程中遇到问题：

1. 检查Netlify的部署日志
2. 确认所有文件结构正确
3. 验证Python依赖是否完整
4. 查看Functions的错误日志

---

**🎊 恭喜！您的项目已经成功迁移到Netlify！** 