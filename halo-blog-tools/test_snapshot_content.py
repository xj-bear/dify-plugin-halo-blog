#!/usr/bin/env python3
"""
通过快照ID获取文章内容
解决编辑器识别问题
"""

import json
import requests
import time

def load_config():
    """加载配置"""
    try:
        with open('key.txt', 'r', encoding='utf-8') as f:
            pat_token = f.read().strip()
        return "https://blog.u2u.fun", pat_token
    except FileNotFoundError:
        print("❌ 找不到 key.txt 文件")
        return None, None

def get_content_by_snapshot():
    """通过快照ID获取内容"""
    print("🔍 通过快照ID获取文章内容")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 从JSON文件读取快照ID
    test_cases = [
        {
            "name": "简单测试文章",
            "article_id": "simple-test-1751214662",
            "snapshot_id": "51d5ae19-af30-4fff-afa1-9d3be6f08a06"
        },
        {
            "name": "浏览器模拟文章",
            "article_id": "browser-like-test-1751214901", 
            "snapshot_id": "25d32409-7b26-4492-b7b8-9b28b1ecd381"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📄 测试: {test_case['name']}")
        print(f"   文章ID: {test_case['article_id']}")
        print(f"   快照ID: {test_case['snapshot_id']}")
        
        # 尝试不同的快照API端点
        snapshot_endpoints = [
            f"{base_url}/apis/content.halo.run/v1alpha1/snapshots/{test_case['snapshot_id']}",
            f"{base_url}/apis/api.console.halo.run/v1alpha1/snapshots/{test_case['snapshot_id']}",
            f"{base_url}/apis/content.halo.run/v1alpha1/contents/{test_case['snapshot_id']}",
            f"{base_url}/apis/api.console.halo.run/v1alpha1/contents/{test_case['snapshot_id']}"
        ]
        
        for i, endpoint in enumerate(snapshot_endpoints, 1):
            print(f"\n📡 端点 {i}: {endpoint}")
            
            try:
                response = session.get(endpoint, timeout=30)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 快照内容获取成功！")
                    
                    # 检查内容字段
                    if 'spec' in data and 'content' in data['spec']:
                        content = data['spec']['content']
                        print(f"   📝 内容长度: {len(content)}")
                        print(f"   📝 内容预览: {content[:100]}{'...' if len(content) > 100 else ''}")
                        
                        # 保存快照数据
                        filename = f"snapshot_{test_case['snapshot_id']}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"   💾 快照数据已保存到: {filename}")
                        
                    else:
                        print(f"   ℹ️  数据结构: {list(data.keys())}")
                        
                elif response.status_code == 404:
                    print(f"   ❌ 快照不存在")
                elif response.status_code == 500:
                    print(f"   ❌ 服务器错误")
                else:
                    print(f"   ❌ 其他错误: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {e}")

def test_fix_content_association():
    """测试修复内容关联"""
    print(f"\n🔧 尝试修复内容关联")
    print("=" * 50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 创建一个新文章并使用更完整的流程
    post_name = f"complete-test-{int(time.time())}"
    test_content = "这是一个完整流程的测试文章。\n\n应该能被编辑器正确识别。"
    
    print(f"📝 创建完整流程测试文章: {post_name}")
    
    try:
        # 1. 创建文章
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name
            },
            "spec": {
                "title": f"完整流程测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "slug": post_name,
                "template": "",
                "cover": "",
                "deleted": False,
                "publish": False,
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
        
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"❌ 文章创建失败: {create_response.status_code}")
            return False
            
        print(f"✅ 文章创建成功")
        
        # 2. 设置内容并包含更多字段
        content_data = {
            "raw": test_content,
            "content": test_content,
            "rawType": "markdown",
            "version": 1
        }
        
        content_response = session.put(
            f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
            data=json.dumps(content_data),
            timeout=30
        )
        
        print(f"📤 内容设置响应: {content_response.status_code}")
        
        if content_response.status_code in [200, 201]:
            print(f"✅ 内容设置成功")
            
            # 3. 等待一下然后重新获取文章信息
            time.sleep(2)
            
            article_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_name}",
                timeout=30
            )
            
            if article_response.status_code == 200:
                article_data = article_response.json()
                new_snapshot = article_data['spec'].get('headSnapshot')
                print(f"📋 新快照ID: {new_snapshot}")
                
                edit_url = f"{base_url}/console/posts/editor?name={post_name}"
                print(f"🔗 编辑链接: {edit_url}")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 修复测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 快照内容获取和修复测试")
    print("=" * 70)
    
    # 尝试通过快照获取内容
    get_content_by_snapshot()
    
    # 测试完整的内容关联流程
    success = test_fix_content_association()
    
    if success:
        print(f"\n✅ 完整流程测试成功")
        print(f"💡 请测试新创建的文章编辑器功能")
    else:
        print(f"\n❌ 完整流程测试失败")

if __name__ == "__main__":
    main() 