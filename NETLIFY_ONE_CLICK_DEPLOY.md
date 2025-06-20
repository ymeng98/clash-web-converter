# 🚀 Clash Web Converter - Netlify 一键部署

## ⚡ 30秒部署完成！

您的项目已经完全准备好在Netlify上部署了！

### 🎯 项目状态
- ✅ **代码已推送** - GitHub仓库：`https://github.com/ymeng98/clash-web-converter`
- ✅ **Netlify配置完成** - `netlify.toml` 已配置
- ✅ **无服务器函数就绪** - 5个API端点已准备
- ✅ **静态文件就绪** - Web界面完全可用

## 🌟 一键部署按钮

点击下面的按钮即可一键部署到Netlify：

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/ymeng98/clash-web-converter)

## 📋 手动部署步骤（如果按钮无效）

### 1. 登录Netlify
- 访问：https://app.netlify.com
- 点击 "Log in with GitHub"

### 2. 创建新站点
- 点击 "New site from Git"
- 选择 "Deploy with GitHub"
- 搜索并选择：`clash-web-converter`

### 3. 配置设置（已自动配置）
项目已包含 `netlify.toml` 文件，设置会自动应用：
```toml
[build]
  publish = "public"
  
[functions]
  directory = "netlify/functions"
```

### 4. 点击部署
- 点击 "Deploy site"
- 等待2-3分钟部署完成

## 🎉 部署完成后

您将获得一个类似这样的网址：
```
https://amazing-clash-converter-123456.netlify.app
```

### 🔧 可用的API端点

部署完成后，以下API将可用：

| 端点 | 功能 | 方法 |
|------|------|------|
| `/api/convert-url` | 转换订阅链接 | POST |
| `/api/convert-file` | 转换上传文件 | POST |
| `/sub/{filename}` | 订阅服务 | GET |
| `/download/{filename}` | 文件下载 | GET |
| `/api/ping` | 健康检查 | GET |

### 🎯 使用方法

1. **直接访问Web界面**
   - 打开您的Netlify网址
   - 使用现代化的Web界面转换配置

2. **API调用示例**
   ```bash
   # 转换订阅链接
   curl -X POST https://your-site.netlify.app/api/convert-url \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-subscription-url"}'
   ```

3. **订阅链接使用**
   - 转换完成后获得订阅链接
   - 在Clash客户端中添加订阅
   - 享受稳定的代理服务

## 🔧 自定义域名（可选）

如果您有自己的域名：

1. 在Netlify控制台中点击 "Domain settings"
2. 点击 "Add custom domain"
3. 输入您的域名
4. 按照提示配置DNS记录

## 🛠️ 故障排除

### 部署失败？
- 确保GitHub仓库是公开的
- 检查netlify.toml文件是否存在
- 查看部署日志获取错误信息

### 函数不工作？
- 检查 `netlify/functions/` 目录是否包含所有JS文件
- 查看函数日志了解具体错误

### 网站无法访问？
- 检查部署状态是否为 "Published"
- 确认自定义域名DNS设置正确

## 💡 优势总结

使用Netlify部署的优势：
- ✅ **永久免费** - 免费计划足够使用
- ✅ **全球CDN** - 访问速度超快
- ✅ **自动HTTPS** - 安全访问
- ✅ **自动部署** - Git推送自动更新
- ✅ **无服务器** - 无需管理服务器

## 🎊 恭喜！

您的Clash代理转换器现在已经在云端运行了！

🌐 **分享您的转换器**：将Netlify网址分享给朋友
📱 **移动端访问**：手机浏览器完美支持
🔄 **自动更新**：推送代码到GitHub自动更新

---

**🚀 享受您的云端代理转换器吧！** 