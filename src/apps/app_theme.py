from addwater import Profile
from addwater.apps.firefox import FirefoxPack
from addwater.components import InstallStatus, OnlineStatus
from gi.repository import Gio
from packaging.version import Version

# TODO abstract AppDetails class to define the interface
# Move what Backend does into this.

class AppTheme:
    _pack: FirefoxPack
    _profiles: set[Profile]
    _settings: Gio.Settings
    _version: Version

    def __init__(self) -> None:
        pass

    def install(self, profile: Profile) -> InstallStatus:
        pass

    def update(self) -> OnlineStatus:
        pass

    def uninstall(self, profile: Profile) -> InstallStatus:
        pass


    # TODO automatically write to the file when this is changed
    """ Preferences
    Theme options that can be configured by the user. Not to be confused with
    Add Water settings nor app-specific GSettings.
    """
    @property
    def preferences(self):
        pass

    @preferences.setter
    def preferences(self, prefs) -> InstallStatus:
        pass

    # TODO only let consumers track profiles since that's
    #      all they should be working with.
    @property
    def pack(self) -> FirefoxPack:
        return self._pack

    #TODO try to handle this here instead of subclasses
    @pack.setter
    def pack(self, pack: FirefoxPack) -> None:
        pass

    # TODO should this be in the base class?
    @property
    def profiles(self) -> set[Profile]:
        return self._profiles

    @property
    def version(self) -> Version:
        return self._version

    #TODO
    @version.setter
    def version(self, version: Version) -> None:
        pass
