#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash稳定中转SOCKS代理转换器 - Web版本
功能：为Web界面提供转换服务
"""

import yaml
import re
import requests
import os
import tempfile
import uuid
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ClashWebConverter:
    def __init__(self):
        self.downloads_dir = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def download_config(self, url: str) -> Tuple[bool, str, str]:
        """
        从URL下载配置文件
        
        Returns:
            Tuple[bool, str, str]: (成功状态, 临时文件路径, 错误信息)
        """
        try:
            # 常用的User-Agent列表
            user_agents = [
                "ClashforWindows/1.0",
                "Clash/1.0",
                "ClashX/1.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
                        # 创建临时文件
                        temp_file = os.path.join(tempfile.gettempdir(), f"clash_temp_{uuid.uuid4().hex}.yaml")
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
        """
        加载YAML配置文件
        
        Returns:
            Tuple[bool, Dict, str]: (成功状态, 配置字典, 错误信息)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return True, config, ""
        except FileNotFoundError:
            return False, {}, f"文件不存在: {file_path}"
        except yaml.YAMLError as e:
            return False, {}, f"YAML解析错误: {str(e)}"
        except Exception as e:
            return False, {}, f"文件读取错误: {str(e)}"
    
    def extract_region_from_name(self, name: str) -> str:
        """从节点名称中提取地区信息"""
        # 地区标识映射表
        region_patterns = {
            '🇭🇰': '香港', '🇺🇸': '美国', '🇯🇵': '日本',
            '🇸🇬': '新加坡', '🇹🇼': '台湾', '🇰🇷': '韩国',
            '🇬🇧': '英国', '🇨🇦': '加拿大', '🇦🇺': '澳大利亚',
            '🇩🇪': '德国', '🇫🇷': '法国', '🇳🇱': '荷兰',
            '🇷🇺': '俄罗斯', '🇮🇳': '印度', '🇹🇭': '泰国',
            '🇲🇾': '马来西亚', '🇵🇭': '菲律宾', '🇻🇳': '越南'
        }
        
        text_patterns = {
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
        
        # 优先匹配emoji旗帜
        for emoji, region in region_patterns.items():
            if emoji in name:
                return region
        
        # 然后匹配文字标识
        for pattern, region in text_patterns.items():
            if re.search(pattern, name):
                return region
        
        return '其他'
    
    def is_stable_transit_node(self, proxy: Dict[str, Any]) -> bool:
        """判断是否为稳定的中转节点"""
        name = proxy.get('name', '').lower()
        proxy_type = proxy.get('type', '').lower()
        server = proxy.get('server', '')
        
        # 排除条件
        exclude_patterns = [
            'direct', '直连', '直通', 'info', '信息', '通知', '公告',
            'test', '测试', 'speed', '网速', 'temp', '临时', 'backup', '备用',
            'ipv6', 'v6', '剩余流量', '套餐到期', '官网', '节点异常', '刷新失败'
        ]
        
        # 检查是否包含排除关键词
        for pattern in exclude_patterns:
            if pattern in name:
                return False
        
        # 只保留主要协议
        if proxy_type not in ['trojan', 'ss', 'vmess', 'vless', 'hysteria2']:
            return False
        
        # 检查是否为IPv6地址
        if ':' in server and '[' not in server:
            return False
        
        # 必须有有效的服务器地址
        if not server or server in ['127.0.0.1', 'localhost']:
            return False
        
        return True
    
    def extract_stable_proxies(self, config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        提取稳定的中转节点
        
        Returns:
            Tuple[List, Dict]: (稳定节点列表, 统计信息)
        """
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
    
    def create_socks_config(self, proxies: List[Dict[str, Any]], region_groups: Dict[str, List[str]]) -> Dict[str, Any]:
        """创建SOCKS代理配置"""
        # 基础配置
        config = {
            'mixed-port': 7890,
            'allow-lan': False,
            'bind-address': '*',
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True,
                'ipv6': False,
                'default-nameserver': ['223.5.5.5', '119.29.29.29'],
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'nameserver': ['https://doh.pub/dns-query', 'https://dns.alidns.com/dns-query']
            },
            'proxies': proxies,
            'proxy-groups': [],
            'rules': [
                'DOMAIN-SUFFIX,local,DIRECT',
                'IP-CIDR,127.0.0.0/8,DIRECT',
                'IP-CIDR,172.16.0.0/12,DIRECT',
                'IP-CIDR,192.168.0.0/16,DIRECT',
                'IP-CIDR,10.0.0.0/8,DIRECT',
                'GEOIP,CN,DIRECT',
                'MATCH,🌟 主选择'
            ]
        }
        
        # 优先地区列表
        priority_regions = ['香港', '美国', '日本', '新加坡', '台湾']
        
        # 创建主选择组
        all_nodes = [proxy['name'] for proxy in proxies]
        config['proxy-groups'].append({
            'name': '🌟 主选择',
            'type': 'select',
            'proxies': all_nodes
        })
        
        # 为每个优先地区创建代理组和监听器
        listeners = []
        port = 7891
        
        for region in priority_regions:
            if region in region_groups and region_groups[region]:
                # 创建代理组
                config['proxy-groups'].append({
                    'name': f'{region}出口',
                    'type': 'select',
                    'proxies': region_groups[region]
                })
                
                # 创建SOCKS监听器
                listeners.append({
                    'name': f'{region}SOCKS',
                    'type': 'socks',
                    'port': port,
                    'proxy': f'{region}出口'
                })
                
                port += 1
        
        # 添加监听器配置
        if listeners:
            config['listeners'] = listeners
        
        return config
    
    def save_config(self, config: Dict[str, Any], filename: str = None) -> str:
        """
        保存配置文件
        
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            filename = f"clash-stable-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        
        file_path = os.path.join(self.downloads_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return file_path
    
    def convert_from_url(self, url: str, host_url: str = 'http://localhost:5000') -> Dict[str, Any]:
        """
        从订阅链接转换配置
        
        Args:
            url: 订阅链接
            host_url: 当前服务的主机地址，用于生成订阅链接
            
        Returns:
            Dict: 转换结果
        """
        result = {
            'success': False,
            'message': '',
            'stats': {},
            'regions': {},
            'download_url': '',
            'subscribe_url': '',
            'filename': ''
        }
        
        try:
            # 下载配置
            success, temp_file, error = self.download_config(url)
            if not success:
                result['message'] = error
                return result
            
            # 加载配置
            success, config, error = self.load_config(temp_file)
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
            
            # 生成SOCKS配置
            socks_config = self.create_socks_config(stable_proxies, region_groups)
            
            # 保存配置
            filename = f"clash-stable-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            file_path = self.save_config(socks_config, filename)
            
            # 清理临时文件
            try:
                os.remove(temp_file)
            except:
                pass
            
            result.update({
                'success': True,
                'message': '转换成功！',
                'stats': stats,
                'regions': region_groups,
                'download_url': f'/download/{filename}',
                'subscribe_url': f'{host_url}/sub/{filename}',
                'filename': filename
            })
            
        except Exception as e:
            result['message'] = f"转换过程出错: {str(e)}"
        
        return result
    
    def convert_from_file(self, file_path: str, host_url: str = 'http://localhost:5000') -> Dict[str, Any]:
        """
        从本地文件转换配置
        
        Args:
            file_path: 本地文件路径
            host_url: 当前服务的主机地址，用于生成订阅链接
            
        Returns:
            Dict: 转换结果
        """
        result = {
            'success': False,
            'message': '',
            'stats': {},
            'regions': {},
            'download_url': '',
            'subscribe_url': '',
            'filename': ''
        }
        
        try:
            # 加载配置
            success, config, error = self.load_config(file_path)
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
            
            # 生成SOCKS配置
            socks_config = self.create_socks_config(stable_proxies, region_groups)
            
            # 保存配置
            filename = f"clash-stable-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            file_path = self.save_config(socks_config, filename)
            
            result.update({
                'success': True,
                'message': '转换成功！',
                'stats': stats,
                'regions': region_groups,
                'download_url': f'/download/{filename}',
                'subscribe_url': f'{host_url}/sub/{filename}',
                'filename': filename
            })
            
        except Exception as e:
            result['message'] = f"转换过程出错: {str(e)}"
        
        return result 