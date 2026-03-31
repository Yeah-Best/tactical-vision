"""
对局复盘业务逻辑
"""

from typing import AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import func  # 【修复点 1】：必须显式导入 func
from app.models import ReviewHistory
from app.schemas import GameReviewRequest
from app.services.hunyuan_client import hunyuan_client


class ReviewService:
    """对局复盘服务"""

    def __init__(self, db: Session):
        self.db = db

    async def analyze_game(
            self,
            request: GameReviewRequest
    ) -> AsyncGenerator[str, None]:
        """
        分析对局并生成复盘报告

        Args:
            request: 对局复盘请求

        Yields:
            逐字生成的复盘报告
        """
        game_data = {
            "game_type": request.game_type,
            "game_result": request.game_result,
            "kda": request.kda,
            "game_description": request.game_description
        }

        # 调用AI生成复盘报告
        async for chunk in hunyuan_client.analyze_game_review(game_data):
            yield chunk

    async def save_review_history(
            self,
            request: GameReviewRequest,
            review_report: str
    ) -> ReviewHistory:
        """
        保存复盘历史到数据库

        Args:
            request: 对局复盘请求
            review_report: AI生成的复盘报告

        Returns:
            保存的复盘历史记录
        """
        history = ReviewHistory(
            game_type=request.game_type,
            game_result=request.game_result,
            kda=request.kda,
            game_description=request.game_description,
            review_report=review_report
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        return history

    def get_review_history(self, limit: int = 20):
        """
        获取复盘历史记录

        Args:
            limit: 返回记录数量

        Returns:
            复盘历史记录列表
        """
        records = self.db.query(ReviewHistory).order_by(
            ReviewHistory.created_at.desc()
        ).limit(limit).all()

        return records

    def get_review_by_id(self, review_id: int):
        """
        根据ID获取复盘记录

        Args:
            review_id: 复盘记录ID

        Returns:
            复盘记录
        """
        return self.db.query(ReviewHistory).filter(
            ReviewHistory.id == review_id
        ).first()

    def update_player_feedback(
            self,
            review_id: int,
            feedback: str
    ) -> bool:
        """
        更新玩家反馈

        Args:
            review_id: 复盘记录ID
            feedback: 玩家反馈（有用/一般/无用）

        Returns:
            是否更新成功
        """
        record = self.db.query(ReviewHistory).filter(
            ReviewHistory.id == review_id
        ).first()

        if record:
            record.player_feedback = feedback
            self.db.commit()
            return True

        return False

    def get_review_stats(self):
        """
        获取复盘统计信息

        Returns:
            统计信息字典
        """
        total_reviews = self.db.query(ReviewHistory).count()

        # 胜负分布
        win_loss_dist = {}
        results = self.db.query(
            ReviewHistory.game_result,
            func.count(ReviewHistory.id)  # 【修复点 2】：去掉 self.db
        ).group_by(ReviewHistory.game_result).all()

        for result, count in results:
            win_loss_dist[result] = count

        # 游戏类型分布
        game_type_dist = {}
        results = self.db.query(
            ReviewHistory.game_type,
            func.count(ReviewHistory.id)  # 【修复点 3】：去掉 self.db
        ).group_by(ReviewHistory.game_type).all()

        for game_type, count in results:
            game_type_dist[game_type] = count

        return {
            "total_reviews": total_reviews,
            "win_loss_distribution": win_loss_dist,
            "game_type_distribution": game_type_dist
        }