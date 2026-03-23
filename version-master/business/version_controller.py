"""
Version Controller

Core business logic for Version-Master skill, implementing version management use cases.
Provides save, restore, list, diff, and clean operations with intelligent features.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from data.models import (
    Intent, SaveResult, RestoreResult, ListVersionsResult, DiffResult, CleanResult,
    VersionMetadata, Change, ChangeType, VersionMasterError, NoChangesError,
    SaveFailedError, RestoreFailedError, VersionNotFoundError, 
    UncommittedChangesError, ConfirmationRequiredError, MissingParameterError, InvalidIntentError
)


class VersionController:
    """
    Version Controller
    
    Core business logic for Version-Master skill, implementing version management use cases.
    Provides save, restore, list, diff, and clean operations with intelligent features.
    """
    
    def __init__(
        self,
        snapshot_repo,
        metadata_repo,
        llm_client,
        storage_optimizer,
        logger
    ):
        self.snapshot_repo = snapshot_repo
        self.metadata_repo = metadata_repo
        self.llm_client = llm_client
        self.storage_optimizer = storage_optimizer
        self.logger = logger
        self.workspace_path = Path.cwd()
    
    # ============ Save Use Case ============
    
    async def save_version(
        self,
        name: Optional[str] = None,
        message: Optional[str] = None,
        trigger: str = "manual"
    ) -> SaveResult:
        """
        保存当前工作区为版本
        
        Args:
            name: 版本名称(可选,未指定时由大模型生成)
            message: 用户自定义注释
            trigger: 触发方式 (manual | auto)
            
        Returns:
            SaveResult: 保存结果
            
        Raises:
            NoChangesError: 工作区无变更
            SaveFailedError: 保存失败
        """
        try:
            # 1. 检测变更
            changes = self._detect_changes()
            if not changes:
                raise NoChangesError("工作区无变更,未保存新版本")
            
            # 2. 生成版本名称(未指定时)
            if not name:
                name = await self._generate_smart_name(changes)
            
            # 3. 生成变更摘要(依赖大模型)
            summary = await self._generate_summary(changes)
            
            # 4. 创建快照(异步,不阻塞)
            snapshot_id = await self._create_snapshot_async(name)
            
            # 5. 保存元数据
            metadata = VersionMetadata(
                name=name,
                timestamp=datetime.now().isoformat(),
                trigger=trigger,
                summary=summary,
                snapshot_path=snapshot_id,
                user_comment=message or "",
                changes=changes
            )
            self.metadata_repo.save(metadata)
            
            # 6. 异步执行存储优化
            await self.storage_optimizer.auto_cleanup_async()
            
            # 7. 记录日志
            self.logger.info(f"保存版本: {name}")
            
            # 8. 返回结果
            return SaveResult(
                success=True,
                version_name=name,
                timestamp=metadata.timestamp,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"保存版本失败: {str(e)}")
            if isinstance(e, VersionMasterError):
                raise
            raise SaveFailedError(f"保存失败: {str(e)}")
    
    async def _generate_smart_name(self, changes: List[Change]) -> str:
        """
        依赖大模型智能生成版本名称
        
        不是简单的规则算法,而是利用 LLM 的强大能力
        理解变更上下文并生成有意义的名称。
        """
        prompt = f"""
        基于以下文件变更,生成一个简洁、有意义的版本名称(不超过20个字符):
        
        变更列表:
        {self._format_changes(changes)}
        
        要求:
        1. 名称要简洁明了
        2. 突出主要变更点
        3. 使用中文
        4. 不包含时间戳
        """
        
        name = await self.llm_client.generate_text(prompt)
        return name.strip()
    
    async def _generate_summary(self, changes: List[Change]) -> str:
        """
        依赖大模型智能生成变更摘要
        
        不是简单的文件列表,而是用自然语言描述变更内容
        """
        prompt = f"""
        基于以下文件变更,生成一个简洁的变更摘要(不超过50个字符):
        
        变更列表:
        {self._format_changes(changes)}
        
        要求:
        1. 用自然语言描述主要变更
        2. 使用中文
        3. 突出关键变更
        """
        
        summary = await self.llm_client.generate_text(prompt)
        return summary.strip()
    
    def _detect_changes(self) -> List[Change]:
        """检测工作区变更"""
        # 在实际实现中，这里会比较当前工作区与最新版本
        # 暂时返回模拟数据
        return [
            Change(
                file_path="src/auth.py",
                change_type=ChangeType.MODIFIED,
                size_bytes=1024,
                timestamp=datetime.now().isoformat(),
                content_hash="abc123"
            ),
            Change(
                file_path="src/models/user.py",
                change_type=ChangeType.ADDED,
                size_bytes=2048,
                timestamp=datetime.now().isoformat(),
                content_hash="def456"
            )
        ]
    
    def _format_changes(self, changes: List[Change]) -> str:
        """格式化变更列表用于提示"""
        return "\n".join([
            f"- {change.file_path} ({change.change_type.value})"
            for change in changes
        ])
    
    async def _create_snapshot_async(self, name: str) -> str:
        """异步创建快照"""
        # 在实际实现中，这里会异步执行文件复制
        await asyncio.sleep(0.1)
        return f"snapshot_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # ============ Restore Use Case ============
    
    async def restore_version(
        self,
        version_name: str,
        force: bool = False
    ) -> RestoreResult:
        """
        恢复到指定版本
        
        Args:
            version_name: 版本名称
            force: 是否跳过警告强制恢复
            
        Returns:
            RestoreResult: 恢复结果
            
        Raises:
            VersionNotFoundError: 版本不存在
            RestoreFailedError: 恢复失败
        """
        try:
            # 1. 查找版本
            version = self.metadata_repo.find(version_name)
            if not version:
                # 提供相似版本建议
                suggestions = self._find_similar_versions(version_name)
                raise VersionNotFoundError(
                    f"版本 '{version_name}' 不存在",
                    suggestions=suggestions
                )
            
            # 2. 检测工作区未提交更改
            current_changes = self._detect_changes()
            if current_changes and not force:
                raise UncommittedChangesError(
                    "工作区有未提交的更改,恢复将覆盖这些更改",
                    changes=current_changes
                )
            
            # 3. 执行原子性恢复
            await self._restore_atomic(version)
            
            # 4. 记录日志
            self.logger.info(f"恢复版本: {version_name}")
            
            # 5. 返回结果
            return RestoreResult(
                success=True,
                version_name=version_name,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"恢复版本失败: {str(e)}")
            if isinstance(e, VersionMasterError):
                raise
            raise RestoreFailedError(f"恢复失败: {str(e)}")
    
    async def _restore_atomic(self, version: VersionMetadata):
        """
        原子性恢复: 备份 → 替换 → 验证 → 确认/回滚
        
        使用三阶段协议保证原子性
        """
        backup_path = None
        
        try:
            # 阶段1: 备份当前工作区
            backup_path = self._backup_workspace()
            
            # 阶段2: 从快照恢复
            await self._restore_from_snapshot(version.snapshot_path)
            
            # 阶段3: 验证恢复结果
            if self._verify_workspace_integrity():
                # 恢复成功,删除备份
                self._cleanup_backup(backup_path)
            else:
                raise RestoreFailedError("验证失败")
        
        except Exception as e:
            # 失败: 回滚到备份
            if backup_path:
                await self._rollback_to_backup(backup_path)
            raise RestoreFailedError(f"恢复失败: {str(e)}")
    
    def _backup_workspace(self) -> str:
        """备份当前工作区"""
        # 在实际实现中，这里会创建临时备份
        return "backup_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    
    async def _restore_from_snapshot(self, snapshot_path: str):
        """从快照恢复"""
        # 在实际实现中，这里会复制文件
        await asyncio.sleep(0.1)
    
    def _verify_workspace_integrity(self) -> bool:
        """验证工作区完整性"""
        # 在实际实现中，这里会检查文件完整性
        return True
    
    async def _rollback_to_backup(self, backup_path: str):
        """回滚到备份"""
        # 在实际实现中，这里会从备份恢复
        await asyncio.sleep(0.1)
    
    def _cleanup_backup(self, backup_path: str):
        """清理备份"""
        # 在实际实现中，这里会删除备份文件
        pass
    
    def _find_similar_versions(self, version_name: str) -> List[str]:
        """查找相似版本"""
        # 在实际实现中，这里会使用模糊匹配算法
        return ["v1.0", "v1.1", "v2.0"]
    
    # ============ List Use Case ============
    
    def list_versions(
        self,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> ListVersionsResult:
        """
        列出版本列表
        
        Args:
            limit: 限制返回数量
            search: 搜索关键词
            from_date: 起始日期
            to_date: 结束日期
            
        Returns:
            ListVersionsResult: 列表结果
        """
        # 1. 查询元数据
        versions = self.metadata_repo.list(
            limit=limit,
            search=search,
            from_date=from_date,
            to_date=to_date
        )
        
        # 2. 计算快照大小
        for version in versions:
            version.size_bytes = self.snapshot_repo.get_size(version.snapshot_path)
        
        # 3. 返回结果
        return ListVersionsResult(
            versions=versions,
            total_count=len(versions),
            total_size_bytes=sum(v.size_bytes or 0 for v in versions)
        )
    
    # ============ Diff Use Case ============
    
    def diff_versions(
        self,
        version1: Optional[str] = None,
        version2: Optional[str] = None
    ) -> DiffResult:
        """
        对比版本差异
        
        Args:
            version1: 第一个版本(未指定时使用当前工作区)
            version2: 第二个版本
            
        Returns:
            DiffResult: 差异结果
        """
        # 1. 确定对比对象
        if version2 is None:
            # 对比当前工作区与指定版本
            current_changes = self._detect_changes()
            return DiffResult(
                compared_with="current",
                changes=current_changes
            )
        else:
            # 对比两个版本
            version1_meta = self.metadata_repo.find(version1)
            version2_meta = self.metadata_repo.find(version2)
            
            changes = self._compare_snapshots(
                version1_meta.snapshot_path,
                version2_meta.snapshot_path
            )
            
            return DiffResult(
                compared_with=f"{version1} vs {version2}",
                changes=changes
            )
    
    def _compare_snapshots(self, snapshot1: str, snapshot2: str) -> List[Change]:
        """比较两个快照的差异"""
        # 在实际实现中，这里会比较文件内容
        return self._detect_changes()
    
    # ============ Clean Use Case ============
    
    async def clean_versions(
        self,
        version: Optional[str] = None,
        auto: bool = False,
        confirm: bool = False
    ) -> CleanResult:
        """
        清理版本
        
        Args:
            version: 指定删除的版本
            auto: 执行自动清理
            confirm: 是否确认
            
        Returns:
            CleanResult: 清理结果
        """
        if auto:
            # 自动清理策略
            deleted_versions = await self.storage_optimizer.auto_cleanup()
        else:
            # 手动删除指定版本
            if not version:
                raise MissingParameterError("需要指定版本名称或使用 --auto")
            
            if not confirm:
                raise ConfirmationRequiredError(
                    f"确认删除版本 '{version}'? 使用 --confirm 确认"
                )
            
            version_meta = self.metadata_repo.find(version)
            if not version_meta:
                raise VersionNotFoundError(f"版本 '{version}' 不存在")
            
            # 删除快照和元数据
            self.snapshot_repo.delete(version_meta.snapshot_path)
            self.metadata_repo.delete(version)
            deleted_versions = [version]
        
        return CleanResult(
            deleted_versions=deleted_versions,
            freed_space_bytes=1024 * 1024  # 模拟释放空间
        )