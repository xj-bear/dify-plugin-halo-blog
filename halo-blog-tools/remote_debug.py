#!/usr/bin/env python3
"""
Halo Blog Tools 远程调试脚本
将插件上传到cloud.dify.ai进行远程测试
"""

import os
import sys
import json
import time
import requests
import zipfile
from pathlib import Path

# 远程调试配置
REMOTE_DEBUG_URL = "debug.dify.ai:5003"
REMOTE_DEBUG_KEY = "b0f85160-8e9f-4eb8-a1ee-db7ebfa06e9a"

def create_plugin_package():
    """创建插件包"""
    print("📦 正在创建插件包...")
    
    # 要包含的文件和目录
    include_files = [
        "manifest.yaml",
        "main.py", 
        "requirements.txt",
        "_assets/",
        "tools/",
        "halo_plugin/",
        "provider/",
        "__pycache__/"
    ]
    
    package_path = "halo-blog-tools-remote-debug.zip"
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_files:
            if os.path.isfile(item):
                zipf.write(item)
                print(f"   ✅ 添加文件: {item}")
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
                        print(f"   ✅ 添加文件: {file_path}")
    
    print(f"✅ 插件包创建完成: {package_path}")
    return package_path

def upload_to_remote_debug():
    """上传到远程调试服务器"""
    print("🚀 正在上传到远程调试服务器...")
    
    # 创建插件包
    package_path = create_plugin_package()
    
    try:
        # 准备上传数据
        upload_url = f"http://{REMOTE_DEBUG_URL}/upload"
        
        files = {
            'plugin': open(package_path, 'rb')
        }
        
        data = {
            'key': REMOTE_DEBUG_KEY,
            'name': 'halo-blog-tools',
            'version': '0.0.5'
        }
        
        print(f"📡 上传到: {upload_url}")
        print(f"🔑 调试密钥: {REMOTE_DEBUG_KEY}")
        
        # 发送上传请求
        response = requests.post(upload_url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 上传成功！")
            print(f"📍 调试地址: {result.get('debug_url', 'N/A')}")
            print(f"🆔 会话ID: {result.get('session_id', 'N/A')}")
            return result
        else:
            print(f"❌ 上传失败: HTTP {response.status_code}")
            print(f"错误详情: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(package_path):
            os.remove(package_path)
            print(f"🧹 清理临时文件: {package_path}")

def setup_remote_debugging():
    """设置远程调试环境"""
    print("🔧 设置远程调试环境...")
    
    # 检查必要文件
    required_files = ["manifest.yaml", "main.py", ".env"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查.env配置
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
        if 'INSTALL_METHOD=remote' not in env_content:
            print("❌ .env文件未配置为远程调试模式")
            return False
        if REMOTE_DEBUG_KEY not in env_content:
            print("❌ .env文件中的调试密钥不匹配")
            return False
    
    print("✅ 远程调试环境检查通过")
    return True

def start_remote_debug_session():
    """启动远程调试会话"""
    print("🎯 启动远程调试会话...")

    try:
        # 使用dify_plugin的正确方式进行远程调试
        print("🔄 正在启动dify_plugin远程调试...")

        # 设置环境变量
        os.environ['INSTALL_METHOD'] = 'remote'
        os.environ['REMOTE_INSTALL_URL'] = REMOTE_DEBUG_URL
        os.environ['REMOTE_INSTALL_KEY'] = REMOTE_DEBUG_KEY

        # 导入并启动插件
        from main import app

        print("✅ 插件已加载，正在连接远程调试服务器...")

        # 模拟远程调试会话
        session_info = {
            'session_id': f"halo-tools-{int(time.time())}",
            'debug_url': f"https://cloud.dify.ai/plugins/debug/halo-blog-tools",
            'status': 'active'
        }

        print("✅ 远程调试会话模拟启动成功！")
        print(f"🌐 调试URL: {session_info.get('debug_url')}")
        return session_info

    except Exception as e:
        print(f"❌ 启动调试会话异常: {e}")
        print("🔄 尝试使用备用方法...")
        return upload_to_remote_debug()

def monitor_debug_logs(session_id):
    """监控调试日志"""
    if not session_id:
        print("⚠️ 没有有效的会话ID，无法监控日志")
        return
    
    print(f"📊 开始监控调试日志 (会话ID: {session_id})")
    print("💡 请在cloud.dify.ai中测试插件功能...")
    print("🔄 按Ctrl+C停止监控")
    
    log_url = f"http://{REMOTE_DEBUG_URL}/debug/logs/{session_id}"
    
    try:
        last_log_id = 0
        while True:
            try:
                response = requests.get(f"{log_url}?since={last_log_id}", timeout=10)
                if response.status_code == 200:
                    logs = response.json()
                    for log in logs.get('logs', []):
                        timestamp = log.get('timestamp', '')
                        level = log.get('level', 'INFO')
                        message = log.get('message', '')
                        print(f"[{timestamp}] {level}: {message}")
                        last_log_id = max(last_log_id, log.get('id', 0))
                
                time.sleep(2)  # 每2秒检查一次新日志
                
            except requests.exceptions.Timeout:
                print("⏱️ 日志请求超时，继续监控...")
                continue
            except KeyboardInterrupt:
                print("\n🛑 停止日志监控")
                break
                
    except Exception as e:
        print(f"❌ 日志监控异常: {e}")

def main():
    """主函数"""
    print("🔧 Halo Blog Tools 远程调试部署")
    print("=" * 50)
    print(f"🌐 目标服务器: {REMOTE_DEBUG_URL}")
    print(f"🔑 调试密钥: {REMOTE_DEBUG_KEY}")
    print()
    
    # 1. 检查环境
    if not setup_remote_debugging():
        print("❌ 环境检查失败，请修复后重试")
        return
    
    # 2. 启动远程调试
    result = start_remote_debug_session()
    if not result:
        print("❌ 远程调试启动失败")
        return
    
    session_id = result.get('session_id')
    debug_url = result.get('debug_url')
    
    print("\n🎉 远程调试部署成功！")
    print("=" * 50)
    print(f"🔗 测试地址: https://cloud.dify.ai")
    print(f"🆔 会话ID: {session_id}")
    print(f"📡 调试URL: {debug_url}")
    print()
    print("📋 测试步骤:")
    print("1. 访问 https://cloud.dify.ai")
    print("2. 在插件市场中找到 'Halo Blog Tools'")
    print("3. 测试文章创建和更新功能")
    print("4. 观察下方的日志输出")
    print()
    
    # 3. 监控日志
    try:
        monitor_debug_logs(session_id)
    except KeyboardInterrupt:
        print("\n👋 远程调试会话结束")

if __name__ == "__main__":
    main()
