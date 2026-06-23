import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchModelSettings, saveModelSettings } from '@api/settings'
import type { ModelProvider, ModelSettingsRead, ModelSettingsWrite } from '@api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const provider = ref<ModelProvider>('local')

  const localModelBaseUrl = ref('http://192.168.0.105:8081/v1')
  const localModelName = ref('Qwen3.6-35B-A3B-UD-Q8_K_XL')

  const ollamaBaseUrl = ref('http://localhost:11434/v1')
  const ollamaModel = ref('llama3.2')

  const qwenApiKey = ref('')
  const qwenBaseUrl = ref('https://dashscope.aliyuncs.com/compatible-mode/v1')
  const qwenModel = ref('qwen-plus')

  const comfyuiBaseUrl = ref('http://192.168.0.122:8188')
  const comfyuiVideoBaseUrl = ref('http://192.168.0.122:8188')

  const loading = ref(false)
  const saving = ref(false)

  function applySettings(data: ModelSettingsRead) {
    provider.value = data.provider
    localModelBaseUrl.value = data.local_model_base_url
    localModelName.value = data.local_model_name
    ollamaBaseUrl.value = data.ollama_base_url
    ollamaModel.value = data.ollama_model
    qwenApiKey.value = data.qwen_api_key
    qwenBaseUrl.value = data.qwen_base_url
    qwenModel.value = data.qwen_model
    comfyuiBaseUrl.value = data.comfyui_base_url
    comfyuiVideoBaseUrl.value = data.comfyui_video_base_url
  }

  async function load() {
    loading.value = true
    try {
      const data = await fetchModelSettings()
      applySettings(data)
    } finally {
      loading.value = false
    }
  }

  async function save(payload: ModelSettingsWrite) {
    saving.value = true
    try {
      const data = await saveModelSettings(payload)
      applySettings(data)
    } finally {
      saving.value = false
    }
  }

  return {
    provider,
    localModelBaseUrl,
    localModelName,
    ollamaBaseUrl,
    ollamaModel,
    qwenApiKey,
    qwenBaseUrl,
    qwenModel,
    comfyuiBaseUrl,
    comfyuiVideoBaseUrl,
    loading,
    saving,
    load,
    save,
  }
})
