# Linux notes

How the Linux hotkey service works and why it is built this way. Written for someone who knows Linux from the
terminal, but not the desktop side. Setup is in [README → Linux (hotkeys)](../README.md#linux-hotkeys).

---

## Background: why there is no AutoHotkey on Linux

Kubuntu here runs **Wayland**. Wayland is the protocol between applications and the **compositor** — in KDE that is
**KWin**, which draws the windows and is the only one receiving all keys. Wayland isolates applications on purpose:
an ordinary program cannot

- listen to keys pressed in another window,
- send keys to another window.

On Windows AutoHotkey does both without asking; on the older X11 display server `xdotool` did. On Wayland each need
goes through a separate side door:

| Need                          | Mechanism                                                                                  | AutoHotkey equivalent         |
|-------------------------------|--------------------------------------------------------------------------------------------|-------------------------------|
| catch a hotkey                | ask KWin through **DBus** (message bus between desktop programs), service `kglobalaccel`   | `^#Right::`                   |
| send keys                     | **uinput** — the kernel creates a virtual keyboard, KWin treats it like a real one         | `SendInput`                   |
| see `Space` after capture     | **evdev** — key events read from the physical keyboard directly from the kernel            | `~Space::` + `#HotIf`         |
| clipboard                     | `wl-copy` / `wl-paste` (data-control protocol, offered by KWin)                            | `A_Clipboard`, `ClipboardAll` |

evdev devices are `/dev/input/event*`, uinput is `/dev/uinput`. Both belong to root; `install.sh` gives them to the
`input` group and adds you to it — that is why a log out / log in is needed.

---

## Why Python

Considered alternatives:

- **bash scripts + `ydotool` + KDE custom shortcuts** — each hotkey starts a script, `ydotool` sends keys. Spaces and
  swaps would work, capture would not: bash has no good way to listen for `Space` after `Ctrl + Meta + Backspace`.
  `ydotool` is also not in the Ubuntu repositories and needs its own daemon.
- **keyd / kanata / input-remapper** — root daemons, great for remapping; spaces and swaps could be plain key macros.
  Running as root they cannot see the clipboard of your session and are not meant to write dictionaries — no capture.
- **AutoKey** (a Linux "AHK" in Python) — X11 only, does not work on Wayland.
- **Espanso** — replaces typed text only, knows nothing about the cursor or action hotkeys.
- **C / Rust** — would work the same, but need compiling and maintenance; overkill for a few dozen lines of logic.

What Python gives:

- one process doing all four rows of the table above
- libraries already there: `python3-dbus` and `python3-gi` (GLib event loop, the base of the desktop) come with
  Kubuntu; the only addition is `python3-evdev`, from apt
- no `pip`, no virtualenv — Ubuntu blocks `pip install` into the system Python (PEP 668), apt packages are enough
- the code reads side by side with the AHK scripts, almost line by line

---

## Code map

| File                     | Content                                                                                 | Windows counterpart   |
|--------------------------|-----------------------------------------------------------------------------------------|-----------------------|
| `typing_helpers.py`      | entrypoint: registers KDE shortcuts over DBus, runs the event loop, dispatches actions  | `AutoHotkey.ahk`      |
| `keyboard.py`            | uinput output (`send`), evdev input (listeners, held keys), clipboard helpers           | built into AHK        |
| `sequence_fixes.py`      | space / transposition fixes                                                             | `sequence_fixes.ahk`  |
| `make_dictionary.py`     | typo capture                                                                            | `make_dictionary.ahk` |
| `espanso_restart.py`     | Espanso restart on keyboard plug-in and hotkey (it stops responding after a reconnect)  | `AutoHotkey.ahk`      |
| `typing-helpers.service` | systemd user unit — starts the service with Plasma, restarts it on crash                | autostart             |
| `install.sh`             | one-time setup                                                                          | —                     |

Each feature module has an `ACTIONS` dict: action name → (label in System Settings, default keys, function).
`typing_helpers.py` merges them and registers each action with KDE.

The **GLib main loop** is the AHK event loop: it waits for DBus signals (hotkey pressed) and keyboard events and calls
the handlers. It is single-threaded, so actions run one after another and never overlap. A handler may block
(e.g. waiting for the clipboard); events meanwhile wait in the kernel.

When KDE reports a hotkey, `Ctrl` and `Meta` are still physically held. A virtual keyboard cannot release keys held
on another device (libinput counts presses per seat), so `wait_for_modifiers_release()` waits until you let go —
otherwise the injected `Left` would reach KWin as `Ctrl + Meta + Left`.

---

## `sequence_fixes.py` vs `sequence_fixes.ahk`

- `fix_early_space` / `fix_late_space` — the same key sequences; `"ctrl+left"` is `^{Left}`
- `swap_chars_around_cursor` — the same steps: `Shift + Left`, `Ctrl + X`, `Right`, `Ctrl + V`, `Left`
- `clipboard_save()` / `clipboard_restore()` replace `ClipboardAll()`; only one format is kept (text preferred),
  so e.g. an image with extra formats may come back simplified
- `clipboard_reset()` + `clipboard_wait()` replace `A_Clipboard := ""` + `ClipWait`: instead of clearing, the clipboard
  briefly gets the text `typing-helpers: waiting for copy` (Klipper's "prevent empty clipboard" would put the old
  content back and the wait would accept it)

## `make_dictionary.py` vs `make_dictionary.ahk`

- `learn_wrong` (global) = `learnWrong`
- `capture()` = `^#Backspace::` — the same order: save clipboard, `Ctrl + Shift + Left`, `Ctrl + C`, `Backspace`,
  restore
- `on_key()` = `#HotIf learnWrong != ""` with `~Space / ~Enter / ~Tab / ~Esc`; evdev only watches the keyboard,
  it does not stop keys, so `Space` still reaches the application — like `~` in AHK
- `GLib.timeout_add(50, …)` — `log_correction` runs 50 ms later. AHK's `~` delivers the key before running the code;
  evdev may see `Space` before the application has processed it, so wait a bit. A heuristic.
- `is_word()` — the same rule; Python `re` has no `\p{L}`, `[^\W_]` (word character except `_`) plays that role
- `append_correction()`, `log_correction()` — the same as AHK, minus `Hotstring(...)`: on Linux Espanso corrects,
  it reloads `auto.yml` on its own (when `~/.config/espanso/match` points at the repository)

---

## Weak points / gotchas

- **`input` group** — any program running as you can read the keyboard. That is the price of watching `Space`.
  Espanso on Wayland does the same through `cap_dac_override`.
- **delay** — an action runs after `Ctrl` / `Meta` are released. That is how Wayland / libinput work; avoiding it
  would mean grabbing the whole keyboard, the way keyd does.
- **KDE only** — hotkeys go through KDE's `kglobalaccel`; another desktop would need another way to catch them.
- **`Ctrl + C` in Konsole** interrupts the program instead of copying (like terminals on Windows) — capture and swap
  do not work in a terminal.
- **Klipper history** keeps the sentinel and the copied characters / words.
- **KWin shortcuts** — `install.sh` removes `Ctrl + Meta + Left / Right / Up / Down` (switch virtual desktop). If KDE
  still owns a key, the service logs `some of [...] not assigned`.

---

## Debugging cheatsheet

```sh
systemctl --user status typing-helpers       # running? last log lines
journalctl --user -u typing-helpers -f       # follow the log (captured words are logged too)
systemctl --user restart typing-helpers      # after editing the scripts

# run in the foreground, errors straight in the terminal
systemctl --user stop typing-helpers
python3 ~/repos/typing-helpers-dyslexic/linux/typing_helpers.py
# Ctrl + C to stop, then:
systemctl --user start typing-helpers

groups                                       # `input` must be listed (after log out / log in)
ls -l /dev/uinput                            # crw-rw---- root input
```

Shortcuts can be viewed and changed in `System Settings → Keyboard → Shortcuts → Typing helpers`.
