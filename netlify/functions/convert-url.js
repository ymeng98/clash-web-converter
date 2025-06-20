const { execSync } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  // 设置CORS头
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // 处理OPTIONS请求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ message: 'OK' })
    };
  }

  // 只允许POST请求
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
    // 解析请求数据
    const body = JSON.parse(event.body);
    const { url, mode = 'standard' } = body;

    if (!url) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          message: '请提供有效的订阅链接'
        })
      };
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          success: false,
          message: '请提供有效的HTTP/HTTPS链接'
        })
      };
    }

    // 构建Python脚本路径
    const scriptDir = path.join(__dirname, '../../');
    const pythonScript = path.join(scriptDir, 'converter_cli.py');

    // 获取当前域名用于生成订阅链接
    const hostUrl = `https://${event.headers.host}`;
    
    // 执行Python转换脚本
    const command = `python "${pythonScript}" --url "${url}" --host "${hostUrl}"`;
    const result = execSync(command, { 
      encoding: 'utf8',
      cwd: scriptDir,
      timeout: 30000 // 30秒超时
    });

    const convertResult = JSON.parse(result);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(convertResult)
    };

  } catch (error) {
    console.error('转换错误:', error);
    
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