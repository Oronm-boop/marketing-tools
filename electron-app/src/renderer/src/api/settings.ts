import request from '@utils/request'

export type ModelProvider = 'local' | 'ollama' | 'bailian'

export interface ModelSettingsRead {
  provider: ModelProvider
  local_model_base_url: string
  local_model_name: string
  ollama_base_url: string
  ollama_model: string
  qwen_api_key: string
  qwen_base_url: string
  qwen_model: string
  comfyui_base_url: string
  comfyui_video_base_url: string
  knowledge_base_url: string
  browser_automation_show_window: boolean
}

export interface ModelSettingsWrite {
  provider: ModelProvider
  local_model_base_url?: string
  local_model_name?: string
  ollama_base_url?: string
  ollama_model?: string
  qwen_api_key?: string
  qwen_base_url?: string
  qwen_model?: string
  comfyui_base_url?: string
  comfyui_video_base_url?: string
  knowledge_base_url?: string
  browser_automation_show_window?: boolean
}

export function fetchModelSettings(): Promise<ModelSettingsRead> {
  return request.get('/model-settings')
}

export function saveModelSettings(data: ModelSettingsWrite): Promise<ModelSettingsRead> {
  return request.put('/model-settings', data)
}
