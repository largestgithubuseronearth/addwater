# backend.py
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

import logging
import os
import shutil
import requests

from enum import Enum
from os.path import join, exists
from typing import Optional, Callable
from configparser import ConfigParser

from gi.repository import Gio
from .components.online import OnlineManager
from .utils import exceptions as exc
from .utils.paths import DOWNLOAD_DIR

log = logging.getLogger(__name__)

# FIXME if the theme files get lost, there is no way for the app to ever install until another update or the user resets the app
# It should attempt to re-download it

class AddWaterBackend():
    """This class handles everything that doesn't relate to the GUI such as installing the theme, getting updates, finding profiles, etc.
    This class can live without a GUI frontend to allow for background updating.

    Args:
        app_name = proper name of app; Firefox or Thunderbird
        app_path = path to where profiles and
        theme_url = url to github releases api page
    """

    installed_version: int
    update_version: int

    app_options: list[dict]
    app_path: str
    installer: callable # This is passed in to allow for the backend to support both apps, and to easily swap out install methods

    profile_list: list[dict[str,str]]

    online_manager: callable

    def __init__(self, app_name: str, app_path: str, app_options: list[dict], installer: callable, theme_url: str):
        log.info("Backend is alive!")

        if not exists(app_path):
            raise exc.FatalBackendException('Profile path does not exist')

        self.app_options = app_options
        self.installer = installer
        self.app_name = app_name
        self.set_app_path(app_path)

        self.online_manager = OnlineManager(theme_url=theme_url)

        self.settings = Gio.Settings(schema_id=f'dev.qwery.AddWater.{app_name}')
        self.installed_version = self.settings.get_int('installed-version')

        try:
            self.profile_list = self._find_profiles(self.app_path)
        except FileNotFoundError as err:
            log.critical(err)
            raise exc.FatalPageException(err)


    """PUBLIC METHODS

    For these methods, it's often impossible to avoid modifying object states. So it's
    important for these methods to be readable and concise, and modify as little
    as possible.
    """

    def get_updates(self):
        return self.online_manager.get_updates_online(
            installed_version=self.installed_version,
            app_name=self.app_name,
        )


    def full_install(self):
        """Setup install method and set userjs preferences"""

        app_name = self.app_name.lower()
        colors = self.settings.get_string('color-theme')
        profile_path = join(self.app_path, self.settings.get_string('last-profile'))
        version = self.online_manager.get_update_version()

        if not exists(profile_path):
            raise exc.FatalPageException('Install failed. Profile doesn\'t exist.')

        self.settings.set_int("installed-version", version)

        # Run install script
        try:
            self.installer(
                profile_path=profile_path,
                theme_color=colors,
                theme_path=join(
                    DOWNLOAD_DIR, f'{app_name}-{version}-extracted', f'{app_name}-gnome-theme'
                ),
            )
            self.installer._set_theme_prefs(profile_path, self.app_options, self.settings)
        except exc.InstallException as err:
            log.error(err)


    def get_app_options(self):
        return self.app_options


    def get_profile_list(self):
        return self.profile_list


    def quick_install(self):
        """Installs theme files but doesn't change any user preferences. This is useful for updating in the background."""
        app_name = self.app_name.lower()
        profile_path = join(self.app_path, self.settings.get_string('last-profile'))
        colors = self.settings.get_string('color-theme')
        version = self.update_version

        if not exists(profile_path):
            raise exc.FatalPageException('Install failed. Profile doesn\'t exist.')

        self.settings.set_int("installed-version", version)

        # Run install script
        try:
            self.installer(
                profile_path=profile_path,
                theme_color=colors,
                theme_path=join(
                    DOWNLOAD_DIR, f'{app_name}-{version}-extracted', f'{app_name}-gnome-theme'
                ),
            )
        except exc.InstallException as err:
            log.critical(err)
            raise exc.InstallException(err)


    def remove_theme(self):
        profile_path = join(self.app_path, self.settings.get_string('last-profile'))
        self.installer_do_uninstall_theme(profile_path)


    def set_app_path(self, new_path: str):
        if exists(new_path):
            self.app_path = new_path
            log.info('Set app path to %s', new_path)
            return

        log.error('Tried to set app_path to non-existant path')
        raise InterfaceMisuseError('Path given does not exist')





    """PRIVATE METHODS

    All private methods should be static and not rely on modifying the object state;
    this helps avoid unexpected behavior and aid in testing these important methods.
    """

    @staticmethod
    def _find_profiles(app_path: str) -> list[dict[str,str]]:
        """Reads the app configuration files and returns a list of profiles. The user's preferred profiles are first in the list.

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
            log.critical('install.ini file not found')
            raise FileNotFoundError('installs.ini file not found')
        if not exists(profiles_file):
            log.critical('profiles.ini file not found')
            raise FileNotFoundError('profiles.ini file not found')

        # Find preferred profile first so it's always at top of list
        cfg.read(install_file)
        for each in cfg.sections():
            default_profile = cfg[each]["Default"]
            defaults.append(default_profile)
            profiles.append({"id" : default_profile,
                            "name" : default_profile.partition(".")[2] + " (Preferred)"})
            log.debug(f"User's default profile is {default_profile}")

        # Find all others
        cfg.read(profiles_file)
        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s not in defaults:
                    profiles.append({"id" : s,
                                    "name" : s.partition(".")[2]})
            except KeyError:
                pass

        if profiles is None:
            log.critical('Could not find any profiles.')
            raise FileNotFoundError('Could not find any profiles.')
        return profiles






    """ OTHER """

    # TODO move this to public and rename when I'm confident when it's fully
    # safe and the uninstaller is fully settled on
    def _reset_full_uninstall(self):
        # TODO is there a cleaner way to implement this?
        log.info(f"Removing theme from all profiles in path [{self.app_path}]")
        for each in self.profile_list:
            profile_path = join(self.app_path, each["id"])
            self.installer._do_uninstall_theme(profile_path=profile_path)





class InstallStatus(Enum):
    SUCCESS = 0
    FAILURE = 1


class InterfaceMisuseError(Exception):
    pass
