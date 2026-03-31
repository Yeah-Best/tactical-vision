/**
 * 对话状态管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '../types'

export const useChatStore = defineStore('chat', () => {
  // 消息列表
  const messages = ref<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '青莲剑仙李白在此，有何烦恼不妨说来听听？',
      timestamp: new Date()
    }
  ])

  // 是否正在生成回复
  const isGenerating = ref(false)

  // 当前情绪状态
  const currentEmotion = ref({
    type: '平静',
    level: 3,
    color: '#2EA043'
  })

  // 添加用户消息
  const addUserMessage = (content: string) => {
    const message: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date()
    }
    messages.value.push(message)
    return message
  }

  // 添加AI消息
  const addAIMessage = (content: string) => {
    const message: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: 'assistant',
      content,
      timestamp: new Date()
    }
    messages.value.push(message)
    return message
  }

  // 流式更新AI消息
  const updateAIMessageStream = (messageId: string, chunk: string) => {
    const message = messages.value.find(m => m.id === messageId)
    if (message) {
      message.content += chunk
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = [
      {
        id: 'welcome',
        role: 'assistant',
        content: '青莲剑仙李白在此，有何烦恼不妨说来听听？',
        timestamp: new Date()
      }
    ]
  }

  // 设置情绪状态
  const setEmotion = (type: string, level: number, color: string) => {
    currentEmotion.value = { type, level, color }
  }

  return {
    messages,
    isGenerating,
    currentEmotion,
    addUserMessage,
    addAIMessage,
    updateAIMessageStream,
    clearMessages,
    setEmotion
  }
})
