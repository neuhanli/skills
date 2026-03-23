"""
Snapshot Repository

Data access layer for Version-Master skill snapshot storage and management.
Handles file system operations for version snapshots with optimization.
"""

import shutil
import hashlib
import json
from pathlib import Path
from typing import List, Optional
from .models import VersionMasterError


class SnapshotRepository:
    """
    Snapshot Repository
    
    Data access layer for Version-Master skill snapshot storage and management.
    Handles file system operations for version snapshots with optimization.
    """
    
    def __init__(self, storage_path: str, logger):
        self.storage_path = Path(storage_path) / "snapshots"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger
    
    def create(self, name: str, workspace_path: Path) -> str:
        """
        创建快照
        
        Args:
            name: 版本名称
            workspace_path: 工作区路径
            
        Returns:
            str: 快照路径 ID
        """
        snapshot_path = self.storage_path / name
        snapshot_path.mkdir(exist_ok=True)
        
        try:
            # 复制工作区文件到快照目录
            self._copy_workspace(workspace_path, snapshot_path)
            
            # 计算哈希值用于完整性验证
            metadata = self._calculate_metadata(snapshot_path)
            
            # 保存元数据文件
            metadata_file = snapshot_path / ".snapshot_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"创建快照: {name}")
            return str(snapshot_path.relative_to(self.storage_path))
            
        except Exception as e:
            # 清理失败的部分文件
            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)
            raise VersionMasterError(f"创建快照失败: {str(e)}")
    
    def _copy_workspace(self, workspace_path: Path, snapshot_path: Path):
        """复制工作区文件到快照目录"""
        # 在实际实现中，这里会递归复制文件，但跳过一些特殊目录
        ignore_patterns = shutil.ignore_patterns(
            '.git', '.trae', '__pycache__', '*.pyc', '*.log'
        )
        
        if workspace_path.is_dir():
            shutil.copytree(
                workspace_path,
                snapshot_path,
                ignore=ignore_patterns,
                dirs_exist_ok=True
            )
        else:
            raise ValueError(f"工作区路径不存在: {workspace_path}")
    
    def _calculate_metadata(self, snapshot_path: Path) -> dict:
        """计算快照元数据"""
        total_size = 0
        file_count = 0
        file_hashes = {}
        
        for file_path in snapshot_path.rglob('*'):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size
                
                # 计算文件哈希
                file_hash = self._calculate_file_hash(file_path)
                relative_path = file_path.relative_to(snapshot_path)
                file_hashes[str(relative_path)] = file_hash
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "file_hashes": file_hashes,
            "created_at": Path(snapshot_path).stat().st_ctime
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def delete(self, snapshot_id: str):
        """
        删除快照
        
        Args:
            snapshot_id: 快照ID
        """
        snapshot_path = self.storage_path / snapshot_id
        
        if not snapshot_path.exists():
            raise VersionMasterError(f"快照不存在: {snapshot_id}")
        
        try:
            shutil.rmtree(snapshot_path)
            self.logger.info(f"删除快照: {snapshot_id}")
        except Exception as e:
            raise VersionMasterError(f"删除快照失败: {str(e)}")
    
    def exists(self, snapshot_id: str) -> bool:
        """
        检查快照是否存在
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            bool: 是否存在
        """
        snapshot_path = self.storage_path / snapshot_id
        return snapshot_path.exists() and snapshot_path.is_dir()
    
    def get_size(self, snapshot_id: str) -> int:
        """
        获取快照大小
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            int: 快照大小(字节)
        """
        snapshot_path = self.storage_path / snapshot_id
        metadata_file = snapshot_path / ".snapshot_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata.get("total_size", 0)
        
        # 如果元数据文件不存在，计算实际大小
        total_size = 0
        for file_path in snapshot_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def verify_integrity(self, snapshot_id: str) -> bool:
        """
        验证快照完整性
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            bool: 是否完整
        """
        snapshot_path = self.storage_path / snapshot_id
        metadata_file = snapshot_path / ".snapshot_metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 检查文件数量和大小
            current_file_count = 0
            current_total_size = 0
            
            for file_path in snapshot_path.rglob('*'):
                if file_path.is_file() and file_path.name != ".snapshot_metadata.json":
                    current_file_count += 1
                    current_total_size += file_path.stat().st_size
            
            expected_file_count = metadata.get("file_count", 0)
            expected_total_size = metadata.get("total_size", 0)
            
            return (
                current_file_count == expected_file_count and
                current_total_size == expected_total_size
            )
            
        except Exception:
            return False
    
    def list_snapshots(self) -> List[str]:
        """
        列出所有快照
        
        Returns:
            List[str]: 快照ID列表
        """
        snapshots = []
        for item in self.storage_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                snapshots.append(item.name)
        
        return sorted(snapshots)
    
    def get_snapshot_path(self, snapshot_id: str) -> Path:
        """
        获取快照路径
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            Path: 快照完整路径
        """
        snapshot_path = self.storage_path / snapshot_id
        if not snapshot_path.exists():
            raise VersionMasterError(f"快照不存在: {snapshot_id}")
        return snapshot_path
    
    def cleanup_orphaned_snapshots(self, valid_snapshot_ids: List[str]) -> List[str]:
        """
        清理孤立的快照
        
        Args:
            valid_snapshot_ids: 有效的快照ID列表
            
        Returns:
            List[str]: 被删除的快照ID列表
        """
        all_snapshots = set(self.list_snapshots())
        valid_snapshots = set(valid_snapshot_ids)
        orphaned_snapshots = all_snapshots - valid_snapshots
        
        deleted = []
        for snapshot_id in orphaned_snapshots:
            try:
                self.delete(snapshot_id)
                deleted.append(snapshot_id)
            except Exception as e:
                self.logger.warning(f"清理孤立快照失败 {snapshot_id}: {str(e)}")
        
        return deleted