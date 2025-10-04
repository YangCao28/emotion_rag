#!/usr/bin/env python3
"""
测试多图像处理的脚本
"""

import json
import requests
import time

def test_multiple_images():
    """测试多图像消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-multi-images",
        "text": "请描述这些图片中的内容，并比较它们的差异",
        "attachments": [
            {
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "filename": "图片1.jpg",
                "type": "image/jpeg",
                "size": 150000
            },
            {
                "url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg",
                "filename": "图片2.jpg", 
                "type": "image/jpeg",
                "size": 120000
            },
            {
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "filename": "图片3.jpg",
                "type": "image/jpeg", 
                "size": 180000
            }
        ],
        "has_attachments": True
    }
    
    print("测试多图像消息...")
    print(f"图像数量: {len(payload['attachments'])}")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)  # 增加超时时间
        response.raise_for_status()
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_mixed_attachments():
    """测试混合附件类型（包含非图像文件）"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-mixed-attachments",
        "text": "请只看图片，忽略其他类型的文件",
        "attachments": [
            {
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "filename": "图片.jpg",
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
                "url": "https://example.com/video.mp4",
                "filename": "视频.mp4",
                "type": "video/mp4",
                "size": 500000
            }
        ],
        "has_attachments": True
    }
    
    print("\n测试混合附件类型...")
    print(f"总附件数量: {len(payload['attachments'])}")
    image_count = sum(1 for att in payload['attachments'] if att['type'].startswith('image/'))
    print(f"图像附件数量: {image_count}")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("=" * 60)
    print("多图像处理测试")
    print("=" * 60)
    
    # 测试多图像
    print("\n" + "=" * 40)
    success1 = test_multiple_images()
    
    # 测试混合附件
    print("\n" + "=" * 40)
    success2 = test_mixed_attachments()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"多图像测试: {'✓ 通过' if success1 else '✗ 失败'}")
    print(f"混合附件测试: {'✓ 通过' if success2 else '✗ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()