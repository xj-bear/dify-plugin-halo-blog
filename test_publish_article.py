#!/usr/bin/env python3
"""
测试文章发布功能
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

def test_publish_article():
    """测试发布文章"""
    print("🔍 测试文章发布功能")
    print("=" * 50)
    print(f"🌐 测试站点: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Publish-Test/1.0'
    })
    
    # 测试数据
    title = "发布测试文章"
    content = "这是一个发布测试文章的内容。\n\n这篇文章将直接创建为发布状态，用于验证前端访问。\n\n## 发布测试\n\n如果您能在前端看到这个内容，说明发布功能正常工作。"
    
    print(f"📝 测试标题: {title}")
    print(f"📄 测试内容: {content[:50]}...")
    print()
    
    # 生成文章ID和slug
    post_id = str(uuid.uuid4())
    slug = f"publish-test-{int(time.time())}"
    
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
            "publish": True,  # 🔧 关键修复：直接创建为发布状态
            "publishTime": datetime.now().isoformat() + 'Z',  # 设置发布时间
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
    
    print("📝 正在创建发布文章...")
    
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
            print(f"   发布状态: {result.get('spec', {}).get('publish', False)}")
            print(f"   发布时间: {result.get('spec', {}).get('publishTime', 'N/A')}")
            
            # 等待一下让Halo处理
            print("⏳ 等待3秒让Halo处理发布...")
            time.sleep(3)
            
            # 测试前端访问
            print()
            print("🔍 测试前端访问")
            print("-" * 30)
            
            # 获取最新文章状态
            latest_response = session.get(
                f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                timeout=30
            )
            
            if latest_response.status_code == 200:
                latest_data = latest_response.json()
                print(f"   最新状态: {latest_data.get('status', {}).get('phase', 'N/A')}")
                
                permalink = latest_data.get('status', {}).get('permalink', f'/archives/{slug}')
                frontend_url = f"{BASE_URL}{permalink}"
                print(f"   前端链接: {frontend_url}")
                
                # 测试前端访问
                frontend_response = requests.get(frontend_url, timeout=30)
                print(f"   前端状态: {frontend_response.status_code}")
                
                if frontend_response.status_code == 200:
                    print(f"✅ 前端访问成功")
                    content_text = frontend_response.text
                    if title in content_text:
                        print(f"   标题存在: ✅")
                    else:
                        print(f"   标题不存在: ❌")
                        
                    if "发布测试文章的内容" in content_text:
                        print(f"   正文内容存在: ✅")
                    else:
                        print(f"   正文内容不存在: ❌")
                        
                    # 检查是否有实际的文章内容区域
                    if '<article' in content_text or 'class="post-content"' in content_text:
                        print(f"   文章结构存在: ✅")
                    else:
                        print(f"   文章结构不存在: ❌")
                        
                elif frontend_response.status_code == 404:
                    print(f"❌ 前端访问404 - 文章可能还在处理中")
                else:
                    print(f"❌ 前端访问失败: {frontend_response.status_code}")
            else:
                print(f"❌ 无法获取最新文章状态: {latest_response.status_code}")
                
            return post_id
            
        else:
            print(f"❌ 文章创建失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建过程中出错: {e}")
        return None

if __name__ == "__main__":
    post_id = test_publish_article()
    
    print()
    print("📊 测试总结")
    print("=" * 50)
    print("如果发布文章能在前端正确显示，说明问题已解决")
    print("如果仍然失败，可能需要检查Halo的发布流程或主题配置")
