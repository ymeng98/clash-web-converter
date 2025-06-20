#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash稳定中转SOCKS代理转换器 - 命令行版本
用于Netlify Functions调用
"""

import sys
import json
import argparse
from converter import ClashWebConverter

def main():
    parser = argparse.ArgumentParser(description='Clash配置转换器')
    parser.add_argument('--url', help='订阅链接')
    parser.add_argument('--file', help='配置文件路径')
    parser.add_argument('--host', default='http://localhost:5000', help='主机地址')
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        print(json.dumps({
            'success': False,
            'message': '必须提供 --url 或 --file 参数'
        }))
        sys.exit(1)
    
    converter = ClashWebConverter()
    
    try:
        if args.url:
            result = converter.convert_from_url(args.url, args.host)
        elif args.file:
            result = converter.convert_from_file(args.file, args.host)
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'转换失败: {str(e)}'
        }, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    main() 