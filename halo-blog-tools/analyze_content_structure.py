#!/usr/bin/env python3
"""
分析正常文章和API创建文章的内容结构差异
找出为什么内容没有被正确保存的原因
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

def analyze_article_content():
    """分析文章内容结构"""
    print("🔍 分析正常文章和API创建文章的内容结构差异")
    print("=" * 70)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 要对比的文章
    test_articles = [
        {
            "name": "正常文章",
            "id": "ab9bc79d-aba8-48dc-a3cf-caf4c2b40aee",  # 不会编程，20分钟手搓一个旅游AI工具
            "is_normal": True
        },
        {
            "name": "API创建的文章",
            "id": "simple-test-1751214662",  # 我们刚创建的测试文章
            "is_normal": False
        }
    ]
    
    for article in test_articles:
        print(f"\n📄 分析文章: {article['name']} ({article['id']})")
        print(f"{'=' * 50}")
        
        try:
            # 1. 获取文章基本信息
            article_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{article['id']}",
                timeout=30
            )
            
            if article_response.status_code == 200:
                article_data = article_response.json()
                print(f"✅ 文章信息获取成功")
                
                # 打印关键字段
                spec = article_data.get("spec", {})
                print(f"📋 文章基本信息:")
                print(f"   标题: {spec.get('title', 'N/A')}")
                print(f"   发布状态: {spec.get('publish', 'N/A')}")
                print(f"   所有者: {spec.get('owner', 'N/A')}")
                print(f"   模板: {spec.get('template', 'N/A')}")
                
            else:
                print(f"❌ 文章信息获取失败: {article_response.status_code}")
                continue
            
            # 2. 获取文章内容
            content_response = session.get(
                f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{article['id']}/content",
                timeout=30
            )
            
            if content_response.status_code == 200:
                content_data = content_response.json()
                print(f"✅ 内容信息获取成功")
                
                print(f"📝 内容详情:")
                print(f"   rawType: {content_data.get('rawType', 'N/A')}")
                print(f"   raw长度: {len(content_data.get('raw', ''))}")
                print(f"   content长度: {len(content_data.get('content', ''))}")
                print(f"   raw前100字符: {content_data.get('raw', '')[:100]}{'...' if len(content_data.get('raw', '')) > 100 else ''}")
                print(f"   content前100字符: {content_data.get('content', '')[:100]}{'...' if len(content_data.get('content', '')) > 100 else ''}")
                
                # 保存到文件以供详细分析
                filename = f"content_analysis_{article['name'].replace(' ', '_')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "article_info": article_data,
                        "content_info": content_data
                    }, f, ensure_ascii=False, indent=2)
                print(f"💾 详细数据已保存到: {filename}")
                
            else:
                print(f"❌ 内容信息获取失败: {content_response.status_code}")
                if content_response.status_code == 500:
                    print("⚠️  这可能是之前遇到的500错误")
            
            # 3. 检查发布状态的内容（仅对已发布文章）
            if article.get("is_normal"):
                published_response = session.get(
                    f"{base_url}/apis/api.halo.run/v1alpha1/posts/{article['id']}/content",
                    timeout=30
                )
                
                if published_response.status_code == 200:
                    published_data = published_response.json()
                    print(f"✅ 发布内容获取成功")
                    print(f"📰 发布内容详情:")
                    print(f"   content长度: {len(published_data.get('content', ''))}")
                    print(f"   content前100字符: {published_data.get('content', '')[:100]}{'...' if len(published_data.get('content', '')) > 100 else ''}")
                else:
                    print(f"ℹ️  发布内容获取失败: {published_response.status_code}")
            
        except Exception as e:
            print(f"❌ 分析异常: {e}")
    
    return True

def suggest_content_fix():
    """基于分析结果提出修复建议"""
    print(f"\n💡 修复建议")
    print("=" * 50)
    
    print("基于发现的问题，可能的原因和解决方案：")
    print()
    print("1. 内容设置API调用方式问题")
    print("   - 检查请求头是否完整")
    print("   - 验证数据格式是否正确")
    print("   - 确认API端点是否正确")
    print()
    print("2. 内容格式不匹配")
    print("   - 尝试不同的rawType值")
    print("   - 检查raw和content字段的差异")
    print("   - 可能需要额外的处理步骤")
    print()
    print("3. 权限或状态问题")
    print("   - 确认用户权限足够")
    print("   - 检查文章状态是否影响内容保存")
    print("   - 可能需要特定的发布流程")
    print()
    print("4. 系统兼容性问题")
    print("   - 对比手动创建的API调用")
    print("   - 检查是否需要特定的编辑器支持")
    print("   - 验证API版本兼容性")

def main():
    """主函数"""
    print("🔧 内容结构差异分析")
    print("=" * 70)
    
    success = analyze_article_content()
    
    if success:
        suggest_content_fix()
        print(f"\n🎯 分析完成")
        print("请查看生成的JSON文件以获取详细信息")
    else:
        print(f"\n❌ 分析失败")

if __name__ == "__main__":
    main() 