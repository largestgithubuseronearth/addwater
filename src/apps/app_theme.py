from addwater import AppProfile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus
from gi.repository import Gio, GLib
from packaging.version import Version
from typing import readonly, abstractmethod

# TODO abstract AppDetails class to define the interface
# Move what Backend does into this.

class AppTheme:
    _name:     readonly[str]
    _cli_tree: readonly[GLib.OptionGroup] | None = None
    _enabled:  bool
    _settings: Gio.Settings
    _version:  Version

    # Methods

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

    # Props

    @property
    def name(self) -> readonly[str]:
        """Display name of this theme"""
        return self._name

    @property
    def cli_command_group(self) -> readonly[GLib.OptionGroup] | None:
        """Optional group of CLI option entries"""
        return self._cli_tree

    @property
    def version(self) -> Version:
        """Currently used version of this theme"""
        return self._version

    @abstractmethod
    @version.setter
    def version(self, version: Version) -> None:
        raise NotImplementedError

