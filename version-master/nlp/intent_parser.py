"""
Intent Parser

Natural language understanding component for Version-Master skill.
Parses user input to extract structured intents and parameters.
"""

import json
from typing import Dict, Any, List
from data.models import Intent, IntentType, VersionMasterError, InvalidIntentError, MissingParameterError


class IntentParser:
    """
    自然语言意图解析器
    
    依赖大模型进行意图识别和参数提取，
    避免弱智的规则匹配算法。
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载意图模式定义"""
        return {
            IntentType.SAVE.value: {
                'required': [],
                'optional': ['name', 'message'],
                'description': '保存当前工作区为版本'
            },
            IntentType.RESTORE.value: {
                'required': ['version'],
                'optional': ['force'],
                'description': '恢复到指定版本'
            },
            IntentType.LIST.value: {
                'required': [],
                'optional': ['limit', 'search', 'from_date', 'to_date'],
                'description': '列出版本列表'
            },
            IntentType.DIFF.value: {
                'required': [],
                'optional': ['version1', 'version2'],
                'description': '对比版本差异'
            },
            IntentType.CLEAN.value: {
                'required': [],
                'optional': ['version', 'auto'],
                'description': '清理版本'
            }
        }
    
    async def parse(self, user_input: str) -> Intent:
        """
        解析用户输入为结构化意图
        
        Args:
            user_input: 用户自然语言输入
            
        Returns:
            Intent: 包含意图类型和参数的结构化对象
        """
        # 调用大模型解析
        parsed = await self._parse_with_llm(user_input)
        
        # 验证和规范化
        validated = self._validate_intent(parsed)
        
        # 处理相对引用
        resolved = await self._resolve_relative_references(validated)
        
        return resolved
    
    async def _parse_with_llm(self, user_input: str) -> Dict[str, Any]:
        """使用大模型解析用户意图"""
        prompt = f"""
        请解析以下用户输入，识别意图类型并提取参数。
        
        用户输入: "{user_input}"
        
        可用的意图类型:
        - save: 保存当前版本
        - restore: 恢复到指定版本  
        - list: 列出版本列表
        - diff: 对比版本差异
        - clean: 清理版本
        
        请返回 JSON 格式的结果，包含以下字段:
        {{
            "intent_type": "意图类型",
            "confidence": 置信度(0-1),
            "parameters": {{
                "参数名": "参数值"
            }}
        }}
        
        注意: 参数值可以是字符串、布尔值或数字。
        """
        
        response = await self.llm_client.generate_text(prompt)
        
        try:
            # 尝试解析 JSON 响应
            result = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，使用启发式规则
            return self._fallback_parse(user_input)
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """启发式规则解析（备用方案）"""
        user_input_lower = user_input.lower()
        
        # 简单的关键词匹配（调整优先级避免冲突）
        if any(word in user_input_lower for word in ['清理', '删除', '清除', '移除']):
            intent_type = IntentType.CLEAN.value
        elif any(word in user_input_lower for word in ['保存', '备份', '存一下', '快照']):
            intent_type = IntentType.SAVE.value
        elif any(word in user_input_lower for word in ['恢复', '回滚', '还原', '回到']):
            intent_type = IntentType.RESTORE.value
        elif any(word in user_input_lower for word in ['列表', '查看', '显示', '所有']):
            intent_type = IntentType.LIST.value
        elif any(word in user_input_lower for word in ['对比', '比较', '差异', '区别']):
            intent_type = IntentType.DIFF.value
        else:
            intent_type = IntentType.SAVE.value  # 默认意图
        
        return {
            "intent_type": intent_type,
            "confidence": 0.7,  # 中等置信度
            "parameters": {}
        }
    
    def _validate_intent(self, parsed: Dict[str, Any]) -> Intent:
        """验证意图的有效性"""
        intent_type_str = parsed.get('intent_type', '')
        confidence = parsed.get('confidence', 0.5)
        parameters = parsed.get('parameters', {})
        
        # 验证意图类型
        if intent_type_str not in self.intent_patterns:
            raise InvalidIntentError(f"未知意图类型: {intent_type_str}")
        
        # 验证必需参数
        required_params = self.intent_patterns[intent_type_str]['required']
        for param in required_params:
            if param not in parameters:
                raise MissingParameterError(f"缺少必需参数: {param}")
        
        # 创建 Intent 对象
        intent_type = IntentType(intent_type_str)
        return Intent(
            type=intent_type,
            params=parameters,
            confidence=confidence,
            original_input=parsed.get('original_input', '')
        )
    
    async def _resolve_relative_references(self, intent: Intent) -> Intent:
        """解析相对引用(如'上个版本')"""
        if intent.type == IntentType.RESTORE:
            version_param = intent.params.get('version')
            
            if version_param == 'latest':
                # 获取最新版本
                latest_version = await self._get_latest_version()
                if latest_version:
                    intent.params['version'] = latest_version
                else:
                    # 无法解析时保持原始值，不抛出异常
                    pass
            elif version_param == 'previous':
                # 获取上一个版本
                previous_version = await self._get_previous_version()
                if previous_version:
                    intent.params['version'] = previous_version
                else:
                    # 无法解析时保持原始值，不抛出异常
                    pass
        
        return intent
    
    async def _get_latest_version(self) -> str:
        """获取最新版本名称（需要与业务层集成）"""
        # 这里需要与 VersionController 集成
        # 暂时返回空字符串，实际使用时需要实现
        return ""
    
    async def _get_previous_version(self) -> str:
        """获取上一个版本名称（需要与业务层集成）"""
        # 这里需要与 VersionController 集成
        # 暂时返回空字符串，实际使用时需要实现
        return ""