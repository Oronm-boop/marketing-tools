<template>
  <div class="agent-page">
    <aside class="agent-sidebar" aria-label="聊天历史">
      <div class="brand">
        <h1>MDT AI Agent</h1>
      </div>

      <div class="sidebar-body">
        <button
          class="new-chat-button"
          :class="{ active: isActiveDraftSession }"
          type="button"
          @click="createNewSession"
        >
          <IconGlyph name="chat" />
          <span>新建聊天</span>
        </button>

        <nav class="history-list" aria-label="会话记录">
          <button
            v-for="chat in sortedSessions"
            :key="chat.id"
            class="history-item"
            :class="{ active: activeChatId === chat.id }"
            type="button"
            :aria-current="activeChatId === chat.id ? 'page' : undefined"
            @click="selectSession(chat.id)"
          >
            <span class="history-row">
              <IconGlyph name="chat" />
              <span class="history-title">{{ chat.title }}</span>
            </span>
            <span class="history-date">{{ formatSessionMeta(chat) }}</span>
          </button>
        </nav>
      </div>
    </aside>

    <section class="agent-workspace">
      <header class="topbar">
        <div class="topbar-left">
          <span class="topbar-divider" aria-hidden="true"></span>
        </div>

        <div class="topbar-actions">
          <button class="icon-button" type="button" aria-label="通知" title="通知">
            <IconGlyph name="bell" />
          </button>
          <button class="icon-button" type="button" aria-label="帮助" title="帮助">
            <IconGlyph name="help" />
          </button>
          <button
            class="icon-button settings-btn"
            type="button"
            aria-label="模型设置"
            title="模型设置"
            @click="settingsVisible = true"
          >
            <IconGlyph name="settings" />
          </button>
          <div class="avatar" aria-label="用户头像">
            <IconGlyph name="user" />
          </div>
        </div>
      </header>

      <main class="tool-canvas">
        <div class="tool-tabs" role="tablist" aria-label="AI 营销工具">
          <button
            class="tool-tab"
            :class="{ active: activeTool === 'seo' }"
            type="button"
            role="tab"
            :aria-selected="activeTool === 'seo'"
            @click="activeTool = 'seo'"
          >
            SEO关键词生成
          </button>
          <button
            class="tool-tab"
            :class="{ active: activeTool === 'copy' }"
            type="button"
            role="tab"
            :aria-selected="activeTool === 'copy'"
            @click="activeTool = 'copy'"
          >
            宣传文案工具
          </button>
        </div>

        <section v-show="activeTool === 'seo'" class="tool-card" aria-labelledby="seo-tool-title">
          <div class="card-header">
            <span class="card-icon">
              <IconGlyph name="searchInsights" />
            </span>
            <div>
              <h2 id="seo-tool-title">SEO 关键词生成器</h2>
              <p>为你的产品生成高相关度搜索关键词。</p>
            </div>
          </div>

          <form class="tool-form" @submit.prevent="submitSeo">
            <label class="field">
              <span>我是做什么的</span>
              <input
                v-model="seoForm.business"
                :disabled="seoLoading"
                type="text"
                placeholder="智能家居设备"
              />
            </label>

            <label class="field">
              <span>产品或服务特点</span>
              <textarea
                v-model="seoForm.features"
                :disabled="seoLoading"
                rows="4"
                placeholder="支持语音控制，兼容米家/苹果HomeKit..."
              ></textarea>
            </label>

            <div class="field-grid">
              <label class="field">
                <span>关键词数量</span>
                <input
                  v-model.number="seoForm.keywordCount"
                  :disabled="seoLoading"
                  min="1"
                  max="100"
                  type="number"
                  placeholder="10"
                />
              </label>
            </div>

            <fieldset class="choice-group">
              <legend>搜索引擎</legend>
              <label v-for="engine in searchEngines" :key="engine" class="choice-pill">
                <input
                  v-model="seoForm.searchEngines"
                  :disabled="seoLoading"
                  :value="engine"
                  type="checkbox"
                />
                <span>{{ engine }}</span>
              </label>
            </fieldset>

            <p v-if="seoError" class="form-error">{{ seoError }}</p>

            <button class="primary-action" :disabled="seoLoading" type="submit">
              <IconGlyph name="spark" />
              <span>{{ seoLoading ? '生成中...' : '生成SEO关键词' }}</span>
            </button>
          </form>

          <section v-if="seoResults.length" ref="seoResultRef" class="result-panel">
            <div class="result-header">
              <h3>SEO关键词结果</h3>
              <span class="model-pill">{{ seoModel }}</span>
            </div>

            <div class="keyword-tags">
              <span v-for="item in seoResults" :key="item.keyword" class="keyword-tag">
                {{ item.keyword }}
              </span>
            </div>

            <div class="result-table-wrap">
              <table class="result-table">
                <thead>
                  <tr>
                    <th>关键词</th>
                    <th>搜索量预估</th>
                    <th>难度</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in seoResults" :key="`${item.keyword}-${item.search_volume_est}`">
                    <td>{{ item.keyword }}</td>
                    <td>{{ item.search_volume_est }}</td>
                    <td>
                      <span class="difficulty-badge" :class="difficultyClass(item.difficulty)">
                        {{ item.difficulty }}
                      </span>
                    </td>
                    <td>
                      <button
                        class="table-action"
                        type="button"
                        :disabled="copyLoading"
                        @click="prepareCopyFromKeyword(item.keyword)"
                      >
                        <IconGlyph name="document" />
                        <span>生成文案</span>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </section>

        <section v-show="activeTool === 'copy'" ref="copyToolRef" class="tool-card" aria-labelledby="copy-tool-title">
          <div class="card-header">
            <span class="card-icon">
              <IconGlyph name="document" />
            </span>
            <div>
              <h2 id="copy-tool-title">宣传文案工具</h2>
              <p>生成适配不同社媒平台的营销文案。</p>
            </div>
          </div>

          <form class="tool-form" @submit.prevent="submitCopy">
            <label class="field">
              <span>关键词</span>
              <input
                ref="copyKeywordInputRef"
                v-model="copyForm.keyword"
                :disabled="copyLoading"
                type="text"
                placeholder="智能家居设备推荐"
              />
            </label>

            <div class="field-grid">
              <label class="field">
                <span>关键词出现次数</span>
                <input
                  v-model.number="copyForm.keywordOccurrences"
                  :disabled="copyLoading"
                  min="0"
                  max="10"
                  type="number"
                  placeholder="0"
                />
              </label>

              <label class="field">
                <span>生成多少篇</span>
                <input
                  v-model.number="copyForm.articleCount"
                  :disabled="copyLoading"
                  min="1"
                  max="20"
                  type="number"
                  placeholder="3"
                />
              </label>
            </div>

            <fieldset class="choice-group">
              <legend>社媒平台</legend>
              <label v-for="platform in socialPlatforms" :key="platform" class="choice-pill">
                <input
                  v-model="copyForm.platforms"
                  :disabled="copyLoading"
                  :value="platform"
                  type="checkbox"
                />
                <span>{{ platform }}</span>
              </label>
            </fieldset>

            <p v-if="copyError" class="form-error">{{ copyError }}</p>

            <button class="primary-action" :disabled="copyLoading" type="submit">
              <IconGlyph name="spark" />
              <span>{{ copyLoading ? '生成中...' : '生成宣传文案' }}</span>
            </button>
          </form>

          <section v-if="copyResults.length" ref="copyResultRef" class="result-panel">
            <div class="result-header">
              <h3>宣传文案结果</h3>
              <span class="model-pill">{{ copyModel }}</span>
            </div>

            <article
              v-for="(item, index) in copyResults"
              :key="`${item.title}-${index}`"
              class="copy-result-card"
            >
              <div class="copy-result-head">
                <h4>{{ item.title || `文案 ${index + 1}` }}</h4>
                <div class="copy-meta">
                  <span>{{ item.platform || '通用' }}</span>
                  <span>{{ item.angle || '综合切入' }}</span>
                  <span>关键词 {{ item.actual_keyword_count }} 次</span>
                </div>
              </div>
              <p>{{ item.content }}</p>
            </article>
          </section>
        </section>

        <section v-if="activeConversationEntries.length" class="conversation-panel">
          <div class="result-header">
            <h3>当前会话记录</h3>
            <span class="model-pill">{{ activeConversationEntries.length }} 条</span>
          </div>

          <article v-for="entry in activeConversationEntries" :key="entry.id" class="conversation-entry">
            <div class="conversation-entry-head">
              <span class="session-type">{{ entry.type === 'seo' ? 'SEO关键词' : '宣传文案' }}</span>
              <div>
                <h4>{{ entry.title }}</h4>
                <p>{{ formatDateTime(entry.createdAt) }}</p>
              </div>
            </div>

            <p class="conversation-query">{{ getEntrySummary(entry) }}</p>

            <div v-if="entry.type === 'seo'" class="keyword-tags compact">
              <span v-for="item in getEntrySeoItems(entry)" :key="item.keyword" class="keyword-tag">
                {{ item.keyword }}
              </span>
            </div>

            <div v-else class="session-copy-list">
              <article
                v-for="(item, index) in getEntryCopyItems(entry)"
                :key="`${entry.id}-${index}`"
                class="session-copy-item"
              >
                <div class="session-copy-item-head">
                  <span class="copy-platform-badge">
                    {{ item.platform || getFallbackCopyPlatform(entry, index) }}
                  </span>
                  <span v-if="item.angle" class="copy-angle-text">{{ item.angle }}</span>
                </div>
                <p>{{ item.content }}</p>
              </article>
            </div>
          </article>
        </section>
      </main>
    </section>

    <SettingsDialog v-model:visible="settingsVisible" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onMounted, reactive, ref, type PropType } from 'vue'
import {
  generateCopywriting,
  generateSeoKeywords,
  type CopywritingItem,
  type SeoKeywordItem
} from '@api/generation'
import SettingsDialog from '@components/SettingsDialog.vue'

type ToolKey = 'seo' | 'copy'
type IconName = 'chat' | 'bell' | 'help' | 'user' | 'searchInsights' | 'document' | 'spark' | 'settings'
type SeoEntryRequest = {
  business: string
  features: string
  keywordCount: number
  searchEngines: string[]
}
type CopyEntryRequest = {
  keyword: string
  keywordOccurrences: number
  articleCount: number
  platforms: string[]
}
type SeoGenerationEntry = {
  id: string
  type: 'seo'
  title: string
  createdAt: number
  request: SeoEntryRequest
  response: {
    items: SeoKeywordItem[]
    model: string
  }
}
type CopyGenerationEntry = {
  id: string
  type: 'copy'
  title: string
  createdAt: number
  request: CopyEntryRequest
  response: {
    items: CopywritingItem[]
    model: string
  }
}
type GenerationEntry = SeoGenerationEntry | CopyGenerationEntry
type ChatSession = {
  id: string
  title: string
  createdAt: number
  updatedAt: number
  entries: GenerationEntry[]
}

const SESSION_STORAGE_KEY = 'mdt-ai-agent.sessions.v1'

const iconPaths: Record<IconName, string[]> = {
  chat: [
    'M5 5.5A3.5 3.5 0 0 1 8.5 2h7A3.5 3.5 0 0 1 19 5.5v4A3.5 3.5 0 0 1 15.5 13H10l-5 4v-4.4A3.5 3.5 0 0 1 2 9.1V5.5A3.5 3.5 0 0 1 5.5 2Z',
    'M7 7h10M7 10h6'
  ],
  bell: ['M18 9a6 6 0 0 0-12 0c0 7-2 8-2 8h16s-2-1-2-8Z', 'M10 20a2 2 0 0 0 4 0'],
  help: ['M9.2 9a3 3 0 1 1 4.1 2.8c-.9.4-1.3 1-1.3 2.2', 'M12 18h.01'],
  user: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4.5 20a7.5 7.5 0 0 1 15 0'],
  searchInsights: ['M4 18V9', 'M9 18V5', 'M14 18v-7', 'M19 18V7', 'M3 20h18'],
  document: ['M7 3h7l4 4v14H7V3Z', 'M14 3v5h5', 'M10 13h6', 'M10 17h4'],
  spark: [
    'M12 3l1.7 4.4L18 9l-4.3 1.6L12 15l-1.7-4.4L6 9l4.3-1.6L12 3Z',
    'M5 14l.8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8L5 14Z'
  ],
  settings: [
    'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z'
  ]
}

const IconGlyph = defineComponent({
  name: 'IconGlyph',
  props: {
    name: {
      type: String as PropType<IconName>,
      required: true
    }
  },
  setup(props, { attrs }) {
    return () =>
      h(
        'svg',
        {
          ...attrs,
          viewBox: '0 0 24 24',
          fill: 'none',
          xmlns: 'http://www.w3.org/2000/svg',
          'aria-hidden': 'true'
        },
        iconPaths[props.name].map((path, index) =>
          h('path', {
            key: `${props.name}-${index}`,
            d: path,
            stroke: 'currentColor',
            'stroke-width': '1.8',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round'
          })
        )
      )
  }
})

const settingsVisible = ref(false)
const activeTool = ref<ToolKey>('seo')
const sessions = ref<ChatSession[]>(loadSessions())
const activeChatId = ref(ensureInitialSessionId(sessions.value))
const seoResultRef = ref<HTMLElement | null>(null)
const copyResultRef = ref<HTMLElement | null>(null)
const copyToolRef = ref<HTMLElement | null>(null)
const copyKeywordInputRef = ref<HTMLInputElement | null>(null)
const sortedSessions = computed(() => [...sessions.value].sort((a, b) => b.updatedAt - a.updatedAt))
const activeSession = computed(() => sessions.value.find((session) => session.id === activeChatId.value) ?? null)
const activeConversationEntries = computed(() => {
  return activeSession.value ? [...activeSession.value.entries].reverse() : []
})
const isActiveDraftSession = computed(() => activeSession.value?.entries.length === 0)

const searchEngines = ['百度', '360搜索', '必应']
const socialPlatforms = ['小红书', '百度', 'B站', '抖音', '视频号', '微博']

const seoForm = reactive({
  business: '',
  features: '',
  keywordCount: 10,
  searchEngines: ['百度', '360搜索', '必应']
})

const copyForm = reactive({
  keyword: '',
  keywordOccurrences: 0,
  articleCount: 3,
  platforms: ['小红书', '百度', 'B站']
})

const seoLoading = ref(false)
const copyLoading = ref(false)
const seoError = ref('')
const copyError = ref('')
const seoModel = ref('')
const copyModel = ref('')
const seoResults = ref<SeoKeywordItem[]>([])
const copyResults = ref<CopywritingItem[]>([])

const submitSeo = async () => {
  const validationError = validateSeoForm()
  if (validationError) {
    seoError.value = validationError
    return
  }

  seoLoading.value = true
  seoError.value = ''
  const requestPayload: SeoEntryRequest = {
    business: seoForm.business.trim(),
    features: seoForm.features.trim(),
    keywordCount: Number(seoForm.keywordCount),
    searchEngines: [...seoForm.searchEngines]
  }

  try {
    const response = await generateSeoKeywords({
      business_description: requestPayload.business,
      product_features: requestPayload.features,
      keyword_count: requestPayload.keywordCount,
      search_engines: requestPayload.searchEngines
    })
    seoResults.value = response.items
    seoModel.value = response.model
    appendSessionEntry({
      id: createId(),
      type: 'seo',
      title: createSeoEntryTitle(requestPayload),
      createdAt: Date.now(),
      request: requestPayload,
      response
    })
    await scrollToResults(seoResultRef.value)
  } catch (error) {
    seoError.value = getErrorMessage(error)
  } finally {
    seoLoading.value = false
  }
}

const submitCopy = async () => {
  const validationError = validateCopyForm()
  if (validationError) {
    copyError.value = validationError
    return
  }

  copyLoading.value = true
  copyError.value = ''
  const requestPayload: CopyEntryRequest = {
    keyword: copyForm.keyword.trim(),
    keywordOccurrences: Number(copyForm.keywordOccurrences),
    articleCount: Number(copyForm.articleCount),
    platforms: [...copyForm.platforms]
  }

  try {
    const response = await generateCopywriting({
      keyword: requestPayload.keyword,
      keyword_repeat_count: requestPayload.keywordOccurrences,
      article_count: requestPayload.articleCount,
      platform_styles: requestPayload.platforms
    })
    console.log('[LLM copywriting response]', response)
    console.log(
      '[LLM copywriting items]',
      response.items.map((item, index) => ({
        index: index + 1,
        title: item.title,
        platform: item.platform,
        angle: item.angle,
        content: item.content,
        actual_keyword_count: item.actual_keyword_count
      }))
    )
    copyResults.value = response.items
    copyModel.value = response.model
    appendSessionEntry({
      id: createId(),
      type: 'copy',
      title: createCopyEntryTitle(requestPayload),
      createdAt: Date.now(),
      request: requestPayload,
      response
    })
    await scrollToResults(copyResultRef.value)
  } catch (error) {
    copyError.value = getErrorMessage(error)
  } finally {
    copyLoading.value = false
  }
}

const validateSeoForm = () => {
  if (!seoForm.business.trim()) return '请输入业务描述'
  if (!seoForm.features.trim()) return '请输入产品或服务特点'
  if (!Number.isFinite(Number(seoForm.keywordCount)) || seoForm.keywordCount < 1) return '关键词数量至少为 1'
  if (seoForm.keywordCount > 100) return '关键词数量最多为 100'
  if (!seoForm.searchEngines.length) return '请至少选择一个搜索引擎'
  return ''
}

const validateCopyForm = () => {
  if (!copyForm.keyword.trim()) return '请输入关键词'
  if (!Number.isFinite(Number(copyForm.keywordOccurrences)) || copyForm.keywordOccurrences < 0) {
    return '关键词出现次数不能小于 0'
  }
  if (copyForm.keywordOccurrences > 10) return '关键词出现次数最多为 10'
  if (!Number.isFinite(Number(copyForm.articleCount)) || copyForm.articleCount < 1) return '生成篇数至少为 1'
  if (copyForm.articleCount > 20) return '生成篇数最多为 20'
  if (!copyForm.platforms.length) return '请至少选择一个社媒平台'
  return ''
}

const getErrorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message
  return '请求失败，请稍后重试'
}

const scrollToResults = async (target: HTMLElement | null) => {
  await nextTick()
  target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const difficultyClass = (difficulty: string) => {
  if (difficulty.includes('低')) return 'low'
  if (difficulty.includes('高')) return 'high'
  return 'medium'
}

const prepareCopyFromKeyword = async (keyword: string) => {
  const selectedKeyword = keyword.trim()
  if (!selectedKeyword || copyLoading.value) return

  copyForm.keyword = selectedKeyword
  copyError.value = ''
  copyResults.value = []
  copyModel.value = ''
  activeTool.value = 'copy'

  await nextTick()
  copyToolRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  copyKeywordInputRef.value?.focus()
}

function createNewSession() {
  if (activeSession.value?.entries.length === 0) {
    resetCurrentResults()
    activeTool.value = 'seo'
    return
  }

  const session = createEmptySession()
  sessions.value = [session, ...sessions.value]
  activeChatId.value = session.id
  activeTool.value = 'seo'
  resetCurrentResults()
  saveSessions(sessions.value)
}

function selectSession(sessionId: string) {
  const session = sessions.value.find((item) => item.id === sessionId)
  if (!session) return

  activeChatId.value = session.id
  hydrateFromSession(session)
}

function appendSessionEntry(entry: GenerationEntry) {
  let session = activeSession.value
  if (!session) {
    session = createEmptySession()
    sessions.value = [session, ...sessions.value]
    activeChatId.value = session.id
  }

  session.entries.push(entry)
  session.updatedAt = entry.createdAt
  if (session.entries.length === 1 || session.title === '新会话') {
    session.title = entry.title
  }
  saveSessions(sessions.value)
}

function hydrateFromSession(session: ChatSession) {
  resetCurrentResults()
  const lastEntry = session.entries[session.entries.length - 1]
  if (!lastEntry) {
    activeTool.value = 'seo'
    return
  }

  activeTool.value = lastEntry.type
  if (lastEntry.type === 'seo') {
    seoForm.business = lastEntry.request.business
    seoForm.features = lastEntry.request.features
    seoForm.keywordCount = lastEntry.request.keywordCount
    seoForm.searchEngines = [...lastEntry.request.searchEngines]
    seoResults.value = lastEntry.response.items
    seoModel.value = lastEntry.response.model
    return
  }

  copyForm.keyword = lastEntry.request.keyword
  copyForm.keywordOccurrences = lastEntry.request.keywordOccurrences
  copyForm.articleCount = lastEntry.request.articleCount
  copyForm.platforms = [...lastEntry.request.platforms]
  copyResults.value = lastEntry.response.items
  copyModel.value = lastEntry.response.model
}

function resetCurrentResults() {
  seoError.value = ''
  copyError.value = ''
  seoResults.value = []
  copyResults.value = []
  seoModel.value = ''
  copyModel.value = ''
}

function createEmptySession(): ChatSession {
  const now = Date.now()
  return {
    id: createId(),
    title: '新会话',
    createdAt: now,
    updatedAt: now,
    entries: []
  }
}

function ensureInitialSessionId(items: ChatSession[]) {
  if (items.length) {
    return [...items].sort((a, b) => b.updatedAt - a.updatedAt)[0].id
  }

  const session = createEmptySession()
  items.push(session)
  saveSessions(items)
  return session.id
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as ChatSession[]
    if (!Array.isArray(parsed)) return []
    return parsed.filter(isValidSession)
  } catch (error) {
    console.warn('读取会话记录失败', error)
    return []
  }
}

function saveSessions(items: ChatSession[]) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(items))
}

function isValidSession(value: ChatSession) {
  return Boolean(value?.id && value.title && Array.isArray(value.entries))
}

function createSeoEntryTitle(request: SeoEntryRequest) {
  return truncateTitle(`SEO：${request.business}`)
}

function createCopyEntryTitle(request: CopyEntryRequest) {
  return truncateTitle(`文案：${request.keyword}`)
}

function truncateTitle(value: string) {
  return value.length > 18 ? `${value.slice(0, 18)}...` : value
}

function createId() {
  if (crypto.randomUUID) return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function formatSessionMeta(session: ChatSession) {
  const countText = session.entries.length ? `${session.entries.length} 条` : '未生成'
  return `${formatDate(session.updatedAt)} · ${countText}`
}

function formatDate(timestamp: number) {
  return new Date(timestamp).toLocaleDateString('zh-CN')
}

function formatDateTime(timestamp: number) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getEntrySummary(entry: GenerationEntry) {
  if (entry.type === 'seo') {
    return `业务：${entry.request.business}；特点：${entry.request.features}`
  }
  return `关键词：${entry.request.keyword}；平台：${entry.request.platforms.join('、')}`
}

function getEntrySeoItems(entry: GenerationEntry) {
  return entry.type === 'seo' ? entry.response.items : []
}

function getEntryCopyItems(entry: GenerationEntry) {
  return entry.type === 'copy' ? entry.response.items : []
}

function getFallbackCopyPlatform(entry: GenerationEntry, index: number) {
  if (entry.type !== 'copy') return '通用'
  return entry.request.platforms[index % entry.request.platforms.length] || '通用'
}

onMounted(() => {
  document.title = 'MDT AI Agent'
  if (activeSession.value) {
    hydrateFromSession(activeSession.value)
  }
})
</script>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  background: #f4f6f8;
}

:global(button),
:global(input),
:global(textarea) {
  font: inherit;
}

.agent-page {
  --primary: #0058be;
  --primary-soft: #dbeafe;
  --success: var(--primary);
  --success-soft: var(--primary-soft);
  --success-faint: #eff6ff;
  --success-border: #bfdbfe;
  --background: #f4f6f8;
  --surface: #ffffff;
  --surface-muted: #f1f5f9;
  --text: #1e293b;
  --text-soft: #334155;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --sidebar-width: 288px;
  min-height: 100vh;
  background: var(--background);
  color: var(--text-soft);
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
}

.agent-sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 20;
  display: flex;
  width: var(--sidebar-width);
  min-height: 100vh;
  flex-direction: column;
  gap: 20px;
  border-right: 1px solid var(--border);
  background: var(--surface);
  padding: 24px 16px;
}

.brand {
  display: flex;
  align-items: center;
  min-height: 68px;
  padding: 0 6px;
}

.brand h1 {
  margin: 0;
  color: #334155;
  font-size: 26px;
  font-weight: 700;
  line-height: 34px;
}

.sidebar-body {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  gap: 24px;
}

.new-chat-button {
  display: inline-flex;
  min-height: 50px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: var(--success-soft);
  color: var(--success);
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(0, 88, 190, 0.04);
  transition:
    background-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
}

.new-chat-button:hover,
.new-chat-button.active {
  background: var(--success);
  color: #ffffff;
  box-shadow: 0 10px 22px rgba(0, 88, 190, 0.18);
}

.history-list {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding: 2px 0;
}

.history-item {
  position: relative;
  display: grid;
  gap: 5px;
  width: 100%;
  min-height: 64px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  padding: 10px 12px 10px 10px;
  text-align: left;
  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
}

.history-item::before {
  position: absolute;
  inset: 12px auto 12px 0;
  width: 3px;
  border-radius: 999px;
  background: var(--success);
  content: '';
  opacity: 0;
  transform: scaleY(0.4);
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.history-item:hover {
  background: #f8fafc;
  border-color: var(--border);
  transform: translateX(1px);
}

.history-item.active {
  background: linear-gradient(90deg, var(--success-faint) 0%, #ffffff 100%);
  border-color: var(--success-border);
  box-shadow: 0 10px 24px rgba(0, 88, 190, 0.1);
  color: #0755b4;
}

.history-item.active::before {
  opacity: 1;
  transform: scaleY(1);
}

.history-row {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 10px;
}

.history-row svg,
.new-chat-button svg,
.icon-button svg,
.avatar svg,
.card-icon svg,
.primary-action svg {
  width: 20px;
  height: 20px;
}

.history-row svg {
  flex: 0 0 20px;
  color: var(--success);
  transition: color 0.18s ease;
}

.history-item.active .history-row svg {
  color: #0755b4;
}

.history-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  line-height: 22px;
  transition: color 0.18s ease;
}

.history-item.active .history-title {
  color: #0755b4;
  font-weight: 700;
}

.history-date {
  margin-left: 30px;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 16px;
  opacity: 0.6;
  transition:
    color 0.18s ease,
    opacity 0.18s ease;
}

.history-item.active .history-date {
  color: #0755b4;
  opacity: 0.78;
}

.agent-workspace {
  min-height: 100vh;
  margin-left: var(--sidebar-width);
}

.topbar {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 10;
  display: flex;
  width: calc(100% - var(--sidebar-width));
  height: 64px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  padding: 0 24px;
}

.topbar-left,
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.topbar-divider {
  display: block;
  width: 1px;
  height: 24px;
  background: var(--border);
}

.topbar-actions {
  gap: 8px;
}

.icon-button,
.avatar {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 999px;
  color: var(--text-muted);
}

.icon-button {
  border: 0;
  background: transparent;
  cursor: pointer;
  transition:
    background-color 0.18s ease,
    color 0.18s ease;
}

.icon-button:hover,
.icon-button:focus-visible {
  background: var(--surface-muted);
  color: var(--primary);
}

.avatar {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  background: #d5e0f8;
  color: #586377;
}

.tool-canvas {
  width: min(100%, 1280px);
  padding: 112px 48px 48px;
}

.tool-tabs {
  display: flex;
  width: fit-content;
  max-width: 100%;
  gap: 4px;
  margin: 0 auto 48px;
  overflow-x: auto;
  border-radius: 8px;
  background: var(--primary-soft);
  padding: 4px;
}

.tool-tab {
  min-height: 40px;
  flex: 0 0 auto;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  padding: 8px 32px;
  transition:
    background-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
}

.tool-tab:hover {
  color: #004395;
}

.tool-tab.active {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 88, 190, 0.16);
}

.new-chat-button:active,
.tool-tab:active,
.primary-action:active,
.table-action:active {
  transform: scale(0.98);
}

.tool-card {
  width: min(100%, 768px);
  margin: 0 auto;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
  padding: 48px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.card-icon {
  display: grid;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  place-items: center;
  color: var(--primary);
}

.card-icon svg {
  width: 32px;
  height: 32px;
}

.card-header h2,
.card-header p {
  margin: 0;
}

.card-header h2 {
  color: var(--text);
  font-size: 24px;
  font-weight: 700;
  line-height: 32px;
}

.card-header p {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 20px;
}

.tool-form {
  display: grid;
  gap: 24px;
}

.field-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field {
  display: grid;
  gap: 8px;
}

.field span,
.choice-group legend {
  color: var(--text);
  font-size: 14px;
  font-weight: 700;
  line-height: 20px;
}

.field input,
.field textarea {
  width: 100%;
  border: 0;
  border-radius: 12px;
  outline: none;
  background: var(--surface-muted);
  color: var(--text);
  font-size: 14px;
  line-height: 20px;
  transition:
    box-shadow 0.18s ease,
    background-color 0.18s ease;
}

.field input:disabled,
.field textarea:disabled,
.choice-pill input:disabled {
  cursor: not-allowed;
  opacity: 0.68;
}

.field input {
  height: 44px;
  padding: 0 16px;
}

.field textarea {
  min-height: 112px;
  padding: 16px;
  resize: vertical;
}

.field input::placeholder,
.field textarea::placeholder {
  color: rgba(100, 116, 139, 0.52);
}

.field input:focus,
.field textarea:focus {
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 88, 190, 0.16);
}

.choice-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 0;
  border: 0;
  padding: 0;
}

.choice-group legend {
  width: 100%;
  padding: 0;
}

.choice-pill {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
  cursor: pointer;
  padding: 8px 16px;
  transition: background-color 0.18s ease;
}

.choice-pill:hover {
  background: var(--surface-muted);
}

.choice-pill input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
}

.choice-pill span {
  color: var(--text);
  font-size: 14px;
  line-height: 20px;
  white-space: nowrap;
}

.primary-action {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  border: 0;
  border-radius: 12px;
  background: var(--primary);
  color: #ffffff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 12px 20px rgba(0, 88, 190, 0.16);
  transition:
    background-color 0.18s ease,
    transform 0.18s ease;
}

.primary-action:hover {
  background: #004395;
}

.primary-action:disabled {
  cursor: wait;
  opacity: 0.72;
  transform: none;
}

.table-action {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #eff6ff;
  color: #0755b4;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  line-height: 20px;
  white-space: nowrap;
  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
  padding: 5px 10px;
}

.table-action svg {
  width: 16px;
  height: 16px;
}

.table-action:hover:not(:disabled) {
  border-color: #93c5fd;
  background: #dbeafe;
  color: #004395;
}

.table-action:disabled {
  cursor: not-allowed;
  opacity: 0.64;
  transform: none;
}

.form-error {
  margin: -4px 0 0;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 13px;
  line-height: 20px;
  padding: 10px 12px;
}

.result-panel {
  display: grid;
  gap: 18px;
  margin-top: 32px;
  border-top: 1px solid var(--border);
  padding-top: 28px;
}

.result-header {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.result-header h3 {
  margin: 0;
  color: var(--text);
  font-size: 18px;
  font-weight: 700;
  line-height: 26px;
}

.model-pill {
  flex: 0 0 auto;
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 18px;
  padding: 4px 10px;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keyword-tag {
  max-width: 100%;
  overflow-wrap: anywhere;
  border: 1px solid #bfdbfe;
  border-radius: 999px;
  background: #eff6ff;
  color: #0755b4;
  font-size: 13px;
  font-weight: 700;
  line-height: 20px;
  padding: 6px 12px;
}

.result-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.result-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  color: var(--text-soft);
  font-size: 14px;
  line-height: 20px;
}

.result-table th,
.result-table td {
  border-bottom: 1px solid var(--border);
  padding: 12px;
  text-align: left;
  vertical-align: top;
}

.result-table th {
  color: var(--text);
  font-size: 13px;
  font-weight: 700;
}

.result-table td:first-child {
  color: var(--text);
  font-weight: 700;
}

.difficulty-badge {
  display: inline-flex;
  min-width: 42px;
  justify-content: center;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  line-height: 18px;
  padding: 3px 9px;
}

.difficulty-badge.low {
  background: #eff6ff;
  color: #0755b4;
}

.difficulty-badge.medium {
  background: #fef3c7;
  color: #b45309;
}

.difficulty-badge.high {
  background: #fee2e2;
  color: #b91c1c;
}

.copy-result-card {
  display: grid;
  gap: 12px;
  border-top: 1px solid var(--border);
  padding-top: 18px;
}

.copy-result-card:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.copy-result-head {
  display: grid;
  gap: 8px;
}

.copy-result-head h4 {
  margin: 0;
  color: var(--text);
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
}

.copy-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.copy-meta span {
  border-radius: 999px;
  background: #dbeafe;
  color: #0755b4;
  font-size: 12px;
  font-weight: 700;
  line-height: 18px;
  padding: 4px 10px;
}

.copy-result-card p {
  margin: 0;
  color: var(--text-soft);
  font-size: 14px;
  line-height: 24px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.conversation-panel {
  display: grid;
  gap: 18px;
  width: min(100%, 768px);
  margin: 32px auto 0;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
  padding: 28px;
}

.conversation-entry {
  display: grid;
  gap: 14px;
  border-top: 1px solid var(--border);
  padding-top: 18px;
}

.conversation-entry:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.conversation-entry-head {
  display: grid;
  gap: 10px;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: start;
}

.conversation-entry-head h4,
.conversation-entry-head p,
.conversation-query,
.session-copy-list p {
  margin: 0;
}

.conversation-entry-head h4 {
  overflow: hidden;
  color: var(--text);
  font-size: 15px;
  font-weight: 700;
  line-height: 22px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-entry-head p {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 18px;
}

.session-type {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: #eff6ff;
  color: #0755b4;
  font-size: 12px;
  font-weight: 700;
  line-height: 18px;
  padding: 4px 10px;
}

.conversation-query {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 20px;
  overflow-wrap: anywhere;
}

.keyword-tags.compact {
  gap: 8px;
}

.keyword-tags.compact .keyword-tag {
  font-size: 12px;
  line-height: 18px;
  padding: 4px 10px;
}

.session-copy-list {
  display: grid;
  gap: 10px;
}

.session-copy-item {
  display: grid;
  gap: 8px;
  border-radius: 8px;
  background: var(--surface-muted);
  padding: 12px;
}

.session-copy-item-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.copy-platform-badge {
  border-radius: 999px;
  background: #dbeafe;
  color: #0755b4;
  font-size: 12px;
  font-weight: 700;
  line-height: 18px;
  padding: 3px 9px;
}

.copy-angle-text {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 18px;
}

.session-copy-list p {
  color: var(--text-soft);
  font-size: 13px;
  line-height: 22px;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

@media (max-width: 900px) {
  .agent-sidebar {
    position: static;
    width: 100%;
    min-height: auto;
  }

  .history-list {
    max-height: 220px;
  }

  .agent-workspace {
    margin-left: 0;
  }

  .topbar {
    position: sticky;
    width: 100%;
  }

  .tool-canvas {
    padding: 48px 24px;
  }
}

@media (max-width: 640px) {
  .agent-sidebar {
    padding: 16px;
  }

  .brand h1,
  .card-header h2 {
    font-size: 22px;
    line-height: 30px;
  }

  .tool-canvas {
    padding: 32px 16px;
  }

  .tool-tabs {
    width: 100%;
    margin-bottom: 24px;
  }

  .tool-tab {
    flex: 1 0 150px;
    padding: 8px 16px;
  }

  .tool-card {
    padding: 24px 16px;
  }

  .card-header {
    align-items: flex-start;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
