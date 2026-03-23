"""
版本元数据仓库

管理版本元数据的 CRUD 操作、索引查询和搜索过滤。
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import VersionMetadata, Change, ChangeType


class VersionMetadataRepository:
    """
    版本元数据仓库
    
    管理版本元数据的 CRUD 操作、索引查询和搜索过滤。
    """
    
    def __init__(self, storage_path: str, logger):
        self.storage_path = Path(storage_path) / "metadata"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / "versions.db"
        self.logger = logger
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 创建版本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS versions (
                    name TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    snapshot_path TEXT NOT NULL,
                    user_comment TEXT,
                    size_bytes INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建变更表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT,
                    FOREIGN KEY (version_name) REFERENCES versions (name) ON DELETE CASCADE
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_timestamp ON versions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_changes_version ON changes(version_name)')
            
            conn.commit()
        finally:
            conn.close()
    
    def save(self, metadata: VersionMetadata):
        """
        保存版本元数据
        
        Args:
            metadata: 版本元数据
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 插入版本信息
            cursor.execute('''
                INSERT OR REPLACE INTO versions 
                (name, timestamp, trigger, summary, snapshot_path, user_comment, size_bytes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.name,
                metadata.timestamp,
                metadata.trigger,
                metadata.summary,
                metadata.snapshot_path,
                metadata.user_comment,
                metadata.size_bytes
            ))
            
            # 删除旧的变更记录
            cursor.execute('DELETE FROM changes WHERE version_name = ?', (metadata.name,))
            
            # 插入变更记录
            for change in metadata.changes:
                cursor.execute('''
                    INSERT INTO changes 
                    (version_name, file_path, change_type, size_bytes, timestamp, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metadata.name,
                    change.file_path,
                    change.change_type.value,
                    change.size_bytes,
                    change.timestamp,
                    change.content_hash
                ))
            
            conn.commit()
            self.logger.info(f"保存元数据: {metadata.name}")
            
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"保存元数据失败: {str(e)}")
        finally:
            conn.close()
    
    def find(self, name: str) -> Optional[VersionMetadata]:
        """
        查找指定版本的元数据
        
        Args:
            name: 版本名称
            
        Returns:
            Optional[VersionMetadata]: 版本元数据，如果不存在返回 None
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 查询版本信息
            cursor.execute('''
                SELECT name, timestamp, trigger, summary, snapshot_path, user_comment, size_bytes
                FROM versions WHERE name = ?
            ''', (name,))
            
            version_row = cursor.fetchone()
            if not version_row:
                return None
            
            # 查询变更记录
            cursor.execute('''
                SELECT file_path, change_type, size_bytes, timestamp, content_hash
                FROM changes WHERE version_name = ?
            ''', (name,))
            
            changes = []
            for row in cursor.fetchall():
                change = Change(
                    file_path=row[0],
                    change_type=ChangeType(row[1]),
                    size_bytes=row[2],
                    timestamp=row[3],
                    content_hash=row[4]
                )
                changes.append(change)
            
            # 构建 VersionMetadata 对象
            metadata = VersionMetadata(
                name=version_row[0],
                timestamp=version_row[1],
                trigger=version_row[2],
                summary=version_row[3],
                snapshot_path=version_row[4],
                user_comment=version_row[5],
                changes=changes,
                size_bytes=version_row[6]
            )
            
            return metadata
            
        finally:
            conn.close()
    
    def delete(self, name: str):
        """
        删除版本元数据
        
        Args:
            name: 版本名称
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 删除版本记录（级联删除变更记录）
            cursor.execute('DELETE FROM versions WHERE name = ?', (name,))
            
            if cursor.rowcount == 0:
                raise RuntimeError(f"版本不存在: {name}")
            
            conn.commit()
            self.logger.info(f"删除元数据: {name}")
            
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"删除元数据失败: {str(e)}")
        finally:
            conn.close()
    
    def list(
        self,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[VersionMetadata]:
        """
        列出版本列表
        
        Args:
            limit: 限制返回数量
            search: 搜索关键词
            from_date: 起始日期
            to_date: 结束日期
            
        Returns:
            List[VersionMetadata]: 版本元数据列表
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 构建查询条件
            query = '''
                SELECT name, timestamp, trigger, summary, snapshot_path, user_comment, size_bytes
                FROM versions
            '''
            conditions = []
            params = []
            
            if search:
                conditions.append('(name LIKE ? OR summary LIKE ? OR user_comment LIKE ?)')
                search_pattern = f'%{search}%'
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if from_date:
                conditions.append('timestamp >= ?')
                params.append(from_date)
            
            if to_date:
                conditions.append('timestamp <= ?')
                params.append(to_date)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY timestamp DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            
            versions = []
            for row in cursor.fetchall():
                # 对于列表查询，只加载基本信息，不加载变更记录以提高性能
                metadata = VersionMetadata(
                    name=row[0],
                    timestamp=row[1],
                    trigger=row[2],
                    summary=row[3],
                    snapshot_path=row[4],
                    user_comment=row[5],
                    changes=[],  # 不加载变更记录
                    size_bytes=row[6]
                )
                versions.append(metadata)
            
            return versions
            
        finally:
            conn.close()
    
    def count(self) -> int:
        """
        获取版本总数
        
        Returns:
            int: 版本数量
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM versions')
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_latest_version(self) -> Optional[VersionMetadata]:
        """
        获取最新版本
        
        Returns:
            Optional[VersionMetadata]: 最新版本元数据
        """
        versions = self.list(limit=1)
        return versions[0] if versions else None
    
    def get_previous_version(self, current_version: str) -> Optional[VersionMetadata]:
        """
        获取上一个版本
        
        Args:
            current_version: 当前版本名称
            
        Returns:
            Optional[VersionMetadata]: 上一个版本元数据
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 获取当前版本的时间戳
            cursor.execute('SELECT timestamp FROM versions WHERE name = ?', (current_version,))
            current_timestamp = cursor.fetchone()
            
            if not current_timestamp:
                return None
            
            # 获取时间戳早于当前版本的最新版本
            cursor.execute('''
                SELECT name, timestamp, trigger, summary, snapshot_path, user_comment, size_bytes
                FROM versions 
                WHERE timestamp < ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (current_timestamp[0],))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            metadata = VersionMetadata(
                name=row[0],
                timestamp=row[1],
                trigger=row[2],
                summary=row[3],
                snapshot_path=row[4],
                user_comment=row[5],
                changes=[],  # 不加载变更记录
                size_bytes=row[6]
            )
            
            return metadata
            
        finally:
            conn.close()
    
    def search_by_content(self, keyword: str) -> List[VersionMetadata]:
        """
        根据内容搜索版本
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[VersionMetadata]: 匹配的版本列表
        """
        # 这个方法需要更复杂的实现，比如全文搜索
        # 这里简化实现，只在摘要和注释中搜索
        return self.list(search=keyword)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 版本总数
            cursor.execute('SELECT COUNT(*) FROM versions')
            total_versions = cursor.fetchone()[0]
            
            # 总存储大小
            cursor.execute('SELECT COALESCE(SUM(size_bytes), 0) FROM versions')
            total_size = cursor.fetchone()[0]
            
            # 最新版本时间
            cursor.execute('SELECT MAX(timestamp) FROM versions')
            latest_timestamp = cursor.fetchone()[0]
            
            # 按触发类型统计
            cursor.execute('SELECT trigger, COUNT(*) FROM versions GROUP BY trigger')
            trigger_stats = dict(cursor.fetchall())
            
            return {
                'total_versions': total_versions,
                'total_size_bytes': total_size,
                'latest_timestamp': latest_timestamp,
                'trigger_stats': trigger_stats
            }
            
        finally:
            conn.close()