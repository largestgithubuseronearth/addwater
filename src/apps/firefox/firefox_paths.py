from os import PathLike
from os.path import exists, join
from pathlib import Path

from addwater.model import AppPack
from addwater.model.paths import user_config, user_home

# TODO use new paths mod

# FIREFOX PATHS
BASE_LEGACY              = user_home() / ".mozilla/firefox/"
BASE                     = user_config() / "mozilla/firefox/"
FLATPAK_LEGACY           = user_home() / ".var/app/org.mozilla.firefox/.mozilla/firefox/"
FLATPAK                  = user_home() / ".var/app/org.mozilla.firefox/config/mozilla/firefox/"

SNAP_LEGACY              = user_home() / "snap/firefox/common/.mozilla/firefox/"
SNAP                     = user_home() / "snap/firefox/common/.config/mozilla/firefox/"

LIBREWOLF_BASE_LEGACY    = user_home() / ".librewolf/"
LIBREWOLF_BASE           = user_config() / "librewolf/librewolf"
LIBREWOLF_FLATPAK_LEGACY = user_home() / ".var/app/io.gitlab.librewolf-community/.librewolf/"
LIBREWOLF_FLATPAK        = user_home() / ".var/app/io.gitlab.librewolf-community/config/librewolf/librewolf/"

FLOORP_BASE              = user_home() / ".floorp"
FLOORP_FLATPAK           = user_home() / ".var/app/one.ablaze.floorp/.floorp"

WATERFOX_BASE            = user_home() / ".waterfox"
WATERFOX_FLATPAK         = user_home() / ".var/app/net.waterfox.waterfox/.waterfox"

CACHY_BASE               = user_home() / ".cachy"

# TODO can this be a GObject so I can use it in ListModels?
#      or must I make a wrapper?
class FirefoxPack(AppPack):
    # TODO rename these to just use the name instead of base later (Firefox / Firefox Flatpak / Librewolf / etc)
    BASE                  = ("Base", BASE)
    BASE_ALT              = ("Base (Alt)", BASE_LEGACY)
    FLATPAK               = ("Flatpak", FLATPAK)
    FLATPAK_ALT           = ("Flatpak (Alt)", FLATPAK_LEGACY)
    SNAP                  = ("Snap", SNAP)
    SNAP_ALT              = ("Snap (Alt)", SNAP_LEGACY)
    LIBREWOLF             = ("Librewolf", LIBREWOLF_BASE)
    LIBREWOLF_ALT         = ("Librewolf (Alt)", LIBREWOLF_BASE_LEGACY)
    LIBREWOLF_FLATPAK     = ("Librewolf Flatpak", LIBREWOLF_FLATPAK)
    LIBREWOLF_FLATPAK_ALT = ("Librewolf Flatpak (Alt)", LIBREWOLF_FLATPAK_LEGACY)
    FLOORP                = ("Floorp", FLOORP_BASE)
    FLOORP_FLATPAK        = ("Floorp Flatpak", FLOORP_FLATPAK)
    WATERFOX              = ("Waterfox", WATERFOX_BASE)
    WATERFOX_FLATPAK      = ("Waterfox Flatpak", WATERFOX_FLATPAK)
    CACHY                 = ("CachyOS Browser", CACHY_BASE)

    def get_profile_ini(self) -> Path:
        prof_ini = join(self.path, "profiles.ini")
        if not exists(prof_ini):
            raise FileNotFoundError(f"profiles.ini does not exist in {self.path}")

        return Path(prof_ini)


    @staticmethod
    def new_from_path(app_path: Path | PathLike) -> AppPack | None:
        app_path = Path(app_path)
        for pack in FirefoxPack:
            if app_path == pack.path:
                return pack

        return None

    @staticmethod
    def new_from_name(name: str) -> AppPack | None:
        for pack in FirefoxPack:
            if name == pack.pack_name:
                return pack

        return None

