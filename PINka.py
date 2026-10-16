import ctypes
import os
from ctypes import wintypes

import win32con
import win32gui

APP_NAME = "PINka"
HOTKEY_TOGGLE_ID = 1
HOTKEY_EXIT_ID = 2

VK_T = 0x54  # Клавиша T
VK_OEM_6 = 0xDD  # Клавиша ] (буква Ъ)


def show_notice():
    msg = (
        "PINka запущена!\n\n"
        "• Ctrl + Alt + T — Закрепить / Открепить текущее окно\n"
        "• Ctrl + Alt + ] — Закрыть утилиту\n\n"
        "Нажмите OK и перейдите в нужное окно."
    )
    win32gui.MessageBox(0, msg, APP_NAME, win32con.MB_ICONINFORMATION | win32con.MB_OK)


def pin_top():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return

    # Игнорируем рабочий стол и панель задач Windows
    class_name = win32gui.GetClassName(hwnd)
    if class_name in [
        "Progman",
        "WorkerW",
        "Shell_TrayWnd",
        "Shell_SecondaryTrayWnd",
    ]:
        return

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    is_topmost = bool(ex_style & win32con.WS_EX_TOPMOST)

    if is_topmost:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        ctypes.windll.user32.MessageBeep(0xFFFFFFFF)  # Звук открепления (низкий тон)
    else:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        ctypes.windll.user32.MessageBeep(0x00000040)  # Звук закрепления (дзинь)


def main():
    show_notice()

    user32 = ctypes.windll.user32

    # Регистрируем сочетания клавиш
    reg_t = user32.RegisterHotKey(
        None,
        HOTKEY_TOGGLE_ID,
        win32con.MOD_CONTROL | win32con.MOD_ALT,
        VK_T,
    )
    reg_exit = user32.RegisterHotKey(
        None,
        HOTKEY_EXIT_ID,
        win32con.MOD_CONTROL | win32con.MOD_ALT,
        VK_OEM_6,
    )

    if not reg_t or not reg_exit:
        win32gui.MessageBox(
            0,
            "Ошибка: Сочетания клавиш уже используются другой программой!",
            APP_NAME,
            win32con.MB_ICONERROR,
        )
        return

    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                if msg.wParam == HOTKEY_TOGGLE_ID:
                    pin_top()
                elif msg.wParam == HOTKEY_EXIT_ID:
                    ctypes.windll.user32.MessageBeep(0x00000010)
                    break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    finally:
        user32.UnregisterHotKey(None, HOTKEY_TOGGLE_ID)
        user32.UnregisterHotKey(None, HOTKEY_EXIT_ID)


if __name__ == "__main__":
    main()
