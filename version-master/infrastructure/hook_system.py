"""
钩子系统

提供事件响应机制，支持 before_compaction 和 before_prompt_build 等钩子。
"""

import asyncio
from typing import Dict, List, Callable, Any, Optional
from enum import Enum


class HookType(Enum):
    """钩子类型枚举"""
    BEFORE_COMPACTION = "before_compaction"
    BEFORE_PROMPT_BUILD = "before_prompt_build"
    BEFORE_SAVE = "before_save"
    AFTER_SAVE = "after_save"
    BEFORE_RESTORE = "before_restore"
    AFTER_RESTORE = "after_restore"


class HookSystem:
    """
    钩子系统
    
    提供事件响应机制，支持多种钩子类型。
    """
    
    def __init__(self, logger):
        self.logger = logger
        self._hooks: Dict[HookType, List[Callable]] = {}
        self._initialize_hooks()
    
    def _initialize_hooks(self):
        """初始化钩子字典"""
        for hook_type in HookType:
            self._hooks[hook_type] = []
    
    def register_hook(self, hook_type: HookType, callback: Callable):
        """
        注册钩子
        
        Args:
            hook_type: 钩子类型
            callback: 回调函数
        """
        if hook_type not in self._hooks:
            self._hooks[hook_type] = []
        
        self._hooks[hook_type].append(callback)
        self.logger.info(f"注册钩子: {hook_type.value}")
    
    def unregister_hook(self, hook_type: HookType, callback: Callable):
        """
        注销钩子
        
        Args:
            hook_type: 钩子类型
            callback: 回调函数
        """
        if hook_type in self._hooks:
            if callback in self._hooks[hook_type]:
                self._hooks[hook_type].remove(callback)
                self.logger.info(f"注销钩子: {hook_type.value}")
    
    async def trigger_hooks(self, hook_type: HookType, *args, **kwargs) -> List[Any]:
        """
        触发钩子
        
        Args:
            hook_type: 钩子类型
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            List[Any]: 所有钩子的返回值
        """
        results = []
        
        if hook_type not in self._hooks:
            return results
        
        self.logger.info(f"触发钩子: {hook_type.value}")
        
        for callback in self._hooks[hook_type]:
            try:
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(callback):
                    result = await callback(*args, **kwargs)
                else:
                    result = callback(*args, **kwargs)
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"钩子执行失败 {hook_type.value}: {str(e)}")
                results.append(None)
        
        return results
    
    def get_registered_hooks(self) -> Dict[HookType, int]:
        """
        获取已注册的钩子统计
        
        Returns:
            Dict[HookType, int]: 钩子类型和数量的映射
        """
        return {
            hook_type: len(callbacks)
            for hook_type, callbacks in self._hooks.items()
        }
    
    # 预定义钩子实现
    
    async def before_compaction_hook(self, context: Dict[str, Any]) -> bool:
        """
        上下文压缩前钩子
        
        Args:
            context: 压缩上下文
            
        Returns:
            bool: 是否允许压缩
        """
        self.logger.info("执行 before_compaction 钩子")
        
        # 在实际实现中，这里可以检查是否有未保存的更改
        # 如果有重要更改，可以返回 False 阻止压缩
        
        return True
    
    async def before_prompt_build_hook(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建提示前钩子
        
        Args:
            prompt_data: 提示数据
            
        Returns:
            Dict[str, Any]: 修改后的提示数据
        """
        self.logger.info("执行 before_prompt_build 钩子")
        
        # 在实际实现中，这里可以添加版本信息到提示中
        # 例如，添加当前版本状态信息
        
        if 'version_info' not in prompt_data:
            prompt_data['version_info'] = {
                'has_unsaved_changes': True,  # 模拟有未保存更改
                'current_version': 'v1.0',
                'last_saved': '2026-03-22 10:00:00'
            }
        
        return prompt_data
    
    async def before_save_hook(self, version_name: str, changes: List[Any]) -> bool:
        """
        保存前钩子
        
        Args:
            version_name: 版本名称
            changes: 变更列表
            
        Returns:
            bool: 是否允许保存
        """
        self.logger.info(f"执行 before_save 钩子: {version_name}")
        
        # 在实际实现中，这里可以检查版本名称是否合法
        # 或者验证变更是否重要
        
        return True
    
    async def after_save_hook(self, version_name: str, result: Dict[str, Any]):
        """
        保存后钩子
        
        Args:
            version_name: 版本名称
            result: 保存结果
        """
        self.logger.info(f"执行 after_save 钩子: {version_name}")
        
        # 在实际实现中，这里可以发送通知
        # 或者更新相关状态
    
    async def before_restore_hook(self, version_name: str) -> bool:
        """
        恢复前钩子
        
        Args:
            version_name: 版本名称
            
        Returns:
            bool: 是否允许恢复
        """
        self.logger.info(f"执行 before_restore 钩子: {version_name}")
        
        # 在实际实现中，这里可以检查是否有未保存的更改
        # 或者验证目标版本是否存在
        
        return True
    
    async def after_restore_hook(self, version_name: str, result: Dict[str, Any]):
        """
        恢复后钩子
        
        Args:
            version_name: 版本名称
            result: 恢复结果
        """
        self.logger.info(f"执行 after_restore 钩子: {version_name}")
        
        # 在实际实现中，这里可以更新界面状态
        # 或者记录恢复操作
    
    def register_default_hooks(self):
        """注册默认钩子"""
        # 注册预定义的钩子
        self.register_hook(HookType.BEFORE_COMPACTION, self.before_compaction_hook)
        self.register_hook(HookType.BEFORE_PROMPT_BUILD, self.before_prompt_build_hook)
        self.register_hook(HookType.BEFORE_SAVE, self.before_save_hook)
        self.register_hook(HookType.AFTER_SAVE, self.after_save_hook)
        self.register_hook(HookType.BEFORE_RESTORE, self.before_restore_hook)
        self.register_hook(HookType.AFTER_RESTORE, self.after_restore_hook)
        
        self.logger.info("注册默认钩子完成")
    
    async def cleanup(self):
        """清理钩子系统"""
        self._hooks.clear()
        self._initialize_hooks()
        self.logger.info("钩子系统已清理")