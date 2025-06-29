#!/usr/bin/env python3
"""
测试resourceVersion处理，解决409冲突问题
关键：正确处理Halo的资源版本控制机制
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

def test_resource_version_handling():
    """测试正确的resourceVersion处理"""
    print("🔧 测试resourceVersion处理 - 解决409冲突")
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
    title = f"ResourceVersion测试 - {int(time.time())}"
    content = """# ResourceVersion处理测试

这是测试正确处理Halo资源版本控制的文章。

## 解决方案

1. 创建文章时直接包含content-json annotation
2. 如果需要更新，正确获取和使用resourceVersion
3. 避免409冲突错误

**预期结果**: content-json注解能正确保存，编辑器能识别。
"""
    
    try:
        print(f"📝 方案1: 创建时直接包含content-json annotation")
        
        # 准备内容数据
        content_data = {
            "rawType": "markdown",
            "raw": content,
            "content": content
        }
        
        # 创建文章时直接包含content-json annotation
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name,
                "annotations": {
                    # 创建时就包含content-json注解
                    "content.halo.run/content-json": json.dumps(content_data)
                }
            },
            "spec": {
                "title": title,
                "slug": f"resourceversion-test-{int(time.time())}",
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
        
        print(f"   标题: {title}")
        print(f"   ID: {post_name}")
        print(f"   Content-json长度: {len(json.dumps(content_data))} 字符")
        
        # 使用标准端点创建文章
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        print(f"   创建响应: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            created_post_name = result.get("metadata", {}).get("name", post_name)
            print(f"   ✅ 文章创建成功! ID: {created_post_name}")
            
            # 立即验证annotations是否被保存
            print(f"\n🔍 验证annotations保存情况")
            
            verify_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{created_post_name}",
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
                        print(f"   ✅ 方案1成功！直接创建包含annotations的文章")
                        
                        # 生成编辑器链接
                        editor_url = f"{base_url}/console/posts/editor?name={created_post_name}"
                        print(f"\n🔗 编辑器链接: {editor_url}")
                        
                        return True
                        
                    except Exception as e:
                        print(f"   ⚠️ content-json注解解析失败: {e}")
                else:
                    print(f"   ❌ 方案1失败，annotations未被保存")
                    
                    # 尝试方案2：获取正确的resourceVersion后更新
                    print(f"\n📝 方案2: 使用正确的resourceVersion更新")
                    
                    current_resource_version = final_post.get("metadata", {}).get("resourceVersion")
                    print(f"   当前resourceVersion: {current_resource_version}")
                    
                    if current_resource_version:
                        # 更新文章，包含正确的resourceVersion
                        updated_post = final_post.copy()
                        if "annotations" not in updated_post["metadata"]:
                            updated_post["metadata"]["annotations"] = {}
                        
                        updated_post["metadata"]["annotations"]["content.halo.run/content-json"] = json.dumps(content_data)
                        
                        update_response = session.put(
                            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{created_post_name}",
                            data=json.dumps(updated_post),
                            timeout=30
                        )
                        
                        print(f"   更新响应: {update_response.status_code}")
                        
                        if update_response.status_code == 200:
                            print(f"   ✅ 方案2成功！使用resourceVersion更新")
                            
                            # 再次验证
                            final_verify_response = session.get(
                                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{created_post_name}",
                                timeout=10
                            )
                            
                            if final_verify_response.status_code == 200:
                                final_final_post = final_verify_response.json()
                                final_annotations = final_final_post.get("metadata", {}).get("annotations", {})
                                final_has_content_json = "content.halo.run/content-json" in final_annotations
                                
                                print(f"   📋 最终content-json注解存在: {'是' if final_has_content_json else '否'}")
                                
                                return final_has_content_json
                        else:
                            print(f"   ❌ 方案2失败: {update_response.status_code}")
                            try:
                                error_data = update_response.json()
                                print(f"   错误详情: {error_data}")
                            except:
                                print(f"   错误文本: {update_response.text[:200]}")
            else:
                print(f"   ❌ 无法验证文章: {verify_response.status_code}")
                
        else:
            print(f"   ❌ 文章创建失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   错误文本: {response.text[:200]}")
        
        return False
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def test_alternative_approach():
    """测试替代方案：使用不同的API端点"""
    print(f"\n📝 方案3: 测试替代API端点")
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 测试使用uc端点创建内容
    post_name = str(uuid.uuid4())
    title = f"UC端点测试 - {int(time.time())}"
    content = "# UC端点测试\n\n使用UC API端点创建文章的测试。"
    
    content_data = {
        "rawType": "markdown",
        "raw": content,
        "content": content
    }
    
    # 使用UC端点的不同payload格式
    uc_post_data = {
        "post": {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name,
                "annotations": {}
            },
            "spec": {
                "title": title,
                "slug": f"uc-test-{int(time.time())}",
                "deleted": False,
                "publish": False,
                "owner": "jason",
                "categories": [],
                "tags": []
            }
        },
        "content": content_data
    }
    
    try:
        uc_response = session.post(
            f"{base_url}/apis/uc.api.content.halo.run/v1alpha1/posts",
            data=json.dumps(uc_post_data),
            timeout=30
        )
        
        print(f"   UC端点响应: {uc_response.status_code}")
        
        if uc_response.status_code in [200, 201]:
            print(f"   ✅ UC端点创建成功")
            result = uc_response.json()
            # 这里可以进一步验证
            return True
        else:
            print(f"   ❌ UC端点失败: {uc_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ UC端点测试异常: {e}")
    
    return False

def main():
    """主函数"""
    print("🔧 Halo编辑器识别问题 - ResourceVersion处理测试")
    print("解决409冲突和annotation保存问题")
    print("=" * 60)
    
    # 测试resourceVersion处理
    success1 = test_resource_version_handling()
    
    # 测试替代方案
    success2 = test_alternative_approach()
    
    print("\n" + "=" * 60)
    if success1 or success2:
        print("🎉 找到了有效的解决方案！")
        if success1:
            print("   ✅ 方案1或2成功：直接创建或正确更新annotations")
        if success2:
            print("   ✅ 方案3成功：UC端点创建")
        print("💡 文章应该能被编辑器正确识别。")
    else:
        print("❌ 所有方案都失败，需要进一步研究API规范。")

if __name__ == "__main__":
    main() 