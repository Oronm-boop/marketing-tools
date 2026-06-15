import { execFile } from 'child_process'
import { randomUUID } from 'crypto'
import { app } from 'electron'
import { appendFileSync, existsSync, mkdirSync, renameSync, statSync } from 'fs'
import { join, resolve } from 'path'
import { promisify } from 'util'
import { is } from '@electron-toolkit/utils'

const LICENSE_DLL_NAMES = ['LicenseValidator.dll', 'LicenseVallidator.dll']
const LICENSE_CHECK_TIMEOUT_MS = 30_000
const LICENSE_LOG_NAME = 'license.log'
const MAX_LICENSE_LOG_BYTES = 2 * 1024 * 1024

const execFileAsync = promisify(execFile)

export type LicenseValidationResult =
  | {
      valid: true
      logPath?: string
    }
  | {
      valid: false
      message: string
      logPath?: string
    }

export async function verifyLicense(ip: string, port: number): Promise<LicenseValidationResult> {
  const logger = createLicenseLogger()
  const validationId = randomUUID()
  const startedAt = Date.now()

  logger.info('License validation started', {
    validationId,
    platform: process.platform,
    arch: process.arch,
    isDev: is.dev,
    ip,
    port
  })

  if (process.platform !== 'win32') {
    return failLicenseValidation(
      logger,
      validationId,
      startedAt,
      '当前 License 校验仅支持 Windows，无法加载 LicenseValidator.dll。',
      { reason: 'unsupported_platform', platform: process.platform }
    )
  }

  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    return failLicenseValidation(logger, validationId, startedAt, `License 验证端口无效：${port}。`, {
      reason: 'invalid_port',
      port
    })
  }

  const licenseDir = getLicenseDir()
  const dllPath = findLicenseDll(licenseDir)

  logger.info('License DLL checked', {
    validationId,
    licenseDir,
    configuredLicenseDir: process.env['MDT_LICENSE_DIR'] || null,
    dllCandidates: LICENSE_DLL_NAMES.map((name) => getFileState(join(licenseDir, name))),
    dllPath
  })

  if (!dllPath) {
    return failLicenseValidation(
      logger,
      validationId,
      startedAt,
      `未找到 License 校验库：${LICENSE_DLL_NAMES.join(' 或 ')}`,
      { reason: 'dll_missing', licenseDir }
    )
  }

  const script = createLicenseCheckScript(licenseDir, dllPath, ip, port)

  try {
    const { stdout, stderr } = await execFileAsync(
      'powershell.exe',
      ['-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-Command', script],
      {
        encoding: 'utf8',
        timeout: LICENSE_CHECK_TIMEOUT_MS,
        windowsHide: true,
        maxBuffer: 1024 * 1024
      }
    )

    logger.info('License validator completed', {
      validationId,
      elapsedMs: Date.now() - startedAt,
      stdout: toText(stdout),
      stderr: toText(stderr)
    })

    if (getOutputLines(stdout).includes('VALID')) {
      return {
        valid: true,
        ...(logger.path ? { logPath: logger.path } : {})
      }
    }

    return failLicenseValidation(
      logger,
      validationId,
      startedAt,
      'License 验证未通过，软件即将退出。',
      { reason: 'unexpected_output', stdout: toText(stdout), stderr: toText(stderr) }
    )
  } catch (error) {
    const execError = error as ExecFailure
    const stdout = toText(execError.stdout)
    const stderr = toText(execError.stderr)

    logger.error('License validator failed', {
      validationId,
      elapsedMs: Date.now() - startedAt,
      exitCode: execError.code ?? null,
      signal: execError.signal ?? null,
      killed: Boolean(execError.killed),
      message: execError.message,
      stdout,
      stderr
    })

    if (execError.code === 2 || getOutputLines(stdout).includes('INVALID')) {
      return failLicenseValidation(
        logger,
        validationId,
        startedAt,
        'License 验证未通过，软件即将退出。',
        { reason: 'dll_returned_invalid', exitCode: execError.code ?? null, stdout, stderr }
      )
    }

    if (execError.killed) {
      return failLicenseValidation(logger, validationId, startedAt, 'License 验证超时，软件即将退出。', {
        reason: 'timeout',
        timeoutMs: LICENSE_CHECK_TIMEOUT_MS,
        stdout,
        stderr
      })
    }

    const detail = [stderr, stdout].filter(Boolean).join('\n')
    return failLicenseValidation(
      logger,
      validationId,
      startedAt,
      detail
        ? `License 验证调用失败，软件即将退出。\n${detail}`
        : 'License 验证调用失败，软件即将退出。',
      {
        reason: 'validator_process_error',
        exitCode: execError.code ?? null,
        signal: execError.signal ?? null,
        stdout,
        stderr
      }
    )
  }
}

function getLicenseDir(): string {
  const configuredLicenseDir = process.env['MDT_LICENSE_DIR']

  if (configuredLicenseDir) {
    return resolve(configuredLicenseDir)
  }

  if (is.dev) {
    return resolve(process.cwd(), 'License')
  }

  return join(process.resourcesPath, 'License')
}

function findLicenseDll(licenseDir: string): string | null {
  for (const name of LICENSE_DLL_NAMES) {
    const dllPath = join(licenseDir, name)
    if (existsSync(dllPath)) {
      return dllPath
    }
  }

  return null
}

function createLicenseCheckScript(
  licenseDir: string,
  dllPath: string,
  ip: string,
  port: number
): string {
  return `
$ErrorActionPreference = 'Stop'
$licenseDir = ${toPowerShellString(licenseDir)}
$dllPath = ${toPowerShellString(dllPath)}
$env:PATH = $licenseDir + ';' + $env:PATH

if (!(Test-Path -LiteralPath $dllPath)) {
  Write-Error "License DLL not found: $dllPath"
  exit 10
}

$source = @'
using System;
using System.Runtime.InteropServices;

public static class NativeLicenseValidator
{
  [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Unicode)]
  public static extern bool SetDllDirectory(string lpPathName);

  [DllImport(@"${toCSharpVerbatimString(dllPath)}", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi, EntryPoint = "ParseAndVerifyLicense")]
  [return: MarshalAs(UnmanagedType.I1)]
  public static extern bool ParseAndVerifyLicense(string ip, int port);
}
'@

Add-Type -TypeDefinition $source

if (-not [NativeLicenseValidator]::SetDllDirectory($licenseDir)) {
  $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
  Write-Error "SetDllDirectory failed: $errorCode"
  exit 11
}

$valid = [NativeLicenseValidator]::ParseAndVerifyLicense(${toPowerShellString(ip)}, ${port})
Write-Output "DLL_RETURN=$valid"

if ($valid) {
  Write-Output 'VALID'
  exit 0
}

Write-Output 'INVALID'
exit 2
`.trim()
}

function toPowerShellString(value: string): string {
  return `'${value.replace(/'/g, "''")}'`
}

function toCSharpVerbatimString(value: string): string {
  return value.replace(/"/g, '""')
}

function toText(value: unknown): string {
  return value ? String(value).trim() : ''
}

function getOutputLines(value: unknown): string[] {
  return toText(value)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
}

function failLicenseValidation(
  logger: LicenseLogger,
  validationId: string,
  startedAt: number,
  message: string,
  details: Record<string, unknown>
): LicenseValidationResult {
  logger.error('License validation failed', {
    validationId,
    elapsedMs: Date.now() - startedAt,
    ...details
  })

  return {
    valid: false,
    message,
    ...(logger.path ? { logPath: logger.path } : {})
  }
}

function getFileState(filePath: string): LicenseFileState {
  try {
    const stat = statSync(filePath)
    return {
      path: filePath,
      exists: true,
      sizeBytes: stat.size,
      modifiedAt: stat.mtime.toISOString()
    }
  } catch (error) {
    return {
      path: filePath,
      exists: false,
      error: error instanceof Error ? error.message : String(error)
    }
  }
}

function createLicenseLogger(): LicenseLogger {
  try {
    const logDir = join(app.getPath('userData'), 'logs')
    mkdirSync(logDir, { recursive: true })

    const logPath = join(logDir, LICENSE_LOG_NAME)
    rotateLicenseLog(logPath)

    return {
      path: logPath,
      info: (message, details) => writeLicenseLog(logPath, 'INFO', message, details),
      error: (message, details) => writeLicenseLog(logPath, 'ERROR', message, details)
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    console.error(`[license] Failed to initialize license log: ${message}`)

    return {
      info: (logMessage, details) => console.info(`[license] ${logMessage}`, details ?? ''),
      error: (logMessage, details) => console.error(`[license] ${logMessage}`, details ?? '')
    }
  }
}

function rotateLicenseLog(logPath: string): void {
  if (!existsSync(logPath)) {
    return
  }

  const stat = statSync(logPath)
  if (stat.size <= MAX_LICENSE_LOG_BYTES) {
    return
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  renameSync(logPath, `${logPath}.${timestamp}.bak`)
}

function writeLicenseLog(
  logPath: string,
  level: LicenseLogLevel,
  message: string,
  details?: Record<string, unknown>
): void {
  const detailText = details ? ` ${JSON.stringify(details)}` : ''
  const line = `${new Date().toISOString()} [${level}] ${message}${detailText}\n`

  try {
    appendFileSync(logPath, line, { encoding: 'utf8' })
  } catch (error) {
    const logError = error instanceof Error ? error.message : String(error)
    console.error(`[license] Failed to write license log: ${logError}`)
  }
}

type ExecFailure = Error & {
  code?: number | string
  killed?: boolean
  signal?: string
  stdout?: unknown
  stderr?: unknown
}

type LicenseLogLevel = 'INFO' | 'ERROR'

type LicenseLogger = {
  path?: string
  info: (message: string, details?: Record<string, unknown>) => void
  error: (message: string, details?: Record<string, unknown>) => void
}

type LicenseFileState =
  | {
      path: string
      exists: true
      sizeBytes: number
      modifiedAt: string
    }
  | {
      path: string
      exists: false
      error: string
    }
