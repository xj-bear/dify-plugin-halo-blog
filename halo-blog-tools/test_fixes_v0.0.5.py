#!/usr/bin/env python3
"""
Halo Blog Tools v0.0.5 修复验证测试
测试文章创建编辑器兼容性和文章更新功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.halo_post_create import HaloPostCreateTool
from tools.halo_post_update import HaloPostUpdateTool
from dify_plugin.entities.tool import ToolInvokeMessage
import time
from datetime import datetime

class MockRuntime:
    """模拟运行时环境"""
    def __init__(self):
        self.credentials = {
            "base_url": "https://blog.u2u.fun",  # 请替换为实际的Halo地址
            "access_token": "pat_your_token_here"  # 请替换为实际的token
        }

def test_post_creation_editor_compatibility():
    """测试文章创建的编辑器兼容性"""
    print("🧪 测试1: 文章创建编辑器兼容性")
    print("=" * 50)
    
    # 创建工具实例
    tool = HaloPostCreateTool()
    tool.runtime = MockRuntime()
    
    # 测试参数
    test_params = {
        "title": f"编辑器兼容性测试 - {datetime.now().strftime('%H:%M:%S')}",
        "content": f"""# 编辑器兼容性测试

这是一篇测试文章，用于验证v0.0.5版本的编辑器兼容性修复。

## 测试内容

- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **版本**: v0.0.5
- **测试项目**: 编辑器兼容性

## Markdown格式测试

### 代码块
```python
def hello_world():
    print("Hello, Halo!")
```

### 列表
1. 第一项
2. 第二项
3. 第三项

### 链接和图片
[Halo官网](https://www.halo.run)

**测试完成时间**: {int(time.time())}
""",
        "tags": "测试,编辑器,v0.0.5",
        "categories": "测试分类",
        "excerpt": "这是一篇用于测试编辑器兼容性的文章",
        "publish_immediately": False,
        "editor_type": "default"
    }
    
    try:
        # 执行创建
        messages = list(tool._invoke(test_params))
        
        # 分析结果
        success = False
        post_id = None
        editor_compatible = False
        
        for msg in messages:
            if isinstance(msg, ToolInvokeMessage):
                if msg.type == "text":
                    print(f"📝 {msg.message}")
                    if "文章创建成功" in msg.message:
                        success = True
                    if "编辑器兼容性" in msg.message and "✅" in msg.message:
                        editor_compatible = True
                elif msg.type == "json":
                    data = msg.message
                    if isinstance(data, dict):
                        post_id = data.get("post_id")
                        editor_compatible = data.get("editor_compatible", False)
        
        print(f"\n📊 测试结果:")
        print(f"   创建成功: {'✅' if success else '❌'}")
        print(f"   编辑器兼容: {'✅' if editor_compatible else '❌'}")
        print(f"   文章ID: {post_id if post_id else 'N/A'}")
        
        return post_id if success else None
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return None

def test_post_update_functionality(post_id):
    """测试文章更新功能"""
    if not post_id:
        print("\n⏭️ 跳过更新测试（没有可用的文章ID）")
        return
        
    print("\n🧪 测试2: 文章更新功能")
    print("=" * 50)
    
    # 创建工具实例
    tool = HaloPostUpdateTool()
    tool.runtime = MockRuntime()
    
    # 更新参数
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_params = {
        "post_id": post_id,
        "title": f"更新测试文章 - {update_time}",
        "content": f"""# 文章更新测试

这是更新后的内容，用于验证v0.0.5版本的文章更新修复。

## 更新信息

- **更新时间**: {update_time}
- **版本**: v0.0.5
- **测试项目**: 文章更新功能
- **时间戳**: {int(time.time())}

## 更新验证

### 修复内容
1. ✅ 修复了datetime导入缺失问题
2. ✅ 重构了更新逻辑顺序
3. ✅ 改进了内容设置机制
4. ✅ 优化了错误处理

### 技术改进
- **快照机制**: 在文章更新后创建
- **内容设置**: 使用正确的API调用顺序
- **状态报告**: 提供详细的更新状态

**验证完成**: {update_time}
""",
        "tags": "更新测试,v0.0.5,修复验证",
        "editor_type": "default"
    }
    
    try:
        # 执行更新
        messages = list(tool._invoke(test_params))
        
        # 分析结果
        success = False
        content_updated = False
        content_update_success = None
        
        for msg in messages:
            if isinstance(msg, ToolInvokeMessage):
                if msg.type == "text":
                    print(f"📝 {msg.message}")
                    if "文章更新成功" in msg.message:
                        success = True
                    if "内容" in msg.message and "已更新" in msg.message:
                        content_updated = True
                elif msg.type == "json":
                    data = msg.message
                    if isinstance(data, dict):
                        content_update_success = data.get("content_update_success")
        
        print(f"\n📊 测试结果:")
        print(f"   更新成功: {'✅' if success else '❌'}")
        print(f"   内容更新: {'✅' if content_updated else '❌'}")
        print(f"   内容设置: {'✅' if content_update_success else '⚠️' if content_update_success is False else 'N/A'}")
        
        return success and content_updated
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 Halo Blog Tools v0.0.5 修复验证测试")
    print("=" * 60)
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 测试版本: v0.0.5")
    print()
    
    # 检查配置
    runtime = MockRuntime()
    if runtime.credentials["access_token"] == "pat_your_token_here":
        print("⚠️ 警告: 请在脚本中配置正确的Halo访问令牌")
        print("   请修改 MockRuntime 类中的 credentials")
        print()
    
    # 测试1: 文章创建编辑器兼容性
    post_id = test_post_creation_editor_compatibility()
    
    # 测试2: 文章更新功能
    update_success = test_post_update_functionality(post_id)
    
    # 总结
    print("\n📊 测试总结")
    print("=" * 50)
    
    creation_status = "✅ 通过" if post_id else "❌ 失败"
    update_status = "✅ 通过" if update_success else "❌ 失败" if post_id else "⏭️ 跳过"
    
    print(f"文章创建编辑器兼容性: {creation_status}")
    print(f"文章更新功能: {update_status}")
    
    if post_id and update_success:
        print("\n🎉 所有测试通过！v0.0.5修复验证成功！")
        print(f"🔗 可以在编辑器中查看文章: https://blog.u2u.fun/console/posts/editor?name={post_id}")
    elif post_id:
        print("\n⚠️ 部分测试通过，请检查文章更新功能")
    else:
        print("\n❌ 测试失败，请检查配置和网络连接")
    
    print(f"\n💡 提示: 请在Halo后台验证文章的实际创建和更新效果")

if __name__ == "__main__":
    main()
