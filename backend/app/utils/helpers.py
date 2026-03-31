"""
工具函数模块
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_emotion_label(level: int) -> str:
    """根据情绪级别获取标签"""
    if level >= 8:
        return "心态崩盘"
    elif level >= 6:
        return "情绪低落"
    elif level >= 4:
        return "略有波动"
    elif level >= 2:
        return "状态良好"
    else:
        return "热血沸腾"


def get_emotion_color(level: int) -> str:
    """根据情绪级别获取颜色"""
    if level >= 8:
        return "#DA3633"  # 红色
    elif level >= 6:
        return "#D29922"  # 黄色
    elif level >= 4:
        return "#388BFD"  # 蓝色
    else:
        return "#2EA043"  # 绿色


def calculate_mindset_trend(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算心态趋势"""
    if not records:
        return {"trend": "stable", "change": 0}

    # 按时间排序
    sorted_records = sorted(records, key=lambda x: x['created_at'])

    # 计算最近7天的平均情绪级别
    recent_avg = sum(r['emotion_level'] for r in sorted_records[-7:]) / min(7, len(sorted_records))
    # 计算之前7天的平均情绪级别
    previous_avg = sum(r['emotion_level'] for r in sorted_records[-14:-7]) / max(1, min(7, len(sorted_records) - 7))

    change = recent_avg - previous_avg

    if change > 1:
        return {"trend": "improving", "change": change}
    elif change < -1:
        return {"trend": "declining", "change": change}
    else:
        return {"trend": "stable", "change": change}

# 缺失的响应模型类
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MindsetRecordResponse(BaseModel):
    id: int
    content: str
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        orm_mode = True