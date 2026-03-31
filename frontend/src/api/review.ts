/**
 * 对局复盘API
 */

import { request, streamRequest } from './request'
import type { ApiResponse, GameReview } from '../types'

/**
 * 分析对局（流式）
 */
export async function* analyzeGame(data: {
  gameType: string
  gameResult: string
  kda?: string
  gameDescription: string
}) {
  const response = streamRequest('/review/analyze', {
    game_type: data.gameType,
    game_result: data.gameResult,
    kda: data.kda,
    game_description: data.gameDescription
  })

  for await (const chunk of response) {
    yield chunk
  }
}

/**
 * 获取复盘历史
 */
export function getReviewHistory(limit: number = 20): Promise<ApiResponse<GameReview[]>> {
  return request.get('/review/history', {
    params: { limit }
  })
}

/**
 * 获取复盘统计
 */
export function getReviewStats(): Promise<ApiResponse<any>> {
  return request.get('/review/stats')
}

/**
 * 更新玩家反馈
 */
export function updatePlayerFeedback(
  reviewId: number,
  feedback: string
): Promise<ApiResponse<any>> {
  return request.post(`/review/${reviewId}/feedback`, {
    feedback
  })
}
