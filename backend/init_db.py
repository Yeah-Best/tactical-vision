#!/usr/bin/env python3
"""
数据库初始化脚本
"""

from app.database import engine, Base
from app.models import MindsetRecord, ReviewHistory, PlayerProfile

def init_database():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")

if __name__ == "__main__":
    init_database()
