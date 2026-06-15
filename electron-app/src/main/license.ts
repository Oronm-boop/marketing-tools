import { execFile } from 'child_process'
import { existsSync } from 'fs'
import { join, resolve } from 'path'
import { promisify } from 'util'
import { is } from '@electron-toolkit/utils'

const LICENSE_DLL_NAME = 'LicenseVallidator.dll'
const LICENSE_CHECK_TIMEOUT_MS = 30_000

const execFileAsync = promisify(execFile)

export type LicenseValidationResult =
  | {
      valid: true
    }
  | {
      valid: false
      message: string
    }

export async function verifyLicense(ip: string, port: number): Promise<LicenseValidationResult> {
  if (process.platform !== 'win32') {
    return {
      valid: false,
      message: '当前 License 校验仅支持 Windows，无法加载 LicenseVallidator.dll。'
    }
  }

  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    return {
      valid: false,
      message: `License 验证端口无效：${port}。`
    }
  }

  const licenseDir = getLicenseDir()
  const dllPath = join(licenseDir, LICENSE_DLL_NAME)

  if (!existsSync(dllPath)) {
    return {
      valid: false,
      message: `未找到 License 校验库：${dllPath}`
    }
  }

  const script = createLicenseCheckScript(licenseDir, dllPath, ip, port)

  try {
    const { stdout } = await execFileAsync('powershell.exe', [
      '-NoProfile',
      '-NonInteractive',
      '-ExecutionPolicy',
      'Bypass',
      '-Command',
      script
    ], {
      encoding: 'utf8',
      timeout: LICENSE_CHECK_TIMEOUT_MS,
      windowsHide: true,
      maxBuffer: 1024 * 1024
    })

    if (getOutputLines(stdout).includes('VALID')) {
      return { valid: true }
    }

    return {
      valid: false,
      message: 'License 验证未通过，软件即将退出。'
    }
  } catch (error) {
    const execError = error as ExecFailure
    const stdout = toText(execError.stdout)
    const stderr = toText(execError.stderr)

    if (execError.code === 2 || getOutputLines(stdout).includes('INVALID')) {
      return {
        valid: false,
        message: 'License 验证未通过，软件即将退出。'
      }
    }

    if (execError.killed) {
      return {
        valid: false,
        message: 'License 验证超时，软件即将退出。'
      }
    }

    const detail = [stderr, stdout].filter(Boolean).join('\n')
    return {
      valid: false,
      message: detail
        ? `License 验证调用失败，软件即将退出。\n${detail}`
        : 'License 验证调用失败，软件即将退出。'
    }
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
  if (!value) {
    return ''
  }

  return String(value).trim()
}

function getOutputLines(value: unknown): string[] {
  return toText(value)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
}

type ExecFailure = Error & {
  code?: number | string
  killed?: boolean
  stdout?: unknown
  stderr?: unknown
}
