#!/usr/bin/env python3
"""
测试纯文本格式和不同内容格式的兼容性
模仿Halo原生创建文章的方式
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

def test_different_content_formats():
    """测试不同的内容格式，特别是纯文本"""
    print("🧪 测试不同内容格式的兼容性")
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
    
    # 测试用例：从最简单的纯文本开始
    test_cases = [
        {
            "name": "纯文本-无格式",
            "rawType": "markdown",
            "raw": "这是一段纯文本内容，没有任何特殊格式。\n\n这是第二段。",
            "content": "这是一段纯文本内容，没有任何特殊格式。\n\n这是第二段。"
        },
        {
            "name": "简单HTML格式",
            "rawType": "html",
            "raw": "<p>这是一段HTML内容</p><p>这是第二段</p>",
            "content": "<p>这是一段HTML内容</p><p>这是第二段</p>"
        },
        {
            "name": "Markdown格式",
            "rawType": "markdown", 
            "raw": "# 标题\n\n这是内容段落。\n\n## 二级标题\n\n- 列表项1\n- 列表项2",
            "content": "# 标题\n\n这是内容段落。\n\n## 二级标题\n\n- 列表项1\n- 列表项2"
        },
        {
            "name": "空内容测试",
            "rawType": "markdown",
            "raw": "",
            "content": ""
        },
        {
            "name": "单行文本",
            "rawType": "markdown",
            "raw": "单行纯文本测试",
            "content": "单行纯文本测试"
        }
    ]
    
    successful_cases = []
    failed_cases = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {test_case['name']}")
        print(f"   rawType: {test_case['rawType']}")
        print(f"   raw长度: {len(test_case['raw'])} 字符")
        
        try:
            # 创建文章的最简化版本
            post_name = f"plain-test-{i}-{int(time.time())}"
            
            # 使用最简单的文章结构
            post_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": post_name
                },
                "spec": {
                    "title": f"纯文本测试 {i} - {test_case['name']}",
                    "slug": post_name,
                    "template": "",
                    "cover": "",
                    "deleted": False,
                    "publish": False,  # 保存为草稿
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
                
                # 使用最简单的内容设置方式
                content_data = {
                    "raw": test_case["raw"],
                    "content": test_case["content"],
                    "rawType": test_case["rawType"]
                }
                
                print(f"   📄 设置内容数据:")
                print(f"      raw: '{test_case['raw'][:50]}{'...' if len(test_case['raw']) > 50 else ''}'")
                print(f"      content: '{test_case['content'][:50]}{'...' if len(test_case['content']) > 50 else ''}'")
                print(f"      rawType: {test_case['rawType']}")
                
                content_response = session.put(
                    f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                    data=json.dumps(content_data),
                    timeout=30
                )
                
                print(f"   📤 内容设置响应: {content_response.status_code}")
                
                if content_response.status_code in [200, 201]:
                    print(f"   ✅ 内容设置成功")
                    
                    # 验证内容是否正确保存
                    verify_response = session.get(
                        f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_name}/content",
                        timeout=10
                    )
                    
                    if verify_response.status_code == 200:
                        saved_content = verify_response.json()
                        saved_raw = saved_content.get("raw", "")
                        saved_rawType = saved_content.get("rawType", "")
                        
                        print(f"   🔍 验证保存内容:")
                        print(f"      保存的raw: '{saved_raw[:50]}{'...' if len(saved_raw) > 50 else ''}'")
                        print(f"      保存的rawType: {saved_rawType}")
                        
                        # 检查是否完全匹配
                        content_match = saved_raw == test_case["raw"]
                        type_match = saved_rawType == test_case["rawType"]
                        
                        if content_match and type_match:
                            print(f"   ✅ 内容验证通过，编辑器应该可以识别")
                            successful_cases.append(test_case['name'])
                        else:
                            print(f"   ❌ 内容验证失败")
                            print(f"      内容匹配: {'✅' if content_match else '❌'}")
                            print(f"      类型匹配: {'✅' if type_match else '❌'}")
                            failed_cases.append({
                                'name': test_case['name'],
                                'reason': 'content_mismatch',
                                'expected_raw': test_case["raw"],
                                'actual_raw': saved_raw,
                                'expected_type': test_case["rawType"],
                                'actual_type': saved_rawType
                            })
                    else:
                        print(f"   ❌ 无法验证保存的内容: {verify_response.status_code}")
                        failed_cases.append({
                            'name': test_case['name'],
                            'reason': 'verification_failed',
                            'status': verify_response.status_code
                        })
                    
                    # 提供编辑链接
                    print(f"   🔗 编辑链接: {base_url}/console/posts/editor?name={post_name}")
                    
                else:
                    print(f"   ❌ 内容设置失败: {content_response.status_code}")
                    try:
                        error_data = content_response.json()
                        print(f"   错误详情: {error_data}")
                    except:
                        print(f"   错误文本: {content_response.text}")
                    
                    failed_cases.append({
                        'name': test_case['name'],
                        'reason': 'content_setting_failed',
                        'status': content_response.status_code,
                        'error': content_response.text
                    })
                    
            else:
                print(f"   ❌ 文章创建失败: {create_response.status_code}")
                failed_cases.append({
                    'name': test_case['name'],
                    'reason': 'post_creation_failed',
                    'status': create_response.status_code
                })
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            failed_cases.append({
                'name': test_case['name'],
                'reason': 'exception',
                'error': str(e)
            })
    
    # 汇总结果
    print(f"\n📊 测试结果汇总")
    print("=" * 60)
    print(f"✅ 成功的格式 ({len(successful_cases)} 个):")
    for case in successful_cases:
        print(f"   - {case}")
    
    print(f"\n❌ 失败的格式 ({len(failed_cases)} 个):")
    for case in failed_cases:
        print(f"   - {case['name']}: {case['reason']}")
        if 'error' in case:
            print(f"     错误: {case['error']}")
    
    return len(successful_cases) > 0

def compare_with_manual_creation():
    """对比手动创建与API创建的差异"""
    print(f"\n🔍 分析手动创建与API创建的差异")
    print("=" * 60)
    
    print("📋 手动创建文章的特点:")
    print("   1. 编辑器会自动处理内容格式")
    print("   2. 内容保存时可能会有预处理")
    print("   3. rawType可能有默认值")
    print("   4. 可能有额外的元数据")
    
    print(f"\n🔧 建议的改进方向:")
    print("   1. 尝试不设置rawType，让系统自动检测")
    print("   2. 使用更简化的内容结构")
    print("   3. 参考手动创建的API调用")
    print("   4. 检查是否需要特定的请求头")

def main():
    """主函数"""
    print("🔧 纯文本格式兼容性测试")
    print("=" * 70)
    
    # 运行格式测试
    success = test_different_content_formats()
    
    # 分析差异
    compare_with_manual_creation()
    
    print(f"\n" + "=" * 70)
    print("🎯 测试完成")
    
    if success:
        print("✅ 找到了可用的格式，请查看上面的成功案例")
    else:
        print("❌ 所有格式都失败，需要进一步分析")
        print("💡 建议:")
        print("   1. 检查手动创建文章时的网络请求")
        print("   2. 对比API调用的差异")
        print("   3. 可能需要特定的内容处理方式")

if __name__ == "__main__":
    main() 