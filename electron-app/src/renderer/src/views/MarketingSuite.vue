<template>
  <div class="suite-shell">
    <aside class="suite-sidebar" aria-label="主导航">
      <div class="suite-brand">MDT Marketing</div>

      <nav class="suite-nav" aria-label="营销工具导航">
        <button
          v-for="item in primaryNav"
          :key="item.page"
          class="nav-item"
          :class="{ active: activeNavPage === item.page }"
          type="button"
          @click="goToPage(item.page)"
        >
          <IconGlyph :name="item.icon" />
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="suite-nav nav-secondary">
        <button
          class="nav-item"
          :class="{ active: activeNavPage === 'accounts' }"
          type="button"
          @click="goToPage('accounts')"
        >
          <IconGlyph name="account" />
          <span>账号管理</span>
        </button>
        <button class="nav-item" type="button" @click="openSettings">
          <IconGlyph name="settings" />
          <span>设置</span>
        </button>
      </div>

      <button class="help-center" type="button">
        <IconGlyph name="help" />
        <span>帮助中心</span>
      </button>
    </aside>

    <section class="suite-main">
      <header class="suite-header">
        <h1>{{ headerTitle }}</h1>
        <div class="header-actions">
          <button class="icon-button" type="button" aria-label="通知">
            <IconGlyph name="bell" />
          </button>
          <button class="icon-button" type="button" aria-label="帮助">
            <IconGlyph name="help" />
          </button>
          <button
            v-if="visiblePage !== 'accounts'"
            class="icon-button"
            type="button"
            aria-label="模型设置"
            @click="openSettings"
          >
            <IconGlyph name="settings" />
          </button>
          <div class="user-avatar" aria-label="用户头像">
            <IconGlyph name="user" />
          </div>
        </div>
      </header>

      <main class="suite-content" :class="`page-${visiblePage}`">
        <section v-if="visiblePage === 'trends'" class="page-stack trends-page">
          <form class="search-bar" @submit.prevent="analyzeTrends">
            <IconGlyph name="search" />
            <input v-model="trendQuery" type="text" placeholder="输入关键词 (例如: 'AI 智能体')" />
            <button type="submit">分析</button>
          </form>

          <div class="dashboard-grid">
            <article class="data-card">
              <div class="card-title-row">
                <span class="card-icon blue"><IconGlyph name="hash" /></span>
                <h2>热门关键词</h2>
              </div>
              <div class="keyword-pills">
                <span v-for="tag in trendKeywords" :key="tag.text" :class="{ selected: tag.selected }">
                  {{ tag.text }}
                </span>
              </div>
            </article>

            <article class="data-card">
              <div class="card-title-row">
                <span class="card-icon red"><IconGlyph name="fire" /></span>
                <h2>爆款内容</h2>
              </div>
              <div class="hot-list">
                <div v-for="item in hotContent" :key="item.title" class="hot-list-item">
                  <span>{{ item.title }}</span>
                  <strong>{{ item.views }}</strong>
                </div>
              </div>
            </article>

            <article class="data-card tall">
              <div class="card-title-row">
                <span class="card-icon gray"><IconGlyph name="chart" /></span>
                <h2>竞品分析</h2>
              </div>
              <div class="competitor-list">
                <div v-for="item in competitors" :key="item.name" class="competitor-item">
                  <span class="competitor-badge">{{ item.short }}</span>
                  <div class="competitor-meta">
                    <div>
                      <span>{{ item.name }}</span>
                      <strong>{{ item.value }}%</strong>
                    </div>
                    <span class="progress-track">
                      <span class="progress-value" :style="{ width: `${item.value}%`, background: item.color }"></span>
                    </span>
                  </div>
                </div>
              </div>
            </article>

            <article class="data-card tall">
              <div class="card-title-row">
                <span class="card-icon green"><IconGlyph name="groups" /></span>
                <h2>目标人群</h2>
              </div>
              <div class="bar-chart" aria-hidden="true">
                <span class="bar bar-1"></span>
                <span class="bar bar-2"></span>
                <span class="bar bar-3"></span>
                <span class="bar bar-4"></span>
              </div>
              <h3 class="minor-heading">用户标签</h3>
              <div class="audience-tags">
                <span v-for="tag in audienceTags" :key="tag">{{ tag }}</span>
              </div>
              <div class="persona-box">
                <span>人群画像简述</span>
                <p>对 AI 效率工具有浓厚兴趣的一线城市专业人士</p>
              </div>
            </article>
          </div>

          <article class="advice-card">
            <div class="advice-title">
              <IconGlyph name="bulb" />
              <h2>AI 营销建议</h2>
            </div>
            <ul>
              <li v-for="item in marketingAdvice" :key="item">
                <IconGlyph name="check" />
                <span>{{ item }}</span>
              </li>
            </ul>
          </article>
        </section>

        <section v-else-if="visiblePage === 'seo'" class="page-stack seo-page">
          <section class="hero-card">
            <span class="hero-icon"><IconGlyph name="search" /></span>
            <div>
              <h2>SEO关键词生成</h2>
              <p>基于AI算法，深度分析并生成高转化的搜索关键词</p>
            </div>
            <button class="ghost-button" type="button" @click="openHistory">
              <IconGlyph name="history" />
              <span>历史记录</span>
            </button>
          </section>

          <form class="form-card" @submit.prevent="submitSeo">
            <label class="input-field">
              <span>我是做什么的 <b>*</b></span>
              <input
                v-model="seoForm.business"
                :disabled="seoLoading"
                type="text"
                placeholder="例如：高端智能家居设备厂商"
              />
            </label>
            <label class="input-field">
              <span>产品特点 <b>*</b></span>
              <textarea
                v-model="seoForm.features"
                :disabled="seoLoading"
                placeholder="描述您的产品核心卖点、竞争优势或目标客群..."
              ></textarea>
            </label>
            <label class="input-field count-field">
              <span>关键词数量</span>
              <input
                v-model.number="seoForm.keywordCount"
                :disabled="seoLoading"
                min="1"
                max="100"
                type="number"
                placeholder="输入1-100"
              />
              <em>MAX 100</em>
            </label>
            <p v-if="seoError" class="error-text">{{ seoError }}</p>
            <button class="primary-action" :disabled="seoLoading" type="submit">
              <IconGlyph name="spark" />
              <span>{{ seoLoading ? '生成中...' : '生成SEO关键词' }}</span>
            </button>
          </form>

          <section class="result-card">
            <div class="result-toolbar">
              <h2>生成结果预览</h2>
              <div>
                <button class="ghost-button compact" type="button">
                  <IconGlyph name="copy" />
                  <span>复制</span>
                </button>
                <button class="ghost-button compact" type="button" @click="resetSeoResults">
                  <IconGlyph name="refresh" />
                  <span>重新生成</span>
                </button>
              </div>
            </div>
            <h3>SEO关键词结果</h3>
            <div class="result-tags">
              <span v-for="item in displayedSeoResults" :key="item.keyword">{{ item.keyword }}</span>
            </div>
            <table class="suite-table">
              <thead>
                <tr>
                  <th>关键词</th>
                  <th>搜索量预估</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in displayedSeoResults" :key="`${item.keyword}-${item.search_volume_est}`">
                  <td>{{ item.keyword }}</td>
                  <td>{{ item.search_volume_est }}</td>
                  <td>
                    <button class="link-action" type="button" @click="prepareCopyFromKeyword(item.keyword)">
                      生成宣传文案
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </section>
        </section>

        <section v-else-if="visiblePage === 'copywriting'" class="copy-page">
          <form class="copy-settings-card" @submit.prevent="submitCopy">
            <div class="card-title-row with-divider">
              <span class="plain-icon"><IconGlyph name="document" /></span>
              <h2>生成设置</h2>
            </div>
            <label class="input-field">
              <span>关键词</span>
              <input
                v-model="copyForm.keyword"
                :disabled="copyLoading"
                type="text"
                placeholder="输入核心关键词，用逗号分隔"
              />
            </label>
            <label class="range-field">
              <span>出现次数</span>
              <strong>{{ copyForm.keywordOccurrences }}</strong>
              <input
                v-model.number="copyForm.keywordOccurrences"
                :disabled="copyLoading"
                type="range"
                min="0"
                max="10"
              />
            </label>
            <fieldset class="platform-grid">
              <legend>社交媒体选择</legend>
              <label v-for="platform in socialPlatforms" :key="platform" :class="{ checked: copyForm.platforms.includes(platform) }">
                <input v-model="copyForm.platforms" :disabled="copyLoading" :value="platform" type="checkbox" />
                <span>{{ platform }}</span>
              </label>
            </fieldset>
            <label class="select-field">
              <span>生成篇数</span>
              <select v-model.number="copyForm.articleCount" :disabled="copyLoading">
                <option :value="1">1</option>
                <option :value="3">3</option>
                <option :value="5">5</option>
                <option :value="8">8</option>
              </select>
            </label>
            <label class="select-field">
              <span>文案长度</span>
              <select v-model="copyLength" :disabled="copyLoading">
                <option>中文案 (300-800字)</option>
                <option>短文案 (100-300字)</option>
                <option>长文案 (800-1500字)</option>
              </select>
            </label>
            <p v-if="copyError" class="error-text">{{ copyError }}</p>
            <button class="primary-action stick-bottom" :disabled="copyLoading" type="submit">
              <IconGlyph name="spark" />
              <span>{{ copyLoading ? '生成中...' : '生成文案' }}</span>
            </button>
          </form>

          <section class="copy-preview-card">
            <div class="preview-tabs">
              <button
                v-for="tab in previewTabs"
                :key="tab"
                class="preview-tab"
                :class="{ active: activePreviewTab === tab }"
                type="button"
                @click="activePreviewTab = tab"
              >
                <IconGlyph :name="tab === '小红书' ? 'message' : 'document'" />
                <span>{{ tab }}</span>
              </button>
            </div>
            <div class="copy-results">
              <article v-for="(item, index) in displayedCopyResults" :key="`${item.title}-${index}`" class="copy-output">
                <div class="copy-output-head">
                  <h2>{{ item.title || `生成${index + 1}` }}</h2>
                  <button class="publish-mini" type="button">
                    <IconGlyph name="upload" />
                    <span>发布</span>
                  </button>
                </div>
                <p>{{ item.content }}</p>
              </article>
            </div>
          </section>
        </section>

        <section v-else-if="visiblePage === 'publish'" class="publish-page">
          <section class="editor-column">
            <article class="title-card">
              <label class="input-field">
                <span>标题</span>
                <input v-model="publishDraft.title" type="text" placeholder="输入文章标题..." />
              </label>
              <label class="input-field tag-field">
                <span>标签</span>
                <div class="tag-row">
                  <button v-for="tag in publishDraft.tags" :key="tag" type="button">
                    {{ tag }} <span>×</span>
                  </button>
                </div>
                <input type="text" placeholder="添加新标签，按回车确认..." />
              </label>
            </article>

            <article class="editor-card">
              <div class="editor-toolbar" aria-label="编辑工具栏">
                <button v-for="tool in editorTools" :key="tool" type="button">{{ tool }}</button>
                <span></span>
                <button type="button"><IconGlyph name="image" /></button>
                <button type="button"><IconGlyph name="link" /></button>
                <button class="ai-button" type="button">
                  <IconGlyph name="spark" />
                  <span>AI Optimized</span>
                </button>
              </div>
              <textarea v-model="publishDraft.content" placeholder="在此输入正文"></textarea>
            </article>
          </section>

          <aside class="publish-panel">
            <article class="publish-settings">
              <div class="card-title-row with-divider">
                <span class="plain-icon"><IconGlyph name="rocket" /></span>
                <h2>发布设置</h2>
              </div>
              <fieldset class="radio-row">
                <legend>发布时间</legend>
                <label>
                  <input v-model="publishDraft.schedule" type="radio" value="now" />
                  <span>立即发布</span>
                </label>
                <label>
                  <input v-model="publishDraft.schedule" type="radio" value="later" />
                  <span>定时发布</span>
                </label>
              </fieldset>

              <fieldset class="publish-platform-list">
                <legend>发布平台</legend>
                <label v-for="platform in publishPlatforms" :key="platform.name" :class="{ failed: platform.failed }">
                  <span class="platform-logo" :class="platform.color"><IconGlyph :name="platform.icon" /></span>
                  <span>
                    <strong>{{ platform.name }}</strong>
                    <em>{{ platform.failed ? '登录失败' : '已连接' }}</em>
                  </span>
                  <input v-model="publishDraft.platforms" :value="platform.name" type="checkbox" />
                </label>
              </fieldset>
            </article>

            <button class="publish-action" type="button">
              <IconGlyph name="send" />
              <span>(Publish)</span>
            </button>

            <article class="publish-alert">
              <IconGlyph name="alert" />
              <div>
                <h3>发布失败</h3>
                <p>部分账号需重新登录验证</p>
                <div>
                  <button type="button">查看详情</button>
                  <button type="button">
                    <IconGlyph name="refresh" />
                    <span>重新发布</span>
                  </button>
                </div>
              </div>
            </article>
          </aside>
        </section>

        <section v-else-if="visiblePage === 'accounts'" class="accounts-page">
          <article class="account-strip">
            <button
              v-for="account in accounts"
              :key="account.id"
              class="account-chip"
              :class="{ active: account.active }"
              type="button"
              @click="selectXhsAccount(account.id)"
            >
              <span class="account-avatar" :class="account.avatarClass">
                <span>{{ account.initial }}</span>
                <i>小红书</i>
              </span>
              <strong>{{ account.name }}<em>-小红书</em></strong>
              <small>{{ formatAccountStatus(account) }}</small>
            </button>
          </article>

          <div class="account-actions">
            <button class="primary-lite" type="button" :disabled="xhsAccountLoading" @click="addXhsAccount">添加账号</button>
            <button class="primary-lite" type="button" :disabled="xhsAccountLoading || !activeXhsAccount" @click="saveActiveXhsSession(true)">同步账号</button>
            <button type="button">账号管理</button>
            <button type="button">账号分组</button>
            <button type="button" :disabled="!activeXhsAccount" @click="openXhsLogin">一键重新登录</button>
          </div>

          <article class="login-browser-frame">
            <div class="login-window-title">
              <span>登录账号：{{ activeXhsAccount?.name ?? '小红书账号' }}</span>
              <div>
                <button type="button">□</button>
                <button type="button">×</button>
              </div>
            </div>
            <div class="browser-toolbar">
              <button type="button" title="后退" @click="goXhsBack"><IconGlyph name="arrowLeft" /></button>
              <button type="button" title="前进" @click="goXhsForward"><IconGlyph name="arrowRight" /></button>
              <button type="button" title="刷新" @click="refreshXhsWebview"><IconGlyph name="refresh" /></button>
              <button type="button" title="主页" @click="openXhsHome"><IconGlyph name="home" /></button>
              <span>{{ currentXhsUrl }}</span>
              <em>{{ activeXhsAccount?.partition ?? '未创建分区' }}</em>
              <em>{{ activeXhsAccount ? `${activeXhsAccount.cookieCount} cookies` : '0 cookies' }}</em>
              <small>− 100 +</small>
            </div>
            <div class="notice-line">
              <strong>{{ xhsSessionMessage }}</strong>
              <a href="#">无法添加账号?</a>
            </div>

            <div class="xiaohongshu-webview-wrap">
              <webview
                v-if="activeXhsAccount"
                :key="activeXhsAccount.id"
                ref="xiaohongshuWebviewRef"
                class="xiaohongshu-webview"
                :src="activeXhsStartUrl"
                :partition="activeXhsAccount.partition"
                useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                allowpopups
                @dom-ready="handleXhsDomReady"
                @did-finish-load="handleXhsLoadState"
                @did-navigate="handleXhsLoadState"
                @did-navigate-in-page="handleXhsLoadState"
              ></webview>
              <div v-else class="xiaohongshu-webview-empty">正在准备小红书账号环境...</div>
            </div>
          </article>
        </section>
      </main>

      <footer class="suite-footer">
        <button class="footer-history" type="button" @click="openHistory">
          <IconGlyph name="history" />
          <span>历史记录</span>
        </button>
        <button v-if="visiblePage === 'trends'" class="download-report" type="button">
          <IconGlyph name="download" />
          <span>下载报告</span>
        </button>
      </footer>
    </section>

    <div v-if="historyDrawerOpen" class="drawer-scrim" @click.self="closeHistory">
      <aside class="history-drawer" aria-label="历史记录">
        <header>
          <h2>历史记录</h2>
          <button type="button" aria-label="关闭历史记录" @click="closeHistory">×</button>
        </header>
        <button v-for="item in historyRecords" :key="item.id" class="history-record" type="button">
          <strong>{{ item.title }}</strong>
          <span>{{ item.time }}</span>
        </button>
      </aside>
    </div>

    <SettingsDialog v-model:visible="settingsVisible" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch, type PropType } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SettingsDialog from '@components/SettingsDialog.vue'
import {
  generateCopywriting,
  generateSeoKeywords,
  type CopywritingItem,
  type SeoKeywordItem
} from '@api/generation'

type PageKey = 'trends' | 'seo' | 'copywriting' | 'publish' | 'accounts' | 'history'
type PrimaryNavPage = 'trends' | 'seo' | 'copywriting' | 'publish'
type IconName =
  | 'account'
  | 'alert'
  | 'arrowLeft'
  | 'arrowRight'
  | 'bell'
  | 'bulb'
  | 'chart'
  | 'check'
  | 'copy'
  | 'document'
  | 'download'
  | 'edit'
  | 'fire'
  | 'groups'
  | 'hash'
  | 'help'
  | 'history'
  | 'home'
  | 'image'
  | 'key'
  | 'link'
  | 'message'
  | 'refresh'
  | 'rocket'
  | 'search'
  | 'send'
  | 'settings'
  | 'spark'
  | 'trend'
  | 'upload'
  | 'user'

type SeoEntryRequest = {
  business: string
  features: string
  keywordCount: number
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

type XiaohongshuAccountStatus = 'pending' | 'saved'

type XiaohongshuAccount = {
  id: string
  platform: 'xiaohongshu'
  name: string
  partition: string
  status: XiaohongshuAccountStatus
  createdAt: number
  updatedAt: number
  lastLoginAt?: number
  lastSessionSaveAt?: number
  lastUrl?: string
  cookieCount: number
  localStorageCount: number
  sessionStorageCount: number
}

type XiaohongshuWebStorageSnapshot = {
  localStorage: Record<string, string>
  sessionStorage: Record<string, string>
  capturedAt: number
  url?: string
}

type XiaohongshuAccountView = XiaohongshuAccount & {
  active: boolean
  initial: string
  avatarClass: string
}

type XiaohongshuWebviewElement = HTMLElement & {
  canGoBack: () => boolean
  canGoForward: () => boolean
  executeJavaScript: <T = unknown>(code: string, userGesture?: boolean) => Promise<T>
  getURL: () => string
  goBack: () => void
  goForward: () => void
  loadURL: (url: string) => void
  reload: () => void
}

const SESSION_STORAGE_KEY = 'mdt-ai-agent.sessions.v1'
const XIAOHONGSHU_HOME_URL = 'https://creator.xiaohongshu.com'
const XIAOHONGSHU_LOGIN_URL = 'https://creator.xiaohongshu.com/login'
const XHS_AVATAR_CLASSES = ['avatar-lake', 'avatar-forest', 'avatar-sea']

const route = useRoute()
const router = useRouter()
const settingsVisible = ref(false)
const trendQuery = ref('')
const activePreviewTab = ref('小红书')
const copyLength = ref('中文案 (300-800字)')
const sessions = ref<ChatSession[]>(loadSessions())
const activeSessionId = ref(ensureInitialSessionId(sessions.value))
const xiaohongshuWebviewRef = ref<XiaohongshuWebviewElement | null>(null)
const xhsAccounts = ref<XiaohongshuAccount[]>([])
const activeXhsAccountId = ref('')
const xhsAccountLoading = ref(false)
const xhsSessionMessage = ref('正在读取小红书账号环境...')
const currentXhsUrl = ref(XIAOHONGSHU_HOME_URL)
const xhsStartUrls = reactive<Record<string, string>>({})
let xhsAutoSaveTimer: number | null = null
const restoredXhsStorageAccountIds = new Set<string>()

const routeToPage = computed<PageKey>(() => {
  const page = route.meta.page
  return typeof page === 'string' ? (page as PageKey) : 'trends'
})
const visiblePage = computed<PageKey>(() => (routeToPage.value === 'history' ? 'trends' : routeToPage.value))
const historyDrawerOpen = computed(() => routeToPage.value === 'history')
const activeNavPage = computed<PrimaryNavPage | 'accounts'>(() => {
  if (visiblePage.value === 'history') return 'trends'
  if (visiblePage.value === 'accounts') return 'accounts'
  return visiblePage.value as PrimaryNavPage
})
const activeXhsAccount = computed(() => {
  return xhsAccounts.value.find((account) => account.id === activeXhsAccountId.value) ?? xhsAccounts.value[0] ?? null
})
const activeXhsStartUrl = computed(() => {
  const account = activeXhsAccount.value
  if (!account) return XIAOHONGSHU_HOME_URL
  return xhsStartUrls[account.id] || account.lastUrl || XIAOHONGSHU_HOME_URL
})

const pageTitles: Record<PageKey, string> = {
  trends: '热点分析',
  seo: 'SEO关键词',
  copywriting: '宣传文案工具',
  publish: '发布中心',
  accounts: '账号管理',
  history: '热点分析'
}
const headerTitle = computed(() => pageTitles[routeToPage.value] ?? '热点分析')

const routeByPage: Record<PageKey, string> = {
  trends: '/trends',
  seo: '/seo',
  copywriting: '/copywriting',
  publish: '/publish',
  accounts: '/accounts',
  history: '/history'
}

const primaryNav: Array<{ page: PrimaryNavPage; label: string; icon: IconName }> = [
  { page: 'trends', label: '热点分析', icon: 'trend' },
  { page: 'seo', label: 'SEO关键词', icon: 'key' },
  { page: 'copywriting', label: '宣传文案工具', icon: 'edit' },
  { page: 'publish', label: '发布中心', icon: 'send' }
]

const iconPaths: Record<IconName, string[]> = {
  account: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4.5 20a7.5 7.5 0 0 1 15 0'],
  alert: ['M12 9v4', 'M12 17h.01', 'M10.3 4.2 2 2.8a2 2 0 0 0-3.4 0l-8.3 14.2A2 2 0 0 0 4.3 22h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0Z'],
  arrowLeft: ['M19 12H5', 'M12 19l-7-7 7-7'],
  arrowRight: ['M5 12h14', 'M12 5l7 7-7 7'],
  bell: ['M18 9a6 6 0 0 0-12 0c0 7-2 8-2 8h16s-2-1-2-8Z', 'M10 20a2 2 0 0 0 4 0'],
  bulb: ['M9 18h6', 'M10 22h4', 'M8.6 14.8A6 6 0 1 1 15.4 14.8c-.9.7-1.4 1.4-1.4 2.2h-4c0-.8-.5-1.5-1.4-2.2Z'],
  chart: ['M4 19V9', 'M10 19V5', 'M16 19v-7', 'M22 19H2'],
  check: ['M20 6 9 17l-5-5'],
  copy: ['M8 8h10v12H8z', 'M6 16H4V4h10v2'],
  document: ['M7 3h7l4 4v14H7V3Z', 'M14 3v5h5', 'M10 13h6', 'M10 17h4'],
  download: ['M12 3v12', 'M7 10l5 5 5-5', 'M5 21h14'],
  edit: ['M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4Z', 'M13.5 6.5l4 4'],
  fire: ['M12 22c4 0 7-2.8 7-6.4 0-2.7-1.4-5.1-3.5-6.5.1 2-1.1 3.2-2.5 3.7.4-2.9-.8-5.6-3.5-7.8.3 3.4-2.4 4.9-4 7.2C3.8 14 5 22 12 22Z'],
  groups: ['M17 21a5 5 0 0 0-10 0', 'M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M22 21a4 4 0 0 0-3-3.9', 'M2 21a4 4 0 0 1 3-3.9'],
  hash: ['M5 9h14', 'M5 15h14', 'M10 4 8 20', 'M16 4l-2 16'],
  help: ['M9.2 9a3 3 0 1 1 4.1 2.8c-.9.4-1.3 1-1.3 2.2', 'M12 18h.01'],
  history: ['M3 12a9 9 0 1 0 3-6.7', 'M3 4v5h5', 'M12 7v5l3 2'],
  home: ['M3 11 12 4l9 7', 'M5 10v10h14V10', 'M9 20v-6h6v6'],
  image: ['M4 5h16v14H4z', 'M8 13l2-2 3 3 2-2 3 4', 'M8 9h.01'],
  key: ['M15 7a4 4 0 1 0 2.8 6.8L22 18v3h-3v-2h-2v-2h-2l-1.8-1.8'],
  link: ['M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.2 1.2', 'M14 11a5 5 0 0 0-7.1 0l-2 2A5 5 0 0 0 12 20.1l1.2-1.2'],
  message: ['M5 5h14v10H8l-3 3V5Z', 'M8 9h8', 'M8 12h5'],
  refresh: ['M20 12a8 8 0 0 1-13.7 5.7', 'M4 12A8 8 0 0 1 17.7 6.3', 'M17 3v4h4', 'M7 21v-4H3'],
  rocket: ['M5 16c-1 1-1.5 2.5-1.5 4.5C5.5 20.5 7 20 8 19', 'M15 9l-6 6', 'M9 15l-1 4 4-1 7.5-7.5A8 8 0 0 0 21 3a8 8 0 0 0-7.5 1.5L6 12l3 3Z'],
  search: ['M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z', 'M21 21l-4.3-4.3'],
  send: ['M22 2 11 13', 'M22 2l-7 20-4-9-9-4 20-7Z'],
  settings: [
    'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z'
  ],
  spark: ['M12 3l1.7 4.4L18 9l-4.3 1.6L12 15l-1.7-4.4L6 9l4.3-1.6L12 3Z', 'M5 14l.8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8L5 14Z'],
  trend: ['M4 17l5-5 4 4 7-8', 'M14 8h6v6'],
  upload: ['M12 16V4', 'M7 9l5-5 5 5', 'M5 20h14'],
  user: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4.5 20a7.5 7.5 0 0 1 15 0']
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
            'stroke-width': '1.85',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round'
          })
        )
      )
  }
})

const trendKeywords = [
  { text: 'AIGC', selected: true },
  { text: '机器学习', selected: false },
  { text: '自动化营销', selected: false },
  { text: '大语言模型', selected: false }
]
const hotContent = [
  { title: '2024年AI智能体发展趋势预测', views: '10w+ 阅读' },
  { title: '如何利用AI提升工作效率？', views: '8.5w 阅读' }
]
const competitors = [
  { short: 'A', name: '品牌 A', value: 45, color: '#0058be' },
  { short: 'B', name: '品牌 B', value: 30, color: '#526069' }
]
const audienceTags = ['25-34岁', '科技爱好者', '营销从业者', '高消费力']
const marketingAdvice = [
  '结合 "AIGC" 和 "工作效率" 创作干货类文章，预计能获得较高转化。',
  '针对 25-34 岁核心受众，建议在周三晚上 8 点推送视频内容。',
  '品牌A近期声量上升，建议监控其 "自动化营销" 相关活动。'
]

const sampleSeoResults: SeoKeywordItem[] = [
  { keyword: '智能手表', search_volume_est: '50k-100k', difficulty: '中' },
  { keyword: '心率监测智能手表', search_volume_est: '1k-3k', difficulty: '低' },
  { keyword: 'GPS定位手表推荐', search_volume_est: '200-500', difficulty: '低' },
  { keyword: '防水50米智能手表', search_volume_est: '1k-3k', difficulty: '中' },
  { keyword: '智能手表怎么测心率', search_volume_est: '300-800', difficulty: '低' },
  { keyword: '运动智能手表gps定位准', search_volume_est: '100-300', difficulty: '中' },
  { keyword: '老人心率监测智能手表怎么样', search_volume_est: '100-300', difficulty: '低' },
  { keyword: '支持gps定位的智能手表推荐', search_volume_est: '50-200', difficulty: '低' },
  { keyword: '智能手表防水50米能游泳吗', search_volume_est: '300-800', difficulty: '中' },
  { keyword: '高性价比心率gps智能手表', search_volume_est: '300-800', difficulty: '中' }
]

const sampleCopyResults: CopywritingItem[] = [
  {
    title: '生成1',
    platform: '小红书',
    angle: '新品发布',
    content:
      '探索未来的营销智能：MDT Marketing 全新升级！\n\n在数字化快速发展的今天，如何让营销更精准、更高效？我们诚挚地向大家介绍 MDT Marketing 的最新版本。借助强大的 AI 驱动，我们为您提供深度的营销洞察，让每一次活动都能触达核心受众。\n\n核心亮点：\n1. 智能 SEO 关键词推荐，抓住流量密码。\n2. 自动化宣传文案生成，解放双手，创意无限。\n3. 多平台一键发布中心，效率提升 300%。\n\n无论您是初创团队还是成熟企业，MDT 都能成为您最得力的营销助手。',
    actual_keyword_count: 1
  },
  {
    title: '生成2',
    platform: '公众号',
    angle: '效率工具',
    content:
      '告别加班，营销人的效率工具测评来了。MDT Marketing 把热点分析、关键词生成、内容创作和发布管理放在同一个工作台中，帮助团队用更少的切换完成更多产出。\n\n从选题到发布，每一步都更清楚：先看趋势，再生成关键词，再把关键词转化为多平台文案，最后进入发布中心完成排期。',
    actual_keyword_count: 1
  }
]

const seoForm = reactive({
  business: '',
  features: '',
  keywordCount: 10
})
const seoLoading = ref(false)
const seoError = ref('')
const seoResults = ref<SeoKeywordItem[]>([])
const seoModel = ref('')
const displayedSeoResults = computed(() => (seoResults.value.length ? seoResults.value : sampleSeoResults))

const socialPlatforms = ['小红书', '公众号', '抖音', '哔哩哔哩']
const previewTabs = ['小红书', '公众号']
const copyForm = reactive({
  keyword: '',
  keywordOccurrences: 3,
  articleCount: 5,
  platforms: ['小红书', '公众号']
})
const copyLoading = ref(false)
const copyError = ref('')
const copyResults = ref<CopywritingItem[]>([])
const copyModel = ref('')
const displayedCopyResults = computed(() => (copyResults.value.length ? copyResults.value : sampleCopyResults))

const publishDraft = reactive({
  title: '',
  tags: ['#AI营销', '#数据分析', '#增长黑客'],
  content: '',
  schedule: 'now',
  platforms: ['公众号 (用户1)']
})
const editorTools = ['B', 'I', 'U', '—', '≡', '☷', '☰', '•', '1.']
const publishPlatforms: Array<{ name: string; failed: boolean; color: string; icon: IconName }> = [
  { name: '公众号 (用户1)', failed: false, color: 'green-logo', icon: 'message' },
  { name: '小红书 (用户1)', failed: false, color: 'blue-logo', icon: 'document' },
  { name: '小红书 (用户2)', failed: true, color: 'pink-logo', icon: 'document' }
]

const accounts = computed<XiaohongshuAccountView[]>(() =>
  xhsAccounts.value.map((account, index) => ({
    ...account,
    active: account.id === activeXhsAccount.value?.id,
    initial: getAccountInitial(account, index),
    avatarClass: XHS_AVATAR_CLASSES[index % XHS_AVATAR_CLASSES.length]
  }))
)

const historyRecords = computed(() => {
  const generated = sessions.value
    .flatMap((session) => session.entries)
    .sort((a, b) => b.createdAt - a.createdAt)
    .map((entry) => ({
      id: entry.id,
      title: entry.title,
      time: formatDateTime(entry.createdAt)
    }))

  if (generated.length) return generated
  return [
    { id: 'sample-1', title: 'AI 智能体', time: '2024-05-15 14:30' },
    { id: 'sample-2', title: '自动化营销工具', time: '2024-05-14 09:15' },
    { id: 'sample-3', title: '短视频带货数据', time: '2024-05-12 16:45' },
    { id: 'sample-4', title: '微信私域运营', time: '2024-05-10 11:20' }
  ]
})

function goToPage(page: PageKey | PrimaryNavPage) {
  router.push(routeByPage[page as PageKey])
}

function openSettings() {
  settingsVisible.value = true
}

function openHistory() {
  router.push(routeByPage.history)
}

function closeHistory() {
  router.push(routeByPage.trends)
}

async function loadXhsAccounts() {
  xhsAccountLoading.value = true
  try {
    const loadedAccounts = await window.api.xiaohongshuAccounts.list()
    xhsAccounts.value = loadedAccounts
    const activeAccount = loadedAccounts.find((account) => account.id === activeXhsAccountId.value) ?? loadedAccounts[0]
    activeXhsAccountId.value = activeAccount?.id ?? ''
    currentXhsUrl.value = activeAccount?.lastUrl || XIAOHONGSHU_HOME_URL
    xhsSessionMessage.value = activeAccount
      ? '请选择小红书账号登录；登录成功后会自动保存 Cookie 和 session'
      : '请先添加小红书账号'
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

async function addXhsAccount() {
  xhsAccountLoading.value = true
  try {
    const account = await window.api.xiaohongshuAccounts.create()
    xhsAccounts.value = [...xhsAccounts.value, account]
    activeXhsAccountId.value = account.id
    xhsStartUrls[account.id] = XIAOHONGSHU_LOGIN_URL
    currentXhsUrl.value = XIAOHONGSHU_LOGIN_URL
    xhsSessionMessage.value = '已创建独立登录环境，请在下方完成小红书登录'
    await nextTick()
    openXhsLogin()
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

function selectXhsAccount(accountId: string) {
  const account = xhsAccounts.value.find((item) => item.id === accountId)
  if (!account) return

  activeXhsAccountId.value = account.id
  currentXhsUrl.value = account.lastUrl || XIAOHONGSHU_HOME_URL
  xhsSessionMessage.value =
    account.status === 'saved'
      ? `已切换到 ${account.name}，登录态将从独立分区恢复`
      : `已切换到 ${account.name}，请登录后保存 Cookie 和 session`
}

function openXhsLogin() {
  navigateXhsWebview(XIAOHONGSHU_LOGIN_URL)
}

function openXhsHome() {
  navigateXhsWebview(XIAOHONGSHU_HOME_URL)
}

function goXhsBack() {
  const webview = getXhsWebview()
  if (webview?.canGoBack()) {
    webview.goBack()
  }
}

function goXhsForward() {
  const webview = getXhsWebview()
  if (webview?.canGoForward()) {
    webview.goForward()
  }
}

function refreshXhsWebview() {
  getXhsWebview()?.reload()
}

function navigateXhsWebview(url: string) {
  const account = activeXhsAccount.value
  if (account) {
    xhsStartUrls[account.id] = url
  }
  currentXhsUrl.value = url
  getXhsWebview()?.loadURL(url)
}

async function handleXhsDomReady() {
  syncCurrentXhsUrl()
  await restoreXhsWebStorage()
}

function handleXhsLoadState() {
  syncCurrentXhsUrl()
  if (looksLikeLoggedInXhsUrl(currentXhsUrl.value)) {
    scheduleAutoSaveXhsSession()
  }
}

function syncCurrentXhsUrl() {
  const url = getXhsWebview()?.getURL()
  if (url) {
    currentXhsUrl.value = url
  }
}

function scheduleAutoSaveXhsSession() {
  if (xhsAutoSaveTimer) {
    window.clearTimeout(xhsAutoSaveTimer)
  }

  xhsAutoSaveTimer = window.setTimeout(() => {
    void saveActiveXhsSession(false)
  }, 1200)
}

async function saveActiveXhsSession(manual = false) {
  const account = activeXhsAccount.value
  const webview = getXhsWebview()
  if (!account || !webview || xhsAccountLoading.value) return

  xhsAccountLoading.value = true
  try {
    syncCurrentXhsUrl()
    const [webStorage, title] = await Promise.all([collectXhsWebStorage(webview), readXhsDocumentTitle(webview)])
    const savedAccount = await window.api.xiaohongshuAccounts.saveSession({
      accountId: account.id,
      url: currentXhsUrl.value,
      title,
      webStorage
    })
    updateXhsAccount(savedAccount)
    xhsSessionMessage.value =
      savedAccount.status === 'saved'
        ? `${manual ? '已同步' : '已自动保存'} ${savedAccount.name} 的 Cookie/session`
        : '当前页面还没有可保存的登录态，请完成小红书登录'
  } catch (error) {
    xhsSessionMessage.value = getErrorMessage(error)
  } finally {
    xhsAccountLoading.value = false
  }
}

async function restoreXhsWebStorage() {
  const account = activeXhsAccount.value
  const webview = getXhsWebview()
  if (!account || !webview || restoredXhsStorageAccountIds.has(account.id)) return

  try {
    const snapshot = await window.api.xiaohongshuAccounts.getWebStorage(account.id)
    if (!snapshot) return

    await webview.executeJavaScript(
      `(() => {
        const restore = (target, data) => {
          Object.entries(data || {}).forEach(([key, value]) => {
            if (typeof key === 'string' && typeof value === 'string') {
              target.setItem(key, value)
            }
          })
        }
        restore(window.localStorage, ${JSON.stringify(snapshot.localStorage)})
        restore(window.sessionStorage, ${JSON.stringify(snapshot.sessionStorage)})
      })()`
    )
    restoredXhsStorageAccountIds.add(account.id)
  } catch (error) {
    console.warn('恢复小红书 Web Storage 失败', error)
  }
}

async function collectXhsWebStorage(webview: XiaohongshuWebviewElement): Promise<XiaohongshuWebStorageSnapshot> {
  try {
    return await webview.executeJavaScript<XiaohongshuWebStorageSnapshot>(
      `(() => {
        const dump = (target) => {
          const result = {}
          for (let index = 0; index < target.length; index += 1) {
            const key = target.key(index)
            if (key) result[key] = target.getItem(key) || ''
          }
          return result
        }
        return {
          localStorage: dump(window.localStorage),
          sessionStorage: dump(window.sessionStorage),
          capturedAt: Date.now(),
          url: window.location.href
        }
      })()`
    )
  } catch {
    return {
      localStorage: {},
      sessionStorage: {},
      capturedAt: Date.now(),
      url: currentXhsUrl.value
    }
  }
}

async function readXhsDocumentTitle(webview: XiaohongshuWebviewElement): Promise<string> {
  try {
    return await webview.executeJavaScript<string>('document.title || ""')
  } catch {
    return ''
  }
}

function getXhsWebview() {
  return xiaohongshuWebviewRef.value
}

function updateXhsAccount(account: XiaohongshuAccount) {
  xhsAccounts.value = xhsAccounts.value.map((item) => (item.id === account.id ? account : item))
}

function looksLikeLoggedInXhsUrl(url: string) {
  try {
    const parsed = new URL(url)
    return parsed.hostname.endsWith('xiaohongshu.com') && !parsed.pathname.includes('/login')
  } catch {
    return false
  }
}

function getAccountInitial(account: XiaohongshuAccount, index: number) {
  const name = account.name.replace(/^小红书账号\s*/u, '').trim()
  return (name[0] || `${index + 1}`).slice(0, 1)
}

function formatAccountStatus(account: XiaohongshuAccount) {
  if (account.status !== 'saved') return '未保存登录态'
  return `已保存 · ${formatDateTime(account.lastSessionSaveAt || account.updatedAt)}`
}

function analyzeTrends() {
  if (!trendQuery.value.trim()) {
    trendQuery.value = 'AI 智能体'
  }
}

async function submitSeo() {
  const validation = validateSeoForm()
  if (validation) {
    seoError.value = validation
    return
  }

  seoLoading.value = true
  seoError.value = ''
  const requestPayload: SeoEntryRequest = {
    business: seoForm.business.trim(),
    features: seoForm.features.trim(),
    keywordCount: Number(seoForm.keywordCount)
  }

  try {
    const response = await generateSeoKeywords({
      business_description: requestPayload.business,
      product_features: requestPayload.features,
      keyword_count: requestPayload.keywordCount,
      search_engines: ['百度', '360搜索', '必应']
    })
    seoResults.value = response.items
    seoModel.value = response.model
    appendSessionEntry({
      id: createId(),
      type: 'seo',
      title: truncateTitle(`SEO：${requestPayload.business}`),
      createdAt: Date.now(),
      request: requestPayload,
      response
    })
  } catch (error) {
    seoError.value = getErrorMessage(error)
  } finally {
    seoLoading.value = false
  }
}

function resetSeoResults() {
  seoResults.value = []
  seoModel.value = ''
}

async function prepareCopyFromKeyword(keyword: string) {
  copyForm.keyword = keyword
  copyForm.keywordOccurrences = Math.max(copyForm.keywordOccurrences, 1)
  await router.push(routeByPage.copywriting)
  await nextTick()
}

async function submitCopy() {
  const validation = validateCopyForm()
  if (validation) {
    copyError.value = validation
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
    copyResults.value = response.items
    copyModel.value = response.model
    appendSessionEntry({
      id: createId(),
      type: 'copy',
      title: truncateTitle(`文案：${requestPayload.keyword}`),
      createdAt: Date.now(),
      request: requestPayload,
      response
    })
  } catch (error) {
    copyError.value = getErrorMessage(error)
  } finally {
    copyLoading.value = false
  }
}

function validateSeoForm() {
  if (!seoForm.business.trim()) return '请输入业务描述'
  if (!seoForm.features.trim()) return '请输入产品特点'
  if (!Number.isFinite(Number(seoForm.keywordCount)) || seoForm.keywordCount < 1 || seoForm.keywordCount > 100) {
    return '关键词数量需在 1-100 之间'
  }
  return ''
}

function validateCopyForm() {
  if (!copyForm.keyword.trim()) return '请输入关键词'
  if (!copyForm.platforms.length) return '请至少选择一个社交媒体平台'
  if (!Number.isFinite(Number(copyForm.articleCount)) || copyForm.articleCount < 1) {
    return '生成篇数需大于 0'
  }
  return ''
}

function appendSessionEntry(entry: GenerationEntry) {
  const currentSession = sessions.value.find((session) => session.id === activeSessionId.value)
  const target = currentSession ?? createEmptySession()
  if (!currentSession) {
    sessions.value.unshift(target)
    activeSessionId.value = target.id
  }
  target.entries.push(entry)
  target.title = entry.title
  target.updatedAt = entry.createdAt
  saveSessions(sessions.value)
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

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as ChatSession[]
    if (!Array.isArray(parsed)) return []
    return parsed.filter((session) => Boolean(session?.id && session.title && Array.isArray(session.entries)))
  } catch (error) {
    console.warn('读取会话记录失败', error)
    return []
  }
}

function saveSessions(items: ChatSession[]) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(items))
}

function createId() {
  if (crypto.randomUUID) return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function truncateTitle(value: string) {
  return value.length > 18 ? `${value.slice(0, 18)}...` : value
}

function formatDateTime(timestamp: number) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) return error.message
  return '请求失败，请检查模型设置或稍后重试'
}

watch(headerTitle, (title) => {
  document.title = `${title} - MDT Marketing`
})

onMounted(() => {
  document.title = `${headerTitle.value} - MDT Marketing`
  void loadXhsAccounts()
})

onBeforeUnmount(() => {
  if (xhsAutoSaveTimer) {
    window.clearTimeout(xhsAutoSaveTimer)
  }
})
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  width: 100%;
  height: 100%;
  margin: 0;
}

:global(body) {
  overflow: hidden;
  background: #f8f9fa;
  color: #191c1d;
  font-family:
    Inter,
    'Microsoft YaHei',
    'PingFang SC',
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
}

:global(*) {
  box-sizing: border-box;
}

:global(button),
:global(input),
:global(textarea),
:global(select) {
  font: inherit;
}

.suite-shell {
  --primary: #0058be;
  --primary-strong: #004d99;
  --primary-soft: #d6e3ff;
  --surface: #ffffff;
  --surface-low: #f3f4f5;
  --surface-container: #edeeef;
  --surface-high: #e7e8e9;
  --surface-highest: #e1e3e4;
  --text: #191c1d;
  --text-muted: #424752;
  --outline: #c2c6d4;
  --outline-dark: #727783;
  --error: #ba1a1a;
  --success: #005c16;
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #f8f9fa;
  color: var(--text);
}

.suite-shell svg {
  width: 22px;
  height: 22px;
  flex: 0 0 22px;
}

.suite-sidebar {
  display: flex;
  width: 276px;
  height: 100vh;
  flex: 0 0 276px;
  flex-direction: column;
  border-right: 1px solid var(--outline);
  background: #ffffff;
  padding: 28px 14px 24px;
}

.suite-brand {
  padding: 0 18px;
  margin-bottom: 42px;
  color: var(--primary-strong);
  font-size: 28px;
  font-weight: 800;
  line-height: 34px;
}

.suite-nav {
  display: grid;
  gap: 10px;
}

.nav-secondary {
  margin-top: 26px;
  border-top: 1px solid var(--outline);
  padding-top: 26px;
}

.nav-item,
.help-center,
.icon-button,
.ghost-button,
.primary-action,
.link-action,
.publish-mini,
.account-actions button,
.primary-lite,
.publish-action,
.editor-toolbar button,
.footer-history,
.download-report,
.history-record {
  border: 0;
  cursor: pointer;
}

.nav-item {
  display: flex;
  min-height: 50px;
  align-items: center;
  gap: 16px;
  border-radius: 8px;
  background: transparent;
  color: #30363d;
  padding: 0 20px;
  text-align: left;
  transition:
    background-color 0.16s ease,
    color 0.16s ease;
}

.nav-item span {
  font-size: 18px;
  line-height: 24px;
}

.nav-item:hover {
  background: var(--surface-low);
}

.nav-item.active {
  background: #2f7dd2;
  color: #ffffff;
  font-weight: 700;
}

.help-center {
  display: flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: auto;
  border-radius: 8px;
  background: #edf4fb;
  color: var(--primary);
  font-weight: 700;
}

.suite-main {
  display: flex;
  min-width: 0;
  height: 100vh;
  flex: 1;
  flex-direction: column;
}

.suite-header {
  display: flex;
  height: 70px;
  flex: 0 0 70px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--outline);
  background: #ffffff;
  padding: 0 30px;
}

.suite-header h1 {
  margin: 0;
  color: #05070a;
  font-size: 24px;
  font-weight: 800;
  line-height: 32px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.icon-button,
.user-avatar {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 999px;
  background: transparent;
  color: #2f3a46;
}

.icon-button:hover {
  background: var(--surface-low);
  color: var(--primary);
}

.user-avatar {
  background: #d3e2ed;
  color: #56656e;
}

.suite-content {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
  padding: 30px;
}

.page-stack {
  display: grid;
  gap: 30px;
  width: min(100%, 1260px);
  margin: 0 auto;
}

.search-bar {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 18px;
  border: 1px solid var(--outline);
  border-radius: 12px;
  background: #ffffff;
  padding: 10px 12px 10px 28px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

.search-bar input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-size: 20px;
}

.search-bar button,
.primary-action,
.publish-action,
.download-report,
.publish-mini,
.primary-lite {
  background: var(--primary);
  color: #ffffff;
  font-weight: 800;
}

.search-bar button {
  min-width: 100px;
  min-height: 50px;
  border: 0;
  border-radius: 10px;
  cursor: pointer;
  font-size: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 30px;
}

.data-card,
.advice-card,
.hero-card,
.form-card,
.result-card,
.copy-settings-card,
.copy-preview-card,
.title-card,
.editor-card,
.publish-settings,
.account-strip,
.browser-frame {
  border: 1px solid var(--outline);
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

.data-card {
  min-height: 232px;
  padding: 30px;
}

.data-card.tall {
  min-height: 468px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
}

.card-title-row.with-divider {
  margin-bottom: 26px;
  border-bottom: 1px solid var(--outline);
  padding-bottom: 28px;
}

.card-title-row h2,
.advice-title h2,
.hero-card h2,
.result-card h2,
.copy-output h2,
.publish-settings h2 {
  margin: 0;
  color: #05070a;
  font-size: 22px;
  font-weight: 800;
  line-height: 28px;
}

.card-icon,
.hero-icon,
.plain-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 6px;
}

.plain-icon {
  color: var(--primary);
}

.card-icon.blue,
.hero-icon {
  background: #d6e3ff;
  color: var(--primary);
}

.card-icon.red {
  background: #ffdad6;
  color: var(--error);
}

.card-icon.gray {
  background: #eef3f6;
  color: #526069;
}

.card-icon.green {
  background: #d9f1dd;
  color: var(--success);
}

.keyword-pills,
.audience-tags,
.result-tags,
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.keyword-pills span,
.audience-tags span,
.result-tags span {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  border: 1px solid var(--outline);
  border-radius: 999px;
  background: var(--surface-high);
  color: #30363d;
  font-size: 18px;
  line-height: 22px;
  padding: 7px 18px;
}

.keyword-pills span.selected,
.result-tags span {
  border-color: #a9c7ff;
  background: #d6e3ff;
  color: var(--primary-strong);
}

.hot-list,
.competitor-list {
  display: grid;
  gap: 22px;
}

.hot-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--surface-highest);
  padding-bottom: 18px;
  font-size: 18px;
}

.hot-list-item strong {
  flex: 0 0 auto;
  color: var(--primary);
  font-weight: 700;
}

.competitor-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
}

.competitor-badge {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: var(--surface-highest);
  font-weight: 800;
}

.competitor-meta {
  display: grid;
  gap: 10px;
}

.competitor-meta div {
  display: flex;
  justify-content: space-between;
  font-size: 20px;
}

.progress-track {
  display: block;
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--surface-highest);
}

.progress-value {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.bar-chart {
  display: flex;
  height: 118px;
  align-items: flex-end;
  justify-content: center;
  gap: 14px;
  margin: 10px 0 28px;
}

.bar {
  display: block;
  width: 80px;
  border-radius: 3px 3px 0 0;
}

.bar-1 {
  height: 62px;
  background: #d6e3ff;
}

.bar-2 {
  height: 102px;
  background: var(--primary);
}

.bar-3 {
  height: 82px;
  background: #a9c7ff;
}

.bar-4 {
  height: 42px;
  background: var(--surface-highest);
}

.minor-heading {
  margin: 0 0 12px;
  color: var(--text-muted);
  font-size: 16px;
}

.audience-tags {
  margin-bottom: 18px;
}

.audience-tags span {
  min-height: 30px;
  border-radius: 4px;
  font-size: 15px;
  padding: 4px 10px;
}

.persona-box {
  border-radius: 8px;
  background: var(--surface-low);
  padding: 16px;
}

.persona-box span {
  color: var(--text-muted);
  font-weight: 700;
}

.persona-box p {
  margin: 8px 0 0;
  font-size: 18px;
  line-height: 28px;
}

.advice-card {
  position: relative;
  overflow: hidden;
  border-left: 5px solid var(--success);
  padding: 36px 40px;
}

.advice-title {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
}

.advice-title svg {
  color: var(--success);
}

.advice-card ul {
  display: grid;
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.advice-card li {
  display: flex;
  gap: 14px;
  font-size: 17px;
  line-height: 26px;
}

.advice-card li svg {
  width: 18px;
  height: 18px;
  margin-top: 3px;
  color: var(--primary);
}

.hero-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 22px;
  padding: 30px;
}

.hero-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
}

.hero-icon svg {
  width: 30px;
  height: 30px;
}

.hero-card p {
  margin: 6px 0 0;
  color: var(--text-muted);
}

.ghost-button {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  color: var(--text-muted);
  font-weight: 700;
  padding: 0 18px;
}

.ghost-button:hover {
  background: var(--surface-low);
  color: var(--primary);
}

.ghost-button.compact {
  min-height: 40px;
  min-width: 88px;
}

.form-card,
.result-card {
  padding: 30px;
}

.input-field,
.select-field {
  display: grid;
  gap: 10px;
  margin-bottom: 22px;
}

.input-field span,
.select-field span,
.range-field span,
.platform-grid legend,
.radio-row legend,
.publish-platform-list legend {
  color: #111827;
  font-size: 18px;
  font-weight: 600;
}

.input-field b {
  color: var(--error);
}

.input-field input,
.input-field textarea,
.select-field select {
  width: 100%;
  border: 1px solid var(--outline);
  border-radius: 8px;
  outline: none;
  background: #ffffff;
  color: var(--text);
  font-size: 17px;
  line-height: 24px;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.input-field input,
.select-field select {
  height: 48px;
  padding: 0 20px;
}

.input-field textarea {
  min-height: 120px;
  resize: vertical;
  padding: 18px 20px;
}

.input-field input:focus,
.input-field textarea:focus,
.select-field select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 88, 190, 0.12);
}

.count-field {
  position: relative;
}

.count-field em {
  position: absolute;
  right: 20px;
  bottom: 13px;
  color: var(--text-muted);
  font-style: normal;
}

.primary-action {
  display: inline-flex;
  width: 100%;
  min-height: 58px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 8px;
  font-size: 18px;
}

.primary-action:disabled {
  cursor: wait;
  opacity: 0.68;
}

.error-text {
  margin: -6px 0 16px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  padding: 10px 12px;
}

.result-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--outline);
  padding-bottom: 10px;
}

.result-toolbar div {
  display: flex;
  gap: 12px;
}

.result-card h3 {
  margin: 24px 0 18px;
  font-size: 18px;
}

.result-tags span {
  min-height: 34px;
  font-size: 15px;
  padding: 5px 14px;
}

.suite-table {
  width: 100%;
  margin-top: 22px;
  border-collapse: collapse;
}

.suite-table th,
.suite-table td {
  border-bottom: 1px solid var(--surface-highest);
  padding: 15px 20px;
  text-align: left;
  vertical-align: top;
}

.suite-table th {
  color: #111827;
  font-weight: 800;
}

.link-action {
  background: transparent;
  color: var(--primary);
  font-weight: 700;
}

.copy-page,
.publish-page {
  display: grid;
  width: min(100%, 1260px);
  grid-template-columns: minmax(360px, 476px) minmax(0, 1fr);
  gap: 30px;
  margin: 0 auto;
}

.copy-settings-card,
.copy-preview-card {
  min-height: calc(100vh - 170px);
}

.copy-settings-card {
  display: flex;
  flex-direction: column;
  padding: 30px;
}

.range-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin-bottom: 28px;
}

.range-field input {
  grid-column: 1 / -1;
  accent-color: var(--primary);
}

.platform-grid,
.radio-row,
.publish-platform-list {
  display: grid;
  gap: 14px;
  margin: 0 0 28px;
  border: 0;
  padding: 0;
}

.platform-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.platform-grid legend,
.publish-platform-list legend,
.radio-row legend {
  grid-column: 1 / -1;
  margin-bottom: 4px;
  padding: 0;
}

.platform-grid label {
  display: flex;
  min-height: 56px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  padding: 0 16px;
}

.platform-grid label.checked {
  border-color: var(--primary);
  background: #f0f6ff;
}

.platform-grid input,
.radio-row input,
.publish-platform-list input,
.agree-row input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
}

.stick-bottom {
  margin-top: auto;
}

.copy-preview-card {
  overflow: hidden;
}

.preview-tabs {
  display: flex;
  height: 66px;
  align-items: stretch;
  border-bottom: 1px solid var(--outline);
  background: var(--surface-low);
}

.preview-tab {
  display: flex;
  min-width: 150px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 0;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-weight: 700;
}

.preview-tab.active {
  border-bottom-color: var(--primary);
  color: var(--primary);
}

.copy-results {
  display: grid;
  gap: 30px;
  max-height: calc(100vh - 236px);
  overflow-y: auto;
  padding: 30px;
}

.copy-output {
  border: 1px solid var(--outline);
  border-radius: 12px;
  padding: 30px;
}

.copy-output-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 44px;
}

.publish-mini {
  display: inline-flex;
  min-width: 100px;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
}

.publish-mini svg {
  width: 18px;
  height: 18px;
}

.copy-output p {
  margin: 0;
  color: #111827;
  font-size: 20px;
  line-height: 34px;
  white-space: pre-wrap;
}

.publish-page {
  grid-template-columns: minmax(0, 1fr) 450px;
}

.editor-column {
  display: grid;
  gap: 20px;
}

.title-card,
.editor-card,
.publish-settings,
.publish-alert {
  padding: 30px;
}

.tag-row button {
  min-height: 32px;
  border: 0;
  border-radius: 999px;
  background: #d3e2ed;
  color: #56656e;
  cursor: pointer;
  font-weight: 700;
  padding: 4px 12px;
}

.tag-row button:first-child {
  background: var(--primary);
  color: #ffffff;
}

.editor-card {
  display: grid;
  grid-template-rows: 86px minmax(520px, 1fr);
  min-height: 810px;
  overflow: hidden;
  padding: 0;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 20px;
  border-bottom: 1px solid var(--outline);
  background: var(--surface-low);
  padding: 0 30px;
}

.editor-toolbar button {
  min-width: 28px;
  border-radius: 6px;
  background: transparent;
  color: #30363d;
  font-size: 20px;
  font-weight: 800;
}

.editor-toolbar span {
  width: 1px;
  height: 26px;
  background: var(--outline);
}

.editor-toolbar .ai-button {
  display: inline-flex;
  min-width: 150px;
  min-height: 50px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-left: auto;
  background: #00771f;
  color: #ffffff;
}

.editor-card textarea {
  width: 100%;
  height: 100%;
  min-height: 520px;
  border: 0;
  outline: none;
  resize: none;
  color: var(--text);
  font-size: 20px;
  line-height: 32px;
  padding: 36px 30px;
}

.publish-panel {
  display: grid;
  align-content: start;
  gap: 30px;
}

.radio-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.radio-row label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.publish-platform-list label {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  min-height: 78px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #f8fafc;
  padding: 12px 16px;
}

.publish-platform-list label.failed {
  border-color: #f3b4b4;
  background: #fff6f5;
}

.platform-logo {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 8px;
  color: #ffffff;
}

.green-logo {
  background: #22c55e;
}

.blue-logo {
  background: #0058be;
}

.pink-logo {
  background: #f77f9a;
}

.publish-platform-list strong,
.publish-platform-list em {
  display: block;
}

.publish-platform-list em {
  margin-top: 2px;
  color: var(--success);
  font-style: normal;
  font-size: 13px;
}

.publish-platform-list label.failed em {
  color: var(--error);
}

.publish-action {
  display: flex;
  min-height: 70px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 10px;
  font-size: 22px;
}

.publish-alert {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 16px;
  border: 1px solid #f2aaaa;
  border-radius: 12px;
  background: #ffd7d4;
  color: #93000a;
}

.publish-alert h3,
.publish-alert p {
  margin: 0;
}

.publish-alert p {
  margin-top: 4px;
  color: #8d3838;
}

.publish-alert div div {
  display: flex;
  justify-content: flex-end;
  gap: 18px;
  margin-top: 36px;
}

.publish-alert button {
  border: 0;
  background: transparent;
  color: #93000a;
  cursor: pointer;
  font-weight: 800;
}

.publish-alert button:last-child {
  display: inline-flex;
  min-height: 46px;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  background: #a60010;
  color: #ffffff;
  padding: 0 18px;
}

.suite-content.page-accounts {
  overflow: hidden;
  background: #f6f8fd;
  padding: 0;
}

.accounts-page {
  display: grid;
  height: 100%;
  min-height: 0;
  grid-template-rows: auto auto minmax(0, 1fr);
  background: #f5f7fc;
}

.account-strip {
  display: flex;
  align-items: center;
  gap: 42px;
  overflow-x: auto;
  border-bottom: 1px solid #cdd3df;
  background: #ffffff;
  padding: 10px 28px;
}

.account-chip {
  position: relative;
  display: inline-grid;
  min-width: 232px;
  height: 64px;
  grid-template-columns: 48px minmax(0, 1fr);
  grid-template-rows: 22px 18px;
  align-items: center;
  gap: 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #111827;
  cursor: pointer;
  padding: 0 18px;
}

.account-chip.active {
  background: #dbeafe;
}

.account-avatar {
  position: relative;
  display: grid;
  grid-row: 1 / 3;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  overflow: visible;
}

.account-avatar span {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  border-radius: inherit;
  background:
    radial-gradient(circle at 35% 25%, rgba(255, 255, 255, 0.9), transparent 24%),
    linear-gradient(135deg, #234f7e, #9fc5e8 48%, #f7d48f);
}

.account-avatar.avatar-forest span {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #263238, #5c8d6b 48%, #c7d69b);
}

.account-avatar.avatar-sea span {
  background:
    radial-gradient(circle at 35% 24%, rgba(255, 255, 255, 0.85), transparent 24%),
    linear-gradient(135deg, #1d3557, #4895ef 48%, #cfe8ff);
}

.account-avatar i {
  position: absolute;
  right: -6px;
  bottom: -2px;
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border: 2px solid #ffffff;
  border-radius: 50%;
  background: #ef1f35;
  color: #ffffff;
  font-size: 8px;
  font-style: normal;
  font-weight: 800;
  line-height: 1;
}

.account-chip strong {
  align-self: end;
  min-width: 0;
  overflow: hidden;
  color: #111827;
  font-size: 17px;
  font-weight: 500;
  line-height: 22px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-chip em {
  color: #6b7280;
  font-style: normal;
}

.account-chip small {
  align-self: start;
  min-width: 0;
  overflow: hidden;
  color: #6b7280;
  font-size: 12px;
  line-height: 16px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f6f8fd;
  padding: 24px 28px;
}

.account-actions button {
  min-height: 38px;
  border: 1px solid #c5ccd8;
  border-radius: 6px;
  background: #ffffff;
  color: #1f2937;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
  padding: 0 14px;
}

.account-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.account-actions .primary-lite {
  border-color: #1d68d8;
  background: #1d68d8;
  color: #ffffff;
}

.login-browser-frame {
  display: grid;
  min-height: 0;
  height: 100%;
  grid-template-rows: 30px 34px 30px minmax(0, 1fr);
  overflow: hidden;
  background: #ffffff;
}

.login-window-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #eef1f6;
  background: #ffffff;
  color: #4b5563;
  font-size: 12px;
  font-weight: 700;
  padding: 0 10px;
}

.login-window-title button {
  border: 0;
  background: transparent;
  color: #8b95a3;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.browser-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid #edf0f5;
  border-bottom: 1px solid #edf0f5;
  background: #ffffff;
  padding: 0 12px;
}

.browser-toolbar button {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border: 0;
  background: transparent;
  color: #9aa2ad;
  cursor: pointer;
  padding: 0;
}

.browser-toolbar svg {
  width: 14px;
  height: 14px;
}

.browser-toolbar span {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  border-radius: 16px;
  background: #f2f3f5;
  color: #9aa2ad;
  font-size: 12px;
  line-height: 22px;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 12px;
}

.browser-toolbar em,
.browser-toolbar small {
  max-width: 180px;
  overflow: hidden;
  color: #7d8794;
  font-size: 11px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.browser-toolbar small {
  color: #111827;
}

.notice-line {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #fff2be;
  background: #fffdf3;
  color: #f59e0b;
  font-size: 12px;
  line-height: 30px;
}

.notice-line strong {
  font-weight: 700;
}

.notice-line a {
  position: absolute;
  right: 14px;
  color: #477cf7;
  font-weight: 700;
  text-decoration: none;
}

.xiaohongshu-webview-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.xiaohongshu-webview {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: #ffffff;
}

.xiaohongshu-webview-empty {
  display: grid;
  flex: 1;
  min-height: 360px;
  place-items: center;
  color: #6b7280;
  font-size: 14px;
}

.suite-footer {
  display: flex;
  min-height: 56px;
  flex: 0 0 56px;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--outline);
  background: #ffffff;
  padding: 0 30px;
}

.footer-history {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  color: #30363d;
  font-size: 16px;
  font-weight: 700;
}

.download-report {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  padding: 0 18px;
}

.drawer-scrim {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(15, 23, 42, 0.48);
}

.history-drawer {
  position: absolute;
  inset: 0 0 0 auto;
  width: min(480px, 100vw);
  background: #ffffff;
  box-shadow: -20px 0 40px rgba(15, 23, 42, 0.16);
  padding: 26px 20px;
}

.history-drawer header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 36px;
}

.history-drawer h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.history-drawer header button {
  border: 0;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 32px;
}

.history-record {
  display: flex;
  width: 100%;
  min-height: 68px;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
  border: 1px solid var(--outline);
  border-radius: 8px;
  background: #ffffff;
  color: var(--text);
  padding: 0 20px;
  text-align: left;
}

.history-record span {
  color: #64748b;
  font-family: Consolas, 'JetBrains Mono', monospace;
  white-space: nowrap;
}

@media (max-width: 1120px) {
  .suite-sidebar {
    width: 240px;
    flex-basis: 240px;
  }

  .suite-brand {
    font-size: 24px;
  }

  .nav-item span {
    font-size: 16px;
  }

  .dashboard-grid,
  .copy-page,
  .publish-page {
    grid-template-columns: 1fr;
  }

  .copy-settings-card,
  .copy-preview-card {
    min-height: auto;
  }

  .publish-page {
    width: min(100%, 900px);
  }
}

@media (max-width: 760px) {
  .suite-shell {
    display: block;
    overflow-y: auto;
  }

  .suite-sidebar {
    position: relative;
    width: 100%;
    height: auto;
    min-height: 0;
  }

  .suite-main {
    height: auto;
  }

  .suite-content {
    overflow: visible;
    padding: 20px;
  }

  .suite-header {
    position: sticky;
    top: 0;
    z-index: 10;
    height: auto;
    min-height: 68px;
  }

  .hero-card {
    grid-template-columns: 1fr;
  }

  .platform-grid,
  .radio-row {
    grid-template-columns: 1fr;
  }

  .login-hero {
    grid-template-columns: 1fr;
  }
}
</style>
