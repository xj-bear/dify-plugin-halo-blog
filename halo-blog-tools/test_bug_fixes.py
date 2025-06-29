#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证bug修复
包括：
1. 瞬间创建标签显示问题
2. 文章发布状态问题  
3. 文章更新状态报告问题
"""

import os
import sys
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 读取配置
def load_config():
    try:
        # 硬编码base_url，和其他测试文件保持一致
        base_url = "https://blog.u2u.fun"
        
        # 从key.txt读取token
        with open('key.txt', 'r', encoding='utf-8') as f:
            access_token = f.read().strip()
            
        return base_url, access_token
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None, None

def test_moment_create_with_tags():
    """测试1: 瞬间创建标签显示问题"""
    print("\n" + "="*50)
    print("测试1: 瞬间创建标签显示")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    try:
        # 直接导入工具类 - 修复导入路径
        sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
        
        from halo_moment_create import HaloMomentCreateTool
        from dify_plugin import Tool
        
        # 模拟运行时环境
        class MockRuntime:
            def __init__(self, credentials):
                self.credentials = credentials
        
        # 模拟消息创建方法
        class MockMessage:
            def __init__(self, message):
                self.message = message
        
        tool = HaloMomentCreateTool()
        tool.runtime = MockRuntime({
            'base_url': base_url,
            'access_token': access_token
        })
        
        # 添加必要的方法
        tool.create_text_message = lambda text: MockMessage(text)
        tool.create_json_message = lambda data: MockMessage(data)
        
        # 测试参数
        test_params = {
            'content': f'测试瞬间标签功能 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'tags': 'dify插件,测试标签,瞬间功能',
            'visible': 'PUBLIC'
        }
        
        print(f"创建瞬间，标签: {test_params['tags']}")
        
        # 执行测试
        messages = list(tool._invoke(test_params))
        
        # 检查结果
        success = False
        tag_info = None
        for msg in messages:
            print(f"📝 {msg.message}")
            if hasattr(msg, 'message') and isinstance(msg.message, str):
                if '✅ **动态创建成功！**' in msg.message:
                    success = True
                if '🏷️ **标签**' in msg.message:
                    tag_info = msg.message
        
        if success and tag_info:
            print("✅ 瞬间创建成功，标签信息显示正常")
            return True
        else:
            print("❌ 瞬间创建失败或标签信息未正确显示")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_post_create_publish():
    """测试2: 文章发布状态问题"""
    print("\n" + "="*50)
    print("测试2: 文章创建和发布状态")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    try:
        from tools.halo_post_create import HaloPostCreateTool
        
        # 模拟运行时环境
        class MockRuntime:
            def __init__(self, credentials):
                self.credentials = credentials
        
        # 模拟消息创建方法
        class MockMessage:
            def __init__(self, message):
                self.message = message
        
        tool = HaloPostCreateTool()
        tool.runtime = MockRuntime({
            'base_url': base_url,
            'access_token': access_token
        })
        
        # 添加必要的方法
        tool.create_text_message = lambda text: MockMessage(text)
        tool.create_json_message = lambda data: MockMessage(data)
        
        # 测试参数 - 立即发布
        test_params = {
            'title': f'测试文章发布功能 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': '这是一篇测试文章，用于验证发布功能是否正常工作。',
            'categories': '技术分享',
            'tags': 'dify,测试,发布',
            'publish_immediately': True,
            'excerpt': '测试文章摘要'
        }
        
        print(f"创建文章并立即发布: {test_params['title']}")
        
        # 执行测试
        messages = list(tool._invoke(test_params))
        
        # 检查结果
        success = False
        post_id = None
        published = False
        
        for msg in messages:
            print(f"📝 {msg.message}")
            if hasattr(msg, 'message') and isinstance(msg.message, str):
                if '✅ **文章创建成功！**' in msg.message:
                    success = True
                if '🚀 **状态**: 已发布' in msg.message:
                    published = True
            
            # 检查JSON响应
            try:
                if hasattr(msg, 'message') and isinstance(msg.message, dict):
                    data = msg.message
                    if data.get('success') and 'post_id' in data:
                        post_id = data['post_id']
                        if data.get('status') == 'PUBLISHED':
                            published = True
            except:
                pass
        
        if success and published and post_id:
            print(f"✅ 文章创建并发布成功，ID: {post_id}")
            
            # 验证文章确实被发布了
            print("🔍 验证文章发布状态...")
            session = requests.Session()
            session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
            
            # 获取文章详情
            response = session.get(f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}")
            if response.status_code == 200:
                post_data = response.json()
                is_published = post_data.get('spec', {}).get('publish', False)
                publish_time = post_data.get('spec', {}).get('publishTime')
                
                if is_published and publish_time:
                    print(f"✅ 验证成功：文章已发布，发布时间: {publish_time}")
                    return True
                else:
                    print(f"❌ 验证失败：文章未正确发布，publish={is_published}, publishTime={publish_time}")
                    return False
            else:
                print(f"❌ 无法获取文章详情: {response.status_code}")
                return False
        else:
            print("❌ 文章创建失败或未正确发布")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_post_update_status():
    """测试3: 文章更新状态报告问题"""
    print("\n" + "="*50)
    print("测试3: 文章更新状态报告")
    print("="*50)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    try:
        # 首先创建一篇测试文章
        from tools.halo_post_create import HaloPostCreateTool
        from tools.halo_post_update import HaloPostUpdateTool
        
        # 模拟运行时环境
        class MockRuntime:
            def __init__(self, credentials):
                self.credentials = credentials
        
        # 模拟消息创建方法
        class MockMessage:
            def __init__(self, message):
                self.message = message
        
        # 创建文章
        create_tool = HaloPostCreateTool()
        create_tool.runtime = MockRuntime({
            'base_url': base_url,
            'access_token': access_token
        })
        
        # 添加必要的方法
        create_tool.create_text_message = lambda text: MockMessage(text)
        create_tool.create_json_message = lambda data: MockMessage(data)
        
        create_params = {
            'title': f'测试更新状态报告 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': '原始内容',
            'publish_immediately': False
        }
        
        print("📝 创建测试文章...")
        create_messages = list(create_tool._invoke(create_params))
        
        # 获取文章ID
        post_id = None
        for msg in create_messages:
            try:
                if hasattr(msg, 'message') and isinstance(msg.message, dict):
                    data = msg.message
                    if data.get('success') and 'post_id' in data:
                        post_id = data['post_id']
                        break
            except:
                pass
        
        if not post_id:
            print("❌ 无法获取文章ID")
            return False
        
        print(f"✅ 测试文章创建成功，ID: {post_id}")
        
        # 更新文章
        update_tool = HaloPostUpdateTool()
        update_tool.runtime = MockRuntime({
            'base_url': base_url,
            'access_token': access_token
        })
        
        # 添加必要的方法
        update_tool.create_text_message = lambda text: MockMessage(text)
        update_tool.create_json_message = lambda data: MockMessage(data)
        
        update_params = {
            'post_id': post_id,
            'title': f'更新后的标题 - {datetime.now().strftime("%H:%M:%S")}',
            'content': '更新后的内容，测试状态报告功能',
            'tags': '更新测试,状态报告',
            'published': True
        }
        
        print("📝 更新测试文章...")
        update_messages = list(update_tool._invoke(update_params))
        
        # 检查更新结果
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for msg in update_messages:
            print(f"📝 {msg.message}")
            if hasattr(msg, 'message') and isinstance(msg.message, str):
                if '✅ **文章更新成功！**' in msg.message:
                    success_count += 1
                elif '⚠️ **文章部分更新成功**' in msg.message:
                    warning_count += 1
                elif '❌' in msg.message:
                    error_count += 1
        
        # 验证状态报告是否清晰
        if success_count == 1 and warning_count == 0:
            print("✅ 更新成功，状态报告清晰")
            return True
        elif warning_count == 1 and success_count == 0:
            print("✅ 部分更新成功，状态报告清晰")
            return True
        else:
            print(f"❌ 状态报告混乱：成功={success_count}, 警告={warning_count}, 错误={error_count}")
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
    test_results.append(("瞬间创建标签显示", test_moment_create_with_tags()))
    test_results.append(("文章发布状态", test_post_create_publish()))
    test_results.append(("文章更新状态报告", test_post_update_status()))
    
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
    sys.exit(0 if success else 1) 