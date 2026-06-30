<template>
  <Teleport to="body">
    <div v-if="visible" class="settings-overlay">
      <div class="settings-dialog" role="dialog" aria-modal="true" aria-labelledby="settings-title">
        <!-- 标题栏 -->
        <div class="dialog-header">
          <div class="header-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <div>
            <h2 id="settings-title">模型设置</h2>
            <p>配置大模型、ComfyUI 和知识库服务地址</p>
          </div>
          <button class="close-btn" type="button" aria-label="关闭" @click="handleClose">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <aside class="settings-sidebar">
            <!-- 提供商选择 -->
            <div class="section provider-section">
              <label class="section-label">大模型类型</label>
              <div class="provider-tabs" role="radiogroup" aria-label="大模型类型">
                <button v-for="opt in providerOptions" :key="opt.value" type="button" role="radio" :aria-checked="form.provider === opt.value" class="provider-tab" :class="{ active: form.provider === opt.value }" @click="form.provider = opt.value">
                  <span class="provider-tab-icon" aria-hidden="true" v-html="opt.icon" />
                  <span class="provider-tab-text">
                    <span class="provider-tab-label">{{ opt.label }}</span>
                    <span class="provider-tab-desc">{{ opt.desc }}</span>
                  </span>
                </button>
              </div>
            </div>
          </aside>

          <div class="settings-content">
            <!-- ComfyUI 配置 -->
            <div class="section fields-section comfyui-section">
              <div class="section-title">
                <span class="section-dot dot-comfyui" aria-hidden="true"></span>
                ComfyUI 服务配置
              </div>
              <div class="field-row two-col">
                <div class="field">
                  <label class="field-label" for="comfyui-image-ip">生图 IP 地址</label>
                  <input id="comfyui-image-ip" v-model="comfyuiImageHost" type="text" class="field-input" placeholder="127.0.0.1" autocomplete="off" spellcheck="false" />
                </div>
                <div class="field">
                  <label class="field-label" for="comfyui-image-port">端口</label>
                  <input id="comfyui-image-port" v-model="comfyuiImagePort" type="number" class="field-input" placeholder="8188" min="1" max="65535" />
                </div>
              </div>
              <div class="url-preview">
                <span class="url-preview-label">生图地址：</span>
                <code>{{ comfyuiBaseUrl }}</code>
              </div>
              <div class="field-row two-col">
                <div class="field">
                  <label class="field-label" for="comfyui-video-ip">生视频 IP 地址</label>
                  <input id="comfyui-video-ip" v-model="comfyuiVideoHost" type="text" class="field-input" placeholder="127.0.0.1" autocomplete="off" spellcheck="false" />
                </div>
                <div class="field">
                  <label class="field-label" for="comfyui-video-port">端口</label>
                  <input id="comfyui-video-port" v-model="comfyuiVideoPort" type="number" class="field-input" placeholder="8188" min="1" max="65535" />
                </div>
              </div>
              <div class="url-preview">
                <span class="url-preview-label">生视频地址：</span>
                <code>{{ comfyuiVideoBaseUrl }}</code>
              </div>
            </div>

            <!-- 知识库配置 -->
            <div class="section fields-section">
              <div class="section-title">
                <span class="section-dot dot-knowledge" aria-hidden="true"></span>
                知识库服务配置
              </div>
              <div class="field-row two-col">
                <div class="field">
                  <label class="field-label" for="knowledge-base-ip">服务 IP 地址</label>
                  <input id="knowledge-base-ip" v-model="knowledgeBaseHost" type="text" class="field-input" placeholder="127.0.0.1" autocomplete="off" spellcheck="false" />
                </div>
                <div class="field">
                  <label class="field-label" for="knowledge-base-port">端口</label>
                  <input id="knowledge-base-port" v-model="knowledgeBasePort" type="number" class="field-input" placeholder="20090" min="1" max="65535" />
                </div>
              </div>
              <div class="url-preview">
                <span class="url-preview-label">知识库地址：</span>
                <code>{{ knowledgeBaseUrl }}</code>
              </div>
            </div>

            <!-- 浏览器自动化配置 -->
            <div class="section fields-section automation-section">
              <div class="section-title">
                <span class="section-dot dot-automation" aria-hidden="true"></span>
                浏览器自动化
              </div>
              <label class="switch-row" for="browser-automation-show-window">
                <span class="switch-copy">
                  <span class="switch-title">显示后台操作界面</span>
                  <span class="switch-desc">开启后，发布时显示自动化浏览器窗口</span>
                </span>
                <input id="browser-automation-show-window" v-model="browserAutomationShowWindow" class="switch-input" type="checkbox" />
                <span class="switch-control" aria-hidden="true"></span>
              </label>
            </div>

            <!-- 局域网AI一体机 配置 -->
            <div v-if="form.provider === 'local'" class="section fields-section">
              <div class="section-title">
                <span class="section-dot dot-local" aria-hidden="true"></span>
                局域网 AI 一体机配置
              </div>
              <div class="field-row two-col">
                <div class="field">
                  <label class="field-label" for="local-ip">服务器 IP 地址</label>
                  <input id="local-ip" v-model="localIp" type="text" class="field-input" placeholder="127.0.0.1" autocomplete="off" spellcheck="false" />
                </div>
                <div class="field">
                  <label class="field-label" for="local-port">端口</label>
                  <input id="local-port" v-model="localPort" type="number" class="field-input" placeholder="8081" min="1" max="65535" />
                </div>
              </div>
              <div class="field">
                <label class="field-label" for="local-model">模型名称</label>
                <input id="local-model" v-model="form.localModelName" type="text" class="field-input" placeholder="Qwen3.6-35B-A3B-UD-Q8_K_XL" autocomplete="off" spellcheck="false" />
              </div>
              <div class="url-preview">
                <span class="url-preview-label">接口地址：</span>
                <code>{{ localBaseUrl }}</code>
              </div>
            </div>

            <!-- 云端大模型 配置 -->
            <div v-if="form.provider === 'bailian'" class="section fields-section">
              <div class="section-title">
                <span class="section-dot dot-cloud" aria-hidden="true"></span>
                云端大模型配置
              </div>
              <div class="field">
                <label class="field-label" for="qwen-api-key">
                  API Key
                  <span class="required-mark" aria-hidden="true">*</span>
                </label>
                <div class="input-with-toggle">
                  <input id="qwen-api-key" v-model="form.qwenApiKey" :type="showApiKey ? 'text' : 'password'" class="field-input" placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx" autocomplete="new-password" spellcheck="false" />
                  <button type="button" class="toggle-visibility" :aria-label="showApiKey ? '隐藏 API Key' : '显示 API Key'" @click="showApiKey = !showApiKey">
                    <svg v-if="!showApiKey" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                      <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                    </svg>
                  </button>
                </div>
                <span v-if="isKeyMasked" class="field-hint">已保存 API Key，如需修改请重新输入</span>
              </div>
              <div class="field">
                <label class="field-label" for="qwen-base-url">服务商接口地址</label>
                <input id="qwen-base-url" v-model="form.qwenBaseUrl" type="url" class="field-input" placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1" autocomplete="off" spellcheck="false" />
                <span class="field-hint">阿里云百炼默认地址，如使用其他兼容 OpenAI 的服务商请修改</span>
              </div>
              <div class="field">
                <label class="field-label" for="qwen-model">模型名称</label>
                <input id="qwen-model" v-model="form.qwenModel" type="text" class="field-input" placeholder="qwen-plus" autocomplete="off" spellcheck="false" />
              </div>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMsg" class="error-banner" role="alert">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8" />
            <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
          </svg>
          {{ errorMsg }}
        </div>

        <!-- 成功提示 -->
        <div v-if="successMsg" class="success-banner" role="status">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          {{ successMsg }}
        </div>

        <!-- 底部操作 -->
        <div class="dialog-footer">
          <button type="button" class="btn-secondary" :disabled="settingsStore.saving" @click="handleClose">取消</button>
          <button type="button" class="btn-primary" :disabled="settingsStore.saving" @click="handleSave">
            <span v-if="settingsStore.saving" class="spinner" aria-hidden="true"></span>
            {{ settingsStore.saving ? '保存中…' : '保存设置' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useSettingsStore } from '@store/useSettingsStore'
import type { ModelProvider } from '@api/settings'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'update:visible', value: boolean): void }>()

const settingsStore = useSettingsStore()

const showApiKey = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

type VisibleModelProvider = Exclude<ModelProvider, 'ollama'>

interface FormState {
  provider: VisibleModelProvider
  localModelName: string
  qwenApiKey: string
  qwenBaseUrl: string
  qwenModel: string
}

const form = reactive<FormState>({
  provider: 'local',
  localModelName: '',
  qwenApiKey: '',
  qwenBaseUrl: '',
  qwenModel: '',
})

const localIp = ref('127.0.0.1')
const localPort = ref('8081')
const comfyuiImageHost = ref('127.0.0.1')
const comfyuiImagePort = ref('8188')
const comfyuiVideoHost = ref('127.0.0.1')
const comfyuiVideoPort = ref('8188')
const knowledgeBaseHost = ref('127.0.0.1')
const knowledgeBasePort = ref('20090')
const browserAutomationShowWindow = ref(false)

const MASKED = '********'
const isKeyMasked = computed(() => form.qwenApiKey === MASKED)

const localBaseUrl = computed(() => `http://${localIp.value || '127.0.0.1'}:${localPort.value || '8081'}/v1`)
const comfyuiBaseUrl = computed(() => `http://${comfyuiImageHost.value.trim()}:${comfyuiImagePort.value.trim()}`)
const comfyuiVideoBaseUrl = computed(() => `http://${comfyuiVideoHost.value.trim()}:${comfyuiVideoPort.value.trim()}`)
const knowledgeBaseUrl = computed(() => `http://${knowledgeBaseHost.value.trim() || '127.0.0.1'}:${knowledgeBasePort.value.trim() || '20090'}`)

function parseBaseUrl(url: string): { host: string; port: string } {
  try {
    const parsed = new URL(url)
    return {
      host: parsed.hostname,
      port: parsed.port || (parsed.protocol === 'https:' ? '443' : '80'),
    }
  } catch {
    return { host: '', port: '' }
  }
}

function isValidPort(port: string): boolean {
  const value = Number(port)
  return Number.isInteger(value) && value >= 1 && value <= 65535
}

function validateServiceEndpoint(label: string, host: string, port: string): string {
  if (!host.trim()) {
    return `请输入 ${label} 的 IP 地址`
  }
  if (!isValidPort(port)) {
    return `请输入 ${label} 的有效端口（1-65535）`
  }
  return ''
}

function syncFromStore() {
  form.provider = settingsStore.provider === 'bailian' ? 'bailian' : 'local'
  form.localModelName = settingsStore.localModelName
  form.qwenApiKey = settingsStore.qwenApiKey
  form.qwenBaseUrl = settingsStore.qwenBaseUrl
  form.qwenModel = settingsStore.qwenModel

  const localParsed = parseBaseUrl(settingsStore.localModelBaseUrl)
  localIp.value = localParsed.host || '127.0.0.1'
  localPort.value = localParsed.port || '8081'

  const comfyuiParsed = parseBaseUrl(settingsStore.comfyuiBaseUrl)
  comfyuiImageHost.value = comfyuiParsed.host || '127.0.0.1'
  comfyuiImagePort.value = comfyuiParsed.port || '8188'

  const comfyuiVideoParsed = parseBaseUrl(settingsStore.comfyuiVideoBaseUrl)
  comfyuiVideoHost.value = comfyuiVideoParsed.host || '127.0.0.1'
  comfyuiVideoPort.value = comfyuiVideoParsed.port || '8188'

  const knowledgeBaseParsed = parseBaseUrl(settingsStore.knowledgeBaseUrl)
  knowledgeBaseHost.value = knowledgeBaseParsed.host || '127.0.0.1'
  knowledgeBasePort.value = knowledgeBaseParsed.port || '20090'
  browserAutomationShowWindow.value = settingsStore.browserAutomationShowWindow
}

watch(
  () => props.visible,
  async (val) => {
    if (val) {
      errorMsg.value = ''
      successMsg.value = ''
      showApiKey.value = false
      if (!settingsStore.loading) {
        try {
          await settingsStore.load()
        } catch (e: unknown) {
          errorMsg.value = e instanceof Error ? e.message : '加载模型设置失败，请确认后端服务已启动'
        }
      }
      syncFromStore()
    }
  },
)

function handleClose() {
  emit('update:visible', false)
}

async function handleSave() {
  errorMsg.value = ''
  successMsg.value = ''

  if (form.provider === 'bailian' && !form.qwenApiKey) {
    errorMsg.value = '请输入云端大模型的 API Key'
    return
  }

  const comfyuiValidationError = validateServiceEndpoint('ComfyUI 生图服务', comfyuiImageHost.value, comfyuiImagePort.value) || validateServiceEndpoint('ComfyUI 生视频服务', comfyuiVideoHost.value, comfyuiVideoPort.value)
  if (comfyuiValidationError) {
    errorMsg.value = comfyuiValidationError
    return
  }

  const knowledgeBaseValidationError = validateServiceEndpoint('知识库服务', knowledgeBaseHost.value, knowledgeBasePort.value)
  if (knowledgeBaseValidationError) {
    errorMsg.value = knowledgeBaseValidationError
    return
  }

  try {
    await settingsStore.save({
      provider: form.provider,
      local_model_base_url: localBaseUrl.value,
      local_model_name: form.localModelName,
      qwen_api_key: form.qwenApiKey,
      qwen_base_url: form.qwenBaseUrl,
      qwen_model: form.qwenModel,
      comfyui_base_url: comfyuiBaseUrl.value,
      comfyui_video_base_url: comfyuiVideoBaseUrl.value,
      knowledge_base_url: knowledgeBaseUrl.value,
      browser_automation_show_window: browserAutomationShowWindow.value,
    })
    successMsg.value = '设置已保存，下次请求将使用新配置'
    setTimeout(() => {
      successMsg.value = ''
      handleClose()
    }, 1800)
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : '保存失败，请重试'
  }
}

const providerOptions: Array<{
  value: VisibleModelProvider
  label: string
  desc: string
  icon: string
}> = [
  {
    value: 'local',
    label: '局域网 AI 一体机',
    desc: '内网自托管大模型',
    icon: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="3" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M8 21h8M12 17v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    </svg>`,
  },
  {
    value: 'bailian',
    label: '云端大模型',
    desc: '阿里云等在线服务',
    icon: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
  },
]
</script>

<style scoped>
.settings-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  padding: 24px;
}

.settings-dialog {
  width: 100%;
  max-width: 980px;
  max-height: 86vh;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow:
    0 10px 40px rgba(15, 23, 42, 0.14),
    0 2px 8px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* ---- 标题栏 ---- */
.dialog-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 24px 24px 20px;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 1;
  border-radius: 16px 16px 0 0;
}

.header-icon {
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #eff4ff;
  color: #2563eb;
  display: grid;
  place-items: center;
}

.header-icon svg {
  width: 22px;
  height: 22px;
}

.dialog-header > div:nth-child(2) {
  flex: 1;
  min-width: 0;
}

.dialog-header h2 {
  margin: 0 0 2px;
  font-size: 17px;
  font-weight: 700;
  color: #0b1c30;
  line-height: 24px;
}

.dialog-header p {
  margin: 0;
  font-size: 13px;
  color: #434655;
  line-height: 18px;
}

.close-btn {
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: transparent;
  color: #737686;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition:
    background 0.15s,
    color 0.15s;
}

.close-btn:hover {
  background: #eff4ff;
  color: #0b1c30;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.dialog-body {
  min-height: 0;
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: 224px minmax(0, 1fr);
  overflow: hidden;
}

.settings-sidebar {
  min-width: 0;
  border-right: 1px solid #e2e8f0;
  background: #fbfdff;
}

.settings-sidebar .section {
  border-bottom: none;
  padding: 20px 18px;
}

.settings-content {
  min-width: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-content: start;
  overflow-y: auto;
}

.settings-content .section {
  min-width: 0;
}

.comfyui-section {
  grid-column: 1 / -1;
}

.automation-section {
  grid-column: 1 / -1;
}

/* ---- Section ---- */
.section {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.section:last-of-type {
  border-bottom: none;
}

.section-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #434655;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

/* ---- 提供商选项卡 ---- */
.provider-tabs {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.provider-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  background: #f8f9ff;
  color: #434655;
  cursor: pointer;
  padding: 13px 12px;
  text-align: left;
  transition:
    border-color 0.15s,
    background 0.15s,
    color 0.15s,
    box-shadow 0.15s;
}

.provider-tab:hover {
  border-color: #b4c5ff;
  background: #eff4ff;
  color: #004ac6;
}

.provider-tab.active {
  border-color: #2563eb;
  background: #eff4ff;
  color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.provider-tab-icon {
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
}

.provider-tab-icon :deep(svg) {
  width: 23px;
  height: 23px;
}

.provider-tab-text {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.provider-tab-label {
  font-size: 12px;
  font-weight: 700;
  line-height: 16px;
}

.provider-tab-desc {
  font-size: 11px;
  color: inherit;
  opacity: 0.75;
  line-height: 14px;
}

/* ---- 配置表单 ---- */
.fields-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #0b1c30;
}

.section-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 8px;
}

.dot-local {
  background: #2563eb;
}

.dot-cloud {
  background: #fd761a;
}

.dot-comfyui {
  background: #2563eb;
}

.dot-knowledge {
  background: #0f766e;
}

.dot-automation {
  background: #7c3aed;
}

.field-row.two-col {
  display: grid;
  grid-template-columns: 1fr 120px;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #0b1c30;
  line-height: 18px;
}

.required-mark {
  color: #dc2626;
  margin-left: 2px;
}

.field-input {
  height: 40px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  background: #f8f9ff;
  color: #0b1c30;
  font-size: 14px;
  padding: 0 12px;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: #2563eb;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.field-hint {
  font-size: 12px;
  color: #94a3b8;
  line-height: 16px;
}

.field-hint code {
  font-family: 'Consolas', 'JetBrains Mono', monospace;
  font-size: 11px;
  background: #f1f5f9;
  border-radius: 3px;
  padding: 1px 4px;
  color: #475569;
}

.switch-row {
  position: relative;
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  background: #f8f9ff;
  padding: 12px 14px;
  cursor: pointer;
  box-sizing: border-box;
}

.switch-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.switch-title {
  font-size: 13px;
  font-weight: 600;
  color: #0b1c30;
  line-height: 18px;
}

.switch-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 16px;
}

.switch-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.switch-control {
  position: relative;
  flex: 0 0 42px;
  width: 42px;
  height: 24px;
  border-radius: 999px;
  background: #cbd5e1;
  transition:
    background 0.15s,
    box-shadow 0.15s;
}

.switch-control::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.24);
  transition: transform 0.15s;
}

.switch-input:checked + .switch-control {
  background: #2563eb;
}

.switch-input:checked + .switch-control::after {
  transform: translateX(18px);
}

.switch-input:focus-visible + .switch-control {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.16);
}

.url-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f1f5f9;
  font-size: 12px;
  color: #434655;
  flex-wrap: wrap;
}

.url-preview-label {
  font-weight: 600;
  white-space: nowrap;
}

.url-preview code {
  font-family: 'Consolas', 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #334155;
  word-break: break-all;
}

/* API Key 显示/隐藏 */
.input-with-toggle {
  position: relative;
  display: flex;
}

.input-with-toggle .field-input {
  padding-right: 40px;
}

.toggle-visibility {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 40px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: color 0.15s;
}

.toggle-visibility:hover {
  color: #475569;
}

.toggle-visibility svg {
  width: 16px;
  height: 16px;
}

/* ---- 消息横幅 ---- */
.error-banner,
.success-banner {
  margin: 0 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 18px;
  padding: 10px 14px;
}

.error-banner {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.success-banner {
  background: #dcfce7;
  color: #007e37;
  border: 1px solid #bbf7d0;
}

.error-banner svg,
.success-banner svg {
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
}

/* ---- 底部按钮 ---- */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid #e2e8f0;
  position: static;
  background: #ffffff;
  border-radius: 0 0 16px 16px;
}

.btn-secondary,
.btn-primary {
  height: 38px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  padding: 0 20px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition:
    background 0.15s,
    opacity 0.15s;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #004ac6;
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载旋转 */
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex: 0 0 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .settings-overlay {
    padding: 12px;
  }

  .settings-dialog {
    max-width: 100%;
    max-height: 92vh;
  }

  .dialog-body {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .settings-sidebar {
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .settings-content {
    grid-template-columns: 1fr;
    overflow: visible;
  }

  .comfyui-section {
    grid-column: auto;
  }

  .automation-section {
    grid-column: auto;
  }

  .provider-tabs {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .provider-tab {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .field-row.two-col {
    grid-template-columns: minmax(0, 1fr) 104px;
  }
}
</style>
