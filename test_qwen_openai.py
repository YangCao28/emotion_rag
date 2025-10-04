#!/usr/bin/env python3
"""
测试 Qwen API (OpenAI兼容模式) 集成的脚本
"""

import json
import requests
import time

def test_text_only():
    """测试纯文本消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-001",
        "text": "你好，今天心情怎么样？",
        "has_attachments": False
    }
    
    print("测试纯文本消息...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_with_attachments():
    """测试带附件的消息"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-002",
        "text": "看看这张图片，给我说说你的想法",
        "attachments": [
            {
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "filename": "测试图片.jpg",
                "type": "image/jpeg",
                "size": 150000
            }
        ],
        "has_attachments": True
    }
    
    print("\n测试带附件的消息...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_health():
    """测试服务健康状态"""
    url = "http://localhost:8080/docs"
    
    print("测试服务健康状态...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✓ 服务正常运行")
            return True
        else:
            print(f"✗ 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到服务: {e}")
        return False

def main():
    print("=" * 50)
    print("Qwen API (OpenAI兼容模式) 集成测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(5)
    
    # 测试服务健康状态
    if not test_health():
        print("服务未正常启动，退出测试")
        return
    
    print("\n请确保已经设置了 DASHSCOPE_API_KEY 环境变量！")
    print("获取 API Key: https://help.aliyun.com/zh/model-studio/get-api-key")
    
    # 测试纯文本
    print("\n" + "=" * 30)
    success1 = test_text_only()
    
    # 测试带附件
    print("\n" + "=" * 30)
    success2 = test_with_attachments()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"纯文本测试: {'✓ 通过' if success1 else '✗ 失败'}")
    print(f"附件测试: {'✓ 通过' if success2 else '✗ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查:")
        print("  1. DASHSCOPE_API_KEY 是否正确设置")
        print("  2. 网络连接是否正常")
        print("  3. API 配额是否充足")

if __name__ == "__main__":
    main()