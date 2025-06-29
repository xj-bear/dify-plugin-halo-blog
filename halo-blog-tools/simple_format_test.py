#!/usr/bin/env python3
"""
最简化的格式测试 - 专注于创建编辑器可识别的文章
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

def create_simple_test():
    """创建最简单的可编辑文章"""
    print("🔧 创建最简单的可编辑文章测试")
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
    
    # 最简单的纯文本内容
    test_content = "这是一个简单的纯文本测试。\n\n请检查编辑器是否能够正确识别和编辑这段内容。"
    post_name = f"simple-test-{int(time.time())}"
    
    print(f"📝 创建文章: {post_name}")
    print(f"内容: {test_content[:50]}...")
    
    # 1. 创建文章
    post_data = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "name": post_name
        },
        "spec": {
            "title": f"简单格式测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
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
    
    try:
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"❌ 文章创建失败: {create_response.status_code}")
            return False
            
        print(f"✅ 文章创建成功")
        
        # 2. 设置内容 - 尝试最简单的格式
        content_data = {
            "raw": test_content,
            "content": test_content,
            "rawType": "markdown"
        }
        
        content_response = session.put(
            f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
            data=json.dumps(content_data),
            timeout=30
        )
        
        print(f"📤 内容设置响应: {content_response.status_code}")
        
        if content_response.status_code in [200, 201]:
            print(f"✅ 内容设置成功")
            edit_url = f"{base_url}/console/posts/editor?name={post_name}"
            print(f"🔗 编辑链接: {edit_url}")
            print(f"")
            print(f"📋 请手动访问编辑链接检查:")
            print(f"   1. 文章是否存在")
            print(f"   2. 内容是否正确显示")
            print(f"   3. 编辑器是否能正常编辑")
            print(f"   4. 是否显示'未找到符合格式的编辑器'错误")
            
            return True
        else:
            print(f"❌ 内容设置失败: {content_response.status_code}")
            try:
                error_info = content_response.json()
                print(f"错误信息: {error_info}")
            except:
                print(f"错误文本: {content_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 操作异常: {e}")
        return False

def main():
    """主函数"""
    print("🎯 最简化文章格式测试")
    print("=" * 60)
    
    success = create_simple_test()
    
    if success:
        print(f"\n✅ 测试文章创建成功")
        print(f"💡 现在请:")
        print(f"   1. 访问上面的编辑链接")
        print(f"   2. 查看编辑器是否正常工作")
        print(f"   3. 确认内容格式是否正确")
        print(f"   4. 反馈测试结果")
    else:
        print(f"\n❌ 测试失败，请检查配置和网络")

if __name__ == "__main__":
    main() 