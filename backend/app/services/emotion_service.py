"""
情绪疏导业务逻辑
"""

from typing import AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import MindsetRecord
from app.schemas import EmotionAnalysisRequest
from app.services.hunyuan_client import hunyuan_client
from app.utils.helpers import get_emotion_label, get_emotion_color


class EmotionService:
    """情绪疏导服务"""

    def __init__(self, db: Session):
        self.db = db

    async def analyze_emotion(
            self,
            request: EmotionAnalysisRequest
    ) -> AsyncGenerator[str, None]:
        """
        分析情绪并生成疏导内容

        Args:
            request: 情绪分析请求

        Yields:
            逐字生成的疏导内容
        """
        # 调用AI生成疏导内容
        async for chunk in hunyuan_client.analyze_emotion(
                request.message,
                request.emotion_type,
                request.emotion_level
        ):
            yield chunk

    async def save_emotion_record(
            self,
            request: EmotionAnalysisRequest,
            guidance_content: str
    ) -> MindsetRecord:
        """
        保存情绪记录到数据库

        Args:
            request: 情绪分析请求
            guidance_content: AI生成的疏导内容

        Returns:
            保存的心态记录
        """
        record = MindsetRecord(
            emotion_type=request.emotion_type,
            emotion_level=request.emotion_level,
            emotion_reason=request.message,
            guidance_content=guidance_content
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def get_recent_emotions(self, limit: int = 10):
        """
        获取最近的情绪记录

        Args:
            limit: 返回记录数量

        Returns:
            情绪记录列表
        """
        records = self.db.query(MindsetRecord).order_by(
            MindsetRecord.created_at.desc()
        ).limit(limit).all()

        return records

    def get_emotion_stats(self):
        """
        获取情绪统计信息

        Returns:
            统计信息字典
        """
        total_records = self.db.query(MindsetRecord).count()

        if total_records == 0:
            return {
                "total_records": 0,
                "avg_emotion_level": 0,
                "emotion_distribution": {}
            }

        # 【修复点】：去掉了外层多余的 self.db.query()，直接获取标量值
        avg_level = self.db.query(func.avg(MindsetRecord.emotion_level)).scalar()
        
        # 处理可能的 None 值（防守型编程）
        avg_level = avg_level if avg_level is not None else 0

        # 情绪类型分布
        distribution = {}
        results = self.db.query(
            MindsetRecord.emotion_type,
            func.count(MindsetRecord.id)
        ).group_by(MindsetRecord.emotion_type).all()

        for emotion_type, count in results:
            distribution[emotion_type] = count

        return {
            "total_records": total_records,
            "avg_emotion_level": round(float(avg_level), 2),
            "emotion_distribution": distribution
        }