#!/usr/bin/env python3
"""
检查真正的已发布文章（排除我们刚创建的）
"""

import json
import requests
from datetime import datetime

# 配置
BASE_URL = "https://blog.u2u.fun"
with open("key.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

def check_real_published_posts():
    """检查真正的已发布文章"""
    print("🔍 检查真正的已发布文章")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Real-Check/1.0'
    })
    
    # 我们创建的文章ID列表（需要排除）
    our_post_ids = [
        "798c53d6-a5f9-41b4-870b-0bbe0c4b5f7b",  # 发布测试文章
        "722f0dde-9675-473f-b800-514454532d74",  # 简化版本测试文章
        "a404524a-6f9f-4764-a9b5-7b14d044afdc",  # 继续测试
        "2dfceeb8-0204-4a8c-9752-1633f07b4ec4",  # 之前的测试文章
    ]
    
    try:
        # 获取所有文章列表
        response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts",
            timeout=30
        )
        
        if response.status_code == 200:
            posts_data = response.json()
            posts = posts_data.get('items', [])
            
            # 找到真正的已发布文章（排除我们创建的）
            real_published_posts = []
            for post in posts:
                post_id = post['metadata']['name']
                is_published = post.get('spec', {}).get('publish', False)
                has_status = post.get('status', {}).get('phase') is not None
                
                if is_published and post_id not in our_post_ids and has_status:
                    real_published_posts.append(post)
            
            print(f"   找到 {len(real_published_posts)} 篇真正的已发布文章")
            
            if real_published_posts:
                # 分析第一篇真正的已发布文章
                real_post = real_published_posts[0]
                post_name = real_post['metadata']['name']
                post_title = real_post['spec']['title']
                
                print()
                print(f"🔍 分析真正的已发布文章: {post_title}")
                print("-" * 50)
                print(f"   文章ID: {post_name}")
                print(f"   标题: {post_title}")
                print(f"   发布状态: {real_post['spec']['publish']}")
                print(f"   Slug: {real_post['spec']['slug']}")
                
                # 检查状态
                status = real_post.get('status', {})
                print(f"   状态阶段: {status.get('phase', 'N/A')}")
                print(f"   前端链接: {status.get('permalink', 'N/A')}")
                print(f"   摘要: {status.get('excerpt', 'N/A')}")
                print(f"   进行中: {status.get('inProgress', 'N/A')}")
                
                # 检查快照
                spec = real_post['spec']
                print(f"   releaseSnapshot: {spec.get('releaseSnapshot', 'N/A')}")
                print(f"   headSnapshot: {spec.get('headSnapshot', 'N/A')}")
                print(f"   baseSnapshot: {spec.get('baseSnapshot', 'N/A')}")
                
                # 检查注解
                annotations = real_post['metadata'].get('annotations', {})
                print(f"   注解数量: {len(annotations)}")
                for key, value in annotations.items():
                    if 'content' in key.lower():
                        print(f"   {key}: {value[:100]}...")
                
                # 测试前端访问
                permalink = status.get('permalink')
                if permalink:
                    frontend_url = f"{BASE_URL}{permalink}"
                    print(f"   测试前端: {frontend_url}")
                    
                    frontend_response = requests.get(frontend_url, timeout=30)
                    print(f"   前端状态: {frontend_response.status_code}")
                    
                    if frontend_response.status_code == 200:
                        print(f"   ✅ 前端访问正常")
                    else:
                        print(f"   ❌ 前端访问失败")
                
                # 检查快照内容
                head_snapshot = spec.get('headSnapshot')
                if head_snapshot:
                    print()
                    print(f"🔍 检查快照: {head_snapshot}")
                    print("-" * 30)
                    
                    snapshot_response = session.get(
                        f"{BASE_URL}/apis/content.halo.run/v1alpha1/snapshots/{head_snapshot}",
                        timeout=30
                    )
                    
                    if snapshot_response.status_code == 200:
                        snapshot_data = snapshot_response.json()
                        snapshot_spec = snapshot_data['spec']
                        print(f"   rawType: {snapshot_spec.get('rawType', 'N/A')}")
                        print(f"   rawPatch长度: {len(snapshot_spec.get('rawPatch', ''))}")
                        print(f"   contentPatch长度: {len(snapshot_spec.get('contentPatch', ''))}")
                        print(f"   owner: {snapshot_spec.get('owner', 'N/A')}")
                        print(f"   lastModifyTime: {snapshot_spec.get('lastModifyTime', 'N/A')}")
                        
                        if snapshot_spec.get('rawPatch'):
                            print(f"   rawPatch内容: {snapshot_spec.get('rawPatch', '')[:200]}...")
                    else:
                        print(f"   ❌ 快照获取失败: {snapshot_response.status_code}")
                
                print()
                print("📋 完整文章结构:")
                print(json.dumps(real_post, indent=2, ensure_ascii=False)[:1000] + "...")
                
                return real_post
            else:
                print("   ❌ 没有找到真正的已发布文章")
                return None
        else:
            print(f"❌ 获取文章列表失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return None

if __name__ == "__main__":
    real_post = check_real_published_posts()
    
    print()
    print("📊 关键发现")
    print("=" * 50)
    if real_post:
        status = real_post.get('status', {})
        spec = real_post['spec']
        
        print("真正的已发布文章具有以下特征：")
        print(f"1. status.phase: {status.get('phase', 'N/A')}")
        print(f"2. status.permalink: {status.get('permalink', 'N/A')}")
        print(f"3. headSnapshot: {spec.get('headSnapshot', 'N/A')}")
        print(f"4. releaseSnapshot: {spec.get('releaseSnapshot', 'N/A')}")
        print()
        print("我们的文章缺少这些关键信息，这就是为什么前端404的原因！")
    else:
        print("无法分析真正的已发布文章")
