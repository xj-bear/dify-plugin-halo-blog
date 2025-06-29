#!/usr/bin/env python3
"""
详细检查快照结构并保存所有数据
"""

import json
import requests

def load_config():
    """加载配置"""
    try:
        with open('key.txt', 'r', encoding='utf-8') as f:
            pat_token = f.read().strip()
        return "https://blog.u2u.fun", pat_token
    except FileNotFoundError:
        print("❌ 找不到 key.txt 文件")
        return None, None

def examine_snapshot_structure():
    """详细检查快照结构"""
    print("🔍 详细检查快照结构")
    print("=" * 60)
    
    base_url, access_token = load_config()
    if not base_url or not access_token:
        return False
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin/1.0'
    })
    
    # 测试快照ID
    snapshot_id = "51d5ae19-af30-4fff-afa1-9d3be6f08a06"
    endpoint = f"{base_url}/apis/content.halo.run/v1alpha1/snapshots/{snapshot_id}"
    
    print(f"📡 获取快照: {snapshot_id}")
    print(f"   端点: {endpoint}")
    
    try:
        response = session.get(endpoint, timeout=30)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 快照获取成功")
            
            # 保存完整快照数据
            filename = f"snapshot_full_{snapshot_id[:8]}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   💾 完整数据已保存到: {filename}")
            
            # 详细分析结构
            print(f"\n📋 快照结构分析:")
            print(f"   顶级字段: {list(data.keys())}")
            
            if 'spec' in data:
                spec = data['spec']
                print(f"   spec字段: {list(spec.keys())}")
                
                # 检查各个字段
                for key, value in spec.items():
                    if isinstance(value, str):
                        print(f"   {key}: '{value[:50]}{'...' if len(value) > 50 else ''}' (长度: {len(value)})")
                    else:
                        print(f"   {key}: {type(value).__name__} - {value}")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"   metadata字段: {list(metadata.keys())}")
            
            return True
        else:
            print(f"   ❌ 获取失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    """主函数"""
    examine_snapshot_structure()

if __name__ == "__main__":
    main() 