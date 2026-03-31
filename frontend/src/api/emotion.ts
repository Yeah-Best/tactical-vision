/**
 * 情绪疏导API
 */

import { request, streamRequest } from './request'
import type { ApiResponse, EmotionRecord } from '../types'

/**
 * 分析情绪（流式）
 */
export async function* analyzeEmotion(data: {
  message: string
  emotionType: string
  emotionLevel: number
}) {
  const response = streamRequest('/emotion/analyze', {
    message: data.message,
    emotion_type: data.emotionType,
    emotion_level: data.emotionLevel
  })

  for await (const chunk of response) {
    yield chunk
  }
}

/**
 * 获取情绪历史
 */
export function getEmotionHistory(limit: number = 10): Promise<ApiResponse<EmotionRecord[]>> {
  return request.get('/emotion/history', {
    params: { limit }
  })
}

/**
 * 获取情绪统计
 */
export function getEmotionStats(): Promise<ApiResponse<any>> {
  return request.get('/emotion/stats')
}
