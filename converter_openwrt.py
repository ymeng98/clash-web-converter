#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash稳定中转SOCKS代理转换器 - OpenWrt软路由专用版
功能：为OpenWrt软路由环境优化配置
"""

import yaml
import re
import requests
import os
import tempfile
import uuid
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ClashOpenWrtConverter:
    def __init__(self):
        self.downloads_dir = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def download_config(self, url: str) -> Tuple[bool, str, str]:
        """从URL下载配置文件"""
        try:
            user_agents = [
                "ClashforWindows/1.0",
                "Clash/1.0", 
                "ClashX/1.0",
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
        """加载YAML配置文件"""
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
            r'(?i)(korea|kr|韩国|韩)': '韩国'
        }
        
        for emoji, region in region_patterns.items():
            if emoji in name:
                return region
        
        for pattern, region in text_patterns.items():
            if re.search(pattern, name):
                return region
        
        return '其他'
    
    def is_stable_transit_node(self, proxy: Dict[str, Any]) -> bool:
        """判断是否为稳定的中转节点"""
        name = proxy.get('name', '').lower()
        proxy_type = proxy.get('type', '').lower()
        server = proxy.get('server', '')
        
        exclude_patterns = [
            'direct', '直连', '直通', 'info', '信息', '通知', '公告',
            'test', '测试', 'speed', '网速', 'temp', '临时', 'backup', '备用',
            'ipv6', 'v6', '剩余流量', '套餐到期', '官网', '节点异常', '刷新失败'
        ]
        
        for pattern in exclude_patterns:
            if pattern in name:
                return False
        
        if proxy_type not in ['trojan', 'ss', 'vmess', 'vless', 'hysteria2']:
            return False
        
        if ':' in server and '[' not in server:
            return False
        
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
    
    def create_openwrt_config(self, proxies: List[Dict[str, Any]], region_groups: Dict[str, List[str]]) -> Dict[str, Any]:
        """创建OpenWrt专用配置"""
        # 基础配置（软路由优化）
        config = {
            'mixed-port': 7890,
            'allow-lan': True,
            'bind-address': '0.0.0.0',
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '0.0.0.0:9090',
            'external-ui': 'dashboard',
            'ipv6': False,
            
            # DNS配置（软路由优化）
            'dns': {
                'enable': True,
                'ipv6': False,
                'listen': '0.0.0.0:1053',
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'fake-ip-filter': [
                    '*.lan',
                    '*.local', 
                    'localhost.ptlogin2.qq.com'
                ],
                'default-nameserver': [
                    '114.114.114.114',
                    '223.5.5.5'
                ],
                'nameserver': [
                    'https://doh.pub/dns-query',
                    'https://dns.alidns.com/dns-query'
                ],
                'fallback': [
                    'https://cloudflare-dns.com/dns-query',
                    'https://dns.google/dns-query'
                ],
                'fallback-filter': {
                    'geoip': True,
                    'geoip-code': 'CN',
                    'ipcidr': ['240.0.0.0/4']
                }
            },
            
            # TUN模式配置（软路由推荐）
            'tun': {
                'enable': True,
                'stack': 'system',
                'dns-hijack': ['198.18.0.2:53'],
                'auto-route': True,
                'auto-detect-interface': True
            },
            
            'proxies': proxies,
            'proxy-groups': [],
            'rules': []
        }
        
        # 生成代理组（软路由优化）
        all_proxies = [proxy['name'] for proxy in proxies]
        
        # 主选择组
        config['proxy-groups'].append({
            'name': '🚀 节点选择',
            'type': 'select',
            'proxies': [
                '♻️ 自动选择',
                '🔯 故障转移', 
                '🔮 负载均衡',
                'DIRECT'
            ] + [f"🇨🇳 {region}节点" for region in ['香港', '美国', '日本', '新加坡', '台湾'] if region in region_groups]
        })
        
        # 自动选择组
        config['proxy-groups'].append({
            'name': '♻️ 自动选择',
            'type': 'url-test',
            'proxies': all_proxies[:10],  # 限制数量避免负载过重
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'tolerance': 50
        })
        
        # 故障转移组
        config['proxy-groups'].append({
            'name': '🔯 故障转移',
            'type': 'fallback',
            'proxies': all_proxies[:8],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        })
        
        # 负载均衡组
        config['proxy-groups'].append({
            'name': '🔮 负载均衡',
            'type': 'load-balance',
            'strategy': 'consistent-hashing',
            'proxies': all_proxies[:6],
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        })
        
        # 地区代理组
        priority_regions = ['香港', '美国', '日本', '新加坡', '台湾']
        region_icons = {
            '香港': '🇭🇰', '美国': '🇺🇸', '日本': '🇯🇵',
            '新加坡': '🇸🇬', '台湾': '🇨🇳'
        }
        
        for region in priority_regions:
            if region in region_groups and region_groups[region]:
                config['proxy-groups'].append({
                    'name': f'{region_icons.get(region, "🌍")} {region}节点',
                    'type': 'select',
                    'proxies': region_groups[region]
                })
        
        # 功能代理组
        config['proxy-groups'].extend([
            {
                'name': '🌍 国外媒体',
                'type': 'select',
                'proxies': ['🚀 节点选择', '♻️ 自动选择'] + [f"{region_icons.get(region, '🌍')} {region}节点" for region in ['美国', '香港', '日本'] if region in region_groups]
            },
            {
                'name': '📲 电报消息',
                'type': 'select',
                'proxies': ['🚀 节点选择'] + [f"{region_icons.get(region, '🌍')} {region}节点" for region in ['新加坡', '香港'] if region in region_groups]
            },
            {
                'name': '🍃 应用净化',
                'type': 'select',
                'proxies': ['REJECT', 'DIRECT']
            },
            {
                'name': '🐟 漏网之鱼',
                'type': 'select',
                'proxies': ['🚀 节点选择', 'DIRECT']
            }
        ])
        
        # 分流规则（软路由专用）
        config['rules'] = [
            # 本地网络直连
            'DOMAIN-SUFFIX,local,DIRECT',
            'IP-CIDR,127.0.0.0/8,DIRECT',
            'IP-CIDR,172.16.0.0/12,DIRECT',
            'IP-CIDR,192.168.0.0/16,DIRECT',
            'IP-CIDR,10.0.0.0/8,DIRECT',
            'IP-CIDR,17.0.0.0/8,DIRECT',
            'IP-CIDR,100.64.0.0/10,DIRECT',
            'IP-CIDR,224.0.0.0/4,DIRECT',
            'IP-CIDR6,fe80::/10,DIRECT',
            
            # OpenWrt管理页面
            'DOMAIN-SUFFIX,openwrt.lan,DIRECT',
            'DOMAIN-SUFFIX,router.lan,DIRECT',
            'IP-CIDR,192.168.1.1/32,DIRECT',
            
            # 广告拦截
            'DOMAIN-SUFFIX,googlesyndication.com,🍃 应用净化',
            'DOMAIN-SUFFIX,googleadservices.com,🍃 应用净化',
            'DOMAIN-KEYWORD,adnxs,🍃 应用净化',
            'DOMAIN-KEYWORD,adsystem,🍃 应用净化',
            
            # Telegram
            'DOMAIN-SUFFIX,t.me,📲 电报消息',
            'DOMAIN-SUFFIX,tdesktop.com,📲 电报消息',
            'DOMAIN-SUFFIX,telegra.ph,📲 电报消息',
            'DOMAIN-SUFFIX,telegram.org,📲 电报消息',
            'IP-CIDR,91.108.4.0/22,📲 电报消息',
            'IP-CIDR,91.108.8.0/21,📲 电报消息',
            'IP-CIDR,91.108.16.0/22,📲 电报消息',
            'IP-CIDR,149.154.160.0/20,📲 电报消息',
            
            # 国外媒体
            'DOMAIN-SUFFIX,youtube.com,🌍 国外媒体',
            'DOMAIN-SUFFIX,googlevideo.com,🌍 国外媒体',
            'DOMAIN-SUFFIX,netflix.com,🌍 国外媒体',
            'DOMAIN-SUFFIX,nflximg.net,🌍 国外媒体',
            'DOMAIN-SUFFIX,twitter.com,🌍 国外媒体',
            'DOMAIN-SUFFIX,facebook.com,🌍 国外媒体',
            'DOMAIN-SUFFIX,instagram.com,🌍 国外媒体',
            
            # 国内直连
            'DOMAIN-SUFFIX,cn,DIRECT',
            'DOMAIN-KEYWORD,-cn,DIRECT',
            'GEOIP,CN,DIRECT',
            
            # 漏网之鱼
            'MATCH,🐟 漏网之鱼'
        ]
        
        return config
    
    def save_config(self, config: Dict[str, Any], filename: str = None) -> str:
        """保存配置文件"""
        if filename is None:
            filename = f"clash-openwrt-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        
        file_path = os.path.join(self.downloads_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return file_path
    
    def convert_for_openwrt(self, source: str, is_url: bool = True) -> Dict[str, Any]:
        """为OpenWrt转换配置"""
        result = {
            'success': False,
            'message': '',
            'stats': {},
            'regions': {},
            'download_url': '',
            'filename': '',
            'openwrt_tips': []
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
            
            # 生成OpenWrt配置
            openwrt_config = self.create_openwrt_config(stable_proxies, region_groups)
            
            # 保存配置
            filename = f"clash-openwrt-{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            file_path = self.save_config(openwrt_config, filename)
            
            # 清理临时文件
            if is_url:
                try:
                    os.remove(config_file)
                except:
                    pass
            
            # OpenWrt使用提示
            openwrt_tips = [
                "✅ 已启用TUN模式，适合软路由透明代理",
                "✅ DNS设置为0.0.0.0:1053，请在OpenWrt中配置DNS重定向",
                "✅ 外部控制器绑定0.0.0.0:9090，可从局域网访问管理界面", 
                "✅ 已启用fake-ip模式，提升解析性能",
                "⚠️ 请确保OpenWrt已安装Clash内核和相关依赖",
                "⚠️ 建议内存2GB以上的设备使用此配置"
            ]
            
            result.update({
                'success': True,
                'message': 'OpenWrt配置转换成功！',
                'stats': stats,
                'regions': region_groups,
                'download_url': f'/download/{filename}',
                'filename': filename,
                'openwrt_tips': openwrt_tips
            })
            
        except Exception as e:
            result['message'] = f"转换过程出错: {str(e)}"
        
        return result

def main():
    """测试函数"""
    converter = ClashOpenWrtConverter()
    
    # 示例：转换demo配置为OpenWrt格式
    demo_file = "demo-config.yaml"
    if os.path.exists(demo_file):
        result = converter.convert_for_openwrt(demo_file, is_url=False)
        if result['success']:
            print("✅ OpenWrt配置转换成功！")
            print(f"📁 文件保存为: {result['filename']}")
            print(f"📊 节点统计: {result['stats']}")
            print("\n🔧 OpenWrt使用提示:")
            for tip in result['openwrt_tips']:
                print(f"  {tip}")
        else:
            print(f"❌ 转换失败: {result['message']}")
    else:
        print("❌ 找不到demo-config.yaml文件")

if __name__ == "__main__":
    main() 