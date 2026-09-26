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

| Tool                                | Windows                   | Linux                                 |
|-------------------------------------|---------------------------|---------------------------------------|
| hotkeys (spaces, swaps, capture, …) | AutoHotkey                | scripts in `linux/` (not yet written) |
| autocorrect                         | AutoHotkey **or** Espanso | Espanso                               |

### Windows: pick one autocorrect engine

**AutoHotkey only** — no `Espanso/espansod.exe`

- AutoHotkey handles hotkeys and autocorrect (`windows/auto.ahk`, `typo_*.ahk`, `spelling.ahk`, `secrets.ahk`)
- captured typos go to `windows/auto.ahk` and also to `Espanso/.espanso/match/auto.yml`, ready to be reviewed into the
  shared Espanso dictionaries

**AutoHotkey + Espanso** — portable Espanso in `Espanso/`

- AutoHotkey handles only hotkeys, its autocorrect dictionaries (including `secrets.ahk`) are disabled
- Espanso handles autocorrect
- captured typos go to `Espanso/.espanso/match/auto.yml` (and to `windows/auto.ahk`, if it exists)

The switch is the existence of `Espanso/espansod.exe`, checked when AutoHotkey starts. Only one engine corrects at a
time. Typo capture writes to each of `windows/auto.ahk`, `Espanso/.espanso/match/auto.yml` that exists — at least one
is needed.

### Linux

- Espanso handles autocorrect, using the same match files as Windows
- hotkeys (spaces, swaps, capture) are not implemented yet

---

## Setup

On Windows, first decide which version you use — **AutoHotkey** or **AutoHotkey + Espanso** — and copy the matching
example files. The version is switched by the presence of portable Espanso (`Espanso/espansod.exe`).

| Copy                                                                                 | Windows: AutoHotkey | Windows: AutoHotkey + Espanso | Linux (Espanso) |
|--------------------------------------------------------------------------------------|---------------------|-------------------------------|-----------------|
| `windows/auto.example.ahk` → `windows/auto.ahk`                                      | yes                 | optional                      |                 |
| `Espanso/.espanso/match/auto.example.yml_` → `Espanso/.espanso/match/auto.yml`       | yes                 | yes                           | yes             |
| `windows/secrets.example.ahk` → `windows/secrets.ahk`                                | yes                 |                               |                 |
| `Espanso/.espanso/match/secrets.example.yml_` → `Espanso/.espanso/match/secrets.yml` |                     | yes                           | yes             |

### Windows: AutoHotkey

Portable AutoHotkey, no installation. After cloning the repository, download **AutoHotkey v2 (ZIP version)** from the
official site and place `AutoHotkey64.exe` in the project root, beside `AutoHotkey.ahk`.

- copy `windows/auto.example.ahk` → `windows/auto.ahk`
- copy `Espanso/.espanso/match/auto.example.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `windows/secrets.example.ahk` → `windows/secrets.ahk` and fill in your private aliases
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

- copy `Espanso/.espanso/match/auto.example.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `Espanso/.espanso/match/secrets.example.yml_` → `Espanso/.espanso/match/secrets.yml` and fill in your private
  aliases

Then start `START_ESPANSO.bat`, also **as administrator**. The configuration lives in `Espanso/.espanso/config/` and
is gitignored.

### Linux (Espanso)

- copy `Espanso/.espanso/match/auto.example.yml_` → `Espanso/.espanso/match/auto.yml`
- copy `Espanso/.espanso/match/secrets.example.yml_` → `Espanso/.espanso/match/secrets.yml` and fill in your private
  aliases

Keep the Linux configuration in `~/.config/espanso/config/` and point the match directory at the repository:

```sh
rm -rf ~/.config/espanso/match
ln -s ~/repos/typing-helpers-dyslexic/Espanso/.espanso/match ~/.config/espanso/match
```

After `git pull`, Espanso sees the new rules directly.

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
| `base.yml`                          |                         | Espanso base file, safe to delete             |

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
  auto.ahk                – captured typos (copy of auto.example.ahk, gitignored)
  typo_pl.ahk             – reviewed Polish typos
  typo_en.ahk             – reviewed English typos
  spelling.ahk            – repeated misspellings
  sequence_fixes.ahk      – space / transposition fixes
  make_dictionary.ahk     – typo capture
  messenger.ahk           – Notepad spellcheck roundtrip
  secrets.ahk             – private aliases / data (gitignored)
linux/                    – Linux hotkey scripts (planned)
Espanso/                  – portable Espanso on Windows (binaries gitignored)
  espansod.exe            – its presence switches autocorrect from AutoHotkey to Espanso
  .espanso/match/
    base.yml              – Espanso base file
    auto.yml              – captured typos (copy of auto.example.yml_, gitignored)
    typo_pl.yml           – reviewed Polish typos
    typo_en.yml           – reviewed English typos
    spelling.yml          – repeated misspellings
    secrets.yml           – private aliases / data (gitignored)
```

---

## Notes

- the autocorrect engine is switched by `Espanso/espansod.exe`, which example files to copy depends on the version,
  see [Setup](#setup)
- `messenger.ahk`
  → add target apps to `IsReviewSource()`
- Espanso configuration (`config/`) is per machine and gitignored; only match files are shared
- temp files:
    - `review.md`
- fully offline (no text leaves your machine)
