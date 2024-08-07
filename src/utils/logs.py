# logs.py
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
from datetime import datetime, timezone, timedelta
import os, os.path
from gi.repository import Gtk, Adw
from . import paths

log = logging.getLogger(__name__)
def init_logs():
    LOG_DIR = paths.LOG_DIR
    try:
        # TODO can this send to both logfile AND to console?
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        LOGFILE = os.path.join(LOG_DIR, f"addwater_{now}.log")
        logging.basicConfig(filename=LOGFILE,
                            filemode="a",
                            style="{",
                            format="[{levelname}] {name} — {asctime} || {message}",
                            datefmt="%H:%M",
                            level=logging.DEBUG)
    except:
        print("Couldn't initialize log file")


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
            if difference.days > 14:
                os.remove(os.path.join(LOG_DIR, each.name))
                log.info(each.name, "removed")

    # TODO Add to top of log file information about system and dependencies such as:
    # distro
    # desktop environment
    # flatpak or not?
    info = f"""
    ------------------------------------------------------------------------
    System Info:
    Add Water — An installer for the GNOME theme for Firefox and Thunderbird
    Time (UTC): {datetime.now(timezone.utc)}
    GTK version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}
    ADW version: {Adw.MAJOR_VERSION}.{Adw.MINOR_VERSION}.{Adw.MICRO_VERSION}
    ------------------------------------------------------------------------
    """
    logging.debug(info)