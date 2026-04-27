# AHK typing helpers

![AutoHotkey v2](https://img.shields.io/badge/AutoHotkey-v2-blue)

A minimal set of tools for:

* fixing sequence errors (character transpositions)
* fixing misplaced spaces
* fast autocorrection
* manual spellchecking (via Notepad)
* logging your own typos

---

## Rationale

This project was created to help with typing patterns often associated with dysgraphia-like transcription difficulties and motor sequencing issues, such as character transpositions and misplaced spaces.

### Why this exists

This setup is designed for typing errors caused by **character transpositions and sequencing issues**
(e.g. `zamaina`, `pojedyncz alitera`), not by lack of spelling knowledge.
Standard spellcheckers are weak at detecting these patterns, because the words often still look “valid enough”.

The approach here focuses on:

- mechanical edit operations (swap, move, fix spacing)
- personal typo patterns learned over time

Everything runs locally — no cloud, no data leaves the machine.

---

## Requirements

This project is implemented using AutoHotkey (AHK) for system-wide keyboard automation.

### Setup

After cloning the repository, download **AutoHotkey v2 (ZIP version)** from the official site

and place `AutoHotkey64.exe` in the project directory.
- run AutoHotkey
- add to autostart or similar

---

## Hotkeys

### Space / transposition fixes (core)

| Hotkey                   | Description                                                 | Meaning                  |
|--------------------------|-------------------------------------------------------------|--------------------------|
| `Ctrl + Win + Left`      | fix "late space" (`pojedynczal itera → pojedyncza litera`)  | move space left          |
| `Ctrl + Win + Right`     | fix "early space" (`pojedyncz alitera → pojedyncza litera`) | move space right         |
| `Ctrl + Win + Up / Down` | swap characters around cursor (`1a\|b4 → 1b\|a4`)           | fix transposition errors |

---

### Spellcheck (via Notepad)

| Hotkey           | Context               | Description                           |
|------------------|-----------------------|---------------------------------------|
| `Ctrl + Win + Z` | selected applications | copy all text → open in Notepad       |
| `Ctrl + Win + Z` | Notepad               | save → return → paste → close Notepad |

---

### Typo logger

| Hotkey                   | Description                               |
|--------------------------|-------------------------------------------|
| `Ctrl + Win + Backspace` | delete previous token and mark as "wrong" |

Logging is triggered by:

- `Space`
- `Enter`
- `Tab`

Output (`typo-log.txt`):

```
timestamp    wrong    correct    process
```

---

### Debug

| Hotkey             | Description                     |
|--------------------|---------------------------------|
| `Ctrl + Win + F12` | show active window process name |

---

## Hotstrings

### Shortcuts (from `secrets.ahk`)

```
BR → Best Regards
```

### Autocorrect (from `auto.ahk`)

```
szie    → size
jeszzce → jeszcze
bęzdie  → będzie
zaimana → zamiana
wszsycy → wszyscy
```

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

Logged into `typo-log.txt` as:

```
zaimana → zamiana
```

Later:

- frequent patterns can be analyzed and converted into hotstrings in `auto.ahk`

---

### Typical usage pattern

- fix **misplaced spaces** and **character swaps** first (`Ctrl + Win + ← → ↑`)
- use Notepad roundtrip for **apps without spellcheck**
- let the system **learn recurring typos**

---

## File structure

```
AutoHotkey.ahk      – main (entrypoint)
auto.ahk            – autocorrect rules
make_dictionary.ahk – typo logger
messenger.ahk       – Notepad spellcheck roundtrip
secrets.ahk         – private aliases / data (gitignored)
AutoHotkey64.exe    – AHK v2 binary (from downloaded ZIP)
```

---

## Notes

- Copy and customize:
    - `auto.example.ahk` → `auto.ahk`
    - `secrets.example.ahk` → `secrets.ahk`
- `messenger.ahk`
  → add target apps to `IsReviewSource()`
- `make_dictionary.ahk`
  → produces typo log (`typo-log.txt`, TSV-like), can be used later to extend `auto.ahk`
- temp files:
    - `review.md`
    - `typo-log.txt`
- fully offline (no text leaves your machine)
