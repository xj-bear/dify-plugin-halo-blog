#!/usr/bin/env python3
"""
调试文章内容设置的不同方法
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

print("🔍 测试不同的文章内容设置方法")
print("=" * 50)

# 创建测试文章
timestamp = int(time.time())
post_title = f"内容测试文章-{timestamp}"
post_name = f"content-test-{timestamp}"

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
            "raw": "这是测试文章摘要"
        },
        "categories": [],
        "tags": [],
        "htmlMetas": []
    }
}

response = requests.post(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts",
    headers=headers,
    json=post_data,
    timeout=10
)

if response.status_code != 201:
    print("❌ 文章创建失败")
    exit(1)

created_post = response.json()
post_id = created_post["metadata"]["name"]
print(f"✅ 文章创建成功，ID: {post_id}")

# 方法1: 使用原始的content端点
print("\n📝 方法1: 使用content端点")
content_data_1 = {
    "raw": f"# {post_title}\n\n这是内容测试",
    "content": f"<h1>{post_title}</h1><p>这是内容测试</p>",
    "rawType": "markdown"
}

response_1 = requests.put(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}/content",
    headers=headers,
    json=content_data_1,
    timeout=10
)
print(f"方法1响应: {response_1.status_code} - {response_1.text}")

# 方法2: 使用console.api端点
print("\n📝 方法2: 使用console.api端点")
response_2 = requests.put(
    f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
    headers=headers,
    json=content_data_1,
    timeout=10
)
print(f"方法2响应: {response_2.status_code} - {response_2.text}")

# 方法3: 使用POST而不是PUT
print("\n📝 方法3: 使用POST创建内容")
response_3 = requests.post(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}/content",
    headers=headers,
    json=content_data_1,
    timeout=10
)
print(f"方法3响应: {response_3.status_code} - {response_3.text}")

# 方法4: 先查看现有的文章内容
print("\n📝 方法4: 查看现有内容结构")
response_4 = requests.get(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
    headers=headers,
    timeout=10
)
if response_4.status_code == 200:
    post_detail = response_4.json()
    print(f"现有文章结构: {json.dumps(post_detail, indent=2, ensure_ascii=False)}")
    
    # 尝试只更新文章的spec，将内容直接放在spec中
    print("\n📝 方法5: 在spec中直接设置内容")
    post_detail["spec"]["baseSnapshot"] = "post-content-base"
    post_detail["spec"]["headSnapshot"] = "post-content-head"
    
    response_5 = requests.put(
        f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
        headers=headers,
        json=post_detail,
        timeout=10
    )
    print(f"方法5响应: {response_5.status_code} - {response_5.text}")

# 方法6: 检查是否有专门的snapshot端点
print("\n📝 方法6: 测试snapshot端点")
snapshot_data = {
    "metadata": {
        "name": f"post-{post_id}-content",
        "generateName": "post-content-"
    },
    "spec": {
        "subjectRef": {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "name": post_id
        },
        "rawType": "markdown",
        "contentType": "content",
        "raw": f"# {post_title}\n\n这是快照测试内容",
        "content": f"<h1>{post_title}</h1><p>这是快照测试内容</p>"
    }
}

response_6 = requests.post(
    f"{base_url}/apis/content.halo.run/v1alpha1/snapshots",
    headers=headers,
    json=snapshot_data,
    timeout=10
)
print(f"方法6响应: {response_6.status_code} - {response_6.text}")

# 清理
print(f"\n�� 清理测试文章: {post_id}")
delete_response = requests.delete(
    f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
    headers=headers,
    timeout=10
)
print(f"删除响应: {delete_response.status_code}")
