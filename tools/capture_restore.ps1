$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RestoreCap {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
}
"@
function Activate($h) {
  for ($i = 0; $i -lt 10; $i++) {
    [RestoreCap]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [RestoreCap]::SetForegroundWindow($h) | Out-Null
    [RestoreCap]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 180
    if ([RestoreCap]::GetForegroundWindow() -eq $h) { return $true }
  }
  return $false
}
function KeyTap($vk, $sc) {
  [RestoreCap]::keybd_event($vk, $sc, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 70
  [RestoreCap]::keybd_event($vk, $sc, 2, [UIntPtr]::Zero)
}
$logPath = "C:\MinecraftModding\mods\finery\wn_restore_capture_log.txt"
"start $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Encoding ASCII
$deadline = (Get-Date).AddSeconds(240)
$proc = $null
do {
  Start-Sleep -Seconds 2
  $proc = Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
} while (-not $proc -and (Get-Date) -lt $deadline)
if (-not $proc) { "NO_WINDOW" | Out-File $logPath -Append -Encoding ASCII; exit }
$h = $proc.MainWindowHandle
"pid=$($proc.Id)" | Out-File $logPath -Append -Encoding ASCII
$joined = $false
$deadline = (Get-Date).AddSeconds(120)
do {
  Start-Sleep -Milliseconds 700
  $tail = Get-Content "C:\MinecraftModding\mods\finery\run\logs\latest.log" -Tail 120 -ErrorAction SilentlyContinue
  if ($tail -match 'VUO_ joined the game') { $joined = $true; break }
} while ((Get-Date) -lt $deadline)
"joined=$joined $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
if ($joined) {
  Start-Sleep -Seconds 3
  $ok = Activate $h
  "activated=$ok" | Out-File $logPath -Append -Encoding ASCII
  KeyTap 0x74 0x3F
  Start-Sleep -Milliseconds 1200
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 1200
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 1000
  KeyTap 0x20 0x39
  Start-Sleep -Milliseconds 260
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 240
  KeyTap 0x71 0x3C
  Get-ChildItem "C:\MinecraftModding\mods\finery\run\screenshots" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 6 Name, LastWriteTime | Out-File $logPath -Append -Encoding ASCII
}
"done $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
