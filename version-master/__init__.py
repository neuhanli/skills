"""
Version-Master - Intelligent Version Management Assistant

AI-powered version management skill with layered architecture and event-driven design.
Provides professional file version control capabilities for AI assistant environments.
"""

__version__ = "1.0.0"
__author__ = "Han Li"

from .data.models import Intent, IntentType, VersionMetadata, Change, ChangeType
from .nlp.intent_parser import IntentParser
from .business.version_controller import VersionController
from .business.orchestration_service import OrchestrationService
from .data.snapshot_repository import SnapshotRepository
from .data.metadata_repository import VersionMetadataRepository
from .infrastructure.file_system import FileSystem
from .infrastructure.storage_optimizer import StorageOptimizer
from .infrastructure.hook_system import HookSystem
from .infrastructure.security import Security
from .infrastructure.logger import Logger
from .infrastructure.encryption import EncryptionManager, SecureSnapshotManager

__all__ = [
    # Data models
    'Intent', 'IntentType', 'VersionMetadata', 'Change', 'ChangeType',
    
    # NLP layer
    'IntentParser',
    
    # Business logic layer
    'VersionController', 'OrchestrationService',
    
    # Data access layer
    'SnapshotRepository', 'VersionMetadataRepository',
    
    # Infrastructure layer
    'FileSystem', 'StorageOptimizer', 'HookSystem', 'Security', 'Logger',
    'EncryptionManager', 'SecureSnapshotManager'
]