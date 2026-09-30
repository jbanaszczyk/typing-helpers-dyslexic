#!/bin/bash
# one-time setup of the Linux typing helpers (Kubuntu, Plasma 6, Wayland); safe to run again
set -euo pipefail
cd "$(dirname "$0")"

if [ "$EUID" -eq 0 ]; then
    echo "Run as your user, without sudo (it asks for sudo itself)." >&2
    exit 1
fi

# ---------- system (sudo)

# python3-dbus, python3-gi and wl-clipboard come with Kubuntu
sudo apt install -y python3-evdev

# /dev/uinput writable for the `input` group, the virtual keyboard injecting the keys
echo 'KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"' \
    | sudo tee /etc/udev/rules.d/60-typing-helpers-uinput.rules >/dev/null
echo uinput | sudo tee /etc/modules-load.d/typing-helpers-uinput.conf >/dev/null
sudo udevadm control --reload-rules
sudo udevadm trigger --name-match=uinput

# reading /dev/input/event* (keyboards) and writing /dev/uinput
sudo usermod -aG input "$USER"

# ---------- KDE shortcuts

# free Ctrl+Meta+Left/Right from KWin's "Switch One Desktop to the Left/Right" (Up/Down the same, if still bound)
for action in "Switch One Desktop to the Left" "Switch One Desktop to the Right" \
              "Switch One Desktop Up" "Switch One Desktop Down"; do
    busctl --user call org.kde.kglobalaccel /kglobalaccel org.kde.KGlobalAccel \
        setForeignShortcutKeys 'asa(ai)' 4 kwin "$action" "" "" 0
done

# ---------- service

mkdir -p ~/.config/systemd/user
ln -sf "$PWD/typing-helpers.service" ~/.config/systemd/user/typing-helpers.service
systemctl --user daemon-reload
systemctl --user enable typing-helpers.service

echo
echo "Log out and log in again (new group membership), the service starts with Plasma."
echo "Status / log:  systemctl --user status typing-helpers;  journalctl --user -u typing-helpers -f"
