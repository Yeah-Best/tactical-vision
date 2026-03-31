"""
情绪疏导API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EmotionAnalysisRequest, APIResponse, MindsetRecordResponse
from app.services.emotion_service import EmotionService
import json

router = APIRouter()


@router.post("/analyze", response_class=StreamingResponse)
async def analyze_emotion(
        request: EmotionAnalysisRequest,
        db: Session = Depends(get_db)
):
    """
    情绪分析（流式输出）

    Args:
        request: 情绪分析请求
        db: 数据库会话

    Returns:
        SSE流式响应
    """
    service = EmotionService(db)

    async def generate():
        full_content = ""
        try:
            async for chunk in service.analyze_emotion(request):
                full_content += chunk
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # 保存记录到数据库
            await service.save_emotion_record(request, full_content)

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
async def get_emotion_history(
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """
    获取情绪历史记录

    Args:
        limit: 返回记录数量
        db: 数据库会话

    Returns:
        情绪历史记录列表
    """
    try:
        service = EmotionService(db)
        records = service.get_recent_emotions(limit)

        return APIResponse(
            success=True,
            message="获取情绪历史成功",
            data=[MindsetRecordResponse.from_orm(record) for record in records]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=APIResponse)
async def get_emotion_stats(db: Session = Depends(get_db)):
    """
    获取情绪统计信息

    Args:
        db: 数据库会话

    Returns:
        统计信息
    """
    try:
        service = EmotionService(db)
        stats = service.get_emotion_stats()

        return APIResponse(
            success=True,
            message="获取情绪统计成功",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
