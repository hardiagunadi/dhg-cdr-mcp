# Auto-sync: commit semua perubahan lokal lalu push ke GitHub (origin).
# Dijalankan berkala oleh Windows Task Scheduler (lihat README bagian "Sinkronisasi otomatis").
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

if (-not (git status --porcelain)) { exit 0 }   # tidak ada perubahan

git add -A
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
git commit -q -m "chore: auto-sync $stamp"
git push -q origin main
