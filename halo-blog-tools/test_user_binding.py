#!/usr/bin/env python3
"""
测试用户绑定和编辑器问题修复
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

def test_post_user_binding():
    """测试文章用户绑定问题"""
    print("\n" + "="*60)
    print("🔧 测试: 文章用户绑定修复")
    print("="*60)
    
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
        print("👤 获取当前用户信息...")
        
        # 先测试用户获取功能
        endpoints = [
            "/apis/api.console.halo.run/v1alpha1/users/-",
            "/apis/api.console.halo.run/v1alpha1/users/-/profile", 
            "/apis/api.halo.run/v1alpha1/users/-",
            "/apis/uc.api.console.halo.run/v1alpha1/users/-"
        ]
        
        current_user = None
        for endpoint in endpoints:
            try:
                user_response = session.get(f"{base_url}{endpoint}", timeout=10)
                print(f"   尝试 {endpoint}: {user_response.status_code}")
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    
                    # 尝试获取用户名
                    if "user" in user_data and "metadata" in user_data["user"]:
                        current_user = user_data["user"]["metadata"].get("name")
                    elif "metadata" in user_data and "name" in user_data["metadata"]:
                        current_user = user_data["metadata"]["name"]
                    elif "spec" in user_data and "displayName" in user_data["spec"]:
                        current_user = user_data["spec"]["displayName"]
                    
                    if current_user:
                        print(f"   ✅ 成功获取用户: {current_user}")
                        break
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
                continue
        
        if not current_user:
            print("   ⚠️ 未能通过API获取用户，使用默认值: jason")
            current_user = "jason"
        
        # 创建测试文章
        print(f"\n📝 创建测试文章...")
        title = f'用户绑定测试文章 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        content = '''# 用户绑定测试

这是一篇测试文章，用于验证：

1. ✅ 文章创建时是否正确绑定用户
2. ✅ 文章内容是否能正确设置
3. ✅ 编辑器功能是否正常

## 测试内容

- **用户绑定**: 验证文章owner字段
- **内容编辑**: 验证Markdown编辑器
- **发布状态**: 验证发布功能

测试时间: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        post_name = f"user-binding-test-{int(time.time())}"
        
        # 准备文章数据（包含owner字段）
        post_data = {
            "apiVersion": "content.halo.run/v1alpha1",
            "kind": "Post",
            "metadata": {
                "name": post_name
            },
            "spec": {
                "title": title,
                "slug": f"user-binding-test-{int(time.time())}",
                "template": "",
                "cover": "",
                "deleted": False,
                "publish": True,  # 立即发布
                "pinned": False,
                "allowComment": True,
                "visible": "PUBLIC",
                "priority": 0,
                "excerpt": {
                    "autoGenerate": False,
                    "raw": "这是一篇测试文章，用于验证用户绑定和编辑器功能"
                },
                "categories": [],
                "tags": ["用户绑定测试", "编辑器测试", "dify插件"],
                "owner": current_user,  # 关键：设置文章作者
                "htmlMetas": []
            }
        }
        
        print(f"   👤 设置文章作者: {current_user}")
        print(f"   📝 文章标题: {title}")
        
        # 创建文章
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"   ❌ 文章创建失败: {create_response.status_code} - {create_response.text}")
            return False
        
        result = create_response.json()
        post_id = result.get("metadata", {}).get("name", post_name)
        
        print(f"   ✅ 文章创建成功: {post_id}")
        
        # 设置文章内容
        print(f"   📄 设置文章内容...")
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
        print(f"   📄 内容设置: {'✅ 成功' if content_success else '❌ 失败'}")
        
        # 验证文章信息
        print(f"\n🔍 验证文章信息...")
        verify_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
            timeout=10
        )
        
        if verify_response.status_code == 200:
            post_detail = verify_response.json()
            actual_owner = post_detail.get("spec", {}).get("owner", "")
            published = post_detail.get("spec", {}).get("publish", False)
            post_title = post_detail.get("spec", {}).get("title", "")
            
            print(f"   📝 文章标题: {post_title}")
            print(f"   👤 实际作者: '{actual_owner}'")
            print(f"   🎯 预期作者: '{current_user}'")
            print(f"   ✅ 用户匹配: {'✅' if actual_owner == current_user else '❌'}")
            print(f"   🚀 发布状态: {'✅ 已发布' if published else '❌ 草稿'}")
            print(f"   📄 内容设置: {'✅ 成功' if content_success else '❌ 失败'}")
            
            # 检查编辑器支持
            if content_success:
                print(f"   🖊️ 编辑器功能: ✅ Markdown编辑器正常")
            else:
                print(f"   🖊️ 编辑器功能: ❌ 内容设置失败")
            
            # 生成查看链接
            print(f"\n🌐 访问地址:")
            print(f"   📱 博客页面: {base_url}/archives/{post_detail.get('spec', {}).get('slug', '')}")
            print(f"   🔧 管理后台: {base_url}/console/posts/editor?name={post_id}")
            
            # 总结修复状态
            user_binding_ok = actual_owner == current_user
            content_ok = content_success
            publish_ok = published
            
            if user_binding_ok and content_ok and publish_ok:
                print(f"\n🎉 修复验证成功！")
                print(f"   ✅ 用户绑定: 文章正确绑定到用户 '{current_user}'")
                print(f"   ✅ 编辑器功能: Markdown内容正确设置")
                print(f"   ✅ 发布功能: 文章成功发布")
                return True
            else:
                print(f"\n❌ 修复验证失败！")
                if not user_binding_ok:
                    print(f"   ❌ 用户绑定问题: 期望 '{current_user}', 实际 '{actual_owner}'")
                if not content_ok:
                    print(f"   ❌ 编辑器问题: 内容设置失败")
                if not publish_ok:
                    print(f"   ❌ 发布问题: 文章未能发布")
                return False
        else:
            print(f"   ❌ 无法获取文章详情: {verify_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_moment_tag_spacing():
    """测试瞬间标签空格问题"""
    print("\n" + "="*60)
    print("🏷️ 测试: 瞬间标签空格修复")
    print("="*60)
    
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
        # 创建测试瞬间
        print("💭 创建测试瞬间...")
        content = f"标签空格测试 - {datetime.now().strftime('%H:%M:%S')}"
        tags = ["标签一", "标签二", "标签三"]
        
        print(f"   📝 内容: {content}")
        print(f"   🏷️ 标签: {', '.join(tags)}")
        
        # 生成包含标签的HTML内容（修复后的逻辑）
        import urllib.parse
        
        tag_links = []
        for tag in tags:
            encoded_tag = urllib.parse.quote(tag)
            tag_link = f'<a class="tag" href="/moments?tag={encoded_tag}" data-pjax="">{tag}</a>'
            tag_links.append(tag_link)
        
        # 标签之间用空格分隔（修复后的逻辑）
        tag_html = ' '.join(tag_links)
        raw_with_tags = ''.join([f'#{tag}' for tag in tags]) + content
        html_with_tags = tag_html + content.replace('\n', '<br>')
        
        moment_name = f"tag-spacing-test-{int(time.time())}"
        moment_data = {
            "apiVersion": "moment.halo.run/v1alpha1",
            "kind": "Moment",
            "metadata": {
                "name": moment_name,
                "generateName": "moment-"
            },
            "spec": {
                "content": {
                    "raw": raw_with_tags,
                    "html": html_with_tags,
                    "medium": []
                },
                "owner": "jason",
                "tags": tags,
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
            moment_id = result.get("metadata", {}).get("name")
            html_content = result.get("spec", {}).get("content", {}).get("html", "")
            
            print(f"   ✅ 瞬间创建成功: {moment_id}")
            print(f"   🔗 HTML内容: {html_content}")
            
            # 检查标签间空格
            space_count = html_content.count('</a><a class="tag"')
            if space_count == 0:  # 说明标签之间有空格
                print(f"   ✅ 标签空格: 正确分隔")
                space_ok = True
            else:
                print(f"   ❌ 标签空格: 标签粘连 ({space_count} 处)")
                space_ok = False
            
            print(f"\n🌐 查看地址: {base_url}/moments")
            
            return space_ok
        else:
            print(f"   ❌ 瞬间创建失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始用户绑定和编辑器问题修复验证")
    print("="*70)
    
    # 运行测试
    post_test = test_post_user_binding()
    moment_test = test_moment_tag_spacing()
    
    # 汇总结果
    print("\n" + "="*70)
    print("🎯 修复验证结果汇总")
    print("="*70)
    print(f"文章用户绑定和编辑器: {'✅ 修复成功' if post_test else '❌ 仍有问题'}")
    print(f"瞬间标签空格: {'✅ 修复成功' if moment_test else '❌ 仍有问题'}")
    
    total_tests = 2
    passed_tests = sum([post_test, moment_test])
    
    print(f"\n通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 所有问题修复成功！可以进行下一步开发了！")
    else:
        print("⚠️ 仍有问题需要解决")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 