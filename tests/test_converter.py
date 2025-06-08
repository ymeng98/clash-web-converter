#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换器测试模块
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_converter import BaseClashConverter
from converter import ClashWebConverter

class TestBaseConverter(unittest.TestCase):
    """基础转换器测试"""
    
    def setUp(self):
        """测试初始化"""
        # 创建一个测试用的转换器实现
        class TestConverter(BaseClashConverter):
            def create_config(self, proxies, region_groups):
                return {'proxies': proxies, 'proxy-groups': []}
            
            def get_filename(self):
                return 'test-config.yaml'
        
        self.converter = TestConverter()
    
    def test_extract_region_from_name(self):
        """测试地区提取功能"""
        test_cases = [
            ('🇭🇰 香港节点', '香港'),
            ('🇺🇸 美国服务器', '美国'),
            ('🇯🇵 日本-东京', '日本'),
            ('Singapore Server', '新加坡'),
            ('HK Premium', '香港'),
            ('US West', '美国'),
            ('普通节点', '其他'),
        ]
        
        for name, expected_region in test_cases:
            with self.subTest(name=name):
                result = self.converter.extract_region_from_name(name)
                self.assertEqual(result, expected_region)
    
    def test_is_stable_transit_node(self):
        """测试稳定节点判断"""
        # 稳定节点
        stable_proxy = {
            'name': '🇭🇰 香港中转',
            'type': 'trojan',
            'server': '1.2.3.4',
            'port': 443
        }
        self.assertTrue(self.converter.is_stable_transit_node(stable_proxy))
        
        # 不稳定节点 - 包含排除关键词
        unstable_proxy1 = {
            'name': '剩余流量',
            'type': 'trojan',
            'server': '1.2.3.4',
            'port': 443
        }
        self.assertFalse(self.converter.is_stable_transit_node(unstable_proxy1))
        
        # 不稳定节点 - 不支持的协议
        unstable_proxy2 = {
            'name': '香港节点',
            'type': 'http',
            'server': '1.2.3.4',
            'port': 443
        }
        self.assertFalse(self.converter.is_stable_transit_node(unstable_proxy2))
        
        # 不稳定节点 - IPv6
        unstable_proxy3 = {
            'name': '香港节点',
            'type': 'trojan',
            'server': '2001:db8::1',
            'port': 443
        }
        self.assertFalse(self.converter.is_stable_transit_node(unstable_proxy3))
    
    def test_load_config_valid(self):
        """测试加载有效配置"""
        # 创建临时配置文件
        config_data = {
            'proxies': [
                {
                    'name': 'test-proxy',
                    'type': 'trojan',
                    'server': '1.2.3.4',
                    'port': 443
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            success, config, error = self.converter.load_config(temp_path)
            self.assertTrue(success)
            self.assertEqual(config['proxies'][0]['name'], 'test-proxy')
            self.assertEqual(error, '')
        finally:
            os.unlink(temp_path)
    
    def test_load_config_invalid(self):
        """测试加载无效配置"""
        # 测试不存在的文件
        success, config, error = self.converter.load_config('/nonexistent/file.yaml')
        self.assertFalse(success)
        self.assertIn('文件不存在', error)
        
        # 测试无效YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            temp_path = f.name
        
        try:
            success, config, error = self.converter.load_config(temp_path)
            self.assertFalse(success)
            self.assertIn('YAML解析错误', error)
        finally:
            os.unlink(temp_path)
    
    def test_group_proxies_by_region(self):
        """测试按地区分组"""
        proxies = [
            {'name': '🇭🇰 香港1'},
            {'name': '🇭🇰 香港2'},
            {'name': '🇺🇸 美国1'},
            {'name': '其他节点'},
        ]
        
        groups = self.converter.group_proxies_by_region(proxies)
        
        self.assertEqual(len(groups['香港']), 2)
        self.assertEqual(len(groups['美国']), 1)
        self.assertEqual(len(groups['其他']), 1)
        self.assertIn('🇭🇰 香港1', groups['香港'])
        self.assertIn('🇺🇸 美国1', groups['美国'])

class TestClashWebConverter(unittest.TestCase):
    """Web转换器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.converter = ClashWebConverter()
    
    @patch('requests.get')
    def test_download_config_success(self, mock_get):
        """测试成功下载配置"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'test config content'
        mock_get.return_value = mock_response
        
        success, temp_file, error = self.converter.download_config('http://test.com/config')
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(temp_file))
        self.assertEqual(error, '')
        
        # 清理临时文件
        os.unlink(temp_file)
    
    @patch('requests.get')
    def test_download_config_404(self, mock_get):
        """测试404错误"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        success, temp_file, error = self.converter.download_config('http://test.com/config')
        
        self.assertFalse(success)
        self.assertIn('404错误', error)
    
    def test_create_socks_config(self):
        """测试SOCKS配置生成"""
        proxies = [
            {
                'name': '🇭🇰 香港节点',
                'type': 'trojan',
                'server': '1.2.3.4',
                'port': 443
            }
        ]
        
        region_groups = {
            '香港': ['🇭🇰 香港节点']
        }
        
        config = self.converter.create_socks_config(proxies, region_groups)
        
        # 检查基础配置
        self.assertEqual(config['mixed-port'], 7890)
        self.assertTrue(config['dns']['enable'])
        self.assertIn('proxies', config)
        self.assertIn('proxy-groups', config)
        self.assertIn('rules', config)
        
        # 检查代理组
        group_names = [group['name'] for group in config['proxy-groups']]
        self.assertIn('🌟 主选择', group_names)
        self.assertIn('香港出口', group_names)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 