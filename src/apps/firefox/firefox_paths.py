from os.path import expanduser, join, exists
from os import environ, PathLike
from enum import Enum
from pathlib import Path
from typing import Optional

config_dir = environ.get("HOST_XDG_CONFIG_HOME", expanduser("~/.config"))

# FIREFOX PATHS
# TODO replace fstring with join()
BASE_LEGACY = expanduser("~/.mozilla/firefox/")
BASE = expanduser(f"{config_dir}/mozilla/firefox/")
FLATPAK_LEGACY = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/config/mozilla/firefox/")
SNAP_LEGACY = expanduser("~/snap/firefox/common/.mozilla/firefox/")
SNAP = expanduser("~/snap/firefox/common/.config/mozilla/firefox/")

LIBREWOLF_BASE_LEGACY = expanduser("~/.librewolf/")
LIBREWOLF_BASE = expanduser(f"{config_dir}/librewolf/librewolf")
LIBREWOLF_FLATPAK_LEGACY = expanduser(
    "~/.var/app/io.gitlab.librewolf-community/.librewolf/"
)
LIBREWOLF_FLATPAK = expanduser(
    "~/.var/app/io.gitlab.librewolf-community/config/librewolf/librewolf/"
)

FLOORP_BASE = expanduser("~/.floorp")
FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")

WATERFOX_BASE = expanduser("~/.waterfox")
WATERFOX_FLATPAK = expanduser("~/.var/app/net.waterfox.waterfox/.waterfox")

CACHY_BASE = expanduser("~/.cachy")

class FirefoxPack(Enum):
    # TODO rename these to just use the name instead of base later (Firefox / Firefox Flatpak / Librewolf / etc)
    BASE = ("Base", BASE)
    BASE_ALT = ("Base (Alt)", BASE_LEGACY)
    FLATPAK = ("Flatpak", FLATPAK)
    FLATPAK_ALT = ("Flatpak (Alt)", FLATPAK_LEGACY)
    SNAP = ("Snap", SNAP)
    SNAP_ALT = ("Snap (Alt)", SNAP_LEGACY)
    LIBREWOLF = ("Librewolf", LIBREWOLF_BASE)
    LIBREWOLF_ALT = ("Librewolf (Alt)", LIBREWOLF_BASE_LEGACY)
    LIBREWOLF_FLATPAK = ("Librewolf Flatpak", LIBREWOLF_FLATPAK)
    LIBREWOLF_FLATPAK_ALT = ("Librewolf Flatpak (Alt)", LIBREWOLF_FLATPAK_LEGACY)
    FLOORP = ("Floorp", FLOORP_BASE)
    FLOORP_FLATPAK = ("Floorp Flatpak", FLOORP_FLATPAK)
    WATERFOX = ("Waterfox", WATERFOX_BASE)
    WATERFOX_FLATPAK = ("Waterfox Flatpak", WATERFOX_FLATPAK)
    CACHY = ("CachyOS Browser", CACHY_BASE)

    def __init__(self, name: str, path: PathLike):
        self.pack_name = name
        self.path = Path(path)

    # TODO maybe make this a prop?
    def get_profile_ini(self) -> Path:
        prof_ini = join(self.path, "profiles.ini")
        if not exists(prof_ini):
            raise FileNotFoundError(f"profiles.ini does not exist in {self.path}")

        return Path(prof_ini)


    @staticmethod
    def new_from_path(app_path: Path | PathLike) -> Optional[Enum]:
        app_path = Path(app_path)
        for pack in FirefoxPack:
            if app_path == pack.path:
                return pack

        return None

    @staticmethod
    def new_from_name(name: str) -> Optional[Enum]:
        for pack in FirefoxPack:
            if name == pack.pack_name:
                return pack

        return None

