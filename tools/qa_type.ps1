$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class QType {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern void keybd_event(byte v, byte s, uint f, UIntPtr e);
}
"@

$p = Get-Process java* -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
if (-not $p) { Write-Output 'NO_GAME'; exit 1 }
$h = $p.MainWindowHandle
for ($i = 0; $i -lt 6; $i++) {
  [QType]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
  [QType]::SetForegroundWindow($h) | Out-Null
  [QType]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 200
  if ([QType]::GetForegroundWindow() -eq $h) { break }
}
Start-Sleep -Milliseconds 400

function Tap([byte]$vk) {
  [QType]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 45
  [QType]::keybd_event($vk, 0, 2, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 45
}

# close any open screen/chat first
Tap 0x1B
Start-Sleep -Milliseconds 600

foreach ($cmd in $args) {
  $text = '/' + $cmd
  Tap 0x54                     # t -> open chat
  Start-Sleep -Milliseconds 700
  foreach ($ch in $text.ToCharArray()) {
    if ($ch -eq '_') {
      [QType]::keybd_event(0x10, 0, 0, [UIntPtr]::Zero)
      Tap 0xBD                 # minus
      [QType]::keybd_event(0x10, 0, 2, [UIntPtr]::Zero)
      Start-Sleep -Milliseconds 45
    } elseif ($ch -eq '/') {
      Tap 0xBF
    } elseif ($ch -eq ' ') {
      Tap 0x20
    } else {
      Tap ([byte][char]([string]$ch).ToUpper())
    }
  }
  Start-Sleep -Milliseconds 250
  Tap 0x0D                     # enter
  Start-Sleep -Milliseconds 900
}
Write-Output 'DONE'
