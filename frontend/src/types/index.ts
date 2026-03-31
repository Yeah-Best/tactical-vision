/**
 * TypeScript类型定义
 */

// 通用API响应
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 消息类型
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  emotion?: string
}

// 情绪记录
export interface EmotionRecord {
  id: number
  emotionType: string
  emotionLevel: number
  emotionReason?: string
  guidanceContent?: string
  createdAt: Date
}

// 对局复盘
export interface GameReview {
  id: number
  gameType: string
  gameResult: string
  kda?: string
  gameDescription: string
  reviewReport: string
  playerFeedback?: string
  createdAt: Date
}

// 玩家画像
export interface PlayerProfile {
  id: number
  favoriteHeroes: string[]
  commonMistakes: string[]
  winRate: number
  totalGames: number
  mindsetScore: number
  updatedAt: Date
}

// 心态日历
export interface CalendarDay {
  day: number
  emotionLevel: number
  emotionType: string
  color: string
}

// 心态趋势
export interface MindsetTrend {
  date: string
  emotionLevel: number
  recordCount: number
}
