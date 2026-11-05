$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class GW {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);
  public struct RECT { public int L,T,R,B; }
}
"@

function Activate($h) {
  for ($i = 0; $i -lt 6; $i++) {
    [GW]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [GW]::SetForegroundWindow($h) | Out-Null
    [GW]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 250
    if ([GW]::GetForegroundWindow() -eq $h) { return $true }
  }
  return $false
}

function KeyTap($vk) {
  [GW]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 70
  [GW]::keybd_event($vk, 0, 2, [UIntPtr]::Zero)
}

$log = "C:\MinecraftModding\mods\finery\wing_capture_log.txt"
"start $(Get-Date -Format HH:mm:ss)" | Out-File $log -Encoding ASCII

Start-Sleep -Seconds 6

$proc = Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
if (-not $proc) { "NO_GAME" | Out-File $log -Append -Encoding ASCII; exit }
$h = $proc.MainWindowHandle
"pid=$($proc.Id)" | Out-File $log -Append -Encoding ASCII

$ok = Activate $h
"activated=$ok" | Out-File $log -Append -Encoding ASCII

$r = New-Object GW+RECT
[GW]::GetWindowRect($h, [ref]$r) | Out-Null
"rect=$($r.L),$($r.T),$($r.R),$($r.B)" | Out-File $log -Append -Encoding ASCII

$x = $r.L + 370
$y = $r.T + 162
[GW]::SetCursorPos($x, $y) | Out-Null
Start-Sleep -Milliseconds 150
[GW]::mouse_event(0x02, 0, 0, 0, [UIntPtr]::Zero)
[GW]::mouse_event(0x04, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 90
[GW]::mouse_event(0x02, 0, 0, 0, [UIntPtr]::Zero)
[GW]::mouse_event(0x04, 0, 0, 0, [UIntPtr]::Zero)
"doubleclicked_world x=$x y=$y" | Out-File $log -Append -Encoding ASCII

Start-Sleep -Seconds 20
$ok = Activate $h
"reactivated=$ok" | Out-File $log -Append -Encoding ASCII

KeyTap 0x74
Start-Sleep -Milliseconds 900
"f5_sent" | Out-File $log -Append -Encoding ASCII

[GW]::MoveWindow($h, 100, 40, 1720, 980, $true) | Out-Null
Start-Sleep -Seconds 3
$ok = Activate $h
"sized_activated=$ok" | Out-File $log -Append -Encoding ASCII

KeyTap 0x71
Start-Sleep -Milliseconds 1200
"f2_sent" | Out-File $log -Append -Encoding ASCII

$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save("C:\MinecraftModding\mods\finery\wing_ingame_desktop.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"done $(Get-Date -Format HH:mm:ss)" | Out-File $log -Append -Encoding ASCII
