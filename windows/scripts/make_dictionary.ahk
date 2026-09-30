;;;;;;;;;;;;;; typo capture

learnWrong := ""

^#Backspace::{
    global learnWrong

    oldClip := ClipboardAll()
    A_Clipboard := ""

    SendInput "+^{Left}"
    Sleep 30
    SendInput "^c"
    if !ClipWait(0.2) {
        A_Clipboard := oldClip
        return
    }

    learnWrong := Trim(A_Clipboard, " `t`r`n")

    SendInput "{Backspace}"

    A_Clipboard := oldClip
}

#HotIf learnWrong != ""

~Space::{
    LogCorrection()
}

~Enter::{
    LogCorrection()
}

~Tab::{
    LogCorrection()
}

~Esc::{
    global learnWrong
    learnWrong := ""
}

#HotIf

; a single word: letters, digits, apostrophe, hyphen; anything else could break the AHK or YAML syntax
IsWord(text) {
    return RegExMatch(text, "^[\p{L}\p{N}'-]+$")
}

AppendCorrection(wrong, correct) {
    ahkDictionary := A_ScriptDir "\windows\auto.ahk"
    ; skip already captured words (with any hotstring options), keeps the dictionary free of duplicates
    if FileExist(ahkDictionary) && !RegExMatch(FileRead(ahkDictionary, "UTF-8"), "m)^:[^:]*:\Q" wrong "\E::") {
        FileAppend "::" wrong "::" correct "`n", ahkDictionary, "UTF-8"
    }

    ; activate in the running instance, no reload needed
    ; HotIf() resets the context inherited from the launching hotkey (`#HotIf learnWrong != ""`) to global
    if ahkTypos {
        HotIf()
        Hotstring("::" wrong, correct)
    }

    espansoDictionary := A_ScriptDir "\Espanso\.espanso\match\auto.yml"
    if FileExist(espansoDictionary) && !InStr(FileRead(espansoDictionary, "UTF-8"), 'trigger: "' wrong '"', true) {
        entry := "`n"
            . '  - trigger: "' wrong '"`n'
            . '    replace: "' correct '"`n'
            . "    word: true`n"
            . "    propagate_case: true`n"
        FileAppend entry, espansoDictionary, "UTF-8"
    }
}

LogCorrection() {
    global learnWrong

    oldClip := ClipboardAll()
    A_Clipboard := ""

    SendInput "{Left}"
    SendInput "+^{Left}"
    Sleep 30
    SendInput "^c"
    if !ClipWait(0.2) {
        SendInput "{Right}"
        A_Clipboard := oldClip
        learnWrong := ""
        return
    }

    correct := Trim(A_Clipboard, " `t`r`n")

    SendInput "{Right}{Right}"

    if (IsWord(learnWrong) && IsWord(correct) && learnWrong != correct) {
        AppendCorrection(learnWrong, correct)
    }

    learnWrong := ""
    A_Clipboard := oldClip
}
