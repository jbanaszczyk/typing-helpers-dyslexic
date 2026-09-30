#SingleInstance force
#Requires AutoHotkey v2.0
SetKeyDelay 0, 10

; AHK typo correction only when portable Espanso (`Espanso/espansod.exe`) is absent; otherwise Espanso corrects
ahkTypos := !FileExist(A_ScriptDir "/Espanso/espansod.exe")

#HotIf ahkTypos
#Include "*i windows/auto.ahk"
#Include "windows/typo_pl.ahk"
#Include "windows/typo_en.ahk"
#Include "windows/spelling.ahk"
#Include "*i windows/secrets.ahk"
#Include "*i windows/local.ahk"   ; your own hotstrings, outside the repo
#HotIf

#Include "windows/scripts/sequence_fixes.ahk"
#Include "windows/scripts/make_dictionary.ahk"
#Include "windows/scripts/messenger.ahk"
