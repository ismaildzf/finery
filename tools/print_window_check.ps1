$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PW {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
  public struct RECT { public int L,T,R,B; }
  public struct POINT { public int X,Y; }
}
"@
$deadline = (Get-Date).AddSeconds(150)
$proc = $null
do {
  Start-Sleep -Seconds 2
  $proc = Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
} while (-not $proc -and (Get-Date) -lt $deadline)
if (-not $proc) { "NO_WINDOW"; exit 1 }
$h = $proc.MainWindowHandle
Start-Sleep -Seconds 3
$wr = New-Object PW+RECT
[PW]::GetWindowRect($h, [ref]$wr) | Out-Null
$cr = New-Object PW+RECT
[PW]::GetClientRect($h, [ref]$cr) | Out-Null
$pt = New-Object PW+POINT
[PW]::ClientToScreen($h, [ref]$pt) | Out-Null
"pid=$($proc.Id) window=$($wr.L),$($wr.T),$($wr.R),$($wr.B) client=$($cr.R)x$($cr.B) clientorigin=$($pt.X),$($pt.Y)" | Out-File "C:\MinecraftModding\mods\finery\printwindow_log.txt" -Encoding ASCII
$w = $cr.R
$hh = $cr.B
if ($w -le 0 -or $hh -le 0) { "BAD_CLIENT"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [PW]::PrintWindow($h, $hdc, 2)
$g.ReleaseHdc($hdc)
$g.Dispose()
$bmp.Save("C:\MinecraftModding\mods\finery\wing_printwindow.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"printwindow=$ok" | Out-File "C:\MinecraftModding\mods\finery\printwindow_log.txt" -Append -Encoding ASCII
