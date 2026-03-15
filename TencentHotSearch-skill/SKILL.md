---
name: "TencentHotSearch-skill"
description: "Fetches trending news and articles using Tencent Cloud Online Search API (SearchPro). Supports searching across the entire web or within specific sites, with multiple output formats (JSON, CSV, TXT, MD). Invoke when user wants to get hot news, trending topics, or search for articles on specific keywords using Tencent Cloud services."
---

# TencentHotSearch Skill

## Overview

TencentHotSearch-skill 是一个基于腾讯云联网搜索 API（SearchPro）的热点搜索工具，支持全网搜索或指定站点搜索，获取关键词相关的热门文章和新闻资讯。

**API 信息:**
- **接口域名**: wsa.tencentcloudapi.com
- **接口版本**: 2025-05-08
- **接口名称**: SearchPro

## Features

- **多关键词搜索**: 支持输入 1-5 个关键词进行组合搜索
- **站点指定**: 可选择全网搜索或指定站点搜索（如腾讯网 qq.com、新闻频道 news.qq.com 等）
- **多种搜索模式**: 
  - 自然检索结果 (Mode=0, 默认)
  - 多模态VR结果 (Mode=1)
  - 混合结果 (Mode=2)
- **时间过滤**: 支持按起始时间和结束时间过滤结果
- **行业过滤**: 支持按行业过滤（gov/news/acad/finance，尊享版）
- **结构化结果**: 返回包含标题、摘要、动态摘要、来源平台、发布时间、原文链接、相关度得分、图片列表等完整信息
- **多格式输出**: 支持 JSON、CSV、TXT、MD 格式输出（默认 MD）
- **自定义输出路径**: 支持在配置文件中设置默认输出目录
- **合规安全**: 所有数据通过腾讯官方 API 合规获取

## When to Use

当用户有以下需求时，应调用此 skill：
- 想要获取某个领域的热点新闻或 trending topics
- 需要搜索特定关键词相关的最新文章
- 想要追踪热门事件或策划选题
- 需要快速掌握某个领域的动态
- 需要在特定站点内搜索内容（如腾讯网、新闻频道等）
- 需要按时间范围或行业筛选搜索结果

## Usage

### Quick Start (Command Line)

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 配置腾讯云 API
编辑 `config.json` 文件，填入您的腾讯云 API 密钥：
```json
{
  "secret_id": "YOUR_TENCENT_CLOUD_SECRET_ID",
  "secret_key": "YOUR_TENCENT_CLOUD_SECRET_KEY",
  "output_dir": "./output"
}
```

详细配置说明请参考 [CONFIG.md](CONFIG.md)

#### 3. 运行搜索
```bash
# 全网搜索（默认模式，输出为 MD 格式）
python scripts/tencent_hotsearch.py 人工智能 AI技术 -l 10

# 指定站点搜索（腾讯网）
python scripts/tencent_hotsearch.py 人工智能 AI技术 -s qq.com -l 10

# 指定站点搜索（新闻频道）
python scripts/tencent_hotsearch.py 科技 创新 -s news.qq.com -l 15

# 使用多模态VR模式搜索
python scripts/tencent_hotsearch.py 人工智能 -m 1 -l 10

# 使用混合模式搜索
python scripts/tencent_hotsearch.py 人工智能 -m 2 -l 20

# 按时间范围搜索
python scripts/tencent_hotsearch.py 人工智能 --from-time 1704067200 --to-time 1706745600

# 按行业过滤（尊享版）
python scripts/tencent_hotsearch.py 人工智能 --industry news -l 20

# 保存结果到指定文件
python scripts/tencent_hotsearch.py 人工智能 AI技术 -o results.md

# 保存结果到 JSON 文件
python scripts/tencent_hotsearch.py 人工智能 AI技术 -o results.json -f json

# 保存结果到 CSV 文件
python scripts/tencent_hotsearch.py 人工智能 AI技术 -o results.csv -f csv

# 保存结果到 TXT 文件
python scripts/tencent_hotsearch.py 人工智能 AI技术 -o results.txt -f txt

# 打印结果到控制台
python scripts/tencent_hotsearch.py 人工智能 AI技术 --print

# 自定义存储路径（相对路径）
python scripts/tencent_hotsearch.py 人工智能 -o output/ai_results.txt -f txt

# 自定义存储路径（绝对路径）
python scripts/tencent_hotsearch.py 科技 -o /path/to/your/output/tech_news.md -f md
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keywords | array[string] | 是 | 1-5 个搜索关键词 |
| site | string | 否 | 指定搜索站点（如 qq.com、news.qq.com），不指定则全网搜索 |
| mode | integer | 否 | 搜索模式：0-自然检索(默认)，1-多模态VR，2-混合结果 |
| limit | integer | 否 | 返回结果数量，默认 10，可选：10/20/30/40/50 |
| from_time | integer | 否 | 起始时间过滤（Unix 时间戳，秒） |
| to_time | integer | 否 | 结束时间过滤（Unix 时间戳，秒） |
| industry | string | 否 | 行业过滤：gov/news/acad/finance（尊享版） |

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keywords` | 搜索关键词（1-5个） | - |
| `-s, --site` | 指定搜索站点（如 qq.com） | 全网搜索 |
| `-m, --mode` | 搜索模式 (0/1/2) | 0 |
| `-l, --limit` | 结果数量 (10/20/30/40/50) | 10 |
| `--from-time` | 起始时间 (Unix 时间戳) | - |
| `--to-time` | 结束时间 (Unix 时间戳) | - |
| `--industry` | 行业过滤 (gov/news/acad/finance) | - |
| `-c, --config` | 配置文件路径 | config.json |
| `-o, --output` | 输出文件路径 | - |
| `-f, --format` | 输出格式 (json/csv/txt/md) | md |
| `--print` | 打印结果到控制台 | False |

### 示例

```json
{
  "keywords": ["人工智能", "AI技术"],
  "site": "qq.com",
  "mode": 0,
  "limit": 10,
  "from_time": 1704067200,
  "to_time": 1706745600,
  "industry": "news"
}
```

### 返回结果格式

```json
{
  "results": [
    {
      "title": "文章标题",
      "summary": "标准摘要...",
      "dynamic_summary": "动态摘要（尊享版）...",
      "source": "来源平台",
      "publishTime": "2024-01-15 10:30:00",
      "url": "https://example.com/article",
      "score": 0.8978,
      "images": ["https://example.com/image1.jpg"],
      "favicon": "https://example.com/favicon.ico"
    }
  ],
  "total": 10,
  "query": {
    "keywords": ["人工智能", "AI技术"],
    "site": "qq.com",
    "mode": 0
  }
}
```

## API Configuration

### 腾讯云联网搜索 API

#### 获取步骤

1. 访问 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 登录您的腾讯云账户
3. 进入"产品" -> "人工智能" -> "联网搜索"
4. 开通服务并获取 API 密钥（SecretId 和 SecretKey）
5. 选择合适的区域（如 ap-guangzhou）

#### 配置参数

| 参数 | 说明 | 示例 |
|------|------|------|
| secret_id | 腾讯云 API 密钥 ID | AKIDxxxxxxxxxxxxxxxx |
| secret_key | 腾讯云 API 密钥 Key | xxxxxxxxxxxxxxxx |
| output_dir | 默认输出目录 | ./output |

## Output Formats

### 1. Markdown 格式 (默认)

适合在 Markdown 编辑器中查看，包含格式化的标题、链接和元数据。

```markdown
# Search Results

**Total results:** 10
**Timestamp:** 2024-01-15T10:30:00

---

## 1. 文章标题

**摘要:** 内容摘要...

**动态摘要:** 动态摘要内容...

**来源:** 来源平台

**时间:** 2024-01-15 10:30:00

**链接:** [https://example.com/article](https://example.com/article)

**相关度:** 0.8978

---
```

### 2. JSON 格式

结构化数据，适合程序处理和数据分析。

```json
{
  "results": [...],
  "total": 10,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. CSV 格式

表格格式，适合 Excel 等工具打开进行数据分析。

### 4. TXT 格式

纯文本格式，适合快速阅读和复制粘贴。

## Search Modes

### Mode 0: 自然检索结果 (默认)
- 返回传统的网页搜索结果
- 支持 Site、FromTime、ToTime、Industry 等过滤参数
- 适合常规搜索需求

### Mode 1: 多模态VR结果
- 返回多模态VR搜索结果
- **注意**: Site、FromTime、ToTime、Industry 参数在此模式下无效
- 适合需要富媒体内容的场景

### Mode 2: 混合结果
- 返回多模态VR结果 + 自然检索结果的混合
- Site、FromTime、ToTime、Industry 参数仅对自然结果生效
- 适合需要全面搜索结果的场景

## Industry Filters (尊享版)

| 值 | 说明 |
|----|------|
| gov | 党政机关 |
| news | 权威媒体 |
| acad | 学术（英文） |
| finance | 金融 |

## Dependencies

- Python 3.7+
- tencentcloud-sdk-python
- pandas (用于 CSV 导出)

## Installation

```bash
# 克隆仓库
git clone https://github.com/neuhanli/skills.git
cd skills/TencentHotSearch-skill

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp config.example.json config.json
# 编辑 config.json 填入您的 API 密钥
```

## Error Handling

- **配置文件不存在**: 提示创建 config.json 文件
- **API 认证失败**: 检查 SecretId 和 SecretKey 是否正确
- **网络错误**: 检查网络连接和 API 服务状态
- **参数错误**: 检查关键词数量、时间戳格式等

## Notes

- 关键词数量限制：1-5 个
- 结果数量限制：10/20/30/40/50（尊享版支持到 50）
- 时间戳格式：Unix 时间戳（秒）
- 行业过滤仅尊享版支持
- 动态摘要仅尊享版支持

## License

MIT License

## Author

Created for Agent Skills platform
