#!/usr/bin/env python3
"""
Halo插件问题修复验证测试脚本
专门测试用户反馈的三个问题：
1. 瞬间的用户获取错误
2. 标签和分类显示但实际不存在
3. 文章创建500错误
"""

import os
import sys
import json
import logging
import requests
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append('.')

class HaloFixesTestSuite:
    def __init__(self):
        # 测试配置 - 请根据实际情况修改
        self.base_url = os.getenv('HALO_BASE_URL', '').strip().rstrip('/')
        self.access_token = os.getenv('HALO_ACCESS_TOKEN', '').strip()
        
        if not self.base_url or not self.access_token:
            print("⚠️  请设置环境变量或在脚本中配置测试信息")
            print("   方式1: export HALO_BASE_URL='https://your-halo-site.com'")
            print("   方式2: 直接在此文件中修改配置")
            # 可以在这里直接设置测试配置
            # self.base_url = "https://blog.u2u.fun"
            # self.access_token = "pat_eyJraWQiOiJ4SkVTN3J1RzF3YnoyRU9teWhEQVVlZHYxREpLUms1T2FIZ3NIMGgzLTZrIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2Jsb2cudTJ1LmZ1bi8iLCJzdWIiOiJqYXNvbiIsImV4cCI6MTc1MTY0NjU0MCwiaWF0IjoxNzUxMTI4MjAyLCJqdGkiOiI5MzQ0NmM3MS1lNDE0LTU2ZjYtYzRmYy0wNjZmYmJhNWUxN2IiLCJwYXRfbmFtZSI6InBhdC1semRnYzJjeSJ9.OflyYLv1uroTGRztkYCvnDPlpGCDqdLKnd-ATXHo_ip1DY3jlJGidirHQSF2SjUxwt4Z2HGWmQXojl9hq6pH1IiiBBNteL7lphUtMihNSUEdGcqmitIwz5rBRPj_Mssxmsus88UMsmREJlfnVBIEt_becE6Ov-E3lEwWBIumDk02GIz8KQkZ5Qkj-JLnmj0dPU6axGDmO2HMJDDqJqil0sgg9Kps-ujVKJDxFe6b1vi55LwSMwevPx3E30_50v6x2ob4mQGo2ndOge1G9HuSFiefPOLEWjwKRC-3ct0x1xU5uVKcdrXl8V3fe5e4h2jAz1o0oC5sOjeL0hP5zOXZBjssNBWAyAYwCyLKAVrtXfx7Pv4CnX3lSvMDG8QKkxBc7o2TpulrNiEQD7IiuoZt2zpIYfxUqoTGvcTpmWy5cYdt7P8sOFOvSg5iaGhuYi1-Ka8g5yHLRFkrEP1-0wjgzeuMhW0B1cQgylbMZQ9UuSvscede0CHtP4vroU65wHB2PxxzdmqIMVfmTF8-6SHoZNv6DiADlboBh6hhe78RMCn3rVjSZBDfwAwyNiAIdXt52Zvi8p8PtBnkNhwQi24ynhWcJD8UjxAUeuFx_nWkB8NMgzvutukAwUoQtS-eRlhlY7VQTZwMLjrDshL9nIUM_naeJdlQ9B4v4rZzLOUHpws"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Halo-Plugin-Test/1.0'
        })
        
        print(f"🔗 测试环境: {self.base_url}")
        print(f"🔑 Token: {self.access_token[:10] if self.access_token else 'None'}...")
    
    def test_user_info_endpoints(self):
        """测试用户信息获取"""
        print("\n" + "="*50)
        print("📋 测试1: 用户信息获取")
        print("="*50)
        
        endpoints = [
            "/apis/api.console.halo.run/v1alpha1/users/-",
            "/apis/api.console.halo.run/v1alpha1/users/-/profile",
            "/apis/api.halo.run/v1alpha1/users/-",
            "/apis/uc.api.console.halo.run/v1alpha1/users/-"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                print(f"\n🔍 测试: {endpoint}")
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                print(f"   状态: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 提取用户名
                    username = None
                    if "metadata" in data and "name" in data["metadata"]:
                        username = data["metadata"]["name"]
                    elif "spec" in data and "displayName" in data["spec"]:
                        username = data["spec"]["displayName"]
                    
                    results[endpoint] = {
                        "success": True,
                        "username": username,
                        "raw_data": data
                    }
                    
                    if username:
                        print(f"   ✅ 用户名: {username}")
                    else:
                        print(f"   ⚠️  未找到用户名字段")
                else:
                    print(f"   ❌ 失败: {response.text}")
                    results[endpoint] = {"success": False, "error": response.text}
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results[endpoint] = {"success": False, "error": str(e)}
        
        return results
    
    def test_tags_creation(self):
        """测试标签创建"""
        print("\n" + "="*50)
        print("📋 测试2: 标签创建")
        print("="*50)
        
        test_tag = f"测试标签{int(time.time())}"
        
        try:
            # 创建标签
            tag_data = {
                "metadata": {
                    "name": f"tag-test-{int(time.time())}",
                    "generateName": "tag-"
                },
                "spec": {
                    "displayName": test_tag,
                    "slug": f"test-tag-{int(time.time())}",
                    "color": "#6366f1",
                    "cover": ""
                }
            }
            
            print(f"🏷️  创建标签: {test_tag}")
            print(f"   数据: {json.dumps(tag_data, indent=2, ensure_ascii=False)}")
            
            response = self.session.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/tags",
                data=json.dumps(tag_data),
                timeout=10
            )
            
            print(f"   状态: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                tag_id = result.get("metadata", {}).get("name")
                print(f"   ✅ 标签创建成功: {tag_id}")
                return {"success": True, "tag_id": tag_id, "tag_name": test_tag}
            else:
                print(f"   ❌ 标签创建失败")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return {"success": False, "error": str(e)}
    
    def test_post_creation(self):
        """测试文章创建"""
        print("\n" + "="*50)
        print("📋 测试3: 文章创建")
        print("="*50)
        
        test_title = f"测试文章{int(time.time())}"
        
        try:
            # 创建文章
            post_data = {
                "metadata": {
                    "name": f"post-test-{int(time.time())}"
                },
                "spec": {
                    "title": test_title,
                    "slug": f"test-post-{int(time.time())}",
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
            
            print(f"📝 创建文章: {test_title}")
            print(f"   数据: {json.dumps(post_data, indent=2, ensure_ascii=False)}")
            
            response = self.session.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts",
                data=json.dumps(post_data),
                timeout=30
            )
            
            print(f"   状态: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get("metadata", {}).get("name")
                print(f"   ✅ 文章创建成功: {post_id}")
                return {"success": True, "post_id": post_id, "title": test_title}
            else:
                print(f"   ❌ 文章创建失败")
                if response.status_code == 500:
                    print(f"   💥 500错误确认存在")
                return {"success": False, "status_code": response.status_code, "error": response.text}
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return {"success": False, "error": str(e)}
    
    def test_moment_creation(self):
        """测试动态创建"""
        print("\n" + "="*50)
        print("📋 测试4: 动态创建")
        print("="*50)
        
        # 先获取用户信息
        user_results = self.test_user_info_endpoints()
        username = "jason"  # 默认
        
        for endpoint, result in user_results.items():
            if result.get("success") and result.get("username"):
                username = result["username"]
                print(f"   使用用户: {username}")
                break
        
        test_content = f"测试动态{int(time.time())}"
        
        try:
            moment_data = {
                "apiVersion": "moment.halo.run/v1alpha1",
                "kind": "Moment",
                "metadata": {
                    "name": f"moment-test-{int(time.time())}",
                    "generateName": "moment-"
                },
                "spec": {
                    "content": {
                        "raw": test_content,
                        "html": test_content,
                        "medium": []
                    },
                    "owner": username,
                    "tags": ["测试"],
                    "visible": "PUBLIC",
                    "approved": True,
                    "allowComment": True
                }
            }
            
            print(f"💭 创建动态: {test_content}")
            print(f"   预期用户: {username}")
            print(f"   数据: {json.dumps(moment_data, indent=2, ensure_ascii=False)}")
            
            response = self.session.post(
                f"{self.base_url}/apis/moment.halo.run/v1alpha1/moments",
                data=json.dumps(moment_data),
                timeout=30
            )
            
            print(f"   状态: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                actual_owner = result.get("spec", {}).get("owner", "")
                moment_id = result.get("metadata", {}).get("name")
                
                print(f"   ✅ 动态创建成功: {moment_id}")
                print(f"   👤 实际用户: '{actual_owner}'")
                print(f"   🎯 用户匹配: {'✅' if actual_owner == username else '❌'}")
                
                return {
                    "success": True,
                    "moment_id": moment_id,
                    "expected_user": username,
                    "actual_user": actual_owner,
                    "user_match": actual_owner == username
                }
            else:
                print(f"   ❌ 动态创建失败")
                return {"success": False, "status_code": response.status_code, "error": response.text}
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 Halo插件问题验证测试")
        print("="*60)
        
        if not self.base_url or not self.access_token:
            print("❌ 测试配置缺失，请设置环境变量或修改脚本配置")
            return None
        
        results = {
            "timestamp": time.time(),
            "base_url": self.base_url,
            "tests": {}
        }
        
        # 执行所有测试
        results["tests"]["user_info"] = self.test_user_info_endpoints()
        results["tests"]["tag_creation"] = self.test_tags_creation()
        results["tests"]["post_creation"] = self.test_post_creation()
        results["tests"]["moment_creation"] = self.test_moment_creation()
        
        # 保存结果
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 生成总结
        print("\n" + "="*60)
        print("📊 测试结果总结")
        print("="*60)
        
        user_success = any(r.get("success") for r in results["tests"]["user_info"].values())
        tag_success = results["tests"]["tag_creation"].get("success", False)
        post_success = results["tests"]["post_creation"].get("success", False)
        moment_success = results["tests"]["moment_creation"].get("success", False)
        
        print(f"🙋‍♂️ 用户信息获取: {'✅' if user_success else '❌'}")
        print(f"🏷️  标签创建: {'✅' if tag_success else '❌'}")
        print(f"📝 文章创建: {'✅' if post_success else '❌'}")
        print(f"💭 动态创建: {'✅' if moment_success else '❌'}")
        
        if moment_success:
            user_match = results["tests"]["moment_creation"].get("user_match", False)
            actual_user = results["tests"]["moment_creation"].get("actual_user", "")
            print(f"👤 用户信息正确: {'✅' if user_match else '❌'} (实际: {actual_user})")
        
        print(f"\n💾 详细结果保存至: test_results.json")
        
        return results


def main():
    """主函数"""
    print("🚀 启动Halo插件修复验证")
    
    # 提示配置
    if not os.getenv('HALO_BASE_URL'):
        print("\n⚠️  请配置测试环境:")
        print("1. 设置环境变量:")
        print("   export HALO_BASE_URL='https://your-halo-site.com'")
        print("   export HALO_ACCESS_TOKEN='your-token'")
        print("2. 或直接修改脚本中的配置")
        
        # 交互式配置
        if input("\n交互式配置? (y/N): ").lower() == 'y':
            base_url = input("Halo站点URL: ").strip()
            token = input("访问令牌: ").strip()
            os.environ['HALO_BASE_URL'] = base_url
            os.environ['HALO_ACCESS_TOKEN'] = token
        else:
            print("请配置后重新运行")
            return
    
    # 运行测试
    test_suite = HaloFixesTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main() 