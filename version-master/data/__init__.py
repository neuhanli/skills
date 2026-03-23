"""
数据访问层模块

管理版本快照的存储和检索，包括快照仓库和元数据仓库。
"""

from .snapshot_repository import SnapshotRepository
from .metadata_repository import VersionMetadataRepository

__all__ = ['SnapshotRepository', 'VersionMetadataRepository']