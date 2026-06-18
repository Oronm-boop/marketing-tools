import request from '@utils/request'

export type SeoKeywordPayload = {
  business_description: string
  product_features: string
  keyword_count: number
  search_engines: string[]
}

export type SeoKeywordItem = {
  keyword: string
  search_volume_est: string
  difficulty: string
}

export type SeoKeywordResponse = {
  items: SeoKeywordItem[]
  model: string
}

export type CopywritingPayload = {
  keyword: string
  keyword_repeat_count: number
  article_count: number
  platform_styles: string[]
}

export type CopywritingItem = {
  title: string
  platform: string
  angle: string
  content: string
  actual_keyword_count: number
}

export type CopywritingResponse = {
  items: CopywritingItem[]
  model: string
}

export type PublishImagePromptPayload = {
  title: string
  content: string
  tags: string[]
}

export type PublishImagePromptItem = {
  title: string
  description: string
  keywords: string[]
}

export type PublishImagePromptResponse = {
  items: PublishImagePromptItem[]
  model: string
}

export type ImageGenerationPayload = {
  prompt: string
  width?: number
  height?: number
  batch_size?: number
}

export type ImageGenerationTaskResponse = {
  prompt_id: string
  status: 'queued'
}

export type GeneratedImageFile = {
  filename: string
  subfolder: string
  type: string
  url: string
}

export type ImageGenerationStatusResponse = {
  prompt_id: string
  status: 'pending' | 'running' | 'success' | 'failed'
  message: string
  image: GeneratedImageFile | null
}

export const generateSeoKeywords = (data: SeoKeywordPayload) => {
  return request({
    url: '/seo-keywords',
    method: 'post',
    data
  }) as unknown as Promise<SeoKeywordResponse>
}

export const generateCopywriting = (data: CopywritingPayload) => {
  return request({
    url: '/copywriting',
    method: 'post',
    data
  }) as unknown as Promise<CopywritingResponse>
}

export const generatePublishImagePrompts = (data: PublishImagePromptPayload) => {
  return request({
    url: '/image-generation/prompts',
    method: 'post',
    data
  }) as unknown as Promise<PublishImagePromptResponse>
}

export const createImageGenerationTask = (data: ImageGenerationPayload) => {
  return request({
    url: '/image-generation/tasks',
    method: 'post',
    data
  }) as unknown as Promise<ImageGenerationTaskResponse>
}

export const getImageGenerationTask = (promptId: string) => {
  return request({
    url: `/image-generation/tasks/${encodeURIComponent(promptId)}`,
    method: 'get'
  }) as unknown as Promise<ImageGenerationStatusResponse>
}
