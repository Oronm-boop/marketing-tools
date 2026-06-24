import { app, ipcMain, BrowserWindow } from 'electron'
import { copyFile, mkdtemp, readFile, rm, stat } from 'fs/promises'
import { appendFileSync, createWriteStream, mkdirSync } from 'fs'
import { request as httpRequest } from 'http'
import { request as httpsRequest } from 'https'
import { tmpdir } from 'os'
import { dirname, extname, isAbsolute, join, resolve } from 'path'

// ─── Types ───────────────────────────────────────────────────────────────────

type PublishImageTextPayload = {
  accountId: string
  title: string
  content: string
  tags: string[]
  imageUrls: string[]
}

type PublishResult = {
  status: 'published' | 'failed'
  message?: string
}

type XhsAccountMinimal = {
  id: string
  partition: string
  status: string
}

type CdpDomNode = {
  nodeId: number
  nodeName: string
  localName?: string
  nodeValue?: string
  attributes?: string[]
  children?: CdpDomNode[]
  shadowRoots?: CdpDomNode[]
}

type CdpBoxModel = {
  model: {
    content: number[]
    border: number[]
  }
}

type PreparedPublishImages = {
  paths: string[]
  tempDir: string
}

// ─── Constants ───────────────────────────────────────────────────────────────

const STORE_FILE_NAME = 'xiaohongshu-accounts.json'
const XHS_PUBLISH_URL = 'https://creator.xiaohongshu.com/publish/publish?source=official'
const XHS_USER_AGENT =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

const PAGE_LOAD_TIMEOUT_MS = 30_000
const UPLOAD_TIMEOUT_MS = 120_000
const ELEMENT_WAIT_TIMEOUT_MS = 15_000
const PUBLISH_CONFIRM_TIMEOUT_MS = 30_000
const POLL_INTERVAL_MS = 500

/** 仅开发环境显示 RPA 浏览器窗口和 DevTools，方便调试 DOM 选择器 */
const RPA_DEBUG = !app.isPackaged && process.env['XHS_RPA_DEBUG'] !== '0'

/** 日志文件路径 — 写入到项目根目录的 xiaohongshu-publish-debug.log */
const LOG_FILE_PATH = (() => {
  // 开发模式: process.cwd() 通常是 electron-app 目录，日志写到上级目录
  // 生产模式: 使用 app 可执行文件所在目录
  const base = resolve(process.cwd(), '..')
  return join(base, 'xiaohongshu-publish-debug.log')
})()
let logFileReady = false

// ─── IPC Registration ────────────────────────────────────────────────────────

export function registerXiaohongshuPublisherIpc(): void {
  ipcMain.handle(
    'xhs-publisher:publish-image-text',
    async (_event, payload: PublishImageTextPayload) => {
      return publishImageText(payload)
    }
  )
}

// ─── Main Publish Flow ───────────────────────────────────────────────────────

async function publishImageText(payload: PublishImageTextPayload): Promise<PublishResult> {
  validatePayload(payload)

  const partition = await resolveAccountPartition(payload.accountId)
  const win = createRpaWindow(partition)

  try {
    return await runPublishSteps(win, payload)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    log(`发布失败: ${message}`)
    return { status: 'failed', message }
  } finally {
    // 调试模式下延迟关闭窗口，方便观察
    if (RPA_DEBUG) {
      await delay(5000)
    }
    if (!win.isDestroyed()) {
      win.close()
    }
  }
}

async function runPublishSteps(
  win: BrowserWindow,
  payload: PublishImageTextPayload
): Promise<PublishResult> {
  // ── Step 1: 导航到发布页 ──────────────────────────────────────────────────
  log('[1/7] 导航到小红书创作者平台发布页')
  await loadUrl(win, XHS_PUBLISH_URL)
  await delay(2500)

  // ── Step 2: 确保进入图文模式 ──────────────────────────────────────────────
  log('[2/7] 切换到图文发布模式')
  await ensureImageTextTab(win)
  await delay(1500)

  const preparedImages = await preparePublishImageFiles(payload.imageUrls)

  try {
    // ── Step 3: 上传图片 (CDP) ────────────────────────────────────────────────
    log(`[3/7] 上传 ${preparedImages.paths.length} 张图片`)
    await uploadImagesViaCDP(win, preparedImages.paths)

    // ── Step 4: 等待上传完成 ──────────────────────────────────────────────────
    log('[4/7] 等待图片上传完成')
    await waitForUploadComplete(win, preparedImages.paths.length)
    await delay(1000)

    // ── Step 5: 填写标题 ──────────────────────────────────────────────────────
    log(`[5/7] 填写标题: "${payload.title.slice(0, 20)}${payload.title.length > 20 ? '...' : ''}"`)
    await fillTitle(win, payload.title)
    await delay(800)

    // ── Step 6: 填写正文 ──────────────────────────────────────────────────────
    log(`[6/7] 填写正文 (${payload.content.length} 字)`)
    await fillContent(win, payload.content)
    await delay(800)

    // ── Step 6.5: 添加话题标签 ────────────────────────────────────────────────
    if (payload.tags.length > 0) {
      log(`[6.5/7] 添加 ${payload.tags.length} 个话题标签`)
      await addTags(win, payload.tags)
      await delay(800)
    }

    // ── Step 7: 点击发布 ──────────────────────────────────────────────────────
    log('[7/7] 点击发布按钮')
    await clickPublishButton(win)
  } finally {
    await cleanupGeneratedImageFiles(preparedImages.tempDir)
  }

  // ── 等待发布结果 ──────────────────────────────────────────────────────────
  log('等待发布结果确认...')
  await waitForPublishConfirmation(win)

  log('✅ 小红书图文发布成功')
  return { status: 'published' }
}

async function preparePublishImageFiles(imageReferences: string[]): Promise<PreparedPublishImages> {
  const tempDir = await mkdtemp(join(tmpdir(), 'mdt-xhs-images-'))
  const paths: string[] = []

  try {
    for (const [index, imageReference] of imageReferences.entries()) {
      const targetPath = join(tempDir, `publish-${index + 1}${inferImageExtension(imageReference)}`)
      if (isRemoteImageReference(imageReference)) {
        log(`下载生成图片 ${index + 1}/${imageReferences.length}: ${imageReference}`)
        await downloadImageToFile(imageReference, targetPath)
      } else {
        const localPath = resolveLocalImagePath(imageReference)
        log(`复制上传图片 ${index + 1}/${imageReferences.length}: ${localPath}`)
        await ensureReadableLocalImage(localPath)
        await copyFile(localPath, targetPath)
      }
      paths.push(targetPath)
    }
  } catch (error) {
    await cleanupGeneratedImageFiles(tempDir)
    throw error
  }

  return { paths, tempDir }
}

function inferImageExtension(imageUrl: string): string {
  const parsed = isRemoteImageReference(imageUrl) ? new URL(imageUrl) : null
  const filename = parsed?.searchParams.get('filename') || parsed?.pathname || imageUrl
  const extension = extname(filename).toLowerCase()
  if (['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'].includes(extension)) return extension
  return '.png'
}

function isRemoteImageReference(imageReference: string): boolean {
  try {
    const parsedUrl = new URL(imageReference)
    return ['http:', 'https:'].includes(parsedUrl.protocol)
  } catch {
    return false
  }
}

function resolveLocalImagePath(imageReference: string): string {
  if (!isAbsolute(imageReference)) {
    throw new Error(`本地图片路径无效: ${imageReference}`)
  }
  return resolve(imageReference)
}

async function ensureReadableLocalImage(imagePath: string): Promise<void> {
  const imageStats = await stat(imagePath)
  if (!imageStats.isFile()) {
    throw new Error(`本地图片不是文件: ${imagePath}`)
  }
}

function downloadImageToFile(
  imageUrl: string,
  targetPath: string,
  redirectCount = 0
): Promise<void> {
  return new Promise((resolveDownload, rejectDownload) => {
    if (redirectCount > 3) {
      rejectDownload(new Error('图片下载重定向次数过多'))
      return
    }

    const parsedUrl = new URL(imageUrl)
    const requestFn = parsedUrl.protocol === 'https:' ? httpsRequest : httpRequest
    const request = requestFn(parsedUrl, (response) => {
      const statusCode = response.statusCode || 0

      if (statusCode >= 300 && statusCode < 400 && response.headers.location) {
        const location = Array.isArray(response.headers.location)
          ? response.headers.location[0]
          : response.headers.location
        response.resume()
        downloadImageToFile(new URL(location, parsedUrl).toString(), targetPath, redirectCount + 1)
          .then(resolveDownload)
          .catch(rejectDownload)
        return
      }

      if (statusCode < 200 || statusCode >= 300) {
        response.resume()
        rejectDownload(new Error(`图片下载失败，HTTP ${statusCode}`))
        return
      }

      const file = createWriteStream(targetPath)
      response.pipe(file)

      file.on('finish', () => {
        file.close((error) => {
          if (error) rejectDownload(error)
          else resolveDownload()
        })
      })

      file.on('error', rejectDownload)
    })

    request.setTimeout(UPLOAD_TIMEOUT_MS, () => {
      request.destroy(new Error('图片下载超时'))
    })

    request.on('error', rejectDownload)
    request.end()
  })
}

async function cleanupGeneratedImageFiles(tempDir: string): Promise<void> {
  try {
    await rm(tempDir, { recursive: true, force: true })
  } catch (error) {
    log(`清理生成图片临时目录失败: ${error instanceof Error ? error.message : String(error)}`)
  }
}

// ─── Step 2: 切换到图文 Tab ──────────────────────────────────────────────────

async function ensureImageTextTab(win: BrowserWindow): Promise<void> {
  await win.webContents.executeJavaScript(`
    (() => {
      // 方式 1: 查找包含 "上传图文" 文本的 tab
      const allClickable = document.querySelectorAll(
        '[class*="tab"], [class*="Tab"], [role="tab"], [class*="menu-item"], [class*="menuItem"], a, button, span'
      );
      for (const el of allClickable) {
        const text = (el.textContent || '').trim();
        if (text === '上传图文' || text === '图文') {
          el.click();
          return 'clicked-tab';
        }
      }

      // 方式 2: 如果 URL 已包含 target=image，说明已在图文模式
      if (window.location.search.includes('target=image')) {
        return 'already-image-mode';
      }

      return 'tab-not-found';
    })()
  `)
}

// ─── Step 3: 上传图片 (通过 CDP 协议) ────────────────────────────────────────

async function uploadImagesViaCDP(
  win: BrowserWindow,
  imagePaths: string[]
): Promise<void> {
  const wc = win.webContents

  // 先尝试触发上传区域，确保 file input 被渲染
  await wc.executeJavaScript(`
    (() => {
      // 点击上传区域或上传按钮，使 file input 出现
      const uploadTriggers = [
        ...document.querySelectorAll('[class*="upload"]'),
        ...document.querySelectorAll('button'),
        ...document.querySelectorAll('[class*="drag"]'),
        ...document.querySelectorAll('[class*="add-img"]'),
        ...document.querySelectorAll('[class*="addImg"]')
      ];
      for (const el of uploadTriggers) {
        const text = (el.textContent || '').trim();
        if (
          text.includes('上传图片') || text.includes('上传') ||
          el.className?.toString().includes('upload-area') ||
          el.className?.toString().includes('uploadArea')
        ) {
          // 不直接 click，只确认存在
          return 'trigger-found';
        }
      }
      return 'no-trigger';
    })()
  `)

  await delay(500)

  // 使用 CDP 设置文件
  try {
    wc.debugger.attach('1.3')
  } catch {
    // debugger 可能已 attach
  }

  try {
    const fileInputNodeId = await findFileInputNode(wc)

    if (!fileInputNodeId) {
      throw new Error(
        '未找到文件上传 <input> 元素。小红书页面结构可能已更新，请检查 DOM。'
      )
    }

    // 通过 CDP 将本地文件路径设置到 file input
    await wc.debugger.sendCommand('DOM.setFileInputFiles', {
      nodeId: fileInputNodeId,
      files: imagePaths
    })

    log(`已通过 CDP 设置 ${imagePaths.length} 个文件到 file input (nodeId: ${fileInputNodeId})`)
  } finally {
    try {
      wc.debugger.detach()
    } catch {
      // ignore
    }
  }
}

/**
 * 在 DOM 中查找 file input 元素的 nodeId。
 * 按优先级尝试多种选择器。
 */
async function findFileInputNode(wc: Electron.WebContents): Promise<number | null> {
  const { root } = (await wc.debugger.sendCommand('DOM.getDocument')) as {
    root: { nodeId: number }
  }

  const selectors = [
    'input[type="file"][accept*="image"]',
    'input[type="file"]',
    '[class*="upload"] input[type="file"]',
    '[class*="Upload"] input[type="file"]'
  ]

  for (const selector of selectors) {
    try {
      const result = (await wc.debugger.sendCommand('DOM.querySelector', {
        nodeId: root.nodeId,
        selector
      })) as { nodeId: number }

      if (result.nodeId && result.nodeId !== 0) {
        log(`file input 定位成功: selector="${selector}", nodeId=${result.nodeId}`)
        return result.nodeId
      }
    } catch {
      continue
    }
  }

  // 如果直接查找失败，尝试 querySelectorAll 找第一个
  try {
    const result = (await wc.debugger.sendCommand('DOM.querySelectorAll', {
      nodeId: root.nodeId,
      selector: 'input[type="file"]'
    })) as { nodeIds: number[] }

    if (result.nodeIds?.length > 0) {
      log(`file input 通过 querySelectorAll 找到: nodeId=${result.nodeIds[0]}`)
      return result.nodeIds[0]
    }
  } catch {
    // ignore
  }

  return null
}

// ─── Step 4: 等待图片上传完成 ────────────────────────────────────────────────

async function waitForUploadComplete(
  win: BrowserWindow,
  expectedCount: number
): Promise<void> {
  const startTime = Date.now()

  while (Date.now() - startTime < UPLOAD_TIMEOUT_MS) {
    const status = (await win.webContents.executeJavaScript(`
      (() => {
        // 检测已上传的图片缩略图数量
        const thumbSelectors = [
          '[class*="image-item"]', '[class*="imageItem"]',
          '[class*="upload-item"]', '[class*="uploadItem"]',
          '[class*="img-container"]', '[class*="imgContainer"]',
          '[class*="coverImg"]', '[class*="cover-img"]',
          '[class*="publish-image"]', '[class*="publishImage"]',
          '[class*="photo-item"]', '[class*="photoItem"]',
          '[class*="uploaded"] img', '[class*="preview"] img'
        ];
        let thumbCount = 0;
        for (const sel of thumbSelectors) {
          const items = document.querySelectorAll(sel);
          if (items.length > thumbCount) thumbCount = items.length;
        }

        // 检测是否还有加载中的元素
        const loadingSelectors = [
          '[class*="loading"]', '[class*="Loading"]',
          '[class*="uploading"]', '[class*="Uploading"]',
          '[class*="progress"]', '[class*="Progress"]',
          '[class*="spinner"]', '[class*="Spinner"]'
        ];
        let isLoading = false;
        for (const sel of loadingSelectors) {
          const loadingEls = document.querySelectorAll(sel);
          for (const el of loadingEls) {
            // 排除不可见的 loading 元素
            const style = window.getComputedStyle(el);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
              isLoading = true;
              break;
            }
          }
          if (isLoading) break;
        }

        return { thumbCount, isLoading };
      })()
    `)) as { thumbCount: number; isLoading: boolean }

    log(
      `上传进度: 检测到 ${status.thumbCount} 张缩略图 (期望 ${expectedCount}), ` +
        `加载中: ${status.isLoading}`
    )

    if (status.thumbCount >= expectedCount && !status.isLoading) {
      log('✓ 图片上传完成')
      return
    }

    await delay(POLL_INTERVAL_MS)
  }

  throw new Error(`图片上传超时 (已等待 ${UPLOAD_TIMEOUT_MS / 1000}s)`)
}

// ─── Step 5: 填写标题 ────────────────────────────────────────────────────────

async function fillTitle(win: BrowserWindow, title: string): Promise<void> {
  // 定位并 focus 标题输入框
  const found = (await win.webContents.executeJavaScript(`
    (() => {
      const selectors = [
        'input[placeholder*="标题"]',
        'input[placeholder*="起个标题"]',
        'input[placeholder*="填写标题"]',
        'input[placeholder*="作品标题"]',
        '[class*="title"] input[type="text"]',
        '[class*="Title"] input[type="text"]',
        '[class*="titleInput"]',
        '[class*="title-input"]',
        '#title',
        '[name="title"]',
        'input[maxlength="20"]'
      ];

      for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (el && el.tagName === 'INPUT') {
          el.focus();
          el.click();
          return { found: true, selector };
        }
      }

      // Fallback: 按 DOM 顺序找第一个看起来像标题的 input
      const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
      for (const input of inputs) {
        const ph = (input.getAttribute('placeholder') || '').toLowerCase();
        const cls = (input.className?.toString() || '').toLowerCase();
        if (ph.includes('标题') || cls.includes('title')) {
          input.focus();
          input.click();
          return { found: true, selector: 'fallback-scan' };
        }
      }

      return { found: false };
    })()
  `)) as { found: boolean; selector?: string }

  if (!found.found) {
    throw new Error('未找到标题输入框')
  }
  log(`标题输入框定位成功: ${found.selector}`)

  await delay(200)

  // 清空现有内容
  await win.webContents.executeJavaScript(`
    (() => {
      const el = document.activeElement;
      if (el && el.tagName === 'INPUT') {
        el.value = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
      }
    })()
  `)

  // 使用 insertText 模拟真实键盘输入
  await win.webContents.insertText(title)
  await delay(300)

  // 触发事件确保框架响应
  await win.webContents.executeJavaScript(`
    (() => {
      const el = document.activeElement;
      if (el) {
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    })()
  `)
}

// ─── Step 6: 填写正文 ────────────────────────────────────────────────────────

async function fillContent(win: BrowserWindow, content: string): Promise<void> {
  const found = (await win.webContents.executeJavaScript(`
    (() => {
      const selectors = [
        '#post-content',
        '[contenteditable="true"]',
        '[class*="ql-editor"]',
        '.ql-editor',
        '[class*="editor"] [contenteditable]',
        '[class*="Editor"] [contenteditable]',
        '[class*="post-content"]',
        '[class*="postContent"]',
        '[data-placeholder*="正文"]',
        '[data-placeholder*="描述"]',
        '[data-placeholder*="输入"]',
        'textarea[placeholder*="正文"]',
        'textarea[placeholder*="描述"]',
        'textarea[placeholder*="输入"]'
      ];

      for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (el) {
          el.focus();
          el.click();
          return {
            found: true,
            selector,
            isContentEditable: el.isContentEditable || false,
            tagName: el.tagName
          };
        }
      }

      return { found: false };
    })()
  `)) as {
    found: boolean
    selector?: string
    isContentEditable?: boolean
    tagName?: string
  }

  if (!found.found) {
    throw new Error('未找到正文编辑区')
  }
  log(
    `正文编辑区定位成功: ${found.selector} (${found.tagName}, contenteditable=${found.isContentEditable})`
  )

  await delay(200)

  if (found.isContentEditable) {
    // contenteditable 元素：先清空再输入
    await win.webContents.executeJavaScript(`
      (() => {
        const el = document.activeElement;
        if (el && el.isContentEditable) {
          el.innerHTML = '';
          el.focus();
          // 确保光标在最前面
          const range = document.createRange();
          const sel = window.getSelection();
          range.selectNodeContents(el);
          range.collapse(true);
          sel.removeAllRanges();
          sel.addRange(range);
        }
      })()
    `)
    await delay(100)
    await win.webContents.insertText(content)
  } else {
    // textarea 或 input 元素
    await win.webContents.executeJavaScript(`
      (() => {
        const el = document.activeElement;
        if (el && (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT')) {
          el.value = '';
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      })()
    `)
    await delay(100)
    await win.webContents.insertText(content)
  }

  await delay(300)

  // 触发事件
  await win.webContents.executeJavaScript(`
    (() => {
      const el = document.activeElement;
      if (el) {
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    })()
  `)
}

// ─── Step 6.5: 添加话题标签 ──────────────────────────────────────────────────

async function addTags(win: BrowserWindow, tags: string[]): Promise<void> {
  for (const rawTag of tags) {
    // 去掉 # 前缀，提取纯文本
    const tagText = rawTag.replace(/^[#＃]+/, '').trim()
    if (!tagText) continue

    log(`添加话题: #${tagText}`)

    // 方式 1: 尝试点击 # 话题按钮来打开话题输入
    const hasTopicButton = await win.webContents.executeJavaScript(`
      (() => {
        const buttons = document.querySelectorAll(
          'button, [class*="tag-btn"], [class*="tagBtn"], [class*="topic-btn"], [class*="topicBtn"], ' +
          '[class*="hash"], [class*="Hash"]'
        );
        for (const btn of buttons) {
          const text = (btn.textContent || '').trim();
          if (text === '#' || text === '# 话题' || text === '#话题' || text.includes('话题')) {
            btn.click();
            return true;
          }
        }
        return false;
      })()
    `)

    if (hasTopicButton) {
      await delay(600)

      // 在话题搜索框中输入后必须回车，小红书才会识别为话题标签
      await win.webContents.insertText(tagText)
      await delay(800)
      await pressKey(win, 'Enter')
      log(`已按 Enter 确认话题: #${tagText}`)

      await delay(500)

      // 关闭可能还打开的下拉面板
      await pressKey(win, 'Escape')
      await delay(300)
    } else {
      // 方式 2: 直接在正文编辑区末尾追加 #话题
      log('未找到话题按钮，在正文末尾追加话题标签')

      await win.webContents.executeJavaScript(`
        (() => {
          // 重新 focus 到正文编辑区
          const editor = document.querySelector(
            '#post-content, [contenteditable="true"], .ql-editor, textarea'
          );
          if (editor) {
            editor.focus();
            if (editor.isContentEditable) {
              const range = document.createRange();
              const sel = window.getSelection();
              range.selectNodeContents(editor);
              range.collapse(false); // 光标移到末尾
              sel.removeAllRanges();
              sel.addRange(range);
            } else if (editor.tagName === 'TEXTAREA') {
              editor.selectionStart = editor.value.length;
              editor.selectionEnd = editor.value.length;
            }
          }
        })()
      `)
      await delay(200)

      // 输入话题文本后同样回车确认
      await win.webContents.insertText(` #${tagText}`)
      await delay(300)
      await pressKey(win, 'Enter')
      log(`已按 Enter 确认话题: #${tagText}`)
      await delay(300)
    }
  }
}

// ─── Step 7: 点击发布按钮 ────────────────────────────────────────────────────

async function clickPublishButton(win: BrowserWindow): Promise<void> {
  const wc = win.webContents

  try {
    wc.debugger.attach('1.3')
  } catch {
    // debugger 可能已 attach
  }

  try {
    const publishButton = await waitForPublishButtonNode(wc)
    await clickNodeCenterViaCDP(wc, publishButton.nodeId)
    log(`已点击发布按钮: "${publishButton.text}" (定位方式: CDP closed shadow DOM)`)
  } finally {
    try {
      wc.debugger.detach()
    } catch {
      // ignore
    }
  }
}

async function waitForPublishButtonNode(
  wc: Electron.WebContents
): Promise<{ nodeId: number; text: string }> {
  const startTime = Date.now()

  while (Date.now() - startTime < ELEMENT_WAIT_TIMEOUT_MS) {
    const publishButton = await findPublishButtonNodeViaCDP(wc)
    if (publishButton) return publishButton
    await delay(POLL_INTERVAL_MS)
  }

  throw new Error(`等待元素超时: 发布按钮 (${ELEMENT_WAIT_TIMEOUT_MS / 1000}s)`)
}

async function findPublishButtonNodeViaCDP(
  wc: Electron.WebContents
): Promise<{ nodeId: number; text: string } | null> {
  const { root } = (await wc.debugger.sendCommand('DOM.getDocument', {
    depth: -1,
    pierce: true
  })) as { root: CdpDomNode }

  const host = findNode(root, (node) => {
    const tagName = getTagName(node)
    if (tagName !== 'xhs-publish-btn') return false

    const attrs = getAttributes(node)
    return attrs['submit-disabled'] !== 'true' && attrs['is-publish'] !== 'false'
  })

  if (!host) return null

  return findPublishButtonInNode(host)
}

function findPublishButtonInNode(
  root: CdpDomNode
): { nodeId: number; text: string } | null {
  const tagName = getTagName(root)

  if (tagName === 'button') {
    const attrs = getAttributes(root)
    const className = attrs['class'] || ''
    const text = getNodeText(root).trim()
    const isDisabled =
      'disabled' in attrs ||
      attrs['aria-disabled'] === 'true' ||
      attrs['disabled'] === 'true'

    if (
      !isDisabled &&
      text === '发布' &&
      className.includes('ce-btn') &&
      className.includes('bg-red')
    ) {
      return { nodeId: root.nodeId, text }
    }
  }

  const descendants = [...(root.shadowRoots || []), ...(root.children || [])]
  for (const child of descendants) {
    const result = findPublishButtonInNode(child)
    if (result) return result
  }

  return null
}

async function clickNodeCenterViaCDP(
  wc: Electron.WebContents,
  nodeId: number
): Promise<void> {
  try {
    await wc.debugger.sendCommand('DOM.scrollIntoViewIfNeeded', { nodeId })
  } catch {
    // ignore
  }

  const { model } = (await wc.debugger.sendCommand('DOM.getBoxModel', {
    nodeId
  })) as CdpBoxModel

  const quad = model.content?.length >= 8 ? model.content : model.border
  const x = (quad[0] + quad[2] + quad[4] + quad[6]) / 4
  const y = (quad[1] + quad[3] + quad[5] + quad[7]) / 4

  await wc.debugger.sendCommand('Input.dispatchMouseEvent', {
    type: 'mouseMoved',
    x,
    y,
    button: 'none'
  })
  await wc.debugger.sendCommand('Input.dispatchMouseEvent', {
    type: 'mousePressed',
    x,
    y,
    button: 'left',
    clickCount: 1
  })
  await wc.debugger.sendCommand('Input.dispatchMouseEvent', {
    type: 'mouseReleased',
    x,
    y,
    button: 'left',
    clickCount: 1
  })
}

function findNode(
  root: CdpDomNode,
  predicate: (node: CdpDomNode) => boolean
): CdpDomNode | null {
  if (predicate(root)) return root

  const descendants = [...(root.shadowRoots || []), ...(root.children || [])]
  for (const child of descendants) {
    const result = findNode(child, predicate)
    if (result) return result
  }

  return null
}

function getTagName(node: CdpDomNode): string {
  return (node.localName || node.nodeName || '').toLowerCase()
}

function getAttributes(node: CdpDomNode): Record<string, string> {
  const attrs: Record<string, string> = {}
  const rawAttrs = node.attributes || []

  for (let i = 0; i < rawAttrs.length; i += 2) {
    attrs[rawAttrs[i]] = rawAttrs[i + 1] || ''
  }

  return attrs
}

function getNodeText(node: CdpDomNode): string {
  const ownText = node.nodeValue || ''
  const descendants = [...(node.shadowRoots || []), ...(node.children || [])]
  return ownText + descendants.map(getNodeText).join('')
}

// ─── 等待发布结果 ────────────────────────────────────────────────────────────

async function waitForPublishConfirmation(win: BrowserWindow): Promise<void> {
  const startTime = Date.now()

  while (Date.now() - startTime < PUBLISH_CONFIRM_TIMEOUT_MS) {
    const status = (await win.webContents.executeJavaScript(`
      (() => {
        const bodyText = (document.body?.innerText || '').slice(0, 6000);
        const url = window.location.href;

        // 成功信号
        const successPatterns = [
          '发布成功', '发布完成', '已发布', '笔记已发布',
          '作品已发布', '提交成功', '发布成功'
        ];
        const hasSuccess = successPatterns.some(p => bodyText.includes(p));

        // 失败信号
        const failPatterns = [
          '发布失败', '发送失败', '提交失败', '操作失败',
          '网络错误', '请重试', '内容违规', '审核不通过'
        ];
        const hasFail = failPatterns.some(p => bodyText.includes(p));

        // Toast / 弹窗消息
        const toastEls = document.querySelectorAll(
          '[class*="toast"], [class*="Toast"], [class*="message"], [class*="Message"], ' +
          '[class*="notification"], [class*="Notification"], [class*="notice"], [class*="Notice"], ' +
          '[class*="dialog"], [class*="Dialog"], [class*="modal"], [class*="Modal"], ' +
          '[class*="success"], [class*="Success"]'
        );
        const toastTexts = [];
        for (const el of toastEls) {
          const text = (el.textContent || '').trim();
          if (text.length > 0 && text.length < 200) {
            toastTexts.push(text);
          }
        }

        return { hasSuccess, hasFail, url, toastTexts };
      })()
    `)) as {
      hasSuccess: boolean
      hasFail: boolean
      url: string
      toastTexts: string[]
    }

    if (status.toastTexts.length) {
      log(`检测到弹窗消息: ${status.toastTexts.join(' | ')}`)
    }

    if (status.hasSuccess) {
      log('✓ 检测到发布成功信号')
      return
    }

    if (status.hasFail) {
      const failMsg = status.toastTexts.find(
        (t) =>
          t.includes('失败') || t.includes('错误') || t.includes('违规')
      )
      throw new Error(`小红书发布失败: ${failMsg || '未知原因'}`)
    }

    // 页面跳转离开发布页也视为成功
    if (status.url && !status.url.includes('/publish/')) {
      log(`页面已跳转到 ${status.url}，判断为发布成功`)
      return
    }

    await delay(POLL_INTERVAL_MS)
  }

  // 超时但没有错误信号，也视为成功（某些情况下页面不会有明确的成功提示）
  log('⚠️ 发布确认等待超时，但未检测到错误信号，视为发布成功')
}

// ─── 工具函数 ────────────────────────────────────────────────────────────────

function validatePayload(payload: PublishImageTextPayload): void {
  if (!payload.accountId) throw new Error('缺少账号 ID')
  if (!payload.title?.trim()) throw new Error('标题不能为空')
  if (!payload.content?.trim()) throw new Error('正文不能为空')
  if (!payload.imageUrls?.length) throw new Error('请先添加图片')
  if (payload.imageUrls.length > 18) throw new Error('最多支持 18 张图片')

  for (const imageReference of payload.imageUrls) {
    if (!imageReference?.trim()) {
      throw new Error('图片地址或路径不能为空')
    }
    if (isRemoteImageReference(imageReference)) {
      continue
    }
    if (!isAbsolute(imageReference)) {
      throw new Error(`图片地址或路径无效: ${imageReference}`)
    }
  }
}

async function resolveAccountPartition(accountId: string): Promise<string> {
  const storePath = join(app.getPath('userData'), STORE_FILE_NAME)

  let raw: string
  try {
    raw = await readFile(storePath, 'utf8')
  } catch {
    throw new Error('未找到账号数据文件，请先添加并登录小红书账号')
  }

  const store = JSON.parse(raw)
  const account = (store.accounts || []).find(
    (a: XhsAccountMinimal) => a.id === accountId
  )

  if (!account) throw new Error(`未找到账号: ${accountId}`)
  if (account.status !== 'saved') {
    throw new Error('该账号尚未完成登录，请先在账号管理中登录小红书')
  }

  return account.partition
}

function createRpaWindow(partition: string): BrowserWindow {
  const win = new BrowserWindow({
    width: 1280,
    height: 900,
    show: RPA_DEBUG,
    title: '[RPA] 小红书发布',
    webPreferences: {
      partition,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  })

  win.webContents.setUserAgent(XHS_USER_AGENT)

  if (RPA_DEBUG) {
    win.webContents.openDevTools({ mode: 'detach' })
  }

  return win
}

function loadUrl(win: BrowserWindow, url: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error(`页面加载超时: ${url}`))
    }, PAGE_LOAD_TIMEOUT_MS)

    win.webContents.once('did-finish-load', () => {
      clearTimeout(timeout)
      resolve()
    })

    win.webContents.once('did-fail-load', (_event, errorCode, errorDescription) => {
      clearTimeout(timeout)
      reject(
        new Error(`页面加载失败: ${errorDescription} (code: ${errorCode})`)
      )
    })

    win.loadURL(url)
  })
}

async function pressKey(win: BrowserWindow, keyCode: string): Promise<void> {
  win.webContents.sendInputEvent({ type: 'keyDown', keyCode })
  await delay(50)
  win.webContents.sendInputEvent({ type: 'keyUp', keyCode })
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function log(message: string): void {
  const timestamp = new Date().toISOString()
  const line = `${timestamp} [xhs-publisher] ${message}`
  console.log(line)
  writeToLogFile(line)
}

function writeToLogFile(line: string): void {
  try {
    if (!logFileReady) {
      const logDir = dirname(LOG_FILE_PATH)
      mkdirSync(logDir, { recursive: true })
      logFileReady = true
    }
    appendFileSync(LOG_FILE_PATH, line + '\n', 'utf8')
  } catch {
    // 日志写入失败不应影响主流程
  }
}
