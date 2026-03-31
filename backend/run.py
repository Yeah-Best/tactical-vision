#!/usr/bin/env python3
"""
战术视界 - 后端启动脚本
FastAPI应用入口文件
"""

import uvicorn
from app.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
