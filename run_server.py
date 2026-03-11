#!/usr/bin/env python3
"""
MBS匹配系统启动脚本
"""
import uvicorn
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 启动MBS匹配系统...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
