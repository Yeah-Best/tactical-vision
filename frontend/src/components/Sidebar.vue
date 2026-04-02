<template>
  <aside class="fixed left-0 top-0 h-full w-64 bg-white border-r border-border shadow-lg">
    <!-- Logo和角色展示 -->
    <div class="p-6 border-b border-border">
      <div class="flex items-center space-x-4">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-gold-primary to-gold-light flex items-center justify-center animate-float shadow-lg">
          <span class="text-2xl font-bold text-white">李</span>
        </div>
        <div>
          <h1 class="text-xl font-bold text-text-primary">战术视界</h1>
          <p class="text-sm text-gold-primary">青莲剑仙</p>
        </div>
      </div>
      <p class="mt-4 text-sm text-text-secondary italic">
        "一篇诗，一斗酒，一曲长歌，一剑天涯。"
      </p>
    </div>

    <!-- 导航菜单 -->
    <nav class="p-4">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center space-x-3 p-4 rounded-xl mb-2 transition-all duration-300 group"
        :class="{
          'bg-gradient-to-r from-gold-primary to-gold-light text-white shadow-md': isActive(item.path),
          'text-text-primary hover:bg-bg-dark hover:text-gold-primary': !isActive(item.path)
        }"
      >
        <component
          :is="item.icon"
          class="w-5 h-5"
          :class="{ 'text-white': isActive(item.path), 'text-gold-primary': !isActive(item.path) }"
        />
        <span class="font-medium">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- 角色语录 -->
    <div class="absolute bottom-6 left-6 right-6">
      <div class="bg-bg-dark rounded-xl p-4 border border-border">
        <p class="text-sm italic" :style="{ color: chatStore.currentEmotion.color }">
          "{{ emotionQuote }}"
        </p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import {
  DataAnalysis as ReviewIcon,
  ChatLineRound as EmotionIcon,
  Calendar as MindsetIcon
} from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'

const route = useRoute()
const chatStore = useChatStore()

const menuItems = [
  {
    name: '对局复盘',
    path: '/review',
    icon: ReviewIcon
  },
  {
    name: '情绪疏导',
    path: '/emotion',
    icon: EmotionIcon
  },
  {
    name: '心态管理',
    path: '/mindset',
    icon: MindsetIcon
  }
]

const isActive = (path: string) => {
  return route.path === path
}

// 根据当前情绪等级和类型返回对应的李白话术
const emotionQuote = computed(() => {
  const { type, level } = chatStore.currentEmotion
  if (level >= 8) {
    // 情绪极差：烦躁/崩溃
    const quotes: Record<string, string> = {
      '烦躁': '怒气伤身，且将此剑入鞘，静候时机！',
      '绝望': '山穷水尽处，方见柳暗花明，莫要放弃！',
      '自责': '剑有钝时，人有失误，磨砺一番再出鞘！',
    }
    return quotes[type] ?? '逆风中，方显剑仙本色！'
  } else if (level >= 6) {
    // 情绪较差
    const quotes: Record<string, string> = {
      '委屈': '天公不作美，剑仙自有风骨，莫让人看轻了去！',
      '自责': '失误乃成长之阶，拂袖重来便是！',
      '绝望': '逆境方知英雄胆，挺住，曙光在前！',
    }
    return quotes[type] ?? '逆风中，方显剑仙本色！'
  } else if (level >= 4) {
    // 情绪波动
    const quotes: Record<string, string> = {
      '紧张': '深呼一口气，剑走偏锋方为上策！',
      '失落': '胜败乃兵家常事，今日休整，明日再战！',
    }
    return quotes[type] ?? '心有波澜，亦可乘风破浪！'
  } else if (level >= 2) {
    // 情绪良好
    return '心态平稳，正是出剑的好时机！'
  } else {
    // 情绪极佳：喜悦
    return '豪情万丈，今日定能所向披靡！'
  }
})
</script>

<style scoped>
</style>
