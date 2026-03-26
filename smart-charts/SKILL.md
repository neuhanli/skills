---
name: "smart-charts"
description: "Intelligent chart generation and data analysis skill. Reads user-supplied data files (CSV/Excel/JSON), analyzes data characteristics with LLM assistance, auto-recommends and generates interactive ECharts visualizations, and produces a structured analysis report. Suitable for any scenario requiring tabular data visualization — sales reports, business dashboards, trend analysis, etc."
---

# Smart Charts

An intelligent chart-generation and data-analysis skill. It reads user-supplied data files, understands their structure and semantics, recommends the most appropriate chart types, generates interactive HTML reports powered by ECharts, and (when a saved report template exists) fills the template automatically.

---

## Installation / 安装

```bash
pip install -r requirements.txt
```

### Dependencies / 依赖

| Package | Required | Description |
|---------|----------|-------------|
| `pandas>=1.5.0` | ✅ Yes | Data parsing (CSV, Excel, JSON) |
| `numpy>=1.21.0` | ✅ Yes | Numerical computations |
| `openpyxl>=3.0.0` | ✅ Yes | Excel file engine |
| `PyPDF2>=3.0.0` | Optional | PDF template extraction |
| `python-docx>=0.8.0` | Optional | Word template processing |

> ECharts is loaded via CDN (`jsdelivr`) — no local installation required.

---

## Activation Triggers

Load and run this skill when **any** of the following conditions are met:

- The user mentions: "analyze data", "generate chart", "data visualization", "chart", "visualization"  
  / 用户提到：「分析数据」「生成图表」「数据可视化」「chart」「visualization」
- The user provides a data file (CSV / Excel / JSON / TXT) and asks for analysis or visualization  
  / 用户上传或提供数据文件并要求分析或可视化
- The user asks to generate charts or a report from tabular data  
  / 用户要求从表格数据生成图表或报告

---

## User Guidance

### When no data file is provided

Prompt the user:

> Please upload the data file(s) you want to analyze. Supported formats:
> - **CSV** (.csv / .tsv / .txt)
> - **Excel** (.xlsx / .xls)
> - **JSON** (.json)
>
> You can drag files directly into the chat box. **Multiple files are supported.**

/ 请上传需要分析的数据文件。支持 CSV / Excel / JSON 格式，可同时上传多个文件。

### When data files are provided

**Step 1 — Parse and display a unified summary:**

> Files loaded: 3
>
> | File | Rows | Cols | Key Fields |
> |------|------|------|------------|
> | east_sales.csv | 120 | 8 | date, revenue, profit… |
> | south_sales.csv | 98 | 8 | date, revenue, profit… |
> | products.xlsx | 45 | 5 | name, category, price… |

**Step 2 — Infer file relationships and recommend an analysis strategy:**

| Situation | Recommendation |
|-----------|----------------|
| Same schema across files | Merge and compare |
| Shared common column(s) | Join on the common key |
| Unrelated schemas | Analyze each file separately |
| Single file | Analyze directly |

**Step 3 — Execute after user confirmation.**

### Error handling

| Error | User message |
|-------|--------------|
| File not found | "File not found. Please verify the path or drag the file into the chat." |
| Unsupported format | "Unsupported file format. Please convert to CSV, Excel, or JSON and retry." |
| File > 100 MB | "File too large. Consider filtering or splitting the data before uploading." |
| Empty file | "The file appears to be empty. Please check that it contains valid data." |
| Encoding error | "Encoding issue detected. Try re-saving the file as CSV (UTF-8) and retry." |
| Cannot auto-merge | "Schemas differ too much to merge automatically. Analyze separately, or specify a join key." |

---

## Execution Workflow

```
1. Obtain data file(s)
   └─ User uploads file(s) directly (primary method)
   └─ Or user provides file path(s)

2. Parse data
   └─ Call data_parser.py on all files
   └─ Single file  → parse directly
   └─ Multiple files → parse each, assess merge feasibility

3. Confirm & recommend
   └─ Display a summary table for all files
   └─ Recommend: merge / separate / join
   └─ Recommend chart type(s) based on data characteristics

4. Generate charts
   └─ Call chart_generator.py → produces ECharts HTML
   └─ Merged data  → cross-group comparison charts
   └─ Separate data → independent charts per file
   └─ Chart type is chosen by the LLM based on data shape

5. Check for a report template
   └─ Scan the templates/ subdirectory under the skill base
   └─ Read each meta.json; let the LLM judge relevance
   └─ No matching template → skip to free-form generation

6. Generate analysis report
   └─ Matching template found → fill template.md with data insights
   └─ No matching template    → LLM generates report freely

7. Present results
   └─ Interactive charts: use preview_url (HTML)
   └─ Markdown report:    use open_result_view
```

---

## Configuration

```yaml
output_dir:    output directory (optional; default: ./smart_charts_output)
templates_dir: report template directory (optional; default: ./templates)
```

> **Important:** Never hard-code absolute paths. All paths must be provided by the user or resolved dynamically from the working directory.

---

## Data Parsing — CLI Reference

### Usage / 调用方式

```bash
# Single file / 单文件
python {skill_base}/core/data_parser.py <file_path> [--summary]

# Multiple files / 多文件
python {skill_base}/core/data_parser.py <file1> <file2> ... [--summary]

# Multiple files with auto-merge / 多文件自动合并
python {skill_base}/core/data_parser.py <file1> <file2> ... [--merge] [--summary]
```

**Merge behavior:**

| Condition | Result |
|-----------|--------|
| Identical column names | Vertical concat; a `source_file` column is added |
| Shared columns exist | Horizontal join on shared key |
| No common structure | Error — advise analyzing separately |

### Supported formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| CSV | .csv, .tsv | Auto-detects delimiter and encoding (UTF-8 / GBK / GB2312) |
| Plain text | .txt | Auto-detects delimiter (comma / tab / semicolon / pipe) |
| Excel | .xlsx, .xls | Reads first non-empty sheet |
| JSON | .json | Supports array format and nested objects |

---

## Chart Generation — CLI Reference

### Usage / 调用方式

```bash
python {skill_base}/core/chart_generator.py \
  <file_path> <chart_type> \
  --title "Chart Title" \
  --x-axis "date" \
  --y-axis "revenue profit" \
  --output-dir "./output"
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `file_path` | Yes | Path to the data file |
| `chart_type` | Yes | Chart type identifier (see table below) |
| `--title` | No | Chart title; default: "Data Chart" |
| `--x-axis` | No | X-axis field; auto-detected if omitted |
| `--y-axis` | No | Y-axis field(s), space-separated; defaults to first 5 numeric columns |
| `--output-dir` | No | Output directory; default: `./smart_charts_output` |

### Supported chart types

| ID | Name | Best For |
|----|------|----------|
| `line` | Line chart | Time-series trends, continuous data |
| `bar` | Bar chart | Category comparison, ranked discrete data |
| `pie` | Pie chart | Composition, share distribution |
| `scatter` | Scatter plot | Correlation, density distribution |
| `area` | Area chart | Cumulative change, emphasized trend |
| `radar` | Radar chart | Multi-dimension comparison, scoring |
| `heatmap` | Heatmap | Density, cross-tabulation analysis |
| `treemap` | Treemap | Hierarchical proportion, attribution |
| `graph` | Network graph | Entity relationships, network topology |
| `boxplot` | Box plot | Distribution, outlier detection |
| `waterfall` | Waterfall chart | Incremental change, contribution breakdown |
| `gauge` | Gauge chart | KPI progress, target tracking |
| `sankey` | Sankey diagram | Flow transfer, conversion path |
| `funnel` | Funnel chart | Conversion rate, stage analysis |
| `sunburst` | Sunburst chart | Multi-level composition, nested proportion |
| `wordcloud` | Word cloud | Frequency distribution, keyword visualization |

---

## Report Templates

Users can store custom report templates under the `templates_dir` directory.

### Directory structure

```
templates/
├── _template_index.json         # Auto-generated metadata index
├── sales_report/
│   ├── meta.json                # Template metadata card
│   ├── template.md              # Template content
│   └── original.docx            # Source file (optional)
└── project_progress/
    ├── meta.json
    └── template.md
```

### meta.json schema

```json
{
  "id": "tmpl_sales_monthly",
  "name": "Monthly Sales Report",
  "description": "For monthly sales summaries: revenue trend, top products, regional breakdown.",
  "scenarios": ["monthly sales report", "sales performance review", "quarterly comparison"],
  "variables": ["period", "revenue", "profit", "order_count", "mom_growth", "yoy_growth"],
  "categories": ["sales", "finance", "business analysis"],
  "format": "markdown",
  "created_time": "2026-03-26T10:30:00",
  "modified_time": "2026-03-26T10:30:00"
}
```

### LLM-driven template matching

**Core principle: template matching is performed by the LLM, not by hard-coded algorithms.**

#### Step 1 — Discover templates and collect metadata
```python
template_summary = template_manager.get_all_templates_summary()
```

#### Step 2 — LLM analyzes the user task
```
User task: "Analyze this month's sales data and generate a report."
LLM reasoning:
  - Keywords: sales, data, report, monthly
  - Task type: data analysis, report generation
  - Data characteristics: sales metrics, time series, KPIs
```

#### Step 3 — LLM selects the best-matching template
```
Templates available:
  tmpl_sales_monthly    → Monthly Sales Report
  tmpl_financial_report → Financial Report
  tmpl_project_progress → Project Progress

Best match: tmpl_sales_monthly
Reason: scenario match (sales), variable overlap (revenue, profit…)
```

#### Step 4 — Load template and fill with data insights
```python
template_content = template_manager.get_template_content("tmpl_sales_monthly")
filled_report = fill_template_variables(template_content, data_insights)
```

#### Fallback behavior (no match)

| Scenario | Behavior |
|----------|----------|
| No suitable template | LLM generates report freely |
| Partial match | LLM uses template structure as reference, generates the rest |
| Empty template library | LLM creates a professional report from scratch |

### Template variable syntax (auto-detected)

| Format | Example |
|--------|---------|
| Single braces | `{variable_name}` |
| Double braces | `{{variable_name}}` |
| Square brackets | `[variable_name]` |
| Percent signs | `%variable_name%` |

---

## Template Management

### Supported template formats

| Format | Extension | Processing |
|--------|-----------|-----------|
| Markdown | .md, .markdown | Native support |
| Word | .docx | Extracts text and preserves formatting |
| PDF | .pdf | Extracts text and structure |
| Plain text | .txt | Simple template parsing |

### Operations / 操作指令

#### Upload / Save a template
- Triggers: `upload template`, `add template`, `save template`  
  / 触发词：`上传模板`、`添加模板`、`保存模板`

```
User: Save this sales report as a template.
AI:   ✅ Template saved: "Sales Report" (Markdown, 8 variables detected)
```

#### View template library
- Triggers: `my templates`, `template list`, `show templates`  
  / 触发词：`我的模板`、`模板列表`、`查看模板`

```
User: Show my templates.
AI:   📋 Your templates (3):
      1. Monthly Sales Report (Markdown) — monthly sales analysis
      2. Project Progress (Word) — project tracking
      3. Financial Report (PDF) — financial analysis
```

#### Auto-matching (seamless)
```
User: Analyze this month's sales data.
AI:   🎯 Matched template: "Monthly Sales Report"
      📊 Auto-filling variables: revenue, profit, growth rate
      📄 Generating professional report…
```

### Template management error handling

| Error | User message | Suggested action |
|-------|-------------|-----------------|
| Unsupported format | "Supported formats: PDF, Word, Markdown." | Convert and retry |
| Template already exists | "Template 'Sales Report' already exists." | Overwrite, rename, or cancel |
| No match found | "No exact template match found." | Use generic template or create new |
| Missing variables | "Data missing: revenue, profit." | Check data file or use defaults |

---

## Key Principles

1. **Multi-file first** — Users often upload multiple files. Guide proactively; handle batches gracefully.
2. **Confirm before executing** — Always show a data summary and confirm understanding before recommending analysis direction.
3. **LLM chooses chart types** — Recommend based on data semantics; never hard-code mapping rules.
4. **Template-first report generation** — Use a saved template when a good match exists; fall back to free-form only when necessary.
5. **Dynamic path resolution** — Absolute paths must never be hard-coded; resolve all paths at runtime.
6. **Immediate result presentation** — Charts via `preview_url`; Markdown reports via `open_result_view`.
