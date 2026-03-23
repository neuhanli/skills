"""
存储优化器

负责自动清理策略和空间计算，优化存储空间使用。
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path


class StorageOptimizer:
    """
    存储优化器
    
    负责自动清理策略和空间计算，优化存储空间使用。
    """
    
    def __init__(self, snapshot_repo, metadata_repo, file_system, logger):
        self.snapshot_repo = snapshot_repo
        self.metadata_repo = metadata_repo
        self.file_system = file_system
        self.logger = logger
        
        # 默认配置
        self.config = {
            'max_versions': 50,  # 最大版本数量
            'max_age_days': 30,  # 最大保留天数
            'min_free_space_gb': 1,  # 最小空闲空间(GB)
            'cleanup_strategy': 'smart',  # 清理策略: smart, age, count
        }
    
    async def auto_cleanup_async(self) -> List[str]:
        """
        异步执行自动清理
        
        Returns:
            List[str]: 被清理的版本列表
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.auto_cleanup
        )
    
    def auto_cleanup(self) -> List[str]:
        """
        执行自动清理
        
        Returns:
            List[str]: 被清理的版本列表
        """
        try:
            # 检查是否需要清理
            if not self._needs_cleanup():
                return []
            
            # 根据策略选择清理方法
            if self.config['cleanup_strategy'] == 'smart':
                versions_to_clean = self._smart_cleanup_strategy()
            elif self.config['cleanup_strategy'] == 'age':
                versions_to_clean = self._age_based_cleanup_strategy()
            elif self.config['cleanup_strategy'] == 'count':
                versions_to_clean = self._count_based_cleanup_strategy()
            else:
                versions_to_clean = self._smart_cleanup_strategy()
            
            # 执行清理
            cleaned_versions = []
            for version_name in versions_to_clean:
                try:
                    self.snapshot_repo.delete(version_name)
                    self.metadata_repo.delete(version_name)
                    cleaned_versions.append(version_name)
                    self.logger.info(f"自动清理版本: {version_name}")
                except Exception as e:
                    self.logger.warning(f"清理版本失败 {version_name}: {str(e)}")
            
            return cleaned_versions
            
        except Exception as e:
            self.logger.error(f"自动清理失败: {str(e)}")
            return []
    
    def _needs_cleanup(self) -> bool:
        """检查是否需要清理"""
        # 检查版本数量
        total_versions = self.metadata_repo.count()
        if total_versions > self.config['max_versions']:
            return True
        
        # 检查存储空间
        free_space_gb = self.file_system.get_available_space() / (1024**3)
        if free_space_gb < self.config['min_free_space_gb']:
            return True
        
        return False
    
    def _smart_cleanup_strategy(self) -> List[str]:
        """智能清理策略"""
        # 获取所有版本
        all_versions = self.metadata_repo.list()
        
        if len(all_versions) <= self.config['max_versions']:
            return []
        
        # 计算每个版本的得分
        version_scores = []
        for version in all_versions:
            score = self._calculate_version_score(version)
            version_scores.append((version.name, score))
        
        # 按得分排序（得分低的优先清理）
        version_scores.sort(key=lambda x: x[1])
        
        # 选择需要清理的版本
        versions_to_keep = self.config['max_versions']
        versions_to_clean = [
            name for name, score in version_scores[versions_to_keep:]
        ]
        
        return versions_to_clean
    
    def _age_based_cleanup_strategy(self) -> List[str]:
        """基于时间的清理策略"""
        cutoff_date = datetime.now() - timedelta(days=self.config['max_age_days'])
        
        # 获取所有版本
        all_versions = self.metadata_repo.list()
        
        versions_to_clean = []
        for version in all_versions:
            version_date = datetime.fromisoformat(version.timestamp.replace('Z', '+00:00'))
            if version_date < cutoff_date:
                versions_to_clean.append(version.name)
        
        return versions_to_clean
    
    def _count_based_cleanup_strategy(self) -> List[str]:
        """基于数量的清理策略"""
        # 获取所有版本（按时间倒序）
        all_versions = self.metadata_repo.list()
        
        if len(all_versions) <= self.config['max_versions']:
            return []
        
        # 保留最新的 N 个版本，清理其余的
        versions_to_keep = self.config['max_versions']
        versions_to_clean = [version.name for version in all_versions[versions_to_keep:]]
        
        return versions_to_clean
    
    def _calculate_version_score(self, version) -> float:
        """计算版本得分"""
        score = 0.0
        
        # 时间因素：越新的版本得分越高
        version_date = datetime.fromisoformat(version.timestamp.replace('Z', '+00:00'))
        days_ago = (datetime.now() - version_date).days
        time_score = max(0, 1.0 - (days_ago / 30))  # 30天内线性衰减
        score += time_score * 0.4
        
        # 大小因素：越小的版本得分越高
        size_mb = (version.size_bytes or 0) / (1024 * 1024)
        size_score = max(0, 1.0 - min(size_mb / 100, 1.0))  # 100MB内线性衰减
        score += size_score * 0.3
        
        # 重要性因素：手动保存的版本得分更高
        importance_score = 1.0 if version.trigger == 'manual' else 0.5
        score += importance_score * 0.3
        
        return score
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        total_versions = self.metadata_repo.count()
        
        # 计算总存储大小
        total_size_bytes = 0
        all_versions = self.metadata_repo.list()
        for version in all_versions:
            total_size_bytes += version.size_bytes or 0
        
        # 获取文件系统信息
        total_space = self.file_system.get_total_space()
        used_space = self.file_system.get_used_space()
        free_space = self.file_system.get_available_space()
        
        return {
            'total_versions': total_versions,
            'total_size_bytes': total_size_bytes,
            'total_space_bytes': total_space,
            'used_space_bytes': used_space,
            'free_space_bytes': free_space,
            'used_percentage': (used_space / total_space * 100) if total_space > 0 else 0
        }
    
    def get_cleanup_recommendation(self) -> Dict[str, Any]:
        """获取清理建议"""
        stats = self.get_storage_statistics()
        
        recommendation = {
            'needs_cleanup': self._needs_cleanup(),
            'recommended_action': 'none',
            'estimated_space_to_free': 0,
            'versions_to_clean': []
        }
        
        if not recommendation['needs_cleanup']:
            return recommendation
        
        # 根据当前策略生成建议
        if self.config['cleanup_strategy'] == 'smart':
            versions_to_clean = self._smart_cleanup_strategy()
            recommendation['recommended_action'] = 'smart_cleanup'
        elif self.config['cleanup_strategy'] == 'age':
            versions_to_clean = self._age_based_cleanup_strategy()
            recommendation['recommended_action'] = 'age_based_cleanup'
        else:
            versions_to_clean = self._count_based_cleanup_strategy()
            recommendation['recommended_action'] = 'count_based_cleanup'
        
        # 计算预计释放的空间
        estimated_space = 0
        for version_name in versions_to_clean:
            version = self.metadata_repo.find(version_name)
            if version and version.size_bytes:
                estimated_space += version.size_bytes
        
        recommendation['versions_to_clean'] = versions_to_clean
        recommendation['estimated_space_to_free'] = estimated_space
        
        return recommendation
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)
        self.logger.info(f"更新存储优化配置: {new_config}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config.copy()