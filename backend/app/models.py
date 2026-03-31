"""
数据模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base


class MindsetRecord(Base):
    """心态记录模型"""
    __tablename__ = "mindset_records"

    id = Column(Integer, primary_key=True, index=True)
    emotion_type = Column(String(50), nullable=False)
    emotion_level = Column(Integer, nullable=False)
    emotion_reason = Column(Text)
    guidance_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReviewHistory(Base):
    """复盘历史模型"""
    __tablename__ = "review_history"

    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(String(100), nullable=False)
    game_result = Column(String(20), nullable=False)
    kda = Column(String(50))
    game_description = Column(Text, nullable=False)
    review_report = Column(Text, nullable=False)
    player_feedback = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PlayerProfile(Base):
    """玩家画像模型"""
    __tablename__ = "player_profiles"

    id = Column(Integer, primary_key=True, index=True)
    favorite_heroes = Column(JSON)
    common_mistakes = Column(JSON)
    win_rate = Column(Float)
    total_games = Column(Integer, default=0)
    mindset_score = Column(Float, default=50.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
