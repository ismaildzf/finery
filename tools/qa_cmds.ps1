$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class QC {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern void keybd_event(byte v, byte s, uint f, UIntPtr e);
}
"@

$p = Get-Process java* -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like 'Minecraft*' } | Select-Object -First 1
if (-not $p) { Write-Output 'NO_GAME'; exit 1 }
$h = $p.MainWindowHandle
for ($i = 0; $i -lt 5; $i++) {
  [QC]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
  [QC]::SetForegroundWindow($h) | Out-Null
  [QC]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 200
  if ([QC]::GetForegroundWindow() -eq $h) { break }
}
Start-Sleep -Milliseconds 500

foreach ($cmd in $args) {
  $text = '/' + $cmd
  [System.Windows.Forms.SendKeys]::SendWait('t')
  Start-Sleep -Milliseconds 500
  [System.Windows.Forms.SendKeys]::SendWait($text)
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
  Start-Sleep -Milliseconds 700
}
Write-Output 'CMDS_SENT'
