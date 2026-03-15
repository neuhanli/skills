# TencentHotSearch Skill

基于腾讯云联网搜索 API（SearchPro）的热点搜索工具，支持全网搜索或指定站点搜索，获取关键词相关的热门文章和新闻资讯。

**API 信息:**
- **接口域名**: wsa.tencentcloudapi.com
- **接口版本**: 2025-05-08
- **接口名称**: SearchPro

## 功能特性

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

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/neuhanli/skills.git
cd skills/TencentHotSearch-skill
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制配置模板并填写您的 API 密钥：

```bash
cp config.example.json config.json
```

编辑 `config.json`，填入您的腾讯云 API 密钥：

```json
{
  "secret_id": "YOUR_TENCENT_CLOUD_SECRET_ID",
  "secret_key": "YOUR_TENCENT_CLOUD_SECRET_KEY",
  "output_dir": "./output"
}
```

详细配置步骤请参考 [CONFIG.md](CONFIG.md)

### 4. 运行搜索

#### 命令行使用

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

## 命令行参数

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

## 使用示例

### 示例 1: 全网搜索 AI 相关新闻

```bash
python scripts/tencent_hotsearch.py 人工智能 AI技术 -l 15 -o ai_news.md
```

### 示例 2: 在腾讯网搜索科技资讯

```bash
python scripts/tencent_hotsearch.py 科技 创新 -s qq.com -l 20 -f json
```

### 示例 3: 在新闻频道搜索财经新闻

```bash
python scripts/tencent_hotsearch.py 财经 股市 -s news.qq.com --print
```

### 示例 4: 多关键词搜索

```bash
python scripts/tencent_hotsearch.py 区块链 Web3 加密货币 -l 10 -f csv
```

### 示例 5: 按时间范围搜索

```bash
python scripts/tencent_hotsearch.py 人工智能 --from-time 1704067200 --to-time 1706745600 -l 30
```

### 示例 6: 使用混合模式搜索

```bash
python scripts/tencent_hotsearch.py 人工智能 -m 2 -l 20 -o results.md
```

## 输出格式

### Markdown 格式 (默认)

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

### JSON 格式

结构化数据，适合程序处理和数据分析。

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
  "timestamp": "2024-01-15T10:30:00"
}
```

### CSV 格式

表格格式，适合 Excel 等工具打开进行数据分析。

### TXT 格式

纯文本格式，适合快速阅读和复制粘贴。

## 搜索模式说明

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

## 行业过滤 (尊享版)

| 值 | 说明 |
|----|------|
| gov | 党政机关 |
| news | 权威媒体 |
| acad | 学术（英文） |
| finance | 金融 |

## API 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 结果标题 |
| summary | string | 标准摘要 |
| dynamic_summary | string | 动态摘要（尊享版） |
| source | string | 网站名称 |
| publishTime | string | 内容发布时间 |
| url | string | 内容发布源 URL |
| score | float | 相关性得分（0～1） |
| images | array | 图片列表 |
| favicon | string | 网站图标链接 |

## 配置文件说明

### config.json 结构

```json
{
  "secret_id": "YOUR_TENCENT_CLOUD_SECRET_ID",
  "secret_key": "YOUR_TENCENT_CLOUD_SECRET_KEY",
  "output_dir": "./output"
}
```

### 配置参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secret_id | string | 是 | 腾讯云 API 密钥 ID |
| secret_key | string | 是 | 腾讯云 API 密钥 Key |
| output_dir | string | 否 | 默认输出目录，默认为 ./output |

## 依赖

- Python 3.7+
- tencentcloud-sdk-python
- pandas (用于 CSV 导出)

## 注意事项

- 关键词数量限制：1-5 个
- 结果数量限制：10/20/30/40/50（尊享版支持到 50）
- 时间戳格式：Unix 时间戳（秒）
- 行业过滤仅尊享版支持
- 动态摘要仅尊享版支持
- Mode 1 模式下，Site、FromTime、ToTime、Industry 参数无效

## 错误处理

- **配置文件不存在**: 提示创建 config.json 文件
- **API 认证失败**: 检查 SecretId 和 SecretKey 是否正确
- **网络错误**: 检查网络连接和 API 服务状态
- **参数错误**: 检查关键词数量、时间戳格式等

## 许可证

MIT License

## 作者

Created for Agent Skills platform
