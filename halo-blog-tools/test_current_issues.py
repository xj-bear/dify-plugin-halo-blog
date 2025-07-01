#!/usr/bin/env python3
"""
测试当前Halo博客工具的问题
1. 文章创建无法在浏览器编辑
2. 文章更新实际未更新
"""

import requests
import json
import time
import uuid
from datetime import datetime

# 测试配置 - 请根据实际情况修改
BASE_URL = "https://blog.u2u.fun"
ACCESS_TOKEN = "pat_1234567890abcdef"  # 请替换为实际的token

# 如果没有配置token，尝试从环境变量获取
import os
if ACCESS_TOKEN == "pat_1234567890abcdef":
    ACCESS_TOKEN = os.getenv("HALO_ACCESS_TOKEN", ACCESS_TOKEN)

def test_post_creation_editor_compatibility():
    """测试文章创建的编辑器兼容性"""
    print("🧪 测试1: 文章创建编辑器兼容性")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Dify-Halo-Plugin-Test/1.0'
    })
    
    # 创建测试文章
    post_name = f"test-editor-{int(time.time())}"
    content = "# 测试编辑器兼容性\n\n这是一篇测试文章，用于验证编辑器兼容性。\n\n- 项目1\n- 项目2\n- 项目3"
    
    content_data = {
        "rawType": "markdown",
        "raw": content,
        "content": content
    }
    
    post_data = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "name": post_name,
            "annotations": {
                "content.halo.run/content-json": json.dumps(content_data),
                "content.halo.run/preferred-editor": "default",
                "content.halo.run/content-type": "markdown"
            }
        },
        "spec": {
            "title": "编辑器兼容性测试文章",
            "slug": f"test-editor-{int(time.time())}",
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
            "htmlMetas": [],
            "baseSnapshot": "",
            "headSnapshot": "",
            "releaseSnapshot": ""
        }
    }
    
    try:
        # 创建文章
        response = session.post(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts",
            json=post_data,
            timeout=30
        )
        
        print(f"📝 创建文章响应: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            post_id = result["metadata"]["name"]
            print(f"✅ 文章创建成功: {post_id}")
            
            # 验证编辑器兼容性注解
            annotations = result.get("metadata", {}).get("annotations", {})
            content_json = annotations.get("content.halo.run/content-json")
            preferred_editor = annotations.get("content.halo.run/preferred-editor")
            content_type = annotations.get("content.halo.run/content-type")
            
            print(f"🔍 编辑器兼容性检查:")
            print(f"   content-json: {'✅' if content_json else '❌'}")
            print(f"   preferred-editor: {'✅' if preferred_editor else '❌'}")
            print(f"   content-type: {'✅' if content_type else '❌'}")
            
            # 测试编辑器内容API
            content_response = session.get(
                f"{BASE_URL}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
                timeout=10
            )
            
            print(f"📄 编辑器内容API: {content_response.status_code}")
            if content_response.status_code == 200:
                content_data = content_response.json()
                print(f"   内容长度: {len(content_data.get('raw', ''))}")
                print(f"   rawType: {content_data.get('rawType', 'N/A')}")
            elif content_response.status_code == 500:
                print("   ⚠️ 500错误（可能是正常现象）")
            
            print(f"🔗 编辑器链接: {BASE_URL}/console/posts/editor?name={post_id}")
            return post_id
            
        else:
            print(f"❌ 文章创建失败: {response.status_code}")
            print(f"   错误详情: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return None

def test_post_update_functionality(post_id):
    """测试文章更新功能"""
    if not post_id:
        print("⏭️ 跳过更新测试（没有可用的文章ID）")
        return
        
    print("\n🧪 测试2: 文章更新功能")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'User-Agent': 'Dify-Halo-Plugin-Test/1.0'
    })
    
    try:
        # 获取当前文章数据
        get_response = session.get(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{post_id}",
            timeout=30
        )
        
        if get_response.status_code != 200:
            print(f"❌ 获取文章失败: {get_response.status_code}")
            return
            
        current_data = get_response.json()
        print(f"📖 获取文章成功: {current_data['spec']['title']}")
        
        # 更新文章内容
        new_content = f"# 更新测试\n\n这是更新后的内容，时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 更新项目\n\n- 标题已更新\n- 内容已更新\n- 时间戳: {int(time.time())}"
        new_title = f"更新测试文章 - {datetime.now().strftime('%H:%M:%S')}"
        
        # 准备更新数据
        update_data = current_data.copy()
        update_data["spec"]["title"] = new_title
        
        # 更新content-json注解
        content_data = {
            "rawType": "markdown",
            "raw": new_content,
            "content": new_content
        }
        
        if "annotations" not in update_data["metadata"]:
            update_data["metadata"]["annotations"] = {}
            
        update_data["metadata"]["annotations"]["content.halo.run/content-json"] = json.dumps(content_data)
        
        # 发送更新请求
        update_response = session.put(
            f"{BASE_URL}/apis/content.halo.run/v1alpha1/posts/{post_id}",
            json=update_data,
            timeout=30
        )
        
        print(f"📝 更新文章响应: {update_response.status_code}")
        if update_response.status_code in [200, 201]:
            result = update_response.json()
            updated_title = result["spec"]["title"]
            print(f"✅ 文章更新成功")
            print(f"   新标题: {updated_title}")
            
            # 验证内容是否真正更新
            verify_response = session.get(
                f"{BASE_URL}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
                timeout=10
            )
            
            print(f"🔍 内容验证: {verify_response.status_code}")
            if verify_response.status_code == 200:
                verify_content = verify_response.json()
                verify_raw = verify_content.get('raw', '')
                if new_content in verify_raw:
                    print("✅ 内容更新验证成功")
                else:
                    print("❌ 内容更新验证失败 - 内容未实际更新")
                    print(f"   期望包含: {new_content[:50]}...")
                    print(f"   实际内容: {verify_raw[:50]}...")
            elif verify_response.status_code == 500:
                print("⚠️ 内容验证返回500（可能需要其他方法验证）")
                
        else:
            print(f"❌ 文章更新失败: {update_response.status_code}")
            print(f"   错误详情: {update_response.text}")
            
    except Exception as e:
        print(f"❌ 更新测试异常: {e}")

def main():
    """主测试函数"""
    print("🔧 Halo博客工具问题诊断测试")
    print("=" * 60)
    print(f"🌐 测试环境: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试1: 文章创建编辑器兼容性
    post_id = test_post_creation_editor_compatibility()
    
    # 测试2: 文章更新功能
    test_post_update_functionality(post_id)
    
    print("\n📊 测试总结")
    print("=" * 50)
    print("请根据上述测试结果分析问题:")
    print("1. 编辑器兼容性注解是否正确设置")
    print("2. 文章更新是否真正生效")
    print("3. Console Content API是否正常工作")

if __name__ == "__main__":
    main()
