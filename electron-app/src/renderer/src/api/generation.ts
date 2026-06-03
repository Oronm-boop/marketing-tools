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
