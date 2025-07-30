#!/usr/bin/env python3
"""
DeepResearch 前端启动脚本
在项目根目录运行此脚本来启动Streamlit前端界面
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查必要的依赖"""
    try:
        import streamlit
        print("✅ Streamlit 已安装")
    except ImportError:
        print("❌ Streamlit 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])
    
    try:
        import markdown
        print("✅ Markdown 已安装")
    except ImportError:
        print("❌ Markdown 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "markdown>=3.4.0"])

def main():
    """主函数"""
    print("🔍 DeepResearch AI 前端启动器")
    print("=" * 40)
    
    # 检查依赖
    print("📦 检查依赖...")
    check_dependencies()
    
    # 获取应用路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "src", "frontend", "app.py")
    
    if not os.path.exists(app_path):
        print(f"❌ 错误: 找不到应用文件 {app_path}")
        sys.exit(1)
    
    print(f"📁 应用路径: {app_path}")
    print("🚀 启动 Streamlit 应用...")
    print("🌐 应用将在浏览器中自动打开")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 40)
    
    try:
        # 启动Streamlit应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔧 故障排除:")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 检查DeepResearch模块是否正确配置")
        print("3. 确保配置文件存在且正确")
        sys.exit(1)

if __name__ == "__main__":
    main()