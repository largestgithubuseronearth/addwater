# details.py
#
# Copyright 2024 Qwery
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import join, exists
from typing import Optional
from enum import Enum
from configparser import ConfigParser
import logging

log = logging.getLogger(__name__)

# TODO would it make sense to create "tickets" that are a copy of the original
# instance — only without ability to be modified — rather than passing in the
# original object? This would allow for
class AppDetails():
    """Conveniently stores important app info to reduce how many arguments
    need to be passed around. If a method requires more than three pieces of info,
    just pass this object into managers and let them find what they need.

    Please avoid altering the state of an AppDetails instance outside of
    construction or dedicated setter methods in the backend interface.


    Args:
        name = proper, capitalized name of the app. i.e. 'Firefox' or 'Thunderbird
        options = theme options that the user can modify from the page GUI
        data_path = full path to the directory which includes all profile folders
                        as well as profiles.ini and installs.ini
    """

    name: str
    options: list[dict[any]]
    data_path: str
    autofind_data_path: bool

    profiles_list: list[dict[str,str]]
    installed_version: int

    def __init__(self, name: str, options: list[dict[any]], data_path: str, installed_version: int):
        self.name = name
        self.options = options
        self.set_data_path(data_path)
        self.set_installed_version(installed_version)

        try:
            self.profiles_list = self._find_profiles(self.data_path)
        except FileNotFoundError as err:
            log.critical(err)
            raise FatalBackendError(f'App cannot continue without profile data: {err}')



    """PUBLIC METHODS"""

    """Getters"""
    def get_name(self,):
        return self.name

    def get_data_path(self,):
        return self.data_path

    def get_installed_version(self,):
        return self.installed_version

    def get_options(self,):
        return self.options

    def get_profiles(self,):
        return self.profiles_list


    """Setters"""
    def set_data_path(self, new_path: str):
        log.info(f'Setting {self.name} data path: {new_path}')
        if exists(new_path):
            self.data_path = new_path
            log.info(f'Valid path. Done.')
            return

        log.error(f'Tried to set app_path to non-existant path. Path given: {new_path}')
        raise AppDetailsException('Data path given does not exist')

    def set_installed_version(self, new_version: int,) -> None:
        log.info(f'Set installed version number to {new_version}')
        self.installed_version = new_version



    """PRIVATE METHODS"""
    @staticmethod
    def _find_profiles(app_path: str) -> list[dict[str,str]]:
        """Reads the app profile data files and returns a list of known profiles.
        The user's preferred profiles are always first in the list.

        Args:
        app_path : The full path to where the app stores its profiles and the profiles.ini files

        Returns:
        A list of dicts with all profiles. Each dict includes the full ID path of the profile ["id"], and a display name to present in the UI ["name"].
        """
        cfg = ConfigParser()
        defaults = []
        profiles = []

        install_file = join(app_path, "installs.ini")
        profiles_file = join(app_path, "profiles.ini")

        if not exists(install_file):
            raise FileNotFoundError('installs.ini file not found')
        if not exists(profiles_file):
            raise FileNotFoundError('profiles.ini file not found')

        # Find preferred profile first so it's always at top of list
        cfg.read(install_file)
        for each in cfg.sections():
            default_profile = cfg[each]["Default"]
            defaults.append(default_profile)
            profiles.append({
                "id" : default_profile,
                "name" : default_profile.partition(".")[2] + " (Preferred)"
            })
            log.debug(f"User's default profile is {default_profile}")

        # Find all others
        cfg.read(profiles_file)
        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s in defaults:
                    pass
                profiles.append({
                    "id" : s,
                    "name" : s.partition(".")[2]
                })
            # TODO find a way to be more explicit instead of relying on this except pass
            except KeyError:
                pass

        if profiles is None:
            raise FileNotFoundError('installs.ini and profiles.ini exist but do not have any profiles.')
        return profiles



class AppDetailsException(Exception):
    pass

