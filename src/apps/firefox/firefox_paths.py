from os.path import expanduser

# FIREFOX PATHS
BASE_LEGACY = expanduser("~/.mozilla/firefox/")
BASE = expanduser("~/.config/mozilla/firefox/")
FLATPAK_LEGACY = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/config/mozilla/firefox/")
SNAP_LEGACY = expanduser("~/snap/firefox/common/.mozilla/firefox/")
SNAP = expanduser("~/snap/firefox/common/.config/mozilla/firefox/")

LIBREWOLF_BASE_LEGACY = expanduser("~/.librewolf/")
LIBREWOLF_BASE = expanduser("~/.config/librewolf/librewolf")
LIBREWOLF_FLATPAK_LEGACY = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")
LIBREWOLF_FLATPAK = expanduser("~/.var/app/io.gitlab.librewolf-community/config/librewolf/librewolf/")

FLOORP_BASE = expanduser("~/.floorp")
FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")

WATERFOX_BASE = expanduser("~/.waterfox")
WATERFOX_FLATPAK = expanduser("~/.var/app/net.waterfox.waterfox/.waterfox")

CACHY_BASE = expanduser("~/.cachy")

FIREFOX_PATHS = [
    {"name": "Base", "path": BASE},
    {"name": "Base (Alt)", "path": BASE_LEGACY},
    {"name": "Flatpak", "path": FLATPAK},
    {"name": "Flatpak (Alt)", "path": FLATPAK_LEGACY},
    {"name": "Snap", "path": SNAP},
    {"name": "Snap (Alt)", "path": SNAP_LEGACY},
    {"name": "Librewolf Base", "path": LIBREWOLF_BASE},
    {"name": "Librewolf Base (Alt)", "path": LIBREWOLF_BASE_LEGACY},
    {"name": "Librewolf Flatpak", "path": LIBREWOLF_FLATPAK},
    {"name": "Librewolf Flatpak (Alt)", "path": LIBREWOLF_FLATPAK_LEGACY},
    {"name": "Floorp Base", "path": FLOORP_BASE},
    {"name": "Floorp Flatpak", "path": FLOORP_FLATPAK},
    {"name": "Waterfox Base", "path": WATERFOX_BASE},
    {"name": "Waterfox Flatpak", "path": WATERFOX_FLATPAK},
    {"name": "CachyOS Browser", "path": CACHY_BASE},
]
