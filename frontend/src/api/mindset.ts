/**
 * 心态管理API
 */

import { request } from './request'
import type { ApiResponse, MindsetTrend, PlayerProfile } from '../types'

/**
 * 获取心态记录
 */
export function getMindsetRecords(
  startDate?: string,
  endDate?: string,
  limit: number = 100
): Promise<ApiResponse<any>> {
  return request.get('/mindset/records', {
    params: {
      start_date: startDate,
      end_date: endDate,
      limit
    }
  })
}

/**
 * 获取心态日历
 */
export function getMindsetCalendar(
  year: number,
  month: number
): Promise<ApiResponse<any>> {
  return request.get(`/mindset/calendar/${year}/${month}`)
}

/**
 * 获取心态趋势
 */
export function getMindsetTrend(days: number = 30): Promise<ApiResponse<MindsetTrend[]>> {
  return request.get('/mindset/trend', {
    params: { days }
  })
}

/**
 * 获取赛前指导
 */
export function getPregameGuidance(): Promise<ApiResponse<any>> {
  return request.get('/mindset/pregame-guidance')
}

/**
 * 获取玩家画像
 */
export function getPlayerProfile(): Promise<ApiResponse<PlayerProfile>> {
  return request.get('/mindset/profile')
}
