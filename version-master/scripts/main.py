"""
Main Application Entry Point

Version-Master skill main application with dependency injection and orchestration.
Initializes all components and provides the main interface for skill operations.
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent  # 指向 version-master 目录
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from infrastructure.logger import Logger
from nlp.llm_client import LLMClient, AIClient
from nlp.intent_parser import IntentParser
from data.snapshot_repository import SnapshotRepository
from data.metadata_repository import VersionMetadataRepository
from infrastructure.file_system import FileSystem
from infrastructure.storage_optimizer import StorageOptimizer
from infrastructure.hook_system import HookSystem
from infrastructure.security import Security
from business.version_controller import VersionController
from business.orchestration_service import OrchestrationService


class VersionMasterApp:
    """Version-Master 应用主类"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigManager(config_path)
        self.logger = Logger.create_default_logger(self.config.get('storage.path'))
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有组件"""
        storage_path = self.config.get('storage.path')
        
        # 基础设施层
        self.file_system = FileSystem(storage_path)
        self.security = Security(self.logger)
        
        # 数据访问层
        self.snapshot_repo = SnapshotRepository(storage_path, self.logger)
        self.metadata_repo = VersionMetadataRepository(storage_path, self.logger)
        
        # 存储优化器
        self.storage_optimizer = StorageOptimizer(
            self.snapshot_repo, self.metadata_repo, self.file_system, self.logger
        )
        
        # 钩子系统
        self.hook_system = HookSystem(self.logger)
        if self.config.get('hooks.auto_register_default'):
            self.hook_system.register_default_hooks()
        
        # AI Assistant Integration
        self.ai_client = AIClient()
        
        # NLP 层
        self.intent_parser = IntentParser(self.ai_client)
        
        # 业务逻辑层
        self.version_controller = VersionController(
            self.snapshot_repo,
            self.metadata_repo,
            self.ai_client,
            self.storage_optimizer,
            self.logger
        )
        
        # 编排服务
        self.orchestration_service = OrchestrationService(
            self.intent_parser,
            self.version_controller,
            self.logger
        )
        
        self.logger.info("Version-Master 组件初始化完成")
    
    async def execute_command(self, user_input: str) -> dict:
        """
        执行用户命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            dict: 执行结果
        """
        try:
            result = await self.orchestration_service.execute_intent(user_input)
            return result
        except Exception as e:
            self.logger.error(f"执行命令失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"命令执行失败: {str(e)}"
            }
    
    async def test_basic_functionality(self):
        """测试基本功能"""
        self.logger.info("开始测试基本功能")
        
        test_cases = [
            "保存当前版本",
            "列出所有版本",
            "对比最新版本",
            "清理旧版本"
        ]
        
        for test_case in test_cases:
            self.logger.info(f"测试: {test_case}")
            result = await self.execute_command(test_case)
            
            if result.get('success'):
                self.logger.info(f"测试通过: {test_case}")
            else:
                self.logger.warning(f"测试失败: {test_case} - {result.get('error')}")
        
        self.logger.info("基本功能测试完成")
    
    def get_status(self) -> dict:
        """获取应用状态"""
        storage_stats = self.storage_optimizer.get_storage_statistics()
        hook_stats = self.hook_system.get_registered_hooks()
        
        return {
            'storage': storage_stats,
            'hooks': hook_stats,
            'config_valid': self.config.validate(),
            'llm_configured': bool(self.config.get('llm.api_key'))
        }
    
    async def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理资源")
        
        # 清理钩子系统
        await self.hook_system.cleanup()
        
        # 清理安全组件
        self.security.cleanup_locks()
        
        # 清理日志系统
        self.logger.cleanup()
        
        self.logger.info("资源清理完成")


async def main():
    """主函数"""
    print("=== Version-Master 智能版本管理助手 ===")
    print("正在初始化...")
    
    # 创建应用实例
    app = VersionMasterApp()
    
    try:
        # 显示状态信息
        status = app.get_status()
        print(f"存储状态: {status['storage']}")
        print(f"钩子系统: {status['hooks']}")
        print(f"配置有效: {status['config_valid']}")
        print(f"LLM 配置: {status['llm_configured']}")
        
        # 测试基本功能
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            print("\n开始功能测试...")
            await app.test_basic_functionality()
        
        # 交互模式
        if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
            print("\n进入交互模式 (输入 'quit' 退出)")
            
            while True:
                try:
                    user_input = input("\nVersion-Master> ").strip()
                    
                    if user_input.lower() in ('quit', 'exit', 'q'):
                        break
                    
                    if not user_input:
                        continue
                    
                    result = await app.execute_command(user_input)
                    
                    if result.get('success'):
                        print(f"✓ {result.get('message')}")
                        if 'result' in result:
                            print(f"结果: {result['result']}")
                    else:
                        print(f"✗ {result.get('message')}")
                        
                except KeyboardInterrupt:
                    print("\n\n收到中断信号，正在退出...")
                    break
                except Exception as e:
                    print(f"错误: {str(e)}")
        
        # 单次命令执行
        elif len(sys.argv) > 1 and sys.argv[1] != '--test':
            user_input = ' '.join(sys.argv[1:])
            result = await app.execute_command(user_input)
            
            if result.get('success'):
                print(f"✓ {result.get('message')}")
                if 'result' in result:
                    print(f"结果: {result['result']}")
            else:
                print(f"✗ {result.get('message')}")
                sys.exit(1)
        
        else:
            print("\n使用说明:")
            print("  python -m versionmaster.scripts.main --test        # 运行测试")
            print("  python -m versionmaster.scripts.main --interactive # 交互模式")
            print("  python -m versionmaster.scripts.main <命令>        # 执行单条命令")
            print("\n示例命令:")
            print("  保存当前版本")
            print("  列出所有版本") 
            print("  对比最新版本")
            print("  清理旧版本")
    
    finally:
        # 清理资源
        await app.cleanup()
        print("\nVersion-Master 已退出")


if __name__ == "__main__":
    asyncio.run(main())