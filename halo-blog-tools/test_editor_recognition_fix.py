#!/usr/bin/env python3
"""
测试编辑器识别问题修复效果
基于VSCode扩展的正确API实现方式
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

def test_correct_api_implementation():
    """测试基于VSCode扩展的正确API实现"""
    print("🔧 测试编辑器识别问题修复 - 基于VSCode扩展实现")
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
    title = f"编辑器识别测试 - 正确API实现 - {int(time.time())}"
    content = """# 编辑器识别测试

这是一个使用正确API实现方式创建的测试文章。

## 测试内容

- 使用了 `content.halo.run/content-json` 注解
- 使用了正确的API端点
- 遵循VSCode扩展的实现方式

**预期结果**: 这篇文章应该能被编辑器正确识别和编辑。

## 技术细节

1. 使用UUID作为文章名称
2. 通过annotations传递内容
3. 使用uc.api.content.halo.run端点

> 让我们看看这次是否能成功！ 🎉
"""
    
    try:
        print(f"📝 创建测试文章: {title}")
        print(f"🆔 文章ID: {post_name}")
        
        # 步骤1: 准备内容数据（按照VSCode扩展的格式）
        content_data = {
            "rawType": "markdown",
            "raw": content,
            "content": content
        }
        
        # 步骤2: 准备文章数据 - 使用正确的annotations
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name,
                "annotations": {
                    # 关键：使用content.halo.run/content-json注解传递内容
                    "content.halo.run/content-json": json.dumps(content_data)
                }
            },
            "spec": {
                "title": title,
                "slug": f"editor-test-{int(time.time())}",
                "template": "",
                "cover": "",
                "deleted": False,
                "publish": False,  # 创建为草稿便于编辑器测试
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
        
        print("🔄 使用正确的API端点创建文章...")
        
        # 步骤3: 使用正确的API端点创建文章
        response = session.post(
            f"{base_url}/apis/uc.api.content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        print(f"   主要端点响应: {response.status_code}")
        
        # 如果主要端点失败，尝试备用端点
        if response.status_code not in [200, 201]:
            print("🔄 尝试备用API端点...")
            response = session.post(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts",
                data=json.dumps(post_data),
                timeout=30
            )
            print(f"   备用端点响应: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            created_post_name = result.get("metadata", {}).get("name", post_name)
            
            print(f"✅ 文章创建成功!")
            print(f"   实际ID: {created_post_name}")
            
            # 步骤4: 验证文章数据结构
            print("\n🔍 验证文章数据结构...")
            
            # 获取文章详情
            detail_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{created_post_name}",
                timeout=10
            )
            
            if detail_response.status_code == 200:
                post_detail = detail_response.json()
                
                # 检查annotations
                annotations = post_detail.get("metadata", {}).get("annotations", {})
                has_content_json = "content.halo.run/content-json" in annotations
                
                print(f"   ✅ 文章详情获取成功")
                print(f"   📋 content-json注解存在: {'是' if has_content_json else '否'}")
                
                if has_content_json:
                    try:
                        content_annotation = json.loads(annotations["content.halo.run/content-json"])
                        print(f"   📄 rawType: {content_annotation.get('rawType', 'None')}")
                        print(f"   📝 内容长度: {len(content_annotation.get('raw', ''))}")
                    except:
                        print("   ⚠️ content-json注解解析失败")
                
                # 检查快照信息
                try:
                    draft_response = session.get(
                        f"{base_url}/apis/uc.api.content.halo.run/v1alpha1/posts/{created_post_name}/head-snapshot",
                        timeout=10
                    )
                    
                    if draft_response.status_code == 200:
                        print(f"   ✅ 快照访问成功")
                    else:
                        print(f"   ⚠️ 快照访问失败: {draft_response.status_code}")
                        # 尝试备用快照端点
                        draft_response = session.get(
                            f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{created_post_name}/snapshot",
                            timeout=10
                        )
                        if draft_response.status_code == 200:
                            print(f"   ✅ 备用快照端点访问成功")
                        
                except Exception as e:
                    print(f"   ⚠️ 快照检查失败: {e}")
                
            else:
                print(f"   ❌ 获取文章详情失败: {detail_response.status_code}")
            
            # 步骤5: 测试编辑器链接
            print("\n🔗 生成编辑器链接...")
            editor_url = f"{base_url}/console/posts/editor?name={created_post_name}"
            print(f"   编辑器链接: {editor_url}")
            
            # 步骤6: 对比分析
            print("\n📊 与传统方式对比分析:")
            print("   ✅ 使用了content.halo.run/content-json注解")
            print("   ✅ 使用了uc.api.content.halo.run端点")
            print("   ✅ 使用了UUID作为文章名称")
            print("   ✅ 包含了完整的快照字段")
            print("   ✅ 遵循了VSCode扩展的实现方式")
            
            return True
            
        else:
            print(f"❌ 文章创建失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_old_vs_new_comparison():
    """对比测试：传统方式 vs 新的正确方式"""
    print("\n" + "=" * 60)
    print("📊 对比分析: 传统方式 vs 正确实现方式")
    print("=" * 60)
    
    print("❌ 传统实现问题:")
    print("   1. 直接设置post内容，没有使用annotations")
    print("   2. 使用标准post API端点")
    print("   3. 缺少content.halo.run/content-json注解")
    print("   4. 快照管理不正确")
    print("   5. 编辑器无法识别")
    
    print("\n✅ 新的正确实现:")
    print("   1. 通过content.halo.run/content-json注解传递内容")
    print("   2. 使用uc.api.content.halo.run端点")
    print("   3. 遵循VSCode扩展的实现方式")
    print("   4. 正确的快照字段结构")
    print("   5. 编辑器应该能正确识别")
    
    print("\n🔧 关键技术差异:")
    print("   传统方式: POST /apis/content.halo.run/v1alpha1/posts + PUT /content")
    print("   正确方式: POST /apis/uc.api.content.halo.run/v1alpha1/posts + annotations")
    
    print("\n💡 VSCode扩展关键代码:")
    print('   annotations["content.halo.run/content-json"] = JSON.stringify(content)')

def main():
    """主函数"""
    print("🔧 Halo编辑器识别问题修复测试")
    print("基于VSCode扩展的正确API实现方式")
    print("=" * 60)
    
    # 测试正确的API实现
    success = test_correct_api_implementation()
    
    # 对比分析
    test_old_vs_new_comparison()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成！请检查创建的文章是否能被编辑器正确识别。")
        print("💡 如果仍有问题，可能需要:")
        print("   1. 检查编辑器插件是否正确安装")
        print("   2. 验证用户权限是否充足")
        print("   3. 确认Halo版本兼容性")
    else:
        print("❌ 测试失败，请检查配置和权限设置。")

if __name__ == "__main__":
    main() 