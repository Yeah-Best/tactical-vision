"""
心态管理API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.schemas import APIResponse
from app.services.mindset_service import MindsetService
from app.utils.helpers import MindsetRecordResponse

router = APIRouter()


@router.get("/records", response_model=APIResponse)
async def get_mindset_records(
        start_date: str = None,
        end_date: str = None,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    获取心态记录

    Args:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        limit: 返回记录数量
        db: 数据库会话

    Returns:
        心态记录列表
    """
    try:
        service = MindsetService(db)

        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        records = service.get_mindset_records(start_dt, end_dt, limit)

        return APIResponse(
            success=True,
            message="获取心态记录成功",
            data=[MindsetRecordResponse.from_orm(record) for record in records]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/{year}/{month}", response_model=APIResponse)
async def get_mindset_calendar(
        year: int,
        month: int,
        db: Session = Depends(get_db)
):
    """
    获取心态日历

    Args:
        year: 年份
        month: 月份
        db: 数据库会话

    Returns:
        日历数据
    """
    try:
        service = MindsetService(db)
        calendar_data = service.get_mindset_calendar(year, month)

        return APIResponse(
            success=True,
            message="获取心态日历成功",
            data=calendar_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend", response_model=APIResponse)
async def get_mindset_trend(
        days: int = 30,
        db: Session = Depends(get_db)
):
    """
    获取心态趋势

    Args:
        days: 获取最近多少天的数据
        db: 数据库会话

    Returns:
        趋势数据
    """
    try:
        service = MindsetService(db)
        trend_data = service.get_mindset_trend(days)

        return APIResponse(
            success=True,
            message="获取心态趋势成功",
            data=trend_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pregame-guidance", response_model=APIResponse)
async def get_pregame_guidance(db: Session = Depends(get_db)):
    """
    获取赛前心态预热指导

    Args:
        db: 数据库会话

    Returns:
        赛前指导内容
    """
    try:
        service = MindsetService(db)
        guidance = service.generate_pregame_guidance()

        return APIResponse(
            success=True,
            message="获取赛前指导成功",
            data={"guidance": guidance}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=APIResponse)
async def get_player_profile(db: Session = Depends(get_db)):
    """
    获取玩家画像

    Args:
        db: 数据库会话

    Returns:
        玩家画像
    """
    try:
        service = MindsetService(db)
        profile = service.get_player_profile()

        return APIResponse(
            success=True,
            message="获取玩家画像成功",
            data=profile
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
