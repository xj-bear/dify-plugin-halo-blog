#!/usr/bin/env python3
"""
诊断文章显示问题
检查为什么API创建的文章在前台显示空白
"""

import requests
import json

def load_config():
    """加载配置"""
    try:
        with open('key.txt', 'r', encoding='utf-8') as f:
            pat_token = f.read().strip()
        return "https://blog.u2u.fun", pat_token
    except FileNotFoundError:
        print("❌ 找不到 key.txt 文件")
        return None, None

def diagnose_article_issue():
    """诊断文章显示问题"""
    
    print("🔍 诊断文章显示问题")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        print("❌ 配置加载失败")
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    })
    
    post_id = 'editor-test-1751279024'
    
    try:
        # 1. 检查文章基本信息
        print("📋 第一步：检查文章基本信息")
        print("-" * 40)
        
        response = session.get(f'{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}')
        
        if response.status_code != 200:
            print(f"❌ 无法获取文章信息: {response.status_code}")
            return False
        
        data = response.json()
        spec = data.get('spec', {})
        metadata = data.get('metadata', {})
        annotations = metadata.get('annotations', {})
        
        print(f"   📝 标题: {spec.get('title', '无')}")
        print(f"   📢 发布状态: {spec.get('publish', False)}")
        print(f"   👁️ 可见性: {spec.get('visible', '无')}")
        print(f"   👤 作者: {spec.get('owner', '无')}")
        print(f"   🔗 Slug: {spec.get('slug', '无')}")
        print(f"   🗑️ 已删除: {spec.get('deleted', False)}")
        
        # 2. 检查内容注解
        print(f"\n📄 第二步：检查内容注解")
        print("-" * 40)
        
        has_content_json = "content.halo.run/content-json" in annotations
        print(f"   📋 content-json注解: {'✅ 存在' if has_content_json else '❌ 缺失'}")
        
        if has_content_json:
            try:
                content_data = json.loads(annotations['content.halo.run/content-json'])
                raw_content = content_data.get('raw', '')
                content_content = content_data.get('content', '')
                raw_type = content_data.get('rawType', '')
                
                print(f"   📝 rawType: {raw_type}")
                print(f"   📊 raw长度: {len(raw_content)} 字符")
                print(f"   📊 content长度: {len(content_content)} 字符")
                
                if len(raw_content) > 0:
                    print(f"   📄 raw内容预览: {raw_content[:100]}{'...' if len(raw_content) > 100 else ''}")
                else:
                    print(f"   ❌ raw内容为空！")
                    
                if len(content_content) > 0:
                    print(f"   📄 content内容预览: {content_content[:100]}{'...' if len(content_content) > 100 else ''}")
                else:
                    print(f"   ❌ content内容为空！")
                    
            except Exception as e:
                print(f"   ❌ content-json注解解析失败: {e}")
        
        # 3. 检查Console API内容
        print(f"\n📄 第三步：检查Console API内容")
        print("-" * 40)
        
        try:
            content_response = session.get(f'{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content')
            print(f"   📡 Console content API: {content_response.status_code}")
            
            if content_response.status_code == 200:
                console_content = content_response.json()
                console_raw = console_content.get('raw', '')
                console_content_text = console_content.get('content', '')
                console_raw_type = console_content.get('rawType', '')
                
                print(f"   📝 Console rawType: {console_raw_type}")
                print(f"   📊 Console raw长度: {len(console_raw)} 字符")
                print(f"   📊 Console content长度: {len(console_content_text)} 字符")
                
                if len(console_raw) == 0:
                    print(f"   ❌ Console API显示内容为空！这是问题所在！")
                else:
                    print(f"   ✅ Console API有内容")
                    
            elif content_response.status_code == 404:
                print(f"   ❌ Console content API返回404 - 内容不存在！")
            else:
                print(f"   ❌ Console content API失败: {content_response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Console API检查异常: {e}")
        
        # 4. 检查发布状态详情
        print(f"\n🚀 第四步：检查发布状态详情")
        print("-" * 40)
        
        if spec.get('publish', False):
            print(f"   ✅ 文章标记为已发布")
            
            # 检查发布时间
            publish_time = spec.get('publishTime')
            if publish_time:
                print(f"   ⏰ 发布时间: {publish_time}")
            else:
                print(f"   ⚠️ 缺少发布时间")
                
        else:
            print(f"   ❌ 文章未发布（草稿状态）")
        
        # 5. 诊断总结
        print(f"\n📊 第五步：问题诊断总结")
        print("=" * 60)
        
        issues = []
        
        # 检查各种可能的问题
        if not spec.get('publish', False):
            issues.append("文章未发布")
            
        if spec.get('deleted', False):
            issues.append("文章已删除")
            
        if not has_content_json:
            issues.append("缺少content-json注解")
        elif has_content_json:
            try:
                content_data = json.loads(annotations['content.halo.run/content-json'])
                if len(content_data.get('raw', '')) == 0:
                    issues.append("content-json中raw内容为空")
                if len(content_data.get('content', '')) == 0:
                    issues.append("content-json中content内容为空")
            except:
                issues.append("content-json注解格式错误")
        
        if not spec.get('owner'):
            issues.append("缺少文章作者")
            
        if len(issues) == 0:
            print("🎉 未发现明显问题，可能是其他原因导致前台显示空白")
            print("   建议检查：")
            print("   • Halo主题模板是否正确")
            print("   • 数据库中的实际内容存储")
            print("   • 缓存问题")
        else:
            print("🔍 发现以下问题：")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. ❌ {issue}")
                
        print(f"\n🔗 相关链接：")
        print(f"   📱 前台地址: {base_url}/archives/{spec.get('slug', '')}")
        print(f"   🔧 编辑器: {base_url}/console/posts/editor?name={post_id}")
        print(f"   📋 管理后台: {base_url}/console/posts/{post_id}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ 诊断过程中出错: {e}")
        return False

if __name__ == "__main__":
    diagnose_article_issue() 