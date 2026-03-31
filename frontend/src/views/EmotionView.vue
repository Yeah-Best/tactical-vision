<template>
  <div class="space-y-8">
    <div class="text-center space-y-2">
      <h1 class="text-4xl font-bold text-text-primary">情绪疏导</h1>
      <p class="text-text-secondary">青莲剑仙在此倾听，为你驱散心头的阴霾</p>
    </div>

    <div class="card">
      <h2 class="text-2xl font-semibold text-gold-primary mb-6 flex items-center">
        <el-icon class="mr-2"><HelpFilled /></el-icon>
        当前情绪状态
      </h2>
      
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <span class="text-text-primary font-medium">心态指数</span>
          <span 
            class="text-2xl font-bold"
            :style="{ color: chatStore.currentEmotion.color }"
          >
            {{ chatStore.currentEmotion.level }}/10
          </span>
        </div>
        
        <div class="emotion-indicator">
          <div 
            class="h-full bg-white rounded-full transition-all duration-500"
            :style="{ 
              width: `${chatStore.currentEmotion.level * 10}%`,
              backgroundColor: chatStore.currentEmotion.color
            }"
          />
        </div>
        
        <div class="flex justify-between text-sm text-text-secondary">
          <span>热血沸腾</span>
          <span>状态良好</span>
          <span>略有波动</span>
          <span>情绪低落</span>
          <span>心态崩盘</span>
        </div>
        
        <div class="text-center">
          <span 
            class="inline-block px-4 py-2 rounded-full text-sm font-medium"
            :style="{
              backgroundColor: chatStore.currentEmotion.color + '20',
              color: chatStore.currentEmotion.color
            }"
          >
            {{ chatStore.currentEmotion.type }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="card space-y-6">
        <h2 class="text-2xl font-semibold text-gold-primary flex items-center">
          <el-icon class="mr-2"><Operation /></el-icon>
          常见场景
        </h2>
        
        <div class="space-y-3">
          <el-button
            v-for="scene in emotionScenes"
            :key="scene.type"
            @click="applyEmotionScene(scene)"
            class="w-full btn-secondary text-left justify-start h-auto py-3"
          >
            <div class="text-left">
              <div class="font-medium">{{ scene.label }}</div>
              <div class="text-xs text-text-secondary mt-1">{{ scene.description }}</div>
            </div>
          </el-button>
        </div>
      </div>

      <div class="lg:col-span-2 card flex flex-col h-[600px]">
        <h2 class="text-2xl font-semibold text-gold-primary mb-6 flex items-center">
          <el-icon class="mr-2"><ChatDotRound /></el-icon>
          与剑仙对话
        </h2>
        
        <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2" ref="messageContainer">
          <div
            v-for="message in chatStore.messages"
            :key="message.id"
            class="animate-fade-in-up"
            :class="message.role === 'user' ? 'text-right' : 'text-left'"
          >
            <div v-if="message.role === 'assistant'" class="flex items-start space-x-3">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-gold-primary to-gold-light flex items-center justify-center flex-shrink-0">
                <span class="text-xs font-bold text-ink-dark">李</span>
              </div>
              <div class="chat-bubble-ai">
                <div 
                  class="text-sm leading-relaxed"
                  v-html="formatMessage(message.content)"
                />
                <div class="text-xs text-text-secondary mt-2">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>
            
            <div v-else class="flex items-start space-x-3 justify-end">
              <div class="chat-bubble-user">
                <div class="text-sm leading-relaxed">
                  {{ message.content }}
                </div>
                <div class="text-xs text-ink-dark/70 mt-2">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                <span class="text-xs font-bold text-white">我</span>
              </div>
            </div>
          </div>
          
          <div v-if="chatStore.isGenerating" class="text-left">
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-gold-primary to-gold-light flex items-center justify-center">
                <span class="text-xs font-bold text-ink-dark">李</span>
              </div>
              <div class="chat-bubble-ai">
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-gold-primary rounded-full animate-bounce" style="animation-delay: 0s"></div>
                  <div class="w-2 h-2 bg-gold-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2 h-2 bg-gold-primary rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="border-t border-ink-darker pt-4">
          <div class="flex space-x-3">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="2"
              placeholder="分享你的烦恼，青莲剑仙在此倾听..."
              class="flex-1"
              resize="none"
              @keyup.enter="handleSend"
              :disabled="chatStore.isGenerating"
            />
            <el-button
              type="primary"
              @click="handleSend"
              :disabled="!userInput.trim() || chatStore.isGenerating"
              class="btn-primary h-20"
            >
              <el-icon class="text-lg"><Position /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="card" v-if="emotionHistory.length > 0">
      <h2 class="text-2xl font-semibold text-gold-primary mb-6 flex items-center">
        <el-icon class="mr-2"><Clock /></el-icon>
        疏导历史
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="record in emotionHistory"
          :key="record.id"
          class="bg-ink-dark rounded-xl p-4 border border-ink-darker hover:border-gold-primary transition-all duration-300"
        >
          <div class="flex justify-between items-start mb-2">
            <span 
              class="inline-block px-2 py-1 rounded-full text-xs font-medium"
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
          <p class="text-sm text-text-secondary line-clamp-2">
            {{ record.emotionReason }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import {
  HelpFilled,
  Operation,
  ChatDotRound,
  Position,
  Clock
} from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'
import { analyzeEmotion, getEmotionHistory } from '../api/emotion'
import type { EmotionRecord } from '../types'

const chatStore = useChatStore()
const { messages } = storeToRefs(chatStore)

const userInput = ref('')
const messageContainer = ref<HTMLElement>()
const emotionHistory = ref<EmotionRecord[]>([])

const emotionScenes = [
  {
    type: '连跪烦躁',
    label: '连跪烦躁',
    description: '连续失利，心情烦躁',
    emotionLevel: 8,
    message: '我已经连跪好几把了，每一把都感觉队友特别坑，现在心态很爆炸，怎么办？'
  },
  {
    type: '失误自责',
    label: '失误自责',
    description: '关键失误，后悔不已',
    emotionLevel: 6,
    message: '刚才那波团战我完全失误了，技能放错导致团灭，队友都在怪我，我感觉特别自责。'
  },
  {
    type: '逆风绝望',
    label: '逆风绝望',
    description: '逆风局势，感到绝望',
    emotionLevel: 7,
    message: '这把开局就逆风，经济落后很多，队友都开始互相埋怨了，我感觉这局已经没了。'
  },
  {
    type: '被喷委屈',
    label: '被喷委屈',
    description: '被队友指责，感到委屈',
    emotionLevel: 5,
    message: '我被对面针对，发育不好，队友就一直喷我，我真的尽力了，感觉很委屈。'
  },
  {
    type: '晋级赛紧张',
    label: '晋级赛紧张',
    description: '晋级赛压力，紧张焦虑',
    emotionLevel: 4,
    message: '这把是晋级赛，我特别紧张，怕输了又要重新打，现在手都在抖。'
  },
  {
    type: '胜利喜悦',
    label: '胜利喜悦',
    description: '取得胜利，心情愉悦',
    emotionLevel: 2,
    message: '刚才逆风翻盘赢了，感觉特别爽！想找人分享这份喜悦！'
  }
]

// 发送消息
const handleSend = async () => {
  const message = userInput.value.trim()
  if (!message || chatStore.isGenerating) return

  // 添加用户消息
  chatStore.addUserMessage(message)
  userInput.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 设置生成状态
  chatStore.isGenerating = true

  try {
    // 【修改点】：在开始接收流式数据前，先创建一条空的AI消息气泡
    chatStore.addAIMessage('')

    // 调用情绪分析API
    const generator = analyzeEmotion({
      message,
      emotionType: detectEmotionType(message),
      emotionLevel: estimateEmotionLevel(message)
    })

    let fullContent = ''
    for await (const chunk of generator) {
      if (chunk.content) {
        fullContent += chunk.content
        
        // 找到所有的AI消息，持续更新最后一条（刚才创建的那条）
        const aiMessages = chatStore.messages.filter(m => m.role === 'assistant')
        if (aiMessages.length > 0) {
          const lastAIMessage = aiMessages[aiMessages.length - 1]
          lastAIMessage.content = fullContent
        }
        
        await nextTick()
        scrollToBottom()
      }
    }

    // 更新情绪状态
    updateEmotionStatus(fullContent)
    
    ElMessage.success('情绪疏导完成')
  } catch (error) {
    console.error('情绪分析失败:', error)
    ElMessage.error('连接失败，请稍后重试')
  } finally {
    chatStore.isGenerating = false
  }
}

// 应用情绪场景
const applyEmotionScene = (scene: any) => {
  chatStore.setEmotion(scene.type, scene.emotionLevel, getEmotionColor(scene.emotionLevel))
  userInput.value = scene.message
  ElMessage.info(`已选择场景：${scene.label}`)
}

// 检测情绪类型
const detectEmotionType = (message: string): string => {
  const keywords: Record<string, string[]> = {
    '烦躁': ['烦', '气', '怒', '火大'],
    '自责': ['错', '失误', '怪我', '自责'],
    '绝望': ['没希望', '绝望', '放弃', '没了'],
    '委屈': ['委屈', '冤枉', '尽力', '怪我'],
    '紧张': ['紧张', '抖', '怕', '压力'],
    '喜悦': ['爽', '开心', '高兴', '棒']
  }
  
  for (const [type, words] of Object.entries(keywords)) {
    if (words.some(word => message.includes(word))) {
      return type
    }
  }
  
  return '失落'
}

// 估计情绪级别
const estimateEmotionLevel = (message: string): number => {
  const strongEmotionWords = ['很', '非常', '特别', '太', '极', '无比', '强烈']
  const count = strongEmotionWords.filter(word => message.includes(word)).length
  
  return Math.min(3 + count, 10)
}

// 获取情绪颜色
const getEmotionColor = (level: number): string => {
  if (level >= 8) return '#DA3633'
  if (level >= 6) return '#D29922'
  if (level >= 4) return '#388BFD'
  return '#2EA043'
}

// 更新情绪状态
const updateEmotionStatus = (content: string) => {
  // 简单根据回复内容判断情绪改善程度
  if (content.includes('不') && content.includes('要') && content.includes('担心')) {
    // 情绪改善
    const newLevel = Math.max(1, chatStore.currentEmotion.level - 2)
    chatStore.setEmotion('缓解', newLevel, getEmotionColor(newLevel))
  }
}

// 格式化消息
const formatMessage = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/【([^】]+)】/g, '<strong class="text-gold-primary">【$1】</strong>')
    .replace(/“([^”]+)”/g, '<span class="text-gold-light italic">“$1”</span>')
}

// 格式化时间
const formatTime = (date: Date) => {
  const d = new Date(date)
  return `${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

// 格式化日期
const formatDate = (date: string | Date) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

// 滚动到底部
const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// 加载情绪历史
const loadEmotionHistory = async () => {
  try {
    const response = await getEmotionHistory(6)
    if (response.success) {
      emotionHistory.value = response.data || []
    }
  } catch (error) {
    console.error('加载情绪历史失败:', error)
  }
}

onMounted(() => {
  loadEmotionHistory()
})
</script>

<style scoped>
</style>