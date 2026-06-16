import { ElectronAPI } from '@electron-toolkit/preload'

type XiaohongshuAccountStatus = 'pending' | 'saved'

type XiaohongshuAccount = {
  id: string
  platform: 'xiaohongshu'
  name: string
  nickname?: string
  avatarUrl?: string
  profileCapturedAt?: number
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

type XiaohongshuProfileSnapshot = {
  nickname?: string
  avatarUrl?: string
  capturedAt?: number
}

type XiaohongshuAccountsAPI = {
  list: () => Promise<XiaohongshuAccount[]>
  create: (payload?: { name?: string }) => Promise<XiaohongshuAccount>
  saveSession: (payload: {
    accountId: string
    url?: string
    title?: string
    profile?: XiaohongshuProfileSnapshot
    webStorage?: XiaohongshuWebStorageSnapshot
  }) => Promise<XiaohongshuAccount>
  getWebStorage: (accountId: string) => Promise<XiaohongshuWebStorageSnapshot | null>
}

declare global {
  interface Window {
    electron: ElectronAPI
    api: {
      xiaohongshuAccounts: XiaohongshuAccountsAPI
    }
  }
}
