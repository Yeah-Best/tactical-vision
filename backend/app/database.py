"""
数据库配置模块
"""

from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 【新增】：当连接建立时，开启 SQLite 的并发高能模式 WAL
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")       # 开启 WAL 模式
        cursor.execute("PRAGMA synchronous=NORMAL")     # 降低同步级别，提速
        cursor.execute("PRAGMA busy_timeout=5000")      # 遇到锁时等待5秒而不是直接报错
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_database_schema():
    """确保数据库表和新增字段已就绪。"""
    from app.models import MindsetRecord, PlayerProfile, ReviewHistory

    _ = (MindsetRecord, PlayerProfile, ReviewHistory)
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "review_history" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("review_history")}
    alter_statements = []

    if "game_version" not in existing_columns:
        alter_statements.append("ALTER TABLE review_history ADD COLUMN game_version VARCHAR(50)")
    if "team_composition" not in existing_columns:
        alter_statements.append("ALTER TABLE review_history ADD COLUMN team_composition JSON")
    if "enemy_composition" not in existing_columns:
        alter_statements.append("ALTER TABLE review_history ADD COLUMN enemy_composition JSON")

    if not alter_statements:
        return

    with engine.begin() as connection:
        for statement in alter_statements:
            connection.execute(text(statement))


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

