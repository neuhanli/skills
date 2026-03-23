#!/usr/bin/env python3
"""
Version-Master 简化版 CLI
提供基本的版本保存、列表、恢复功能
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

class SimpleVersionMaster:
    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path)
        self.versions_dir = self.workspace / '.versions'
        self.versions_dir.mkdir(exist_ok=True)
    
    def save(self, name=None):
        """保存当前版本"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = name or f"version_{timestamp}"
        version_path = self.versions_dir / f"{name}_{timestamp}"
        
        # 复制当前目录（排除 .versions）
        shutil.copytree(self.workspace, version_path,
                       ignore=shutil.ignore_patterns('.versions', '__pycache__', '.git'))
        
        # 保存元数据
        metadata = {
            'name': name,
            'timestamp': timestamp,
            'path': str(version_path)
        }
        with open(f"{version_path}.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return f"版本 '{name}' 已保存"
    
    def list(self):
        """列出所有版本"""
        versions = []
        for meta_file in self.versions_dir.glob('*.json'):
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                versions.append(metadata)
        
        # 按时间排序
        versions.sort(key=lambda x: x['timestamp'], reverse=True)
        return versions
    
    def restore(self, name):
        """恢复到指定版本"""
        # 查找匹配的版本
        target_version = None
        for meta_file in self.versions_dir.glob('*.json'):
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if metadata['name'] == name or name in metadata['name']:
                    target_version = metadata
                    break
        
        if not target_version:
            return f"未找到版本: {name}"
        
        # 备份当前状态
        backup_name = f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.save(backup_name)
        
        # 恢复目标版本
        version_path = Path(target_version['path'])
        
        # 删除当前文件（排除 .versions）
        for item in self.workspace.iterdir():
            if item.name != '.versions' and item.is_file():
                item.unlink()
            elif item.name != '.versions' and item.is_dir():
                shutil.rmtree(item)
        
        # 复制版本文件
        for item in version_path.iterdir():
            if item.is_file():
                shutil.copy2(item, self.workspace / item.name)
            elif item.is_dir():
                shutil.copytree(item, self.workspace / item.name)
        
        return f"已恢复到版本: {target_version['name']}"
    
    def clean(self, keep_count=10):
        """清理旧版本，保留指定数量的最新版本"""
        versions = self.list()
        if len(versions) <= keep_count:
            return f"当前只有 {len(versions)} 个版本，无需清理"
        
        # 保留最新的 keep_count 个版本
        versions_to_keep = versions[:keep_count]
        versions_to_delete = versions[keep_count:]
        
        deleted_count = 0
        for version in versions_to_delete:
            version_path = Path(version['path'])
            meta_file = Path(f"{version_path}.json")
            
            if version_path.exists():
                shutil.rmtree(version_path)
            if meta_file.exists():
                meta_file.unlink()
            
            deleted_count += 1
        
        return f"已清理 {deleted_count} 个旧版本，保留 {keep_count} 个最新版本"

def main():
    if len(sys.argv) < 2:
        print("用法: python simple_cli.py <命令> [参数]")
        print("命令: save, list, restore, clean")
        return
    
    command = sys.argv[1]
    workspace_path = os.getcwd()  # 使用当前工作目录
    
    vm = SimpleVersionMaster(workspace_path)
    
    if command == "save":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        result = vm.save(name)
        print(result)
    
    elif command == "list":
        versions = vm.list()
        if not versions:
            print("暂无版本记录")
        else:
            print("版本列表:")
            for i, version in enumerate(versions, 1):
                print(f"{i}. {version['name']} - {version['timestamp']}")
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("请指定要恢复的版本名称")
            return
        name = sys.argv[2]
        result = vm.restore(name)
        print(result)
    
    elif command == "clean":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = vm.clean(keep_count)
        print(result)
    
    else:
        print(f"未知命令: {command}")

if __name__ == '__main__':
    main()