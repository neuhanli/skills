"""
Data Model Definitions

Define core data models for Version-Master skill, including intents, version metadata, changes, etc.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


class IntentType(Enum):
    """Intent type enumeration"""
    SAVE = "save"
    RESTORE = "restore"
    LIST = "list"
    DIFF = "diff"
    CLEAN = "clean"


class ChangeType(Enum):
    """Change type enumeration"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class Change:
    """File change information"""
    file_path: str
    change_type: ChangeType
    size_bytes: int
    timestamp: str
    content_hash: Optional[str] = None


@dataclass
class Intent:
    """Structured intent object"""
    type: IntentType
    params: Dict[str, Any]
    confidence: float
    original_input: str


@dataclass
class VersionMetadata:
    """Version metadata"""
    name: str
    timestamp: str
    trigger: str  # manual | auto
    summary: str
    snapshot_path: str
    user_comment: str
    changes: List[Change]
    size_bytes: Optional[int] = None


@dataclass
class SaveResult:
    """Save operation result"""
    success: bool
    version_name: str
    timestamp: str
    summary: str
    error_message: Optional[str] = None


@dataclass
class RestoreResult:
    """Restore operation result"""
    success: bool
    version_name: str
    timestamp: str
    error_message: Optional[str] = None


@dataclass
class ListVersionsResult:
    """List versions result"""
    versions: List[VersionMetadata]
    total_count: int
    total_size_bytes: int


@dataclass
class DiffResult:
    """Version comparison result"""
    compared_with: str
    changes: List[Change]
    summary: Optional[str] = None


@dataclass
class CleanResult:
    """Clean operation result"""
    deleted_versions: List[str]
    freed_space_bytes: int


# Exception class definitions
class VersionMasterError(Exception):
    """Version-Master base exception"""
    pass


class InvalidIntentError(VersionMasterError):
    """Invalid intent exception"""
    pass


class MissingParameterError(VersionMasterError):
    """Missing required parameter exception"""
    pass


class VersionNotFoundError(VersionMasterError):
    """Version not found exception"""
    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class NoChangesError(VersionMasterError):
    """No changes exception"""
    pass


class SaveFailedError(VersionMasterError):
    """Save failed exception"""
    pass


class RestoreFailedError(VersionMasterError):
    """Restore failed exception"""
    pass


class UncommittedChangesError(VersionMasterError):
    """Uncommitted changes exception"""
    def __init__(self, message: str, changes: List[Change] = None):
        super().__init__(message)
        self.changes = changes or []


class ConfirmationRequiredError(VersionMasterError):
    """Confirmation required exception"""
    pass


class StorageLimitExceededError(VersionMasterError):
    """Storage limit exceeded exception"""
    pass