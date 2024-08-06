# paths.py
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

# This module owns all app paths and must be used when referring to general paths like config or firefox paths
# TODO make list here of all firefox locations and the "name". List of

import os
from os.path import expanduser, join
from .logs import logging
from gi.repository import GLib

log = logging.getLogger(__name__)

# APP PATHS
XDG_CACHE_DIR = GLib.get_user_cache_dir()
XDG_DATA_DIR = GLib.get_user_data_dir()
XDG_CONFIG_DIR = GLib.get_user_config_dir()

APP_CACHE = join(XDG_CACHE_DIR, "add-water")
APP_CONFIG = join(XDG_CONFIG_DIR, "add-water")
APP_DATA = join(XDG_DATA_DIR, "add-water")

DOWNLOAD_DIR = join(APP_CACHE, "downloads")
LOG_DIR = join(APP_CACHE, "logs")


# FIREFOX PATHS
FIREFOX_BASE = expanduser("~/.mozilla/firefox/")
FIREFOX_FLATPAK = expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FIREFOX_SNAP = expanduser("~/snap/firefox/common/.mozilla/firefox/")

FIREFOX_LIBREWOLF_BASE = expanduser("~/.librewolf/")
FIREFOX_LIBREWOLF_FLATPAK = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")
FIREFOX_LIBREWOLF_SNAP = expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")

FIREFOX_FLOORP_BASE = expanduser("~/.floorp")
FIREFOX_FLOORP_FLATPAK = expanduser("~/.var/app/one.ablaze.floorp/.floorp")


def init_paths():
    paths = [APP_CACHE, DOWNLOAD_DIR, LOG_DIR]
    for each in paths:
        try:
            os.mkdir(path=each)
            log.info(f"{each} directory created.")
            print(f"{each} directory created.")
        except FileExistsError as err:
            log.info(f"{each} already exists. Skipped.")
            print(f"{each} already exists. Skipped.")
        except FileNotFoundError as err:
            log.error("Couldn't find parent dir when initializing dirs ::", err)
            print("Couldn't find parent dir when initializing dirs ::", err)
            return

    log.info("All paths initialized.")
