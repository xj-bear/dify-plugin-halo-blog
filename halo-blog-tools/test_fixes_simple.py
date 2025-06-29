#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Bug修复测试脚本
直接使用HTTP请求测试功能，避免复杂的模块导入问题
"""

import requests
import json
import time
from datetime import datetime

def load_config():
    """加载配置"""
    try:
        base_url = "https://blog.u2u.fun"
        with open('key.txt', 'r', encoding='utf-8') as f:
            access_token = f.read().strip()
        return base_url, access_token
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None, None

def test_tag_creation():
    """测试标签创建功能"""
    print("\n" + "="*50)
    print("测试: 标签创建功能")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    try:
        # 创建测试标签
        tag_name = f"测试标签-{int(time.time())}"
        tag_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Tag",
            "metadata": {
                "generateName": "tag-"
            },
            "spec": {
                "displayName": tag_name,
                "slug": f"test-tag-{int(time.time())}",
                "color": "#6366f1",
                "cover": ""
            }
        }
        
        print(f"创建标签: {tag_name}")
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/tags",
            data=json.dumps(tag_data),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            created_tag = response.json()
            tag_id = created_tag['metadata']['name']
            print(f"✅ 标签创建成功: {tag_name} (ID: {tag_id})")
            return tag_id
        else:
            print(f"❌ 标签创建失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 标签创建异常: {e}")
        return None

def test_moment_with_tags():
    """测试瞬间创建标签显示功能"""
    print("\n" + "="*50)
    print("测试1: 瞬间创建标签显示")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    try:
        # 首先创建一些测试标签
        tag_ids = []
        tag_names = ['dify插件', '测试标签', '瞬间功能']
        
        print("🏷️ 正在处理标签...")
        for tag_name in tag_names:
            # 检查标签是否存在
            tag_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/tags",
                timeout=10
            )
            
            if tag_response.status_code == 200:
                tag_data = tag_response.json()
                existing_tag = None
                
                # 查找现有标签
                for tag in tag_data.get('items', []):
                    if tag.get('spec', {}).get('displayName') == tag_name:
                        existing_tag = tag
                        break
                
                if existing_tag:
                    tag_ids.append(existing_tag['metadata']['name'])
                    print(f"  标签 '{tag_name}' 已存在")
                else:
                    # 创建新标签
                    tag_create_data = {
                        "apiVersion": "content.halo.run/v1alpha1",
                        "kind": "Tag",
                        "metadata": {
                            "generateName": "tag-"
                        },
                        "spec": {
                            "displayName": tag_name,
                            "slug": f"{tag_name.lower().replace(' ', '-')}-{int(time.time())}",
                            "color": "#6366f1",
                            "cover": ""
                        }
                    }
                    
                    create_response = session.post(
                        f"{base_url}/apis/content.halo.run/v1alpha1/tags",
                        data=json.dumps(tag_create_data),
                        timeout=10
                    )
                    
                    if create_response.status_code in [200, 201]:
                        created_tag = create_response.json()
                        tag_id = created_tag['metadata']['name']
                        tag_ids.append(tag_id)
                        print(f"  标签 '{tag_name}' 创建成功")
                    else:
                        print(f"  标签 '{tag_name}' 创建失败")
        
        if not tag_ids:
            print("❌ 没有可用的标签")
            return False
        
        # 创建瞬间，使用标签ID
        print("💭 正在创建瞬间...")
        moment_name = f"moment-{int(time.time())}"
        content = f'测试瞬间标签功能 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        
        moment_data = {
            "apiVersion": "moment.halo.run/v1alpha1",
            "kind": "Moment",
            "metadata": {
                "name": moment_name,
                "generateName": "moment-"
            },
            "spec": {
                "content": {
                    "raw": content,
                    "html": content,
                    "medium": []
                },
                "owner": "jason",
                "tags": tag_ids,  # 使用标签ID而不是名称
                "visible": "PUBLIC",
                "approved": True,
                "allowComment": True
            }
        }
        
        response = session.post(
            f"{base_url}/apis/moment.halo.run/v1alpha1/moments",
            data=json.dumps(moment_data),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 瞬间创建成功，包含 {len(tag_ids)} 个标签")
            print(f"   ID: {result.get('metadata', {}).get('name', moment_name)}")
            print(f"   标签: {', '.join(tag_names)}")
            return True
        else:
            print(f"❌ 瞬间创建失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_post_publish():
    """测试文章发布功能"""
    print("\n" + "="*50)
    print("测试2: 文章发布状态")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    try:
        # 创建并立即发布文章
        title = f'测试文章发布功能 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        content = '这是一篇测试文章，用于验证发布功能是否正常工作。'
        
        post_name = f"post-{int(time.time())}"
        publish_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name
            },
            "spec": {
                "title": title,
                "slug": f"test-post-{int(time.time())}",
                "template": "",
                "cover": "",
                "deleted": False,
                "publish": True,  # 立即发布
                "publishTime": publish_time,  # 设置发布时间
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
                "htmlMetas": []
            }
        }
        
        print(f"创建文章: {title}")
        print("设置为立即发布...")
        
        # 创建文章
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ 文章创建失败: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        post_id = result.get("metadata", {}).get("name", post_name)
        
        # 设置文章内容
        print("设置文章内容...")
        content_data = {
            "raw": content,
            "content": content,
            "rawType": "markdown"
        }
        
        content_response = session.put(
            f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
            data=json.dumps(content_data),
            timeout=30
        )
        
        content_success = content_response.status_code in [200, 201]
        
        # 验证文章发布状态
        print("🔍 验证文章发布状态...")
        verify_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
            timeout=10
        )
        
        if verify_response.status_code == 200:
            post_data = verify_response.json()
            is_published = post_data.get('spec', {}).get('publish', False)
            publish_time = post_data.get('spec', {}).get('publishTime')
            
            print(f"✅ 文章创建成功，ID: {post_id}")
            print(f"   发布状态: {'已发布' if is_published else '草稿'}")
            print(f"   发布时间: {publish_time if publish_time else '未设置'}")
            print(f"   内容设置: {'成功' if content_success else '失败'}")
            
            if is_published and publish_time:
                print("✅ 文章发布功能正常")
                return True
            else:
                print("❌ 文章未正确发布")
                return False
        else:
            print(f"❌ 无法验证文章状态: {verify_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始Bug修复验证测试")
    print("="*50)
    
    test_results = []
    
    # 执行测试
    test_results.append(("瞬间创建标签显示", test_moment_with_tags()))
    test_results.append(("文章发布状态", test_post_publish()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("🎯 测试结果汇总")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！Bug修复验证成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 