# firefox_install.py
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
import os
import shutil
from os import PathLike
from os.path import exists, join

from addwater.components.install import InstallException

log = logging.getLogger(__name__)


@staticmethod  # This is necessary to avoid InstallManager passing self as an arg. "Passed multiple values for profile_path"
def install_for_firefox(
    profile_path: PathLike, theme_path: PathLike
) -> None:
    """Install the Firefox theme. This method should be injected into the
    InstallManager at runtime. If it isn't obvious, this should not be reused for
    installing other app themes.

    Args:
        theme_path: path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path: path to the profile folder in which the theme will be installed.

    """
    # Check paths to ensure they exist
    log.info("Installing theme file for Firefox...")
    try:
        if not exists(profile_path):
            raise FileNotFoundError("Install failed. Profile path not found.")

        if not exists(theme_path):
            raise FileNotFoundError("Install failed. Theme files not found.")
    except (TypeError, FileNotFoundError) as err:
        log.critical(err)
        raise InstallException("Install failed")

    chrome_path = join(profile_path, "chrome")

    _copy_files(chrome_path, theme_path)
    _import_css(chrome_path)

    userjs_template = join(
        chrome_path, "firefox-gnome-theme", "configuration", "user.js"
    )
    _copy_userjs(profile_path, userjs_template)

    log.info("Firefox installation done.")


def _copy_files(chrome_path: str, theme_path: str):
    # Make chrome folder if it doesn't already exist
    log.debug("Copying theme files into profile path...")
    try:
        os.mkdir(chrome_path)
    except FileNotFoundError:
        log.critical("Profile path does not exist. Install canceled.")
        raise InstallException("Profile doesn't exist.")
    except FileExistsError:
        pass

    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path, dst=join(chrome_path, "firefox-gnome-theme"), dirs_exist_ok=True
    )
    log.debug("Done.")


def _import_css(chrome_path: str):
    log.debug("Adding CSS imports...")
    css_files = ["userChrome.css", "userContent.css"]

    for each in css_files:
        p = join(chrome_path, each)
        try:
            with open(file=p, mode="r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            log.debug(f"{each} does not exist. Creating it from scratch")
            lines = []

        with open(file=p, mode="w", encoding="utf-8") as file:
            # Remove old import lines
            for line in lines:
                if "firefox-gnome-theme" in line:
                    lines.remove(line)

            import_lines = []
            import_lines.append(f'@import "firefox-gnome-theme/{each}";\n')

            file.writelines(import_lines + lines)

        log.debug(f"Finished importing {each}")
    log.debug("Done.")


def _copy_userjs(profile_path: str, template_path: str) -> None:
    """Append content of user.js template to the existing user.js if the URL doesn't exist."""
    log.debug("Checking if URL already exists in user.js...")
    user_js = join(profile_path, "user.js")
    user_js_backup = join(profile_path, "user.js.bak")
    url_to_check = "https://github.com/rafaelmardojai/firefox-gnome-theme/"

    # Check if the (Required user.js content) already exists in user.js
    if exists(user_js):
        with open(user_js, "r", encoding="utf-8") as user_js_file:
            content = user_js_file.read()
            if url_to_check in content:
                log.debug("The specified URL already exists in user.js.")
                return True  # URL exists, exit the function

    # Backup user.js if it exists and backup does not exist
    if exists(user_js) and not exists(user_js_backup):
        log.debug("Backing up user's previous user.js file")
        shutil.copy(user_js, user_js_backup)

    # Append the content of the template user.js to the existing user.js
    try:
        with open(template_path, "r", encoding="utf-8") as template_file:
            template_content = template_file.read()

        with open(user_js, "a", encoding="utf-8") as user_js_file:
            user_js_file.write(template_content)
            log.debug("Appended user.js content successfully.")

    except Exception as e:
        log.critical(f"Failed to append to user.js: {e}")
        raise InstallException("Failed to append user.js")

    log.debug("Done.")
