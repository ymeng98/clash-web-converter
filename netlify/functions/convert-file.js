const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ message: 'OK' })
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: 'Method not allowed' 
      })
    };
  }

  try {
    // 处理multipart/form-data
    const body = event.body;
    const isBase64Encoded = event.isBase64Encoded;
    
    // 简单的文件上传处理（这里需要更完整的multipart解析）
    const boundary = event.headers['content-type'].split('boundary=')[1];
    
    if (!boundary) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          message: '无效的文件上传格式'
        })
      };
    }

    // 解析multipart数据（简化版本）
    let fileContent = '';
    let filename = '';
    let mode = 'standard';

    // 这里应该有更完整的multipart解析，暂时使用简化版本
    const parts = body.split(`--${boundary}`);
    
    for (const part of parts) {
      if (part.includes('name="file"')) {
        const lines = part.split('\r\n');
        const contentIndex = lines.findIndex(line => line.trim() === '') + 1;
        fileContent = lines.slice(contentIndex).join('\r\n').trim();
        
        // 提取文件名
        const dispositionLine = lines.find(line => line.includes('Content-Disposition'));
        if (dispositionLine) {
          const filenameMatch = dispositionLine.match(/filename="([^"]+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
      } else if (part.includes('name="mode"')) {
        const lines = part.split('\r\n');
        const contentIndex = lines.findIndex(line => line.trim() === '') + 1;
        mode = lines.slice(contentIndex).join('\r\n').trim();
      }
    }

    if (!fileContent || !filename) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          message: '未找到有效的上传文件'
        })
      };
    }

    // 检查文件扩展名
    const allowedExtensions = ['.yaml', '.yml', '.txt'];
    const ext = path.extname(filename).toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          message: '只支持 .yaml, .yml, .txt 格式的文件'
        })
      };
    }

    // 创建临时文件
    const tempDir = os.tmpdir();
    const tempFile = path.join(tempDir, `upload_${Date.now()}_${filename}`);
    fs.writeFileSync(tempFile, fileContent, 'utf8');

    try {
      // 构建Python脚本路径
      const scriptDir = path.join(__dirname, '../../');
      const pythonScript = path.join(scriptDir, 'converter_cli.py');

      // 获取当前域名用于生成订阅链接
      const hostUrl = `https://${event.headers.host}`;
      
      // 执行Python转换脚本
      const command = `python "${pythonScript}" --file "${tempFile}" --host "${hostUrl}"`;
      const result = execSync(command, { 
        encoding: 'utf8',
        cwd: scriptDir,
        timeout: 30000
      });

      const convertResult = JSON.parse(result);

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(convertResult)
      };

    } finally {
      // 清理临时文件
      try {
        fs.unlinkSync(tempFile);
      } catch (e) {
        console.error('清理临时文件失败:', e);
      }
    }

  } catch (error) {
    console.error('文件转换错误:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        message: `服务器错误: ${error.message}`
      })
    };
  }
}; 