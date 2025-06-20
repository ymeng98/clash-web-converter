const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/octet-stream'
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
    
    if (!filename) {
      return {
        statusCode: 404,
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          success: false,
          message: '文件不存在'
        })
      };
    }

    // 构建文件路径
    const filePath = path.join(__dirname, '../../public/downloads', filename);
    
    if (!fs.existsSync(filePath)) {
      return {
        statusCode: 404,
        headers: {
          ...headers,
          'Content-Type': 'text/plain'
        },
        body: '文件不存在'
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
    console.error('文件下载错误:', error);
    
    return {
      statusCode: 500,
      headers: {
        ...headers,
        'Content-Type': 'text/plain'
      },
      body: `文件下载失败: ${error.message}`
    };
  }
}; 