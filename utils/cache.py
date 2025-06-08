#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存工具模块
"""

import hashlib
import pickle
import os
import time
from typing import Any, Optional
from functools import wraps

class SimpleCache:
    """简单的文件缓存实现"""
    
    def __init__(self, cache_dir: str = None, default_timeout: int = 3600):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '..', 'cache')
        self.default_timeout = default_timeout
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if cache_data['expires_at'] < time.time():
                os.remove(cache_path)
                return None
            
            return cache_data['value']
        except (IOError, pickle.PickleError, KeyError):
            # 缓存文件损坏，删除
            try:
                os.remove(cache_path)
            except:
                pass
            return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存"""
        timeout = timeout or self.default_timeout
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'value': value,
            'expires_at': time.time() + timeout
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            return True
        except (IOError, pickle.PickleError):
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        try:
            os.remove(cache_path)
            return True
        except FileNotFoundError:
            return True
        except OSError:
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except OSError:
            return False

# 全局缓存实例
cache = SimpleCache()

def cached(timeout: int = 3600, key_func=None):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

def cache_subscription_result(url: str) -> str:
    """为订阅链接生成缓存键"""
    return f"subscription:{hashlib.md5(url.encode()).hexdigest()}" 