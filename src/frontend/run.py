#!/usr/bin/env python3
"""
DeepResearch Streamlit 前端启动脚本
"""

import os
import sys
import subprocess

def main():
    """启动Streamlit应用"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    # 检查app.py是否存在
    if not os.path.exists(app_path):
        print(f"错误: 找不到 {app_path}")
        sys.exit(1)
    
    # 启动Streamlit应用
    try:
        print("🚀 启动 DeepResearch AI 研究助手...")
        print(f"📁 应用路径: {app_path}")
        print("🌐 应用将在浏览器中自动打开")
        print("⏹️  按 Ctrl+C 停止应用")
        print("-" * 50)
        
        # 运行streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()