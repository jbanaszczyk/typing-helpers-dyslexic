;;;;;;;;;;;;;; any app + notepad spellcheck

^#F12::{
    MsgBox WinGetProcessName("A")
}

IsReviewSource() {
    exe := WinGetProcessName("A")
    return exe = "ChatGPT.exe"
        || exe = "YourCorpMessenger.exe"
        || exe = "SomeOtherApp.exe"
}

reviewFile := A_ScriptDir "\review.md"
sourceHwnd := 0

#HotIf IsReviewSource()

^#z::{
    global reviewFile, sourceHwnd

    sourceHwnd := WinGetID("A")

    oldClip := ClipboardAll()
    A_Clipboard := ""

    SendInput "^a"
    Sleep 50
    SendInput "^c"

    if !ClipWait(0.5) {
        A_Clipboard := oldClip
        return
    }

    try FileDelete reviewFile
    FileAppend A_Clipboard, reviewFile, "UTF-8"

    A_Clipboard := oldClip

    Run 'notepad.exe "' reviewFile '"'
}

#HotIf WinActive("ahk_exe notepad.exe")

^#z::{
    global reviewFile, sourceHwnd

    notepadHwnd := WinGetID("A")

    oldClip := ClipboardAll()
    A_Clipboard := ""

    SendInput "^s"
    Sleep 100
    SendInput "^a"
    Sleep 50
    SendInput "^c"

    if !ClipWait(0.5) {
        A_Clipboard := oldClip
        return
    }

    copiedText := A_Clipboard

    if !sourceHwnd || !WinExist("ahk_id " sourceHwnd) {
        A_Clipboard := oldClip
        MsgBox "Source window not found."
        return
    }

    WinActivate "ahk_id " sourceHwnd
    Sleep 150

    A_Clipboard := copiedText
    ClipWait 0.5

    SendInput "^a"
    Sleep 50
    SendInput "^v"

    Sleep 100
    A_Clipboard := oldClip

    if WinExist("ahk_id " notepadHwnd)
        WinClose "ahk_id " notepadHwnd
}

#HotIf

;;;;;;;;;;;;;;
