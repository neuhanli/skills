#!/usr/bin/env python3
"""
数据解析和清洗工具
支持多种文件格式的数据解析和预处理

**配置要求**:
- config_file: MySQL配置文件路径 (必需参数，默认: sqlconfig.json)

**安全说明**:
- 仅访问用户提供的文件和配置的数据库
- MySQL配置文件应仅包含开发/测试环境凭据
- 不支持生产环境数据库连接
"""

import pandas as pd
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import sys
import os

# 动态导入MySQL连接器，避免在没有安装时导致导入错误
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️ mysql-connector-python 未安装，MySQL功能将不可用")
    print("💡 安装命令: pip install mysql-connector-python")


class DataParser:
    """数据解析器类，支持多种文件格式"""
    
    def __init__(self, config_file: str = "sqlconfig.json"):
        self.supported_formats = {
            '.csv': self._parse_csv,
            '.xlsx': self._parse_excel,
            '.xls': self._parse_excel,
            '.json': self._parse_json,
            '.txt': self._parse_text
        }
        self.mysql_config = None
        self.config_file = config_file
        self._load_mysql_config()
    
    def parse_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """解析文件并返回DataFrame"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        parser_func = self.supported_formats[file_ext]
        return parser_func(file_path, **kwargs)
    
    def _parse_csv(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """解析CSV文件"""
        delimiter = kwargs.get('delimiter', ',')
        encoding = kwargs.get('encoding', 'utf-8')
        
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
        except UnicodeDecodeError:
            # 尝试其他编码
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='gbk')
        
        return self._clean_data(df)
    
    def _parse_excel(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """解析Excel文件"""
        sheet_name = kwargs.get('sheet_name', 0)
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return self._clean_data(df)
    
    def _parse_json(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """解析JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 尝试不同的JSON结构
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # 如果是字典，尝试找到数组数据
            for key, value in data.items():
                if isinstance(value, list):
                    df = pd.DataFrame(value)
                    break
            else:
                # 如果没有数组，将字典转换为DataFrame
                df = pd.DataFrame([data])
        else:
            raise ValueError("不支持的JSON结构")
        
        return self._clean_data(df)
    
    def _parse_text(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """解析文本文件"""
        delimiter = kwargs.get('delimiter', None)
        
        if delimiter:
            # 自定义分隔符
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
        else:
            # 尝试自动检测分隔符
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            # 常见分隔符检测
            for delim in [',', '\t', ';', '|']:
                if delim in first_line:
                    df = pd.read_csv(file_path, delimiter=delim, encoding='utf-8')
                    break
            else:
                # 如果没有分隔符，按行读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                df = pd.DataFrame({'content': lines})
        
        return self._clean_data(df)
    
    def query_mysql(self, query: str, params: tuple = None) -> pd.DataFrame:
        """安全的MySQL查询方法"""
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python 未安装，无法使用MySQL功能")
        
        if not self.mysql_config:
            raise ValueError("MySQL配置未设置，请先调用set_mysql_config()")
        
        # SQL注入检测
        if self._detect_sql_injection(query):
            raise ValueError("检测到潜在的SQL注入攻击，查询被拒绝")
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            # 使用参数化查询
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            conn.close()
            return self._clean_data(df)
        except mysql.connector.Error as e:
            raise ValueError(f"MySQL查询错误: {e}")
    
    def get_mysql_tables(self) -> List[str]:
        """获取MySQL数据库中的所有表"""
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python 未安装，无法使用MySQL功能")
        
        if not self.mysql_config:
            raise ValueError("MySQL配置未设置，请先调用set_mysql_config()")
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            return tables
        except mysql.connector.Error as e:
            raise ValueError(f"获取MySQL表错误: {e}")
    
    def _detect_sql_injection(self, query: str) -> bool:
        """检测SQL注入攻击"""
        dangerous_patterns = [
            r'\b(?:DROP\s+TABLE|DELETE\s+FROM|UPDATE\s+\w+\s+SET)\b',
            r'\b(?:UNION\s+SELECT|INSERT\s+INTO)\b',
            r'\b(?:EXEC\s*\(|EXECUTE\s*\(|sp_)\b',
            r';.*--',  # 注释攻击
            r'\bor\b.*=.*\bor\b',  # OR注入
            r"'.*--",  # 单引号注释
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return True
        return False

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        # 去除空行
        df = df.dropna(how='all')
        
        # 去除完全重复的行
        df = df.drop_duplicates()
        
        # 自动推断数据类型
        for col in df.columns:
            # 尝试转换为数值类型
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            
            # 尝试转换为日期类型
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    def _load_mysql_config(self):
        """从配置文件加载MySQL配置"""
        if not os.path.exists(self.config_file):
            print(f"⚠️ MySQL配置文件 {self.config_file} 不存在，MySQL功能将使用手动配置")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 优先使用connections中的配置，如果没有则使用根级mysql配置
            if 'connections' in config_data and config_data['connections']:
                # 使用第一个连接配置
                connection_name = list(config_data['connections'].keys())[0]
                self.mysql_config = config_data['connections'][connection_name]
                print(f"✅ 已从配置文件加载MySQL连接配置: {connection_name}")
            elif 'mysql' in config_data:
                self.mysql_config = config_data['mysql']
                print("✅ 已从配置文件加载MySQL配置")
            else:
                print("⚠️ 配置文件中未找到有效的MySQL配置")
                
        except Exception as e:
            print(f"❌ 加载MySQL配置文件失败: {e}")
    
    def set_mysql_config(self, host: str, user: str, password: str, database: str, port: int = 3306, connection_name: str = None):
        """设置MySQL数据库配置"""
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python 未安装，无法使用MySQL功能")
        
        self.mysql_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        
        # 如果提供了连接名称，更新配置文件
        if connection_name:
            self._update_config_file(connection_name)
    
    def _update_config_file(self, connection_name: str):
        """更新配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            if 'connections' not in config_data:
                config_data['connections'] = {}
            
            config_data['connections'][connection_name] = self.mysql_config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已更新配置文件中的连接配置: {connection_name}")
            
        except Exception as e:
            print(f"❌ 更新配置文件失败: {e}")
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取数据摘要"""
        summary = {
            'record_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])],
            'date_columns': [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])],
            'text_columns': [col for col in df.columns if df[col].dtype == 'object']
        }
        
        # 数值列的统计信息
        if summary['numeric_columns']:
            summary['numeric_stats'] = df[summary['numeric_columns']].describe().to_dict()
        
        return summary


def main():
    """测试函数"""
    parser = DataParser()
    
    # 示例用法
    try:
        # 解析CSV文件
        df = parser.parse_file('example.csv')
        summary = parser.get_data_summary(df)
        print("数据摘要:", summary)
        print("前5行数据:")
        print(df.head())
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()