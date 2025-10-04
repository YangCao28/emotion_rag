#!/usr/bin/env python3
"""
测试合并后的 query_llm_with_prompt 功能
"""

import json
import requests
import time

def test_text_only():
    """测试纯文本消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-text-001",
        "text": "今天心情不好，需要安慰",
        "has_attachments": False
    }
    
    print("测试纯文本消息...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"Token使用: Prompt={result.get('prompt_tokens', 0)}, Completion={result.get('completion_tokens', 0)}, Total={result.get('total_tokens', 0)}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_single_image():
    """测试单图像消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-single-image",
        "text": "请描述这张图片的内容",
        "attachments": [
            {
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "filename": "图片.jpg",
                "type": "image/jpeg",
                "size": 150000
            }
        ],
        "has_attachments": True
    }
    
    print("\n测试单图像消息...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        print(f"Token使用: Prompt={result.get('prompt_tokens', 0)}, Completion={result.get('completion_tokens', 0)}, Total={result.get('total_tokens', 0)}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_multiple_images():
    """测试多图像消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-multi-images",
        "text": "请比较这些图片的内容和差异",
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
                "type": "image/png",
                "size": 180000
            }
        ],
        "has_attachments": True
    }
    
    print("\n测试多图像消息...")
    print(f"图像数量: {len(payload['attachments'])}")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)  # 增加超时时间
        response.raise_for_status()
        result = response.json()
        
        print(f"Token使用: Prompt={result.get('prompt_tokens', 0)}, Completion={result.get('completion_tokens', 0)}, Total={result.get('total_tokens', 0)}")
        print(f"处理的图像数量: {result.get('attachment_count', 0)}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_mixed_attachments():
    """测试混合附件类型"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-mixed",
        "text": "请只分析图片内容，忽略其他文件",
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
            }
        ],
        "has_attachments": True
    }
    
    print("\n测试混合附件类型...")
    image_count = sum(1 for att in payload['attachments'] if att['type'].startswith('image/'))
    print(f"总附件: {len(payload['attachments'])}, 图像: {image_count}")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        print(f"Token使用: Prompt={result.get('prompt_tokens', 0)}, Completion={result.get('completion_tokens', 0)}, Total={result.get('total_tokens', 0)}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("=" * 60)
    print("合并后的 query_llm_with_prompt 功能测试")
    print("=" * 60)
    
    # 测试纯文本
    print("\n" + "=" * 40)
    success1 = test_text_only()
    
    # 测试单图像
    print("\n" + "=" * 40)
    success2 = test_single_image()
    
    # 测试多图像
    print("\n" + "=" * 40)
    success3 = test_multiple_images()
    
    # 测试混合附件
    print("\n" + "=" * 40)
    success4 = test_mixed_attachments()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"纯文本测试: {'✓ 通过' if success1 else '✗ 失败'}")
    print(f"单图像测试: {'✓ 通过' if success2 else '✗ 失败'}")
    print(f"多图像测试: {'✓ 通过' if success3 else '✗ 失败'}")
    print(f"混合附件测试: {'✓ 通过' if success4 else '✗ 失败'}")
    
    if all([success1, success2, success3, success4]):
        print("🎉 所有测试通过！合并功能正常工作！")
    else:
        print("⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()