"""Keyboard and clipboard I/O on KDE Plasma (Wayland).

- keys are injected through a uinput virtual keyboard (needs write access to /dev/uinput)
- physical keyboards are read through evdev, without grabbing (needs read access to /dev/input/event*)
- the clipboard is handled by wl-clipboard (KWin supports the data-control protocol)
"""

import subprocess
import time

import evdev
from evdev import ecodes
from gi.repository import GLib

NAME = "typing-helpers"
KEY_DELAY = 0.01  # like AHK `SetKeyDelay 0, 10`

MODIFIERS = {
    ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
    ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT,
    ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
    ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA,
}

KEY_ALIASES = {
    "ctrl": ecodes.KEY_LEFTCTRL,
    "shift": ecodes.KEY_LEFTSHIFT,
    "alt": ecodes.KEY_LEFTALT,
    "meta": ecodes.KEY_LEFTMETA,
}

# set while waiting for a copy; Klipper's "prevent empty clipboard" makes clearing the clipboard unreliable
CLIPBOARD_SENTINEL = "typing-helpers: waiting for copy"


def parse_combo(combo):
    """"ctrl+shift+left" -> [KEY_LEFTCTRL, KEY_LEFTSHIFT, KEY_LEFT]"""
    return [KEY_ALIASES.get(name) or ecodes.ecodes["KEY_" + name.upper()] for name in combo.split("+")]


class Keyboard:
    def __init__(self):
        self.output = evdev.UInput(name=NAME)
        self.devices = {}  # path -> evdev.InputDevice
        self.listeners = []  # callables (key code, value), value: 1 press, 0 release, 2 autorepeat
        self.scan()
        GLib.timeout_add_seconds(3, self.scan)  # keyboards plugged in later

    # ---------- input

    def scan(self):
        for path in evdev.list_devices():
            if path in self.devices:
                continue
            try:
                device = evdev.InputDevice(path)
            except OSError:
                continue
            keys = device.capabilities().get(ecodes.EV_KEY, [])
            if device.name == NAME or ecodes.KEY_SPACE not in keys or ecodes.KEY_A not in keys:
                device.close()
                continue
            self.devices[path] = device
            conditions = GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP | GLib.IO_NVAL
            GLib.io_add_watch(device.fd, GLib.PRIORITY_DEFAULT, conditions, self.on_input, path)
        return True

    def drop(self, path):
        device = self.devices.pop(path, None)
        if device:
            try:
                device.close()
            except OSError:
                pass

    def on_input(self, _fd, _condition, path):
        device = self.devices.get(path)
        if device is None:
            return False
        try:
            events = list(device.read())
        except BlockingIOError:
            return True
        except OSError:  # unplugged
            self.drop(path)
            return False
        for event in events:
            if event.type == ecodes.EV_KEY:
                for listener in self.listeners:
                    listener(event.code, event.value)
        return True

    def held_keys(self):
        held = set()
        for path, device in list(self.devices.items()):
            try:
                held.update(device.active_keys())
            except OSError:
                self.drop(path)
        return held

    def wait_for_modifiers_release(self, timeout=3.0):
        """The hotkey modifiers are still physically held when KDE reports the shortcut.
        A virtual keyboard cannot release keys held on another device, so wait for the user to release them."""
        deadline = time.monotonic() + timeout
        while self.held_keys() & MODIFIERS:
            if time.monotonic() > deadline:
                return False
            time.sleep(0.01)
        return True

    # ---------- output

    def send(self, *combos):
        """send("ctrl+left", "backspace") - each combo is pressed, then released in reverse order"""
        for combo in combos:
            keys = parse_combo(combo)
            for key in keys:
                self.output.write(ecodes.EV_KEY, key, 1)
                self.output.syn()
                time.sleep(KEY_DELAY)
            for key in reversed(keys):
                self.output.write(ecodes.EV_KEY, key, 0)
                self.output.syn()
                time.sleep(KEY_DELAY)

    def close(self):
        self.output.close()
        for path in list(self.devices):
            self.drop(path)


# ---------- clipboard

def clipboard_save():
    """-> (mime type, data) of the current clipboard, None if empty; one type only, preferring text"""
    listed = subprocess.run(["wl-paste", "--list-types"], capture_output=True, text=True)
    types = listed.stdout.split("\n") if listed.returncode == 0 else []
    types = [t for t in types if t]
    if not types:
        return None
    mime = "text/plain;charset=utf-8" if "text/plain;charset=utf-8" in types else types[0]
    data = subprocess.run(["wl-paste", "--no-newline", "--type", mime], capture_output=True)
    return (mime, data.stdout) if data.returncode == 0 else None


def clipboard_restore(saved):
    if saved is None:
        subprocess.run(["wl-copy", "--clear"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    mime, data = saved
    subprocess.run(["wl-copy", "--type", mime], input=data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def clipboard_text():
    result = subprocess.run(["wl-paste", "--no-newline", "--type", "text"], capture_output=True)
    return result.stdout.decode("utf-8", "replace") if result.returncode == 0 else None


def clipboard_reset():
    """Put the sentinel into the clipboard and wait until it is really there (wl-copy sets it in background)"""
    subprocess.run(["wl-copy", CLIPBOARD_SENTINEL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return clipboard_wait(0.3, lambda text: text == CLIPBOARD_SENTINEL) is not None


def clipboard_wait(timeout, accept=lambda text: text and text != CLIPBOARD_SENTINEL):
    """like AHK `ClipWait` after `clipboard_reset()`: -> the new clipboard text, None on timeout"""
    deadline = time.monotonic() + timeout
    while True:
        text = clipboard_text()
        if text is not None and accept(text):
            return text
        if time.monotonic() > deadline:
            return None
        time.sleep(0.02)
