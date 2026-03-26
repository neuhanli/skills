"""图表生成器。基于 DataFrame 生成独立的 ECharts 交互式 HTML 文件。"""

import sys
import json
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.exceptions import ChartError, ErrorCode
else:
    from .exceptions import ChartError, ErrorCode


class ChartType(Enum):
    LINE = 'line'
    BAR = 'bar'
    PIE = 'pie'
    SCATTER = 'scatter'
    AREA = 'area'
    RADAR = 'radar'
    HEATMAP = 'heatmap'
    TREEMAP = 'treemap'
    GRAPH = 'graph'
    BOXPLOT = 'boxplot'
    WATERFALL = 'waterfall'
    GAUGE = 'gauge'
    SANKEY = 'sankey'
    FUNNEL = 'funnel'
    SUNBURST = 'sunburst'
    WORDCLOUD = 'wordcloud'


class ChartGenerator:

    def __init__(self, output_dir: str = './smart_charts_output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        title: str = '数据图表',
        x_axis: Optional[str] = None,
        y_axis: Optional[List[str]] = None,
        width: int = 900,
        height: int = 560,
    ) -> Dict[str, str]:
        if df.empty:
            raise ChartError("数据为空", ErrorCode.DATA_EMPTY)
        try:
            ct = ChartType(chart_type)
        except ValueError:
            supported = ', '.join(t.value for t in ChartType)
            raise ChartError(f"不支持的图表类型: {chart_type}，支持: {supported}", ErrorCode.CHART_TYPE_UNSUPPORTED)

        gen = getattr(self, f'_{ct.value}', None)
        if gen is None:
            raise ChartError(f"暂不支持该图表类型: {chart_type}", ErrorCode.CHART_TYPE_UNSUPPORTED)

        x_axis, y_axis = self._prepare_axes(df, chart_type, x_axis, y_axis)
        option = gen(df, x_axis, y_axis, title)
        html_path = self._save_html(option, title, width, height)
        return {'html_path': str(html_path)}

    def generate_multi_charts(
        self,
        df: pd.DataFrame,
        chart_configs: List[Dict[str, Any]],
        width: int = 900,
        height: int = 560,
    ) -> Dict[str, Any]:
        """批量生成多个图表，返回 {'charts': [{'type', 'title', 'html_path'}]}"""
        results = []
        for cfg in chart_configs:
            try:
                r = self.generate_chart(
                    df=df,
                    chart_type=cfg.get('type', 'bar'),
                    title=cfg.get('title', ''),
                    x_axis=cfg.get('x_axis'),
                    y_axis=cfg.get('y_axis'),
                    width=cfg.get('width', width),
                    height=cfg.get('height', height),
                )
                results.append({**cfg, 'html_path': r['html_path'], 'success': True})
            except Exception as e:
                results.append({**cfg, 'error': str(e), 'success': False})
        return {'charts': results}

    # ---- 轴自动检测 ----

    def _prepare_axes(self, df, chart_type, x_axis, y_axis) -> Tuple[str, List[str]]:
        if x_axis is None:
            date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns
            cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns
            x_axis = date_cols[0] if len(date_cols) > 0 else (cat_cols[0] if len(cat_cols) > 0 else df.columns[0])

        if y_axis is None:
            avail = [c for c in df.columns if c != x_axis]
            nums = df[avail].select_dtypes(include=[np.number]).columns.tolist()
            y_axis = nums[:5] if nums else avail[:3]
        elif isinstance(y_axis, str):
            y_axis = [y_axis]

        if x_axis not in df.columns:
            raise ChartError(f"X轴字段不存在: {x_axis}", ErrorCode.CHART_CONFIG_ERROR)
        for y in y_axis:
            if y not in df.columns:
                raise ChartError(f"Y轴字段不存在: {y}", ErrorCode.CHART_CONFIG_ERROR)
        return x_axis, y_axis

    # ---- 图表配置生成 ----

    def _base(self, title, x_label='', y_label=''):
        return {
            'title': {'text': title, 'left': 'center', 'textStyle': {'fontSize': 16}},
            'tooltip': {'trigger': 'axis'},
            'legend': {'top': 'bottom'},
            'grid': {'left': '3%', 'right': '4%', 'bottom': '12%', 'containLabel': True},
        }

    def _line(self, df, x, y, title):
        opt = self._base(title)
        opt['xAxis'] = {'type': 'category', 'data': df[x].astype(str).tolist()}
        opt['yAxis'] = {'type': 'value', 'name': y[0] if len(y) == 1 else ''}
        opt['series'] = [
            {'name': col, 'type': 'line', 'smooth': True, 'data': df[col].tolist()}
            for col in y
        ]
        return opt

    def _bar(self, df, x, y, title):
        opt = self._base(title)
        opt['xAxis'] = {'type': 'category', 'data': df[x].astype(str).tolist()}
        opt['yAxis'] = {'type': 'value'}
        opt['series'] = [
            {'name': col, 'type': 'bar', 'data': df[col].tolist()}
            for col in y
        ]
        return opt

    def _pie(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'trigger': 'item', 'formatter': '{a} <br/>{b}: {c} ({d}%)'}
        opt['legend'] = {'orient': 'vertical', 'left': 'left', 'top': 'center'}
        y_col = y[0] if y else df.columns[-1]
        data = [{'name': str(r[x]), 'value': float(r[y_col])} for _, r in df.iterrows()]
        opt['series'] = [{
            'name': y_col, 'type': 'pie', 'radius': ['40%', '70%'], 'data': data,
            'label': {'show': True, 'formatter': '{b}: {c} ({d}%)'},
            'emphasis': {'itemStyle': {'shadowBlur': 10, 'shadowColor': 'rgba(0,0,0,0.5)'}},
        }]
        return opt

    def _scatter(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'trigger': 'item', 'formatter': '({c})'}
        opt['xAxis'] = {'type': 'value', 'name': x, 'scale': True}
        opt['yAxis'] = {'type': 'value', 'name': y[0] if y else '', 'scale': True}
        y_col = y[0] if y else df.columns[-1]
        data = [[float(r[x]), float(r[y_col])] for _, r in df.iterrows()]
        opt['series'] = [{'name': '数据点', 'type': 'scatter', 'data': data, 'symbolSize': 10}]
        return opt

    def _area(self, df, x, y, title):
        opt = self._line(df, x, y, title)
        for s in opt['series']:
            s['areaStyle'] = {'opacity': 0.5}
        return opt

    def _radar(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'trigger': 'item'}
        max_val = float(df[y].max().max() * 1.2) if len(y) > 0 else 100
        indicator = [{'name': str(r[x]), 'max': max_val} for _, r in df.iterrows()]
        opt['radar'] = {'indicator': indicator, 'shape': 'polygon'}
        opt['series'] = [{'name': '雷达图', 'type': 'radar', 'data': [{'name': c, 'value': df[c].tolist()} for c in y]}]
        return opt

    def _heatmap(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'position': 'top'}
        y_data = y[:2] if len(y) >= 2 else [y[0], y[0]]
        x_data = df[x].astype(str).tolist()
        matrix = [[j, i, float(df.iloc[i][y_data[j]]) if j < len(y_data) else 0]
                   for i in range(len(x_data)) for j in range(len(y_data))]
        opt['xAxis'] = {'type': 'category', 'data': y_data, 'splitArea': {'show': True}}
        opt['yAxis'] = {'type': 'category', 'data': x_data, 'splitArea': {'show': True}}
        opt['visualMap'] = {'min': 0, 'max': 100, 'calculable': True, 'orient': 'horizontal', 'left': 'center', 'bottom': '15%'}
        opt['series'] = [{'name': '热力图', 'type': 'heatmap', 'data': matrix, 'label': {'show': True}}]
        return opt

    def _treemap(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'trigger': 'item'}
        y_col = y[0] if y else df.columns[-1]
        data = [{'name': str(r[x]), 'value': float(r[y_col])} for _, r in df.iterrows()]
        opt['series'] = [{'name': '树图', 'type': 'treemap', 'data': data, 'roam': False, 'breadcrumb': {'show': True}}]
        return opt

    def _graph(self, df, x, y, title):
        opt = self._base(title)
        y_col = y[0] if y else df.columns[-1]
        nodes = [{'id': str(r[x]), 'name': str(r[x]), 'value': float(r[y_col]), 'category': 0} for _, r in df.iterrows()]
        links = [{'source': nodes[i]['id'], 'target': nodes[i+1]['id'], 'value': 1} for i in range(len(nodes)-1)]
        opt['series'] = [{'name': '关系图', 'type': 'graph', 'layout': 'force', 'data': nodes, 'links': links,
                          'roam': True, 'label': {'show': True}, 'force': {'repulsion': 100, 'edgeLength': 30}}]
        return opt

    def _boxplot(self, df, x, y, title):
        opt = self._base(title)
        opt['tooltip'] = {'trigger': 'item', 'axisPointer': {'type': 'shadow'}}
        opt['xAxis'] = {'type': 'category', 'data': df[x].astype(str).tolist(), 'boundaryGap': True}
        opt['yAxis'] = {'type': 'value'}
        cols = y[:3] if len(y) > 0 else df.select_dtypes(include=[np.number]).columns[:3]
        box_data = []
        for col in cols:
            s = df[col].dropna()
            q1, q2, q3 = float(s.quantile(0.25)), float(s.quantile(0.5)), float(s.quantile(0.75))
            iqr = q3 - q1
            lo = max(float(s.min()), q1 - 1.5 * iqr)
            hi = min(float(s.max()), q3 + 1.5 * iqr)
            box_data.append([lo, q1, q2, q3, hi])
        opt['series'] = [{'name': '箱线图', 'type': 'boxplot', 'data': box_data}]
        return opt

    def _waterfall(self, df, x, y, title):
        opt = self._bar(df, x, y, title)
        y_col = y[0] if y else df.columns[-1]
        vals = df[y_col].tolist()
        diffs = [vals[0]] + [vals[i] - vals[i-1] for i in range(1, len(vals))]
        opt['series'][0]['data'] = diffs
        opt['series'][0]['label'] = {'show': True, 'position': 'top'}
        return opt

    def _gauge(self, df, x, y, title):
        y_col = y[0] if y else df.select_dtypes(include=[np.number]).columns[0]
        value = float(df[y_col].mean())
        opt = {'title': {'text': title, 'left': 'center'}}
        opt['series'] = [{'name': '仪表盘', 'type': 'gauge', 'detail': {'formatter': '{value}%'},
                          'data': [{'value': value, 'name': y_col}],
                          'axisLine': {'lineStyle': {'width': 10, 'color': [[0.3, '#67e0e3'], [0.7, '#37a2da'], [1, '#fd666d']]}}}]
        return opt

    def _sankey(self, df, x, y, title):
        opt = {'title': {'text': title, 'left': 'center'}}
        y_col = y[0] if y else df.columns[-1]
        nodes, links = [], []
        for i, r in df.iterrows():
            nodes.append({'name': str(r[x])})
            if i > 0:
                links.append({'source': str(df.iloc[i-1][x]), 'target': str(r[x]),
                             'value': float(r[y_col]) if pd.notna(r.get(y_col)) else 1})
        opt['tooltip'] = {'trigger': 'item', 'formatter': '{source} -> {target}: {value}'}
        opt['series'] = [{'name': '桑基图', 'type': 'sankey', 'data': nodes, 'links': links,
                          'emphasis': {'focus': 'adjacency'}, 'lineStyle': {'curveness': 0.5}}]
        return opt

    def _funnel(self, df, x, y, title):
        opt = self._base(title)
        y_col = y[0] if y else df.columns[-1]
        data = [{'name': str(r[x]), 'value': float(r[y_col])} for _, r in df.iterrows()]
        opt['series'] = [{'name': '漏斗图', 'type': 'funnel', 'left': '10%', 'top': 60, 'bottom': 60, 'width': '80%',
                          'min': 0, 'max': 100, 'sort': 'descending', 'gap': 2,
                          'label': {'show': True, 'position': 'inside'},
                          'data': data}]
        return opt

    def _sunburst(self, df, x, y, title):
        opt = {'title': {'text': title, 'left': 'center'}}
        y_col = y[0] if y else df.columns[-1]
        data = [{'name': str(r[x]), 'value': float(r[y_col])} for _, r in df.iterrows()]
        opt['series'] = [{'name': '旭日图', 'type': 'sunburst', 'data': data, 'radius': [0, '90%'],
                          'label': {'rotate': 'radial'}}]
        return opt

    def _wordcloud(self, df, x, y, title):
        opt = {'title': {'text': title, 'left': 'center'}}
        y_col = y[0] if y else df.columns[-1]
        data = [{'name': str(r[x]), 'value': float(r[y_col])} for _, r in df.iterrows()]
        opt['series'] = [{'name': '词云', 'type': 'wordCloud', 'shape': 'circle',
                          'sizeRange': [12, 60], 'rotationRange': [-90, 90], 'rotationStep': 45,
                          'data': data}]
        return opt

    # ---- HTML 输出 ----

    def _save_html(self, option: Dict, title: str, width: int, height: int) -> Path:
        import hashlib
        content_str = json.dumps(option, ensure_ascii=False, sort_keys=True)
        suffix = hashlib.md5(content_str.encode()).hexdigest()[:6]
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:30]
        filename = f"{safe_title}_{suffix}.html"
        path = self.output_dir / filename

        option_json = json.dumps(option, ensure_ascii=False, indent=2)
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>
body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: #f8f9fa; }}
.container {{ max-width: {width}px; margin: 0 auto; background: #fff; padding: 30px;
             border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
.header {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #4CAF50; }}
.title {{ font-size: 24px; font-weight: 700; color: #2E7D32; margin: 0; }}
.subtitle {{ font-size: 12px; color: #999; }}
.chart {{ width: 100%; height: {height}px; }}
.controls {{ text-align: center; margin: 15px 0; }}
.btn {{ display: inline-block; padding: 6px 16px; background: #4CAF50; color: #fff;
        border: none; border-radius: 4px; cursor: pointer; font-size: 13px; margin: 0 4px; }}
.btn:hover {{ background: #45a049; }}
.footer {{ margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee; text-align: center;
          font-size: 11px; color: #aaa; }}
@media print {{ .controls {{ display: none; }} .container {{ box-shadow: none; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1 class="title">{title}</h1>
    <div class="subtitle">Smart Charts &middot; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
  </div>
  <div class="controls">
    <button class="btn" onclick="saveAsImage()">保存图片</button>
    <button class="btn" onclick="toggleFull()">全屏</button>
  </div>
  <div id="chart" class="chart"></div>
  <div class="footer">由 Smart Charts 生成 &middot; ECharts 5.4.3</div>
</div>
<script>
var chart = echarts.init(document.getElementById('chart'));
chart.setOption({option_json});
window.addEventListener('resize', function() {{ chart.resize(); }});
function saveAsImage() {{
  var url = chart.getDataURL({{ type: 'png', pixelRatio: 2, backgroundColor: '#fff' }});
  var a = document.createElement('a'); a.href = url; a.download = '{title}.png'; a.click();
}}
function toggleFull() {{
  var el = document.getElementById('chart');
  if (!document.fullscreenElement) el.requestFullscreen();
  else document.exitFullscreen();
}}
</script>
</body>
</html>"""
        path.write_text(html, encoding='utf-8')
        return path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python chart_generator.py <file_path> <chart_type> [--title 标题] [--x-axis 列名] [--y-axis 列1 列2] [--output-dir 目录]")
        sys.exit(1)

    args = sys.argv[1:]
    file_path = args[0]
    chart_type = args[1]

    title = '数据图表'
    x_axis = None
    y_axis = None
    output_dir = './smart_charts_output'

    i = 2
    while i < len(args):
        if args[i] == '--title' and i + 1 < len(args):
            title = args[i + 1]; i += 2
        elif args[i] == '--x-axis' and i + 1 < len(args):
            x_axis = args[i + 1]; i += 2
        elif args[i] == '--y-axis':
            y_list = []
            i += 1
            while i < len(args) and not args[i].startswith('--'):
                y_list.append(args[i]); i += 1
            y_axis = y_list if y_list else None
        elif args[i] == '--output-dir' and i + 1 < len(args):
            output_dir = args[i + 1]; i += 2
        else:
            i += 1

    # 兼容直接运行和 import 两种方式
    if __package__ is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from core.data_parser import DataParser
    else:
        from .data_parser import DataParser

    try:
        dp = DataParser()
        df = dp.parse_file(file_path)
        gen = ChartGenerator(output_dir=output_dir)
        result = gen.generate_chart(df, chart_type, title=title, x_axis=x_axis, y_axis=y_axis)
        print(result['html_path'])
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
