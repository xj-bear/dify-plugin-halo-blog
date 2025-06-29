#!/usr/bin/env python3
"""修复Token问题并重新测试"""

import requests
import json
import time
import os

def clean_token(token):
    """清理token，移除换行符和空白字符"""
    if not token:
        return token
    # 移除所有换行符和多余空白
    return token.strip().replace('\n', '').replace('\r', '')

def test_with_clean_token():
    """用清理后的token测试API"""
    raw_token = os.getenv('HALO_ACCESS_TOKEN', '')
    clean_token_value = clean_token(raw_token)
    
    print("🧹 Token清理测试")
    print("="*50)
    print(f"原始token长度: {len(raw_token)}")
    print(f"清理后长度: {len(clean_token_value)}")
    print(f"是否包含换行: {'是' if '\\n' in repr(raw_token) else '否'}")
    
    base_url = "https://blog.u2u.fun"
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {clean_token_value}',
        'User-Agent': 'Halo-Clean-Test/1.0'
    })
    
    print(f"\n✨ 使用清理后的token测试...")
    
    # 测试GET权限
    try:
        response = session.get(f"{base_url}/apis/content.halo.run/v1alpha1/tags", timeout=10)
        print(f"📋 GET标签列表: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   标签数量: {len(data.get('items', []))}")
    except Exception as e:
        print(f"   ❌ GET请求异常: {e}")
    
    # 测试简单标签创建
    simple_tag = {
        "metadata": {
            "generateName": "tag-"
        },
        "spec": {
            "displayName": f"清理测试标签{int(time.time())}",
            "slug": f"clean-test-{int(time.time())}"
        }
    }
    
    try:
        print(f"\n🏷️  测试标签创建...")
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/tags",
            data=json.dumps(simple_tag),
            timeout=30
        )
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.text[:200]}...")
        
        if response.status_code < 400:
            print("   ✅ 标签创建成功！")
            return True
        else:
            print("   ❌ 标签创建失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 标签创建异常: {e}")
        return False

if __name__ == "__main__":
    test_with_clean_token()
