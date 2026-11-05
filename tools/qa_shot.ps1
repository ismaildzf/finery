$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class QShot {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, uint f, UIntPtr e);
  public struct RECT { public int L,T,R,B; }
}
"@

$out = $args[0]
if (-not $out) { $out = "C:\MinecraftModding\mods\finery\qa_shot.png" }

$proc = Get-Process java* -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
if (-not $proc) { Write-Output 'NO_GAME'; exit 1 }

$h = $proc.MainWindowHandle
for ($i = 0; $i -lt 6; $i++) {
  [QShot]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
  [QShot]::SetForegroundWindow($h) | Out-Null
  [QShot]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 250
  if ([QShot]::GetForegroundWindow() -eq $h) { break }
}
Start-Sleep -Milliseconds 700

$r = New-Object QShot+RECT
[QShot]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.R - $r.L
$ht = $r.B - $r.T
if ($w -le 0 -or $ht -le 0) { Write-Output 'BAD_RECT'; exit 1 }

$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "SAVED $out ${w}x${ht}"
