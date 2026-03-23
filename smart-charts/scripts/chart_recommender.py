#!/usr/bin/env python3
"""
自动图表推荐器
根据数据特征自动推荐最合适的图表类型

**配置要求**:
- 无必需配置参数

**安全说明**:
- 仅分析提供的数据，不访问外部系统
- 不存储或传输用户数据
- 推荐结果基于数据特征，不涉及敏感信息
"""

import pandas as pd
from typing import List, Dict, Any, Optional


class ChartRecommender:
    """图表推荐器类"""
    
    def __init__(self):
        # 图表类型及其适用场景
        self.chart_types = {
            'line': {
                'name': '折线图',
                'description': '显示数据随时间或其他连续变量的变化趋势',
                'suitable_for': ['时间序列', '趋势分析', '连续变化'],
                'requirements': {
                    'min_columns': 2,
                    'max_columns': 10,
                    'preferred_x': ['日期', '时间', '序号'],
                    'preferred_y': ['数值', '百分比']
                }
            },
            'bar': {
                'name': '柱状图',
                'description': '比较不同类别之间的数值差异',
                'suitable_for': ['分类比较', '排名对比', '离散数据'],
                'requirements': {
                    'min_columns': 2,
                    'max_columns': 20,
                    'preferred_x': ['类别', '名称', '文本'],
                    'preferred_y': ['数值', '计数', '百分比']
                }
            },
            'pie': {
                'name': '饼图',
                'description': '展示各部分在整体中的占比情况',
                'suitable_for': ['占比分析', '构成比例', '百分比数据'],
                'requirements': {
                    'min_columns': 2,
                    'max_columns': 2,
                    'preferred_x': ['类别', '名称'],
                    'preferred_y': ['数值', '百分比']
                }
            },
            'scatter': {
                'name': '散点图',
                'description': '显示两个变量之间的相关性',
                'suitable_for': ['相关性分析', '分布观察', '异常值检测'],
                'requirements': {
                    'min_columns': 2,
                    'max_columns': 10,
                    'preferred_x': ['数值', '连续变量'],
                    'preferred_y': ['数值', '连续变量']
                }
            },
            'area': {
                'name': '面积图',
                'description': '展示数据的累积变化趋势',
                'suitable_for': ['累积趋势', '堆叠分析', '时间序列'],
                'requirements': {
                    'min_columns': 2,
                    'max_columns': 10,
                    'preferred_x': ['日期', '时间', '序号'],
                    'preferred_y': ['数值', '百分比']
                }
            },
            'radar': {
                'name': '雷达图',
                'description': '展示多个维度的数据分布情况',
                'suitable_for': ['多维度比较', '综合评价', '性能分析'],
                'requirements': {
                    'min_columns': 3,
                    'max_columns': 8,
                    'preferred_x': ['维度', '指标'],
                    'preferred_y': ['数值', '评分']
                }
            }
        }
    
    def recommend_charts(self, df: pd.DataFrame, 
                        target_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """推荐适合的图表类型"""
        
        # 分析数据特征
        data_features = self._analyze_data_features(df, target_columns)
        
        # 为每种图表类型计算匹配度
        recommendations = []
        
        for chart_type, chart_info in self.chart_types.items():
            score = self._calculate_match_score(chart_info, data_features)
            
            if score > 0:  # 只推荐匹配度大于0的图表
                recommendations.append({
                    'chart_type': chart_type,
                    'name': chart_info['name'],
                    'description': chart_info['description'],
                    'match_score': score,
                    'suggested_x': data_features['suggested_x'],
                    'suggested_y': data_features['suggested_y'],
                    'reasoning': self._generate_reasoning(chart_type, data_features)
                })
        
        # 按匹配度排序
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations
    
    def _analyze_data_features(self, df: pd.DataFrame, target_columns: Optional[List[str]]) -> Dict[str, Any]:
        """分析数据特征"""
        
        features = {
            'column_count': len(df.columns),
            'row_count': len(df),
            'numeric_columns': [],
            'date_columns': [],
            'text_columns': [],
            'column_types': {},
            'suggested_x': None,
            'suggested_y': []
        }
        
        # 分析每列的数据类型
        for col in df.columns:
            col_type = self._classify_column_type(df[col])
            features['column_types'][col] = col_type
            
            if col_type == 'numeric':
                features['numeric_columns'].append(col)
            elif col_type == 'date':
                features['date_columns'].append(col)
            elif col_type == 'text':
                features['text_columns'].append(col)
        
        # 建议X轴和Y轴
        if target_columns:
            # 如果用户指定了目标列，优先使用这些列
            features['suggested_x'] = target_columns[0] if target_columns else None
            features['suggested_y'] = target_columns[1:] if len(target_columns) > 1 else []
        else:
            # 自动推荐
            if features['date_columns']:
                features['suggested_x'] = features['date_columns'][0]
            elif features['text_columns']:
                features['suggested_x'] = features['text_columns'][0]
            else:
                features['suggested_x'] = df.columns[0]
            
            features['suggested_y'] = features['numeric_columns']
        
        return features
    
    def _classify_column_type(self, series: pd.Series) -> str:
        """分类列的数据类型"""
        
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'date'
        elif pd.api.types.is_string_dtype(series):
            # 检查是否是分类数据
            unique_count = series.nunique()
            if unique_count <= 20 and len(series) > unique_count * 2:
                return 'category'
            else:
                return 'text'
        else:
            return 'other'
    
    def _calculate_match_score(self, chart_info: Dict, data_features: Dict) -> float:
        """计算图表匹配度分数"""
        
        score = 0.0
        requirements = chart_info['requirements']
        
        # 检查列数要求
        col_count = data_features['column_count']
        if col_count < requirements['min_columns'] or col_count > requirements['max_columns']:
            return 0.0
        
        # 基础分数
        score += 1.0
        
        # 检查X轴类型匹配
        if data_features['suggested_x']:
            x_col_type = data_features['column_types'][data_features['suggested_x']]
            if any(x_type in x_col_type for x_type in requirements['preferred_x']):
                score += 1.0
        
        # 检查Y轴类型匹配
        if data_features['suggested_y']:
            y_match_count = 0
            for y_col in data_features['suggested_y']:
                y_col_type = data_features['column_types'][y_col]
                if any(y_type in y_col_type for y_type in requirements['preferred_y']):
                    y_match_count += 1
            
            if y_match_count > 0:
                score += y_match_count / len(data_features['suggested_y'])
        
        # 特殊规则
        if chart_info['name'] == '饼图':
            # 饼图需要类别数据和数值数据
            if (len(data_features['text_columns']) >= 1 and 
                len(data_features['numeric_columns']) >= 1):
                score += 1.0
        
        elif chart_info['name'] == '雷达图':
            # 雷达图需要多个数值维度
            if len(data_features['numeric_columns']) >= 3:
                score += 1.0
        
        return score
    
    def _generate_reasoning(self, chart_type: str, data_features: Dict) -> str:
        """生成推荐理由"""
        
        reasoning_map = {
            'line': f"数据包含{len(data_features['date_columns'])}个日期列和{len(data_features['numeric_columns'])}个数值列，适合展示趋势变化",
            'bar': f"数据包含{len(data_features['text_columns'])}个文本列和{len(data_features['numeric_columns'])}个数值列，适合进行类别比较",
            'pie': f"数据包含分类数据和数值数据，适合展示占比关系",
            'scatter': f"数据包含多个数值列，适合分析变量间的相关性",
            'area': f"数据适合展示累积变化趋势",
            'radar': f"数据包含多个数值维度，适合进行多维度综合评价"
        }
        
        return reasoning_map.get(chart_type, "数据特征适合生成此类型图表")
    
    def get_best_recommendation(self, df: pd.DataFrame, 
                              target_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取最佳推荐"""
        recommendations = self.recommend_charts(df, target_columns)
        
        if recommendations:
            return recommendations[0]  # 返回匹配度最高的推荐
        else:
            # 如果没有推荐，返回默认的柱状图
            return {
                'chart_type': 'bar',
                'name': '柱状图',
                'description': '比较不同类别之间的数值差异',
                'match_score': 1.0,
                'suggested_x': df.columns[0],
                'suggested_y': df.columns[1:2] if len(df.columns) > 1 else [],
                'reasoning': '默认推荐柱状图进行数据展示'
            }


def main():
    """测试函数"""
    recommender = ChartRecommender()
    
    # 测试数据1：销售数据
    sales_data = {
        '月份': ['1月', '2月', '3月', '4月', '5月'],
        '销售额': [100, 150, 200, 180, 220],
        '利润': [20, 30, 40, 35, 45],
        '增长率': [0.0, 0.5, 0.33, -0.1, 0.22]
    }
    df_sales = pd.DataFrame(sales_data)
    
    print("=== 销售数据推荐 ===")
    recommendations = recommender.recommend_charts(df_sales)
    for rec in recommendations:
        print(f"{rec['name']}: 匹配度 {rec['match_score']:.2f}")
        print(f"  理由: {rec['reasoning']}")
        print(f"  建议X轴: {rec['suggested_x']}")
        print(f"  建议Y轴: {rec['suggested_y']}")
        print()
    
    # 测试数据2：用户评分数据
    user_data = {
        '用户ID': ['U001', 'U002', 'U003', 'U004', 'U005'],
        '满意度': [4.5, 3.8, 4.2, 3.5, 4.8],
        '活跃度': [85, 70, 90, 60, 95],
        '留存率': [0.92, 0.85, 0.88, 0.78, 0.96]
    }
    df_users = pd.DataFrame(user_data)
    
    print("=== 用户数据推荐 ===")
    best_rec = recommender.get_best_recommendation(df_users)
    print(f"最佳推荐: {best_rec['name']}")
    print(f"匹配度: {best_rec['match_score']:.2f}")
    print(f"理由: {best_rec['reasoning']}")


if __name__ == "__main__":
    main()