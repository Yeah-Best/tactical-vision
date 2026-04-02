"""
语音合成服务 - 使用 edge-tts
"""
import asyncio
import edge_tts
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 支持的语音列表
AVAILABLE_VOICES = {
    'yunxi': 'zh-CN-YunxiNeural',  # 云希 - 游戏少年感男声
    'xiaoxiao': 'zh-CN-XiaoxiaoNeural',  # 晓晓 - 温柔女声
    'xiaoyi': 'zh-CN-XiaoyiNeural',  # 晓伊 - 清脆女声
    'yunjian': 'zh-CN-YunjianNeural',  # 云健 - 成熟男声
    'xiaoyan': 'zh-CN-XiaoyanNeural',  # 晓燕 - 沉稳女声
}

class TTSService:
    """语音合成服务"""

    def __init__(self):
        self.default_voice = AVAILABLE_VOICES['yunxi']

    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> bytes:
        """
        将文本转换为语音

        Args:
            text: 要合成的文本
            voice: 语音名称，默认使用云希
            rate: 语速，例如 '+0%', '+10%', '-10%'
            pitch: 音调，例如 '+0Hz', '+2Hz', '-2Hz'
            volume: 音量，例如 '+0%', '+10%', '-10%'

        Returns:
            音频数据的字节流
        """
        try:
            # 使用指定的语音或默认语音
            voice_name = voice or self.default_voice
            logger.info(f"开始语音合成: 语音={voice_name}, 语速={rate}, 音调={pitch}")

            # 创建 edge-tts 通信对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_name,
                rate=rate,
                pitch=pitch,
                volume=volume
            )

            # 生成音频数据
            audio_data = b""
            chunk_count = 0
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                    chunk_count += 1

            if len(audio_data) == 0:
                raise RuntimeError("生成的音频数据为空，请检查网络连接")

            logger.info(f"语音合成完成，音频大小: {len(audio_data)} bytes, 块数量: {chunk_count}")
            return audio_data

        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}")
            raise

    def get_emotion_voice_params(self, emotion_type: str) -> dict:
        """
        根据情绪类型获取语音参数

        Args:
            emotion_type: 情绪类型

        Returns:
            包含 rate, pitch, volume 的字典
        """
        emotion_params = {
            '烦躁': {
                'rate': '-10%',  # 较慢语速
                'pitch': '-2Hz',  # 较低音调
                'volume': '-5%'
            },
            '自责': {
                'rate': '-5%',  # 稍慢
                'pitch': '0Hz',  # 正常音调
                'volume': '0%'
            },
            '绝望': {
                'rate': '-15%',  # 慢速
                'pitch': '-1Hz',  # 温和音调
                'volume': '-5%'
            },
            '委屈': {
                'rate': '-5%',  # 温和语速
                'pitch': '+1Hz',  # 稍高音调
                'volume': '0%'
            },
            '紧张': {
                'rate': '+5%',  # 稍快
                'pitch': '+2Hz',  # 较高音调
                'volume': '-5%'
            },
            '喜悦': {
                'rate': '+10%',  # 轻快语速
                'pitch': '+3Hz',  # 高音调
                'volume': '+5%'
            },
            '失落': {
                'rate': '-5%',  # 慢速安慰
                'pitch': '-2Hz',  # 低沉音调
                'volume': '0%'
            },
            '缓解': {
                'rate': '0%',  # 正常语速
                'pitch': '0Hz',  # 正常音调
                'volume': '0%'
            }
        }

        return emotion_params.get(emotion_type, emotion_params['缓解'])

    async def text_to_speech_with_emotion(
        self,
        text: str,
        emotion_type: str = '缓解',
        voice: Optional[str] = None,
        volume_adjust: float = 1.0
    ) -> bytes:
        """
        根据情绪合成语音

        Args:
            text: 要合成的文本
            emotion_type: 情绪类型
            voice: 语音名称
            volume_adjust: 音量调整系数 (0.0-1.5)

        Returns:
            音频数据的字节流
        """
        # 获取情绪参数
        params = self.get_emotion_voice_params(emotion_type)

        # 调整音量 - 确保总是有有效的音量参数
        if volume_adjust != 1.0:
            vol_percent = int((volume_adjust - 1.0) * 100)
            base_volume = int(params['volume'].replace('%', '').replace('+', '').replace('-', ''))
            total_volume = base_volume + vol_percent
            # 限制音量范围在 -50% 到 +50% 之间
            total_volume = max(-50, min(50, total_volume))
            params['volume'] = f"{total_volume:+d}%"

        return await self.text_to_speech(
            text=text,
            voice=voice,
            rate=params['rate'],
            pitch=params['pitch'],
            volume=params['volume']
        )


# 全局 TTS 服务实例
tts_service = TTSService()
