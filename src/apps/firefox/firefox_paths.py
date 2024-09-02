from os.path import expanduser

# FIREFOX PATHS
FIREFOX_BASE = expanduser("~/.mozilla/firefox/")
FIREFOX_FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FIREFOX_SNAP = expanduser("~/snap/firefox/common/.mozilla/firefox/")

FIREFOX_LIBREWOLF_BASE = expanduser("~/.librewolf/")
FIREFOX_LIBREWOLF_FLATPAK = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")
FIREFOX_LIBREWOLF_SNAP = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")

FIREFOX_FLOORP_BASE = expanduser("~/.floorp")
FIREFOX_FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")

FIREFOX_PATHS = [
	{"name" : "Base", "path" : FIREFOX_BASE},
	{"name" : "Flatpak", "path" : FIREFOX_FLATPAK},
	{"name" : "Snap", "path" : FIREFOX_SNAP},
	{"name" : "Librewolf Base", "path" : FIREFOX_LIBREWOLF_BASE},
	{"name" : "Librewolf Flatpak", "path" : FIREFOX_LIBREWOLF_FLATPAK},
	{"name" : "Librewolf Snap", "path" : FIREFOX_LIBREWOLF_SNAP},
	{"name" : "Floorp Base", "path" : FIREFOX_FLOORP_BASE},
	{"name" : "Floorp Flatpak", "path" : FIREFOX_FLOORP_FLATPAK},
]
