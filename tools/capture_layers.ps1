$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class LayerCap {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
  public struct POINT { public int X,Y; }
}
"@
function Activate($h) {
  for ($i = 0; $i -lt 10; $i++) {
    [LayerCap]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [LayerCap]::SetForegroundWindow($h) | Out-Null
    [LayerCap]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 180
    if ([LayerCap]::GetForegroundWindow() -eq $h) { return $true }
  }
  return $false
}
function KeyTap($vk, $sc) {
  [LayerCap]::keybd_event($vk, $sc, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 70
  [LayerCap]::keybd_event($vk, $sc, 2, [UIntPtr]::Zero)
}
function ClickAt($x, $y) {
  [LayerCap]::SetCursorPos($x, $y) | Out-Null
  Start-Sleep -Milliseconds 140
  [LayerCap]::mouse_event(0x02, 0, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [LayerCap]::mouse_event(0x04, 0, 0, 0, [UIntPtr]::Zero)
}
$logPath = "C:\MinecraftModding\mods\finery\wn_layers_capture_log.txt"
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
Start-Sleep -Seconds 10
$pt = New-Object LayerCap+POINT
[LayerCap]::ClientToScreen($h, [ref]$pt) | Out-Null
"clientorigin=$($pt.X),$($pt.Y)" | Out-File $logPath -Append -Encoding ASCII
$ok = Activate $h
"activated=$ok" | Out-File $logPath -Append -Encoding ASCII
ClickAt ($pt.X + 860) ($pt.Y + 361)
Start-Sleep -Milliseconds 1800
$ok = Activate $h
"react1=$ok" | Out-File $logPath -Append -Encoding ASCII
ClickAt ($pt.X + 860) ($pt.Y + 132)
Start-Sleep -Milliseconds 500
ClickAt ($pt.X + 860) ($pt.Y + 132)
Start-Sleep -Milliseconds 500
ClickAt ($pt.X + 702) ($pt.Y + 896)
"world_click" | Out-File $logPath -Append -Encoding ASCII
$joined = $false
$deadline = (Get-Date).AddSeconds(90)
do {
  Start-Sleep -Milliseconds 500
  $tail = Get-Content "C:\MinecraftModding\mods\finery\run\logs\latest.log" -Tail 100 -ErrorAction SilentlyContinue
  if ($tail -match 'VUO_ joined the game') { $joined = $true; break }
} while ((Get-Date) -lt $deadline)
"joined=$joined $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
if ($joined) {
  Start-Sleep -Seconds 2
  $ok = Activate $h
  "react2=$ok" | Out-File $logPath -Append -Encoding ASCII
  KeyTap 0x74 0x3F
  Start-Sleep -Milliseconds 1200
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 1400
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 1400
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 1000
  KeyTap 0x20 0x39
  Start-Sleep -Milliseconds 260
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 240
  KeyTap 0x71 0x3C
  Get-ChildItem "C:\MinecraftModding\mods\finery\run\screenshots" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 8 Name, LastWriteTime | Out-File $logPath -Append -Encoding ASCII
}
"done $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
