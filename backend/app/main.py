"""
FastAPI主应用文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.config import settings
from app.database import ensure_database_schema
from app.services.game_knowledge_manager import game_knowledge_manager

# 新增：生命周期管理器，在 FastAPI 启动时执行预热
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：丢入后台线程执行知识库预热，不阻塞服务启动
    print("🚀 正在后台预热游戏知识库...")
    asyncio.create_task(asyncio.to_thread(game_knowledge_manager.ensure_knowledge_base))
    yield
    # 关闭时：可以在这里写清理逻辑

def create_app() -> FastAPI:
    app = FastAPI(
        title="战术视界API",
        description="电竞对局复盘与心态指导智能体",
        version="1.0.0",
        lifespan=lifespan  # 绑定生命周期
    )

    ensure_database_schema()


    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.routers import review, emotion, mindset, tts, game_version
    app.include_router(review.router, prefix="/api/review", tags=["对局复盘"])
    app.include_router(emotion.router, prefix="/api/emotion", tags=["情绪疏导"])
    app.include_router(mindset.router, prefix="/api/mindset", tags=["心态管理"])
    app.include_router(tts.router, prefix="/api/tts", tags=["语音合成"])
    app.include_router(game_version.router, prefix="/api/game-version", tags=["游戏版本"])

    @app.get("/")
    async def root():
        return {"message": "战术视界API", "version": "1.0.0"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app
