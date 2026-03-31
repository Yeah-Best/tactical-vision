<template>
  <aside class="fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-ink-dark to-ink-darker border-r border-ink-darker shadow-2xl">
    <!-- Logo和角色展示 -->
    <div class="p-6 border-b border-ink-darker">
      <div class="flex items-center space-x-4">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-gold-primary to-gold-light flex items-center justify-center animate-float shadow-lg">
          <span class="text-2xl font-bold text-ink-dark">李</span>
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
          'bg-gradient-to-r from-gold-primary to-gold-light text-ink-dark shadow-lg': isActive(item.path),
          'text-text-primary hover:bg-ink-dark hover:text-gold-primary': !isActive(item.path)
        }"
      >
        <component
          :is="item.icon"
          class="w-5 h-5"
          :class="{ 'text-ink-dark': isActive(item.path), 'text-gold-primary': !isActive(item.path) }"
        />
        <span class="font-medium">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- 角色语录 -->
    <div class="absolute bottom-6 left-6 right-6">
      <div class="bg-gradient-to-r from-ink-darker to-ink-dark rounded-xl p-4 border border-ink-darker">
        <p class="text-sm text-text-secondary italic">
          "逆风中，方显剑仙本色！"
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

const route = useRoute()

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
</script>

<style scoped>
</style>
