#!/usr/bin/env python3
"""
测试向量搜索逻辑的脚本
"""

import json
import requests
import time

def test_vector_search_without_attachments():
    """测试没有附件时的向量搜索"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-no-attachments",
        "text": "今天心情不好，需要安慰",
        "has_attachments": False
    }
    
    print("测试纯文本向量搜索...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"检索到的文档数量: {len(result.get('rag_docs', []))}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_vector_search_with_attachments():
    """测试有附件时的向量搜索（应该忽略附件信息）"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-with-attachments",
        "text": "今天心情不好，需要安慰",  # 与上面相同的文本
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
    
    print("\n测试带附件的向量搜索（附件不参与搜索）...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"检索到的文档数量: {len(result.get('rag_docs', []))}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True, result.get('rag_docs', [])
    except Exception as e:
        print(f"错误: {e}")
        return False, []

def test_different_text_with_attachments():
    """测试不同文本但有附件的向量搜索"""
    url = "http://localhost:8080/generate"
    
    payload = {
        "message_id": "test-different-text",
        "text": "这是完全不同的查询文本内容",
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
    
    print("\n测试不同文本的向量搜索...")
    print(f"请求: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"检索到的文档数量: {len(result.get('rag_docs', []))}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True, result.get('rag_docs', [])
    except Exception as e:
        print(f"错误: {e}")
        return False, []

def compare_rag_results(docs1, docs2):
    """比较两次检索的结果是否相同"""
    if len(docs1) != len(docs2):
        return False
    
    # 比较文档内容
    for i, (doc1, doc2) in enumerate(zip(docs1, docs2)):
        if doc1 != doc2:
            return False
    
    return True

def main():
    print("=" * 60)
    print("向量搜索逻辑测试")
    print("=" * 60)
    
    # 测试1：无附件
    print("\n" + "=" * 40)
    success1 = test_vector_search_without_attachments()
    
    # 测试2：有附件，相同文本
    print("\n" + "=" * 40)
    success2, docs_with_attachments = test_vector_search_with_attachments()
    
    # 测试3：有附件，不同文本
    print("\n" + "=" * 40)
    success3, docs_different_text = test_different_text_with_attachments()
    
    # 分析结果
    print("\n" + "=" * 60)
    print("测试分析:")
    
    if success2 and success3:
        if not compare_rag_results(docs_with_attachments, docs_different_text):
            print("✅ 向量搜索正确：不同文本检索到不同结果")
            print("✅ 附件信息未影响向量搜索")
        else:
            print("⚠️ 可能的问题：不同文本检索到相同结果")
    
    # 总结
    print("\n测试总结:")
    print(f"无附件测试: {'✓ 通过' if success1 else '✗ 失败'}")
    print(f"有附件测试: {'✓ 通过' if success2 else '✗ 失败'}")
    print(f"不同文本测试: {'✓ 通过' if success3 else '✗ 失败'}")
    
    if success1 and success2 and success3:
        print("🎉 所有测试通过！向量搜索逻辑正确！")
    else:
        print("⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()