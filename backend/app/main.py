"""
FastAPI主应用文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="战术视界API",
        description="电竞对局复盘与心态指导智能体",
        version="1.0.0"
    )

    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.routers import review, emotion, mindset
    app.include_router(review.router, prefix="/api/review", tags=["对局复盘"])
    app.include_router(emotion.router, prefix="/api/emotion", tags=["情绪疏导"])
    app.include_router(mindset.router, prefix="/api/mindset", tags=["心态管理"])

    @app.get("/")
    async def root():
        return {"message": "战术视界API", "version": "1.0.0"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app
