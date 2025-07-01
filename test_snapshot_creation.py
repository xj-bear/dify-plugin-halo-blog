#!/usr/bin/env python3
"""
测试Halo快照创建
验证快照创建和关联是否正常工作
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "https://blog.u2u.fun"
with open("key.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

def test_snapshot_creation():
    """测试快照创建"""
    print("🔍 Halo快照创建测试")
    print("=" * 50)
    print(f"🌐 测试站点: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Snapshot-Test/1.0'
    })
    
    # 测试文章ID
    test_post_id = "2dfceeb8-0204-4a8c-9752-1633f07b4ec4"
    test_content = "这是一个测试快照内容，用于验证快照创建功能是否正常工作。"
    
    print(f"📝 测试文章ID: {test_post_id}")
    print(f"📄 测试内容: {test_content}")
    print()
    
    # 1. 创建快照
    print("1️⃣ 创建快照")
    print("-" * 30)
    
    try:
        timestamp = int(time.time() * 1000)
        snapshot_name = f"test-snapshot-{timestamp}"
        
        snapshot_data = {
            'spec': {
                'subjectRef': {
                    'group': 'content.halo.run',
                    'version': 'v1alpha1',
                    'kind': 'Post',
                    'name': test_post_id
                },
                'rawType': 'markdown',
                'rawPatch': test_content,
                'contentPatch': test_content,
                'lastModifyTime': datetime.now().isoformat() + 'Z',
                'owner': 'jason',
                'contributors': ['jason']
            },
            'apiVersion': 'content.halo.run/v1alpha1',
            'kind': 'Snapshot',
            'metadata': {
                'name': snapshot_name,
                'annotations': {
                    'content.halo.run/keep-raw': 'true',
                    'content.halo.run/display-name': f'测试快照-{test_post_id}',
                    'content.halo.run/version': str(timestamp)
                }
            }
        }
        
        print(f"   快照名称: {snapshot_name}")
        print(f"   快照数据: {json.dumps(snapshot_data, indent=2, ensure_ascii=False)}")
        
        snapshot_response = session.post(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/snapshots",
            json=snapshot_data,
            timeout=30
        )
        
        print(f"   HTTP状态: {snapshot_response.status_code}")
        
        if snapshot_response.status_code in [200, 201]:
            print(f"✅ 快照创建成功")
            snapshot_result = snapshot_response.json()
            print(f"   创建的快照: {snapshot_result['metadata']['name']}")
            
            # 2. 关联快照到文章
            print()
            print("2️⃣ 关联快照到文章")
            print("-" * 30)
            
            # 获取最新文章数据
            post_response = session.get(
                f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{test_post_id}",
                timeout=30
            )
            
            if post_response.status_code == 200:
                post_data = post_response.json()
                print(f"   当前版本: {post_data['metadata']['version']}")
                print(f"   当前headSnapshot: {post_data['spec'].get('headSnapshot', 'N/A')}")
                
                # 更新快照关联
                post_data['spec']['releaseSnapshot'] = snapshot_name
                post_data['spec']['headSnapshot'] = snapshot_name
                post_data['spec']['baseSnapshot'] = snapshot_name
                
                update_response = session.put(
                    f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{test_post_id}",
                    json=post_data,
                    timeout=30
                )
                
                print(f"   关联HTTP状态: {update_response.status_code}")
                
                if update_response.status_code in [200, 201]:
                    print(f"✅ 快照关联成功")
                    update_result = update_response.json()
                    print(f"   新版本: {update_result['metadata']['version']}")
                    print(f"   新headSnapshot: {update_result['spec'].get('headSnapshot', 'N/A')}")
                    
                    # 3. 验证快照内容
                    print()
                    print("3️⃣ 验证快照内容")
                    print("-" * 30)
                    
                    verify_response = session.get(
                        f"{BASE_URL}/apis/content.halo.run/v1alpha1/snapshots/{snapshot_name}",
                        timeout=30
                    )
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        print(f"✅ 快照验证成功")
                        print(f"   rawPatch: {verify_data['spec'].get('rawPatch', 'N/A')}")
                        print(f"   contentPatch: {verify_data['spec'].get('contentPatch', 'N/A')}")
                    else:
                        print(f"❌ 快照验证失败: {verify_response.status_code}")
                        
                else:
                    print(f"❌ 快照关联失败: {update_response.status_code}")
                    print(f"   错误: {update_response.text}")
            else:
                print(f"❌ 获取文章数据失败: {post_response.status_code}")
                
        else:
            print(f"❌ 快照创建失败: {snapshot_response.status_code}")
            print(f"   错误: {snapshot_response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    
    print()
    print("📊 测试总结")
    print("=" * 50)
    print("如果快照创建和关联都成功，说明API工作正常")
    print("如果失败，需要检查权限或API调用方式")

if __name__ == "__main__":
    test_snapshot_creation()
