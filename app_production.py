#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash稳定中转SOCKS代理转换器 - Web应用（生产环境版本）
提供用户友好的Web界面
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
import logging
from converter import ClashWebConverter
from converter_openwrt import ClashOpenWrtConverter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clash_converter_secret_key_2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制16MB上传

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'yaml', 'yml', 'txt'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Favicon处理"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/convert/url', methods=['POST'])
def convert_from_url():
    """从订阅链接转换配置的API接口"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        mode = data.get('mode', 'standard')  # standard 或 openwrt
        
        if not url:
            return jsonify({'success': False, 'message': '请提供有效的订阅链接'})
        
        if not (url.startswith('http://') or url.startswith('https://')):
            return jsonify({'success': False, 'message': '请提供有效的HTTP/HTTPS链接'})
        
        # 获取当前请求的主机信息，用于生成订阅链接
        host_url = request.host_url.rstrip('/')
        
        # 如果是通过反向代理访问，使用X-Forwarded-Host
        if 'X-Forwarded-Host' in request.headers:
            protocol = 'https' if request.headers.get('X-Forwarded-Proto', 'http') == 'https' else 'http'
            host_url = f"{protocol}://{request.headers['X-Forwarded-Host']}"
        
        app.logger.info(f"URL转换请求: {url}, 模式: {mode}, 主机: {host_url}")
        
        if mode == 'openwrt':
            converter = ClashOpenWrtConverter()
            result = converter.convert_for_openwrt(url, is_url=True)
        else:
            converter = ClashWebConverter()
            result = converter.convert_from_url(url, host_url=host_url)
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"URL转换错误: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'})

@app.route('/api/convert/file', methods=['POST'])
def convert_from_file():
    """从上传文件转换配置的API接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未找到上传文件'})
        
        file = request.files['file']
        mode = request.form.get('mode', 'standard')  # standard 或 openwrt
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '只支持 .yaml, .yml, .txt 格式的文件'})
        
        # 保存上传的文件到临时目录
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), f"upload_{uuid.uuid4().hex}_{filename}")
        file.save(temp_path)
        
        # 获取当前请求的主机信息，用于生成订阅链接
        host_url = request.host_url.rstrip('/')
        
        # 如果是通过反向代理访问，使用X-Forwarded-Host
        if 'X-Forwarded-Host' in request.headers:
            protocol = 'https' if request.headers.get('X-Forwarded-Proto', 'http') == 'https' else 'http'
            host_url = f"{protocol}://{request.headers['X-Forwarded-Host']}"
        
        app.logger.info(f"文件转换请求: {filename}, 模式: {mode}, 主机: {host_url}")
        
        # 转换配置
        if mode == 'openwrt':
            converter = ClashOpenWrtConverter()
            result = converter.convert_for_openwrt(temp_path, is_url=False)
        else:
            converter = ClashWebConverter()
            result = converter.convert_from_file(temp_path, host_url=host_url)
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"文件转换错误: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的配置文件"""
    try:
        downloads_dir = os.path.join(app.root_path, 'static', 'downloads')
        return send_from_directory(downloads_dir, filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"文件下载错误: {str(e)}")
        return f"文件下载失败: {str(e)}", 404

@app.route('/sub/<filename>')
def subscribe_file(filename):
    """订阅链接服务"""
    try:
        downloads_dir = os.path.join(app.root_path, 'static', 'downloads')
        file_path = os.path.join(downloads_dir, filename)
        
        if not os.path.exists(file_path):
            app.logger.warning(f"订阅文件不存在: {filename}")
            return "订阅文件不存在", 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        app.logger.info(f"订阅文件访问: {filename}")
        
        return content, 200, {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Profile-Update-Interval': '24'  # 24小时更新间隔
        }
    except Exception as e:
        app.logger.error(f"订阅服务错误: {str(e)}")
        return f"订阅服务失败: {str(e)}", 500

@app.route('/api/ping')
def ping():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'Clash转换器服务正常运行'})

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    app.logger.error(f"内部服务器错误: {str(error)}")
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(error):
    """文件过大错误处理"""
    return jsonify({'success': False, 'message': '上传文件过大，请确保文件小于16MB'}), 413

if __name__ == '__main__':
    # 确保下载目录存在
    downloads_dir = os.path.join(app.root_path, 'static', 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # 生产环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Clash稳定中转SOCKS代理转换器 - 生产环境版")
    print("=" * 60)
    print(f"🌐 服务端口: {port}")
    print(f"🔧 调试模式: {debug}")
    print(f"📁 下载目录: {downloads_dir}")
    print("=" * 60)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=debug) 