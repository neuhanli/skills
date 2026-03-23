"""
安全组件

提供敏感文件过滤、文件锁机制和权限检查功能。
"""

import os
import platform
from pathlib import Path
from typing import List, Set, Optional

# 跨平台文件锁定支持
if platform.system() != 'Windows':
    import fcntl
else:
    # Windows平台使用简单的文件存在性检查作为锁机制
    fcntl = None


class Security:
    """
    安全组件
    
    提供敏感文件过滤、文件锁机制和权限检查功能。
    """
    
    def __init__(self, logger):
        self.logger = logger
        
        # 敏感文件模式
        self.sensitive_patterns = [
            # 配置文件
            '*.env', '.env*', 'config*.py', 'settings*.py',
            # 密钥文件
            '*.key', '*.pem', '*.crt', 'id_rsa', 'id_dsa',
            # 数据库文件
            '*.db', '*.sqlite', '*.mdb',
            # 日志文件
            '*.log', 'logs/',
            # 临时文件
            '*.tmp', 'temp/', 'tmp/',
            # 版本控制
            '.git/', '.svn/',
            # 系统文件
            '.DS_Store', 'Thumbs.db'
        ]
        
        # 文件锁字典
        self._file_locks: Dict[Path, int] = {}
    
    def is_sensitive_file(self, file_path: str) -> bool:
        """
        检查文件是否敏感
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否敏感
        """
        path = Path(file_path)
        
        # 检查文件名和路径是否匹配敏感模式
        for pattern in self.sensitive_patterns:
            if self._match_pattern(path, pattern):
                self.logger.debug(f"检测到敏感文件: {file_path} (匹配模式: {pattern})")
                return True
        
        # 检查文件内容是否包含敏感信息
        if self._contains_sensitive_content(path):
            self.logger.debug(f"检测到敏感内容: {file_path}")
            return True
        
        return False
    
    def _match_pattern(self, path: Path, pattern: str) -> bool:
        """匹配文件模式"""
        try:
            # 简单的模式匹配实现
            if pattern.endswith('/'):
                # 目录匹配
                return pattern.rstrip('/') in str(path)
            elif '*' in pattern:
                # 通配符匹配
                import fnmatch
                return fnmatch.fnmatch(path.name, pattern)
            else:
                # 精确匹配
                return path.name == pattern
        except Exception:
            return False
    
    def _contains_sensitive_content(self, path: Path) -> bool:
        """检查文件内容是否包含敏感信息"""
        if not path.exists() or not path.is_file():
            return False
        
        # 只检查小文件
        if path.stat().st_size > 1024 * 1024:  # 1MB
            return False
        
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(8192)  # 只读取前8KB
                
            # 敏感关键词
            sensitive_keywords = [
                'password', 'secret', 'key', 'token', 'api_key',
                'private_key', 'database_url', 'credential'
            ]
            
            content_lower = content.lower()
            for keyword in sensitive_keywords:
                if keyword in content_lower:
                    return True
                    
        except Exception:
            # 如果无法读取文件内容，保守起见认为可能敏感
            return True
        
        return False
    
    def filter_sensitive_files(self, file_paths: List[str]) -> List[str]:
        """
        过滤敏感文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[str]: 过滤后的文件路径列表
        """
        safe_files = []
        sensitive_files = []
        
        for file_path in file_paths:
            if self.is_sensitive_file(file_path):
                sensitive_files.append(file_path)
            else:
                safe_files.append(file_path)
        
        if sensitive_files:
            self.logger.info(f"过滤掉 {len(sensitive_files)} 个敏感文件")
        
        return safe_files
    
    def acquire_file_lock(self, file_path: str, timeout: float = 10.0) -> bool:
        """
        获取文件锁
        
        Args:
            file_path: 文件路径
            timeout: 超时时间(秒)
            
        Returns:
            bool: 是否成功获取锁
        """
        path = Path(file_path)
        lock_file = path.with_suffix(path.suffix + '.lock')
        
        try:
            # 创建锁文件
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            
            if fcntl is not None:
                # Linux/Mac: 使用fcntl文件锁
                fd = os.open(str(lock_file), os.O_CREAT | os.O_WRONLY)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._file_locks[path] = fd
            else:
                # Windows: 使用文件存在性检查作为锁机制
                import time
                max_attempts = int(timeout * 10)  # 每0.1秒尝试一次
                
                for attempt in range(max_attempts):
                    try:
                        # 尝试创建锁文件（原子操作）
                        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                        os.close(fd)
                        self._file_locks[path] = -1  # 标记为Windows锁
                        break
                    except FileExistsError:
                        if attempt == max_attempts - 1:
                            self.logger.warning(f"文件被锁定: {file_path}")
                            return False
                        time.sleep(0.1)
            
            self.logger.debug(f"获取文件锁: {file_path}")
            return True
            
        except (IOError, BlockingIOError):
            # 锁已被占用
            self.logger.warning(f"文件被锁定: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"获取文件锁失败 {file_path}: {str(e)}")
            return False
    
    def release_file_lock(self, file_path: str) -> bool:
        """
        释放文件锁
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功释放锁
        """
        path = Path(file_path)
        
        if path not in self._file_locks:
            self.logger.warning(f"未找到文件锁: {file_path}")
            return False
        
        try:
            fd = self._file_locks[path]
            
            if fcntl is not None and fd != -1:
                # Linux/Mac: 使用fcntl释放锁
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
            else:
                # Windows: 只需删除锁文件
                if fd == -1:
                    # Windows锁，不需要关闭文件描述符
                    pass
                else:
                    # 其他情况，关闭文件描述符
                    os.close(fd)
            
            # 删除锁文件
            lock_file = path.with_suffix(path.suffix + '.lock')
            if lock_file.exists():
                lock_file.unlink()
            
            # 从字典中移除
            del self._file_locks[path]
            
            self.logger.debug(f"释放文件锁: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"释放文件锁失败 {file_path}: {str(e)}")
            return False
    
    def check_permissions(self, file_path: str, required_permissions: str) -> bool:
        """
        检查文件权限
        
        Args:
            file_path: 文件路径
            required_permissions: 所需权限 (r, w, x 的组合)
            
        Returns:
            bool: 是否具有所需权限
        """
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"文件不存在: {file_path}")
            return False
        
        try:
            stat = path.stat()
            
            # 检查读权限
            if 'r' in required_permissions:
                if not os.access(path, os.R_OK):
                    self.logger.warning(f"无读权限: {file_path}")
                    return False
            
            # 检查写权限
            if 'w' in required_permissions:
                if not os.access(path, os.W_OK):
                    self.logger.warning(f"无写权限: {file_path}")
                    return False
            
            # 检查执行权限
            if 'x' in required_permissions:
                if not os.access(path, os.X_OK):
                    self.logger.warning(f"无执行权限: {file_path}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查权限失败 {file_path}: {str(e)}")
            return False
    
    def validate_file_integrity(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """
        验证文件完整性
        
        Args:
            file_path: 文件路径
            expected_hash: 期望的哈希值(可选)
            
        Returns:
            bool: 文件是否完整
        """
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"文件不存在: {file_path}")
            return False
        
        try:
            # 检查文件大小是否合理
            file_size = path.stat().st_size
            if file_size == 0:
                self.logger.warning(f"文件为空: {file_path}")
                return False
            
            # 如果提供了期望哈希，验证哈希值
            if expected_hash:
                actual_hash = self._calculate_file_hash(path)
                if actual_hash != expected_hash:
                    self.logger.warning(f"文件哈希不匹配: {file_path}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证文件完整性失败 {file_path}: {str(e)}")
            return False
    
    def _calculate_file_hash(self, path: Path) -> str:
        """计算文件哈希值"""
        import hashlib
        
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def add_sensitive_pattern(self, pattern: str):
        """
        添加敏感文件模式
        
        Args:
            pattern: 文件模式
        """
        if pattern not in self.sensitive_patterns:
            self.sensitive_patterns.append(pattern)
            self.logger.info(f"添加敏感文件模式: {pattern}")
    
    def remove_sensitive_pattern(self, pattern: str):
        """
        移除敏感文件模式
        
        Args:
            pattern: 文件模式
        """
        if pattern in self.sensitive_patterns:
            self.sensitive_patterns.remove(pattern)
            self.logger.info(f"移除敏感文件模式: {pattern}")
    
    def get_sensitive_patterns(self) -> List[str]:
        """获取敏感文件模式列表"""
        return self.sensitive_patterns.copy()
    
    def cleanup_locks(self):
        """清理所有文件锁"""
        locked_files = list(self._file_locks.keys())
        
        for file_path in locked_files:
            self.release_file_lock(str(file_path))
        
        self.logger.info("清理所有文件锁完成")