#!/usr/bin/env python3
"""
对比正常工作的文章与API创建文章的结构差异
找出为什么编辑器无法识别API创建的文章
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

def analyze_working_article():
    """分析一个正常工作的文章"""
    print("🔍 分析正常工作的文章结构")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return None
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 用户提到的正常文章 - "不会编程，20分钟手搓一个旅游AI工具"
    working_article_id = "ab9bc79d-aba8-48dc-a3cf-caf4c2b40aee"
    
    try:
        # 获取文章信息
        article_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{working_article_id}",
            timeout=30
        )
        
        if article_response.status_code == 200:
            article_data = article_response.json()
            print(f"✅ 正常文章信息获取成功")
            
            # 保存文章数据
            with open("working_article_spec.json", 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            print(f"💾 正常文章数据已保存")
            
            # 获取快照信息
            snapshot_id = article_data['spec'].get('headSnapshot')
            if snapshot_id:
                print(f"📋 正常文章快照ID: {snapshot_id}")
                
                snapshot_response = session.get(
                    f"{base_url}/apis/content.halo.run/v1alpha1/snapshots/{snapshot_id}",
                    timeout=30
                )
                
                if snapshot_response.status_code == 200:
                    snapshot_data = snapshot_response.json()
                    print(f"✅ 正常文章快照获取成功")
                    
                    # 保存快照数据
                    with open("working_article_snapshot.json", 'w', encoding='utf-8') as f:
                        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
                    print(f"💾 正常文章快照已保存")
                    
                    return {
                        'article': article_data,
                        'snapshot': snapshot_data,
                        'snapshot_id': snapshot_id
                    }
                else:
                    print(f"❌ 正常文章快照获取失败: {snapshot_response.status_code}")
            else:
                print(f"❌ 正常文章没有快照ID")
        else:
            print(f"❌ 正常文章信息获取失败: {article_response.status_code}")
    
    except Exception as e:
        print(f"❌ 分析正常文章异常: {e}")
    
    return None

def analyze_api_article():
    """分析API创建的文章"""
    print(f"\n🔍 分析API创建的文章结构")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return None
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 我们创建的文章
    api_article_id = "simple-test-1751214662"
    
    try:
        # 获取文章信息
        article_response = session.get(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{api_article_id}",
            timeout=30
        )
        
        if article_response.status_code == 200:
            article_data = article_response.json()
            print(f"✅ API文章信息获取成功")
            
            # 保存文章数据
            with open("api_article_spec.json", 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            print(f"💾 API文章数据已保存")
            
            # 获取快照信息
            snapshot_id = article_data['spec'].get('headSnapshot')
            if snapshot_id:
                print(f"📋 API文章快照ID: {snapshot_id}")
                
                snapshot_response = session.get(
                    f"{base_url}/apis/content.halo.run/v1alpha1/snapshots/{snapshot_id}",
                    timeout=30
                )
                
                if snapshot_response.status_code == 200:
                    snapshot_data = snapshot_response.json()
                    print(f"✅ API文章快照获取成功")
                    
                    # 保存快照数据
                    with open("api_article_snapshot.json", 'w', encoding='utf-8') as f:
                        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
                    print(f"💾 API文章快照已保存")
                    
                    return {
                        'article': article_data,
                        'snapshot': snapshot_data,
                        'snapshot_id': snapshot_id
                    }
                else:
                    print(f"❌ API文章快照获取失败: {snapshot_response.status_code}")
            else:
                print(f"❌ API文章没有快照ID")
        else:
            print(f"❌ API文章信息获取失败: {article_response.status_code}")
    
    except Exception as e:
        print(f"❌ 分析API文章异常: {e}")
    
    return None

def compare_structures(working_data, api_data):
    """对比两个文章的结构差异"""
    print(f"\n📊 结构差异对比")
    print("=" * 60)
    
    if not working_data or not api_data:
        print("❌ 数据不完整，无法对比")
        return
    
    print(f"🔍 文章spec字段对比:")
    working_spec = working_data['article']['spec']
    api_spec = api_data['article']['spec']
    
    # 对比spec字段
    all_keys = set(working_spec.keys()) | set(api_spec.keys())
    for key in sorted(all_keys):
        working_val = working_spec.get(key, '❌ 缺失')
        api_val = api_spec.get(key, '❌ 缺失')
        
        if working_val != api_val:
            print(f"   ⚠️  {key}:")
            print(f"      正常文章: {working_val}")
            print(f"      API文章: {api_val}")
        else:
            print(f"   ✅ {key}: 相同")
    
    print(f"\n🔍 快照spec字段对比:")
    working_snapshot = working_data['snapshot']['spec']
    api_snapshot = api_data['snapshot']['spec']
    
    # 对比快照字段
    all_snapshot_keys = set(working_snapshot.keys()) | set(api_snapshot.keys())
    for key in sorted(all_snapshot_keys):
        working_val = working_snapshot.get(key, '❌ 缺失')
        api_val = api_snapshot.get(key, '❌ 缺失')
        
        if key in ['rawPatch', 'contentPatch']:
            # 内容字段只比较长度
            if isinstance(working_val, str) and isinstance(api_val, str):
                print(f"   📝 {key}: 正常文章({len(working_val)}字符) vs API文章({len(api_val)}字符)")
            else:
                print(f"   📝 {key}: 正常文章({type(working_val)}) vs API文章({type(api_val)})")
        elif working_val != api_val:
            print(f"   ⚠️  {key}:")
            print(f"      正常文章: {working_val}")
            print(f"      API文章: {api_val}")
        else:
            print(f"   ✅ {key}: 相同")

def create_article_like_working(working_data):
    """基于正常文章的结构创建新文章"""
    print(f"\n🛠️  基于正常文章结构创建新文章")
    print("=" * 60)
    
    if not working_data:
        print("❌ 没有正常文章数据参考")
        return False
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    post_name = f"mimic-working-{int(time.time())}"
    test_content = "这是模仿正常文章结构创建的测试。\n\n应该能被编辑器正确识别。"
    
    # 使用正常文章的结构模板
    working_spec = working_data['article']['spec']
    
    post_data = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "name": post_name
        },
        "spec": {
            "title": f"模仿正常结构测试 - {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "slug": post_name,
            "template": working_spec.get("template", ""),
            "cover": working_spec.get("cover", ""),
            "deleted": False,
            "publish": False,
            "pinned": working_spec.get("pinned", False),
            "allowComment": working_spec.get("allowComment", True),
            "visible": working_spec.get("visible", "PUBLIC"),
            "priority": working_spec.get("priority", 0),
            "excerpt": working_spec.get("excerpt", {"autoGenerate": True, "raw": ""}),
            "categories": working_spec.get("categories", []),
            "tags": working_spec.get("tags", []),
            "owner": "jason",
            "htmlMetas": working_spec.get("htmlMetas", [])
        }
    }
    
    try:
        # 创建文章
        create_response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"❌ 模仿文章创建失败: {create_response.status_code}")
            return False
            
        print(f"✅ 模仿文章创建成功")
        
        # 设置内容
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
        
        if content_response.status_code in [200, 201]:
            print(f"✅ 模仿文章内容设置成功")
            edit_url = f"{base_url}/console/posts/editor?name={post_name}"
            print(f"🔗 编辑链接: {edit_url}")
            return True
        else:
            print(f"❌ 模仿文章内容设置失败: {content_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模仿文章创建异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 正常文章 vs API文章 结构对比分析")
    print("=" * 70)
    
    # 分析正常工作的文章
    working_data = analyze_working_article()
    
    # 分析API创建的文章
    api_data = analyze_api_article()
    
    # 对比结构差异
    compare_structures(working_data, api_data)
    
    # 基于正常文章结构创建新文章
    if working_data:
        success = create_article_like_working(working_data)
        if success:
            print(f"\n✅ 模仿正常结构的文章创建成功")
            print(f"💡 请测试新文章的编辑器功能")
        else:
            print(f"\n❌ 模仿正常结构的文章创建失败")

if __name__ == "__main__":
    main() 