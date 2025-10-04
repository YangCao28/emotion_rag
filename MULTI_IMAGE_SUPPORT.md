# 多图像处理说明

## 概述

当前系统完全支持多图像输入处理。当 API 接收到包含多个图像 URL 的请求时，系统会：

1. **自动识别图像附件**：从所有附件中筛选出图像类型文件
2. **构建多模态内容**：将所有图像添加到用户消息中
3. **发送到 Qwen API**：使用 OpenAI 兼容格式发送包含多图像的请求
4. **获取综合响应**：模型会分析所有图像并给出综合回答

## 支持的场景

### 1. 多图像分析
```json
{
  "message_id": "multi-001",
  "text": "请比较这些图片的异同",
  "attachments": [
    {
      "url": "https://example.com/image1.jpg",
      "filename": "图片1.jpg",
      "type": "image/jpeg",
      "size": 150000
    },
    {
      "url": "https://example.com/image2.jpg", 
      "filename": "图片2.jpg",
      "type": "image/jpeg",
      "size": 120000
    },
    {
      "url": "https://example.com/image3.jpg",
      "filename": "图片3.jpg",
      "type": "image/png",
      "size": 180000
    }
  ],
  "has_attachments": true
}
```

### 2. 混合附件类型
```json
{
  "message_id": "mixed-001",
  "text": "请只分析图片，忽略其他文件",
  "attachments": [
    {
      "url": "https://example.com/photo.jpg",
      "filename": "照片.jpg",
      "type": "image/jpeg",
      "size": 150000
    },
    {
      "url": "https://example.com/document.pdf",
      "filename": "文档.pdf", 
      "type": "application/pdf",
      "size": 50000
    },
    {
      "url": "https://example.com/chart.png",
      "filename": "图表.png",
      "type": "image/png",
      "size": 80000
    }
  ],
  "has_attachments": true
}
```

## 处理流程

### 1. 附件筛选
```python
# 系统会自动分离图像和非图像附件
image_attachments = []
non_image_attachments = []

for attachment in attachments:
    if attachment.get("type", "").startswith("image/"):
        image_attachments.append(attachment)
    else:
        non_image_attachments.append(attachment)
```

### 2. 消息构建
```python
# 为每个图像创建一个内容项
user_content_parts = [
    {
        "type": "text",
        "text": "【用户输入】：{user_input}\n【你可以参考的资料】：{doc_text}"
    }
]

# 添加所有图像
for attachment in image_attachments:
    user_content_parts.append({
        "type": "image",
        "image": attachment.get("url", "")
    })
```

### 3. API 调用
```python
# 转换为 OpenAI 兼容格式
openai_content = []
for item in content:
    if item["type"] == "text":
        openai_content.append({
            "type": "text",
            "text": item["text"]
        })
    elif item["type"] == "image":
        openai_content.append({
            "type": "image_url",
            "image_url": {
                "url": item["image"]
            }
        })
```

## 日志输出示例

### 多图像处理日志
```
[2025-10-01 10:30:15] INFO - Processing 3 attachments
[2025-10-01 10:30:15] INFO - Found 2 image attachments: ['https://example.com/image1.jpg...', 'https://example.com/image2.jpg...']
[2025-10-01 10:30:15] INFO - Ignoring 1 non-image attachments
[2025-10-01 10:30:15] INFO - Built messages with user input length 25, 150 chars docs, and 2 images
[2025-10-01 10:30:15] INFO - Calling Qwen API with 2 messages
[2025-10-01 10:30:15] INFO - Sending request to Qwen API via OpenAI compatible mode with 2 images
[2025-10-01 10:30:18] INFO - Received response from Qwen API: chatcmpl-xxx
```

## 技术限制

### 1. 模型限制
- **Qwen VL Max**: 支持多图像输入
- **最大图像数**: 建议不超过10张图像
- **图像大小**: 每张图像建议不超过10MB
- **分辨率**: 建议不超过2048x2048

### 2. API 限制
- **请求超时**: 多图像请求可能需要更长处理时间
- **费用**: 每张图像都会产生额外费用
- **并发**: 多图像请求对API配额消耗更大

### 3. 网络限制
- **图像可访问性**: 所有图像URL必须公网可访问
- **加载时间**: 多个图像的加载可能影响响应时间

## 最佳实践

### 1. 图像优化
- 使用CDN加速图像访问
- 压缩图像以减少加载时间
- 确保图像URL的稳定性

### 2. 请求优化
- 合理控制图像数量（建议3-5张）
- 设置合适的超时时间
- 添加重试机制

### 3. 错误处理
- 检查图像URL的有效性
- 处理图像加载失败的情况
- 提供降级方案（纯文本模式）

## 测试

运行多图像测试脚本：
```bash
python test_multiple_images.py
```

该脚本会测试：
- 多图像处理能力
- 混合附件类型处理
- 日志输出验证

## 总结

当前系统已经完全支持多图像处理：

✅ **支持多图像输入**
✅ **自动过滤非图像附件** 
✅ **OpenAI兼容格式转换**
✅ **详细的日志记录**
✅ **错误处理和降级**

系统会自动处理1张到多张图像的所有情况，无需额外配置。