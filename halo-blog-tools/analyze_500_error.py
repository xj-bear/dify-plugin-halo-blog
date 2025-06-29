#!/usr/bin/env python3
"""分析500错误的具体原因"""

import requests
import json
import time

def read_token():
    with open('key.txt', 'r') as f:
        return f.read().strip()

def test_different_tag_formats():
    """测试不同的标签数据格式"""
    print("🔬 分析标签创建500错误")
    print("="*50)
    
    token = read_token()
    base_url = "https://blog.u2u.fun"
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Halo-Analysis/1.0'
    })
    
    # 先获取现有标签，看看正确的格式
    print("📋 步骤1: 分析现有标签格式")
    try:
        response = session.get(f"{base_url}/apis/content.halo.run/v1alpha1/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                sample_tag = data['items'][0]
                print("   现有标签样本格式:")
                print(json.dumps(sample_tag, indent=2, ensure_ascii=False)[:500] + "...")
            else:
                print("   ⚠️  没有现有标签可以参考")
    except Exception as e:
        print(f"   ❌ 获取现有标签失败: {e}")
    
    # 测试不同的创建格式
    test_formats = [
        {
            "name": "最简格式1",
            "data": {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Tag",
                "metadata": {
                    "generateName": "tag-"
                },
                "spec": {
                    "displayName": f"格式1-{int(time.time())}",
                    "slug": f"format1-{int(time.time())}"
                }
            }
        },
        {
            "name": "最简格式2",
            "data": {
                "metadata": {
                    "generateName": "tag-"
                },
                "spec": {
                    "displayName": f"格式2-{int(time.time())}",
                    "slug": f"format2-{int(time.time())}",
                    "color": "#000000"
                }
            }
        },
        {
            "name": "完整格式",
            "data": {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Tag",
                "metadata": {
                    "generateName": "tag-",
                    "labels": {},
                    "annotations": {}
                },
                "spec": {
                    "displayName": f"完整格式-{int(time.time())}",
                    "slug": f"full-format-{int(time.time())}",
                    "color": "#6366f1",
                    "cover": ""
                }
            }
        }
    ]
    
    for i, test_format in enumerate(test_formats, 1):
        print(f"\n🧪 测试{i}: {test_format['name']}")
        print(f"   数据: {json.dumps(test_format['data'], ensure_ascii=False)}")
        
        try:
            response = session.post(
                f"{base_url}/apis/content.halo.run/v1alpha1/tags",
                data=json.dumps(test_format['data']),
                timeout=30
            )
            print(f"   状态: {response.status_code}")
            
            if response.status_code < 400:
                print("   ✅ 成功！")
                break
            else:
                print(f"   ❌ 失败: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 测试文章创建格式
    print(f"\n📝 测试文章创建格式")
    post_data = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {
            "generateName": "post-"
        },
        "spec": {
            "title": f"分析测试文章{int(time.time())}",
            "slug": f"analysis-post-{int(time.time())}",
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
            "htmlMetas": []
        }
    }
    
    try:
        response = session.post(
            f"{base_url}/apis/content.halo.run/v1alpha1/posts",
            data=json.dumps(post_data),
            timeout=30
        )
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.text[:200]}...")
        
        if response.status_code < 400:
            print("   ✅ 文章创建成功！")
        else:
            print("   ❌ 文章创建失败")
            
    except Exception as e:
        print(f"   ❌ 文章创建异常: {e}")

if __name__ == "__main__":
    test_different_tag_formats()
