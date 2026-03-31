"""
配置管理模块
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 腾讯云配置
    TENCENT_SECRET_ID: str = os.getenv("TENCENT_SECRET_ID", "")
    TENCENT_SECRET_KEY: str = os.getenv("TENCENT_SECRET_KEY", "")
    HUNYUAN_ENDPOINT: str = os.getenv("HUNYUAN_ENDPOINT", "hunyuan.tencentcloudapi.com")
    HUNYUAN_REGION: str = os.getenv("HUNYUAN_REGION", "ap-guangzhou")
    # 新增：腾讯元器智能体ID
    YUANQI_AGENT_ID: str = os.getenv("YUANQI_AGENT_ID", "")
    # 腾讯元器API配置
    YUANQI_API_KEY: str = os.getenv("YUANQI_API_KEY", "")
    YUANQI_ASSISTANT_ID: str = os.getenv("YUANQI_ASSISTANT_ID", "")
    YUANQI_API_BASE_URL: str = os.getenv("YUANQI_API_BASE_URL", "https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions")

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tactical_vision.db")

    # CORS配置
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

    # 应用配置
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # AI配置
    HUNYUAN_MODEL: str = os.getenv("HUNYUAN_MODEL", "hunyuan-standard")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    # 模拟模式（当API调用失败时使用模拟数据）
    SIMULATE_MODE: bool = os.getenv("SIMULATE_MODE", "false").lower() == "true"


settings = Settings()