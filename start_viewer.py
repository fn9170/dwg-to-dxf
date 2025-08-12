#!/usr/bin/env python3
"""
启动本地HTTP服务器来查看GeoJSON数据可视化界面
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def start_server(port=8000):
    """启动HTTP服务器"""
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 创建HTTP服务器
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"🚀 服务器已启动!")
            print(f"📁 服务目录: {script_dir}")
            print(f"🌐 访问地址: http://localhost:{port}")
            print(f"📊 数据查看器: http://localhost:{port}/viewer.html")
            print(f"📁 数据目录: http://localhost:{port}/tj_metro_lines/")
            print("\n💡 提示:")
            print("   - 在浏览器中打开 viewer.html 查看可视化界面")
            print("   - 按 Ctrl+C 停止服务器")
            print("   - 确保 tj_metro_lines 目录存在且包含GeoJSON文件")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f"http://localhost:{port}/viewer.html")
                print(f"\n✅ 已自动打开浏览器")
            except:
                print(f"\n⚠️  请手动在浏览器中打开: http://localhost:{port}/viewer.html")
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 已被占用，尝试使用其他端口...")
            start_server(port + 1)
        else:
            print(f"❌ 启动服务器失败: {e}")
    except KeyboardInterrupt:
        print(f"\n🛑 服务器已停止")

if __name__ == "__main__":
    print("🌍 天津地铁5号线数据查看器")
    print("=" * 50)
    start_server()
