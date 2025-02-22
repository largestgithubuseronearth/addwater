# logs.py
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

# TODO standardize all logs to make info logs more meaningful. Debug should include the tech details and info should only communicate the actual purpose and action that's being done and whether it was successful or not.

import logging
import os
import os.path
import sys
from datetime import datetime, timedelta, timezone

from addwater.info import PROFILE, VERSION
from gi.repository import Adw, Gtk

from . import paths


def init_logs():
    """Set up logging system"""
    LOG_DIR = paths.LOG_DIR
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        CURRENT_LOGFILE = os.path.join(LOG_DIR, f"addwater_{now}.log")

        file_handler = logging.FileHandler(CURRENT_LOGFILE)
        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setLevel(logging.DEBUG)
        if PROFILE == "development":
            console_handler.setLevel(logging.DEBUG)
        elif PROFILE == "default":
            console_handler.setLevel(logging.INFO)

        logging.basicConfig(
            handlers=[file_handler, console_handler],
            style="{",
            # TODO how to give a consistent spacing between levelname and name?
            format="[{levelname}]   {name} — {asctime} || {message}",
            datefmt="%H:%M",
            level=logging.DEBUG,
        )
    except Exception as err:
        print("Couldn't initialize log file: ", err)

    # Delete logs that are over two weeks old
    with os.scandir(path=LOG_DIR) as scan:
        oldest = ""
        for each in scan:
            time = datetime.strptime(
                each.name,
                "addwater_%Y-%m-%d.log",
            )
            time = time.replace(tzinfo=timezone.utc)
            difference = datetime.now(timezone.utc) - time
            if difference.days > 7:
                os.remove(os.path.join(LOG_DIR, each.name))

    info = f"""
	------------------------------------------------------------------------
	------------------------------------------------------------------------
	System Info:
	Add Water — An installer for the GNOME theme for Firefox and Thunderbird
	Version: {VERSION}
	Time (UTC): {datetime.now(timezone.utc)}
	GTK version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}
	ADW version: {Adw.MAJOR_VERSION}.{Adw.MINOR_VERSION}.{Adw.MICRO_VERSION}
	------------------------------------------------------------------------
	"""
    logging.debug(info)
