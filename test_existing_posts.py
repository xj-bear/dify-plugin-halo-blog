#!/usr/bin/env python3
"""
检查现有文章的结构
找出正常工作的文章与我们创建的文章的区别
"""

import json
import requests
from datetime import datetime

# 配置
BASE_URL = "https://blog.u2u.fun"
with open("key.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

def check_existing_posts():
    """检查现有文章"""
    print("🔍 检查现有文章结构")
    print("=" * 50)
    print(f"🌐 测试站点: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Structure-Check/1.0'
    })
    
    try:
        # 获取所有文章列表
        print("📝 获取文章列表...")
        response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts",
            timeout=30
        )
        
        if response.status_code == 200:
            posts_data = response.json()
            posts = posts_data.get('items', [])
            print(f"   找到 {len(posts)} 篇文章")
            
            # 找到已发布的文章
            published_posts = [p for p in posts if p.get('spec', {}).get('publish', False)]
            print(f"   其中 {len(published_posts)} 篇已发布")
            
            if published_posts:
                # 分析第一篇已发布文章
                first_post = published_posts[0]
                post_name = first_post['metadata']['name']
                post_title = first_post['spec']['title']
                
                print()
                print(f"🔍 分析已发布文章: {post_title}")
                print("-" * 30)
                print(f"   文章ID: {post_name}")
                print(f"   标题: {post_title}")
                print(f"   发布状态: {first_post['spec']['publish']}")
                print(f"   Slug: {first_post['spec']['slug']}")
                
                # 检查状态
                status = first_post.get('status', {})
                print(f"   状态阶段: {status.get('phase', 'N/A')}")
                print(f"   前端链接: {status.get('permalink', 'N/A')}")
                
                # 检查快照
                spec = first_post['spec']
                print(f"   releaseSnapshot: {spec.get('releaseSnapshot', 'N/A')}")
                print(f"   headSnapshot: {spec.get('headSnapshot', 'N/A')}")
                print(f"   baseSnapshot: {spec.get('baseSnapshot', 'N/A')}")
                
                # 检查注解
                annotations = first_post['metadata'].get('annotations', {})
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
                        content = frontend_response.text
                        if post_title in content:
                            print(f"   ✅ 标题存在于前端")
                        else:
                            print(f"   ❌ 标题不存在于前端")
                    else:
                        print(f"   ❌ 前端访问失败")
                
                # 如果有快照，检查快照内容
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
                        print(f"   rawPatch内容: {snapshot_spec.get('rawPatch', 'N/A')[:100]}...")
                    else:
                        print(f"   ❌ 快照获取失败: {snapshot_response.status_code}")
                
                return first_post
            else:
                print("   ❌ 没有找到已发布的文章")
                return None
        else:
            print(f"❌ 获取文章列表失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return None

def compare_with_our_post():
    """对比我们创建的文章"""
    print()
    print("🔍 对比我们创建的文章")
    print("=" * 50)
    
    # 我们刚创建的文章ID
    our_post_id = "798c53d6-a5f9-41b4-870b-0bbe0c4b5f7b"
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Structure-Check/1.0'
    })
    
    try:
        response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{our_post_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            our_post = response.json()
            print(f"✅ 我们的文章获取成功")
            print(f"   标题: {our_post['spec']['title']}")
            print(f"   发布状态: {our_post['spec']['publish']}")
            print(f"   状态阶段: {our_post.get('status', {}).get('phase', 'N/A')}")
            print(f"   前端链接: {our_post.get('status', {}).get('permalink', 'N/A')}")
            
            # 检查快照
            spec = our_post['spec']
            print(f"   releaseSnapshot: {spec.get('releaseSnapshot', 'N/A')}")
            print(f"   headSnapshot: {spec.get('headSnapshot', 'N/A')}")
            print(f"   baseSnapshot: {spec.get('baseSnapshot', 'N/A')}")
            
            return our_post
        else:
            print(f"❌ 我们的文章获取失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 对比过程中出错: {e}")
        return None

if __name__ == "__main__":
    existing_post = check_existing_posts()
    our_post = compare_with_our_post()
    
    print()
    print("📊 分析总结")
    print("=" * 50)
    if existing_post and our_post:
        print("对比正常文章和我们创建的文章，找出差异：")
        print(f"1. 正常文章状态: {existing_post.get('status', {}).get('phase', 'N/A')}")
        print(f"   我们的文章状态: {our_post.get('status', {}).get('phase', 'N/A')}")
        print(f"2. 正常文章快照: {existing_post['spec'].get('headSnapshot', 'N/A')}")
        print(f"   我们的文章快照: {our_post['spec'].get('headSnapshot', 'N/A')}")
    else:
        print("无法完成对比分析")
