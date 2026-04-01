# firefox_details.py
#
# Copyright 2025 Qwery
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
from configparser import ConfigParser
from enum import Enum
from os.path import exists, join
from typing import Any, Callable, Optional
from pathlib import Path

from addwater.utils import paths
from gi.repository import Gio
from packaging.version import Version

from addwater import info
from addwater.profile import Profile
from .firefox_install import install_for_firefox
from .firefox_options import FIREFOX_OPTIONS
from .firefox_paths import FIREFOX_PATHS

log = logging.getLogger(__name__)

# TODO specialize this into Firefox first and then make it an injectible,
# dynamic class in the future once the app's core logic has settled and it's
# clearer what exact variables and roles AppDetails should take responsibility
# for.


class FirefoxAppDetails:
    """Conveniently stores important app info to reduce how many arguments
    need to be passed around. If a method requires more than three pieces of info,
    just pass this object into managers and let them find what they need.

    Avoid altering the state of an AppDetails instance outside of
    construction or dedicated setter methods in the backend interface.


    Args
        name: proper, capitalized name of the app. i.e. 'Firefox' or 'Thunderbird
        options: theme options that the user can modify from the page GUI
        data_path:full path to the directory which includes all profile folders
                                        as well as profiles.ini and installs.ini
    """

    package_formats: list[dict[str, str]] = FIREFOX_PATHS

    # primary
    name: str = "Firefox"
    installed_version: Version

    # install
    installer: Callable = install_for_firefox
    options: list[dict[Any, Any]] = FIREFOX_OPTIONS
    data_path: str

    # online
    theme_gh_url: str = (
        "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"
    )

    save_to = paths.DOWNLOAD_DIR
    app_folder = "firefox"
    theme_folder = "firefox-gnome-theme"
    full_path = join(save_to, app_folder, theme_folder)

    def __init__(self):
        self.settings = self.get_new_gsettings()

        version = Version(self.settings.get_string("installed-version"))
        self.set_installed_version(version)

        current_path = self.settings.get_string("data-path")
        try:
            self.set_data_path(current_path)
        except FileNotFoundError as err:
            available_paths = self._find_data_paths(self.package_formats)
            self.set_data_path(available_paths[0]["path"])

    """PUBLIC METHODS"""

    def reset_settings(self):
        """Resets all GSettings keys to their default"""
        log.info(f"Resetting all gsettings for {self.name}")
        self.settings.reset("theme-enabled")
        self.settings.reset("data-path")
        self.settings.reset("autofind-paths")
        self.settings.reset("installed-version")
        self.settings.reset("profile-selected")

        for group in self.options:
            for option in group["options"]:
                gset_key = option["key"]
                self.settings.reset(gset_key)
        log.info("done. gsettings reset")

    """Getters"""

    def get_new_gsettings(self):
        """Returns a ready-to-use Gsettings reader pre-configured for the relevant app theme."""
        log.debug(f"creating new Gsettings reader for {self.get_name()}")
        schema_id = info.APP_ID + "." + self.get_name()
        return Gio.Settings(schema_id=schema_id)

    def get_theme_folder_name(self):
        return self.theme_folder

    def get_download_path_info(self) -> tuple:
        """Returns a tuple of ([download cache path], [app folder], [theme files folder])

        Join these together to get the full path to the theme files for installation.
        """
        return (self.save_to, self.app_folder, self.theme_folder)

    def get_full_theme_path(self) -> str:
        return self.full_path

    def get_name(self):
        return self.name

    def get_data_path(self):
        return self.data_path

    def get_installer(self):
        return self.installer

    def get_installed_version(self):
        return self.installed_version

    def get_options(self):
        # TODO grab only the details the consumer would need.
        #      Multiple methods or add a flag?
        return self.options

    def get_profiles(self) -> list[Profile]:
        return self._find_profiles(self.data_path)


    def get_info_url(self):
        return self.theme_gh_url

    """Setters"""

    def set_data_path(self, new_path: str):
        log.info(f"Setting {self.name} data path: {new_path}")
        if exists(join(new_path, "profiles.ini")):
            self.data_path = new_path
            self.settings.set_string("data-path", self.data_path)
            log.info(f"Valid path. Done.")
            return

        log.error(f"Tried to set app_path to non-existant path. Path given: {new_path}")
        raise FileNotFoundError("Invalid data path")

    def set_installed_version(self, new_version: Version) -> None:
        log.debug(f"Set installed version number to {new_version}")
        if not isinstance(new_version, Version):
            log.error("gave something that isn't a Version object. Fail")
            log.debug(f"input: {type(new_version)}")
            raise TypeError

        self.settings.set_string("installed-version", str(new_version))
        self.installed_version = new_version

    """PRIVATE METHODS"""

    @staticmethod
    def _find_profiles(app_path: Path) -> list[Profile]:
        cfg = ConfigParser()
        profiles = []

        profiles_ini = join(app_path, "profiles.ini")
        if not exists(profiles_ini):
            raise FileNotFoundError("profiles.ini not found")

        cfg.read(profiles_ini)
        for sect in filter(lambda sect: sect.startswith("Profile"), cfg.sections()):
            name = cfg[sect]["Name"]
            id = cfg[sect]["Path"]
            fav = False
            try:
                # TODO it would be nice to flatten this check
                if cfg[sect]["Default"] == '1':
                    fav = True
            except KeyError:
                pass

            filepath = Path(join(app_path, id))

            # TODO add package label to the profile
            #      probably requires pooling all profiles into one model first.
            profiles.append(Profile(name, id, filepath, fav, 'TODO'))

        return profiles

    @staticmethod
    def _find_data_paths(path_list: list[dict[str, str]]) -> list[dict[str, str]]:
        """Iterates over all common Firefox config directories return all that exist.

        Args:
                path_list: Either of the list of dicts from the paths module to make it easy to iterate over
        """
        found = []
        for each in path_list:
            path = each["path"]
            if exists(join(path, "profiles.ini")):
                name = each["name"]
                log.debug(f"Found Firefox path: {name} — {path}")
                found.append(each)
        if not found:
            log.critical("Could not find any valid data paths. App cannot function.")

        return found
