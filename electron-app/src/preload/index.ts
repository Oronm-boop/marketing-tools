import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  xiaohongshuAccounts: {
    list: () => ipcRenderer.invoke('xhs-accounts:list'),
    create: (payload?: { name?: string }) => ipcRenderer.invoke('xhs-accounts:create', payload),
    delete: (accountId: string) => ipcRenderer.invoke('xhs-accounts:delete', accountId),
    saveSession: (payload: {
      accountId: string
      url?: string
      title?: string
      profile?: {
        nickname?: string
        avatarUrl?: string
        capturedAt?: number
        isLoggedIn?: boolean
      }
      webStorage?: {
        localStorage: Record<string, string>
        sessionStorage: Record<string, string>
        capturedAt: number
        url?: string
      }
    }) => ipcRenderer.invoke('xhs-accounts:save-session', payload),
    getWebStorage: (accountId: string) => ipcRenderer.invoke('xhs-accounts:get-web-storage', accountId)
  },

  xiaohongshuPublisher: {
    publishImageText: (payload: {
      accountId: string
      title: string
      content: string
      tags: string[]
      imageUrls: string[]
    }) => ipcRenderer.invoke('xhs-publisher:publish-image-text', payload)
  }

}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}
