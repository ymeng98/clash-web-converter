# 🌐 Clash转换器 API 文档

## 概述

Clash稳定中转SOCKS代理转换器提供RESTful API接口，支持订阅链接和配置文件转换。

## 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`
- **编码**: `UTF-8`

## 认证

当前版本不需要认证，生产环境建议添加API密钥验证。

## API接口

### 1. 健康检查

检查服务运行状态。

**请求**
```http
GET /api/ping
```

**响应**
```json
{
    "status": "ok",
    "message": "Clash转换器服务正常运行"
}
```

### 2. 订阅链接转换

从机场订阅链接转换配置。

**请求**
```http
POST /api/convert/url
Content-Type: application/json

{
    "url": "https://example.com/subscribe?token=xxx",
    "mode": "standard"
}
```

**参数说明**
- `url` (string, 必需): 机场订阅链接
- `mode` (string, 可选): 转换模式
  - `"standard"`: 标准模式（默认）
  - `"openwrt"`: OpenWrt软路由模式

**响应示例**
```json
{
    "success": true,
    "message": "转换成功！",
    "stats": {
        "total_nodes": 50,
        "stable_nodes": 35,
        "filtered_nodes": 15
    },
    "regions": {
        "香港": ["🇭🇰 香港中转1", "🇭🇰 香港中转2"],
        "美国": ["🇺🇸 美国中转1"],
        "日本": ["🇯🇵 日本中转1", "🇯🇵 日本中转2"]
    },
    "download_url": "/download/clash-stable-20241206_143022.yaml",
    "filename": "clash-stable-20241206_143022.yaml"
}
```

### 3. 文件上传转换

上传配置文件进行转换。

**请求**
```http
POST /api/convert/file
Content-Type: multipart/form-data

file: [配置文件]
mode: standard
```

**参数说明**
- `file` (file, 必需): 配置文件（.yaml/.yml/.txt）
- `mode` (string, 可选): 转换模式（同上）

**文件限制**
- 大小限制: 16MB
- 支持格式: `.yaml`, `.yml`, `.txt`

**响应格式**
同订阅链接转换接口。

### 4. 异步任务状态查询

查询异步转换任务状态。

**请求**
```http
GET /api/task/{task_id}
```

**响应示例**
```json
{
    "task_id": "uuid-string",
    "status": "completed",
    "progress": 100.0,
    "result": {
        "success": true,
        "download_url": "/download/file.yaml"
    },
    "created_at": "2024-12-06T14:30:22Z",
    "completed_at": "2024-12-06T14:30:25Z"
}
```

**状态说明**
- `pending`: 等待处理
- `running`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

### 5. 文件下载

下载生成的配置文件。

**请求**
```http
GET /download/{filename}
```

**响应**
- 成功: 返回文件内容，`Content-Type: application/octet-stream`
- 失败: 返回404错误

## 错误响应

所有API在出错时返回统一格式：

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

**常见错误码**
- `400`: 请求参数错误
- `413`: 上传文件过大
- `429`: 请求频率超限
- `500`: 服务器内部错误

## 使用示例

### JavaScript

```javascript
// 订阅链接转换
async function convertFromUrl(url, mode = 'standard') {
    const response = await fetch('/api/convert/url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, mode }),
    });
    
    return await response.json();
}

// 文件上传转换
async function convertFromFile(file, mode = 'standard') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);
    
    const response = await fetch('/api/convert/file', {
        method: 'POST',
        body: formData,
    });
    
    return await response.json();
}
```

### Python

```python
import requests

# 订阅链接转换
def convert_from_url(url, mode='standard'):
    response = requests.post('http://localhost:5000/api/convert/url', 
                           json={'url': url, 'mode': mode})
    return response.json()

# 文件上传转换
def convert_from_file(file_path, mode='standard'):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'mode': mode}
        response = requests.post('http://localhost:5000/api/convert/file',
                               files=files, data=data)
    return response.json()
```

### cURL

```bash
# 订阅链接转换
curl -X POST http://localhost:5000/api/convert/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/subscribe", "mode": "standard"}'

# 文件上传转换
curl -X POST http://localhost:5000/api/convert/file \
  -F "file=@config.yaml" \
  -F "mode=standard"

# 健康检查
curl http://localhost:5000/api/ping
```

## 速率限制

为防止滥用，API接口设有速率限制：

- 默认限制: 每小时100次请求
- 转换接口: 每分钟10次请求
- 下载接口: 每分钟50次请求

超出限制将返回429错误。

## 开发注意事项

1. **超时设置**: 转换可能需要较长时间，建议设置30秒以上超时
2. **文件大小**: 上传文件不要超过16MB
3. **缓存**: 相同订阅链接1小时内会返回缓存结果
4. **清理**: 生成的文件会在24小时后自动清理

## 更新日志

### v1.0.0 (2024-12-06)
- 初始版本发布
- 支持订阅链接和文件转换
- 添加OpenWrt模式支持
- 实现异步任务处理 