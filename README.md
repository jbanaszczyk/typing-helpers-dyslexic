# typing-helpers-dyslexic

![AutoHotkey v2](https://img.shields.io/badge/AutoHotkey-v2-blue)
![Espanso](https://img.shields.io/badge/Espanso-match%20files-green)

A minimal set of tools for:

* fixing sequence errors (character transpositions)
* fixing misplaced spaces
* fast autocorrection
* manual spellchecking (via Notepad)
* building your own autocorrect dictionary from captured typos

---

## Rationale

This project was created to help with typing patterns often associated with dysgraphia-like transcription difficulties
and motor sequencing issues, such as character transpositions and misplaced spaces.

### Why this exists

This setup is designed for typing errors caused by **character transpositions and sequencing issues**
(e.g. `zamaina`, `pojedyncz alitera`), not by lack of spelling knowledge.
Standard spellcheckers are weak at detecting these patterns, because the words often still look “valid enough”.

The approach here focuses on:

- mechanical edit operations (swap, move, fix spacing)
- personal typo patterns learned over time

Roughly the same setup works on **Windows and Linux**. Captured typos stay local until reviewed; reviewed rules are
shared between machines through Git.

Everything runs locally — no cloud, no data leaves the machine.

---

## Platforms

| Tool                                | Windows                   | Linux (Kubuntu, Plasma 6, Wayland) |
|-------------------------------------|---------------------------|------------------------------------|
| hotkeys (spaces, swaps, capture)    | AutoHotkey                | Python service in `linux/`         |
| spellcheck roundtrip, debug hotkey  | AutoHotkey                | —                                  |
| autocorrect                         | AutoHotkey **or** Espanso | Espanso                            |

### Windows: pick one autocorrect engine

**AutoHotkey only** — no `Espanso/espansod.exe`

- AutoHotkey handles hotkeys and autocorrect (`windows/`: `auto.ahk`, `typo_*.ahk`, `spelling.ahk`, `secrets.ahk`)
- captured typos go to `windows/auto.ahk` and also to `Espanso/.espanso/match/auto.yml`, ready to be
  reviewed into the shared Espanso dictionaries

**AutoHotkey + Espanso** — portable Espanso in `Espanso/`

- AutoHotkey handles only hotkeys, its autocorrect dictionaries (including `secrets.ahk`) are disabled
- Espanso handles autocorrect
- captured typos go to `Espanso/.espanso/match/auto.yml` (and to `windows/auto.ahk`, if it exists)

The switch is the existence of `Espanso/espansod.exe`, checked when AutoHotkey starts. Only one engine corrects at a
time. Typo capture writes to each of `windows/auto.ahk`, `Espanso/.espanso/match/auto.yml` that
exists — at least one is needed.

### Linux

- Espanso handles autocorrect, using the same match files as Windows
- `linux/typing_helpers.py` (systemd user service) handles the hotkeys: space / transposition fixes and typo capture;
  the Notepad roundtrip and the debug hotkey are Windows only
- the hotkeys are KDE global shortcuts, component **Typing helpers** in
  `System Settings → Keyboard → Shortcuts` — they can be changed there
- keys are injected through a uinput virtual keyboard, the clipboard is used through `wl-copy` / `wl-paste`
- an action runs after the hotkey modifiers are released (a virtual keyboard cannot release keys held on the physical
  one)
- while copying, the clipboard briefly holds `typing-helpers: waiting for copy`, then the previous content is
  restored; Klipper history keeps these entries
- how it works, why Python, debugging: [`linux/NOTES.md`](linux/NOTES.md)

---

## Setup

On Windows, first decide which version you use — **AutoHotkey** or **AutoHotkey + Espanso** — and copy the matching
template files (`*_`). The version is switched by the presence of portable Espanso (`Espanso/espansod.exe`).

| Copy                                                                         | Windows: AutoHotkey | Windows: AutoHotkey + Espanso | Linux (Espanso) |
|------------------------------------------------------------------------------|---------------------|-------------------------------|-----------------|
| `windows/auto.ahk_` → `windows/auto.ahk`                                     | yes                 | optional                      |                 |
| `Espanso/.espanso/match/auto.yml_` → `Espanso/.espanso/match/auto.yml`       | yes                 | yes                           | yes             |
| `windows/secrets.ahk_` → `windows/secrets.ahk`                               | yes                 |                               |                 |
| `Espanso/.espanso/match/secrets.yml_` → `Espanso/.espanso/match/secrets.yml` |                     | yes                           | yes             |

### Windows: AutoHotkey

Portable AutoHotkey, no installation. After cloning the repository, download **AutoHotkey v2 (ZIP version)** from the
official site and place `AutoHotkey64.exe` in the project root, beside `AutoHotkey.ahk`.

- copy `windows/auto.ahk_` → `windows/auto.ahk`
- copy `Espanso/.espanso/match/auto.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `windows/secrets.ahk_` → `windows/secrets.ahk` and fill in your private aliases
- run AutoHotkey
- add to autostart or similar

### Windows: AutoHotkey + Espanso

Portable AutoHotkey and portable Espanso, no installation.

Set up AutoHotkey as above. `windows/secrets.ahk` is not needed (disabled with Espanso); `windows/auto.ahk` is
optional — if it exists, captured typos are collected there too.

Extract portable Espanso into `Espanso/` (keep `espansod.exe` there — its presence disables AutoHotkey autocorrect;
restart AutoHotkey after adding or removing it). From that directory, 

#### **as administrator**

From that directory, run once **as administrator**:

```
espanso service register
```

- copy `Espanso/.espanso/match/auto.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `Espanso/.espanso/match/secrets.yml_` → `Espanso/.espanso/match/secrets.yml` and fill in your private
  aliases

Then start `START_ESPANSO.bat`, also **as administrator**. The configuration lives in `Espanso/.espanso/config/` and
is gitignored.

### Linux (Espanso)

- copy `Espanso/.espanso/match/auto.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `Espanso/.espanso/match/secrets.yml_` → `Espanso/.espanso/match/secrets.yml` and fill in your private
  aliases

Point Espanso's config directory (`~/.config/espanso`) at the repository:

```sh
linux/link_espanso.sh
```

It replaces `~/.config/espanso` with a symlink to `Espanso/.espanso`; an existing directory is kept as
`~/.config/espanso.bak-<date>` and its `config/` is copied over, if the repository has none yet (`config/` is per
machine, gitignored).

After `git pull`, Espanso sees the new rules directly.

### Linux (hotkeys)

Run once:

```sh
linux/install.sh
```

Run it as yourself, **not** with `sudo linux/install.sh` — it would then set things up for `root` instead of you (the
script refuses to run as root). It asks for `sudo` itself and:

- installs `python3-evdev`
- makes `/dev/uinput` accessible to the `input` group (udev rule) and adds you to that group — note that any
  program of yours can then read the keyboard
- removes KWin's `Ctrl + Meta + Left / Right / Up / Down` (switch virtual desktop), taken by the hotkeys
- enables the systemd user service `linux/typing-helpers.service` (starts with Plasma)

`linux/uninstall.sh` reverts it (`python3-evdev` stays installed, KWin's desktop switching gets its default shortcuts
back).

Then log out and log in. Status and log:

```sh
systemctl --user status typing-helpers
journalctl --user -u typing-helpers -f
```

After changing the scripts: `systemctl --user restart typing-helpers`.

A hotkey acts only after you release `Ctrl` and `Meta` (AutoHotkey acts right away). That is how Wayland works —
Espanso waits the same way. See `linux/NOTES.md`.

---

## Hotkeys

`Win` is `Meta` on Linux.

### Space / transposition fixes (core)

| Hotkey                   | Description                                                 | Meaning                  |
|--------------------------|-------------------------------------------------------------|--------------------------|
| `Ctrl + Win + Left`      | fix "late space" (`pojedynczal itera → pojedyncza litera`)  | move space left          |
| `Ctrl + Win + Right`     | fix "early space" (`pojedyncz alitera → pojedyncza litera`) | move space right         |
| `Ctrl + Win + Up`        | swap characters around cursor (`1a\|b4 → 1b\|a4`)           | fix transposition errors |

---

### Espanso restart

| Hotkey              | Description     |
|---------------------|-----------------|
| `Ctrl + Win + Down` | restart Espanso |

Espanso stops responding after the keyboard disconnects and reconnects (e.g. a KVM switch), its log shows
`Can't read from device /dev/input/event…`. On Linux the service restarts Espanso on its own, up to 7 s after a keyboard
is plugged in; the hotkey is the fallback. On Windows the hotkey exists only with portable Espanso
(`Espanso/espansod.exe`).

---

### Spellcheck (via Notepad)

| Hotkey           | Context               | Description                           |
|------------------|-----------------------|---------------------------------------|
| `Ctrl + Win + Z` | selected applications | copy all text → open in Notepad       |
| `Ctrl + Win + Z` | Notepad               | save → return → paste → close Notepad |

---

### Typo capture

| Hotkey                   | Description                              |
|--------------------------|------------------------------------------|
| `Ctrl + Win + Backspace` | delete previous word and mark as "wrong" |

Then type the correct word. It is captured on:

- `Space`
- `Enter`
- `Tab`

`Esc` cancels a pending capture. Only single words (letters, digits, `'`, `-`) are captured.

The correction is appended to each dictionary that exists:

| File                              | Appended entry           |
|-----------------------------------|--------------------------|
| `windows/auto.ahk`                | `::zaimana::zamiana`     |
| `Espanso/.espanso/match/auto.yml` | Espanso match, see below |

```yaml
  - trigger: "zaimana"
    replace: "zamiana"
    word: true
    propagate_case: true
```

A missing file is skipped, never created. A word already captured is not appended again.
A captured correction works immediately — in the AutoHotkey version it is activated in the running instance, Espanso
reloads `auto.yml` on its own.

`auto.ahk` and `auto.yml` are gitignored — captured words should be reviewed and moved to the `typo_*` files, then
committed and pushed (see [Review](#review)).

---

### Debug

| Hotkey             | Description                     |
|--------------------|---------------------------------|
| `Ctrl + Win + F12` | show active window process name |

---

## Dictionaries

| Espanso (`Espanso/.espanso/match/`) | AutoHotkey (`windows/`) | Content                                       |
|-------------------------------------|-------------------------|-----------------------------------------------|
| `auto.yml`                          | `auto.ahk`              | captured typos, not reviewed yet (gitignored) |
| `typo_pl.yml`                       | `typo_pl.ahk`           | reviewed Polish typos                         |
| `typo_en.yml`                       | `typo_en.ahk`           | reviewed English typos                        |
| `spelling.yml`                      | `spelling.ahk`          | words I repeatedly misspell                   |
| `secrets.yml`                       | `secrets.ahk`           | private aliases / data (gitignored)           |
| any other `*.yml`                   | `local.ahk`             | your own rules (gitignored)                   |

Examples:

```
szie    → size
bęzdie  → będzie
zaimana → zamiana
jesli   → jeśli
BR      → Best Regards   (from secrets)
```

The Espanso and AutoHotkey files do not have to be identical. Each uses its own syntax:

| Espanso                              | AutoHotkey                                    |
|--------------------------------------|-----------------------------------------------|
| `word: true`, `propagate_case: true` | `::jesli::jeśli` (AHK follows the typed case) |
| `word: true`, no case propagation    | `:c:dc::cd`                                   |
| no `word` (fragment inside a word)   | `:?c*:szzc::szcz`                             |
| `triggers: [a, b]`                   | one hotstring per trigger                     |

### Own dictionaries

Only the files listed in `Espanso/.gitignore` and `.gitignore` are shared; everything else in `Espanso/` and `windows/`
stays local. A new file is ignored until you add it to the list (or `git add -f` it once), so nothing private is
committed by accident.

- Espanso loads every `*.yml` in `Espanso/.espanso/match/` — just add a file.
- AutoHotkey loads only included files: put your hotstrings into `windows/local.ahk` (included if it exists, like
  `secrets.ahk`), which may `#Include` further files. Like the other dictionaries, it is active only without Espanso.

### Review

`auto.yml` and `auto.ahk` are local to each machine. From time to time, go through them:

- remove duplicates and one-off accidents
- merge variants, replace them with a generic rule where safe
- move what is worth keeping to `typo_pl.yml`, `typo_en.yml` or `spelling.yml` (and the matching `.ahk`)
- commit and push — only now the rules reach the other machines

Misplaced spaces (`zamianas pacji`) are not autocorrected — use `Ctrl + Win + Left / Right`.

---

## Example workflow

### Fixing misplaced spaces (common sequencing issue)

Typing:

```
pojedyncz alitera
                  ^
```

Press:

```
Ctrl + Win + Right
```

Result:

```
pojedyncza litera
                  ^
```

---

### Fixing transposition errors (PL: "Czech typo")

Typing:

```
zamaina
    ^
```

Press:

```
Ctrl + Win + Up
```

Result:

```
zamiana
    ^
```

---

### Quick spellcheck

In an app without spellcheck:

1. Press:

```
Ctrl + Win + Z
```

2. Text opens in Notepad
    - Notepad supports multiple languages (e.g. EN + PL)
    - configure via:
      `Windows Settings → Time & Language → Language & Region → Preferred languages`

3. Edit/fix text with spellchecker support
4. Press again:

```
Ctrl + Win + Z
```

Result:

- edited/fixed text is pasted back into the original app
- Notepad closes automatically

---

### Building your personal autocorrect

Typing error:

```
zaimana
```

To fix and store both error and correct form:

```
Ctrl + Win + Backspace
zamiana␠
```

From now on `zaimana` is corrected automatically on this machine. After review (see [Review](#review)), commit and
push, pull on the other machine — it works there too.

---

### Typical usage pattern

- fix **misplaced spaces** and **character swaps** first (`Ctrl + Win + ← → ↑`)
- use Notepad roundtrip for **apps without spellcheck**
- capture **recurring typos** so they are corrected next time

---

## File structure

```
AutoHotkey.ahk            – main AHK script (entrypoint), next to AutoHotkey64.exe
AutoHotkey64.exe          – AHK v2 binary (from downloaded ZIP, gitignored)
windows/
  auto.ahk                – captured typos (copy of auto.ahk_, gitignored)
  typo_pl.ahk             – reviewed Polish typos
  typo_en.ahk             – reviewed English typos
  spelling.ahk            – repeated misspellings
  secrets.ahk             – private aliases / data (copy of secrets.ahk_, gitignored)
  local.ahk               – your own hotstrings (optional, gitignored)
  scripts/
    sequence_fixes.ahk    – space / transposition fixes
    make_dictionary.ahk   – typo capture
    messenger.ahk         – Notepad spellcheck roundtrip
linux/
  typing_helpers.py       – Linux hotkey service (entrypoint), KDE global shortcuts
  keyboard.py             – key injection (uinput), keyboard reading (evdev), clipboard (wl-clipboard)
  sequence_fixes.py       – space / transposition fixes
  make_dictionary.py      – typo capture
  typing-helpers.service  – systemd user unit
  install.sh              – one-time setup
  uninstall.sh            – reverts install.sh
  link_espanso.sh         – links ~/.config/espanso to Espanso/.espanso
  NOTES.md                – how the Linux service works, debugging
Espanso/                  – portable Espanso on Windows (binaries gitignored)
  espansod.exe            – its presence switches autocorrect from AutoHotkey to Espanso
  .espanso/match/
    auto.yml              – captured typos (copy of auto.yml_, gitignored)
    typo_pl.yml           – reviewed Polish typos
    typo_en.yml           – reviewed English typos
    spelling.yml          – repeated misspellings
    secrets.yml           – private aliases / data (copy of secrets.yml_, gitignored)
    *.yml                 – your own rules (gitignored)
```

---

## Notes

- the autocorrect engine is switched by `Espanso/espansod.exe`, which template files to copy depends on the version,
  see [Setup](#setup)
- `windows/scripts/messenger.ahk`
  → add target apps to `IsReviewSource()`
- Espanso configuration (`config/`) is per machine and gitignored; only the listed match files are shared (see
  [Own dictionaries](#own-dictionaries))
- temp files:
    - `review.md`
- fully offline (no text leaves your machine)
