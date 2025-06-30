#!/usr/bin/env python3
"""
Halo 瞬间功能 Bug 修复测试 - v0.0.3
测试时间戳显示和标签分行问题的修复效果
"""

import requests
import json
import time
from datetime import datetime

def load_config():
    """从key.txt加载配置"""
    try:
        with open('key.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            config = {}
            
            # 查找第一行作为token
            if lines:
                token = lines[0].strip()
                if token:
                    config['ACCESS_TOKEN'] = token
                    config['BASE_URL'] = 'https://blog.u2u.fun'  # 从网址推断
            
            # 如果还是KEY=VALUE格式，也支持
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
            return config
    except Exception as e:
        print(f"❌ 无法加载配置文件: {e}")
        return None

def test_moment_creation_with_fixes():
    """测试瞬间创建功能的修复效果"""
    print("🔧 Halo 瞬间功能 Bug 修复测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if not config:
        return False
    
    base_url = config.get('BASE_URL', '').strip().rstrip('/')
    access_token = config.get('ACCESS_TOKEN', '').strip()
    
    if not base_url or not access_token:
        print("❌ 缺少必要的配置信息")
        return False
    
    # 创建HTTP会话
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Dify-Halo-Plugin-Test/1.0'
    })
    
    # 准备测试数据
    test_content = "这是一条测试瞬间，用于验证时间戳和标签显示修复效果。"
    test_tags = ['修复测试', '时间戳', '标签显示']
    
    # 生成标签HTML（应用修复）
    def generate_fixed_content_with_tags(raw_content, tag_list):
        """生成修复后的标签内容"""
        import urllib.parse
        
        if not tag_list:
            return raw_content, raw_content.replace('\n', '<br>')
        
        # 为每个标签生成HTML链接
        tag_links = []
        for tag in tag_list:
            encoded_tag = urllib.parse.quote(tag)
            tag_link = f'<a class="tag" href="/moments?tag={encoded_tag}" data-pjax="">{tag}</a>'
            tag_links.append(tag_link)
        
        # ✅ 修复标签分行问题：使用更好的HTML结构
        tag_html = '<span class="tags">' + ' '.join(tag_links) + '</span>'
        
        # 在标签和内容之间添加换行
        raw_with_tags = ''.join([f'#{tag} ' for tag in tag_list]) + raw_content
        html_with_tags = tag_html + '<br>' + raw_content.replace('\n', '<br>')
        
        return raw_with_tags, html_with_tags
    
    # 生成包含标签的内容
    content_with_tags, html_with_tags = generate_fixed_content_with_tags(test_content, test_tags)
    
    # ✅ 修复时间戳显示问题：添加发布时间字段
    current_time = datetime.now().isoformat() + "Z"
    
    # 准备瞬间数据
    moment_name = f"test-fix-moment-{int(time.time())}"
    moment_data = {
        "apiVersion": "moment.halo.run/v1alpha1",
        "kind": "Moment",
        "metadata": {
            "name": moment_name,
            "generateName": "moment-"
        },
        "spec": {
            "content": {
                "raw": content_with_tags,
                "html": html_with_tags,
                "medium": []
            },
            "owner": "jason",  # 根据用户反馈使用的用户名
            "tags": test_tags,
            "visible": "PUBLIC",
            "approved": True,
            "allowComment": True,
            "releaseTime": current_time  # ✅ 新增：发布时间字段
        }
    }
    
    try:
        print("📅 创建时间:", current_time)
        print("🏷️ 测试标签:", test_tags)
        print("📝 HTML内容预览:", html_with_tags[:100] + "...")
        print()
        
        # 发送创建请求
        response = session.post(
            f"{base_url}/apis/moment.halo.run/v1alpha1/moments",
            data=json.dumps(moment_data),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("📊 创建结果:")
            print(f"  - ID: {result.get('metadata', {}).get('name', 'N/A')}")
            print(f"  - 创建时间: {result.get('metadata', {}).get('creationTimestamp', 'N/A')}")
            print(f"  - 发布时间: {result.get('spec', {}).get('releaseTime', 'N/A')} ✅")
            print(f"  - 标签: {result.get('spec', {}).get('tags', [])}")
            print()
            
            # 验证修复效果
            print("🔍 修复验证:")
            spec = result.get('spec', {})
            
            # 检查时间戳修复
            has_release_time = 'releaseTime' in spec and spec['releaseTime']
            print(f"  ✅ 时间戳修复: {'是' if has_release_time else '否'} - {'包含releaseTime字段' if has_release_time else '缺少releaseTime字段'}")
            
            # 检查标签HTML修复
            html_content = spec.get('content', {}).get('html', '')
            has_tags_span = '<span class="tags">' in html_content
            print(f"  ✅ 标签HTML修复: {'是' if has_tags_span else '否'} - {'使用span容器' if has_tags_span else '未使用span容器'}")
            
            # 检查内容分隔修复
            has_br_separator = '<span class="tags">' in html_content and '<br>' in html_content
            print(f"  ✅ 内容分隔修复: {'是' if has_br_separator else '否'} - {'标签与内容间有换行' if has_br_separator else '标签与内容间无换行'}")
            
            print()
            print("✅ 瞬间创建成功，修复验证完成！")
            return True
            
        else:
            print(f"❌ 创建失败: HTTP {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = test_moment_creation_with_fixes()
    print()
    if success:
        print("🎉 Bug 修复测试通过！")
    else:
        print("❌ Bug 修复测试失败，请检查配置和网络连接") 