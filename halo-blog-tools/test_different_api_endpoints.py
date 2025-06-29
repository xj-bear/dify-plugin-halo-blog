#!/usr/bin/env python3
"""
测试不同的API端点和方法
尝试模仿浏览器手动创建文章的方式
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

def test_content_read_endpoints():
    """测试不同的内容读取端点"""
    print("🔍 测试不同的内容读取API端点")
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
    
    # 测试文章ID
    test_article = "simple-test-1751214662"
    
    # 不同的API端点
    endpoints = [
        {
            "name": "Console API v1alpha1",
            "url": f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{test_article}/content"
        },
        {
            "name": "Public API v1alpha1", 
            "url": f"{base_url}/apis/api.halo.run/v1alpha1/posts/{test_article}/content"
        },
        {
            "name": "Content API v1alpha1",
            "url": f"{base_url}/apis/content.halo.run/v1alpha1/posts/{test_article}"
        },
        {
            "name": "UC API posts",
            "url": f"{base_url}/apis/uc.api.console.halo.run/v1alpha1/posts/{test_article}"
        },
        {
            "name": "UC API content",
            "url": f"{base_url}/apis/uc.api.console.halo.run/v1alpha1/posts/{test_article}/content"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            response = session.get(endpoint['url'], timeout=30)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功获取数据")
                
                # 检查是否包含内容信息
                if 'raw' in data:
                    print(f"   📝 包含raw内容，长度: {len(data.get('raw', ''))}")
                elif 'spec' in data:
                    print(f"   📋 包含spec信息")
                else:
                    print(f"   ℹ️  其他格式数据")
                    
            elif response.status_code == 404:
                print(f"   ❌ 资源不存在")
            elif response.status_code == 500:
                print(f"   ❌ 服务器内部错误")
            else:
                print(f"   ❌ 其他错误: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

def test_browser_like_creation():
    """测试模仿浏览器的创建方式"""
    print(f"\n🌐 模仿浏览器手动创建文章的方式")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    # 添加更多浏览器相关的请求头
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    })
    
    test_content = "这是模仿浏览器创建的测试文章。\n\n内容应该可以被编辑器正确识别。"
    post_name = f"browser-like-test-{int(time.time())}"
    
    print(f"📝 创建文章: {post_name}")
    
    try:
        # 1. 创建文章（使用更简单的结构）
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name,
                "annotations": {}
            },
            "spec": {
                "title": f"浏览器模拟测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
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
                "owner": "jason"
            }
        }
        
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"❌ 文章创建失败: {create_response.status_code}")
            print(f"错误信息: {create_response.text}")
            return False
            
        print(f"✅ 文章创建成功")
        
        # 2. 尝试不同的内容设置方法
        content_methods = [
            {
                "name": "标准方法",
                "data": {
                    "raw": test_content,
                    "content": test_content,
                    "rawType": "markdown"
                }
            },
            {
                "name": "HTML内容",
                "data": {
                    "raw": test_content.replace('\n', '<br>'),
                    "content": test_content.replace('\n', '<br>'),
                    "rawType": "html"
                }
            },
            {
                "name": "富文本",
                "data": {
                    "raw": test_content,
                    "content": test_content,
                    "rawType": "richtext"
                }
            }
        ]
        
        for i, method in enumerate(content_methods, 1):
            print(f"\n📤 方法 {i}: {method['name']}")
            
            content_response = session.put(
                f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                data=json.dumps(method['data']),
                timeout=30
            )
            
            print(f"   状态码: {content_response.status_code}")
            
            if content_response.status_code in [200, 201]:
                print(f"   ✅ 内容设置成功")
                
                # 立即验证是否能读取
                print("   🔍 验证内容保存...")
                time.sleep(1)  # 等待一秒
                
                verify_response = session.get(
                    f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    print("   ✅ 内容读取成功，这个方法有效！")
                    edit_url = f"{base_url}/console/posts/editor?name={post_name}"
                    print(f"   🔗 编辑链接: {edit_url}")
                    return True
                else:
                    print(f"   ❌ 内容读取失败: {verify_response.status_code}")
            else:
                print(f"   ❌ 内容设置失败: {content_response.status_code}")
                try:
                    error_info = content_response.json()
                    print(f"   错误: {error_info}")
                except:
                    print(f"   错误文本: {content_response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ 创建异常: {e}")
        return False

def test_minimal_approach():
    """测试最小化方法"""
    print(f"\n🎯 测试最小化创建方法")
    print("=" * 50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    })
    
    post_name = f"minimal-test-{int(time.time())}"
    
    # 最小化文章数据
    minimal_post = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "name": post_name
        },
        "spec": {
            "title": "最小化测试",
            "slug": post_name,
            "deleted": False,
            "publish": False,
            "visible": "PUBLIC",
            "owner": "jason"
        }
    }
    
    try:
        # 创建文章
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(minimal_post),
            timeout=30
        )
        
        if create_response.status_code in [200, 201]:
            print(f"✅ 最小化文章创建成功")
            
            # 最小化内容
            minimal_content = {
                "raw": "简单测试",
                "rawType": "markdown"
            }
            
            content_response = session.put(
                f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                data=json.dumps(minimal_content),
                timeout=30
            )
            
            print(f"内容设置状态: {content_response.status_code}")
            
            if content_response.status_code in [200, 201]:
                edit_url = f"{base_url}/console/posts/editor?name={post_name}"
                print(f"🔗 编辑链接: {edit_url}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 最小化测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 API端点和创建方法测试")
    print("=" * 70)
    
    # 测试读取端点
    test_content_read_endpoints()
    
    # 测试浏览器模拟创建
    browser_success = test_browser_like_creation()
    
    if not browser_success:
        # 测试最小化方法
        minimal_success = test_minimal_approach()
        
        if minimal_success:
            print(f"\n✅ 最小化方法成功")
        else:
            print(f"\n❌ 所有方法都失败")
    else:
        print(f"\n✅ 浏览器模拟方法成功")

if __name__ == "__main__":
    main() 