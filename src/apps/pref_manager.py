from addwater.components import InstallStatus
from typing import abstractmethod, abc

class PreferenceHandler(abc):
    _apply_on_change: bool

    @abstractmethod
    def apply_preferences(self) -> InstallStatus:
        raise NotImplementedError

    # PROPERTIES

    # TODO automatically write to the file when this is changed

    # @abstractmethod
    # @property
    # def preferences(self):
    #     """Theme options that can be configured by the user. Not to be
    #         confused with Add Water settings nor app-specific GSettings"""
    #     raise NotImplementedError
    #
    # @abstractmethod
    # @preferences.setter
    # def preferences(self, prefs) -> InstallStatus:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # @property
    # def apply_on_change(self) -> bool:
    #     """Whether changes should automatically be written as soon as they are
    #         changed in the UI"""
    #     return self._apply_on_change
    #
