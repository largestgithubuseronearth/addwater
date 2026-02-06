from os.path import expanduser

# FIREFOX PATHS
BASE = expanduser("~/.mozilla/firefox/")
BASE_XDG = expanduser("~/.config/mozilla/firefox/")
FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FLATPAK_XDG = expanduser("~/.var/app/org.mozilla.firefox/.config/mozilla/firefox/")
SNAP = expanduser("~/snap/firefox/common/.mozilla/firefox/")
SNAP_XDG = expanduser("~/snap/firefox/common/.config/mozilla/firefox/")

LIBREWOLF_BASE = expanduser("~/.librewolf/")
LIBREWOLF_FLATPAK = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")

FLOORP_BASE = expanduser("~/.floorp")
FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")

WATERFOX_BASE = expanduser("~/.waterfox")
WATERFOX_FLATPAK = expanduser("~/.var/app/net.waterfox.waterfox/.waterfox")

CACHY_BASE = expanduser("~/.cachy")

FIREFOX_PATHS = [
    {"name": "Base", "path": BASE},
    {"name": "Base (XDG)", "path": BASE_XDG},
    {"name": "Flatpak", "path": FLATPAK},
    {"name": "Flatpak (XDG)", "path": FLATPAK_XDG},
    {"name": "Snap", "path": SNAP},
    {"name": "Snap (XDG)", "path": SNAP_XDG},
    {"name": "Librewolf Base", "path": LIBREWOLF_BASE},
    {"name": "Librewolf Flatpak", "path": LIBREWOLF_FLATPAK},
    {"name": "Floorp Base", "path": FLOORP_BASE},
    {"name": "Floorp Flatpak", "path": FLOORP_FLATPAK},
    {"name": "Waterfox Base", "path": WATERFOX_BASE},
    {"name": "Waterfox Flatpak", "path": WATERFOX_FLATPAK},
    {"name": "CachyOS Browser", "path": CACHY_BASE},
]
