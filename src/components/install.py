# install.py
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

import os
import shutil
import logging

from os.path import join, exists
from typing import Optional, Callable
from enum import Enum

from addwater.utils.paths import DOWNLOAD_DIR

log = logging.getLogger(__name__)

# TODO rework to use AppDetails
class InstallManager():

    _install_theme: callable
    _set_preferences: callable
    _uninstall_theme: callable

   # TODO ensure that this class can never create its own GSettings objects. If
   # it really needs it, it must be injected in the args. Minimize cases of that.

    def __init__(self, installer: callable, preference_handler: callable=None, uninstaller: callable=None):
        self._install_theme = installer

        if preference_handler:
            self._set_preferences = preferences_handler
        else:
            self._set_preferences = _set_theme_prefs

        if uninstaller:
            self._uninstall_theme = uninstaller
        self._uninstall_theme = _do_uninstall_theme


    """PUBLIC METHODS"""

    def full_install(self, app_details: callable, profile_id: str, color_palette: str, version: int, gset_reader):
        """Kick off installing theme and setting its user.js preferences.

        Args:
            app_details = AppDetails instance set up for this app
            profile_id = id of the profile as it appears in filesystem.
            color_palette = name of the color palette to import
            version = theme version to install
        """
        log.info('Starting a full install...')
        log.debug(f'Profile: {profile_id}')
        log.debug(f'Version: v{version}')
        log.debug(f'Color Palette: {color_palette}')

        app_name = app_details.get_name().lower()
        app_path = app_details.get_data_path()
        color_palette = color_palette.lower()
        profile_path = join(app_path, profile_id)

        app_options = app_details.get_options()

        if not exists(profile_path):
            raise FatalBackendException('Install failed. Profile folder doesn\'t exist.')


        # Run install script
        try:
            self._install_theme(
                profile_path=profile_path,
                color_palette=color_palette,
                # TODO move this theme_path to app_details
                theme_path=join(
                    DOWNLOAD_DIR, f'{app_name}-{version}-extracted', f'{app_name}-gnome-theme'
                ),
            )
            self._set_preferences(profile_path, app_options, gset_reader)
        except InstallException as err:
            log.critical(err)
            return InstallStatus.FAILURE

        log.info('Full install done.')
        return InstallStatus.SUCCESS


    def quick_install(self, app_details: callable, profile_id: str, color_palette: str, version: int,):
        """Installs theme files but doesn't change any user preferences. This is
        useful for updating in the background."""

        log.info('Starting a quick install...')
        log.debug(f'Profile: {profile_id}')
        log.debug(f'Version: v{version}')
        log.debug(f'Color Palette: {color_palette}')

        app_name = app_details.get_name.lower()
        app_path = app_details.get_data_path()
        color_palette = color_palette.lower()
        profile_path = join(app_path, profile_id)

        if not exists(profile_path):
            raise FatalBackendException('Install failed. Profile folder doesn\'t exist.')

        try:
            self._install_theme(
                profile_path=profile_path,
                color_palette=color_palette,
                # TODO move this theme_path to app_details
                theme_path=join(
                    DOWNLOAD_DIR, f'{app_name}-{version}-extracted', f'{app_name}-gnome-theme'
                ),
            )
        except (InstallException, FileNotFoundError) as err:
            log.critical(err)
            return InstallStatus.FAILURE

        log.info('Quick install done.')
        return InstallStatus.SUCCESS

    def uninstall(self, profile_path: str) -> Enum:
        try:
            self._uninstall_theme(profile_path)
        except InstallException as err:
            log.critical(err)
            return InstallStatus.FAILURE

        return InstallStatus.SUCCESS



"""PRIVATE FUNCTIONS"""

"""Default install handlers. Can be overridden at InstallManager construction."""
def _set_theme_prefs(profile_path: str, options: list[dict], gset_reader) -> None:
    """Update user preferences in user.js according to GSettings.

    Args:
        settings = Gio.Settings object to read the values of the keys

    """
    log.info('Setting theme preferences in profile data...')

    user_js = join(profile_path, "user.js")
    # FIXME If the user.js file is gone, the other required prefs won't be set here
    # and thus the theme will not work properly
    try:
        with open(file=user_js, mode="r", encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []
    with open(file=user_js, mode="w", encoding='utf-8') as file:
        for group in options:
            for option in group["options"]:
                pref_name = f'gnomeTheme.{option["js_key"]}'
                pref_value = str(gset_reader.get_boolean(option["key"])).lower()
                full_line = f"""user_pref("{pref_name}", {pref_value});\n"""

                found = False
                for i in range(len(lines)):
                    # This is easier than a for-each
                    if pref_name in lines[i]:
                        lines[i] = full_line
                        found = True
                        break
                if found is False:
                    lines.append(full_line)
                log.debug(f'{pref_name} -> {pref_value}')

        file.writelines(lines)

    log.info("Done.")


def _do_uninstall_theme(profile_path: str) -> None:
    log.info('Uninstalling theme from profile...')
    log.debug(f'Profile path: {profile_path}')
    # Delete theme folder
    try:
        # TODO make this app agnostic. Pass this in from app_details or something.
        chrome_path = join(profile_path, "chrome", "firefox-gnome-theme")
        shutil.rmtree(chrome_path)
    except FileNotFoundError:
        pass

    # TODO remove css import lines

    # Set all user_prefs to false
    user_js = join(profile_path, "user.js")
    try:
        with open(file=user_js, mode="r", encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        log.info("Done.")
        return

    # TODO find relevant exceptions for writing to a file
    try:
        with open(file=user_js, mode="w", encoding='utf-8') as file:
            # This is easier than a foreach
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)
    except OSError as err:
        log.error(f'Resetting user.js prefs to false failed: {err}')
        raise InstallException('Uninstall failed')

    log.info('Done.')



class InstallStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

class InstallException(Exception):
    pass
