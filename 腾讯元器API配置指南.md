# 腾讯元器API配置指南

## 当前状态

已成功完成以下迁移工作：
1. ✅ 删除所有模拟回复代码
2. ✅ 关闭模拟模式（SIMULATE_MODE=false）
3. ✅ 更新API客户端为腾讯元器接口
4. ✅ 修正HTTP请求头（X-source: openapi）
5. ✅ 使用Bearer Token认证方式

## 当前问题

API调用返回401未授权错误，原因是当前的API密钥无效或格式不正确。

当前配置：
- `YUANQI_API_KEY`: `这里填入你的腾讯元器API密钥`（需要从腾讯元器平台获取Bearer Token）
- `YUANQI_ASSISTANT_ID`: `这里填入你的腾讯元器智能体ID`（需要从腾讯元器平台获取）
- `YUANQI_API_BASE_URL`: `https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions`（正确）

## 解决方案

您需要从腾讯元器平台获取正确的Bearer Token（API Key）。

### 步骤1：获取腾讯元器API Token

1. 登录腾讯元器平台：https://yuanqi.tencent.com
2. 进入您的智能体管理页面
3. 查找"API接口"、"开发者设置"或"API密钥"相关选项
4. 申请或生成一个新的API Token（Bearer Token）
5. 复制生成的Token（通常是一串较长的随机字符串）

### 步骤2：更新配置文件

编辑 `backend/.env` 文件，将 `YUANQI_API_KEY` 替换为刚刚获取的Token：

```env
# 腾讯元器API配置
YUANQI_ASSISTANT_ID=这里填入你的腾讯元器智能体ID
YUANQI_API_KEY=这里填入你的腾讯元器API密钥
YUANQI_API_BASE_URL=https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions
SIMULATE_MODE=false
```

### 步骤3：测试API

更新配置后，重启后端服务：

```bash
cd backend
python main.py
```

或者使用我们提供的测试脚本：

```bash
cd backend
python -c "
import asyncio
from app.services.hunyuan_client import hunyuan_client

async def test():
    messages = [{'role': 'user', 'content': '你好'}]
    try:
        response = await hunyuan_client.chat_completions(messages)
        print(f'成功: {response[:100]}...')
    except Exception as e:
        print(f'失败: {e}')

asyncio.run(test())
"
```

## API接口详情

### 认证方式
- **类型**: Bearer Token
- **HTTP头**: 
  ```
  Authorization: Bearer <您的Token>
  Content-Type: application/json
  X-source: openapi
  ```

### 请求端点
```
POST https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions
```

### 请求体格式
```json
{
  "assistant_id": "您的智能体ID",
  "user_id": "用户标识（如default_user）",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": "用户消息内容"
    }
  ]
}
```

### 响应格式
```json
{
  "id": "请求ID",
  "choices": [
    {
      "message": {
        "content": "AI回复内容"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## 故障排除

### 1. 401未授权错误
- 确认API Token是否正确
- 确认Token是否为Bearer Token格式（不是SecretId/SecretKey）
- 确认智能体已发布并启用API访问

### 2. 404未找到错误
- 确认API端点URL是否正确
- 确认智能体ID是否正确

### 3. 超时错误
- 腾讯元器API响应超时为240秒
- 检查网络连接
- 减少请求内容长度

### 4. 其他错误
- 查看后端日志获取详细错误信息
- 检查腾讯元器平台状态

## 技术支持

- 腾讯元器官方文档：https://yuanqi.tencent.com/guide
- 腾讯云开发者社区：https://cloud.tencent.com/developer
- 项目GitHub仓库：[如有]

---

**重要提示**：获取正确的API Token后，系统将完全使用真实的腾讯元器AI服务，不再有任何模拟回复。