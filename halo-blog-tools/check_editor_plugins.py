#!/usr/bin/env python3
"""
检查Halo CMS编辑器插件状态和内容格式问题
"""

import json
import requests
import time
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

def check_editor_plugins():
    """检查编辑器插件状态"""
    print("🔍 检查编辑器插件状态")
    print("=" * 50)
    
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
        # 1. 检查插件列表
        print("📦 检查已安装的插件...")
        plugins_response = session.get(
            f"{base_url}/apis/plugin.halo.run/v1alpha1/plugins",
            timeout=10
        )
        
        if plugins_response.status_code == 200:
            plugins_data = plugins_response.json()
            plugins = plugins_data.get('items', [])
            
            print(f"   总插件数: {len(plugins)}")
            
            # 查找编辑器相关插件
            editor_plugins = []
            for plugin in plugins:
                plugin_name = plugin.get('metadata', {}).get('name', '')
                plugin_enabled = plugin.get('status', {}).get('phase', '') == 'STARTED'
                plugin_display_name = plugin.get('spec', {}).get('displayName', plugin_name)
                
                # 检查是否是编辑器插件
                if any(keyword in plugin_name.lower() for keyword in ['editor', 'stackedit', 'bytemd', 'vditor', 'cherry', 'md']):
                    editor_plugins.append({
                        'name': plugin_name,
                        'display_name': plugin_display_name,
                        'enabled': plugin_enabled,
                        'phase': plugin.get('status', {}).get('phase', 'Unknown')
                    })
            
            if editor_plugins:
                print(f"\n📝 发现编辑器插件 ({len(editor_plugins)} 个):")
                for plugin in editor_plugins:
                    status_icon = "✅" if plugin['enabled'] else "❌"
                    print(f"   {status_icon} {plugin['display_name']} ({plugin['name']})")
                    print(f"      状态: {plugin['phase']}")
            else:
                print("   ⚠️ 未发现编辑器插件")
                
                # 列出所有插件，帮助识别
                print(f"\n📋 所有已安装插件:")
                for plugin in plugins[:10]:  # 只显示前10个
                    plugin_name = plugin.get('metadata', {}).get('name', '')
                    plugin_enabled = plugin.get('status', {}).get('phase', '') == 'STARTED'
                    plugin_display_name = plugin.get('spec', {}).get('displayName', plugin_name)
                    status_icon = "✅" if plugin_enabled else "❌"
                    print(f"   {status_icon} {plugin_display_name} ({plugin_name})")
        else:
            print(f"   ❌ 无法获取插件列表: {plugins_response.status_code}")
            
        # 2. 检查内容类型支持
        print(f"\n📄 检查内容类型支持...")
        
        # 尝试获取系统设置或配置信息
        try:
            # 检查系统配置
            config_endpoints = [
                "/apis/api.console.halo.run/v1alpha1/systems/states",
                "/apis/api.console.halo.run/v1alpha1/configs",
                "/apis/config.halo.run/v1alpha1/configmaps"
            ]
            
            for endpoint in config_endpoints:
                try:
                    config_response = session.get(f"{base_url}{endpoint}", timeout=10)
                    if config_response.status_code == 200:
                        print(f"   ✅ 系统配置可访问: {endpoint}")
                        break
                except:
                    continue
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def test_content_format_compatibility():
    """测试不同内容格式的兼容性"""
    print("\n🧪 测试内容格式兼容性")
    print("=" * 50)
    
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
    
    # 测试不同的内容格式
    test_cases = [
        {
            "name": "标准Markdown",
            "rawType": "markdown",
            "content": "# 测试标题\n\n这是一个测试内容。\n\n- 列表项1\n- 列表项2"
        },
        {
            "name": "HTML格式",
            "rawType": "html", 
            "content": "<h1>测试标题</h1><p>这是一个测试内容。</p><ul><li>列表项1</li><li>列表项2</li></ul>"
        },
        {
            "name": "富文本格式",
            "rawType": "richtext",
            "content": "# 测试标题\n\n这是一个测试内容。"
        }
    ]
    
    successful_formats = []
    
    for test_case in test_cases:
        print(f"\n📝 测试 {test_case['name']} (rawType: {test_case['rawType']})...")
        
        try:
            # 创建测试文章
            post_name = f"format-test-{test_case['rawType']}-{int(time.time())}"
            
            post_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": post_name
                },
                "spec": {
                    "title": f"格式测试 - {test_case['name']}",
                    "slug": post_name,
                    "template": "",
                    "cover": "",
                    "deleted": False,
                    "publish": False,  # 只保存为草稿
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
            
            # 创建文章
            create_response = session.post(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts",
                data=json.dumps(post_data),
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                print(f"   ✅ 文章创建成功")
                
                # 设置内容
                content_data = {
                    "raw": test_case["content"],
                    "content": test_case["content"],
                    "rawType": test_case["rawType"]
                }
                
                content_response = session.put(
                    f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                    data=json.dumps(content_data),
                    timeout=30
                )
                
                if content_response.status_code in [200, 201]:
                    print(f"   ✅ 内容设置成功 - {test_case['name']} 格式支持")
                    successful_formats.append(test_case['rawType'])
                    
                    # 尝试获取文章详情，检查是否能正常访问编辑器
                    detail_response = session.get(
                        f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_name}",
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        print(f"   ✅ 文章可正常访问")
                        print(f"   🔗 编辑链接: {base_url}/console/posts/editor?name={post_name}")
                    else:
                        print(f"   ⚠️ 文章访问异常: {detail_response.status_code}")
                else:
                    print(f"   ❌ 内容设置失败: {content_response.status_code}")
                    try:
                        error_data = content_response.json()
                        print(f"   错误详情: {error_data}")
                    except:
                        print(f"   错误文本: {content_response.text}")
            else:
                print(f"   ❌ 文章创建失败: {create_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    print(f"\n📊 格式兼容性测试结果:")
    print(f"   支持的格式: {', '.join(successful_formats) if successful_formats else '无'}")
    
    return len(successful_formats) > 0

def check_markdown_editor_requirements():
    """检查Markdown编辑器的具体要求"""
    print("\n📋 Markdown编辑器要求分析")
    print("=" * 50)
    
    print("🔍 常见的Halo编辑器插件:")
    print("   1. StackEdit Editor - 支持Markdown")
    print("   2. ByteMD Editor - 字节跳动的Markdown编辑器")
    print("   3. Vditor Editor - 一款浏览器端的Markdown编辑器")
    print("   4. CherryMarkdown Editor - 腾讯的Markdown编辑器")
    print("   5. 默认编辑器 - Halo内置编辑器")
    
    print("\n📝 内容格式要求:")
    print("   - rawType: 'markdown' (必须)")
    print("   - raw: 原始Markdown文本")
    print("   - content: 处理后的内容(通常与raw相同)")
    print("   - 确保用户有编辑权限")
    
    print("\n🔧 可能的解决方案:")
    print("   1. 安装Markdown编辑器插件")
    print("   2. 检查插件是否启用")
    print("   3. 验证内容格式是否正确")
    print("   4. 确认用户权限")

def main():
    """主函数"""
    print("🔧 Halo编辑器诊断工具")
    print("=" * 60)
    
    # 检查插件状态
    check_editor_plugins()
    
    # 测试内容格式
    test_content_format_compatibility()
    
    # 显示编辑器要求
    check_markdown_editor_requirements()
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成")
    print("   如果仍有问题，请检查:")
    print("   1. 是否安装了Markdown编辑器插件")
    print("   2. 插件是否处于启用状态")
    print("   3. 用户是否有足够的编辑权限")

if __name__ == "__main__":
    main() 