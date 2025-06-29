#!/usr/bin/env python3
"""直接测试用户信息解析逻辑"""

def parse_user_info(user_data):
    """提取用户信息的逻辑（从工具中复制）"""
    username = None
    
    # 方法1：从嵌套的user.metadata.name获取（实际API返回格式）
    if "user" in user_data and "metadata" in user_data["user"]:
        username = user_data["user"]["metadata"].get("name")
    
    # 方法2：从顶级metadata.name获取
    elif "metadata" in user_data and "name" in user_data["metadata"]:
        username = user_data["metadata"]["name"]
    
    # 方法3：从spec.displayName获取
    elif "spec" in user_data and "displayName" in user_data["spec"]:
        username = user_data["spec"]["displayName"]
    
    # 方法4：从嵌套的user.spec.displayName获取
    elif "user" in user_data and "spec" in user_data["user"]:
        username = user_data["user"]["spec"].get("displayName")
    
    # 方法5：直接从顶级字段获取
    elif "name" in user_data:
        username = user_data["name"]
    elif "username" in user_data:
        username = user_data["username"]
    elif "displayName" in user_data:
        username = user_data["displayName"]
    
    return username.strip() if username and username.strip() else None

def test():
    """测试解析逻辑"""
    # 实际API返回的数据结构
    test_data = {
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
    
    print("🧪 用户信息解析测试")
    print("="*40)
    
    result = parse_user_info(test_data)
    
    print(f"📋 数据结构: user.metadata.name = '{test_data['user']['metadata']['name']}'")
    print(f"🎯 解析结果: '{result}'")
    print(f"✅ 测试状态: {'通过' if result == 'jason' else '失败'}")
    
    # 测试其他可能的数据结构
    print("\n🔍 测试其他数据结构...")
    
    test_cases = [
        {"metadata": {"name": "jason"}},  # 直接metadata格式
        {"spec": {"displayName": "jason"}},  # spec格式
        {"name": "jason"},  # 直接name格式
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = parse_user_info(case)
        print(f"   测试{i}: {result} {'✅' if result == 'jason' else '❌'}")

if __name__ == "__main__":
    test()
