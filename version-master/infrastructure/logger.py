"""
日志系统

提供操作日志和错误日志功能，支持不同日志级别和输出格式。
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """
    日志系统
    
    提供操作日志和错误日志功能，支持不同日志级别和输出格式。
    """
    
    def __init__(self, name: str = "versionmaster", log_level: str = "INFO", log_file: Optional[str] = None):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_file = log_file
        
        # 配置日志记录器
        self._setup_logger()
    
    def _setup_logger(self):
        """配置日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了日志文件）
        if self.log_file:
            # 确保日志目录存在
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message)
    
    def log_operation(self, operation: str, details: dict):
        """
        记录操作日志
        
        Args:
            operation: 操作名称
            details: 操作详情
        """
        log_message = f"操作: {operation}"
        if details:
            log_message += f" | 详情: {details}"
        self.info(log_message)
    
    def log_error(self, operation: str, error: Exception, context: dict = None):
        """
        记录错误日志
        
        Args:
            operation: 操作名称
            error: 错误对象
            context: 错误上下文
        """
        error_message = f"操作失败: {operation} | 错误: {str(error)}"
        if context:
            error_message += f" | 上下文: {context}"
        self.error(error_message)
    
    def log_performance(self, operation: str, duration: float, metrics: dict = None):
        """
        记录性能日志
        
        Args:
            operation: 操作名称
            duration: 耗时(秒)
            metrics: 性能指标
        """
        perf_message = f"性能: {operation} | 耗时: {duration:.3f}s"
        if metrics:
            perf_message += f" | 指标: {metrics}"
        self.debug(perf_message)
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper())
        self.log_level = new_level
        self.logger.setLevel(new_level)
        
        # 更新所有处理器的级别
        for handler in self.logger.handlers:
            handler.setLevel(new_level)
    
    def add_file_handler(self, log_file: str):
        """
        添加文件处理器
        
        Args:
            log_file: 日志文件路径
        """
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def get_log_stats(self) -> dict:
        """
        获取日志统计信息
        
        Returns:
            dict: 日志统计信息
        """
        # 在实际实现中，这里可以分析日志文件
        # 暂时返回模拟数据
        return {
            'total_entries': 100,
            'error_count': 5,
            'warning_count': 10,
            'last_log_time': datetime.now().isoformat(),
            'log_file_size': 1024 * 1024  # 1MB
        }
    
    def rotate_logs(self, max_size_mb: int = 10, backup_count: int = 5):
        """
        轮转日志文件
        
        Args:
            max_size_mb: 最大文件大小(MB)
            backup_count: 备份文件数量
        """
        if not self.log_file:
            return
        
        log_path = Path(self.log_file)
        if not log_path.exists():
            return
        
        # 检查文件大小
        file_size_mb = log_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            self.info(f"日志文件达到 {file_size_mb:.1f}MB，开始轮转")
            
            # 在实际实现中，这里会实现日志轮转逻辑
            # 暂时只记录信息
            self.info("日志轮转功能待实现")
    
    def cleanup(self):
        """清理日志资源"""
        # 关闭所有文件处理器
        for handler in self.logger.handlers:
            if hasattr(handler, 'close'):
                handler.close()
        
        # 清除所有处理器
        self.logger.handlers.clear()
    
    @classmethod
    def create_default_logger(cls, storage_path: str) -> 'Logger':
        """
        创建默认日志记录器
        
        Args:
            storage_path: 存储路径
            
        Returns:
            Logger: 日志记录器实例
        """
        log_file = str(Path(storage_path) / "logs" / "versionmaster.log")
        return cls(log_file=log_file)