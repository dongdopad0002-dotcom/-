[CmdletBinding()]
param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$browserDirectory = Join-Path $repoRoot "playwright-browsers"
Set-Location $repoRoot
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install pyinstaller
$env:PLAYWRIGHT_BROWSERS_PATH = $browserDirectory
& $Python -m playwright install chromium
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
& $Python -m PyInstaller --noconfirm --clean windows_portable.spec
if (-not (Test-Path "dist/JeongSoyoonAI/JeongSoyoonAI.exe")) { throw "EXE was not created." }
Write-Host "Build complete: $repoRoot/dist/JeongSoyoonAI/JeongSoyoonAI.exe"
