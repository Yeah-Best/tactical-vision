<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div class="text-center space-y-2">
      <h1 class="text-4xl font-bold text-text-primary">对局复盘</h1>
      <p class="text-text-secondary">让青莲剑仙为你剖析战局，指点迷津</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- 左侧：数据输入 -->
      <div class="card space-y-6">
        <h2 class="text-2xl font-semibold text-gold-primary flex items-center">
          <el-icon class="mr-2"><DataAnalysis /></el-icon>
          对局信息
        </h2>

        <el-form :model="formData" label-position="top" class="space-y-4">
          <el-form-item label="游戏类型">
            <el-select
              v-model="formData.gameType"
              placeholder="请选择游戏类型"
              class="w-full"
            >
              <el-option label="王者荣耀" value="王者荣耀" />
              <el-option label="英雄联盟" value="英雄联盟" />
              <el-option label="和平精英" value="和平精英" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>

          <el-form-item label="对局结果">
            <el-select
              v-model="formData.gameResult"
              placeholder="请选择对局结果"
              class="w-full"
            >
              <el-option label="胜利" value="胜利" />
              <el-option label="失败" value="失败" />
              <el-option label="平局" value="平局" />
            </el-select>
          </el-form-item>

          <el-form-item label="KDA数据">
            <el-input
              v-model="formData.kda"
              placeholder="例如：8/3/12"
              class="w-full"
            />
          </el-form-item>

          <el-form-item label="对局描述">
            <el-input
              v-model="formData.gameDescription"
              type="textarea"
              :rows="6"
              placeholder="请详细描述这场对局的情况，包括：
- 你在游戏中的位置和角色
- 关键团战的情况
- 觉得失误的地方
- 当时的思路和决策"
              class="w-full"
            />
          </el-form-item>

          <el-button
            type="primary"
            @click="analyzeGame"
            :loading="isAnalyzing"
            class="w-full btn-primary"
            :disabled="!formData.gameType || !formData.gameResult || !formData.gameDescription"
          >
            <el-icon class="mr-2"><MagicStick /></el-icon>
            开始复盘分析
          </el-button>
        </el-form>

        <!-- 快捷场景 -->
        <div class="space-y-3">
          <h3 class="text-lg font-medium text-text-primary">快捷场景</h3>
          <div class="grid grid-cols-2 gap-3">
            <el-button
              v-for="scene in quickScenes"
              :key="scene.label"
              @click="applyQuickScene(scene)"
              class="btn-secondary text-left"
            >
              {{ scene.label }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧：复盘报告 -->
      <div class="card space-y-6">
        <h2 class="text-2xl font-semibold text-gold-primary flex items-center">
          <el-icon class="mr-2"><Document /></el-icon>
          复盘报告
        </h2>

        <div v-if="!analysisReport" class="text-center py-12">
          <el-icon class="text-6xl text-text-secondary mb-4"><DataAnalysis /></el-icon>
          <p class="text-text-secondary">提交对局信息后，青莲剑仙将为你生成复盘报告</p>
        </div>

        <div v-else class="space-y-4">
          <!-- 报告内容 -->
          <div
            class="prose prose-invert max-w-none"
            v-html="formatReport(analysisReport)"
          />

          <!-- 操作按钮 -->
          <div class="flex space-x-3 pt-4 border-t border-ink-darker">
            <el-button @click="saveReport" class="btn-secondary">
              <el-icon class="mr-2"><Collection /></el-icon>
              保存报告
            </el-button>
            <el-button @click="shareReport" class="btn-secondary">
              <el-icon class="mr-2"><Share /></el-icon>
              分享
            </el-button>
          </div>
        </div>

        <!-- 分析中状态 -->
        <div v-if="isAnalyzing" class="text-center py-8">
          <el-icon class="text-4xl text-gold-primary animate-spin mb-4"><Loading /></el-icon>
          <p class="text-gold-primary">青莲剑仙正在分析战局...</p>
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div class="card" v-if="historyRecords.length > 0">
      <h2 class="text-2xl font-semibold text-gold-primary mb-6 flex items-center">
        <el-icon class="mr-2"><Clock /></el-icon>
        复盘历史
      </h2>

      <div class="space-y-4">
        <div
          v-for="record in historyRecords"
          :key="record.id"
          class="bg-ink-dark rounded-xl p-4 border border-ink-darker hover:border-gold-primary transition-all duration-300 cursor-pointer"
          @click="loadHistory(record)"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold text-text-primary">
              {{ record.gameType }} - {{ record.gameResult }}
            </h3>
            <span class="text-sm text-text-secondary">
              {{ formatDate(record.createdAt) }}
            </span>
          </div>
          <p class="text-sm text-text-secondary truncate">
            {{ record.gameDescription }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  MagicStick,
  Document,
  Collection,
  Share,
  Clock,
  Loading
} from '@element-plus/icons-vue'
import { analyzeGame, getReviewHistory } from '../api/review'
import type { GameReview } from '../types'

const formData = ref({
  gameType: '王者荣耀',
  gameResult: '失败',
  kda: '',
  gameDescription: ''
})

const isAnalyzing = ref(false)
const analysisReport = ref('')
const historyRecords = ref<GameReview[]>([])

const quickScenes = [
  {
    label: '排位赛失利',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameDescription: '刚才的排位赛，我玩的是打野位。前期节奏不错，拿了几条龙，但是到了中期团战总是输。后期对面C位装备起来了，我们根本打不动。最后高地团灭，被推了水晶。'
    }
  },
  {
    label: '连跪心态崩',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameDescription: '已经连跪5把了，每一把都感觉队友特别坑。上单把把被单杀，中路不会支援，辅助不做视野。我感觉自己打得挺好的，但就是赢不了，现在心态很爆炸。'
    }
  },
  {
    label: '逆风翻盘',
    data: {
      gameType: '王者荣耀',
      gameResult: '胜利',
      gameDescription: '这把开局大逆风，对面经济领先我们5000多。但是我们没有放弃，慢慢运营带线拖后期。最后一波团战，我找准时机切后排，团灭对面一波翻盘。'
    }
  },
  {
    label: '个人失误多',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameDescription: '这把输主要是因为我自己失误太多了。前期对线期还好，但是到了团战阶段，我总是站位不好，经常被对面开团秒杀。有几波关键的龙团，我技能放错了，导致团战输了。'
    }
  }
]

// 分析对局
const analyzeGame = async () => {
  if (!formData.value.gameType || !formData.value.gameResult || !formData.value.gameDescription) {
    ElMessage.warning('请填写完整的对局信息')
    return
  }

  isAnalyzing.value = true
  analysisReport.value = ''

  try {
    const generator = analyzeGame({
      gameType: formData.value.gameType,
      gameResult: formData.value.gameResult,
      kda: formData.value.kda,
      gameDescription: formData.value.gameDescription
    })

    for await (const chunk of generator) {
      if (chunk.content) {
        analysisReport.value += chunk.content
      }
      if (chunk.done) {
        break
      }
    }

    ElMessage.success('复盘分析完成！')
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请稍后重试')
  } finally {
    isAnalyzing.value = false
  }
}

// 应用快捷场景
const applyQuickScene = (scene: any) => {
  formData.value = { ...scene.data }
  ElMessage.info('已填充场景模板，可根据实际情况修改')
}

// 格式化报告
const formatReport = (report: string) => {
  return report
    .replace(/\n/g, '<br>')
    .replace(/【([^】]+)】/g, '<strong class="text-gold-primary">【$1】</strong>')
    .replace(/“([^”]+)”/g, '<span class="text-gold-light italic">“$1”</span>')
}

// 保存报告
const saveReport = () => {
  ElMessage.success('报告已保存到历史记录')
  loadHistoryRecords()
}

// 分享报告
const shareReport = () => {
  if (navigator.share) {
    navigator.share({
      title: '战术视界 - 对局复盘',
      text: analysisReport.value.slice(0, 100) + '...',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(analysisReport.value)
    ElMessage.success('报告已复制到剪贴板')
  }
}

// 加载历史记录
const loadHistoryRecords = async () => {
  try {
    const response = await getReviewHistory(10)
    if (response.success) {
      historyRecords.value = response.data || []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

// 加载历史记录详情
const loadHistory = (record: GameReview) => {
  formData.value = {
    gameType: record.gameType,
    gameResult: record.gameResult,
    kda: record.kda || '',
    gameDescription: record.gameDescription
  }
  analysisReport.value = record.reviewReport
  ElMessage.info('已加载历史记录')
}

// 格式化日期
const formatDate = (date: string | Date) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  loadHistoryRecords()
})
</script>

<style scoped>
</style>
