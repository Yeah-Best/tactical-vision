"""
心态管理服务逻辑
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import MindsetRecord, PlayerProfile
from app.utils.helpers import calculate_mindset_trend, get_emotion_label, get_emotion_color


class MindsetService:
    """心态管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_mindset_records(
            self,
            start_date: datetime = None,
            end_date: datetime = None,
            limit: int = 100
    ) -> List[MindsetRecord]:
        """获取心态记录"""
        query = self.db.query(MindsetRecord)

        if start_date:
            query = query.filter(MindsetRecord.created_at >= start_date)
        if end_date:
            query = query.filter(MindsetRecord.created_at <= end_date)

        return query.order_by(MindsetRecord.created_at.desc()).limit(limit).all()

    def get_mindset_calendar(
            self,
            year: int,
            month: int
    ) -> Dict[str, Any]:
        """获取心态日历数据"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # 按时间正序查询，这样同一天如果有多条记录，最后会保留当天的最后一次状态（覆盖）
        records = self.db.query(MindsetRecord).filter(
            MindsetRecord.created_at >= start_date,
            MindsetRecord.created_at < end_date
        ).order_by(MindsetRecord.created_at.asc()).all()

        calendar_data = {}
        for record in records:
            day = record.created_at.day
            # 【优化点】：因为按正序遍历，同一天的后续记录会覆盖前面的，保留当天最终心态
            calendar_data[day] = {
                "emotion_level": record.emotion_level,
                "emotion_type": record.emotion_type,
                "color": get_emotion_color(record.emotion_level)
            }

        return calendar_data

    def get_mindset_trend(
            self,
            days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取心态趋势数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 按天聚合数据
        daily_stats = self.db.query(
            func.date(MindsetRecord.created_at).label('date'),
            func.avg(MindsetRecord.emotion_level).label('avg_emotion'),
            func.count(MindsetRecord.id).label('record_count')
        ).filter(
            MindsetRecord.created_at >= start_date,
            MindsetRecord.created_at <= end_date
        ).group_by(
            func.date(MindsetRecord.created_at)
        ).all()

        trend_data = []
        for stat in daily_stats:
            trend_data.append({
                "date": stat.date,
                "emotion_level": round(stat.avg_emotion, 2),
                "record_count": stat.record_count
            })

        return sorted(trend_data, key=lambda x: x["date"])

    def generate_pregame_guidance(self) -> str:
        """生成赛前心态预热指导"""
        # 获取最近的心态记录
        recent_records = self.db.query(MindsetRecord).order_by(
            MindsetRecord.created_at.desc()
        ).limit(5).all()

        # 【修改点】：全面替换为教练人设
        if not recent_records:
            return """
            【战术视界】专属教练赛前寄语：

            "别紧张，把排位当成一次普通的训练赛。"

            召唤师，新的对局即将开始！保持平常心，深呼吸。
            记住我们的核心战术：稳住发育，观察小地图，不打无准备的团战。

            今日战术板：专注当下，相信操作，准备享受比赛！
            """

        # 分析近期心态状态
        avg_emotion = sum(r.emotion_level for r in recent_records) / len(recent_records)

        if avg_emotion >= 7:
            status = "我看你最近心态有些起伏，可能是遇到了连败或者坑货队友。但这都是上分路上的正常波动。"
            advice = "今天开局前，先深呼吸三次。屏蔽掉外界干扰，只要你自己不乱，这局就稳了一半！"
        elif avg_emotion >= 4:
            status = "近期你的心态整体控制得不错，这是高分段玩家必备的素质。"
            advice = "保持这份从容，把注意力集中在自己的兵线和野区上，按部就班地拿下优势！"
        else:
            status = "近期你的心态非常棒，连胜的火热手感还在！"
            advice = "趁着状态好，带着队友一起飞！用你的节奏去接管整场比赛吧！"

        return f"""
        【战术视界】专属教练赛前寄语：

        {status}

        "比赛总有起伏，咱们调整好了肯定能赢！"

        {advice}

        上分三大铁律：
        1. 逆风不投降，顺风不浪战。
        2. 劣势局多带线发育，少接无意义的团战。
        3. 享受对抗的过程，每一局都在提升你的游戏理解。

        准备好了吗？点击匹配，拿下这局！
        """

    def get_player_profile(self) -> PlayerProfile:
        """获取玩家画像"""
        profile = self.db.query(PlayerProfile).first()

        if not profile:
            # 创建默认画像
            profile = PlayerProfile(
                favorite_heroes=[],
                common_mistakes=[],
                win_rate=0,
                total_games=0,
                mindset_score=50.0
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        return profile

    def update_player_profile(
            self,
            favorite_heroes: List[str] = None,
            common_mistakes: List[str] = None,
            win_rate: float = None,
            total_games: int = None
    ) -> PlayerProfile:
        """更新玩家画像"""
        profile = self.get_player_profile()

        if favorite_heroes is not None:
            profile.favorite_heroes = favorite_heroes
        if common_mistakes is not None:
            profile.common_mistakes = common_mistakes
        if win_rate is not None:
            profile.win_rate = win_rate
        if total_games is not None:
            profile.total_games = total_games

        # 计算心态分数（基于最近30天的记录）
        recent_records = self.get_mindset_records(
            start_date=datetime.now() - timedelta(days=30),
            limit=1000
        )

        if recent_records:
            avg_emotion = sum(r.emotion_level for r in recent_records) / len(recent_records)
            profile.mindset_score = (10 - avg_emotion) * 10  # 转换为0-100分

        self.db.commit()
        self.db.refresh(profile)

        return profile