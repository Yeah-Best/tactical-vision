"""
游戏版本信息 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.services.game_version_service import get_latest_game_version, game_version_service

logger = logging.getLogger(__name__)

router = APIRouter()


class GameVersionInfo(BaseModel):
    """游戏版本信息模型"""
    game_name: str = Field(..., description="游戏名称")
    version: str = Field(..., description="版本号")
    update_time: str = Field(..., description="更新时间")
    update_content: Optional[str] = Field(None, description="更新内容摘要")
    source_url: Optional[str] = Field(None, description="来源链接")


@router.get("/latest", response_model=GameVersionInfo)
async def get_latest_version(game: str = "honor_of_kings"):
    """
    获取指定游戏的最新版本信息

    Args:
        game: 游戏名称 (honor_of_kings, lol, valorant, 或中文名称)

    Returns:
        游戏版本信息
    """
    try:
        logger.info(f"获取游戏版本: {game}")

        version_info = get_latest_game_version(game)

        if version_info is None:
            raise HTTPException(status_code=404, detail=f"无法获取游戏 '{game}' 的版本信息")

        return GameVersionInfo(**version_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取版本信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取版本信息失败")


@router.get("/all", response_model=List[GameVersionInfo])
async def get_all_versions():
    """
    获取所有支持游戏的版本信息

    Returns:
        所有游戏的版本信息列表
    """
    try:
        logger.info("获取所有游戏版本信息")

        versions = game_version_service.get_game_versions()

        if not versions:
            raise HTTPException(status_code=404, detail="无法获取任何游戏的版本信息")

        return [GameVersionInfo(**v) for v in versions]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取所有版本信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取版本信息失败")


@router.get("/supported-games")
async def get_supported_games():
    """
    获取支持的游戏列表

    Returns:
        支持的游戏列表
    """
    return {
        "games": [
            {
                "code": "honor_of_kings",
                "name": "王者荣耀",
                "platform": "Tencent"
            },
            {
                "code": "lol",
                "name": "英雄联盟",
                "platform": "Tencent"
            },
            {
                "code": "valorant",
                "name": "无畏契约",
                "platform": "Tencent"
            }
        ]
    }
