import logging

from addwater import AppProfile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus, OnlineManager, InstallManager
from addwater.apps.firefox.firefox_install import install_for_firefox
from gi.repository import Gio, GLib
from packaging.version import Version
from typing import readonly
from pathlib import Path
from os.path import join

from addwater.utils.paths import DOWNLOAD_DIR
from .firefox.firefox_install import install_for_firefox
from .firefox.firefox_options import FIREFOX_OPTIONS
from addwater.utils.paths import APP_CACHE
from.pref_handler import PreferenceHandler

from .app_theme import AppTheme

log = logging.getLogger("firefox-gnome-theme")

class FirefoxGnomeTheme(AppTheme, PreferenceHandler):
    _name = _("Firefox GNOME Theme")
    _profiles: readonly[set[AppProfile]]
    _pack: FirefoxPack | None
    _settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
    _cache_dir: readonly[Path] = Path(join(APP_CACHE,
                                           "themes",
                                           "firefox-gnome-theme"))

    _cli_tree: GLib.OptionGroup.new(_("Firefox GNOME Theme"),
                                    _("Actions for the Firefox GNOME Theme"),
                                    None)
    _Version = Version("0.0.0")

    # TODO replace this with a git repo manager later on
    _online_provider: OnlineManager = OnlineManager(
        "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"
    )
    _install_provider: InstallManager = InstallManager(install_for_firefox)

    # TODO replace this with TypedDict (stashed)
    _options_spec: dict

    def __init__(self) -> None:
        try:
            self._cache_dir.mkdir(parents=True)
        except FileExistsError:
            pass

        # Setup CLI actions

    # Methods

    def install(self, profile: AppProfile) -> InstallStatus:
        if not profile:
            raise TypeError()

        # FIXME use new _cache_dir
        theme_path = join(DOWNLOAD_DIR, "firefox", "firefox-gnome-theme")
        return self._install_provider.combined_install(theme_path,
                                                       profile,
                                                       None)

    def uninstall(self, profile: AppProfile) -> InstallStatus:
        # FIXME installer should know where it installed the theme
        return self._install_provider.uninstall(profile,
                                                "firefox-gnome-theme")

    def update(self) -> OnlineStatus:
        # FIXME simplify this path bullshit
        #  update(version,  dest: join(self._cache_dir, "theme-files"))
        status = self._online_provider.get_updates_online(
            self.version, (DOWNLOAD_DIR, "firefox", "firefox-gnome-theme")
        )
        self.version = self._online_provider.get_update_version()

        return status

    def apply_preferences(self) -> InstallStatus:
        raise NotImplementedError

    # Props

    # TODO only let consumers track profiles since that's
    #      all they should be working with.
    @property
    def pack(self) -> FirefoxPack:
        return self._pack

    @pack.setter
    def pack(self, pack: FirefoxPack) -> None:
        raise NotImplementedError

    # TODO
    @property
    def profiles(self) -> readonly[set[AppProfile]]:
        return self._profiles

    # TODO
    def version(self, version: Version) -> None:
        raise NotImplementedError

    # Plumbing

    def _setup_cli_tree(self) -> None:
        self._cli_tree.add_option_entries([
            GLib.OptionEntry(arg=GLib.OptionArg.STRING,
                             arg_description=_("Profile name"),
                             long_name=_("install"),
                             description=_("Install theme to a profile")),
            GLib.OptionEntry(arg=GLib.OptionArg.NONE,
                             long_name=_("update"),
                             description=_("check for updates")),
        ])
