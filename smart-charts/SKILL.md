---
name: "smart-charts"
description: "Smart chart generation tool that creates interactive ECharts from Excel, CSV, JSON files and MySQL databases. Use when users need to analyze data, generate charts, or create visual reports from various data sources."
environment:
  - "sqlconfig.json: MySQL database configuration file (required for database access)"
config:
  - "input_dir: Directory path for data files (required for file processing)"
  - "output_dir: Directory path for generated charts (required for chart generation)"
---

# Smart Charts Skill

Smart Charts is an intelligent chart generation skill that helps users create interactive charts and reports from various data sources including Excel files, CSV files, JSON data, and MySQL databases.

## When to Use This Skill

Use this skill when the user:
- Asks to "analyze data" or "process data files"
- Wants to "generate charts" or "create visualizations"
- Needs to "make reports" from Excel, CSV, or JSON files
- Asks about "data visualization" or "chart generation"
- Mentions specific file types like "Excel", "CSV", "JSON"
- Needs to work with "MySQL databases" for reporting

## What This Skill Does

### Core Capabilities
- **File Processing**: Read and parse Excel (.xlsx, .xls), CSV, and JSON files
- **Database Access**: Query MySQL databases for data analysis
- **Chart Generation**: Create interactive ECharts (line, bar, pie, scatter, area, radar)
- **Report Creation**: Generate HTML reports with interactive visualizations
- **Smart Recommendations**: Automatically suggest appropriate chart types based on data

### Supported Data Sources
- Excel spreadsheets (.xlsx, .xls)
- CSV files with various delimiters
- JSON data files and APIs
- MySQL database connections

## How to Use This Skill

### Workflow Overview

The data visualization process follows this logical sequence:

```
1. File Location → 2. Data Parsing → 3. Chart Recommendation → 4. Chart Generation
```

### Step 1: File Location (Required)
**Script**: `file_locator.py`
**Purpose**: Locate data files based on user description

**Parameters**:
- `FileLocator(input_dir: str)` - **Required**: Input directory path
- `locate_files(description: str)` - **Required**: File description string

**Usage**:
```python
from scripts.file_locator import FileLocator

# User must provide input directory
locator = FileLocator(input_dir="/path/to/data")  # Required parameter
files = locator.locate_files("sales data file")  # Required parameter
```

### Step 2: Data Parsing (Required)
**Script**: `data_parser.py`
**Purpose**: Parse data files or query databases

**Parameters**:
- `DataParser(config_file: str)` - **Required**: MySQL configuration file path
- `parse_file(file_path: str)` - **Required**: File path
- `query_mysql(query: str)` - **Required**: SQL query statement

**Usage**:
```python
from scripts.data_parser import DataParser

# Parse file data
parser = DataParser(config_file="sqlconfig.json")  # Required parameter
df = parser.parse_file(files[0])  # Required parameter

# Or query database
df = parser.query_mysql("SELECT * FROM sales_data")  # Required parameter
```

### Step 3: Chart Recommendation (Optional)
**Script**: `chart_recommender.py`
**Purpose**: Recommend optimal chart types based on data characteristics

**Parameters**:
- `ChartRecommender()` - No parameters required
- `recommend_charts(df)` - **Required**: DataFrame for analysis
- `get_best_recommendation(df)` - **Required**: DataFrame for analysis

**Usage**:
```python
from scripts.chart_recommender import ChartRecommender

# Get chart recommendations
recommender = ChartRecommender()
recommendations = recommender.recommend_charts(df)  # Required parameter
best_chart = recommender.get_best_recommendation(df)

print(f"Recommended: {best_chart['chart_type']} (score: {best_chart['score']})")
```

### Step 4: Chart Generation (Required)
**Script**: `chart_generator.py`
**Purpose**: Generate interactive ECharts visualizations

**Parameters**:
- `ChartGenerator(output_dir: str)` - **Required**: Output directory path
- `generate_chart(df, chart_type, x_axis, y_axis, title, description, output_format)`
  - `df` - **Required**: pandas DataFrame data
  - `chart_type` - **Required**: Chart type (line, bar, pie, scatter, area, radar)
  - `x_axis` - **Optional**: X-axis field name
  - `y_axis` - **Optional**: Y-axis field list
  - `title` - **Optional**: Chart title
  - `description` - **Optional**: Chart description
  - `output_format` - **Optional**: Output format (html, png)

**Usage**:
```python
from scripts.chart_generator import ChartGenerator

# Generate visualization
generator = ChartGenerator(output_dir="/path/to/output")  # Required parameter
result = generator.generate_chart(
    df=df,  # Required
    chart_type=best_chart['chart_type'],  # Required
    x_axis='date',  # Optional
    y_axis=['sales']  # Optional
)
```

### Complete Workflow Example

```python
# Complete data visualization workflow
from scripts.file_locator import FileLocator
from scripts.data_parser import DataParser
from scripts.chart_recommender import ChartRecommender
from scripts.chart_generator import ChartGenerator

# Step 1: Locate files (User must provide input directory)
locator = FileLocator(input_dir="/path/to/data")  # Required
files = locator.locate_files("sales data file")  # Required

# Step 2: Parse data
parser = DataParser(config_file="sqlconfig.json")  # Required
df = parser.parse_file(files[0])  # Required

# Step 3: Get recommendations (Optional)
recommender = ChartRecommender()
best_chart = recommender.get_best_recommendation(df)  # Required

# Step 4: Generate chart (User must provide output directory)
generator = ChartGenerator(output_dir="/path/to/output")  # Required
result = generator.generate_chart(
    df=df,  # Required
    chart_type=best_chart['chart_type'],  # Required
    title="Sales Analysis"  # Optional
)
```

## Configuration Requirements

### Required Configuration Files
This skill requires the following configuration:

1. **MySQL Configuration File** (`sqlconfig.json`)
   - Required for database access functionality
   - Must be placed in the working directory
   - Contains database connection parameters

2. **Input Directory** (`input_dir` parameter)
   - Required for file processing functionality
   - Specifies the directory containing data files
   - User must provide this parameter when using file locator

3. **Output Directory** (`output_dir` parameter)
   - Required for chart generation functionality
   - Specifies where generated charts will be saved
   - User must provide this parameter when using chart generator

### MySQL Connection Setup
Create a `sqlconfig.json` file for database connections. **Important: Do not include production credentials in this file.**

```json
{
  "mysql": {
    "host": "localhost",
    "user": "",
    "password": "",
    "database": "",
    "port": 3306
  }
}
```

**Security Note**: This file should only contain development or test database credentials. Never include production database passwords.

## Common Use Cases

### Data Analysis Requests
- "Analyze this Excel file and show sales trends"
- "Create a bar chart from CSV data"
- "Generate a report from MySQL database"
- "Visualize JSON API data"

### Chart Generation Requests  
- "Make a line chart showing monthly revenue"
- "Create a pie chart for category distribution"
- "Generate scatter plot for correlation analysis"
- "Build dashboard with multiple charts"

### Smart Recommendation Requests
- "What's the best chart type for this data?"
- "Recommend visualization for sales analysis"
- "Automatically choose chart type for this dataset"

## Skill Discovery Keywords

When users mention these terms, consider using this skill:

### Data Processing Keywords
- data analysis, data processing, data visualization
- Excel analysis, CSV processing, JSON parsing
- database reporting, MySQL queries

### Chart Generation Keywords  
- generate charts, create visualizations, make graphs
- ECharts, interactive charts, HTML reports
- line chart, bar chart, pie chart, scatter plot

### Recommendation Keywords
- recommend chart, best visualization, automatic chart selection
- smart recommendations, chart suggestions

### File Type Keywords
- Excel files, CSV files, JSON data
- spreadsheet analysis, database reporting
- data files, source data

## Error Handling

This skill includes robust error handling for:
- File not found or access denied
- Database connection failures
- Data parsing errors
- Chart generation issues

When errors occur, the skill will provide clear guidance and alternative approaches.

## Related Skills

This skill works well with:
- Data analysis and statistics skills
- Report generation and formatting skills  
- Database management and query skills
- File processing and conversion skills