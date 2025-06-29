#!/usr/bin/env python3
"""
Halo插件全面功能测试脚本
测试所有核心功能，包括连接、文章CRUD、瞬间CRUD、分类标签获取等
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class HaloPluginTester:
    def __init__(self):
        self.base_url = "https://blog.u2u.fun"
        # 从key.txt读取token
        try:
            with open('key.txt', 'r') as f:
                self.token = f.read().strip()
        except FileNotFoundError:
            print("❌ 错误：找不到key.txt文件")
            exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # 测试结果统计
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # 存储创建的资源ID，用于清理
        self.created_resources = {
            "posts": [],
            "moments": [],
            "tags": [],
            "categories": []
        }

    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"\n{status} - {test_name}")
        if message:
            print(f"   {message}")
        if data and not success:
            print(f"   数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")

    def test_connection(self) -> bool:
        """测试API连接"""
        print("\n🔗 测试1: API连接测试")
        try:
            response = requests.get(
                f"{self.base_url}/apis/api.console.halo.run/v1alpha1/users/-",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                user_name = user_data.get("user", {}).get("metadata", {}).get("name", "未知")
                self.log_test("API连接", True, f"成功连接，当前用户: {user_name}")
                return True
            else:
                self.log_test("API连接", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API连接", False, f"连接异常: {str(e)}")
            return False

    def test_get_posts_list(self) -> bool:
        """测试获取文章列表"""
        print("\n📄 测试2: 获取文章列表")
        try:
            response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts",
                headers=self.headers,
                params={"page": 0, "size": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                items = len(data.get("items", []))
                self.log_test("获取文章列表", True, f"成功获取，总计: {total}篇，当前页: {items}篇")
                return True
            else:
                self.log_test("获取文章列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("获取文章列表", False, f"请求异常: {str(e)}")
            return False

    def test_get_post_detail(self) -> Optional[str]:
        """测试获取文章详情，返回文章ID用于后续更新测试"""
        print("\n📖 测试3: 获取文章详情")
        try:
            # 先获取文章列表
            response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts",
                headers=self.headers,
                params={"page": 0, "size": 1},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("获取文章详情", False, "无法获取文章列表")
                return None
                
            posts = response.json().get("items", [])
            if not posts:
                self.log_test("获取文章详情", False, "没有找到任何文章")
                return None
                
            post_id = posts[0]["metadata"]["name"]
            
            # 获取文章详情
            detail_response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                headers=self.headers,
                timeout=10
            )
            
            if detail_response.status_code == 200:
                post_data = detail_response.json()
                title = post_data.get("spec", {}).get("title", "无标题")
                self.log_test("获取文章详情", True, f"成功获取文章: {title} (ID: {post_id})")
                return post_id
            else:
                self.log_test("获取文章详情", False, f"HTTP {detail_response.status_code}: {detail_response.text}")
                return None
                
        except Exception as e:
            self.log_test("获取文章详情", False, f"请求异常: {str(e)}")
            return None

    def test_create_tag(self) -> Optional[str]:
        """测试创建标签"""
        print("\n🏷️ 测试4: 创建标签")
        try:
            tag_name = f"测试标签-{int(time.time())}"
            tag_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Tag",
                "metadata": {
                    "name": tag_name.lower().replace(" ", "-").replace("测试标签-", "test-tag-"),
                    "generateName": "tag-"
                },
                "spec": {
                    "displayName": tag_name,
                    "slug": tag_name.lower().replace(" ", "-").replace("测试标签-", "test-tag-"),
                    "color": "#3b82f6",
                    "cover": ""
                }
            }
            
            response = requests.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/tags",
                headers=self.headers,
                json=tag_data,
                timeout=10
            )
            
            if response.status_code == 201:
                created_tag = response.json()
                tag_id = created_tag["metadata"]["name"]
                self.created_resources["tags"].append(tag_id)
                self.log_test("创建标签", True, f"成功创建标签: {tag_name} (ID: {tag_id})")
                return tag_id
            else:
                self.log_test("创建标签", False, f"HTTP {response.status_code}: {response.text}", tag_data)
                return None
                
        except Exception as e:
            self.log_test("创建标签", False, f"请求异常: {str(e)}")
            return None

    def test_create_category(self) -> Optional[str]:
        """测试创建分类"""
        print("\n📂 测试5: 创建分类")
        try:
            category_name = f"测试分类-{int(time.time())}"
            category_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Category",
                "metadata": {
                    "name": category_name.lower().replace(" ", "-").replace("测试分类-", "test-category-"),
                    "generateName": "category-"
                },
                "spec": {
                    "displayName": category_name,
                    "slug": category_name.lower().replace(" ", "-").replace("测试分类-", "test-category-"),
                    "description": "这是一个测试分类",
                    "cover": "",
                    "template": "",
                    "priority": 0,
                    "children": []
                }
            }
            
            response = requests.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/categories",
                headers=self.headers,
                json=category_data,
                timeout=10
            )
            
            if response.status_code == 201:
                created_category = response.json()
                category_id = created_category["metadata"]["name"]
                self.created_resources["categories"].append(category_id)
                self.log_test("创建分类", True, f"成功创建分类: {category_name} (ID: {category_id})")
                return category_id
            else:
                self.log_test("创建分类", False, f"HTTP {response.status_code}: {response.text}", category_data)
                return None
                
        except Exception as e:
            self.log_test("创建分类", False, f"请求异常: {str(e)}")
            return None

    def test_create_post(self, tag_id: Optional[str] = None, category_id: Optional[str] = None) -> Optional[str]:
        """测试创建文章"""
        print("\n✍️ 测试6: 创建文章")
        try:
            timestamp = int(time.time())
            post_title = f"测试文章-{timestamp}"
            post_name = f"test-post-{timestamp}"
            
            post_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": post_name,
                    "generateName": "post-"
                },
                "spec": {
                    "title": post_title,
                    "slug": post_name,
                    "template": "",
                    "cover": "",
                    "deleted": False,
                    "publish": False,
                    "publishTime": None,
                    "pinned": False,
                    "allowComment": True,
                    "visible": "PUBLIC",
                    "priority": 0,
                    "excerpt": {
                        "autoGenerate": True,
                        "raw": "这是一篇测试文章的摘要"
                    },
                    "categories": [category_id] if category_id else [],
                    "tags": [tag_id] if tag_id else [],
                    "htmlMetas": []
                }
            }
            
            # 第一步：创建文章
            response = requests.post(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts",
                headers=self.headers,
                json=post_data,
                timeout=10
            )
            
            if response.status_code != 201:
                self.log_test("创建文章", False, f"创建文章失败 HTTP {response.status_code}: {response.text}", post_data)
                return None
            
            created_post = response.json()
            post_id = created_post["metadata"]["name"]
            self.created_resources["posts"].append(post_id)
            
            # 第二步：设置文章内容
            content_data = {
                "raw": f"# {post_title}\n\n这是一篇测试文章的内容。\n\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 测试内容\n\n- 项目一\n- 项目二\n- 项目三",
                "content": f"<h1>{post_title}</h1><p>这是一篇测试文章的内容。</p><p>创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p><h2>测试内容</h2><ul><li>项目一</li><li>项目二</li><li>项目三</li></ul>",
                "rawType": "markdown"
            }
            
            content_response = requests.put(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}/content",
                headers=self.headers,
                json=content_data,
                timeout=10
            )
            
            if content_response.status_code in [200, 201]:
                self.log_test("创建文章", True, f"成功创建文章: {post_title} (ID: {post_id})")
                return post_id
            else:
                self.log_test("创建文章", False, f"设置文章内容失败 HTTP {content_response.status_code}: {content_response.text}")
                return post_id  # 即使内容设置失败，文章已创建
                
        except Exception as e:
            self.log_test("创建文章", False, f"请求异常: {str(e)}")
            return None

    def test_update_post(self, post_id: str) -> bool:
        """测试更新文章"""
        print("\n📝 测试7: 更新文章")
        try:
            # 先获取当前文章信息
            get_response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                headers=self.headers,
                timeout=10
            )
            
            if get_response.status_code != 200:
                self.log_test("更新文章", False, f"无法获取文章信息 HTTP {get_response.status_code}")
                return False
            
            post_data = get_response.json()
            
            # 更新标题
            original_title = post_data["spec"]["title"]
            updated_title = f"{original_title} (已更新-{int(time.time())})"
            post_data["spec"]["title"] = updated_title
            
            # 更新文章
            update_response = requests.put(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                headers=self.headers,
                json=post_data,
                timeout=10
            )
            
            if update_response.status_code == 200:
                self.log_test("更新文章", True, f"成功更新文章标题: {updated_title}")
                return True
            else:
                self.log_test("更新文章", False, f"HTTP {update_response.status_code}: {update_response.text}")
                return False
                
        except Exception as e:
            self.log_test("更新文章", False, f"请求异常: {str(e)}")
            return False

    def test_create_moment(self) -> Optional[str]:
        """测试创建瞬间"""
        print("\n💭 测试8: 创建瞬间")
        try:
            # 先获取用户信息
            user_response = requests.get(
                f"{self.base_url}/apis/api.console.halo.run/v1alpha1/users/-",
                headers=self.headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                self.log_test("创建瞬间", False, "无法获取用户信息")
                return None
            
            user_data = user_response.json()
            owner = user_data.get("user", {}).get("metadata", {}).get("name")
            
            if not owner:
                self.log_test("创建瞬间", False, "无法解析用户名")
                return None
            
            timestamp = int(time.time())
            moment_content = f"这是一条测试瞬间 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            moment_data = {
                "apiVersion": "moment.halo.run/v1alpha1",
                "kind": "Moment",
                "metadata": {
                    "generateName": "moment-"
                },
                "spec": {
                    "content": {
                        "raw": moment_content,
                        "html": f"<p>{moment_content}</p>"
                    },
                    "releaseTime": datetime.now().isoformat() + "Z",
                    "visible": "PUBLIC",
                    "owner": owner,
                    "tags": [],
                    "media": []
                }
            }
            
            response = requests.post(
                f"{self.base_url}/apis/moment.halo.run/v1alpha1/moments",
                headers=self.headers,
                json=moment_data,
                timeout=10
            )
            
            if response.status_code == 201:
                created_moment = response.json()
                moment_id = created_moment["metadata"]["name"]
                self.created_resources["moments"].append(moment_id)
                self.log_test("创建瞬间", True, f"成功创建瞬间 (ID: {moment_id}, 用户: {owner})")
                return moment_id
            else:
                self.log_test("创建瞬间", False, f"HTTP {response.status_code}: {response.text}", moment_data)
                return None
                
        except Exception as e:
            self.log_test("创建瞬间", False, f"请求异常: {str(e)}")
            return None

    def test_get_moments_list(self) -> bool:
        """测试获取瞬间列表"""
        print("\n💭 测试9: 获取瞬间列表")
        try:
            response = requests.get(
                f"{self.base_url}/apis/moment.halo.run/v1alpha1/moments",
                headers=self.headers,
                params={"page": 0, "size": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                items = len(data.get("items", []))
                self.log_test("获取瞬间列表", True, f"成功获取，总计: {total}条，当前页: {items}条")
                return True
            else:
                self.log_test("获取瞬间列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("获取瞬间列表", False, f"请求异常: {str(e)}")
            return False

    def test_get_categories_list(self) -> bool:
        """测试获取分类列表"""
        print("\n📂 测试10: 获取分类列表")
        try:
            response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/categories",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                items = len(data.get("items", []))
                self.log_test("获取分类列表", True, f"成功获取 {items} 个分类")
                return True
            else:
                self.log_test("获取分类列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("获取分类列表", False, f"请求异常: {str(e)}")
            return False

    def test_get_tags_list(self) -> bool:
        """测试获取标签列表"""
        print("\n🏷️ 测试11: 获取标签列表")
        try:
            response = requests.get(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/tags",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                items = len(data.get("items", []))
                self.log_test("获取标签列表", True, f"成功获取 {items} 个标签")
                return True
            else:
                self.log_test("获取标签列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("获取标签列表", False, f"请求异常: {str(e)}")
            return False

    def test_delete_post(self, post_id: str) -> bool:
        """测试删除文章"""
        print("\n🗑️ 测试12: 删除测试文章")
        try:
            response = requests.delete(
                f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                self.log_test("删除文章", True, f"成功删除文章 (ID: {post_id})")
                if post_id in self.created_resources["posts"]:
                    self.created_resources["posts"].remove(post_id)
                return True
            else:
                self.log_test("删除文章", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("删除文章", False, f"请求异常: {str(e)}")
            return False

    def cleanup_resources(self):
        """清理测试过程中创建的资源"""
        print("\n🧹 清理测试资源...")
        
        # 删除创建的文章
        for post_id in self.created_resources["posts"][:]:
            try:
                response = requests.delete(
                    f"{self.base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    print(f"   ✅ 已删除文章: {post_id}")
                    self.created_resources["posts"].remove(post_id)
                else:
                    print(f"   ❌ 删除文章失败: {post_id}")
            except Exception as e:
                print(f"   ❌ 删除文章异常 {post_id}: {str(e)}")
        
        # 删除创建的瞬间
        for moment_id in self.created_resources["moments"][:]:
            try:
                response = requests.delete(
                    f"{self.base_url}/apis/moment.halo.run/v1alpha1/moments/{moment_id}",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    print(f"   ✅ 已删除瞬间: {moment_id}")
                    self.created_resources["moments"].remove(moment_id)
                else:
                    print(f"   ❌ 删除瞬间失败: {moment_id}")
            except Exception as e:
                print(f"   ❌ 删除瞬间异常 {moment_id}: {str(e)}")
        
        # 删除创建的标签
        for tag_id in self.created_resources["tags"][:]:
            try:
                response = requests.delete(
                    f"{self.base_url}/apis/content.halo.run/v1alpha1/tags/{tag_id}",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    print(f"   ✅ 已删除标签: {tag_id}")
                    self.created_resources["tags"].remove(tag_id)
                else:
                    print(f"   ❌ 删除标签失败: {tag_id}")
            except Exception as e:
                print(f"   ❌ 删除标签异常 {tag_id}: {str(e)}")
        
        # 删除创建的分类
        for category_id in self.created_resources["categories"][:]:
            try:
                response = requests.delete(
                    f"{self.base_url}/apis/content.halo.run/v1alpha1/categories/{category_id}",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    print(f"   ✅ 已删除分类: {category_id}")
                    self.created_resources["categories"].remove(category_id)
                else:
                    print(f"   ❌ 删除分类失败: {category_id}")
            except Exception as e:
                print(f"   ❌ 删除分类异常 {category_id}: {str(e)}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Halo插件全面功能测试")
        print("=" * 60)
        
        # 基础连接测试
        if not self.test_connection():
            print("\n❌ 连接测试失败，停止后续测试")
            return
        
        # 读取操作测试
        self.test_get_posts_list()
        existing_post_id = self.test_get_post_detail()
        self.test_get_categories_list()
        self.test_get_tags_list()
        self.test_get_moments_list()
        
        # 创建操作测试
        tag_id = self.test_create_tag()
        category_id = self.test_create_category()
        created_post_id = self.test_create_post(tag_id, category_id)
        moment_id = self.test_create_moment()
        
        # 更新操作测试
        if existing_post_id:
            self.test_update_post(existing_post_id)
        elif created_post_id:
            self.test_update_post(created_post_id)
        
        # 删除操作测试
        if created_post_id:
            self.test_delete_post(created_post_id)
        
        # 清理测试资源
        self.cleanup_resources()
        
        # 显示测试总结
        self.print_summary()

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {self.test_results['passed']}")
        print(f"失败: {self.test_results['failed']}")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.test_results["failed"] > 0:
            print("\n❌ 失败的测试:")
            for error in self.test_results["errors"]:
                print(f"   • {error}")
        
        if success_rate == 100:
            print("\n🎉 所有测试通过！插件功能正常。")
        elif success_rate >= 80:
            print("\n⚠️ 大部分测试通过，有少量问题需要修复。")
        else:
            print("\n💥 多个测试失败，需要全面检查和修复。")

if __name__ == "__main__":
    tester = HaloPluginTester()
    tester.run_all_tests() 