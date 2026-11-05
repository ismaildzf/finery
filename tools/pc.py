"""Tiny Windows desktop driver: screenshots, clicks, keys, clipboard typing.

Usage examples:
  python pc.py shot out.png
  python pc.py click 640 400
  python pc.py key f5
  python pc.py type "/give @p finery:seraph_ai"
  python pc.py focus
"""
import ctypes
import subprocess
import sys
import time

from PIL import ImageGrab

user32 = ctypes.windll.user32

VK = {
    "esc": 0x1B, "enter": 0x0D, "space": 0x20, "tab": 0x09, "backspace": 0x08,
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74,
    "e": 0x45, "t": 0x54, "v": 0x56, "w": 0x57, "a": 0x41, "s": 0x53, "d": 0x44,
    "q": 0x51, "c": 0x43, "x": 0x58, "z": 0x5A, "r": 0x52, "p": 0x50, "k": 0x4B,
    "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34, "5": 0x35,
}
KEYEVENTF_KEYUP = 0x0002


def shot(path):
    img = ImageGrab.grab()
    img.save(path)
    return img


def click(x, y, button="left"):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.08)
    if button == "left":
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
    else:
        user32.mouse_event(0x0008, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(0x0010, 0, 0, 0, 0)
    time.sleep(0.12)


def double_click(x, y):
    click(x, y)
    time.sleep(0.06)
    click(x, y)


def key_down(name):
    user32.keybd_event(VK[name], 0, 0, 0)


def key_up(name):
    user32.keybd_event(VK[name], 0, KEYEVENTF_KEYUP, 0)


def press(name, hold=0.06):
    key_down(name)
    time.sleep(hold)
    key_up(name)
    time.sleep(0.08)



def press_many(name, n=40, gap=0.008):
    """Tap one key n times quickly (used to clear a text field)."""
    vk = VK[name]
    for _ in range(n):
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(gap)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(gap)
    time.sleep(0.05)
def focus(title="Minecraft"):
    """Bring a window whose title contains `title` to the foreground."""
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        found = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def enum_proc(h, _):
            length = user32.GetWindowTextLengthW(h)
            if length:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(h, buf, length + 1)
                if title.lower() in buf.value.lower() and user32.IsWindowVisible(h):
                    found.append(h)
            return True

        user32.EnumWindows(enum_proc, 0)
        hwnd = found[0] if found else 0
    if not hwnd:
        return False
    user32.ShowWindow(hwnd, 9)   # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    time.sleep(0.35)
    return True



def type_raw(text):
    """Type ASCII char by char with keybd_event (no clipboard, no focus steal).

    Letters are mapped explicitly because the active Windows layout may be
    Arabic, which makes VkKeyScanW return 0xFFFF for A-Z.
    """
    user32.VkKeyScanW.restype = ctypes.c_short
    user32.VkKeyScanW.argtypes = [ctypes.c_wchar]
    for ch in text:
        shift = False
        if "a" <= ch <= "z":
            vk = 0x41 + (ord(ch) - ord("a"))
        elif "A" <= ch <= "Z":
            vk = 0x41 + (ord(ch) - ord("A"))
            shift = True
        elif "0" <= ch <= "9":
            vk = 0x30 + (ord(ch) - ord("0"))
        elif ch == " ":
            vk = 0x20
        else:
            scan = user32.VkKeyScanW(ch)
            if scan == -1 or (scan & 0xFFFF) == 0xFFFF:
                continue
            vk = scan & 0xFF
            shift = bool((scan >> 8) & 1)
        if shift:
            key_down("shift")
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        if shift:
            key_up("shift")
        time.sleep(0.035)
    time.sleep(0.05)


def set_clipboard(text, tries=12):
    """Set the text clipboard through the Win32 API (survives locks/other apps)."""
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    CF_UNICODETEXT, GMEM_MOVEABLE = 13, 0x0002
    data = text.encode("utf-16-le") + b"\x00\x00"
    for _ in range(tries):
        if user32.OpenClipboard(None):
            try:
                user32.EmptyClipboard()
                handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
                if handle:
                    ptr = kernel32.GlobalLock(handle)
                    ctypes.memmove(ptr, data, len(data))
                    kernel32.GlobalUnlock(handle)
                    user32.SetClipboardData(CF_UNICODETEXT, handle)
                return True
            finally:
                user32.CloseClipboard()
        time.sleep(0.25)
    return False


def paste_text(text):
    """Paste text into the focused window via the clipboard (layout independent)."""
    if not set_clipboard(text):
        return False
    time.sleep(0.12)
    key_down("ctrl")
    press("v")
    key_up("ctrl")
    time.sleep(0.12)
    return True


def type_text(text):
    subprocess.run(["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Value "{text}"'],
                   check=True)
    time.sleep(0.15)
    key_down("ctrl")
    press("v")
    key_up("ctrl")
    time.sleep(0.15)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "shot":
        shot(sys.argv[2])
    elif cmd == "click":
        click(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == "dclick":
        double_click(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == "key":
        press(sys.argv[2])
    elif cmd == "type":
        type_text(sys.argv[2])
    elif cmd == "raw":
        type_raw(sys.argv[2])
    elif cmd == "focus":
        print(focus())
    else:
        print("unknown command")
