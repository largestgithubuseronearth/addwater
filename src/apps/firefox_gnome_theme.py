from addwater import AppProfile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus, OnlineManager, InstallManager
from addwater.apps.firefox.firefox_install import install_for_firefox
from gi.repository import Gio
from packaging.version import Version
from typing import readonly
from pathlib import Path
from os.path import join

from addwater.utils.paths import DOWNLOAD_DIR
from .firefox.firefox_install import install_for_firefox
from .firefox.firefox_options import FIREFOX_OPTIONS
from addwater.utils.paths import APP_CACHE

from .app_theme import AppTheme

class FirefoxGnomeTheme(AppTheme):
    _settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

    _cache_dir: readonly[Path] = Path(join(APP_CACHE,
                                           "themes",
                                           "firefox-gnome-theme"))

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

    # TODO
    def install(self, profile: AppProfile) -> InstallStatus:
        if not profile:
            return InstallStatus.FAILURE

        # FIXME use new _cache_dir
        theme_path = join(DOWNLOAD_DIR, "firefox", "firefox-gnome-theme")
        return self._install_provider.combined_install(theme_path,
                                                       profile,
                                                       None)

    # TODO
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

