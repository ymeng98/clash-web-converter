#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务处理模块
"""

import asyncio
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    progress: float = 0.0
    created_at: datetime = None
    completed_at: datetime = None

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TaskResult] = {}
        self.cleanup_lock = threading.Lock()
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """提交异步任务"""
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        self.tasks[task_id] = task_result
        
        # 提交任务到线程池
        future = self.executor.submit(self._run_task, task_id, func, *args, **kwargs)
        future.add_done_callback(lambda f: self._cleanup_old_tasks())
        
        return task_id
    
    def _run_task(self, task_id: str, func: Callable, *args, **kwargs):
        """运行任务"""
        task_result = self.tasks[task_id]
        
        try:
            # 更新状态为运行中
            task_result.status = TaskStatus.RUNNING
            
            # 执行任务
            result = func(*args, **kwargs)
            
            # 更新结果
            task_result.status = TaskStatus.COMPLETED
            task_result.result = result
            task_result.progress = 100.0
            task_result.completed_at = datetime.now()
            
        except Exception as e:
            # 更新错误状态
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.completed_at = datetime.now()
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def update_progress(self, task_id: str, progress: float):
        """更新任务进度"""
        if task_id in self.tasks:
            self.tasks[task_id].progress = progress
    
    def _cleanup_old_tasks(self):
        """清理旧任务（保留最近100个）"""
        with self.cleanup_lock:
            if len(self.tasks) > 100:
                # 按创建时间排序，删除最老的任务
                sorted_tasks = sorted(
                    self.tasks.items(),
                    key=lambda x: x[1].created_at
                )
                
                # 保留最新的50个任务
                tasks_to_keep = dict(sorted_tasks[-50:])
                self.tasks.clear()
                self.tasks.update(tasks_to_keep)
    
    def shutdown(self):
        """关闭任务管理器"""
        self.executor.shutdown(wait=True)

# 全局任务管理器
task_manager = AsyncTaskManager()

def async_task(func):
    """异步任务装饰器"""
    def wrapper(*args, **kwargs):
        return task_manager.submit_task(func, *args, **kwargs)
    return wrapper

class ProgressCallback:
    """进度回调类"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
    
    def update(self, progress: float):
        """更新进度"""
        task_manager.update_progress(self.task_id, progress) 