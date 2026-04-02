"""
TTS (Text-to-Speech) API 路由
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging
import io

from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

router = APIRouter()


class TTSRequest(BaseModel):
    """TTS 请求模型"""
    text: str = Field(..., description="要合成的文本", min_length=1, max_length=1000)
    emotion_type: str = Field(default="缓解", description="情绪类型")
    voice: Optional[str] = Field(default=None, description="语音名称")
    volume: float = Field(default=1.0, ge=0.0, le=2.0, description="音量调整系数")


class VoicesResponse(BaseModel):
    """可用语音列表响应"""
    voices: dict
    default: str


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """
    获取可用的语音列表

    Returns:
        语音列表和默认语音
    """
    try:
        from app.services.tts_service import AVAILABLE_VOICES

        return VoicesResponse(
            voices=AVAILABLE_VOICES,
            default=tts_service.default_voice
        )
    except Exception as e:
        logger.error(f"获取语音列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取语音列表失败")


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    将文本合成为语音流

    Args:
        request: TTS 请求对象

    Returns:
        音频流 (audio/mpeg)
    """
    try:
        logger.info(f"收到TTS请求: emotion_type={request.emotion_type}, text_length={len(request.text)}")

        # 生成音频
        audio_data = await tts_service.text_to_speech_with_emotion(
            text=request.text,
            emotion_type=request.emotion_type,
            voice=request.voice,
            volume_adjust=request.volume
        )

        logger.info(f"TTS合成成功: 音频大小={len(audio_data)} bytes")

        # 返回音频流
        return StreamingResponse(
            io=io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="speech_{request.emotion_type}.mp3"',
                "Content-Length": str(len(audio_data))
            }
        )

    except Exception as e:
        logger.error(f"语音合成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.get("/test")
async def test_tts():
    """
    测试 TTS 服务

    Returns:
        测试音频流
    """
    try:
        test_text = "你好，我是青莲剑仙，很高兴为您服务。这是语音测试。"
        audio_data = await tts_service.text_to_speech_with_emotion(
            text=test_text,
            emotion_type="喜悦",
            volume_adjust=0.9
        )

        return StreamingResponse(
            io=io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="test_speech.mp3"',
                "Content-Length": str(len(audio_data))
            }
        )

    except Exception as e:
        logger.error(f"TTS测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS测试失败: {str(e)}")
