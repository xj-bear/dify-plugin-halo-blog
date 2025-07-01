#!/usr/bin/env python3
"""
测试Halo文章实际内容
验证文章创建和更新后是否真的有正文内容
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "https://blog.u2u.fun"
with open("key.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

def test_article_content():
    """测试文章内容"""
    print("🔍 Halo文章内容验证测试")
    print("=" * 50)
    print(f"🌐 测试站点: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Halo-Content-Test/1.0'
    })
    
    # 测试文章ID（从远程调试日志中获取）
    test_post_id = "2dfceeb8-0204-4a8c-9752-1633f07b4ec4"
    
    print(f"📝 测试文章ID: {test_post_id}")
    print()
    
    # 1. 获取文章基本信息
    print("1️⃣ 获取文章基本信息")
    print("-" * 30)
    
    try:
        post_response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{test_post_id}",
            timeout=30
        )
        
        if post_response.status_code == 200:
            post_data = post_response.json()
            print(f"✅ 文章获取成功")
            print(f"   标题: {post_data['spec']['title']}")
            print(f"   状态: {post_data.get('status', {}).get('phase', 'N/A')}")
            print(f"   版本: {post_data['metadata']['version']}")
            
            # 检查注解
            annotations = post_data.get('metadata', {}).get('annotations', {})
            content_json = annotations.get('content.halo.run/content-json')
            if content_json:
                try:
                    content_data = json.loads(content_json)
                    print(f"   content-json存在: ✅")
                    print(f"   rawType: {content_data.get('rawType', 'N/A')}")
                    print(f"   raw长度: {len(content_data.get('raw', ''))}")
                    print(f"   content长度: {len(content_data.get('content', ''))}")
                    print(f"   raw内容预览: {content_data.get('raw', '')[:50]}...")
                except:
                    print(f"   content-json解析失败: ❌")
            else:
                print(f"   content-json不存在: ❌")
                
        else:
            print(f"❌ 文章获取失败: {post_response.status_code}")
            print(f"   错误: {post_response.text}")
            return
            
    except Exception as e:
        print(f"❌ 文章获取异常: {e}")
        return
    
    print()
    
    # 2. 测试Console Content API
    print("2️⃣ 测试Console Content API")
    print("-" * 30)
    
    try:
        content_response = session.get(
            f"{BASE_URL}/apis/api.console.halo.run/v1alpha1/posts/{test_post_id}/content",
            timeout=30
        )
        
        print(f"   HTTP状态: {content_response.status_code}")
        
        if content_response.status_code == 200:
            content_data = content_response.json()
            print(f"✅ Console Content API成功")
            print(f"   rawType: {content_data.get('rawType', 'N/A')}")
            print(f"   raw长度: {len(content_data.get('raw', ''))}")
            print(f"   content长度: {len(content_data.get('content', ''))}")
            print(f"   raw内容: {content_data.get('raw', 'N/A')}")
            print(f"   content内容: {content_data.get('content', 'N/A')}")
        elif content_response.status_code == 500:
            print(f"⚠️ Console Content API返回500（可能是正常现象）")
            print(f"   响应: {content_response.text}")
        else:
            print(f"❌ Console Content API失败: {content_response.status_code}")
            print(f"   响应: {content_response.text}")
            
    except Exception as e:
        print(f"❌ Console Content API异常: {e}")
    
    print()
    
    # 3. 测试前端访问
    print("3️⃣ 测试前端文章访问")
    print("-" * 30)
    
    try:
        # 获取文章的permalink
        permalink = post_data.get('status', {}).get('permalink', '/archives/4')
        frontend_url = f"{BASE_URL}{permalink}"
        
        print(f"   前端链接: {frontend_url}")
        
        # 不使用认证访问前端
        frontend_session = requests.Session()
        frontend_response = frontend_session.get(frontend_url, timeout=30)
        
        print(f"   HTTP状态: {frontend_response.status_code}")
        
        if frontend_response.status_code == 200:
            content = frontend_response.text
            print(f"✅ 前端访问成功")
            print(f"   页面大小: {len(content)} 字符")
            
            # 检查是否包含文章内容
            title = post_data['spec']['title']
            if title in content:
                print(f"   标题存在: ✅")
            else:
                print(f"   标题不存在: ❌")
                
            # 检查是否有实际内容（不只是摘要）
            if "这是一篇新的dify测试文章" in content or "我需要更新这篇新的测试文章" in content:
                print(f"   正文内容存在: ✅")
            else:
                print(f"   正文内容不存在: ❌")
                print(f"   页面内容预览: {content[content.find('<body'):content.find('</body>')][:200]}...")
                
        else:
            print(f"❌ 前端访问失败: {frontend_response.status_code}")
            
    except Exception as e:
        print(f"❌ 前端访问异常: {e}")
    
    print()
    
    # 4. 测试快照API
    print("4️⃣ 测试快照信息")
    print("-" * 30)
    
    try:
        head_snapshot = post_data['spec'].get('headSnapshot')
        if head_snapshot:
            print(f"   headSnapshot: {head_snapshot}")
            
            snapshot_response = session.get(
                f"{BASE_URL}/apis/content.halo.run/v1alpha1/snapshots/{head_snapshot}",
                timeout=30
            )
            
            if snapshot_response.status_code == 200:
                snapshot_data = snapshot_response.json()
                print(f"✅ 快照获取成功")
                print(f"   rawType: {snapshot_data['spec'].get('rawType', 'N/A')}")
                print(f"   rawPatch长度: {len(snapshot_data['spec'].get('rawPatch', ''))}")
                print(f"   contentPatch长度: {len(snapshot_data['spec'].get('contentPatch', ''))}")
                print(f"   rawPatch内容: {snapshot_data['spec'].get('rawPatch', 'N/A')}")
            else:
                print(f"❌ 快照获取失败: {snapshot_response.status_code}")
        else:
            print(f"   无headSnapshot")
            
    except Exception as e:
        print(f"❌ 快照测试异常: {e}")
    
    print()
    print("📊 测试总结")
    print("=" * 50)
    print("请根据上述测试结果分析问题:")
    print("1. content-json注解是否正确设置")
    print("2. Console Content API是否返回正确内容")
    print("3. 前端是否能正确显示文章内容")
    print("4. 快照是否包含正确内容")

if __name__ == "__main__":
    test_article_content()
