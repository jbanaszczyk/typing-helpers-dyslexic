#!/usr/bin/env python3
"""Typing helpers for KDE Plasma (Wayland), Linux counterpart of `AutoHotkey.ahk`.

Hotkeys are KDE global shortcuts (component "Typing helpers" in System Settings → Keyboard → Shortcuts),
registered over DBus at start. Autocorrect is left to Espanso, restarted when a keyboard is plugged in and by `Ctrl + Meta + Down`.
"""

import signal
import sys
import traceback

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import espanso_restart
import make_dictionary
import sequence_fixes
from keyboard import Keyboard

COMPONENT = "typing-helpers"
COMPONENT_NAME = "Typing helpers"

# kglobalaccel `SetShortcutFlag`
SET_PRESENT = 2
NO_AUTOLOADING = 4
IS_DEFAULT = 8

# Qt key codes, as kglobalaccel expects them over DBus
QT_MODIFIERS = {"ctrl": 0x04000000, "shift": 0x02000000, "alt": 0x08000000, "meta": 0x10000000}
QT_KEYS = {"left": 0x01000012, "up": 0x01000013, "right": 0x01000014, "down": 0x01000015,
           "backspace": 0x01000003}

# swap before espanso-restart: an older swap default held Ctrl+Meta+Down
ACTIONS = {**sequence_fixes.ACTIONS, **make_dictionary.ACTIONS, **espanso_restart.ACTIONS}


def qt_key(combo):
    """"ctrl+meta+left" -> Qt key code"""
    *modifiers, key = combo.split("+")
    code = QT_KEYS.get(key) or ord(key.upper())
    for modifier in modifiers:
        code |= QT_MODIFIERS[modifier]
    return code


def qt_shortcuts(combos):
    # a QKeySequence is sent as 4 ints (chord), unused ones 0
    return dbus.Array([dbus.Struct([dbus.Array([qt_key(c), 0, 0, 0], signature="i")], signature="ai")
                       for c in combos], signature="(ai)")


class TypingHelpers:
    def __init__(self):
        self.keyboard = Keyboard()
        self.keyboard.listeners.append(lambda code, value: make_dictionary.on_key(self.keyboard, code, value))
        self.keyboard.plug_listeners.append(lambda: espanso_restart.on_keyboard_plugged(self.keyboard))
        if not self.keyboard.devices:
            print("no keyboard readable in /dev/input - is the user in the `input` group?", file=sys.stderr)

        bus = dbus.SessionBus()
        self.kglobalaccel = dbus.Interface(bus.get_object("org.kde.kglobalaccel", "/kglobalaccel"),
                                           "org.kde.KGlobalAccel")
        for action, (label, combos, _function) in ACTIONS.items():
            action_id = self.action_id(action, label)
            self.kglobalaccel.doRegister(action_id)
            # keys changed in System Settings are kept; keys still at the old default follow a changed default
            customized = self.kglobalaccel.shortcutKeys(action_id) != self.kglobalaccel.defaultShortcutKeys(action_id)
            self.kglobalaccel.setShortcutKeys(action_id, qt_shortcuts(combos), dbus.UInt32(IS_DEFAULT))
            flags = SET_PRESENT if customized else SET_PRESENT | NO_AUTOLOADING
            active = self.kglobalaccel.setShortcutKeys(action_id, qt_shortcuts(combos), dbus.UInt32(flags))
            if len(active) < len(combos):
                print(f"{action}: some of {combos} not assigned, taken by another shortcut?", file=sys.stderr)

        component = self.kglobalaccel.getComponent(COMPONENT)
        bus.add_signal_receiver(self.on_shortcut, signal_name="globalShortcutPressed",
                                dbus_interface="org.kde.kglobalaccel.Component", path=component)

    @staticmethod
    def action_id(action, label):
        return dbus.Array([COMPONENT, action, COMPONENT_NAME, label], signature="s")

    def on_shortcut(self, _component, action, _timestamp):
        if action not in ACTIONS:
            return
        if not self.keyboard.wait_for_modifiers_release():
            print(f"{action}: modifiers still held, skipped", file=sys.stderr)
            return
        try:
            ACTIONS[action][2](self.keyboard)
        except Exception:
            traceback.print_exc()

    def close(self):
        # without this the keys stay grabbed by KDE, doing nothing
        for action, (label, _combos, _function) in ACTIONS.items():
            try:
                self.kglobalaccel.setInactive(self.action_id(action, label))
            except dbus.DBusException:
                pass
        self.keyboard.close()


def main():
    DBusGMainLoop(set_as_default=True)
    helpers = TypingHelpers()
    loop = GLib.MainLoop()
    for signum in (signal.SIGTERM, signal.SIGINT):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signum, loop.quit)
    print("typing helpers running", flush=True)
    try:
        loop.run()
    finally:
        helpers.close()


if __name__ == "__main__":
    main()
