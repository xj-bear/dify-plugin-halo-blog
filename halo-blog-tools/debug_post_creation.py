#!/usr/bin/env python3
"""
详细调试文章创建问题
"""

import requests
import json
import time
from datetime import datetime

# 从key.txt读取token
with open('key.txt', 'r') as f:
    token = f.read().strip()

base_url = "https://blog.u2u.fun"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("🔍 详细调试文章创建流程")
print("=" * 50)

# 第一步：创建文章
timestamp = int(time.time())
post_title = f"调试测试文章-{timestamp}"
post_name = f"debug-post-{timestamp}"

post_data = {
    "apiVersion": "content.halo.run/v1alpha1",
    "kind": "Post",
    "metadata": {
        "name": post_name,
        "generateName": "post-"
    },
    "spec": {
        "title": post_title,
        "slug": post_name,
        "template": "",
        "cover": "",
        "deleted": False,
        "publish": False,
        "publishTime": None,
        "pinned": False,
        "allowComment": True,
        "visible": "PUBLIC",
        "priority": 0,
        "excerpt": {
            "autoGenerate": True,
            "raw": "这是一篇调试测试文章的摘要"
        },
        "categories": [],
        "tags": [],
        "htmlMetas": []
    }
}

print("📝 步骤1: 创建文章结构")
print(f"数据: {json.dumps(post_data, indent=2, ensure_ascii=False)}")

response = requests.post(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts",
    headers=headers,
    json=post_data,
    timeout=10
)

print(f"响应状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容: {response.text}")

if response.status_code != 201:
    print("❌ 文章创建失败")
    exit(1)

created_post = response.json()
post_id = created_post["metadata"]["name"]
print(f"✅ 文章创建成功，ID: {post_id}")

# 第二步：设置文章内容
print("\n📄 步骤2: 设置文章内容")
content_data = {
    "raw": f"# {post_title}\n\n这是一篇调试测试文章的内容。\n\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "content": f"<h1>{post_title}</h1><p>这是一篇调试测试文章的内容。</p><p>创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    "rawType": "markdown"
}

print(f"内容数据: {json.dumps(content_data, indent=2, ensure_ascii=False)}")

content_url = f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}/content"
print(f"内容设置URL: {content_url}")

content_response = requests.put(
    content_url,
    headers=headers,
    json=content_data,
    timeout=10
)

print(f"内容响应状态码: {content_response.status_code}")
print(f"内容响应头: {dict(content_response.headers)}")
print(f"内容响应内容: {content_response.text}")

if content_response.status_code in [200, 201]:
    print(f"✅ 文章内容设置成功")
else:
    print(f"❌ 文章内容设置失败: {content_response.status_code}")
    
    # 尝试获取用户权限信息
    print("\n🔍 检查用户权限:")
    user_response = requests.get(
        f"{base_url}/apis/api.console.halo.run/v1alpha1/users/-",
        headers=headers
    )
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
    
    # 尝试不同的内容格式
    print("\n🔍 尝试简化的内容格式:")
    simple_content = {
        "raw": "简单测试内容",
        "content": "<p>简单测试内容</p>",
        "rawType": "markdown"
    }
    
    simple_response = requests.put(
        content_url,
        headers=headers,
        json=simple_content,
        timeout=10
    )
    print(f"简化内容响应: {simple_response.status_code} - {simple_response.text}")

# 清理：删除测试文章
print(f"\n🧹 清理测试文章: {post_id}")
delete_response = requests.delete(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
    headers=headers,
    timeout=10
)
print(f"删除响应: {delete_response.status_code}")
