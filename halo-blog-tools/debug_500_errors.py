#!/usr/bin/env python3
"""调试500错误的脚本"""

import requests
import json
import time
import os

class HaloAPIDebugger:
    def __init__(self):
        self.base_url = "https://blog.u2u.fun"  # 根据测试结果
        self.access_token = os.getenv('HALO_ACCESS_TOKEN', '')  # 需要设置
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Halo-Debug/1.0'
        })
    
    def test_minimal_tag_creation(self):
        """测试最简化的标签创建"""
        print("🏷️  测试标签创建 (最简化)")
        print("-" * 40)
        
        # 尝试最简单的标签数据
        simple_tag = {
            "metadata": {
                "generateName": "tag-"
            },
            "spec": {
                "displayName": f"测试标签{int(time.time())}",
                "slug": f"test-tag-{int(time.time())}"
            }
        }
        
        print(f"📤 发送数据: {json.dumps(simple_tag, indent=2, ensure_ascii=False)}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/tags",
                data=json.dumps(simple_tag),
                timeout=30
            )
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📥 响应头: {dict(response.headers)}")
            print(f"📥 响应内容: {response.text}")
            
            return response.status_code < 400
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_minimal_post_creation(self):
        """测试最简化的文章创建"""
        print("\n📝 测试文章创建 (最简化)")
        print("-" * 40)
        
        # 尝试最简单的文章数据
        simple_post = {
            "metadata": {
                "generateName": "post-"
            },
            "spec": {
                "title": f"测试文章{int(time.time())}",
                "slug": f"test-post-{int(time.time())}",
                "deleted": False,
                "publish": False
            }
        }
        
        print(f"📤 发送数据: {json.dumps(simple_post, indent=2, ensure_ascii=False)}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts",
                data=json.dumps(simple_post),
                timeout=30
            )
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📥 响应头: {dict(response.headers)}")
            print(f"📥 响应内容: {response.text}")
            
            return response.status_code < 400
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def check_api_permissions(self):
        """检查API权限"""
        print("\n🔒 检查API权限")
        print("-" * 40)
        
        # 检查可以访问的端点
        endpoints_to_check = [
            "/apis/content.halo.run/v1alpha1/tags",  # GET - 查看标签
            "/apis/content.halo.run/v1alpha1/posts",  # GET - 查看文章
            "/apis/content.halo.run/v1alpha1/categories"  # GET - 查看分类
        ]
        
        for endpoint in endpoints_to_check:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                print(f"🔍 {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    item_count = len(data.get('items', []))
                    print(f"   📊 数据项: {item_count}")
                elif response.status_code == 403:
                    print(f"   ❌ 权限不足")
                elif response.status_code == 401:
                    print(f"   ❌ 认证失败")
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
    
    def run_debug(self):
        """运行调试测试"""
        print("🐛 Halo API 500错误调试")
        print("=" * 50)
        
        if not self.access_token:
            print("⚠️  警告: 未设置访问令牌")
            print("请设置环境变量: export HALO_ACCESS_TOKEN='your-token'")
            return
        
        print(f"🔗 测试环境: {self.base_url}")
        print(f"🔑 Token: {self.access_token[:10]}...")
        
        # 检查权限
        self.check_api_permissions()
        
        # 测试标签创建
        tag_success = self.test_minimal_tag_creation()
        
        # 测试文章创建  
        post_success = self.test_minimal_post_creation()
        
        print(f"\n📊 测试结果总结:")
        print(f"🏷️  标签创建: {'✅' if tag_success else '❌'}")
        print(f"📝 文章创建: {'✅' if post_success else '❌'}")

if __name__ == "__main__":
    debugger = HaloAPIDebugger()
    debugger.run_debug()
