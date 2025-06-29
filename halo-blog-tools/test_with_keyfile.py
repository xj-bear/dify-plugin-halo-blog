#!/usr/bin/env python3
"""使用key.txt中的token进行测试"""

import requests
import json
import time

def read_token_from_file():
    """从key.txt读取token"""
    try:
        with open('key.txt', 'r') as f:
            token = f.read().strip()
        return token
    except Exception as e:
        print(f"❌ 读取key.txt失败: {e}")
        return None

def test_api_with_keyfile_token():
    """使用key.txt中的token测试API"""
    print("🔑 使用key.txt测试API")
    print("="*50)
    
    token = read_token_from_file()
    if not token:
        print("❌ 无法读取token")
        return
    
    print(f"✅ Token读取成功，长度: {len(token)}")
    print(f"🔍 Token开头: {token[:20]}...")
    
    base_url = "https://blog.u2u.fun"
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Halo-KeyFile-Test/1.0'
    })
    
    # 1. 测试GET标签列表（权限检查）
    print(f"\n📋 测试1: 获取标签列表")
    try:
        response = session.get(f"{base_url}/apis/content.halo.run/v1alpha1/tags", timeout=10)
        print(f"   状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取 {len(data.get('items', []))} 个标签")
        elif response.status_code == 403:
            print(f"   ⚠️  权限不足")
        else:
            print(f"   ❌ 失败: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 2. 测试标签创建
    print(f"\n🏷️  测试2: 创建标签")
    tag_data = {
        "metadata": {
            "generateName": "tag-"
        },
        "spec": {
            "displayName": f"KeyFile测试标签{int(time.time())}",
            "slug": f"keyfile-test-{int(time.time())}"
        }
    }
    
    try:
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/tags",
            data=json.dumps(tag_data),
            timeout=30
        )
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            created_tag = response.json()
            tag_id = created_tag.get("metadata", {}).get("name")
            print(f"   ✅ 标签创建成功: {tag_id}")
            return True
        else:
            print(f"   ❌ 标签创建失败")
            if "500" in str(response.status_code):
                print(f"   💥 确认500错误")
            return False
            
    except Exception as e:
        print(f"   ❌ 标签创建异常: {e}")
        return False

    # 3. 测试文章创建
    print(f"\n📝 测试3: 创建文章")
    post_data = {
        "metadata": {
            "generateName": "post-"
        },
        "spec": {
            "title": f"KeyFile测试文章{int(time.time())}",
            "slug": f"keyfile-test-post-{int(time.time())}",
            "deleted": False,
            "publish": False
        }
    }
    
    try:
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            created_post = response.json()
            post_id = created_post.get("metadata", {}).get("name")
            print(f"   ✅ 文章创建成功: {post_id}")
            return True
        else:
            print(f"   ❌ 文章创建失败")
            if "500" in str(response.status_code):
                print(f"   💥 确认500错误")
            return False
            
    except Exception as e:
        print(f"   ❌ 文章创建异常: {e}")
        return False

if __name__ == "__main__":
    test_api_with_keyfile_token()
