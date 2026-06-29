import request from '@utils/request'

export type KnowledgeBaseReference = {
  id: string
  name: string
}

export type KnowledgeBaseDocument = {
  id: string
  name: string
  size: number
  uploadedAt: number
}

export type KnowledgeBase = KnowledgeBaseReference & {
  documentCount: number
  updatedAt: string
  documents: KnowledgeBaseDocument[]
}

export type KnowledgeBaseDocumentsResponse = {
  documents: KnowledgeBaseDocument[]
}

export const listKnowledgeBases = () => {
  return request({
    url: '/knowledge-bases',
    method: 'get'
  }) as unknown as Promise<KnowledgeBase[]>
}

export const createKnowledgeBase = (name: string) => {
  return request({
    url: '/knowledge-bases',
    method: 'post',
    data: { name }
  }) as unknown as Promise<KnowledgeBase>
}

export const deleteKnowledgeBase = (knowledgeBaseId: string) => {
  return request({
    url: `/knowledge-bases/${encodeURIComponent(knowledgeBaseId)}`,
    method: 'delete'
  }) as unknown as Promise<{ ok: boolean }>
}

export const listKnowledgeBaseDocuments = (knowledgeBaseId: string) => {
  return request({
    url: `/knowledge-bases/${encodeURIComponent(knowledgeBaseId)}/documents`,
    method: 'get'
  }) as unknown as Promise<KnowledgeBaseDocumentsResponse>
}

export const uploadKnowledgeBaseDocuments = (knowledgeBaseId: string, files: File[]) => {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file, file.name)
  })

  return request({
    url: `/knowledge-bases/${encodeURIComponent(knowledgeBaseId)}/documents`,
    method: 'post',
    data: formData
  }) as unknown as Promise<KnowledgeBaseDocumentsResponse>
}

export const deleteKnowledgeBaseDocument = (knowledgeBaseId: string, documentId: string) => {
  return request({
    url: `/knowledge-bases/${encodeURIComponent(knowledgeBaseId)}/documents/${encodeURIComponent(documentId)}`,
    method: 'delete'
  }) as unknown as Promise<KnowledgeBaseDocumentsResponse>
}
