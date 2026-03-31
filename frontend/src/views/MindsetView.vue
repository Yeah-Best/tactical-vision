<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div class="text-center space-y-2">
      <h1 class="text-4xl font-bold text-text-primary">心态管理</h1>
      <p class="text-text-secondary">记录成长轨迹，培养坚韧心态</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- 左侧：心态日历 -->
      <div class="lg:col-span-2 card space-y-6">
        <h2 class="text-2xl font-semibold text-gold-primary flex items-center">
          <el-icon class="mr-2"><Calendar /></el-icon>
          心态日历
        </h2>
        
        <!-- 日历头部 -->
        <div class="flex justify-between items-center mb-4">
          <el-button @click="changeMonth(-1)" class="btn-secondary">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <h3 class="text-xl font-semibold text-text-primary">
            {{ currentYear }}年{{ currentMonth }}月
          </h3>
          <el-button @click="changeMonth(1)" class="btn-secondary">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <!-- 星期标题 -->
        <div class="grid grid-cols-7 gap-2 mb-2">
          <div 
            v-for="day in weekDays"
            :key="day"
            class="text-center text-sm font-medium text-text-secondary py-2"
          >
            {{ day }}
          </div>
        </div>
        
        <!-- 日历网格 -->
        <div class="grid grid-cols-7 gap-2">
          <!-- 空白填充 -->
          <div
            v-for="n in firstDayOfMonth"
            :key="`empty-${n}`"
            class="aspect-square"
          />
          
          <!-- 日期 -->
          <div
            v-for="day in daysInMonth"
            :key="day"
            class="aspect-square flex flex-col items-center justify-center rounded-lg border transition-all duration-300 cursor-pointer"
            :class="{
              'border-ink-darker bg-bg-dark hover:border-gold-primary': !isToday(day),
              'border-gold-primary bg-gold-primary/20': isToday(day)
            }"
            @click="selectDate(day)"
          >
            <span 
              class="text-sm font-medium"
              :class="isToday(day) ? 'text-gold-primary' : 'text-text-primary'"
            >
              {{ day }}
            </span>
            <div 
              v-if="calendarData[day]"
              class="w-2 h-2 rounded-full mt-1"
              :style="{ backgroundColor: calendarData[day].color }"
            />
          </div>
        </div>
        
        <!-- 图例 -->
        <div class="flex justify-center space-x-6 mt-4 text-sm">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span class="text-text-secondary">心态良好</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span class="text-text-secondary">略有波动</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-red-500"></div>
            <span class="text-text-secondary">情绪低落</span>
          </div>
        </div>
      </div>

      <!-- 右侧：赛前预热 -->
      <div class="space-y-6">
        <div class="card space-y-4">
          <h2 class="text-2xl font-semibold text-gold-primary flex items-center">
            <el-icon class="mr-2"><MagicStick /></el-icon>
            赛前预热
          </h2>
          
          <div class="bg-gradient-to-br from-ink-darker to-ink-dark rounded-xl p-6 border border-ink-darker">
            <div class="text-center mb-4">
              <el-icon class="text-4xl text-gold-primary mb-2"><Opportunity /></el-icon>
              <h3 class="text-lg font-semibold text-text-primary">今日心法</h3>
            </div>
            
            <div 
              class="text-sm text-text-secondary leading-relaxed whitespace-pre-line"
              v-if="pregameGuidance"
            >
              {{ pregameGuidance }}
            </div>
            
            <el-button
              v-else
              @click="loadPregameGuidance"
              :loading="loadingPregame"
              class="w-full btn-primary"
            >
              生成赛前指导
            </el-button>
          </div>
        </div>

        <!-- 心态统计 -->
        <div class="card space-y-4">
          <h2 class="text-xl font-semibold text-gold-primary flex items-center">
            <el-icon class="mr-2"><TrendCharts /></el-icon>
            本月统计
          </h2>
          
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-ink-dark rounded-lg p-4 text-center border border-ink-darker">
              <div class="text-2xl font-bold text-text-primary">
                {{ mindsetStore.records.length }}
              </div>
              <div class="text-xs text-text-secondary">疏导次数</div>
            </div>
            <div class="bg-ink-dark rounded-lg p-4 text-center border border-ink-darker">
              <div class="text-2xl font-bold text-gold-primary">
                {{ averageMindset }}
              </div>
              <div class="text-xs text-text-secondary">平均心态</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 成长笔记 -->
    <div class="card" v-if="mindsetStore.records.length > 0">
      <h2 class="text-2xl font-semibold text-gold-primary mb-6 flex items-center">
        <el-icon class="mr-2"><Notebook /></el-icon>
        成长笔记
      </h2>
      
      <div class="space-y-4">
        <div
          v-for="record in mindsetStore.records.slice(0, 5)"
          :key="record.id"
          class="bg-ink-dark rounded-xl p-4 border-l-4 transition-all duration-300"
          :style="{ borderLeftColor: getEmotionColor(record.emotionLevel) }"
        >
          <div class="flex justify-between items-start mb-2">
            <div class="flex items-center space-x-3">
              <span 
                class="inline-block px-3 py-1 rounded-full text-sm font-medium"
                :style="{
                  backgroundColor: getEmotionColor(record.emotionLevel) + '20',
                  color: getEmotionColor(record.emotionLevel)
                }"
              >
                {{ record.emotionType }}
              </span>
              <span class="text-xs text-text-secondary">
                {{ formatDate(record.createdAt) }}
              </span>
            </div>
            <div class="text-xs text-text-secondary">
              心态指数: {{ record.emotionLevel }}/10
            </div>
          </div>
          <p class="text-sm text-text-secondary mb-2">
            {{ record.emotionReason }}
          </p>
          <div class="text-sm text-text-primary leading-relaxed">
            <strong class="text-gold-primary">疏导记录：</strong>
            {{ record.guidanceContent?.slice(0, 100) }}...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Calendar,
  MagicStick,
  Opportunity,
  TrendCharts,
  Notebook,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import { useMindsetStore } from '../stores/mindset'
import { getMindsetCalendar, getPregameGuidance } from '../api/mindset'

const mindsetStore = useMindsetStore()

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const pregameGuidance = ref('')
const loadingPregame = ref(false)

const calendarData = computed(() => mindsetStore.calendarData)

// 计算本月天数
const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 0).getDate()
})

// 计算本月第一天是星期几
const firstDayOfMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value - 1, 1).getDay()
})

// 判断是否是今天
const isToday = (day: number): boolean => {
  const today = new Date()
  return (
    day === today.getDate() &&
    currentMonth.value === today.getMonth() + 1 &&
    currentYear.value === today.getFullYear()
  )
}

// 切换月份
const changeMonth = (delta: number) => {
  currentMonth.value += delta
  if (currentMonth.value > 12) {
    currentMonth.value = 1
    currentYear.value++
  } else if (currentMonth.value < 1) {
    currentMonth.value = 12
    currentYear.value--
  }
  loadCalendarData()
}

// 选择日期
const selectDate = (day: number) => {
  mindsetStore.setSelectedDate(new Date(currentYear.value, currentMonth.value - 1, day))
}

// 加载日历数据
const loadCalendarData = async () => {
  try {
    const response = await getMindsetCalendar(currentYear.value, currentMonth.value)
    if (response.success) {
      mindsetStore.setCalendarData(response.data || {})
    }
  } catch (error) {
    console.error('加载日历数据失败:', error)
  }
}

// 加载赛前指导
const loadPregameGuidance = async () => {
  loadingPregame.value = true
  try {
    const response = await getPregameGuidance()
    if (response.success) {
      pregameGuidance.value = response.data?.guidance || ''
    }
  } catch (error) {
    console.error('加载赛前指导失败:', error)
  } finally {
    loadingPregame.value = false
  }
}

// 计算平均心态
const averageMindset = computed(() => {
  if (mindsetStore.records.length === 0) return '0.0'
  const sum = mindsetStore.records.reduce((acc, record) => acc + record.emotionLevel, 0)
  return (sum / mindsetStore.records.length).toFixed(1)
})

// 获取情绪颜色
const getEmotionColor = (level: number): string => {
  if (level >= 8) return '#DA3633'
  if (level >= 6) return '#D29922'
  if (level >= 4) return '#388BFD'
  return '#2EA043'
}

// 格式化日期
const formatDate = (date: string | Date) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  loadCalendarData()
})
</script>

<style scoped>
</style>
