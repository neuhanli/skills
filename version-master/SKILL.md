---
name: "version-master"
description: "Intelligent version management assistant for file snapshot saving, restoration, comparison, and cleanup. Activate immediately when users need version control, file backup, compare differences, or save/restore project states. Supports Chinese commands like '保存版本', '查看版本', '恢复版本', '对比版本' and English commands like 'save version', 'view versions', 'restore version', 'compare versions'."
---

# Version-Master - Intelligent Version Management Assistant

Version-Master is an AI-powered version management skill designed for AI assistant environments. It provides professional file version control capabilities using a layered architecture with event-driven design.

## 🚀 Quick Usage Instructions

Invoke Version-Master skill when users need the following operations:

| User Commands | Invocation Method | Description |
|---------------|------------------|-------------|
| "保存版本", "备份当前状态", "Save version", "Backup current state" | `version-master save [name]` | Save current project state |
| "查看版本", "列出所有版本", "View versions", "List all versions" | `version-master list` | Display all historical versions |
| "恢复版本", "回到之前版本", "Restore version", "Go back to previous version" | `version-master restore <name>` | Restore to specified version |
| "对比版本", "查看差异", "Compare versions", "View differences" | `version-master diff <version1> <version2>` | Compare differences between two versions |
| "清理版本", "删除旧版本", "Clean versions", "Delete old versions" | `version-master clean` | Clean up expired versions |

### Chinese Command Examples
- "帮我保存一下当前版本" → Automatically activate version-master save
- "看看我有哪些历史版本" → Automatically activate version-master list  
- "我想回到昨天的版本" → Automatically activate version-master restore
- "对比一下这两个版本有什么不同" → Automatically activate version-master diff
- "清理一些旧的备份版本" → Automatically activate version-master clean

### English Command Examples
- "Save the current version for me" → Automatically activate version-master save
- "Show me what historical versions I have" → Automatically activate version-master list
- "I want to go back to yesterday's version" → Automatically activate version-master restore
- "Compare the differences between these two versions" → Automatically activate version-master diff
- "Clean up some old backup versions" → Automatically activate version-master clean

## Core Capabilities

### 1. Version Saving (Save)
- **Smart Naming**: AI-assisted meaningful version name generation
- **Atomic Operations**: Ensures snapshot creation is either fully successful or fully failed
- **Incremental Storage**: Only stores changed files to optimize storage

### 2. Version Restoration (Restore)
- **Natural Language References**: Supports "latest version", "previous version" references
- **Fuzzy Matching**: Intelligent version name matching with partial matching support
- **Integrity Verification**: Validates snapshot integrity before restoration

### 3. Version Comparison (Diff)
- **Intelligent Summaries**: AI-generated human-readable change summaries
- **Multi-dimensional Comparison**: Supports file content, size, modification time comparisons
- **Visualization**: Clear change visualization interface

### 4. Version Listing (List)
- **Smart Sorting**: Multiple sorting dimensions including time and importance
- **Search Filtering**: Keyword search and conditional filtering support
- **Space Statistics**: Shows storage usage statistics per version

### 5. Version Cleanup (Clean)
- **Smart Strategies**: Automatic cleanup recommendations based on usage frequency
- **Safe Deletion**: Preview and confirmation mechanisms to prevent accidental deletion
- **Space Optimization**: Automatic cleanup of expired versions to free storage

## Trigger Scenarios

Invoke Version-Master skill when users express these needs:

### High-Frequency Triggers
- "Save the current project state"
- "I want to restore to yesterday's version"
- "Compare the differences between these two versions"
- "View all historical versions"
- "Clean up some old backup versions"

### Medium-Frequency Triggers
- "Backup before modifying the project"
- "Show me what files have been changed recently"
- "Delete some unimportant historical versions"
- "Give this version a meaningful name"

### Low-Frequency Triggers
- "How to enable auto-save feature"
- "Storage usage statistics for version management"
- "How to configure version retention policies"

## Usage Examples

### Basic Usage
```
User: Save current project state
Version-Master: Created snapshot "Feature Development - Basic Framework - 2026-03-22"

User: Restore to previous version
Version-Master: Restored to "Feature Development - User Login Module - 2026-03-21"

User: Compare latest two versions
Version-Master: Detected 15 file changes, mainly involving user authentication module optimization...
```

### Advanced Usage
```
User: Save and name it "User Permission System Refactor"
Version-Master: Snapshot "User Permission System Refactor" created successfully, containing 42 file changes

User: List versions containing "login" keyword
Version-Master: Found 3 related versions:
- User Login Module Optimization (2026-03-21)
- Login Security Enhancement (2026-03-20)
- Multi-factor Login Implementation (2026-03-19)

User: Clean versions older than 30 days but keep important milestones
Version-Master: Recommend keeping 5 important versions, cleaning 12 old versions, freeing 2.3GB space
```

## Technical Architecture

Version-Master uses a four-layer architecture:

### 1. Presentation Layer
- **SKILL.md**: Skill description and trigger rules
- **Command Mapping**: Natural language to structured command mapping
- **Usage Examples**: Rich usage scenario examples

### 2. Natural Language Understanding Layer
- **Intent Parser**: Intent recognition and parameter extraction
- **AI Integration**: AI-powered intelligent generation
- **Relative Reference Handling**: Natural time references support

### 3. Business Logic Layer
- **VersionController**: Core business use case implementation
- **Orchestration Service**: Operation flow orchestration and transaction management
- **Asynchronous Task Scheduling**: Support for long-running operations

### 4. Data Access Layer
- **SnapshotRepository**: Snapshot data persistence
- **VersionMetadataRepository**: Metadata management
- **Storage Optimization**: Automatic space management and cleanup strategies

## Best Practices

### 1. Naming Conventions
- Use meaningful version names for easy future reference
- Include key information like functional modules and dates
- Avoid overly simple names like "v1", "backup"

### 2. Saving Strategies
- Always save snapshots before important feature development
- Save regularly for milestone achievements
- Create milestone versions before major refactoring

### 3. Restoration Strategies
- Confirm target version correctness before restoration
- Backup current state before important operations
- Use comparison features to understand change content

### 4. Cleanup Strategies
- Regularly clean expired versions to free space
- Keep important milestone versions
- Use intelligent recommendation strategies for cleanup

## Security Features

### Data Security
- **Atomic Operations**: All operations either fully succeed or fully fail
- **Integrity Verification**: Integrity checks during snapshot creation and restoration
- **Sensitive File Filtering**: Automatic filtering of configuration files, keys, etc.

### Operation Security
- **Confirmation Mechanisms**: Confirmation prompts before important operations
- **Operation Logging**: Records all version management operations
- **Rollback Capability**: Supports operation rollback and error recovery

## Performance Optimization

### Storage Optimization
- **Incremental Storage**: Only stores changed files, reducing space usage
- **Compression Algorithms**: Efficient compression algorithms for storage optimization
- **Intelligent Cleanup**: Automatic storage optimization based on usage frequency

### Response Optimization
- **Asynchronous Operations**: Asynchronous execution for long operations
- **Caching Mechanism**: Caching for frequently accessed data
- **Parallel Processing**: Support for multi-task parallel processing

## Extension Capabilities

Version-Master supports the following extension features:

### Hook System
- **before_compaction**: Automatic save before context compression
- **before_prompt_build**: Version check before prompt building
- **Custom Hooks**: Support for user-defined event responses

### Plugin System
- **Storage Backends**: Support for multiple storage backends (local, cloud)
- **Comparison Engines**: Pluggable comparison algorithms
- **Notification Mechanisms**: Support for multiple notification methods

## Troubleshooting

### Common Issues
1. **Snapshot Creation Failed**: Check file permissions and disk space
2. **Version Restoration Conflict**: Confirm target files aren't used by other processes
3. **Insufficient Storage Space**: Use cleanup feature to free space

### Debug Information
- Enable verbose logging mode for operation details
- Check operation logs for specific error causes
- Use validation features to check snapshot integrity

---

**Version-Master** - Making version management simple and intelligent