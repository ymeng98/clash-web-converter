#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash转换器基类
将公共功能抽象出来，避免代码重复
"""

import yaml
import re
import requests
import os
import tempfile
import uuid
from typing import Dict, List, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

class BaseClashConverter(ABC):
    """Clash转换器基类"""
    
    def __init__(self):
        self.downloads_dir = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        # 地区映射配置
        self.region_patterns = {
            '🇭🇰': '香港', '🇺🇸': '美国', '🇯🇵': '日本',
            '🇸🇬': '新加坡', '🇹🇼': '台湾', '🇰🇷': '韩国',
            '🇬🇧': '英国', '🇨🇦': '加拿大', '🇦🇺': '澳大利亚',
            '🇩🇪': '德国', '🇫🇷': '法国', '🇳🇱': '荷兰',
            '🇷🇺': '俄罗斯', '🇮🇳': '印度', '🇹🇭': '泰国',
            '🇲🇾': '马来西亚', '🇵🇭': '菲律宾', '🇻🇳': '越南'
        }
        
        self.text_patterns = {
            r'(?i)(hong\s*kong|hk|香港|港)': '香港',
            r'(?i)(united\s*states|usa?|us|美国|美)': '美国',
            r'(?i)(japan|jp|日本|日)': '日本',
            r'(?i)(singapore|sg|新加坡|新)': '新加坡',
            r'(?i)(taiwan|tw|台湾|台)': '台湾',
            r'(?i)(korea|kr|韩国|韩)': '韩国',
            r'(?i)(britain|uk|英国|英)': '英国',
            r'(?i)(canada|ca|加拿大|加)': '加拿大',
            r'(?i)(australia|au|澳大利亚|澳洲|澳)': '澳大利亚',
            r'(?i)(germany|de|德国|德)': '德国',
            r'(?i)(france|fr|法国|法)': '法国',
            r'(?i)(netherlands|nl|荷兰|荷)': '荷兰',
            r'(?i)(russia|ru|俄罗斯|俄)': '俄罗斯',
            r'(?i)(india|in|印度)': '印度',
            r'(?i)(thailand|th|泰国|泰)': '泰国',
            r'(?i)(malaysia|my|马来西亚|马来|大马)': '马来西亚'
        }
        
        # 排除关键词
        self.exclude_patterns = [
            'direct', '直连', '直通', 'info', '信息', '通知', '公告',
            'test', '测试', 'speed', '网速', 'temp', '临时', 'backup', '备用',
            'ipv6', 'v6', '剩余流量', '套餐到期', '官网', '节点异常', '刷新失败'
        ]
        
        # 支持的代理类型
        self.supported_types = ['trojan', 'ss', 'vmess', 'vless', 'hysteria2']
    
    def download_config(self, url: str) -> Tuple[bool, str, str]:
        """从URL下载配置文件"""
        try:
            user_agents = [
                "ClashforWindows/1.0",
                "Clash/1.0",
                "ClashX/1.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
            
            for ua in user_agents:
                try:
                    response = requests.get(
                        url,
                        headers={"User-Agent": ua},
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        temp_file = os.path.join(
                            tempfile.gettempdir(), 
                            f"clash_temp_{uuid.uuid4().hex}.yaml"
                        )
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        return True, temp_file, ""
                    elif response.status_code == 404:
                        return False, "", "404错误 - 链接不存在或已过期"
                    else:
                        continue
                        
                except requests.exceptions.RequestException:
                    continue
            
            return False, "", "所有下载尝试均失败，请检查网络连接或链接有效性"
            
        except Exception as e:
            return False, "", f"下载出错: {str(e)}"
    
    def load_config(self, file_path: str) -> Tuple[bool, Dict[str, Any], str]:
        """加载YAML配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 验证配置结构
            if not isinstance(config, dict):
                return False, {}, "配置文件格式错误：根节点必须是字典"
            
            if 'proxies' not in config:
                return False, {}, "配置文件格式错误：缺少proxies字段"
            
            return True, config, ""
        except FileNotFoundError:
            return False, {}, f"文件不存在: {file_path}"
        except yaml.YAMLError as e:
            return False, {}, f"YAML解析错误: {str(e)}"
        except Exception as e:
            return False, {}, f"文件读取错误: {str(e)}"
    
    def extract_region_from_name(self, name: str) -> str:
        """从节点名称中提取地区信息"""
        # 优先匹配emoji旗帜
        for emoji, region in self.region_patterns.items():
            if emoji in name:
                return region
        
        # 然后匹配文字标识
        for pattern, region in self.text_patterns.items():
            if re.search(pattern, name):
                return region
        
        return '其他'
    
    def is_stable_transit_node(self, proxy: Dict[str, Any]) -> bool:
        """判断是否为稳定的中转节点"""
        name = proxy.get('name', '').lower()
        proxy_type = proxy.get('type', '').lower()
        server = proxy.get('server', '')
        
        # 检查是否包含排除关键词
        for pattern in self.exclude_patterns:
            if pattern in name:
                return False
        
        # 只保留支持的协议
        if proxy_type not in self.supported_types:
            return False
        
        # 检查是否为IPv6地址（简单判断）
        if ':' in server and '[' not in server:
            return False
        
        # 必须有有效的服务器地址
        if not server or server in ['127.0.0.1', 'localhost']:
            return False
        
        return True
    
    def extract_stable_proxies(self, config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """提取稳定的中转节点"""
        proxies = config.get('proxies', [])
        stable_proxies = []
        stats = {
            'total_nodes': len(proxies),
            'stable_nodes': 0,
            'filtered_nodes': 0
        }
        
        for proxy in proxies:
            if self.is_stable_transit_node(proxy):
                stable_proxies.append(proxy)
        
        stats['stable_nodes'] = len(stable_proxies)
        stats['filtered_nodes'] = stats['total_nodes'] - stats['stable_nodes']
        
        return stable_proxies, stats
    
    def group_proxies_by_region(self, proxies: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """按地区分组节点"""
        region_groups = {}
        
        for proxy in proxies:
            name = proxy['name']
            region = self.extract_region_from_name(name)
            
            if region not in region_groups:
                region_groups[region] = []
            
            region_groups[region].append(name)
        
        return region_groups
    
    def save_config(self, config: Dict[str, Any], filename: str = None) -> str:
        """保存配置文件"""
        if filename is None:
            filename = f"clash-converted-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        
        file_path = os.path.join(self.downloads_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return file_path
    
    @abstractmethod
    def create_config(self, proxies: List[Dict[str, Any]], region_groups: Dict[str, List[str]]) -> Dict[str, Any]:
        """创建配置文件（子类实现）"""
        pass
    
    def convert_config(self, source: str, is_url: bool = True) -> Dict[str, Any]:
        """转换配置的通用流程"""
        result = {
            'success': False,
            'message': '',
            'stats': {},
            'regions': {},
            'download_url': '',
            'filename': ''
        }
        
        try:
            if is_url:
                # 从URL下载配置
                success, temp_file, error = self.download_config(source)
                if not success:
                    result['message'] = error
                    return result
                config_file = temp_file
            else:
                # 本地文件
                config_file = source
            
            # 加载配置
            success, config, error = self.load_config(config_file)
            if not success:
                result['message'] = error
                return result
            
            # 提取稳定节点
            stable_proxies, stats = self.extract_stable_proxies(config)
            if not stable_proxies:
                result['message'] = "未找到稳定的中转节点"
                return result
            
            # 按地区分组
            region_groups = self.group_proxies_by_region(stable_proxies)
            
            # 生成配置（子类实现）
            converted_config = self.create_config(stable_proxies, region_groups)
            
            # 保存配置
            filename = self.get_filename()
            file_path = self.save_config(converted_config, filename)
            
            # 清理临时文件
            if is_url:
                try:
                    os.remove(config_file)
                except:
                    pass
            
            result.update({
                'success': True,
                'message': '转换成功！',
                'stats': stats,
                'regions': region_groups,
                'download_url': f'/download/{filename}',
                'filename': filename
            })
            
        except Exception as e:
            result['message'] = f"转换过程出错: {str(e)}"
        
        return result
    
    @abstractmethod
    def get_filename(self) -> str:
        """获取保存的文件名（子类实现）"""
        pass 