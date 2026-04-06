"""
腾讯混元大模型客户端封装
支持流式和非流式ChatCompletions接口调用 (基于 httpx 全异步实现)
"""

import asyncio
import json
import logging
import httpx
from typing import List, Dict, Any, AsyncGenerator
from ..config import settings

logger = logging.getLogger(__name__)


class HunyuanClient:
    """混元大模型客户端"""

    def __init__(self):
        # 腾讯元器API配置
        self.api_key = settings.YUANQI_API_KEY or settings.TENCENT_SECRET_ID
        self.assistant_id = settings.YUANQI_ASSISTANT_ID or settings.YUANQI_AGENT_ID
        self.base_url = settings.YUANQI_API_BASE_URL
        
        # 请求头
        self.headers = {
            "X-source": "openapi",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 兼容旧配置
        self.model = settings.HUNYUAN_MODEL

    async def chat_completions(
            self,
            messages: List[Dict[str, str]],
            stream: bool = False,
            temperature: float = 0.7
    ) -> str:
        """
        调用腾讯元器智能体ChatCompletions接口 (完全异步)
        """
        # 【容灾机制】判断是否处于模拟模式，断网演示必用
        if getattr(settings, 'SIMULATE_MODE', False):
            logger.info("模拟模式已开启，返回非流式模拟数据。")
            await asyncio.sleep(1) # 模拟网络延迟
            return "【模拟模式运行中】这是一段预设的复盘分析/对话回复。当前系统与外部大模型的网络通信已隔离，以保障比赛演示稳定。"

        try:
            # 检查必要的配置
            if not self.assistant_id:
                raise ValueError("未配置腾讯元器助手ID (YUANQI_ASSISTANT_ID)")
            if not self.api_key:
                raise ValueError("未配置腾讯元器API密钥 (YUANQI_API_KEY 或 TENCENT_SECRET_ID)")
            
            # 构建请求负载
            formatted_messages = []
            for msg in messages:
                # 去掉 system 角色
                role = msg.get("role", "user")
                if role == "system":
                    continue 
                    
                content = msg.get("content", "")
                
                # 腾讯元器 Agent API 要求 content 必须是带有 type 的对象数组
                formatted_messages.append({
                    "role": role,
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                })
            
            payload = {
                "assistant_id": self.assistant_id,
                "user_id": "default_user",
                "stream": stream,
                "messages": formatted_messages
            }
            
            if stream:
                raise ValueError("流式输出请使用 chat_completions_stream 方法")
            
            # 发送完全异步的 HTTP 请求
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            # 解析响应
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    msg_content = choice["message"]["content"]
                    # 兼容元器返回的 content 可能是数组的情况
                    if isinstance(msg_content, list) and len(msg_content) > 0:
                        return msg_content[0].get("text", "")
                    return msg_content
                elif "content" in choice:
                    return choice["content"]
            
            if "data" in result and "content" in result["data"]:
                return result["data"]["content"]
            
            logger.error(f"腾讯元器API返回异常响应: {json.dumps(result, ensure_ascii=False)}")
            return "抱歉，青莲剑仙暂时无法回应，请稍后再试。"
            
        except httpx.RequestError as e:
            logger.error(f"腾讯元器API网络请求失败: {str(e)}")
            return "抱歉，AI服务暂时无法访问，请检查网络后再试。"
        except httpx.HTTPStatusError as e:
            logger.error(f"腾讯元器API返回错误状态码: {e.response.status_code}")
            return f"抱歉，服务提供商返回错误 ({e.response.status_code})。"
        except ValueError as e:
            logger.error(f"配置错误: {str(e)}")
            return f"配置错误: {str(e)}"
        except Exception as e:
            logger.error(f"调用腾讯元器API时发生未知错误: {str(e)}")
            return f"抱歉，发生了未知错误: {str(e)}"

    async def chat_completions_stream(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        流式调用腾讯元器智能体ChatCompletions接口 (完全异步)
        """
        # 【容灾机制】模拟模式下的流式输出
        if getattr(settings, 'SIMULATE_MODE', False):
            logger.info("模拟模式已开启，开始流式模拟输出。")
            simulated_chunks = [
                "【模拟模式】",
                "系统检测到目前处于网络隔离的比赛演示模式。",
                "您的请求已被接收。",
                "\n\n分析结论：\n",
                "这是一段系统预设好的安全流式数据，",
                "完美避开了网络延迟和阻塞风险，",
                "确保比赛过程万无一失。"
            ]
            for chunk in simulated_chunks:
                await asyncio.sleep(0.4) # 模拟打字机效果的延迟
                yield chunk
            return

        try:
            # 检查必要的配置
            if not self.assistant_id:
                raise ValueError("未配置腾讯元器助手ID (YUANQI_ASSISTANT_ID)")
            if not self.api_key:
                raise ValueError("未配置腾讯元器API密钥 (YUANQI_API_KEY 或 TENCENT_SECRET_ID)")
            
            # 构建请求负载
            formatted_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                if role == "system":
                    continue # 忽略 system 角色
                    
                content = msg.get("content", "")
                
                formatted_messages.append({
                    "role": role,
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                })
            
            payload = {
                "assistant_id": self.assistant_id,
                "user_id": "default_user", 
                "stream": True,
                "messages": formatted_messages
            }
            
            # 发送异步流式 HTTP 请求
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    # 使用 httpx 的 aiter_lines() 异步按行读取流数据
                    async for line in response.aiter_lines():
                        if line:
                            line_str = line.strip()
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  
                                if data_str == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        choice = data["choices"][0]
                                        if "delta" in choice and "content" in choice["delta"]:
                                            delta_content = choice["delta"]["content"]
                                            # 流式返回的也可能是数组结构，做安全解析
                                            if isinstance(delta_content, list) and len(delta_content) > 0:
                                                yield delta_content[0].get("text", "")
                                            else:
                                                yield delta_content
                                        elif "message" in choice and "content" in choice["message"]:
                                            msg_content = choice["message"]["content"]
                                            if isinstance(msg_content, list) and len(msg_content) > 0:
                                                yield msg_content[0].get("text", "")
                                            else:
                                                yield msg_content
                                        elif "content" in choice:
                                            yield choice["content"]
                                    elif "data" in data and "content" in data["data"]:
                                        yield data["data"]["content"]
                                except json.JSONDecodeError:
                                    continue
                                except KeyError:
                                    continue
            
        except httpx.RequestError as e:
            logger.error(f"腾讯元器流式API网络异常: {str(e)}")
            yield "抱歉，网络连接暂时中断，请稍后再试。"
        except httpx.HTTPStatusError as e:
            logger.error(f"腾讯元器流式API状态码错误: {e.response.status_code}")
            yield f"抱歉，服务暂时不可用 (错误码: {e.response.status_code})。"
        except ValueError as e:
            logger.error(f"配置错误: {str(e)}")
            yield f"配置错误: {str(e)}"
        except Exception as e:
            logger.error(f"调用腾讯元器流式API时发生未知错误: {str(e)}")
            yield f"抱歉，发生了未知错误: {str(e)}"

    async def analyze_emotion(
            self,
            user_message: str,
            emotion_type: str = "失落",
            emotion_level: int = 5
    ) -> AsyncGenerator[str, None]:
        """
        情绪分析并生成疏导内容（流式）
        直接将用户原话传递给腾讯元器，不添加任何系统提示或模板
        """
        messages = [
            {
                "role": "user",
                "content": user_message
            }
        ]

        async for chunk in self.chat_completions_stream(messages, temperature=0.8):
            yield chunk

    async def analyze_game_review(
            self,
            game_data: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        对局复盘分析（流式）
        将版本知识库检索结果作为上下文注入到元器提示词中。
        """
        game_type = game_data.get('game_type', '')
        game_result = game_data.get('game_result', '')
        kda = game_data.get('kda', '')
        game_description = game_data.get('game_description', '')
        game_version = game_data.get('game_version') or settings.GAME_DEFAULT_VERSION_LABEL
        team_composition = '、'.join(game_data.get('team_composition', []) or []) or '未提供'
        enemy_composition = '、'.join(game_data.get('enemy_composition', []) or []) or '未提供'
        detected_champions = '、'.join(game_data.get('detected_champions', []) or []) or '未识别'
        rag_context = game_data.get('rag_context', '当前知识库暂无可用版本情报。')

        prompt = f"""
你是《战术视界》的电竞复盘分析助手，需要结合当前版本知识库输出专业、可信、可执行的复盘建议。

请严格遵守以下要求：
1. 开头必须明确写出“基于当前 {game_version} 版本更新与统计情报...”。
2. 必须优先引用我提供的【当前版本情报上下文】来判断阵容强势点、弱势点、克制关系与版本倾向。
3. 如果知识库没有直接命中某个英雄或关系，要明确说“当前版本知识库暂无直接命中”，不要编造。
4. 回复结构尽量包含：版本判断、阵容强弱势、关键失误复盘、下一把优化建议。
5. 语言保持专业、简洁，适当保留项目的李白风格，但不要过度文绉绉。

【当前版本情报上下文】
{rag_context}

【玩家对局信息】
- 游戏类型：{game_type}
- 对局结果：{game_result}
- KDA：{kda or '未提供'}
- 我方阵容：{team_composition}
- 敌方阵容：{enemy_composition}
- 从描述中识别到的英雄：{detected_champions}
- 对局描述：{game_description}

请基于以上信息直接开始复盘。
""".strip()

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        async for chunk in self.chat_completions_stream(messages, temperature=0.6):
            yield chunk


# 全局客户端实例
hunyuan_client = HunyuanClient()