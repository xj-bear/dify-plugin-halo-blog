#!/usr/bin/env python3
"""
通过Content API读取文章spec信息
检查内容是否正确保存，以及编辑器能否识别
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

def check_article_via_content_api():
    """通过Content API检查文章信息"""
    print("🔍 通过Content API检查文章内容状态")
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
    
    # 检查我们创建的文章
    test_articles = [
        "simple-test-1751214662",
        "browser-like-test-1751214901"  
    ]
    
    for article_id in test_articles:
        print(f"\n📄 检查文章: {article_id}")
        print(f"{'=' * 40}")
        
        try:
            # 通过Content API获取文章信息
            response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{article_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                article_data = response.json()
                print(f"✅ 文章信息获取成功")
                
                # 分析spec信息
                spec = article_data.get("spec", {})
                metadata = article_data.get("metadata", {})
                
                print(f"📋 基本信息:")
                print(f"   名称: {metadata.get('name', 'N/A')}")
                print(f"   标题: {spec.get('title', 'N/A')}")
                print(f"   所有者: {spec.get('owner', 'N/A')}")
                print(f"   发布状态: {spec.get('publish', 'N/A')}")
                print(f"   模板: {spec.get('template', 'N/A')}")
                
                # 检查是否有headSnapshot字段（这可能包含内容信息）
                if 'headSnapshot' in spec:
                    print(f"   headSnapshot: {spec['headSnapshot']}")
                
                # 检查是否有baseSnapshot字段
                if 'baseSnapshot' in spec:
                    print(f"   baseSnapshot: {spec['baseSnapshot']}")
                
                # 检查是否有releaseSnapshot字段
                if 'releaseSnapshot' in spec:
                    print(f"   releaseSnapshot: {spec['releaseSnapshot']}")
                
                # 保存完整数据以供分析
                filename = f"article_spec_{article_id}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=2)
                print(f"💾 完整数据已保存到: {filename}")
                
                # 生成编辑链接
                edit_url = f"{base_url}/console/posts/editor?name={article_id}"
                print(f"🔗 编辑链接: {edit_url}")
                
            else:
                print(f"❌ 文章信息获取失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 检查异常: {e}")

def create_simple_markdown_test():
    """创建一个简单的Markdown测试文章"""
    print(f"\n🆕 创建简单的Markdown测试文章")
    print("=" * 50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return None
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    post_name = f"markdown-test-{int(time.time())}"
    test_content = """# 这是一个测试标题

这是一段简单的Markdown内容。

## 二级标题

- 列表项 1
- 列表项 2

**粗体文本** 和 *斜体文本*

这个测试用于验证编辑器能否正确识别Markdown内容。"""
    
    print(f"📝 创建文章: {post_name}")
    
    try:
        # 1. 创建文章
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name
            },
            "spec": {
                "title": f"Markdown编辑器测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
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
            return None
            
        print(f"✅ 文章创建成功")
        
        # 2. 设置Markdown内容
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
            print(f"✅ Markdown内容设置成功")
            edit_url = f"{base_url}/console/posts/editor?name={post_name}"
            print(f"🔗 编辑链接: {edit_url}")
            print(f"📝 内容长度: {len(test_content)} 字符")
            return post_name
        else:
            print(f"❌ 内容设置失败: {content_response.status_code}")
            try:
                error_info = content_response.json()
                print(f"错误信息: {error_info}")
            except:
                print(f"错误文本: {content_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建异常: {e}")
        return None

def main():
    """主函数"""
    print("🔧 Content API文章检查和Markdown测试")
    print("=" * 70)
    
    # 检查现有文章
    check_article_via_content_api()
    
    # 创建新的Markdown测试
    new_article = create_simple_markdown_test()
    
    if new_article:
        print(f"\n🎯 测试完成")
        print(f"✅ 已创建新的Markdown测试文章: {new_article}")
        print(f"💡 请手动访问编辑链接测试编辑器功能")
        print(f"📋 检查要点:")
        print(f"   1. 编辑器是否正常加载")
        print(f"   2. Markdown内容是否正确显示")
        print(f"   3. 是否还提示'未找到符合格式的编辑器'")
        print(f"   4. 能否正常编辑和保存")
    else:
        print(f"\n❌ Markdown测试创建失败")

if __name__ == "__main__":
    main() 