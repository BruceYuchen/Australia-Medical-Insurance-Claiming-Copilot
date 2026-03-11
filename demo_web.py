#!/usr/bin/env python3
"""
MBS匹配系统Web界面演示脚本
"""
import webbrowser
import time
import requests
import subprocess
import sys
import os
from threading import Thread

def check_server_running():
    """检查服务器是否正在运行"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动MBS匹配系统服务器...")
    try:
        # 激活虚拟环境并启动服务器
        if os.name == 'nt':  # Windows
            subprocess.run([sys.executable, "run_server.py"], check=True)
        else:  # Unix/Linux/Mac
            subprocess.run(["python3", "run_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动服务器失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 服务器已停止")
        return False
    return True

def wait_for_server(max_wait=30):
    """等待服务器启动"""
    print("⏳ 等待服务器启动...")
    for i in range(max_wait):
        if check_server_running():
            print("✅ 服务器启动成功!")
            return True
        time.sleep(1)
        print(f"   等待中... ({i+1}/{max_wait})")
    
    print("❌ 服务器启动超时")
    return False

def open_web_interface():
    """打开Web界面"""
    print("🌐 打开Web界面...")
    try:
        webbrowser.open("http://localhost:8000")
        print("✅ Web界面已在浏览器中打开")
        print("📖 访问地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
    except Exception as e:
        print(f"❌ 打开浏览器失败: {e}")
        print("💡 请手动访问: http://localhost:8000")

def demo_features():
    """演示系统功能"""
    print("\n🎯 系统功能演示")
    print("=" * 50)
    
    # 演示搜索功能
    print("\n1. 症状文本搜索演示")
    search_examples = [
        "患者主诉胸痛、呼吸困难，需要咨询",
        "general practitioner consultation 20 minutes",
        "mental health assessment and treatment plan",
        "chest pain shortness of breath consultation"
    ]
    
    for i, example in enumerate(search_examples, 1):
        print(f"\n   示例 {i}: {example}")
        try:
            response = requests.post("http://localhost:8000/suggest_items", 
                json={
                    "transcript": example,
                    "context": {
                        "setting": "consulting_rooms",
                        "duration": 30,
                        "referral": False,
                        "provider": "general practitioner",
                        "date": "2024-01-15T10:00:00Z",
                        "patient_type": "community"
                    },
                    "top_k": 3
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 找到 {result['total_found']} 个建议项目")
                for j, suggestion in enumerate(result['suggestions'][:3], 1):
                    confidence = int(suggestion['score'] * 100)
                    print(f"      {j}. Item {suggestion['item_num']} (置信度: {confidence}%)")
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 搜索错误: {e}")
    
    # 演示验证功能
    print("\n2. 项目验证演示")
    validation_examples = [
        {
            "items": ["3", "4", "23"],
            "description": "基础咨询项目组合"
        },
        {
            "items": ["2713", "92115"],
            "description": "心理健康相关项目"
        }
    ]
    
    for i, example in enumerate(validation_examples, 1):
        print(f"\n   示例 {i}: {example['description']}")
        try:
            response = requests.post("http://localhost:8000/validate_claim",
                json={
                    "selected_items": example["items"],
                    "context": {
                        "setting": "consulting_rooms",
                        "duration": 30,
                        "referral": False,
                        "provider": "general practitioner",
                        "date": "2024-01-15T10:00:00Z",
                        "patient_type": "community"
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                validation = result['result']
                print(f"   ✅ 验证完成")
                print(f"      可计费项目: {validation['billable_items']}")
                print(f"      被拒绝项目: {validation['rejected_items']}")
                print(f"      处理时间: {result['processing_time']:.3f}秒")
            else:
                print(f"   ❌ 验证失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 验证错误: {e}")

def main():
    """主函数"""
    print("🎉 MBS匹配系统Web界面演示")
    print("=" * 50)
    
    # 检查服务器是否已运行
    if check_server_running():
        print("✅ 检测到服务器已在运行")
        open_web_interface()
        demo_features()
        
        print("\n" + "=" * 50)
        print("🎯 Web界面功能说明:")
        print("   • 左侧: 症状文本搜索，支持置信度排序")
        print("   • 右侧: 项目验证，实时显示验证结果")
        print("   • 底部: 系统统计信息")
        print("   • 置信度颜色: 绿色(高) > 黄色(中) > 橙色(低) > 红色(很低)")
        print("\n💡 使用提示:")
        print("   • 输入症状描述后点击'搜索项目'")
        print("   • 勾选感兴趣的项目进行验证")
        print("   • 点击置信度排序按钮切换排序方式")
        print("   • 查看验证结果了解项目冲突和限制")
        
        input("\n按回车键继续...")
    else:
        print("🚀 启动服务器...")
        
        # 在后台线程启动服务器
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        if wait_for_server():
            open_web_interface()
            demo_features()
            
            print("\n" + "=" * 50)
            print("🎯 Web界面已启动!")
            print("📖 访问地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/docs")
            print("\n💡 功能特色:")
            print("   • 🎨 现代化响应式界面")
            print("   • 📊 置信度可视化排序")
            print("   • ⚡ 实时搜索和验证")
            print("   • 📈 系统统计信息")
            print("   • 🔍 智能项目匹配")
            
            try:
                print("\n⏹️ 按 Ctrl+C 停止服务器")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 演示结束!")
        else:
            print("❌ 无法启动服务器，请检查端口8000是否被占用")

if __name__ == "__main__":
    main()
