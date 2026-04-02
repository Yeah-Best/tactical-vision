# Edge-TTS 语音合成配置说明

## 功能概述

系统已集成 Edge-TTS（微软 Azure 神经语音），为情绪疏导功能提供高质量语音朗读服务。

## 使用的语音

当前默认使用 **zh-CN-YunxiNeural（云希）** 语音包：
- **特点**：游戏少年感最强的男声
- **适用场景**：非常适合"青莲剑仙"这个角色定位
- **知名度**：B站游戏解说和独立游戏的首选语音

## 情绪语调映射

后端会根据情绪类型自动调整语音参数：

| 情绪类型 | 语速 | 音调 | 音量 |
|---------|------|------|------|
| 烦躁 | -10% | -2Hz | -5% |
| 自责 | -5% | 0Hz | 0% |
| 绝望 | -15% | -1Hz | -5% |
| 委屈 | -5% | +1Hz | 0% |
| 紧张 | +5% | +2Hz | -5% |
| 喜悦 | +10% | +3Hz | +5% |
| 失落 | -5% | -2Hz | 0% |
| 缓解 | 0% | 0Hz | 0% |

## 安装步骤

### 1. 安装 Python 依赖

在 `backend` 目录下执行：

```bash
pip install edge-tts==6.1.9
```

或更新所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 重启后端服务

```bash
# 停止当前服务
# 重新启动
uvicorn app.main:create_app --reload
```

### 3. 验证安装

访问 `http://localhost:8000/docs` 查看 API 文档，应该能看到 `/api/tts` 相关接口。

## API 接口

### 获取语音列表

```http
GET /api/tts/voices
```

返回可用的语音包列表。

### 合成语音

```http
POST /api/tts/synthesize
Content-Type: application/json

{
  "text": "你好，我是青莲剑仙",
  "emotion_type": "喜悦",
  "voice": "zh-CN-YunxiNeural",
  "volume": 0.8
}
```

返回音频流（audio/mpeg 格式）。

### 测试语音

```http
GET /api/tts/test
```

返回测试音频流。

## 可用语音包

当前支持的语音包：

- `zh-CN-YunxiNeural` - 云希（默认，游戏少年感男声）
- `zh-CN-XiaoxiaoNeural` - 晓晓（温柔女声）
- `zh-CN-XiaoyiNeural` - 晓伊（清脆女声）
- `zh-CN-YunjianNeural` - 云健（成熟男声）
- `zh-CN-XiaoyanNeural` - 晓燕（沉稳女声）

## 注意事项

1. **首次使用**：首次合成语音时可能会有延迟，因为需要下载语音模型
2. **网络要求**：Edge-TTS 需要联网访问 Microsoft 服务器
3. **音频格式**：返回 MP3 格式音频
4. **文本限制**：单次请求文本最长 1000 字

## 故障排查

### 问题：听不到声音

1. 检查后端是否正常运行
2. 打开浏览器开发者工具查看网络请求
3. 确认 `/api/tts/synthesize` 请求是否成功
4. 检查浏览器控制台是否有错误信息

### 问题：语音质量差

- 确保网络连接良好
- 首次使用时等待语音模型下载完成
- 检查系统音量设置

### 问题：TTS API 错误

1. 确认 edge-tts 已正确安装：`pip list | grep edge-tts`
2. 查看后端日志了解详细错误信息
3. 尝试升级依赖：`pip install --upgrade edge-tts`

## 扩展其他语音

如需使用其他语音，修改 `backend/app/services/tts_service.py` 中的 `AVAILABLE_VOICES` 字典：

```python
AVAILABLE_VOICES = {
    'yunxi': 'zh-CN-YunxiNeural',
    'your_voice_name': 'en-US-YourVoiceNeural',  # 添加新语音
}
```

完整语音列表参考：[Microsoft TTS 语音文档](https://learn.microsoft.com/zh-CN/azure/cognitive-services/speech-service/language-support)
