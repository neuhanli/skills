"""
Configuration Manager

Manages Version-Master skill configuration, including loading, saving, and validation.
Supports environment variables, configuration files, and default values.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    配置管理器
    
    管理 Version-Master 技能的配置，支持环境变量和配置文件。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Dict[str, Any] = self._load_default_config()
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 优先使用环境变量指定的路径
        env_path = os.getenv('VERSIONMASTER_CONFIG_PATH')
        if env_path:
            return env_path
        
        # 默认路径
        return str(Path.home() / '.trae' / 'versionmaster' / 'config.json')
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            'storage': {
                'path': str(Path.home() / '.trae' / 'versionmaster' / 'data'),
                'max_versions': 50,
                'max_age_days': 30,
                'min_free_space_gb': 1
            },
            'ai_assistant': {
                'model': 'built-in',
                'capabilities': ['text_generation', 'intent_parsing']
            },
            'logging': {
                'level': 'INFO',
                'file': str(Path.home() / '.trae' / 'versionmaster' / 'logs' / 'versionmaster.log'),
                'max_size_mb': 10
            },
            'security': {
                'sensitive_patterns': [
                    '*.env', '.env*', 'config*.py', 'settings*.py',
                    '*.key', '*.pem', '*.crt', 'id_rsa', 'id_dsa',
                    '*.db', '*.sqlite', '*.mdb',
                    '*.log', 'logs/',
                    '*.tmp', 'temp/', 'tmp/',
                    '.git/', '.svn/',
                    '.DS_Store', 'Thumbs.db'
                ]
            },
            'hooks': {
                'enabled': True,
                'auto_register_default': True
            }
        }
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 深度合并配置
                self._merge_config(self._config, user_config)
                
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """深度合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        env_mappings = {
            'VERSIONMASTER_STORAGE_PATH': ['storage', 'path'],
            'VERSIONMASTER_MAX_VERSIONS': ['storage', 'max_versions'],
            'VERSIONMASTER_MAX_AGE_DAYS': ['storage', 'max_age_days'],
            'VERSIONMASTER_MIN_FREE_SPACE_GB': ['storage', 'min_free_space_gb'],
            'VERSIONMASTER_AI_MODEL': ['ai_assistant', 'model'],
            'VERSIONMASTER_LOG_LEVEL': ['logging', 'level'],
            'VERSIONMASTER_LOG_FILE': ['logging', 'file']
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_config(self._config, config_path, env_value)
    
    def _set_nested_config(self, config: Dict[str, Any], path: list, value: Any):
        """设置嵌套配置值"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 类型转换
        last_key = path[-1]
        if isinstance(value, str):
            # 尝试转换为适当类型
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
        
        current[last_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分隔符 (如 'storage.path')
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        current = self._config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点分隔符
            value: 配置值
        """
        keys = key.split('.')
        current = self._config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        config_path = Path(self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return self.get('storage', {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取 LLM 配置"""
        return self.get('llm', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.get('security', {})
    
    def get_hooks_config(self) -> Dict[str, Any]:
        """获取钩子配置"""
        return self.get('hooks', {})
    
    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 检查存储路径
            storage_path = self.get('storage.path')
            if not storage_path:
                return False
            
            # 检查 AI 助手配置（统一使用 ai_assistant.model）
            ai_model = self.get('ai_assistant.model')
            if not ai_model:
                return False
            
            # 检查数值配置的合理性
            max_versions = self.get('storage.max_versions')
            if max_versions <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()
    
    @classmethod
    def create_with_defaults(cls, storage_path: str) -> 'ConfigManager':
        """
        使用默认值创建配置管理器
        
        Args:
            storage_path: 存储路径
            
        Returns:
            ConfigManager: 配置管理器实例
        """
        config = cls()
        config.set('storage.path', storage_path)
        return config