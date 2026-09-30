"""typo capture, port of `windows/scripts/make_dictionary.ahk`"""

import re
import time
from pathlib import Path

from evdev import ecodes
from gi.repository import GLib

from keyboard import clipboard_reset, clipboard_restore, clipboard_save, clipboard_wait

ROOT = Path(__file__).resolve().parent.parent
AHK_DICTIONARY = ROOT / "windows" / "auto.ahk"
ESPANSO_DICTIONARY = ROOT / "Espanso" / ".espanso" / "match" / "auto.yml"

CAPTURE_KEYS = {ecodes.KEY_SPACE, ecodes.KEY_ENTER, ecodes.KEY_KPENTER, ecodes.KEY_TAB}

learn_wrong = ""


def capture(keyboard):
    global learn_wrong

    old_clip = clipboard_save()
    if not clipboard_reset():
        return

    keyboard.send("ctrl+shift+left")
    time.sleep(0.03)
    keyboard.send("ctrl+c")
    copied = clipboard_wait(0.5)
    if copied is None:
        clipboard_restore(old_clip)
        return

    learn_wrong = copied.strip(" \t\r\n")

    keyboard.send("backspace")

    clipboard_restore(old_clip)


def on_key(keyboard, code, value):
    """physical keyboard listener: after `capture`, the correct word is typed and ended by Space / Enter / Tab"""
    global learn_wrong

    if not learn_wrong or value != 1:
        return
    if code == ecodes.KEY_ESC:
        learn_wrong = ""
    elif code in CAPTURE_KEYS:
        # the key goes to the application too (like AHK `~Space`), give it time to arrive there first
        GLib.timeout_add(50, lambda: log_correction(keyboard) and False)


# a single word: letters, digits, apostrophe, hyphen; anything else could break the AHK or YAML syntax
def is_word(text):
    return re.fullmatch(r"(?:[^\W_]|['-])+", text) is not None


def append_correction(wrong, correct):
    # skip already captured words (with any hotstring options), keeps the dictionary free of duplicates
    if AHK_DICTIONARY.exists():
        content = AHK_DICTIONARY.read_text(encoding="utf-8")
        if not re.search("(?m)^:[^:]*:" + re.escape(wrong) + "::", content):
            with AHK_DICTIONARY.open("a", encoding="utf-8") as file:
                file.write("::" + wrong + "::" + correct + "\n")

    # Espanso reloads `auto.yml` on its own
    if ESPANSO_DICTIONARY.exists():
        content = ESPANSO_DICTIONARY.read_text(encoding="utf-8")
        if 'trigger: "' + wrong + '"' not in content:
            entry = ("\n"
                     '  - trigger: "' + wrong + '"\n'
                     '    replace: "' + correct + '"\n'
                     "    word: true\n"
                     "    propagate_case: true\n")
            with ESPANSO_DICTIONARY.open("a", encoding="utf-8") as file:
                file.write(entry)


def log_correction(keyboard):
    global learn_wrong

    if not learn_wrong or not keyboard.wait_for_modifiers_release():
        learn_wrong = ""
        return

    old_clip = clipboard_save()
    if not clipboard_reset():
        learn_wrong = ""
        return

    keyboard.send("left")
    keyboard.send("ctrl+shift+left")
    time.sleep(0.03)
    keyboard.send("ctrl+c")
    copied = clipboard_wait(0.5)
    if copied is None:
        keyboard.send("right")
        clipboard_restore(old_clip)
        learn_wrong = ""
        return

    correct = copied.strip(" \t\r\n")

    keyboard.send("right", "right")

    if is_word(learn_wrong) and is_word(correct) and learn_wrong != correct:
        append_correction(learn_wrong, correct)
        print(f"captured: {learn_wrong} -> {correct}", flush=True)

    learn_wrong = ""
    clipboard_restore(old_clip)


ACTIONS = {
    "capture": ("Delete previous word and capture its correction", ["ctrl+meta+backspace"], capture),
}
