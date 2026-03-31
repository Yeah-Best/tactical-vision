/**
 * Vue Router配置
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/review'
  },
  {
    path: '/review',
    name: 'Review',
    component: () => import('../views/ReviewView.vue'),
    meta: {
      title: '对局复盘',
      icon: 'swords'
    }
  },
  {
    path: '/emotion',
    name: 'Emotion',
    component: () => import('../views/EmotionView.vue'),
    meta: {
      title: '情绪疏导',
      icon: 'heart'
    }
  },
  {
    path: '/mindset',
    name: 'Mindset',
    component: () => import('../views/MindsetView.vue'),
    meta: {
      title: '心态管理',
      icon: 'calendar'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title as string} - 战术视界`
  next()
})

export default router
