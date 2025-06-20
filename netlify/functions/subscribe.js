const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'text/plain; charset=utf-8',
    'Profile-Update-Interval': '24'
  };

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        success: false, 
        message: 'Method not allowed' 
      })
    };
  }

  try {
    // 从路径中提取文件名
    const filename = event.path.split('/').pop();
    
    if (!filename || !filename.endsWith('.yaml')) {
      return {
        statusCode: 404,
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          success: false,
          message: '订阅文件不存在'
        })
      };
    }

    // 构建文件路径（在Netlify环境中静态文件路径）
    const filePath = path.join(__dirname, '../../public/downloads', filename);
    
    if (!fs.existsSync(filePath)) {
      return {
        statusCode: 404,
        headers: {
          ...headers,
          'Content-Type': 'text/plain'
        },
        body: '订阅文件不存在'
      };
    }

    // 读取文件内容
    const content = fs.readFileSync(filePath, 'utf8');

    return {
      statusCode: 200,
      headers: {
        ...headers,
        'Content-Disposition': `attachment; filename="${filename}"`
      },
      body: content
    };

  } catch (error) {
    console.error('订阅服务错误:', error);
    
    return {
      statusCode: 500,
      headers: {
        ...headers,
        'Content-Type': 'text/plain'
      },
      body: `订阅服务失败: ${error.message}`
    };
  }
}; 