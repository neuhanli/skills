"""
编排服务

负责操作流程编排、事务边界管理和异步任务调度。
"""

import asyncio
from typing import Dict, Any, Optional
from data.models import Intent, IntentType
from business.version_controller import VersionController
from nlp.intent_parser import IntentParser


class OrchestrationService:
    """
    编排服务
    
    负责操作流程编排、事务边界管理和异步任务调度。
    """
    
    def __init__(
        self,
        intent_parser: IntentParser,
        version_controller: VersionController,
        logger
    ):
        self.intent_parser = intent_parser
        self.version_controller = version_controller
        self.logger = logger
        self._active_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_intent(self, user_input: str) -> Dict[str, Any]:
        """
        执行用户意图
        
        Args:
            user_input: 用户自然语言输入
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 1. 解析意图
            intent = await self.intent_parser.parse(user_input)
            
            # 2. 记录意图
            self.logger.info(f"解析意图: {intent.type.value}")
            
            # 3. 根据意图类型执行相应操作
            result = await self._execute_by_intent_type(intent)
            
            # 4. 记录执行结果
            self.logger.info(f"意图执行完成: {intent.type.value}")
            
            return {
                "success": True,
                "intent_type": intent.type.value,
                "result": result,
                "message": self._format_success_message(intent.type)
            }
            
        except Exception as e:
            self.logger.error(f"意图执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._format_error_message(str(e))
            }
    
    async def _execute_by_intent_type(self, intent: Intent) -> Any:
        """根据意图类型执行相应操作"""
        if intent.type == IntentType.SAVE:
            return await self._execute_save(intent)
        elif intent.type == IntentType.RESTORE:
            return await self._execute_restore(intent)
        elif intent.type == IntentType.LIST:
            return await self._execute_list(intent)
        elif intent.type == IntentType.DIFF:
            return await self._execute_diff(intent)
        elif intent.type == IntentType.CLEAN:
            return await self._execute_clean(intent)
        else:
            raise ValueError(f"未知意图类型: {intent.type}")
    
    async def _execute_save(self, intent: Intent) -> Any:
        """执行保存操作"""
        name = intent.params.get('name')
        message = intent.params.get('message')
        
        result = await self.version_controller.save_version(
            name=name,
            message=message
        )
        
        return {
            "version_name": result.version_name,
            "timestamp": result.timestamp,
            "summary": result.summary
        }
    
    async def _execute_restore(self, intent: Intent) -> Any:
        """执行恢复操作"""
        version = intent.params.get('version')
        force = intent.params.get('force', False)
        
        result = await self.version_controller.restore_version(
            version_name=version,
            force=force
        )
        
        return {
            "version_name": result.version_name,
            "timestamp": result.timestamp
        }
    
    async def _execute_list(self, intent: Intent) -> Any:
        """执行列表操作"""
        limit = intent.params.get('limit')
        search = intent.params.get('search')
        from_date = intent.params.get('from_date')
        to_date = intent.params.get('to_date')
        
        result = self.version_controller.list_versions(
            limit=limit,
            search=search,
            from_date=from_date,
            to_date=to_date
        )
        
        return {
            "versions": [
                {
                    "name": v.name,
                    "timestamp": v.timestamp,
                    "summary": v.summary,
                    "size_bytes": v.size_bytes
                }
                for v in result.versions
            ],
            "total_count": result.total_count,
            "total_size_bytes": result.total_size_bytes
        }
    
    async def _execute_diff(self, intent: Intent) -> Any:
        """执行对比操作"""
        version1 = intent.params.get('version1')
        version2 = intent.params.get('version2')
        
        result = self.version_controller.diff_versions(
            version1=version1,
            version2=version2
        )
        
        return {
            "compared_with": result.compared_with,
            "changes": [
                {
                    "file_path": c.file_path,
                    "change_type": c.change_type.value,
                    "size_bytes": c.size_bytes
                }
                for c in result.changes
            ],
            "summary": result.summary
        }
    
    async def _execute_clean(self, intent: Intent) -> Any:
        """执行清理操作"""
        version = intent.params.get('version')
        auto = intent.params.get('auto', False)
        confirm = intent.params.get('confirm', False)
        
        result = await self.version_controller.clean_versions(
            version=version,
            auto=auto,
            confirm=confirm
        )
        
        return {
            "deleted_versions": result.deleted_versions,
            "freed_space_bytes": result.freed_space_bytes,
            "operation_type": "clean"
        }
    
    def _format_success_message(self, intent_type: IntentType) -> str:
        """格式化成功消息"""
        messages = {
            IntentType.SAVE: "版本保存成功",
            IntentType.RESTORE: "版本恢复成功",
            IntentType.LIST: "版本列表获取成功",
            IntentType.DIFF: "版本对比完成",
            IntentType.CLEAN: "版本清理完成"
        }
        return messages.get(intent_type, "操作执行成功")
    
    def _format_error_message(self, error: str) -> str:
        """格式化错误消息"""
        # 在实际实现中，这里会根据错误类型提供更友好的消息
        return f"操作执行失败: {error}"
    
    async def execute_async(self, user_input: str, task_id: str) -> str:
        """
        异步执行用户意图
        
        Args:
            user_input: 用户输入
            task_id: 任务ID
            
        Returns:
            str: 任务ID
        """
        if task_id in self._active_tasks:
            raise ValueError(f"任务ID已存在: {task_id}")
        
        # 创建异步任务
        task = asyncio.create_task(self.execute_intent(user_input))
        self._active_tasks[task_id] = task
        
        # 设置任务完成回调
        task.add_done_callback(lambda t: self._cleanup_task(task_id))
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 任务状态
        """
        if task_id not in self._active_tasks:
            return {"status": "not_found"}
        
        task = self._active_tasks[task_id]
        
        if task.done():
            try:
                result = task.result()
                return {
                    "status": "completed",
                    "result": result
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            return {"status": "running"}
    
    def _cleanup_task(self, task_id: str):
        """清理已完成的任务"""
        if task_id in self._active_tasks:
            del self._active_tasks[task_id]
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        if task_id not in self._active_tasks:
            return False
        
        task = self._active_tasks[task_id]
        if not task.done():
            task.cancel()
            return True
        
        return False
    
    def get_active_tasks(self) -> Dict[str, str]:
        """获取活跃任务列表"""
        return {
            task_id: "running" if not task.done() else "completed"
            for task_id, task in self._active_tasks.items()
        }