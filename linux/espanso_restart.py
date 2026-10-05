"""Espanso restart - it stops responding after the keyboard reconnects (KVM switch)"""

from gi.repository import GLib

PLUG_DELAY = 2  # seconds; a keyboard is several input devices, a restart waits for all of them

pending = None  # GLib source of the restart waiting for PLUG_DELAY


def restart_espanso(_keyboard):
    # in background, the restart takes a while and the key listener must keep running
    pid, *_ = GLib.spawn_async(["espanso", "restart"],
                               flags=GLib.SpawnFlags.SEARCH_PATH | GLib.SpawnFlags.DO_NOT_REAP_CHILD)
    GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, on_exit)


def on_exit(_pid, status):
    print("espanso restarted" if status == 0 else f"espanso restart failed, wait status {status}", flush=True)


def on_keyboard_plugged(keyboard):
    global pending

    if pending:
        GLib.source_remove(pending)
    pending = GLib.timeout_add_seconds(PLUG_DELAY, restart_after_plug, keyboard)


def restart_after_plug(keyboard):
    global pending

    pending = None
    print("keyboard plugged in, restarting espanso", flush=True)
    restart_espanso(keyboard)
    return False


ACTIONS = {
    "espanso-restart": ("Restart Espanso", ["ctrl+meta+down"], restart_espanso),
}
