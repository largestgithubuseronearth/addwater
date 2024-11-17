from os.path import expanduser

# FIREFOX PATHS
BASE = expanduser("~/.mozilla/firefox/")
FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
SNAP = expanduser("~/snap/firefox/common/.mozilla/firefox/")

LIBREWOLF_BASE = expanduser("~/.librewolf/")
LIBREWOLF_FLATPAK = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")
LIBREWOLF_SNAP = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")

FLOORP_BASE = expanduser("~/.floorp")
FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")

CACHY_BASE = expanduser("~/.cachy")

FIREFOX_PATHS = [
    {"name": "Base", "path": BASE},
    {"name": "Flatpak", "path": FLATPAK},
    {"name": "Snap", "path": SNAP},
    {"name": "Librewolf Base", "path": LIBREWOLF_BASE},
    {"name": "Librewolf Flatpak", "path": LIBREWOLF_FLATPAK},
    {"name": "Librewolf Snap", "path": LIBREWOLF_SNAP},
    {"name": "Floorp Base", "path": FLOORP_BASE},
    {"name": "Floorp Flatpak", "path": FLOORP_FLATPAK},
    {"name": "CachyOS Browser", "path": CACHY_BASE},
]
