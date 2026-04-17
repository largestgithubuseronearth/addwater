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
from .firefox_paths import FirefoxPack

log = logging.getLogger(__name__)

class FirefoxAppDetails:
    """
    name: proper, capitalized name of the app. i.e. 'Firefox' or 'Thunderbird
    options: theme options that the user can modify from the page GUI
    """

    # primary
    name: str = "Firefox"
    installed_version: Version

    # install
    installer: Callable = install_for_firefox
    options: list[dict[Any, Any]] = FIREFOX_OPTIONS
    package: FirefoxPack

    # online
    # TODO this should be defined as a const elsewhere
    THEME_URL: str = (
        "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"
    )

    # TODO just save the unzipped download in /tmp/ and then unzip into addwater/cache
    save_to = paths.DOWNLOAD_DIR
    app_folder = "firefox"
    theme_folder = "firefox-gnome-theme"
    full_path = join(save_to, app_folder, theme_folder)

    def __init__(self):
        self.settings = self.get_new_gsettings()

        version = Version(self.settings.get_string("installed-version"))
        self.set_installed_version(version)

        # If the path in GSettings is invalid, use the first available package
        current_path = self.settings.get_string("data-path")
        current_pack = FirefoxPack.new_from_path(Path(current_path))
        if not current_pack:
            available_packs = self._get_valid_packs()
            # TODO what should the app do if no packs are available?
            if not found:
                log.critical("Could not find any valid data paths. App cannot function.")
                return
            self.set_package(available_packs[0])
            return

        self.set_package(current_pack)
        return

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

    def get_name(self) -> str:
        return self.name

    def get_package(self) -> FirefoxPack:
        return self.package

    def get_installer(self):
        return self.installer

    def get_installed_version(self):
        return self.installed_version

    def get_options(self):
        # TODO grab only the details the consumer would need.
        #      Multiple methods or add a flag?
        return self.options

    def get_profiles(self) -> list[Profile]:
        return self._find_profiles(self.package)


    def get_info_url(self):
        return self.THEME_URL

    """Setters"""

    def set_package(self, package: FirefoxPack):
        # check if path is valid before setting
        _ini = package.get_profile_ini()

        self.settings.set_string("data-path", str(package.path))
        self.package = package


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
    def _find_profiles(package: FirefoxPack) -> list[Profile]:
        cfg = ConfigParser()
        profiles = []

        profiles_ini = package.get_profile_ini()

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

            filepath = join(package.path, id)

            # TODO add package label to the profile
            #      probably requires pooling all profiles into one model first.
            profiles.append(Profile(name, id, filepath, fav, 'TODO'))

        return profiles

    def _get_valid_packs() -> list[FirefoxPack]:
        found = []
        for pack in FirefoxPack:
            try:
                if (pack.get_profile_ini()):
                    found.append(pack)
            except FileNotFoundError:
                pass

        return found
