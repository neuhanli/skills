"""
文件系统组件

提供快照目录管理和文件拷贝/删除功能。
"""

import shutil
import os
from pathlib import Path
from typing import List, Optional


class FileSystem:
    """
    文件系统组件
    
    提供快照目录管理和文件拷贝/删除功能。
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_directory(self, path: str) -> Path:
        """
        创建目录
        
        Args:
            path: 目录路径
            
        Returns:
            Path: 创建的目录路径
        """
        full_path = self.base_path / path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def copy_directory(self, source: Path, destination: Path, ignore_patterns: Optional[List[str]] = None):
        """
        复制目录
        
        Args:
            source: 源目录
            destination: 目标目录
            ignore_patterns: 忽略模式列表
        """
        if not source.exists():
            raise ValueError(f"源目录不存在: {source}")
        
        # 创建自定义忽略函数
        def ignore_func(path, names):
            ignored = set()
            if ignore_patterns:
                for pattern in ignore_patterns:
                    for name in names:
                        if pattern in name or name.startswith('.'):
                            ignored.add(name)
            return ignored
        
        shutil.copytree(source, destination, ignore=ignore_func, dirs_exist_ok=True)
    
    def copy_file(self, source: Path, destination: Path):
        """
        复制文件
        
        Args:
            source: 源文件
            destination: 目标文件
        """
        if not source.exists():
            raise ValueError(f"源文件不存在: {source}")
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    
    def delete_directory(self, path: str):
        """
        删除目录
        
        Args:
            path: 目录路径
        """
        full_path = self.base_path / path
        if full_path.exists() and full_path.is_dir():
            shutil.rmtree(full_path)
    
    def delete_file(self, path: str):
        """
        删除文件
        
        Args:
            path: 文件路径
        """
        full_path = self.base_path / path
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
    
    def file_exists(self, path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 是否存在
        """
        full_path = self.base_path / path
        return full_path.exists() and full_path.is_file()
    
    def directory_exists(self, path: str) -> bool:
        """
        检查目录是否存在
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 是否存在
        """
        full_path = self.base_path / path
        return full_path.exists() and full_path.is_dir()
    
    def list_files(self, path: str, pattern: str = "*") -> List[Path]:
        """
        列出文件
        
        Args:
            path: 目录路径
            pattern: 文件模式
            
        Returns:
            List[Path]: 文件路径列表
        """
        full_path = self.base_path / path
        if not full_path.exists():
            return []
        
        return list(full_path.rglob(pattern))
    
    def get_file_size(self, path: str) -> int:
        """
        获取文件大小
        
        Args:
            path: 文件路径
            
        Returns:
            int: 文件大小(字节)
        """
        full_path = self.base_path / path
        if not full_path.exists():
            raise ValueError(f"文件不存在: {path}")
        
        return full_path.stat().st_size
    
    def get_directory_size(self, path: str) -> int:
        """
        获取目录大小
        
        Args:
            path: 目录路径
            
        Returns:
            int: 目录大小(字节)
        """
        full_path = self.base_path / path
        if not full_path.exists():
            raise ValueError(f"目录不存在: {path}")
        
        total_size = 0
        for file_path in full_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def move_file(self, source: str, destination: str):
        """
        移动文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
        """
        source_path = self.base_path / source
        destination_path = self.base_path / destination
        
        if not source_path.exists():
            raise ValueError(f"源文件不存在: {source}")
        
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(destination_path))
    
    def create_symlink(self, target: str, link_name: str):
        """
        创建符号链接
        
        Args:
            target: 目标路径
            link_name: 链接名称
        """
        target_path = self.base_path / target
        link_path = self.base_path / link_name
        
        if not target_path.exists():
            raise ValueError(f"目标路径不存在: {target}")
        
        link_path.parent.mkdir(parents=True, exist_ok=True)
        
        if link_path.exists():
            link_path.unlink()
        
        os.symlink(str(target_path), str(link_path))
    
    def get_available_space(self) -> int:
        """
        获取可用空间
        
        Returns:
            int: 可用空间(字节)
        """
        stat = os.statvfs(str(self.base_path))
        return stat.f_bavail * stat.f_frsize
    
    def get_total_space(self) -> int:
        """
        获取总空间
        
        Returns:
            int: 总空间(字节)
        """
        stat = os.statvfs(str(self.base_path))
        return stat.f_blocks * stat.f_frsize
    
    def get_used_space(self) -> int:
        """
        获取已用空间
        
        Returns:
            int: 已用空间(字节)
        """
        total = self.get_total_space()
        available = self.get_available_space()
        return total - available