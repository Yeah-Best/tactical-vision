"""
对局复盘API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GameReviewRequest, APIResponse, GameReviewResponse
from app.services.review_service import ReviewService
from app.services.game_knowledge_manager import game_knowledge_manager
import json
import asyncio

router = APIRouter()


@router.post("/analyze", response_class=StreamingResponse)
async def analyze_game(
        request: GameReviewRequest,
        db: Session = Depends(get_db)
):
    """
    对局复盘分析（流式输出）

    Args:
        request: 对局复盘请求
        db: 数据库会话

    Returns:
        SSE流式响应
    """
    service = ReviewService(db)

    async def generate():
        full_content = ""
        try:
            async for chunk in service.analyze_game(request):
                full_content += chunk
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # 保存记录到数据库
            await service.save_review_history(request, full_content)

            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/history", response_model=APIResponse)
async def get_review_history(
        limit: int = 20,
        db: Session = Depends(get_db)
):
    """
    获取复盘历史记录

    Args:
        limit: 返回记录数量
        db: 数据库会话

    Returns:
        复盘历史记录列表
    """
    try:
        service = ReviewService(db)
        records = service.get_review_history(limit)

        return APIResponse(
            success=True,
            message="获取复盘历史成功",
            data=[GameReviewResponse.from_orm(record) for record in records]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=APIResponse)
async def get_review_stats(db: Session = Depends(get_db)):
    """
    获取复盘统计信息

    Args:
        db: 数据库会话

    Returns:
        统计信息
    """
    try:
        service = ReviewService(db)
        stats = service.get_review_stats()

        return APIResponse(
            success=True,
            message="获取复盘统计成功",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/feedback", response_model=APIResponse)
async def update_feedback(
        review_id: int,
        feedback: str,
        db: Session = Depends(get_db)
):
    """
    更新玩家反馈

    Args:
        review_id: 复盘记录ID
        feedback: 玩家反馈
        db: 数据库会话

    Returns:
        更新结果
    """
    try:
        service = ReviewService(db)
        success = service.update_player_feedback(review_id, feedback)

        if success:
            return APIResponse(
                success=True,
                message="反馈更新成功"
            )
        else:
            raise HTTPException(status_code=404, detail="复盘记录不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games/supported", response_model=APIResponse)
async def get_supported_games():
    """
    获取支持的游戏列表

    Returns:
        支持的游戏列表及其状态
    """
    try:
        games = game_knowledge_manager.get_supported_games()
        return APIResponse(
            success=True,
            message="获取支持的游戏列表成功",
            data=games
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/refresh", response_model=APIResponse)
async def refresh_knowledge(game_type: str = "王者荣耀"):
    try:
        # 【修改点】：用 asyncio.to_thread 包裹同步的耗时方法，防止阻塞主线程
        result = await asyncio.to_thread(
            game_knowledge_manager.refresh_game_knowledge, 
            game_type
        )
        return APIResponse(
            success=True,
            message=f"{game_type} 知识库刷新成功",
            data={
                "game_type": game_type,
                "version_label": result.get("version_label"),
                # ... 其他返回字段保持不变
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))