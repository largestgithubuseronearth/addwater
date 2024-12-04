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

import logging
import shutil
from enum import Enum
from os import PathLike
from os.path import exists, join
from typing import Callable, Optional

from addwater.utils.paths import DOWNLOAD_DIR

log = logging.getLogger(__name__)


class InstallManager:
    """Provides API for all interactions that write or modify Firefox profiles.
    Make sure this is air-gapped and only accessed via strict pipelines to limit
    programmer errors that may lead to user data loss.

    Methods for installation, setting theme preferences, and uninstalling theme
    can be overridden by injecting your own functions. This leaves the door open
    for supporting different apps or themes in the future.

    args:
        installer = method that writes theme files into the app
        preference_handler = method to, if necessary, handle optional settings
                                that may need to be written to a file somewhere.
        uninstaller = method to remove theme files from app. For now, this must
                        handle removing those settings from pref_handler on its own.
    """

    def __init__(
        self,
        installer: Callable,
        preference_handler: Optional[Callable] = None,
        uninstaller: Optional[Callable] = None,
    ):
        self._installer = installer

        self._preferences_handler = _set_theme_prefs
        if preference_handler:
            self._preferences_handler = preferences_handler

        self._uninstaller = _do_uninstall_theme
        if uninstaller:
            self._uninstaller = uninstaller

    """PUBLIC METHODS"""

    def combined_install(
        self,
        theme_path: PathLike,
        profile_path: PathLike,
        options_results: Optional[dict[str, bool]] = None,
    ) -> Enum:
        # The preference setter should use a dict of gset_key:bool_value to set all the prefs to slim the number of required args.
        """Handle installation of quick and full theme installs

        args:
            theme_path = path to theme files
            profile_path = path to profile which to apply theme to
            options_results = optional; if included, theme options will be
                                updated. otherwise that's skipped
        """
        log.info("kicking off install...")

        if not exists(theme_path) or not exists(profile_path):
            log.error("Install failed. can't find theme path OR profile path.")
            return InstallStatus.FAILURE


        # Run install script
        try:
            self._installer(
                profile_path=profile_path,
                theme_path=theme_path,
            )
            if options_results:
                self._preferences_handler(profile_path, options_results)
        except InstallException as err:
            log.critical(err)
            return InstallStatus.FAILURE

        log.info("install complete!")
        return InstallStatus.SUCCESS

    def uninstall(self, profile_path, folder_name):
        try:
            self._uninstaller(profile_path, folder_name)
        except InstallException as err:
            log.error(err)
            return InstallStatus.FAILURE

        return InstallStatus.SUCCESS


"""PRIVATE FUNCTIONS"""

"""Default install handlers. Can be overridden by injecting functions at construction."""


@staticmethod  # To avoid InstallManager passing self
def _set_theme_prefs(profile_path: str, options: dict[str, bool]) -> None:
    """Update user preferences in user.js according to GSettings.

    Args:
            profile_path = full file path to the profile that the theme will be installed to
            options = the theme options list dicts
            gset_reader = Gio.Settings object preconfigured for the correct schema
                                            to read the values of the keys

    """
    log.info("Setting theme preferences in profile data...")

    user_js = join(profile_path, "user.js")
    # FIXME If the user.js file is gone, the other required prefs won't be set here
    # and thus the theme will not work properly
    try:
        with open(file=user_js, mode="r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []
    with open(file=user_js, mode="w", encoding="utf-8") as file:
        for key, value in options.items():
            pref_name = f"gnomeTheme.{key}"
            pref_value = str(value).lower()  # This MUST be lowercase
            full_line = f"""user_pref("{pref_name}", {pref_value});\n"""

            # TODO simplify this section
            found = False
            for i, line in enumerate(lines):
                # This is easier than a for-each
                if pref_name in line:
                    lines[i] = full_line
                    found = True
                    break
            if found is False:
                lines.append(full_line)
            log.debug(f"{pref_name} -> {pref_value}")

        file.writelines(lines)

    log.info("Done.")


@staticmethod  # To avoid InstallManager passing self
def _do_uninstall_theme(profile_path: str, theme_folder: str) -> None:
    log.info("Uninstalling theme from profile...")
    log.debug(f"Profile path: {profile_path}")

    # Delete theme folder
    try:
        chrome_path = join(profile_path, "chrome", theme_folder)
        shutil.rmtree(chrome_path)
    except FileNotFoundError:
        pass

    # TODO remove css import lines

    # Set all user_prefs to false
    user_js = join(profile_path, "user.js")
    try:
        with open(file=user_js, mode="r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        log.info("Done.")
        return

    try:
        with open(file=user_js, mode="w", encoding="utf-8") as file:
            # TODO find a way to avoid using the index and just edit the line in the list directly
            for i, line in enumerate(lines):
                if "gnomeTheme" in line:
                    lines[i] = line.replace("true", "false")

            file.writelines(lines)
    except OSError as err:
        log.error(f"Resetting user.js prefs to false failed: {err}")
        raise InstallException("Uninstall failed")

    log.info("Done.")


class InstallTypeFlag(Enum):
    QUICK = 0
    FULL = 1


class InstallStatus(Enum):
    SUCCESS = 0
    FAILURE = 1


class InstallException(Exception):
    pass
