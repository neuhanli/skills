#!/usr/bin/env python3
"""
基于ECharts的图表生成器
生成交互式HTML图表和静态PNG图片

**配置要求**:
- output_dir: 输出目录路径 (必需参数)

**安全说明**:
- 仅在指定输出目录生成文件
- 不修改系统文件或用户数据
- 生成的文件仅包含图表数据，不包含敏感信息
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# 依赖检查
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("❌ pandas 未安装，图表生成功能将不可用")
    print("💡 安装命令: pip install pandas")


class ChartGenerator:
    """基于ECharts的图表生成器"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 图表类型映射
        self.chart_types = {
            'line': self._generate_line_chart,
            'bar': self._generate_bar_chart,
            'pie': self._generate_pie_chart,
            'scatter': self._generate_scatter_chart,
            'area': self._generate_area_chart,
            'radar': self._generate_radar_chart
        }
    
    def generate_chart(self, df: pd.DataFrame, chart_type: str, 
                      x_axis: Optional[str] = None,
                      y_axis: Optional[List[str]] = None,
                      title: str = "数据图表",
                      description: str = "",
                      output_format: str = "html") -> Dict[str, Any]:
        """生成图表"""
        
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas 未安装，无法生成图表")
        
        if chart_type not in self.chart_types:
            raise ValueError(f"不支持的图表类型: {chart_type}")
        
        # 自动检测合适的轴
        if not x_axis:
            x_axis = self._detect_x_axis(df)
        
        if not y_axis:
            y_axis = self._detect_y_axis(df)
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成图表配置
        chart_config = self.chart_types[chart_type](df, x_axis, y_axis, title)
        
        # 生成说明文字（如果用户没有提供）
        if not description:
            description = self._generate_description(df, chart_type, x_axis, y_axis, chart_config)
        
        result = {
            'chart_type': chart_type,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'title': title,
            'description': description,
            'data_summary': self._get_data_summary(df),
            'chart_config': chart_config
        }
        
        # 根据输出格式生成相应文件
        if output_format == "html":
            html_content = self._generate_html(chart_config, title, description)
            html_filename = f"{chart_type}_chart_{timestamp}.html"
            html_path = self.output_dir / html_filename
            html_path.write_text(html_content, encoding='utf-8')
            result['html_path'] = str(html_path)
            result['html_content'] = html_content
        
        elif output_format == "md":
            md_content = self._generate_md_report(title, description, df, chart_config, chart_type, timestamp)
            md_filename = f"report_{timestamp}.md"
            md_path = self.output_dir / md_filename
            md_path.write_text(md_content, encoding='utf-8')
            result['md_path'] = str(md_path)
            result['md_content'] = md_content
        
        return result
    
    def _detect_x_axis(self, df: pd.DataFrame) -> str:
        """自动检测X轴"""
        # 优先选择日期列
        date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        if date_cols:
            return date_cols[0]
        
        # 其次选择文本列
        text_cols = [col for col in df.columns if df[col].dtype == 'object']
        if text_cols:
            return text_cols[0]
        
        # 最后选择第一列
        return df.columns[0]
    
    def _detect_y_axis(self, df: pd.DataFrame) -> List[str]:
        """自动检测Y轴"""
        # 优先选择数值列
        numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if numeric_cols:
            return numeric_cols[:3]  # 最多返回3个数值列
        
        # 如果没有数值列，返回除X轴外的其他列
        x_axis = self._detect_x_axis(df)
        other_cols = [col for col in df.columns if col != x_axis]
        return other_cols[:3]
    
    def _generate_line_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成折线图配置"""
        x_data = df[x_axis].tolist()
        
        series = []
        for y_col in y_axis:
            series.append({
                'name': y_col,
                'type': 'line',
                'data': df[y_col].tolist(),
                'smooth': True
            })
        
        return {
            'title': {'text': title},
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': y_axis},
            'xAxis': {
                'type': 'category',
                'data': x_data
            },
            'yAxis': {'type': 'value'},
            'series': series
        }
    
    def _generate_bar_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成柱状图配置"""
        x_data = df[x_axis].tolist()
        
        series = []
        for y_col in y_axis:
            series.append({
                'name': y_col,
                'type': 'bar',
                'data': df[y_col].tolist()
            })
        
        return {
            'title': {'text': title},
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': y_axis},
            'xAxis': {
                'type': 'category',
                'data': x_data
            },
            'yAxis': {'type': 'value'},
            'series': series
        }
    
    def _generate_pie_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成饼图配置"""
        y_col = y_axis[0] if y_axis else df.columns[1]
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'name': str(row[x_axis]),
                'value': float(row[y_col])
            })
        
        return {
            'title': {'text': title},
            'tooltip': {'trigger': 'item'},
            'series': [{
                'name': y_col,
                'type': 'pie',
                'radius': '50%',
                'data': data,
                'emphasis': {
                    'itemStyle': {
                        'shadowBlur': 10,
                        'shadowOffsetX': 0,
                        'shadowColor': 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        }
    
    def _generate_scatter_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成散点图配置"""
        x_col = x_axis
        y_col = y_axis[0] if y_axis else df.columns[1]
        
        data = []
        for _, row in df.iterrows():
            data.append([float(row[x_col]), float(row[y_col])])
        
        return {
            'title': {'text': title},
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'value'},
            'yAxis': {'type': 'value'},
            'series': [{
                'type': 'scatter',
                'data': data,
                'symbolSize': 10
            }]
        }
    
    def _generate_area_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成面积图配置"""
        x_data = df[x_axis].tolist()
        
        series = []
        for y_col in y_axis:
            series.append({
                'name': y_col,
                'type': 'line',
                'data': df[y_col].tolist(),
                'areaStyle': {},
                'smooth': True
            })
        
        return {
            'title': {'text': title},
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': y_axis},
            'xAxis': {
                'type': 'category',
                'data': x_data
            },
            'yAxis': {'type': 'value'},
            'series': series
        }
    
    def _generate_radar_chart(self, df: pd.DataFrame, x_axis: str, y_axis: List[str], title: str) -> Dict:
        """生成雷达图配置"""
        indicator = []
        for _, row in df.iterrows():
            indicator.append({
                'name': str(row[x_axis]),
                'max': df[y_axis].max().max() * 1.2
            })
        
        data = []
        for y_col in y_axis:
            data.append({
                'name': y_col,
                'value': df[y_col].tolist()
            })
        
        return {
            'title': {'text': title},
            'tooltip': {},
            'legend': {'data': y_axis},
            'radar': {
                'indicator': indicator
            },
            'series': [{
                'type': 'radar',
                'data': data
            }]
        }
    
    def _generate_description(self, df: pd.DataFrame, chart_type: str, 
                            x_axis: str, y_axis: List[str], chart_config: Dict) -> str:
        """自动生成图表说明"""
        
        chart_type_names = {
            'line': '折线图',
            'bar': '柱状图',
            'pie': '饼图',
            'scatter': '散点图',
            'area': '面积图',
            'radar': '雷达图'
        }
        
        chart_name = chart_type_names.get(chart_type, chart_type)
        
        description = f"""
## {chart_name}说明

此图表展示了数据中的趋势和分布情况：

- **图表类型**: {chart_name}
- **X轴数据**: {x_axis}
- **Y轴数据**: {', '.join(y_axis)}
- **数据记录数**: {len(df)} 条
- **数据字段**: {', '.join(df.columns)}

### 图表解读
"""
        
        if chart_type == 'line':
            description += "该折线图显示了数据随时间或其他分类变量的变化趋势。"
        elif chart_type == 'bar':
            description += "该柱状图比较了不同类别之间的数值差异。"
        elif chart_type == 'pie':
            description += "该饼图展示了各部分在整体中的占比情况。"
        elif chart_type == 'scatter':
            description += "该散点图显示了两个变量之间的相关性。"
        elif chart_type == 'area':
            description += "该面积图展示了数据的累积变化趋势。"
        elif chart_type == 'radar':
            description += "该雷达图展示了多个维度的数据分布情况。"
        
        return description.strip()
    
    def _get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取数据摘要"""
        return {
            'record_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'numeric_columns': [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])],
            'date_columns': [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        }
    
    def _generate_html(self, chart_config: Dict, title: str, description: str) -> str:
        """生成HTML页面"""
        
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart-container {{ width: 100%; height: 600px; }}
        .description {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        .data-summary {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="description">
        {description}
    </div>
    
    <div id="chart" class="chart-container"></div>
    
    <div class="data-summary">
        <h3>数据摘要</h3>
        <p>生成时间: {timestamp}</p>
        <p>图表类型: {chart_type}</p>
    </div>
    
    <script>
        var chart = echarts.init(document.getElementById('chart'));
        var option = {chart_config};
        chart.setOption(option);
        
        // 响应式调整
        window.addEventListener('resize', function() {{
            chart.resize();
        }});
    </script>
</body>
</html>
"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chart_type = chart_config.get('title', {}).get('text', '未知图表')
        
        return html_template.format(
            title=title,
            description=description.replace('\n', '<br>'),
            timestamp=timestamp,
            chart_type=chart_type,
            chart_config=json.dumps(chart_config, ensure_ascii=False, indent=2)
        )
    
    def _generate_md_report(self, title: str, description: str, df: pd.DataFrame, 
                          chart_config: Dict, chart_type: str, timestamp: str) -> str:
        """生成Markdown报告"""
        
        md_content = f"""# {title}

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 图表说明

{description}

## 数据摘要

- **记录数**: {len(df)}
- **字段数**: {len(df.columns)}
- **字段列表**: {', '.join(df.columns)}

## 图表预览

由于Markdown不支持直接显示ECharts图表，请查看生成的HTML文件以获得交互式图表体验。

## 数据预览

```
{df.head().to_string()}
```

## 图表配置

```json
{json.dumps(chart_config, ensure_ascii=False, indent=2)}
```

---

*此报告由 Smart Charts Skill 自动生成*
"""
        
        return md_content


def main():
    """测试函数"""
    # 创建测试数据
    data = {
        '月份': ['1月', '2月', '3月', '4月', '5月'],
        '销售额': [100, 150, 200, 180, 220],
        '利润': [20, 30, 40, 35, 45]
    }
    df = pd.DataFrame(data)
    
    # 测试图表生成
    generator = ChartGenerator()
    
    try:
        result = generator.generate_chart(
            df=df,
            chart_type='line',
            x_axis='月份',
            y_axis=['销售额', '利润'],
            title='销售数据趋势图',
            output_format='html'
        )
        
        print("图表生成成功!")
        print(f"HTML文件路径: {result.get('html_path')}")
        print(f"图表类型: {result['chart_type']}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()