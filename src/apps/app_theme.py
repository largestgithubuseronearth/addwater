from addwater import AppProfile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus
from gi.repository import Gio
from packaging.version import Version
from typing import readonly, abstractmethod

# TODO abstract AppDetails class to define the interface
# Move what Backend does into this.

class AppTheme:
    _name: readonly[str]
    _enabled:  bool
    _pack:     FirefoxPack
    _profiles: set[AppProfile]
    _settings: readonly[Gio.Settings]
    _version:  Version

    # METHODS

    @abstractmethod
    def install(self, profile: AppProfile) -> InstallStatus:
        """Apply base theme files. Don't configure anything here."""
        raise NotImplementedError

    @abstractmethod
    def uninstall(self, profile: AppProfile) -> InstallStatus:
        """Remove theme files. Don't remove configuration"""
        raise NotImplementedError

    @abstractmethod
    def update(self) -> OnlineStatus:
        """Query for updates and download them if available"""
        raise NotImplementedError

    # PROPERTIES

    # TODO automatically write to the file when this is changed
    @abstractmethod
    @property
        """Theme options that can be configured by the user. Not to be
            confused with Add Water settings nor app-specific GSettings"""
    def preferences(self):
        raise NotImplementedError

    @abstractmethod
    @preferences.setter
        """When preferences are set, they will automatically be applied if the
            theme is enabled."""
    def preferences(self, prefs) -> InstallStatus:
        raise NotImplementedError

    # TODO only let consumers track profiles since that's
    #      all they should be working with.
    @property
    def pack(self) -> FirefoxPack:
        return self._pack

    #TODO try to handle this here instead of subclasses
    @abstractmethod
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
    @abstractmethod
    @version.setter
    def version(self, version: Version) -> None:
        raise NotImplementedError

    @property
    def name(self) -> readonly[str]:
        return self._name
