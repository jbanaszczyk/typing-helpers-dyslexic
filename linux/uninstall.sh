#!/bin/bash
# reverts install.sh (python3-evdev stays installed); safe to run again
set -euo pipefail
cd "$(dirname "$0")"

if [ "$EUID" -eq 0 ]; then
    echo "Run as your user, without sudo (it asks for sudo itself)." >&2
    exit 1
fi

# ---------- service

systemctl --user disable --now typing-helpers.service 2>/dev/null || true
rm -f ~/.config/systemd/user/typing-helpers.service
systemctl --user daemon-reload

# ---------- KDE shortcuts

# restore KWin's default Ctrl+Meta+Left/Right/Up/Down (Qt: Ctrl 0x04000000, Meta 0x10000000, Left 0x01000012 ...)
restore_shortcut() {
    busctl --user call org.kde.kglobalaccel /kglobalaccel org.kde.KGlobalAccel \
        setForeignShortcutKeys 'asa(ai)' 4 kwin "$1" "" "" 1 1 $((0x04000000 | 0x10000000 | $2))
}
restore_shortcut "Switch One Desktop to the Left"  0x01000012
restore_shortcut "Switch One Desktop Up"           0x01000013
restore_shortcut "Switch One Desktop to the Right" 0x01000014
restore_shortcut "Switch One Desktop Down"         0x01000015

# ---------- system (sudo)

sudo rm -f /etc/udev/rules.d/60-typing-helpers-uinput.rules /etc/modules-load.d/typing-helpers-uinput.conf
sudo udevadm control --reload-rules
sudo udevadm trigger --name-match=uinput

if id -nG "$USER" | grep -qw input; then
    sudo gpasswd -d "$USER" input
fi

echo
echo "Log out and log in again (group membership)."
