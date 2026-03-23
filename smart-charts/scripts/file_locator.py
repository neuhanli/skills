#!/usr/bin/env python3
"""
文件定位工具
支持自然语言指令理解的文件定位功能

**配置要求**:
- input_dir: 输入目录路径 (必需参数)

**安全说明**:
- 仅扫描指定输入目录，不访问系统文件
- 需要用户明确提供输入目录路径
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import glob
import sys

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    'excel': ['.xlsx', '.xls'],
    'csv': ['.csv', '.tsv'],
    'json': ['.json'],
    'word': ['.docx'],
    'sqlite': ['.db', '.sqlite', '.sqlite3'],
    'text': ['.txt']
}

# 所有支持的文件扩展名
ALL_SUPPORTED_EXTENSIONS = []
for ext_list in SUPPORTED_EXTENSIONS.values():
    ALL_SUPPORTED_EXTENSIONS.extend(ext_list)


class FileLocator:
    """文件定位器类，支持自然语言指令理解"""
    
    def __init__(self, input_dir: str = "./input"):
        # 路径规范化
        input_dir = os.path.abspath(os.path.expanduser(input_dir))
        
        # 路径安全检查
        if not self._is_safe_path(input_dir):
            raise ValueError(f"不安全的工作目录: {input_dir}")
        
        self.input_dir = Path(input_dir)
        
        # 检查输入目录是否存在
        if not self.input_dir.exists():
            try:
                self.input_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ 创建输入目录: {self.input_dir}")
            except PermissionError:
                print(f"⚠️ 无法创建输入目录 {self.input_dir}，权限不足")
                # 使用当前目录作为备用
                self.input_dir = Path.cwd()
                print(f"📁 使用当前目录作为输入目录: {self.input_dir}")
        
        print(f"📂 输入目录: {self.input_dir}")
        
        # 支持的文件扩展名
        self.supported_extensions = {
            '.csv', '.xlsx', '.xls', '.json', '.txt', 
            '.sqlite', '.db', '.docx'
        }
        
        # 设置搜索深度限制
        self.max_search_depth = 5
        self.max_files_per_search = 1000
    
    def _is_safe_path(self, path: str) -> bool:
        """验证路径是否安全"""
        # 禁止访问系统关键目录
        forbidden_paths = [
            '/', '/etc', '/var', '/usr', '/bin', '/sbin',
            '/System', '/Library', '/Applications',
            'C:\\', 'C:\\Windows', 'C:\\Program Files'
        ]
        
        abs_path = os.path.abspath(path)
        
        # 检查是否在禁止目录中
        for forbidden in forbidden_paths:
            if abs_path.startswith(forbidden):
                return False
        
        # 检查路径深度
        path_depth = len(abs_path.split(os.sep))
        if path_depth > 20:  # 限制路径深度
            return False
        
        return True
    
    def _is_file_safe(self, file_path: Path) -> bool:
        """验证文件是否安全"""
        try:
            # 检查文件是否在输入目录内
            if not file_path.is_relative_to(self.input_dir):
                return False
                
            # 检查文件大小 (限制大文件)
            if file_path.stat().st_size > 100 * 1024 * 1024:  # 100MB限制
                return False
                
            # 检查文件扩展名
            if file_path.suffix.lower() not in self.supported_extensions:
                return False
                
            return True
        except Exception:
            return False
    
    def _sanitize_input(self, text: str) -> str:
        """清理用户输入"""
        # 移除潜在的路径遍历字符
        dangerous_chars = ['../', '..\\', '/etc/', '/var/', 'C:\\']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def locate_files(self, description: str) -> List[Path]:
        """安全的文件定位方法"""
        # 输入验证
        if not description or len(description.strip()) == 0:
            raise ValueError("描述不能为空")
        
        # 清理输入，防止路径遍历攻击
        description = self._sanitize_input(description)
        
        if len(description) > 500:  # 限制输入长度
            raise ValueError("描述过长")
        
        # 检查输入目录是否存在且可读
        if not self.input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {self.input_dir}")
        
        if not os.access(self.input_dir, os.R_OK):
            raise PermissionError(f"输入目录不可读: {self.input_dir}")
        
        # 解析描述
        parsed = self._parse_description(description)
        
        # 获取所有支持的文件
        all_files = self._get_all_supported_files()
        
        # 过滤文件
        filtered_files = self._filter_files(all_files, parsed)
        
        # 排序和选择
        selected_files = self._select_files(filtered_files, parsed)
        
        return selected_files
    
    def _parse_description(self, description: str) -> Dict[str, Any]:
        """解析自然语言描述"""
        parsed = {
            'keywords': [],
            'file_type': None,
            'time_filter': None,
            'pattern': None,
            'count': 1
        }
        
        # 转换为小写便于匹配
        desc_lower = description.lower()
        
        # 提取关键词
        keywords = re.findall(r'[\u4e00-\u9fff\w]+', description)
        parsed['keywords'] = keywords
        
        # 检测文件类型
        file_type_patterns = {
            'excel': ['excel', 'xlsx', 'xls'],
            'csv': ['csv'],
            'json': ['json'],
            'txt': ['txt', '文本'],
            'sqlite': ['sqlite', 'db', '数据库'],
            'word': ['word', 'docx']
        }
        
        for file_type, patterns in file_type_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                parsed['file_type'] = file_type
                break
        
        # 检测时间过滤
        time_patterns = {
            'today': ['今天', '今日'],
            'yesterday': ['昨天', '昨日'],
            'this_week': ['本周', '这周'],
            'this_month': ['本月', '这个月'],
            'latest': ['最新', '最近', 'newest', 'latest']
        }
        
        for time_key, patterns in time_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                parsed['time_filter'] = time_key
                break
        
        # 检测数量
        count_match = re.search(r'(\d+)(?:个|个文件|个数据)', description)
        if count_match:
            parsed['count'] = int(count_match.group(1))
        
        # 检测通配符模式
        if '*' in description or '?' in description:
            parsed['pattern'] = description
        
        return parsed
    
    def _get_all_supported_files(self) -> List[Path]:
        """安全的文件搜索方法"""
        files = []
        search_count = 0
        
        # 限制搜索深度
        for depth in range(self.max_search_depth + 1):
            if search_count >= self.max_files_per_search:
                break
                
            for ext in self.supported_extensions:
                # 使用深度限制的搜索模式
                if depth == 0:
                    pattern = f"*{ext}"
                else:
                    pattern = f"*/{'*/' * (depth-1)}*{ext}"
                
                try:
                    matching_files = list(self.input_dir.glob(pattern))
                    for file_path in matching_files:
                        # 验证文件是否在安全范围内
                        if self._is_file_safe(file_path):
                            files.append(file_path)
                            search_count += 1
                            
                        if search_count >= self.max_files_per_search:
                            break
                except Exception as e:
                    print(f"⚠️ 搜索文件时出错: {e}")
                    continue
                    
                if search_count >= self.max_files_per_search:
                    break
                    
        return files[:self.max_files_per_search]  # 限制返回数量
    
    def _filter_files(self, files: List[Path], parsed: Dict[str, Any]) -> List[Path]:
        """根据解析结果过滤文件"""
        filtered = files.copy()
        
        # 按文件类型过滤
        if parsed['file_type']:
            ext_mapping = {
                'excel': ['.xlsx', '.xls'],
                'csv': ['.csv'],
                'json': ['.json'],
                'txt': ['.txt'],
                'sqlite': ['.sqlite', '.db'],
                'word': ['.docx']
            }
            
            target_exts = ext_mapping.get(parsed['file_type'], [])
            filtered = [f for f in filtered if f.suffix.lower() in target_exts]
        
        # 按关键词过滤
        if parsed['keywords']:
            keyword_filtered = []
            for file_path in filtered:
                filename_lower = file_path.name.lower()
                # 检查文件名是否包含任何关键词
                if any(keyword.lower() in filename_lower for keyword in parsed['keywords']):
                    keyword_filtered.append(file_path)
            filtered = keyword_filtered
        
        # 按时间过滤
        if parsed['time_filter']:
            now = datetime.now()
            time_cutoff = {
                'today': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'yesterday': now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
                'this_week': now - timedelta(days=now.weekday()),
                'this_month': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            }
            
            cutoff = time_cutoff.get(parsed['time_filter'])
            if cutoff:
                filtered = [f for f in filtered if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff]
        
        # 按通配符模式过滤
        if parsed['pattern']:
            try:
                pattern_files = []
                for file_path in filtered:
                    if self._match_pattern(file_path.name, parsed['pattern']):
                        pattern_files.append(file_path)
                filtered = pattern_files
            except:
                pass  # 如果模式匹配失败，忽略模式过滤
        
        return filtered
    
    def _select_files(self, files: List[Path], parsed: Dict[str, Any]) -> List[Path]:
        """选择最终的文件"""
        if not files:
            return []
        
        # 按修改时间排序（最新的在前）
        files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        
        # 如果是"最新"过滤，取第一个
        if parsed['time_filter'] == 'latest':
            return files_sorted[:1]
        
        # 根据数量限制返回文件
        return files_sorted[:parsed['count']]
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """匹配通配符模式"""
        # 将通配符模式转换为正则表达式
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return re.match(regex_pattern, filename, re.IGNORECASE) is not None
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        stat = file_path.stat()
        
        return {
            'name': file_path.name,
            'path': str(file_path),
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'extension': file_path.suffix.lower(),
            'relative_path': str(file_path.relative_to(self.input_dir))
        }
    
    def list_available_files(self) -> List[Dict[str, Any]]:
        """列出所有可用文件的信息"""
        files = self._get_all_supported_files()
        file_info_list = []
        
        for file_path in files:
            file_info_list.append(self.get_file_info(file_path))
        
        # 按修改时间排序
        file_info_list.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return file_info_list


def main():
    """测试函数"""
    locator = FileLocator()
    
    # 测试自然语言描述
    test_descriptions = [
        "最新的销售数据Excel文件",
        "包含用户信息的CSV文件",
        "昨天更新的数据库文件",
        "项目配置文件JSON",
        "*销售*.xlsx"
    ]
    
    for desc in test_descriptions:
        print(f"\n搜索描述: {desc}")
        try:
            files = locator.locate_files(desc)
            if files:
                print(f"找到 {len(files)} 个文件:")
                for file_path in files:
                    file_info = locator.get_file_info(file_path)
                    print(f"  - {file_info['name']} (修改时间: {file_info['modified_time']})")
            else:
                print("未找到匹配的文件")
        except Exception as e:
            print(f"错误: {e}")
    
    # 列出所有可用文件
    print("\n所有可用文件:")
    all_files = locator.list_available_files()
    for file_info in all_files:
        print(f"  - {file_info['name']} ({file_info['extension']}, {file_info['size']} bytes)")


if __name__ == "__main__":
    main()