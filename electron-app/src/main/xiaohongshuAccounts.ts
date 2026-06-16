import { app, ipcMain, safeStorage, session } from 'electron'
import { randomUUID } from 'crypto'
import { mkdir, readFile, writeFile } from 'fs/promises'
import { dirname, join } from 'path'
import type { Cookie } from 'electron'

const STORE_FILE_NAME = 'xiaohongshu-accounts.json'
const STORE_VERSION = 1
const DEFAULT_ACCOUNT_ID = 'xhs-default'
const DEFAULT_PARTITION = 'persist:xiaohongshu'

type XhsAccountStatus = 'pending' | 'saved'

type WebStorageSnapshot = {
  localStorage: Record<string, string>
  sessionStorage: Record<string, string>
  capturedAt: number
  url?: string
}

type ProtectedString = {
  mode: 'safeStorage' | 'plain'
  value: string
}

type XhsAccountRecord = {
  id: string
  platform: 'xiaohongshu'
  name: string
  nickname?: string
  avatarUrl?: string
  profileCapturedAt?: number
  partition: string
  status: XhsAccountStatus
  createdAt: number
  updatedAt: number
  lastLoginAt?: number
  lastSessionSaveAt?: number
  lastUrl?: string
  cookieCount: number
  localStorageCount: number
  sessionStorageCount: number
  encryptedCookies?: ProtectedString
  encryptedWebStorage?: ProtectedString
}

type XhsAccountPublic = Omit<XhsAccountRecord, 'encryptedCookies' | 'encryptedWebStorage'>

type XhsAccountStore = {
  version: number
  accounts: XhsAccountRecord[]
}

type CreateAccountPayload = {
  name?: string
}

type SaveSessionPayload = {
  accountId: string
  url?: string
  title?: string
  profile?: XhsProfileSnapshot
  webStorage?: WebStorageSnapshot
}

type XhsProfileSnapshot = {
  nickname?: string
  avatarUrl?: string
  capturedAt?: number
}

export function registerXiaohongshuAccountIpc(): void {
  ipcMain.handle('xhs-accounts:list', async () => {
    const store = await readAccountStore()
    return store.accounts.map(toPublicAccount)
  })

  ipcMain.handle('xhs-accounts:create', async (_event, payload?: CreateAccountPayload) => {
    const store = await readAccountStore()
    const now = Date.now()
    const id = `xhs-${randomUUID()}`
    const account: XhsAccountRecord = {
      id,
      platform: 'xiaohongshu',
      name: normalizeAccountName(payload?.name) || `小红书账号 ${store.accounts.length + 1}`,
      partition: `persist:${id}`,
      status: 'pending',
      createdAt: now,
      updatedAt: now,
      cookieCount: 0,
      localStorageCount: 0,
      sessionStorageCount: 0
    }

    store.accounts.push(account)
    await writeAccountStore(store)
    return toPublicAccount(account)
  })

  ipcMain.handle('xhs-accounts:save-session', async (_event, payload: SaveSessionPayload) => {
    if (!payload?.accountId) {
      throw new Error('缺少小红书账号 ID')
    }

    const store = await readAccountStore()
    const account = store.accounts.find((item) => item.id === payload.accountId)
    if (!account) {
      throw new Error('未找到小红书账号')
    }

    const accountSession = session.fromPartition(account.partition)
    const cookies = await accountSession.cookies.get({})
    const xhsCookies = cookies.filter(isXiaohongshuCookie)
    await accountSession.cookies.flushStore()
    await flushStorageData(accountSession)

    const webStorage = normalizeWebStorage(payload.webStorage, payload.url)
    const profile = normalizeProfile(payload.profile)
    const now = Date.now()
    account.updatedAt = now
    account.lastSessionSaveAt = now
    account.lastUrl = payload.url || account.lastUrl
    account.cookieCount = xhsCookies.length
    account.localStorageCount = webStorage ? Object.keys(webStorage.localStorage).length : account.localStorageCount
    account.sessionStorageCount = webStorage ? Object.keys(webStorage.sessionStorage).length : account.sessionStorageCount
    account.status = xhsCookies.length > 0 || account.localStorageCount > 0 || account.sessionStorageCount > 0 ? 'saved' : 'pending'

    if (account.status === 'saved') {
      account.lastLoginAt = now
    }

    if (payload.title) {
      account.name = deriveAccountName(account.name, payload.title)
    }

    if (profile) {
      account.nickname = profile.nickname || account.nickname
      account.avatarUrl = profile.avatarUrl || account.avatarUrl
      account.profileCapturedAt = profile.capturedAt
    }

    account.encryptedCookies = protectString(JSON.stringify(xhsCookies.map(serializeCookie)))
    if (webStorage) {
      account.encryptedWebStorage = protectString(JSON.stringify(webStorage))
    }

    await writeAccountStore(store)
    return toPublicAccount(account)
  })

  ipcMain.handle('xhs-accounts:get-web-storage', async (_event, accountId: string) => {
    const store = await readAccountStore()
    const account = store.accounts.find((item) => item.id === accountId)
    if (!account?.encryptedWebStorage) return null

    const raw = unprotectString(account.encryptedWebStorage)
    if (!raw) return null

    try {
      return JSON.parse(raw) as WebStorageSnapshot
    } catch {
      return null
    }
  })
}

async function readAccountStore(): Promise<XhsAccountStore> {
  try {
    const raw = await readFile(getStorePath(), 'utf8')
    const parsed = JSON.parse(raw) as Partial<XhsAccountStore>
    return ensureDefaultAccount({
      version: STORE_VERSION,
      accounts: Array.isArray(parsed.accounts) ? parsed.accounts.map(normalizeAccountRecord).filter(isAccountRecord) : []
    })
  } catch {
    const store = ensureDefaultAccount({ version: STORE_VERSION, accounts: [] })
    await writeAccountStore(store)
    return store
  }
}

async function writeAccountStore(store: XhsAccountStore): Promise<void> {
  const storePath = getStorePath()
  await mkdir(dirname(storePath), { recursive: true })
  await writeFile(storePath, JSON.stringify({ ...store, version: STORE_VERSION }, null, 2), 'utf8')
}

function ensureDefaultAccount(store: XhsAccountStore): XhsAccountStore {
  if (store.accounts.length) return store

  const now = Date.now()
  store.accounts.push({
    id: DEFAULT_ACCOUNT_ID,
    platform: 'xiaohongshu',
    name: '小红书账号 1',
    partition: DEFAULT_PARTITION,
    status: 'pending',
    createdAt: now,
    updatedAt: now,
    cookieCount: 0,
    localStorageCount: 0,
    sessionStorageCount: 0
  })
  return store
}

function normalizeAccountRecord(record: Partial<XhsAccountRecord>): XhsAccountRecord | null {
  if (!record?.id || !record.partition) return null

  const now = Date.now()
  const nickname = normalizeAccountName(record.nickname)
  const avatarUrl = normalizeAvatarUrl(record.avatarUrl)

  return {
    id: String(record.id),
    platform: 'xiaohongshu',
    name: normalizeAccountName(record.name) || '小红书账号',
    nickname: nickname || undefined,
    avatarUrl: avatarUrl || undefined,
    profileCapturedAt: Number(record.profileCapturedAt) || undefined,
    partition: String(record.partition),
    status: record.status === 'saved' ? 'saved' : 'pending',
    createdAt: Number(record.createdAt) || now,
    updatedAt: Number(record.updatedAt) || now,
    lastLoginAt: Number(record.lastLoginAt) || undefined,
    lastSessionSaveAt: Number(record.lastSessionSaveAt) || undefined,
    lastUrl: typeof record.lastUrl === 'string' ? record.lastUrl : undefined,
    cookieCount: Number(record.cookieCount) || 0,
    localStorageCount: Number(record.localStorageCount) || 0,
    sessionStorageCount: Number(record.sessionStorageCount) || 0,
    encryptedCookies: record.encryptedCookies,
    encryptedWebStorage: record.encryptedWebStorage
  }
}

function isAccountRecord(record: XhsAccountRecord | null): record is XhsAccountRecord {
  return Boolean(record)
}

function toPublicAccount(account: XhsAccountRecord): XhsAccountPublic {
  const { encryptedCookies, encryptedWebStorage, ...publicAccount } = account
  void encryptedCookies
  void encryptedWebStorage
  return publicAccount
}

function getStorePath(): string {
  return join(app.getPath('userData'), STORE_FILE_NAME)
}

function normalizeAccountName(value?: string): string {
  return typeof value === 'string' ? value.trim().slice(0, 32) : ''
}

function normalizeProfile(profile?: XhsProfileSnapshot): XhsProfileSnapshot | null {
  if (!profile) return null

  const nickname = normalizeAccountName(profile.nickname)
  const avatarUrl = normalizeAvatarUrl(profile.avatarUrl)
  if (!nickname && !avatarUrl) return null

  return {
    nickname,
    avatarUrl,
    capturedAt: Number(profile.capturedAt) || Date.now()
  }
}

function normalizeAvatarUrl(value?: string): string {
  if (typeof value !== 'string') return ''

  const url = value.trim()
  if (!url) return ''
  if (url.startsWith('//')) return `https:${url}`.slice(0, 512)
  return /^https?:\/\//i.test(url) ? url.slice(0, 512) : ''
}

function deriveAccountName(currentName: string, pageTitle: string): string {
  const title = pageTitle.replace(/\s+/g, ' ').trim()
  if (!title || /^小红书账号\s*\d+$/u.test(currentName)) return currentName
  if (title.includes('登录')) return currentName
  return title.slice(0, 32)
}

function normalizeWebStorage(snapshot?: WebStorageSnapshot, url?: string): WebStorageSnapshot | null {
  if (!snapshot) return null

  return {
    localStorage: normalizeStorageRecord(snapshot.localStorage),
    sessionStorage: normalizeStorageRecord(snapshot.sessionStorage),
    capturedAt: Number(snapshot.capturedAt) || Date.now(),
    url: snapshot.url || url
  }
}

function normalizeStorageRecord(value: unknown): Record<string, string> {
  if (!value || typeof value !== 'object') return {}

  return Object.entries(value as Record<string, unknown>).reduce<Record<string, string>>((storage, [key, item]) => {
    if (typeof item === 'string') {
      storage[key] = item
    }
    return storage
  }, {})
}

function isXiaohongshuCookie(cookie: Cookie): boolean {
  const domain = cookie.domain ?? ''
  return /(^|\.)xiaohongshu\.com$/i.test(domain.replace(/^\./, '')) || domain.includes('xiaohongshu.com')
}

function serializeCookie(cookie: Cookie): Cookie {
  return { ...cookie }
}

function protectString(value: string): ProtectedString {
  if (safeStorage.isEncryptionAvailable()) {
    return {
      mode: 'safeStorage',
      value: safeStorage.encryptString(value).toString('base64')
    }
  }

  return {
    mode: 'plain',
    value
  }
}

function unprotectString(payload: ProtectedString): string {
  if (payload.mode === 'safeStorage') {
    return safeStorage.decryptString(Buffer.from(payload.value, 'base64'))
  }

  return payload.value
}

async function flushStorageData(accountSession: Electron.Session): Promise<void> {
  const flushableSession = accountSession as Electron.Session & {
    flushStorageData?: () => void | Promise<void>
  }

  if (flushableSession.flushStorageData) {
    await Promise.resolve(flushableSession.flushStorageData())
  }
}
