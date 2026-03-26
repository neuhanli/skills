"""
智能模板管理器
支持PDF、Word、Markdown等多种格式的模板管理
"""

import os
import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re

from .format_extractor import FormatExtractor
from .exceptions import TemplateError, FileError, ErrorCode


class TemplateManager:
    """智能模板管理器"""
    
    def __init__(self, templates_dir: str = "./templates"):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = Path(templates_dir).resolve()
        self.format_extractor = FormatExtractor()
        
        # 确保模板目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 模板索引文件
        self.index_file = self.templates_dir / "_template_index.json"
        self._load_index()
    
    def _load_index(self):
        """加载模板索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except json.JSONDecodeError:
                self.index = {}
        else:
            self.index = {}
    
    def _save_index(self):
        """保存模板索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _generate_template_id(self) -> str:
        """生成唯一的模板ID"""
        return f"tmpl_{uuid.uuid4().hex[:8]}"
    
    def _scan_existing_templates(self):
        """扫描现有的模板目录，更新索引"""
        if not self.templates_dir.exists():
            return
        
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir() and not template_dir.name.startswith('_'):
                meta_file = template_dir / "meta.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta_data = json.load(f)
                        template_id = meta_data.get('id', template_dir.name)
                        self.index[template_id] = {
                            'id': template_id,
                            'name': meta_data.get('name', template_dir.name),
                            'description': meta_data.get('description', ''),
                            'scenarios': meta_data.get('scenarios', []),
                            'format': meta_data.get('format', 'markdown'),
                            'created_time': meta_data.get('created_time', datetime.now().isoformat()),
                            'modified_time': meta_data.get('modified_time', datetime.now().isoformat()),
                            'file_count': meta_data.get('file_count', 1),
                            'variables': meta_data.get('variables', []),
                            'categories': meta_data.get('categories', []),
                            'path': str(template_dir.relative_to(self.templates_dir))
                        }
                    except Exception as e:
                        print(f"警告: 无法加载模板元数据 {meta_file}: {e}")
        
        self._save_index()
    
    def add_template(self, template_file: str, template_name: str = None, 
                    description: str = None, scenarios: List[str] = None) -> Dict:
        """
        添加新模板
        
        Args:
            template_file: 模板文件路径（支持PDF、Word、Markdown）
            template_name: 模板名称（可选，自动从文件提取）
            description: 模板描述（可选，自动生成）
            scenarios: 适用场景列表（可选，自动分类）
            
        Returns:
            Dict: 创建的模板信息
        """
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileError(f"模板文件不存在: {template_file}")
        
        # 检测文件格式
        format_type = self.format_extractor.detect_format(template_file)
        if format_type == 'unknown':
            raise TemplateError(
                f"不支持的文件格式: {template_path.suffix}",
                code=ErrorCode.TEMPLATE_FORMAT_UNSUPPORTED,
                details={'file_ext': template_path.suffix}
            )
        
        # 提取内容和结构
        content = self.format_extractor.extract_text(template_file)
        structure = self.format_extractor.extract_structure(template_file)
        metadata = self.format_extractor.extract_metadata(template_file)
        
        # 生成模板ID和目录
        template_id = self._generate_template_id()
        template_dir = self.templates_dir / template_id
        os.makedirs(template_dir, exist_ok=True)
        
        # 保存原始文件
        original_ext = template_path.suffix
        original_filename = f"original{original_ext}"
        original_path = template_dir / original_filename
        shutil.copy2(template_file, original_path)
        
        # 生成Markdown版本（方便AI处理）
        md_filename = "template.md"
        md_path = template_dir / md_filename
        
        # 根据格式生成合适的Markdown内容
        if format_type == 'pdf':
            md_content = self._pdf_to_markdown(content, structure)
        elif format_type == 'docx':
            md_content = self._docx_to_markdown(content, structure)
        else:  # markdown 或 text
            md_content = content
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # 自动提取模板名称和描述
        if not template_name:
            template_name = structure.get('title', template_path.stem)
        
        if not description:
            description = self._generate_description(content, structure, template_name)
        
        # 自动分类场景
        if not scenarios:
            categories = self.format_extractor.auto_categorize(content)
            scenarios = categories
        
        # 提取变量
        variables = structure.get('variables', [])
        
        # 创建元数据文件
        meta_data = {
            'id': template_id,
            'name': template_name,
            'description': description,
            'scenarios': scenarios,
            'variables': variables,
            'format': format_type,
            'original_file': original_filename,
            'markdown_file': md_filename,
            'categories': categories if 'categories' in locals() else [],
            'file_count': 2,  # 原始文件 + Markdown文件
            'created_time': datetime.now().isoformat(),
            'modified_time': datetime.now().isoformat(),
            'structure_summary': {
                'title': structure.get('title'),
                'headings_count': len(structure.get('headings', [])),
                'paragraphs_count': len(structure.get('paragraphs', [])),
                'word_count': structure.get('word_count', 0)
            }
        }
        
        meta_path = template_dir / "meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        self.index[template_id] = {
            'id': template_id,
            'name': template_name,
            'description': description,
            'scenarios': scenarios,
            'format': format_type,
            'created_time': meta_data['created_time'],
            'modified_time': meta_data['modified_time'],
            'file_count': meta_data['file_count'],
            'variables': variables,
            'categories': meta_data['categories'],
            'path': template_id
        }
        self._save_index()
        
        return {
            'success': True,
            'template_id': template_id,
            'template_name': template_name,
            'format': format_type,
            'description': description,
            'scenarios': scenarios,
            'variables': variables,
            'template_dir': str(template_dir),
            'file_saved': [original_filename, md_filename]
        }
    
    def list_templates(self, filter_by: Dict = None) -> List[Dict]:
        """
        列出所有模板
        
        Args:
            filter_by: 过滤条件（格式、分类、场景等）
            
        Returns:
            List[Dict]: 模板列表
        """
        # 确保索引是最新的
        self._scan_existing_templates()
        
        templates = list(self.index.values())
        
        if filter_by:
            filtered_templates = []
            for template in templates:
                match = True
                
                # 按格式过滤
                if 'format' in filter_by and template.get('format') != filter_by['format']:
                    match = False
                
                # 按分类过滤
                if 'category' in filter_by:
                    category = filter_by['category']
                    categories = template.get('categories', [])
                    if category not in categories and category != template.get('name'):
                        match = False
                
                # 按场景过滤
                if 'scenario' in filter_by:
                    scenario = filter_by['scenario'].lower()
                    scenarios = [s.lower() for s in template.get('scenarios', [])]
                    if scenario not in scenarios and scenario not in template.get('name', '').lower():
                        match = False
                
                # 按关键词搜索
                if 'search' in filter_by:
                    search_term = filter_by['search'].lower()
                    search_fields = [
                        template.get('name', '').lower(),
                        template.get('description', '').lower(),
                        ' '.join(template.get('scenarios', [])).lower(),
                        ' '.join(template.get('categories', [])).lower()
                    ]
                    if not any(search_term in field for field in search_fields):
                        match = False
                
                if match:
                    filtered_templates.append(template)
            
            return filtered_templates
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """
        获取指定模板的详细信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            Optional[Dict]: 模板详细信息
        """
        if template_id not in self.index:
            return None
        
        template_info = self.index[template_id].copy()
        template_dir = self.templates_dir / template_info['path']
        
        # 加载完整的元数据
        meta_file = template_dir / "meta.json"
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    full_meta = json.load(f)
                template_info.update(full_meta)
            except:
                pass
        
        # 添加文件列表
        template_info['files'] = []
        if template_dir.exists():
            for file in template_dir.iterdir():
                if file.is_file():
                    template_info['files'].append({
                        'name': file.name,
                        'size': file.stat().st_size,
                        'type': file.suffix[1:] if file.suffix else 'unknown'
                    })
        
        return template_info
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            bool: 是否成功删除
        """
        if template_id not in self.index:
            return False
        
        # 获取模板目录
        template_info = self.index[template_id]
        template_dir = self.templates_dir / template_info['path']
        
        # 删除目录
        if template_dir.exists():
            shutil.rmtree(template_dir)
        
        # 从索引中移除
        del self.index[template_id]
        self._save_index()
        
        return True
    
    def match_template(self, user_task: str, data_features: Dict = None) -> Optional[Dict]:
        """
        智能匹配用户任务到模板
        
        Args:
            user_task: 用户任务描述
            data_features: 数据特征（可选）
            
        Returns:
            Optional[Dict]: 最佳匹配的模板信息
            
        注意：此方法不实际执行匹配，而是生成模板元数据供大模型进行智能匹配。
        真正的匹配决策由大模型在SKILL.md的流程中完成。
        """
        # 此方法保留原有接口，但实际匹配由大模型完成
        templates = self.list_templates()
        if not templates:
            return None
        
        # 生成模板元数据汇总，供大模型阅读
        template_summary = self._generate_template_summary(templates)
        
        # 返回所有模板，让大模型做决策
        # 在实际使用中，大模型会阅读template_summary并选择最佳模板
        return templates[0] if templates else None
    
    def _generate_template_summary(self, templates: List[Dict]) -> str:
        """
        生成模板元数据汇总，供大模型阅读和匹配
        
        Args:
            templates: 模板列表
            
        Returns:
            str: 格式化后的模板元数据汇总
        """
        if not templates:
            return "当前没有可用的模板。"
        
        summary_lines = []
        summary_lines.append(f"## 模板库概览（共 {len(templates)} 个模板）")
        summary_lines.append("")
        
        for i, template in enumerate(templates, 1):
            summary_lines.append(f"### {i}. {template.get('name', '未命名模板')}")
            summary_lines.append(f"- **模板ID**: {template.get('id', '未知')}")
            summary_lines.append(f"- **格式**: {template.get('format', '未知')}")
            summary_lines.append(f"- **描述**: {template.get('description', '无描述')}")
            summary_lines.append(f"- **适用场景**: {', '.join(template.get('scenarios', []))}")
            summary_lines.append(f"- **包含变量**: {', '.join(template.get('variables', []))}")
            summary_lines.append(f"- **分类**: {', '.join(template.get('categories', []))}")
            summary_lines.append(f"- **创建时间**: {template.get('created_time', '未知')}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def get_all_templates_summary(self) -> str:
        """
        获取所有模板的元数据汇总
        
        Returns:
            str: 模板元数据汇总
        """
        templates = self.list_templates()
        return self._generate_template_summary(templates)
    
    def _pdf_to_markdown(self, content: str, structure: Dict) -> str:
        """将PDF内容转换为Markdown格式"""
        md_lines = []
        
        # 添加标题
        if structure.get('title'):
            md_lines.append(f"# {structure['title']}\n")
        
        # 添加段落
        paragraphs = structure.get('paragraphs', [])
        for para in paragraphs[:50]:  # 限制段落数量
            if len(para) > 10:  # 过滤太短的段落
                md_lines.append(f"{para}\n")
        
        # 添加变量占位符说明
        variables = structure.get('variables', [])
        if variables:
            md_lines.append("\n---\n")
            md_lines.append("## 模板变量说明\n")
            md_lines.append("以下变量可在生成报告时自动填充：\n")
            for var in variables[:10]:  # 最多显示10个变量
                md_lines.append(f"- `{{{var}}}`: 请根据数据填充")
        
        return "\n".join(md_lines)
    
    def _docx_to_markdown(self, content: str, structure: Dict) -> str:
        """将Word文档内容转换为Markdown格式"""
        md_lines = []
        
        # 处理标题结构
        headings = structure.get('headings', [])
        current_level = 0
        
        for heading in headings:
            level = heading.get('level', 1)
            content_text = heading.get('content', '')
            
            # 添加适当数量的#号
            md_lines.append(f"{'#' * level} {content_text}\n")
        
        # 添加段落
        paragraphs = structure.get('paragraphs', [])
        for para in paragraphs[:50]:
            if len(para) > 10:
                md_lines.append(f"{para}\n")
        
        # 添加变量说明
        variables = structure.get('variables', [])
        if variables:
            md_lines.append("\n---\n")
            md_lines.append("## 模板变量\n")
            for var in variables[:10]:
                md_lines.append(f"- `{{{var}}}`")
        
        return "\n".join(md_lines)
    
    def _generate_description(self, content: str, structure: Dict, template_name: str) -> str:
        """自动生成模板描述"""
        # 提取关键信息
        title = structure.get('title', '')
        word_count = structure.get('word_count', 0)
        variables = structure.get('variables', [])
        
        # 分析内容类型
        content_lower = content.lower()
        
        description_parts = []
        
        # 基本描述
        if title and title != template_name:
            description_parts.append(f"模板标题: {title}")
        
        # 内容特征
        if word_count > 0:
            if word_count < 500:
                size_desc = "简洁"
            elif word_count < 2000:
                size_desc = "详细"
            else:
                size_desc = "全面"
            description_parts.append(f"{size_desc}的{template_name}模板")
        
        # 适用场景推断
        if any(word in content_lower for word in ['销售', '业绩', '营收']):
            description_parts.append("适用于销售数据分析")
        elif any(word in content_lower for word in ['财务', '利润', '成本']):
            description_parts.append("适用于财务报表")
        elif any(word in content_lower for word in ['项目', '进度', '里程碑']):
            description_parts.append("适用于项目管理")
        
        # 变量信息
        if variables:
            var_count = len(variables)
            if var_count <= 5:
                var_desc = "少量"
            elif var_count <= 15:
                var_desc = "多个"
            else:
                var_desc = "丰富"
            description_parts.append(f"包含{var_desc}可填充变量")
        
        # 组合描述
        if description_parts:
            return "。".join(description_parts) + "。"
        else:
            return f"这是一个{template_name}模板，可用于生成相关报告。"
    
    def export_template(self, template_id: str, output_dir: str = None) -> str:
        """
        导出模板到指定目录
        
        Args:
            template_id: 模板ID
            output_dir: 输出目录（默认为当前目录）
            
        Returns:
            str: 导出路径
        """
        if template_id not in self.index:
            raise TemplateError(
                f"模板不存在: {template_id}",
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                details={'template_id': template_id}
            )
        
        template_info = self.get_template(template_id)
        if not template_info:
            raise TemplateError(
                f"无法获取模板信息: {template_id}",
                code=ErrorCode.TEMPLATE_PARSE_ERROR,
                details={'template_id': template_id}
            )
        
        # 确定输出目录
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path.cwd()
        
        # 创建导出目录
        export_path = export_dir / f"template_{template_id}"
        os.makedirs(export_path, exist_ok=True)
        
        # 获取源模板目录
        source_dir = self.templates_dir / template_info['path']
        
        # 复制文件
        for file in source_dir.iterdir():
            if file.is_file():
                shutil.copy2(file, export_path / file.name)
        
        # 创建使用说明文件
        readme_content = f"""# {template_info['name']} 模板

## 基本信息
- **模板ID**: {template_id}
- **格式**: {template_info.get('format', '未知')}
- **创建时间**: {template_info.get('created_time', '未知')}
- **最后修改**: {template_info.get('modified_time', '未知')}

## 模板描述
{template_info.get('description', '无描述')}

## 适用场景
{chr(10).join(f"- {s}" for s in template_info.get('scenarios', []))}

## 包含变量
{chr(10).join(f"- `{{{v}}}`" for v in template_info.get('variables', []))}

## 使用说明
1. 将此目录复制到 smart-charts 的 templates/ 目录下
2. 在 smart-charts 技能中，该模板会自动被识别和使用
3. 生成报告时，系统会根据任务自动匹配此模板

## 文件列表
{chr(10).join(f"- {f['name']} ({f['type']}格式)" for f in template_info.get('files', []))}
"""
        
        readme_path = export_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return str(export_path)
    
    def get_template_content(self, template_id: str, file_type: str = "markdown") -> str:
        """
        获取模板内容
        
        Args:
            template_id: 模板ID
            file_type: 文件类型 (markdown/original)
            
        Returns:
            str: 模板内容
        """
        if template_id not in self.index:
            raise TemplateError(
                f"模板不存在: {template_id}",
                code=ErrorCode.TEMPLATE_NOT_FOUND,
                details={'template_id': template_id}
            )
        
        template_info = self.get_template(template_id)
        if not template_info:
            raise TemplateError(
                f"无法获取模板信息: {template_id}",
                code=ErrorCode.TEMPLATE_PARSE_ERROR,
                details={'template_id': template_id}
            )
        
        template_dir = self.templates_dir / template_info['path']
        
        if file_type == "markdown":
            md_file = template_dir / "template.md"
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    return f.read()
        
        elif file_type == "original":
            # 查找原始文件
            for file_info in template_info.get('files', []):
                if file_info['name'].startswith('original'):
                    original_file = template_dir / file_info['name']
                    if original_file.exists():
                        # 使用格式提取器读取内容
                        return self.format_extractor.extract_text(str(original_file))
        
        raise TemplateError(
            f"无法找到指定类型的模板内容: {file_type}",
            code=ErrorCode.TEMPLATE_PARSE_ERROR,
            details={'file_type': file_type, 'template_id': template_id}
        )


# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="智能模板管理器")
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 添加模板命令
    add_parser = subparsers.add_parser('add', help='添加新模板')
    add_parser.add_argument('file', help='模板文件路径')
    add_parser.add_argument('--name', help='模板名称')
    add_parser.add_argument('--description', help='模板描述')
    
    # 列出模板命令
    list_parser = subparsers.add_parser('list', help='列出所有模板')
    list_parser.add_argument('--format', help='按格式过滤')
    list_parser.add_argument('--category', help='按分类过滤')
    list_parser.add_argument('--search', help='搜索关键词')
    
    # 获取模板命令
    get_parser = subparsers.add_parser('get', help='获取模板详情')
    get_parser.add_argument('id', help='模板ID')
    
    # 删除模板命令
    delete_parser = subparsers.add_parser('delete', help='删除模板')
    delete_parser.add_argument('id', help='模板ID')
    
    # 匹配模板命令
    match_parser = subparsers.add_parser('match', help='匹配模板')
    match_parser.add_argument('task', help='用户任务描述')
    
    # 导出模板命令
    export_parser = subparsers.add_parser('export', help='导出模板')
    export_parser.add_argument('id', help='模板ID')
    export_parser.add_argument('--output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建管理器实例
    manager = TemplateManager()
    
    try:
        if args.command == 'add':
            result = manager.add_template(
                args.file,
                template_name=args.name,
                description=args.description
            )
            print(f"✅ 模板添加成功:")
            print(f"   ID: {result['template_id']}")
            print(f"   名称: {result['template_name']}")
            print(f"   格式: {result['format']}")
            print(f"   描述: {result['description']}")
            print(f"   场景: {', '.join(result['scenarios'])}")
            print(f"   变量: {', '.join(result['variables'][:5])}..." if result['variables'] else "   变量: 无")
        
        elif args.command == 'list':
            filter_by = {}
            if args.format:
                filter_by['format'] = args.format
            if args.category:
                filter_by['category'] = args.category
            if args.search:
                filter_by['search'] = args.search
            
            templates = manager.list_templates(filter_by)
            
            if templates:
                print(f"📋 找到 {len(templates)} 个模板:\n")
                for i, template in enumerate(templates, 1):
                    print(f"{i}. {template['name']} ({template.get('format', '未知')})")
                    print(f"   ID: {template['id']}")
                    print(f"   描述: {template.get('description', '无描述')[:80]}...")
                    print(f"   场景: {', '.join(template.get('scenarios', []))[:50]}")
                    print(f"   创建: {template.get('created_time', '未知')[:10]}")
                    print()
            else:
                print("📭 未找到模板")
        
        elif args.command == 'get':
            template = manager.get_template(args.id)
            if template:
                print(f"📄 模板详情: {template['name']}")
                print(f"ID: {template['id']}")
                print(f"格式: {template.get('format', '未知')}")
                print(f"描述: {template.get('description', '无描述')}")
                print(f"场景: {', '.join(template.get('scenarios', []))}")
                print(f"分类: {', '.join(template.get('categories', []))}")
                print(f"变量: {', '.join(template.get('variables', []))}")
                print(f"创建: {template.get('created_time', '未知')}")
                print(f"修改: {template.get('modified_time', '未知')}")
                print(f"文件数: {template.get('file_count', 0)}")
            else:
                print(f"❌ 模板不存在: {args.id}")
        
        elif args.command == 'delete':
            confirm = input(f"⚠️  确认删除模板 {args.id}？(y/N): ")
            if confirm.lower() == 'y':
                if manager.delete_template(args.id):
                    print(f"✅ 模板 {args.id} 已删除")
                else:
                    print(f"❌ 删除失败，模板可能不存在")
            else:
                print("取消删除")
        
        elif args.command == 'match':
            result = manager.match_template(args.task)
            if result:
                print(f"🎯 最佳匹配模板: {result['name']}")
                print(f"ID: {result['id']}")
                print(f"描述: {result.get('description', '无描述')}")
                print(f"场景: {', '.join(result.get('scenarios', []))}")
                print(f"匹配原因: 该模板与您的任务描述高度相关")
            else:
                print("🤔 未找到匹配的模板")
                print("建议: 您可以添加新模板或使用通用模板")
        
        elif args.command == 'export':
            export_path = manager.export_template(args.id, args.output)
            print(f"📤 模板已导出到: {export_path}")
            print("包含文件:")
            for file in Path(export_path).iterdir():
                if file.is_file():
                    print(f"  - {file.name}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误: {e}")