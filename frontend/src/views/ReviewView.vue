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
              :loading="isLoadingGames"
            >
              <el-option
                v-for="game in supportedGames"
                :key="game.code"
                :label="game.name"
                :value="game.name"
                :disabled="game.status !== '已实现'"
              >
                <div class="flex items-center justify-between">
                  <span>{{ game.name }}</span>
                  <el-tag
                    :type="game.status === '已实现' ? 'success' : 'info'"
                    size="small"
                    class="ml-2"
                  >
                    {{ game.status }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
            <p v-if="formData.gameType && !isGameSupported" class="mt-2 text-xs text-orange-500">
              该游戏类型暂未实现完整的数据抓取，可能影响复盘质量。
            </p>
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

          <el-form-item label="当前版本（可选）">
            <div class="flex space-x-2">
              <el-input
                v-model="formData.gameVersion"
                placeholder="例如：14.6"
                class="flex-1"
              />
              <el-button
                @click="fetchLatestVersion"
                :loading="isLoadingVersion"
                type="primary"
                :icon="Clock"
              >
                获取最新版本
              </el-button>
            </div>
            <p class="mt-2 text-xs text-text-secondary">
              如需启用版本知识检索，建议填写{{ formData.gameType }}当前版本号。
              <span v-if="latestVersion" class="text-gold-primary">
                最新版本：{{ latestVersion.version }}（{{ latestVersion.update_time }}）
              </span>
            </p>
          </el-form-item>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <el-form-item label="我方阵容（可选）">
              <el-input
                v-model="formData.teamCompositionText"
                type="textarea"
                :rows="3"
                placeholder="请输入我方英雄，使用逗号分隔，例如：Aatrox, Lee Sin, Ahri"
                class="w-full"
              />
            </el-form-item>

            <el-form-item label="敌方阵容（可选）">
              <el-input
                v-model="formData.enemyCompositionText"
                type="textarea"
                :rows="3"
                placeholder="请输入敌方英雄，使用逗号分隔，例如：Jax, Viego, Orianna"
                class="w-full"
              />
            </el-form-item>
          </div>

          <el-form-item label="对局截图（可选）">
            <div
              class="w-full border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer"
              :class="isDragOver ? 'border-gold-primary bg-amber-50' : 'border-border hover:border-gold-primary hover:bg-amber-50/40'"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleDrop"
              @click="triggerFileInput"
            >
              <!-- 已上传图片预览 -->
              <div v-if="uploadedImages.length > 0" class="p-3">
                <div class="grid grid-cols-3 gap-2 mb-3">
                  <div
                    v-for="(img, index) in uploadedImages"
                    :key="index"
                    class="relative group aspect-video rounded-lg overflow-hidden border border-border shadow-sm"
                  >
                    <img :src="img.url" :alt="img.name" class="w-full h-full object-cover" />
                    <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <el-button
                        type="danger"
                        :icon="Delete"
                        circle
                        size="small"
                        @click.stop="removeImage(index)"
                      />
                    </div>
                    <div class="absolute bottom-0 left-0 right-0 bg-black/40 text-white text-xs px-1 py-0.5 truncate">
                      {{ img.name }}
                    </div>
                  </div>
                  <!-- 继续添加按钮 -->
                  <div
                    v-if="uploadedImages.length < 6"
                    class="aspect-video rounded-lg border-2 border-dashed border-border flex items-center justify-center cursor-pointer hover:border-gold-primary transition-colors"
                    @click.stop="triggerFileInput"
                  >
                    <el-icon class="text-2xl text-text-secondary"><Plus /></el-icon>
                  </div>
                </div>
                <p class="text-xs text-text-secondary text-center">已上传 {{ uploadedImages.length }}/6 张，点击图片可删除</p>
              </div>

              <!-- 空状态提示 -->
              <div v-else class="flex flex-col items-center justify-center py-8 space-y-3">
                <el-icon class="text-4xl text-gold-primary"><Picture /></el-icon>
                <div class="text-center">
                  <p class="text-text-primary font-medium">上传对局截图</p>
                  <p class="text-sm text-text-secondary mt-1">拖拽图片到此处，或点击选择文件</p>
                  <p class="text-xs text-text-secondary mt-1">支持 JPG、PNG、WEBP，最多 6 张</p>
                </div>
              </div>
            </div>
            <input
              ref="fileInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              multiple
              class="hidden"
              @change="handleFileChange"
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
            @click="handleAnalyzeGame"
            :loading="isAnalyzing"
            class="w-full btn-primary"
            :disabled="!formData.gameType || !formData.gameResult || !formData.gameDescription"
          >
            <el-icon class="mr-2"><MagicStick /></el-icon>
            开始复盘分析
          </el-button>
        </el-form>

        <!-- 快捷场景 -->
        <div v-if="currentQuickScenes.length > 0" class="space-y-3">
          <h3 class="text-lg font-medium text-text-primary">快捷场景</h3>
          <div class="grid grid-cols-2 gap-3">
            <el-button
              v-for="scene in currentQuickScenes"
              :key="scene.label"
              @click="applyQuickScene(scene)"
              class="btn-secondary h-auto py-3 h-16"
            >
              <div class="text-left font-medium leading-tight">{{ scene.label }}</div>
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
            class="prose max-w-none text-text-primary"
            v-html="formatReport(analysisReport)"
          />

          <!-- 操作按钮 -->
          <div class="flex space-x-3 pt-4 border-t border-border">
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
          class="bg-bg-dark rounded-xl p-4 border border-border hover:border-gold-primary transition-all duration-300 cursor-pointer"
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
import { onBeforeUnmount, onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  MagicStick,
  Document,
  Collection,
  Share,
  Clock,
  Loading,
  Picture,
  Plus,
  Delete
} from '@element-plus/icons-vue'
import { analyzeGame, getReviewHistory, getSupportedGames } from '../api/review'
import { getLatestVersion } from '../api/game_version'
import type { GameReview, GameVersionInfo } from '../types'

interface ReviewFormData {
  gameType: string
  gameResult: string
  kda: string
  gameVersion: string
  teamCompositionText: string
  enemyCompositionText: string
  gameDescription: string
}

interface UploadedImage {
  url: string
  name: string
  file: File
}

interface QuickScene {
  label: string
  data: Partial<ReviewFormData>
}

const createDefaultFormData = (): ReviewFormData => ({
  gameType: '王者荣耀',
  gameResult: '失败',
  kda: '',
  gameVersion: '当前版本',
  teamCompositionText: '',
  enemyCompositionText: '',
  gameDescription: ''
})

const formData = ref<ReviewFormData>(createDefaultFormData())
const isAnalyzing = ref(false)
const analysisReport = ref('')
const historyRecords = ref<GameReview[]>([])
const uploadedImages = ref<UploadedImage[]>([])
const fileInputRef = ref<HTMLInputElement>()
const isDragOver = ref(false)
const supportedGames = ref<any[]>([])
const isLoadingGames = ref(false)
const latestVersion = ref<GameVersionInfo | null>(null)
const isLoadingVersion = ref(false)

// 计算当前游戏是否支持
const isGameSupported = computed(() => {
  const currentGame = supportedGames.value.find(g => g.name === formData.value.gameType)
  return currentGame?.status === '已实现'
})

// 计算当前游戏类型的快捷场景
const currentQuickScenes = computed(() => {
  if (!formData.value.gameType) return []
  return quickScenes.filter(scene => scene.data.gameType === formData.value.gameType)
})

const clearUploadedImages = () => {
  uploadedImages.value.forEach(image => URL.revokeObjectURL(image.url))
  uploadedImages.value = []
}

const loadSupportedGames = async () => {
  if (isLoadingGames.value) return
  isLoadingGames.value = true
  try {
    const response = await getSupportedGames()
    if (response.success) {
      supportedGames.value = response.data || []
    }
  } catch (error) {
    console.error('加载支持的游戏列表失败:', error)
    // 使用默认游戏列表
    supportedGames.value = [
      { code: 'honor_kings', name: '王者荣耀', status: '已实现' },
      { code: 'league_of_legends', name: '英雄联盟', status: '未实现' },
    ]
  } finally {
    isLoadingGames.value = false
  }
}

const fetchLatestVersion = async () => {
  if (!formData.value.gameType) {
    ElMessage.warning('请先选择游戏类型')
    return
  }

  isLoadingVersion.value = true
  try {
    // 根据游戏名称映射到游戏代码
    const gameCodeMap: Record<string, string> = {
      '王者荣耀': 'honor_of_kings',
      '英雄联盟': 'lol',
      '无畏契约': 'valorant'
    }

    const gameCode = gameCodeMap[formData.value.gameType] || 'honor_of_kings'
    const versionInfo = await getLatestVersion(gameCode)

    if (versionInfo) {
      latestVersion.value = versionInfo
      formData.value.gameVersion = versionInfo.version
      ElMessage.success(`已获取最新版本：${versionInfo.version}`)
    } else {
      ElMessage.warning('无法获取最新版本信息')
    }
  } catch (error) {
    console.error('获取最新版本失败:', error)
    ElMessage.error('获取最新版本失败，请稍后重试')
  } finally {
    isLoadingVersion.value = false
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const processFiles = (files: FileList | File[]) => {
  const arr = Array.from(files)
  const remaining = 6 - uploadedImages.value.length
  if (remaining <= 0) {
    ElMessage.warning('最多上传 6 张截图')
    return
  }

  const toAdd = arr.slice(0, remaining)
  toAdd.forEach(file => {
    if (!file.type.startsWith('image/')) {
      ElMessage.warning(`${file.name} 不是图片文件`)
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`${file.name} 超过 10MB 限制`)
      return
    }

    const url = URL.createObjectURL(file)
    uploadedImages.value.push({ url, name: file.name, file })
  })

  if (arr.length > remaining) {
    ElMessage.warning(`已达上限，仅添加了前 ${remaining} 张`)
  }
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    processFiles(input.files)
  }
  input.value = ''
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files) {
    processFiles(event.dataTransfer.files)
  }
}

const removeImage = (index: number) => {
  const image = uploadedImages.value[index]
  if (!image) {
    return
  }
  URL.revokeObjectURL(image.url)
  uploadedImages.value.splice(index, 1)
}

const parseCompositionInput = (input: string) =>
  input
    .split(/[\n,，、/]+/)
    .map(item => item.trim())
    .filter(Boolean)

const quickScenes: QuickScene[] = [
  // 王者荣耀场景
  {
    label: '王者荣耀排位失利',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameVersion: '当前版本',
      teamCompositionText: '亚瑟, 韩信, 妲己, 后羿, 庄周',
      enemyCompositionText: '廉颇, 李白, 王昭君, 鲁班七号, 张飞',
      gameDescription: '这把我玩打野韩信，前期控到两条小龙，但中期连续两波暴君团被对面开到双C。对面王昭君和张飞的联动太快，我几次想大招进场都被反开，最后主宰团溃败输掉比赛。'
    }
  },
  {
    label: '连跪心态崩',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameVersion: '当前版本',
      teamCompositionText: '赵云, 孙悟空, 安琪拉, 虞姬, 牛魔',
      enemyCompositionText: '程咬金, 阿轲, 甄姬, 孙尚香, 蔡文姬',
      gameDescription: '已经连跪好几把了，这把我玩中单安琪拉。对线还能顶住，但边路一直掉点，野区视野也总被抢。每次团战还没拉开阵型就被阿轲切进来，打着打着心态直接炸了。'
    }
  },
  {
    label: '逆风翻盘',
    data: {
      gameType: '王者荣耀',
      gameResult: '胜利',
      gameVersion: '当前版本',
      teamCompositionText: '老夫子, 铠, 诸葛亮, 成吉思汗, 孙膑',
      enemyCompositionText: '花木兰, 兰陵王, 小乔, 马可波罗, 大乔',
      gameDescription: '前15分钟我们被线权压得很惨，外塔掉得很快，但我方双C拖到了三件套。后期我用铠绕后先手开到马可波罗，孙膑加速保住成吉思汗，最后一波暴君团完成翻盘。'
    }
  },
  {
    label: '个人失误多',
    data: {
      gameType: '王者荣耀',
      gameResult: '失败',
      gameVersion: '当前版本',
      teamCompositionText: '夏侯惇, 典韦, 高渐离, 百里守约, 东皇太一',
      enemyCompositionText: '项羽, 澜, 周瑜, 黄忠, 鬼谷子',
      gameDescription: '这把我玩百里守约，前期狙击还可以，但中期两波暴君团站位太靠前，被澜潜水进场直接秒掉。还有一波高地防守我输出位置导致团战瞬间崩盘，整体看主要是自己处理失误太多。'
    }
  },
  // 英雄联盟场景
  {
    label: 'LOL排位失利',
    data: {
      gameType: '英雄联盟',
      gameResult: '失败',
      gameVersion: '14.6',
      teamCompositionText: '诺手, 梦魇, 阿狸, 金克丝, 布隆',
      enemyCompositionText: '鳄鱼, 盲僧, 瑞兹, 薇恩, 锤石',
      gameDescription: '这把我玩打野梦魇，前期拿到一血但控龙节奏不好。中期对面鳄鱼发育太好，我几次关灯进场都被秒掉。后期大龙团我开团时机不对，被薇恩进场收割，团灭输掉比赛。'
    }
  },
  {
    label: '连跪心态崩',
    data: {
      gameType: '英雄联盟',
      gameResult: '失败',
      gameVersion: '14.6',
      teamCompositionText: '猴子, 劫, 佐伊, 轮子妈, 巴德',
      enemyCompositionText: '石头人, 永恩, 辛德拉, 女警, 洛',
      gameDescription: '已经连跪好几把了，这把我玩中单劫。对线还可以，但下路一直被军训，野区也总被对面打野入侵。每次团战还没拉开阵型就被永恩进场切死，打着打着心态直接炸了。'
    }
  },
  {
    label: '逆风翻盘',
    data: {
      gameType: '英雄联盟',
      gameResult: '胜利',
      gameVersion: '14.6',
      teamCompositionText: '杰斯, 千珏, 拉克丝, 卡莎, 牛头',
      enemyCompositionText: '瑞文, 豹女, 发条, 艾希, 娜美',
      gameDescription: '前15分钟我们被线权压得很惨，外塔掉得很快，但我方双C拖到了三件套。后期我用千珏大招保住卡莎，牛头开团顶飞对面双C，最后一波大龙团完成翻盘。'
    }
  },
  {
    label: '个人失误多',
    data: {
      gameType: '英雄联盟',
      gameResult: '失败',
      gameVersion: '14.6',
      teamCompositionText: '蒙多, 梦魇, 泽拉斯, 伊泽瑞尔, 烬',
      enemyCompositionText: '铁男, 螳螂, 薇恩, 卢锡安, 泰坦',
      gameDescription: '这把我玩ADC伊泽瑞尔，前期对线还能打，但中期几波小龙团站位太靠前，被螳螂进化E进场直接秒掉。还有一波高地防守我E技能撞墙，导致团战瞬间崩盘，整体看主要是自己处理失误太多。'
    }
  }
]

const handleAnalyzeGame = async () => {
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
      gameDescription: formData.value.gameDescription,
      gameVersion: formData.value.gameVersion.trim() || undefined,
      teamComposition: parseCompositionInput(formData.value.teamCompositionText),
      enemyComposition: parseCompositionInput(formData.value.enemyCompositionText)
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

const applyQuickScene = (scene: QuickScene) => {
  clearUploadedImages()
  formData.value = {
    ...createDefaultFormData(),
    ...scene.data
  }
  ElMessage.info('已填充场景模板，可根据实际情况修改')
}

const formatReport = (report: string) => {
  return report
    .replace(/\n/g, '<br>')
    .replace(/【([^】]+)】/g, '<strong class="text-gold-primary">【$1】</strong>')
    .replace(/“([^”]+)”/g, '<span class="text-gold-light italic">“$1”</span>')
}

const saveReport = () => {
  ElMessage.success('报告已保存到历史记录')
  loadHistoryRecords()
}

const shareReport = () => {
  if (navigator.share) {
    void navigator.share({
      title: '战术视界 - 对局复盘',
      text: analysisReport.value.slice(0, 100) + '...',
      url: window.location.href
    })
  } else {
    void navigator.clipboard.writeText(analysisReport.value)
    ElMessage.success('报告已复制到剪贴板')
  }
}

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

const loadHistory = (record: GameReview) => {
  clearUploadedImages()
  const defaultFormData = createDefaultFormData()
  formData.value = {
    ...defaultFormData,
    gameType: record.gameType,
    gameResult: record.gameResult,
    kda: record.kda || '',
    gameVersion: record.gameVersion || defaultFormData.gameVersion,
    teamCompositionText: (record.teamComposition || []).join(', '),
    enemyCompositionText: (record.enemyComposition || []).join(', '),
    gameDescription: record.gameDescription
  }
  analysisReport.value = record.reviewReport
  ElMessage.info('已加载历史记录')
}

const formatDate = (date: string | Date) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  loadHistoryRecords()
  loadSupportedGames()
})

onBeforeUnmount(() => {
  clearUploadedImages()
})
</script>

<style scoped>
</style>
