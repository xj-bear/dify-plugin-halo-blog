#!/usr/bin/env python3
"""
测试完整的Halo文章创建API流程
基于VSCode扩展的完整实现，包括快照更新
"""

import json
import requests
import time
import uuid
from datetime import datetime

def load_config():
    """加载配置"""
    try:
        with open('key.txt', 'r', encoding='utf-8') as f:
            pat_token = f.read().strip()
        return "https://blog.u2u.fun", pat_token
    except FileNotFoundError:
        print("❌ 找不到 key.txt 文件")
        return None, None

def test_complete_vscode_flow():
    """测试完整的VSCode扩展流程"""
    print("🔧 测试完整的VSCode扩展API流程")
    print("=" * 60)
    
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
    
    # 测试数据
    post_name = str(uuid.uuid4())
    title = f"完整API流程测试 - {int(time.time())}"
    content = """# 完整API流程测试

这是测试VSCode扩展完整API流程的文章。

## 测试步骤

1. 创建文章
2. 获取draft snapshot
3. 更新draft snapshot with content-json annotation
4. 验证编辑器识别

**预期结果**: 编辑器能正确识别和编辑这篇文章。
"""
    
    try:
        print(f"📝 第1步: 创建基础文章")
        print(f"   标题: {title}")
        print(f"   ID: {post_name}")
        
        # 第1步: 创建基础文章（不包含content-json annotation）
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name,
                "annotations": {}  # 先不设置content-json
            },
            "spec": {
                "title": title,
                "slug": f"complete-test-{int(time.time())}",
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
        
        # 尝试多个端点创建文章
        endpoints = [
            "/apis/uc.api.content.halo.run/v1alpha1/posts",
            "/apis/content.halo.run/v1alpha1/posts"
        ]
        
        create_success = False
        for endpoint in endpoints:
            try:
                response = session.post(
                    f"{base_url}{endpoint}",
                    data=json.dumps(post_data),
                    timeout=30
                )
                print(f"   尝试端点 {endpoint}: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    created_post_name = result.get("metadata", {}).get("name", post_name)
                    print(f"   ✅ 文章创建成功! ID: {created_post_name}")
                    create_success = True
                    post_name = created_post_name
                    break
                    
            except Exception as e:
                print(f"   ❌ 端点 {endpoint} 失败: {e}")
                continue
        
        if not create_success:
            print("❌ 所有创建端点都失败")
            return False
        
        # 第2步: 获取draft snapshot
        print(f"\n📄 第2步: 获取draft snapshot")
        
        draft_endpoints = [
            f"/apis/uc.api.content.halo.run/v1alpha1/posts/{post_name}/draft",
            f"/apis/api.console.halo.run/v1alpha1/posts/{post_name}/draft"
        ]
        
        snapshot = None
        for endpoint in draft_endpoints:
            try:
                draft_response = session.get(
                    f"{base_url}{endpoint}?patched=true",
                    timeout=10
                )
                print(f"   尝试获取snapshot {endpoint}: {draft_response.status_code}")
                
                if draft_response.status_code == 200:
                    snapshot = draft_response.json()
                    print(f"   ✅ 获取snapshot成功")
                    break
                    
            except Exception as e:
                print(f"   ❌ 获取snapshot失败: {e}")
                continue
        
        if not snapshot:
            print("   ⚠️ 无法获取snapshot，尝试创建新的")
            # 如果无法获取snapshot，我们尝试直接更新文章的annotations
            
        # 第3步: 更新文章annotations with content-json
        print(f"\n🔄 第3步: 更新文章annotations")
        
        content_data = {
            "rawType": "markdown",
            "raw": content,
            "content": content
        }
        
        # 获取当前文章数据
        get_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_name}",
            timeout=10
        )
        
        if get_response.status_code == 200:
            current_post = get_response.json()
            
            # 更新annotations
            if "annotations" not in current_post["metadata"]:
                current_post["metadata"]["annotations"] = {}
            
            current_post["metadata"]["annotations"]["content.halo.run/content-json"] = json.dumps(content_data)
            
            # 更新文章
            update_response = session.put(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_name}",
                data=json.dumps(current_post),
                timeout=30
            )
            
            print(f"   更新文章annotations: {update_response.status_code}")
            
            if update_response.status_code == 200:
                print(f"   ✅ annotations更新成功")
            else:
                print(f"   ❌ annotations更新失败: {update_response.text[:200]}")
        
        # 第4步: 如果有snapshot，更新snapshot
        if snapshot:
            print(f"\n📋 第4步: 更新draft snapshot")
            
            # 更新snapshot的annotations
            if "annotations" not in snapshot["metadata"]:
                snapshot["metadata"]["annotations"] = {}
            
            snapshot["metadata"]["annotations"]["content.halo.run/content-json"] = json.dumps(content_data)
            
            # 尝试更新snapshot
            snapshot_update_endpoints = [
                f"/apis/uc.api.content.halo.run/v1alpha1/posts/{post_name}/draft",
                f"/apis/api.console.halo.run/v1alpha1/posts/{post_name}/draft"
            ]
            
            for endpoint in snapshot_update_endpoints:
                try:
                    snapshot_response = session.put(
                        f"{base_url}{endpoint}",
                        data=json.dumps(snapshot),
                        timeout=30
                    )
                    print(f"   更新snapshot {endpoint}: {snapshot_response.status_code}")
                    
                    if snapshot_response.status_code == 200:
                        print(f"   ✅ snapshot更新成功")
                        break
                        
                except Exception as e:
                    print(f"   ❌ 更新snapshot失败: {e}")
                    continue
        
        # 第5步: 验证最终结果
        print(f"\n🔍 第5步: 验证最终结果")
        
        # 重新获取文章详情
        verify_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_name}",
            timeout=10
        )
        
        if verify_response.status_code == 200:
            final_post = verify_response.json()
            annotations = final_post.get("metadata", {}).get("annotations", {})
            has_content_json = "content.halo.run/content-json" in annotations
            
            print(f"   📋 content-json注解存在: {'是' if has_content_json else '否'}")
            
            if has_content_json:
                try:
                    content_annotation = json.loads(annotations["content.halo.run/content-json"])
                    print(f"   📄 rawType: {content_annotation.get('rawType', 'None')}")
                    print(f"   📝 内容长度: {len(content_annotation.get('raw', ''))}")
                    print(f"   ✅ annotations验证成功!")
                except:
                    print("   ⚠️ content-json注解解析失败")
            
            # 生成编辑器链接
            editor_url = f"{base_url}/console/posts/editor?name={post_name}"
            print(f"\n🔗 编辑器链接: {editor_url}")
            
            return has_content_json
        else:
            print(f"   ❌ 无法验证最终结果: {verify_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Halo编辑器识别问题 - 完整API流程测试")
    print("模拟VSCode扩展的完整实现流程")
    print("=" * 60)
    
    success = test_complete_vscode_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 完整流程测试成功！content-json注解已正确保存。")
        print("💡 文章应该能被编辑器正确识别。")
    else:
        print("❌ 流程测试失败，content-json注解未能正确保存。")
        print("💡 可能需要进一步调试API调用顺序。")

if __name__ == "__main__":
    main() 