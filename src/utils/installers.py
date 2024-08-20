# installers.py
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
import logging
import shutil
from os.path import join, exists
from . import exceptions as exc

log = logging.getLogger(__name__)

def firefox_installer(profile_path: str, theme_path: str, theme_color: str="adwaita") -> None:
    """FIREFOX ONLY
    Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """
    # Check paths to ensure they exist
    try:
        if not exists(profile_path):
            raise FileNotFoundError('Install failed. Profile path not found.')

        if not exists(theme_path):
            raise FileNotFoundError('Install failed. Cannot find theme files.')
    except (TypeError, FileNotFoundError) as err:
        log.critical(err)
        raise exc.InstallException("Install failed")

    # Make chrome folder if it doesn't already exist
    chrome_path = join(profile_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileNotFoundError:
        log.critical("Install path does not exist. Install canceled.")
        raise exc.InstallException('Profile doesn\'t exist.')
    except FileExistsError:
        pass

    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path,
        dst=join(chrome_path, "firefox-gnome-theme"),
        dirs_exist_ok=True
    )

    # Add import lines to CSS files, and creates them if necessary.
    css_files = ["userChrome.css", "userContent.css"]

    for each in css_files:
        p = join(chrome_path, each)
        try:
            with open(file=p, mode="r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        with open(file=p, mode="w", encoding='utf-8') as file:
            # Remove old import lines
            remove_list = []
            for line in lines:
                if "firefox-gnome-theme" in line:
                    lines.remove(line)

            # Add new import lines
            # FIXME inserting like this puts all three imports onto the same line. Doesn't seem to cause issues though.
            if theme_color != "adwaita":
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/light-{theme_color}.css";')
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/dark-{theme_color}.css";')
                log.debug('Installing the %s theme', theme_color)
            import_line = f'@import "firefox-gnome-theme/{each}";'
            lines.insert(0, import_line)

            file.writelines(lines)
        log.debug("%s finished", each)

    # Backup user.js and replace with provided version that includes the prerequisite prefs
    user_js = join(profile_path, 'user.js')
    user_js_backup = join(profile_path, 'user.js.bak')
    if exists(user_js) is True and exists(user_js_backup) is False:
        os.rename(user_js, user_js_backup)

    # TODO make this app agnostic ↓↓
    template = join(profile_path, 'chrome', 'firefox-gnome-theme', 'configuration', 'user.js')
    shutil.copy(template, profile_path)

    log.info("Install successful")
