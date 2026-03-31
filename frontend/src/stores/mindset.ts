/**
 * 心态管理状态管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { EmotionRecord, MindsetTrend, PlayerProfile, CalendarDay } from '../types'

export const useMindsetStore = defineStore('mindset', () => {
  // 心态记录列表
  const records = ref<EmotionRecord[]>([])

  // 心态趋势数据
  const trends = ref<MindsetTrend[]>([])

  // 玩家画像
  const profile = ref<PlayerProfile | null>(null)

  // 日历数据
  const calendarData = ref<Record<number, CalendarDay>>({})

  // 当前选中的日期
  const selectedDate = ref<Date>(new Date())

  // 加载状态
  const loading = ref(false)

  // 设置心态记录
  const setRecords = (data: EmotionRecord[]) => {
    records.value = data
  }

  // 添加心态记录
  const addRecord = (record: EmotionRecord) => {
    records.value.unshift(record)
  }

  // 设置趋势数据
  const setTrends = (data: MindsetTrend[]) => {
    trends.value = data
  }

  // 设置玩家画像
  const setProfile = (data: PlayerProfile) => {
    profile.value = data
  }

  // 设置日历数据
  const setCalendarData = (data: Record<number, CalendarDay>) => {
    calendarData.value = data
  }

  // 设置选中的日期
  const setSelectedDate = (date: Date) => {
    selectedDate.value = date
  }

  // 清空数据
  const clearData = () => {
    records.value = []
    trends.value = []
    profile.value = null
    calendarData.value = {}
  }

  return {
    records,
    trends,
    profile,
    calendarData,
    selectedDate,
    loading,
    setRecords,
    addRecord,
    setTrends,
    setProfile,
    setCalendarData,
    setSelectedDate,
    clearData
  }
})
