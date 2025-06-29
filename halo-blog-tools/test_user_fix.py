#!/usr/bin/env python3
"""简单测试用户信息解析修复"""

import sys
import os
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入工具文件
exec(open('tools/halo-moment-create.py').read())

import json

def test_user_parsing():
    """测试用户信息解析"""
    
    # 模拟实际API返回的数据结构（从test_results.json中获取）
    mock_user_data = {
        "user": {
            "spec": {
                "displayName": "Jason",
                "avatar": "/upload/4d5599ba-88e2-4f32-b6cf-bb98a5f045b0.png",
                "email": "xj_bear@163.com"
            },
            "metadata": {
                "name": "jason",
                "annotations": {
                    "rbac.authorization.halo.run/role-names": "[\"super-role\"]"
                }
            }
        }
    }
    
    print("🧪 测试用户信息解析修复")
    print("="*50)
    
    # 创建工具实例
    tool = HaloMomentCreateTool()
    
    # 创建模拟session
    class MockSession:
        def get(self, url, timeout=None):
            class MockResponse:
                status_code = 200
                def json(self):
                    return mock_user_data
            return MockResponse()
    
    # 测试用户信息提取
    mock_session = MockSession()
    username = tool._get_current_user(mock_session, "https://example.com")
    
    print(f"📋 测试数据结构:")
    print(json.dumps(mock_user_data, indent=2, ensure_ascii=False))
    
    print(f"\n🎯 解析结果:")
    print(f"   提取的用户名: '{username}'")
    print(f"   预期用户名: 'jason'")
    print(f"   解析状态: {'✅ 成功' if username == 'jason' else '❌ 失败'}")
    
    return username == 'jason'

if __name__ == "__main__":
    success = test_user_parsing()
    print(f"\n🏁 测试{'通过' if success else '失败'}") 