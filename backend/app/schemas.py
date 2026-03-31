"""
Pydantic数据模型
用于请求和响应验证
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# 心态管理相关Schema
class MindsetRecordCreate(BaseModel):
    emotion_type: str
    emotion_level: int
    emotion_reason: Optional[str] = None
    guidance_content: Optional[str] = None


class MindsetRecordResponse(BaseModel):
    id: int
    emotion_type: str
    emotion_level: int
    emotion_reason: Optional[str]
    guidance_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EmotionAnalysisRequest(BaseModel):
    message: str
    emotion_type: str = "失落"
    emotion_level: int = 5


# 对局复盘相关Schema
class GameReviewRequest(BaseModel):
    game_type: str
    game_result: str
    kda: Optional[str] = None
    game_description: str


class GameReviewResponse(BaseModel):
    id: int
    game_type: str
    game_result: str
    kda: Optional[str]
    game_description: str
    review_report: str
    player_feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# 战术优化相关Schema
class TacticsRequest(BaseModel):
    favorite_heroes: List[str]
    common_mistakes: List[str]
    win_rate: float
    recent_performance: str


# 通用响应Schema
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
