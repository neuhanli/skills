# 配置说明

## 腾讯云 API 密钥配置

在使用 TencentCloud-HotSearch-skill 之前，您需要配置腾讯云联网搜索 API（SearchPro）的密钥。腾讯云联网搜索 API 使用 **SecretId** 和 **SecretKey** 进行认证。

**API 信息:**
- **接口域名**: wsa.tencentcloudapi.com
- **接口版本**: 2025-05-08
- **接口名称**: SearchPro

## 获取腾讯云 API 密钥

### 步骤 1: 注册/登录腾讯云账户

1. 访问 [腾讯云官网](https://cloud.tencent.com/)
2. 点击右上角的"注册"或"登录"
3. 如果是新用户，完成注册流程
4. 登录您的腾讯云账户

### 步骤 2: 开通联网搜索服务

1. 登录后，访问 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 在搜索框中输入"联网搜索"
3. 点击进入"联网搜索"产品页面
4. 点击"立即开通"按钮
5. 阅读并同意服务协议
6. 完成开通流程

### 步骤 3: 获取 API 密钥

#### 获取 SecretId 和 SecretKey

1. 访问 [腾讯云访问管理控制台](https://console.cloud.tencent.com/cam/capi)
2. 点击"新建密钥"按钮
3. 系统会生成一对密钥：
   - **SecretId**: 密钥 ID（格式类似：AKIDxxxxxxxxxxxxxxxx）
   - **SecretKey**: 密钥 Key（格式类似：xxxxxxxxxxxxxxxx）
4. **重要**: 请立即保存这两个密钥，SecretKey 只显示一次！

#### 通过联网搜索产品获取

1. 进入 [联网搜索控制台](https://console.cloud.tencent.com/ais)
2. 在左侧导航栏选择"API 密钥管理"
3. 点击"创建密钥"
4. 复制生成的 SecretId 和 SecretKey

## 配置文件说明

### config.json 文件结构

```json
{
  "secret_id": "YOUR_TENCENT_CLOUD_SECRET_ID",
  "secret_key": "YOUR_TENCENT_CLOUD_SECRET_KEY",
  "output_dir": "./output"
}
```

### 配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secret_id | string | 是 | 腾讯云 API 密钥 SecretId |
| secret_key | string | 是 | 腾讯云 API 密钥 SecretKey |
| output_dir | string | 否 | 默认输出目录，默认为 ./output |

## 配置步骤

### 1. 创建配置文件

如果 `config.json` 文件不存在，请从示例文件复制：

```bash
cp config.example.json config.json
```

### 2. 编辑配置文件

使用文本编辑器打开 `config.json`，填入您的 API 密钥：

```json
{
  "secret_id": "AKIDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "output_dir": "./output"
}
```

**注意事项：**
- 请确保 JSON 格式正确，不要有多余的逗号
- SecretId 和 SecretKey 需要用引号包裹
- 不要在配置文件中添加注释（JSON 不支持注释）
- `output_dir` 指定默认输出目录，如果未指定则使用 `./output`

## 安全建议

### 1. 保护 API 密钥

- ✅ **不要**将 `config.json` 提交到版本控制系统（Git）
- ✅ 使用 `.gitignore` 忽略 `config.json` 文件
- ✅ 定期轮换 API 密钥
- ✅ 为不同的环境使用不同的密钥

### 2. 配置文件权限

在 Linux/macOS 系统上，设置配置文件的访问权限：

```bash
chmod 600 config.json
```

这确保只有文件所有者可以读取和修改配置文件。

### 3. 环境变量（可选）

作为替代方案，您也可以使用环境变量来存储 API 密钥：

```bash
export TENCENT_CLOUD_SECRET_ID="your_secret_id"
export TENCENT_CLOUD_SECRET_KEY="your_secret_key"
export TENCENT_CLOUD_OUTPUT_DIR="./output"
```

然后修改代码以从环境变量读取密钥。

## 验证配置

配置完成后，您可以通过运行测试命令来验证配置是否正确：

```bash
python scripts/tencent_hotsearch.py 测试 -l 1 --print
```

如果配置正确，您应该能看到搜索结果。如果出现错误，请检查：

1. SecretId 和 SecretKey 是否正确填写
2. 网络连接是否正常
3. 腾讯云账户是否已开通联网搜索服务
4. API 密钥是否有足够的权限

## 输出目录配置

您可以在 `config.json` 中配置默认输出目录：

```json
{
  "secret_id": "AKIDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "output_dir": "/path/to/your/search_results"
}
```

支持以下路径格式：
- **相对路径**: `./output`, `../results`, `search_output`
- **绝对路径**: `/path/to/your/search_results`, `C:\Users\yourname\Documents\search_results`

如果未指定 `output_dir`，默认使用 `./output`。

## 常见问题

### Q1: SecretId 和 SecretKey 在哪里查看？

A: 访问 [腾讯云访问管理控制台](https://console.cloud.tencent.com/cam/capi)，点击"新建密钥"获取。注意 SecretKey 只显示一次，请妥善保存。

### Q2: SecretKey 忘记保存了怎么办？

A: 您可以删除旧密钥并创建新密钥。访问 [访问管理控制台](https://console.cloud.tencent.com/cam/capi)，删除旧密钥后创建新密钥。

### Q3: API 调用失败，提示认证失败？

A: 请检查：
- SecretId 和 SecretKey 是否正确复制（注意不要有多余的空格）
- SecretId 是否以 AKID 开头
- 账户是否有足够的余额或免费额度
- 账户是否已开通联网搜索服务

### Q4: 如何查看 API 调用次数和费用？

A: 访问 [腾讯云费用中心](https://console.cloud.tencent.com/expense/bill) 查看详细的调用记录和费用信息。

### Q5: 免费额度是多少？

A: 腾讯云联网搜索 API 提供一定的免费调用额度，具体额度请参考官方文档。超出免费额度后，按实际调用量计费。

### Q6: 如何提高 API 调用速度？

A: 
- 优化网络连接
- 使用 CDN 加速
- 合理设置并发请求数

### Q7: 输出目录不存在会怎样？

A: 程序会自动创建输出目录（包括所有父目录），无需手动创建。

### Q8: 可以同时指定输出路径和输出格式吗？

A: 可以。使用 `-o` 参数指定输出路径，使用 `-f` 参数指定输出格式。例如：

```bash
python scripts/tencent_hotsearch.py 人工智能 -o results.json -f json
```

## 相关链接

- [腾讯云联网搜索产品页](https://cloud.tencent.com/product/ais)
- [腾讯云联网搜索 API 文档](https://cloud.tencent.com/document/product/1139/46888)
- [腾讯云访问管理控制台](https://console.cloud.tencent.com/cam/capi)
- [腾讯云联网搜索控制台](https://console.cloud.tencent.com/ais)
- [腾讯云费用中心](https://console.cloud.tencent.com/expense/bill)

## 技术支持

如果您在配置过程中遇到问题：

1. 查看 [腾讯云文档中心](https://cloud.tencent.com/document/product)
2. 提交 [工单系统](https://console.cloud.tencent.com/workorder)
3. 联系腾讯云技术支持

---

**最后更新**: 2024年
