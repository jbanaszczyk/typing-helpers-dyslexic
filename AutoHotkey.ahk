#SingleInstance force
#Requires AutoHotkey v2.0
SetKeyDelay 0, 10

;;;;;;;;;;;;;; space fixes

FixEarlySpace() {
    SendInput "{Alt up}{Esc}"
    SendInput "^{Left}{Backspace}{Right}{Space}^{Right}"
}

FixLateSpace() {
    SendInput "{Alt up}{Esc}"
    SendInput "^{Left}{Backspace}{Left}{Space}^{Right}"
}

;;;;;;;;;;;;;; transposition fix

SwapCharsAroundCursor() {
    oldClip := ClipboardAll()
    A_Clipboard := ""

    ; copy left char, then delete it
    SendInput "+{Left}"
    Sleep 30
    SendInput "^x"
    Sleep 30
    if !ClipWait(0.3) {
        A_Clipboard := oldClip
        return
    }

    SendInput "{Right}"
    Sleep 30
    SendInput "^v"
    Sleep 30
    SendInput "{Left}"

    Sleep 30
    A_Clipboard := oldClip
}

^#Right::FixEarlySpace()
^#Left::FixLateSpace()
^#Up::SwapCharsAroundCursor()
^#Down::SwapCharsAroundCursor()

;;;;;;;;;;;;;;

#Include "auto.ahk"
#Include "secrets.ahk"
#Include "make_dictionary.ahk"
#Include "messenger.ahk"
