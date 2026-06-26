import { app, shell, BrowserWindow, screen, dialog } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { startBackend, stopBackend } from './backend'
import { verifyLicense } from './license'
import { registerXiaohongshuAccountIpc } from './xiaohongshuAccounts'
import { registerXiaohongshuPublisherIpc } from './xiaohongshuPublisher'

const PREFERRED_WINDOW_WIDTH = 1984
const PREFERRED_WINDOW_HEIGHT = 1274
const MIN_WINDOW_WIDTH = 720
const MIN_WINDOW_HEIGHT = 480
const WINDOW_SCREEN_MARGIN = 24
const ZOOM_BASE_WIDTH = 1024
const ZOOM_BASE_HEIGHT = 720
const MIN_ZOOM_FACTOR = 0.55
const MAX_ZOOM_FACTOR = 1

let mainWindow: BrowserWindow | null = null

function createWindow(): BrowserWindow {
  const { width, height } = getInitialWindowSize()

  // Create the browser window.
  const window = new BrowserWindow({
    width,
    height,
    minWidth: Math.min(MIN_WINDOW_WIDTH, width),
    minHeight: Math.min(MIN_WINDOW_HEIGHT, height),
    center: true,
    show: false,
    autoHideMenuBar: true,
    title: '',
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#ffffff',
      symbolColor: '#0b1c30'
    },
    icon,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      webviewTag: true,
      enablePreferredSizeMode: true
    }
  })

  mainWindow = window
  installWindowZoomBehavior(window)

  window.on('ready-to-show', () => {
    applyWindowZoom(window)
    window.show()
  })

  window.on('closed', () => {
    if (mainWindow === window) {
      mainWindow = null
    }
  })

  window.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    window.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    window.loadFile(join(__dirname, '../renderer/index.html'))
  }

  return window
}

function getInitialWindowSize(): { width: number; height: number } {
  const { width: workAreaWidth, height: workAreaHeight } = screen.getPrimaryDisplay().workAreaSize
  const availableWidth = Math.max(1, workAreaWidth - WINDOW_SCREEN_MARGIN)
  const availableHeight = Math.max(1, workAreaHeight - WINDOW_SCREEN_MARGIN)

  return {
    width: Math.min(PREFERRED_WINDOW_WIDTH, availableWidth),
    height: Math.min(PREFERRED_WINDOW_HEIGHT, availableHeight)
  }
}

function installWindowZoomBehavior(window: BrowserWindow): void {
  let zoomTimer: ReturnType<typeof setTimeout> | null = null

  const scheduleZoomUpdate = (): void => {
    if (zoomTimer) {
      clearTimeout(zoomTimer)
    }
    zoomTimer = setTimeout(() => {
      zoomTimer = null
      applyWindowZoom(window)
    }, 80)
  }

  const handleDisplayChange = (): void => {
    scheduleZoomUpdate()
  }

  window.webContents.on('did-finish-load', () => applyWindowZoom(window))
  window.on('resize', scheduleZoomUpdate)
  window.on('maximize', scheduleZoomUpdate)
  window.on('unmaximize', scheduleZoomUpdate)
  window.on('restore', scheduleZoomUpdate)
  window.on('enter-full-screen', scheduleZoomUpdate)
  window.on('leave-full-screen', scheduleZoomUpdate)

  screen.on('display-added', handleDisplayChange)
  screen.on('display-removed', handleDisplayChange)
  screen.on('display-metrics-changed', handleDisplayChange)

  window.on('closed', () => {
    if (zoomTimer) {
      clearTimeout(zoomTimer)
      zoomTimer = null
    }
    screen.off('display-added', handleDisplayChange)
    screen.off('display-removed', handleDisplayChange)
    screen.off('display-metrics-changed', handleDisplayChange)
  })
}

function applyWindowZoom(window: BrowserWindow): void {
  if (window.isDestroyed()) return

  const { width, height } = window.getContentBounds()
  const zoomFactor = getWindowZoomFactor(width, height)
  window.webContents.setZoomFactor(zoomFactor)
}

function getWindowZoomFactor(width: number, height: number): number {
  const widthZoomFactor = width / ZOOM_BASE_WIDTH
  const heightZoomFactor = height / ZOOM_BASE_HEIGHT
  const zoomFactor = Math.min(widthZoomFactor, heightZoomFactor, MAX_ZOOM_FACTOR)

  return Math.max(MIN_ZOOM_FACTOR, Number(zoomFactor.toFixed(2)))
}

const gotSingleInstanceLock = app.requestSingleInstanceLock()

if (!gotSingleInstanceLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (!mainWindow) return
    if (mainWindow.isMinimized()) {
      mainWindow.restore()
    }
    mainWindow.focus()
  })

  // This method will be called when Electron has finished
  // initialization and is ready to create browser windows.
  // Some APIs can only be used after this event occurs.
  app.whenReady().then(async () => {
    // Set app user model id for windows
    electronApp.setAppUserModelId('com.market.sales')

    // Default open or close DevTools by F12 in development
    // and ignore CommandOrControl + R in production.
    // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
    app.on('browser-window-created', (_, window) => {
      optimizer.watchWindowShortcuts(window)
    })

    if (is.dev) {
      console.info('[license] development mode detected, skipping license validation')
    } else {
      const licenseResult = await verifyLicense()
      if (!licenseResult.ok) {
        const reason = licenseResult.reason ?? '未知原因'
        const logHint = licenseResult.logFile ? `\n\n日志位置：${licenseResult.logFile}` : ''
        console.error(`[license] 授权校验失败: ${reason}`)
        dialog.showErrorBox('License 验证失败', `未检测到有效授权，应用将退出。\n\n原因：${reason}${logHint}`)
        app.exit(1)
        return
      }
    }

    registerXiaohongshuAccountIpc()
    registerXiaohongshuPublisherIpc()
    await startBackend()
    createWindow()

    app.on('activate', function () {
      // On macOS it's common to re-create a window in the app when the
      // dock icon is clicked and there are no other windows open.
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })
}

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopBackend()
})

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.
