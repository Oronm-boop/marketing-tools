import { app, dialog } from 'electron'
import { spawn, type ChildProcess } from 'child_process'
import { createWriteStream, existsSync, mkdirSync } from 'fs'
import { get } from 'http'
import { join, resolve } from 'path'
import { is } from '@electron-toolkit/utils'

export const BACKEND_HOST = process.env['MDT_BACKEND_HOST'] || '127.0.0.1'
export const BACKEND_PORT = Number(process.env['MDT_BACKEND_PORT'] || 8000)
const BACKEND_HEALTH_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/health`

let backendProcess: ChildProcess | null = null

type BackendCommand = {
  command: string
  args: string[]
  cwd: string
}

export async function startBackend(): Promise<void> {
  if (process.env['MDT_SKIP_BACKEND'] === '1') {
    return
  }

  if (await waitForBackend(600)) {
    return
  }

  const command = resolveBackendCommand()
  const processRef = spawn(command.command, command.args, {
    cwd: command.cwd,
    env: {
      ...process.env,
      BACKEND_HOST,
      BACKEND_PORT: String(BACKEND_PORT),
      PYTHONUTF8: '1'
    },
    stdio: is.dev ? 'pipe' : ['ignore', 'pipe', 'pipe'],
    windowsHide: true
  })

  backendProcess = processRef
  pipeBackendLogs(processRef)

  processRef.once('exit', (code, signal) => {
    console.log(`[backend] exited with code=${code ?? 'null'} signal=${signal ?? 'null'}`)
    backendProcess = null
  })

  if (!(await waitForBackend(15_000))) {
    dialog.showErrorBox(
      '后端服务启动失败',
      `无法连接本地后端：${BACKEND_HEALTH_URL}\n请检查后端配置或端口占用。`
    )
  }
}

export function stopBackend(): void {
  if (!backendProcess?.pid) {
    return
  }

  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', String(backendProcess.pid), '/t', '/f'], {
      windowsHide: true,
      stdio: 'ignore'
    })
    backendProcess = null
    return
  }

  backendProcess.kill()
  backendProcess = null
}

function resolveBackendCommand(): BackendCommand {
  if (!is.dev) {
    const backendDir = join(process.resourcesPath, 'backend')
    const executable = process.platform === 'win32' ? 'mdt-ai-backend.exe' : 'mdt-ai-backend'
    return {
      command: join(backendDir, executable),
      args: [],
      cwd: backendDir
    }
  }

  const backendDir = resolve(process.cwd(), '..', 'backend')
  const venvPython = join(backendDir, '.venv', 'Scripts', 'python.exe')

  if (existsSync(venvPython)) {
    return {
      command: venvPython,
      args: ['run_backend.py'],
      cwd: backendDir
    }
  }

  return {
    command: 'py',
    args: ['run_backend.py'],
    cwd: backendDir
  }
}

function pipeBackendLogs(processRef: ChildProcess): void {
  const logDir = join(app.getPath('userData'), 'logs')
  mkdirSync(logDir, { recursive: true })
  const logStream = createWriteStream(join(logDir, 'backend.log'), { flags: 'a' })

  processRef.stdout?.on('data', (chunk) => {
    const text = chunk.toString()
    logStream.write(text)
    if (is.dev) console.log(`[backend] ${text.trimEnd()}`)
  })

  processRef.stderr?.on('data', (chunk) => {
    const text = chunk.toString()
    logStream.write(text)
    if (is.dev) console.error(`[backend] ${text.trimEnd()}`)
  })
}

async function waitForBackend(timeoutMs: number): Promise<boolean> {
  const startedAt = Date.now()

  while (Date.now() - startedAt < timeoutMs) {
    if (await checkBackendHealth()) {
      return true
    }
    await delay(350)
  }

  return false
}

function checkBackendHealth(): Promise<boolean> {
  return new Promise((resolveResult) => {
    const request = get(BACKEND_HEALTH_URL, (response) => {
      response.resume()
      resolveResult(response.statusCode === 200)
    })

    request.setTimeout(800, () => {
      request.destroy()
      resolveResult(false)
    })

    request.on('error', () => {
      resolveResult(false)
    })
  })
}

function delay(ms: number): Promise<void> {
  return new Promise((resolveDelay) => {
    setTimeout(resolveDelay, ms)
  })
}
