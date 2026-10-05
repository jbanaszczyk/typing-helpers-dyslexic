"""space / transposition fixes, port of `windows/scripts/sequence_fixes.ahk`"""

import time

from keyboard import clipboard_reset, clipboard_restore, clipboard_save, clipboard_wait


# ---------- space fixes

def fix_early_space(keyboard):
    keyboard.send("ctrl+left", "backspace", "right", "space", "ctrl+right")


def fix_late_space(keyboard):
    keyboard.send("ctrl+left", "backspace", "left", "space", "ctrl+right")


# ---------- transposition fix

def swap_chars_around_cursor(keyboard):
    old_clip = clipboard_save()
    if not clipboard_reset():
        return

    # copy left char, then delete it
    keyboard.send("shift+left")
    time.sleep(0.03)
    keyboard.send("ctrl+x")
    if clipboard_wait(0.5) is None:
        clipboard_restore(old_clip)
        return

    keyboard.send("right")
    time.sleep(0.03)
    keyboard.send("ctrl+v")
    time.sleep(0.03)
    keyboard.send("left")

    time.sleep(0.1)  # let the application finish pasting
    clipboard_restore(old_clip)


ACTIONS = {
    # action: (label in KDE System Settings, default keys, function)
    "early-space": ("Fix early space (pojedyncz alitera)", ["ctrl+meta+right"], fix_early_space),
    "late-space": ("Fix late space (pojedynczal itera)", ["ctrl+meta+left"], fix_late_space),
    "swap": ("Swap characters around cursor", ["ctrl+meta+up"], swap_chars_around_cursor),
}
