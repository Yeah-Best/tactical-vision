/**
 * 用户状态管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserProfile {
  id: string
  username: string
  nickname: string
  avatar?: string
  level: number
  gameRank?: string
  totalGames: number
  winRate: number
  joinDate: string
}

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const user = ref<UserProfile>({
    id: '1',
    username: 'player001',
    nickname: '李白的小迷弟',
    avatar: undefined,
    level: 15,
    gameRank: '荣耀王者',
    totalGames: 258,
    winRate: 68.5,
    joinDate: '2024-01-15'
  })

  // 是否已登录
  const isLoggedIn = ref(true)

  // 更新用户信息
  const updateUser = (profile: Partial<UserProfile>) => {
    user.value = { ...user.value, ...profile }
  }

  // 登录
  const login = (profile: UserProfile) => {
    user.value = profile
    isLoggedIn.value = true
    // 保存到 localStorage
    localStorage.setItem('user', JSON.stringify(profile))
  }

  // 登出
  const logout = () => {
    user.value = {
      id: '1',
      username: 'player001',
      nickname: '李白的小迷弟',
      avatar: undefined,
      level: 15,
      gameRank: '荣耀王者',
      totalGames: 258,
      winRate: 68.5,
      joinDate: '2024-01-15'
    }
    isLoggedIn.value = true
    localStorage.removeItem('user')
  }

  // 从本地存储加载用户信息
  const loadUserFromStorage = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
        isLoggedIn.value = true
      } catch (e) {
        console.error('Failed to parse user from storage:', e)
      }
    }
  }

  // 初始化时加载用户信息
  loadUserFromStorage()

  return {
    user,
    isLoggedIn,
    updateUser,
    login,
    logout
  }
})
