$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PG {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
  public struct RECT { public int L,T,R,B; }
  public struct POINT { public int X,Y; }
}
"@
function Activate($h) {
  for ($i = 0; $i -lt 8; $i++) {
    [PG]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [PG]::SetForegroundWindow($h) | Out-Null
    [PG]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 200
    if ([PG]::GetForegroundWindow() -eq $h) { return $true }
  }
  return $false
}
function KeyTap($vk, $sc) {
  [PG]::keybd_event($vk, $sc, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 70
  [PG]::keybd_event($vk, $sc, 2, [UIntPtr]::Zero)
}
function ClickAt($x, $y) {
  [PG]::SetCursorPos($x, $y) | Out-Null
  Start-Sleep -Milliseconds 140
  [PG]::mouse_event(0x02, 0, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [PG]::mouse_event(0x04, 0, 0, 0, [UIntPtr]::Zero)
}
$logPath = "C:\MinecraftModding\mods\finery\wing_capture_log2.txt"
"start $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Encoding ASCII
Start-Sleep -Seconds 3
$proc = Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
if (-not $proc) { "NO_GAME" | Out-File $logPath -Append -Encoding ASCII; exit }
$h = $proc.MainWindowHandle
$pt = New-Object PG+POINT
[PG]::ClientToScreen($h, [ref]$pt) | Out-Null
"pid=$($proc.Id) clientorigin=$($pt.X),$($pt.Y)" | Out-File $logPath -Append -Encoding ASCII
$ok = Activate $h
"activated=$ok" | Out-File $logPath -Append -Encoding ASCII
ClickAt ($pt.X + 860) ($pt.Y + 361)
"singleplayer_click" | Out-File $logPath -Append -Encoding ASCII
Start-Sleep -Milliseconds 1600
$ok = Activate $h
"react1=$ok" | Out-File $logPath -Append -Encoding ASCII
ClickAt ($pt.X + 860) ($pt.Y + 132)
Start-Sleep -Milliseconds 500
ClickAt ($pt.X + 860) ($pt.Y + 132)
Start-Sleep -Milliseconds 600
ClickAt ($pt.X + 702) ($pt.Y + 896)
"world_click" | Out-File $logPath -Append -Encoding ASCII
$joined = $false
$deadline = (Get-Date).AddSeconds(45)
do {
  Start-Sleep -Milliseconds 500
  $tail = Get-Content "C:\MinecraftModding\mods\finery\run\logs\latest.log" -Tail 80 -ErrorAction SilentlyContinue
  if ($tail -match 'VUO_ joined the game') { $joined = $true; break }
} while ((Get-Date) -lt $deadline)
"joined=$joined $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
if ($joined) {
  Start-Sleep -Milliseconds 400
  $ok = Activate $h
  "react2=$ok" | Out-File $logPath -Append -Encoding ASCII
  KeyTap 0x74 0x3F
  Start-Sleep -Milliseconds 800
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 900
  KeyTap 0x71 0x3C
  Start-Sleep -Milliseconds 700
  Get-ChildItem "C:\MinecraftModding\mods\finery\run\screenshots" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 Name, LastWriteTime | Out-File $logPath -Append -Encoding ASCII
}
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save("C:\MinecraftModding\mods\finery\wing_ingame_desktop.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"done $(Get-Date -Format HH:mm:ss)" | Out-File $logPath -Append -Encoding ASCII
