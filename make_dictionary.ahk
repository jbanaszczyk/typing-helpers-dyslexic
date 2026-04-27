;;;;;;;;;;;;;; logger

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

    learnWrong := Trim(A_Clipboard)

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

#HotIf

LogCorrection() {
    global learnWrong

    oldClip := ClipboardAll()
    A_Clipboard := ""

    SendInput "{Left}"
    SendInput "+^{Left}"
    Sleep 30
    SendInput "^c"
    if !ClipWait(0.2) {
        A_Clipboard := oldClip
        learnWrong := ""
        return
    }

    correct := Trim(A_Clipboard)

    SendInput "{Right}"

    if (StrLen(learnWrong) >= 4 && StrLen(correct) >= 4 && learnWrong != correct) {
        line := FormatTime(, "yyyy-MM-dd HH:mm:ss")
            . "`t" learnWrong
            . "`t" correct
            . "`t" WinGetProcessName("A")
            . "`n"

        FileAppend line, A_ScriptDir "\typo-log.txt", "UTF-8"
    }

    learnWrong := ""
    A_Clipboard := oldClip
}

;;;;;;;;;;;;;;
