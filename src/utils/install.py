# theme_actions.py
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

import os, shutil
import os.path
import tarfile

from gi.repository import Gio
from . import paths
from .logs import logging

log = logging.getLogger(__name__)

DL_CACHE = paths.DOWNLOAD_DIR

def install_firefox_theme(version, profile_path, theme):
    # TODO ensure complete functional parity with install script
    """Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """

    # Check paths to ensure they exist
    if os.path.exists(profile_path) is False:
        log.error("profile_path not found. Install canceled.")
        return

    # TODO move 'extract tarball' step into 'download theme release' step
    theme_path = extract_release(app="Firefox", version=version)

    if theme_path == None:
        log.error(f"Failed to extract Firefox v{version}")
        return
    elif os.path.exists(theme_path) is False:
        log.error("theme_path not found. Install canceled.")
        return


    # Make chrome folder if it doesn't already exist
    chrome_path = os.path.join(profile_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileExistsError:
        pass
    except FileNotFoundError:
        log.critical("Install path does not exist. Install canceled.")
        return False


    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path,
        dst=os.path.join(chrome_path, "firefox-gnome-theme"),
        dirs_exist_ok=True
    )

    # Add import lines to CSS files, and creates them if necessary.
    css_files = [
        "userChrome.css",
        "userContent.css"
    ]

    for each in css_files:
        p = os.path.join(chrome_path, each)
        try:
            with open(file=p, mode="r") as file:
                lines = file.readlines()
                log.debug(f"Found {each}.")
        except FileNotFoundError:
                lines = []
                log.debug(f"Creating {each}.")

        with open(file=p, mode="w") as file:
            # Remove old import lines
            remove_list = []
            for line in lines:
                if "firefox-gnome-theme" in line:
                    lines.remove(line)
            log.debug("Removed prior import lines")

            # Add new import lines
            # TODO inserting like this puts all three imports onto the same line. Doesn't seem to cause issues though.
            if theme != "adwaita":
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/light-{theme}.css";')
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/dark-{theme}.css";')
                log.debug(f"Installing the {theme} theme")
            import_line = f'@import "firefox-gnome-theme/{each}";'
            lines.insert(0, import_line)

            file.writelines(lines)
            log.debug(f"{each} finished")


    # Backup user.js and replace with provided version that includes the prerequisite prefs
    user_js = os.path.join(profile_path, "user.js")
    user_js_backup = os.path.join(profile_path, "user.js.bak")
    if os.path.exists(user_js) is True and os.path.exists(user_js_backup) is False:
        os.rename(user_js, user_js_backup)

    template = os.path.join(chrome_path, "firefox-gnome-theme", "configuration", "user.js")
    shutil.copy(template, profile_path)

    log.info("Install successful")


def extract_release(app, version):
    # TODO refactor to be cleaner
    name = f"{app}-{version}"
    zipfile = os.path.join(DL_CACHE, f"{name}.tar.gz")
    extract_dir = os.path.join(DL_CACHE, f"{name}-extracted/")

    if os.path.exists(extract_dir):
        log.info(f"{name} already extracted. Skipping.")
        return os.path.join(extract_dir, "firefox-gnome-theme")

    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        return None

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir,
                        filter="data")

    # Must rename the inner folder to "firefox-gnome-theme" for the provided script to work. Otherwise the theme won't show properly
    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith("rafaelmardojai-firefox-gnome-theme"):
                old = os.path.join(extract_dir, each.name)
                new = os.path.join(extract_dir, "firefox-gnome-theme")
                os.rename(old, new)
    print("new: ", new)
    log.info(f"{name} tarball extracted successfully.")
    return new
