from addwater import AppProfile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus
from gi.repository import Gio
from packaging.version import Version
from typing import readonly

# TODO abstract AppDetails class to define the interface
# Move what Backend does into this.

class AppTheme:
    _pack: FirefoxPack
    _profiles: set[AppProfile]
    _settings: readonly[Gio.Settings]
    _version: Version

    """Apply base theme files. Don't configure anything here."""
    def install(self, profile: AppProfile) -> InstallStatus:
        raise NotImplementedError

    """Remove theme files. Don't remove configuration"""
    def uninstall(self, profile: AppProfile) -> InstallStatus:
        raise NotImplementedError

    """Search online for available updates and automatically download it."""
    def update(self) -> OnlineStatus:
        raise NotImplementedError

    # TODO automatically write to the file when this is changed
    """ Preferences
    Theme options that can be configured by the user. Not to be confused with
    Add Water settings nor app-specific GSettings.
    """
    @property
    def preferences(self):
        raise NotImplementedError

    @preferences.setter
    def preferences(self, prefs) -> InstallStatus:
        raise NotImplementedError

    # TODO only let consumers track profiles since that's
    #      all they should be working with.
    @property
    def pack(self) -> FirefoxPack:
        return self._pack

    #TODO try to handle this here instead of subclasses
    @pack.setter
    def pack(self, pack: FirefoxPack) -> None:
        raise NotImplementedError

    # TODO should this be in the base class?
    @property
    def profiles(self) -> set[AppProfile]:
        return self._profiles

    @property
    def version(self) -> Version:
        return self._version

    #TODO
    @version.setter
    def version(self, version: Version) -> None:
        raise NotImplementedError
