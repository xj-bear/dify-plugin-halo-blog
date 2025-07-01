#!/usr/bin/env python3
"""
测试简化版本的文章创建
"""

import json
import time
import uuid
import requests
from datetime import datetime

# 配置
BASE_URL = "https://blog.u2u.fun"
with open("key.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

def test_simple_create():
    """测试简化版本的文章创建"""
    print("🔍 测试简化版本的文章创建")
    print("=" * 50)
    print(f"🌐 测试站点: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Simple-Test/1.0'
    })
    
    # 测试数据
    title = "简化版本测试文章"
    content = "这是一个简化版本的测试文章内容。\n\n包含多行内容，用于验证简化版本是否能正确创建文章。\n\n## 测试标题\n\n测试内容正文。"
    
    print(f"📝 测试标题: {title}")
    print(f"📄 测试内容: {content[:50]}...")
    print()
    
    # 生成文章ID和slug
    post_id = str(uuid.uuid4())
    slug = f"simple-test-{int(time.time())}"
    
    print(f"🆔 文章ID: {post_id}")
    print(f"🔗 Slug: {slug}")
    print()
    
    # 创建content-json
    content_json = {
        "rawType": "markdown",
        "raw": content,
        "content": content
    }
    
    post_data = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "name": post_id,
            "annotations": {
                "content.halo.run/content-json": json.dumps(content_json, ensure_ascii=False),
                "content.halo.run/preferred-editor": "default",
                "content.halo.run/content-type": "markdown"
            }
        },
        "spec": {
            "title": title,
            "slug": slug,
            "template": "",
            "cover": "",
            "deleted": False,
            "publish": False,  # 创建为草稿
            "pinned": False,
            "allowComment": True,
            "visible": "PUBLIC",
            "priority": 0,
            "excerpt": {
                "autoGenerate": True,
                "raw": ""
            },
            "categories": [],
            "tags": [],
            "owner": "jason",
            "htmlMetas": []
        }
    }
    
    print("📝 正在创建文章...")
    print(f"   请求数据: {json.dumps(post_data, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        response = session.post(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts",
            json=post_data,
            timeout=30
        )
        
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 文章创建成功")
            print(f"   创建的文章ID: {result.get('metadata', {}).get('name', 'N/A')}")
            print(f"   文章标题: {result.get('spec', {}).get('title', 'N/A')}")
            print(f"   文章状态: {result.get('spec', {}).get('publish', False)}")
            
            # 验证content-json注解
            annotations = result.get('metadata', {}).get('annotations', {})
            content_json_str = annotations.get('content.halo.run/content-json')
            if content_json_str:
                try:
                    content_data = json.loads(content_json_str)
                    print(f"   content-json存在: ✅")
                    print(f"   raw长度: {len(content_data.get('raw', ''))}")
                    print(f"   content长度: {len(content_data.get('content', ''))}")
                    print(f"   raw内容: {content_data.get('raw', 'N/A')}")
                except:
                    print(f"   content-json解析失败: ❌")
            else:
                print(f"   content-json不存在: ❌")
                
            return result.get('metadata', {}).get('name')
            
        else:
            print(f"❌ 文章创建失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建过程中出错: {e}")
        return None

def test_article_access(post_id):
    """测试文章访问"""
    if not post_id:
        return
        
    print()
    print("🔍 测试文章访问")
    print("-" * 30)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Simple-Test/1.0'
    })
    
    try:
        # 获取文章详情
        response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{post_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            post_data = response.json()
            print(f"✅ 文章获取成功")
            print(f"   标题: {post_data['spec']['title']}")
            print(f"   状态: {post_data.get('status', {}).get('phase', 'N/A')}")
            print(f"   版本: {post_data['metadata']['version']}")
            
            # 检查前端链接
            permalink = post_data.get('status', {}).get('permalink', f'/archives/{post_data["spec"]["slug"]}')
            frontend_url = f"{BASE_URL}{permalink}"
            print(f"   前端链接: {frontend_url}")
            
            # 测试前端访问
            frontend_response = requests.get(frontend_url, timeout=30)
            print(f"   前端状态: {frontend_response.status_code}")
            
            if frontend_response.status_code == 200:
                print(f"✅ 前端访问成功")
                content = frontend_response.text
                if "简化版本测试文章" in content:
                    print(f"   标题存在: ✅")
                else:
                    print(f"   标题不存在: ❌")
                    
                if "这是一个简化版本的测试文章内容" in content:
                    print(f"   正文内容存在: ✅")
                else:
                    print(f"   正文内容不存在: ❌")
            else:
                print(f"❌ 前端访问失败")
                
        else:
            print(f"❌ 文章获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 访问测试出错: {e}")

if __name__ == "__main__":
    post_id = test_simple_create()
    test_article_access(post_id)
    
    print()
    print("📊 测试总结")
    print("=" * 50)
    print("如果文章创建成功且前端能正确显示内容，说明简化版本工作正常")
    print("如果失败，需要进一步分析Halo的内容架构")
