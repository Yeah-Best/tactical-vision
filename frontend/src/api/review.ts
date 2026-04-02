/**
 * 对局复盘API
 */

import { request, streamRequest } from './request'
import type { ApiResponse, GameReview, GameReviewAnalyzePayload } from '../types'


/**
 * 分析对局（流式）
 */
export async function* analyzeGame(data: GameReviewAnalyzePayload) {
  const response = streamRequest('/review/analyze', {
    game_type: data.gameType,
    game_result: data.gameResult,
    kda: data.kda,
    game_description: data.gameDescription,
    game_version: data.gameVersion,
    team_composition: data.teamComposition,
    enemy_composition: data.enemyComposition
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

/**
 * 获取支持的游戏列表
 */
export function getSupportedGames(): Promise<ApiResponse<any[]>> {
  return request.get('/review/games/supported')
}

/**
 * 刷新游戏知识库
 */
export function refreshKnowledge(gameType: string = '王者荣耀'): Promise<ApiResponse<any>> {
  return request.post('/review/knowledge/refresh', null, {
    params: { game_type: gameType }
  })
}
