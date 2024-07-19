# paths.py
# This module owns all app paths and must be used when referring to general paths like config or firefox paths

import os.path
from .logs import logging
from gi.repository import GLib

log = logging.getLogger(__name__)

# APP PATHS
XDG_CACHE_DIR = GLib.get_user_cache_dir()
XDG_DATA_DIR = GLib.get_user_data_dir()
XDG_CONFIG_DIR = GLib.get_user_config_dir()

APP_CACHE = os.path.join(XDG_CACHE_DIR, "add-water")
APP_CONFIG = os.path.join(XDG_CONFIG_DIR, "add-water")
APP_DATA = os.path.join(XDG_DATA_DIR, "add-water")

DOWNLOAD_DIR = os.path.join(APP_CACHE, "downloads")
LOG_DIR = os.path.join(APP_CACHE, "logs")


# FIREFOX PATHS
FIREFOX_BASE = os.path.expanduser("~/.mozilla/firefox/")
FIREFOX_FLATPAK = os.path.expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/")
FIREFOX_FLATPAK_WRONG = os.path.expanduser("~/.var/app/org.mozilla.Firefox/.mozilla/firefox/")
FIREFOX_SNAP = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/")
FIREFOX_LIBRE_FLATPAK = os.path.expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/")
# TODO Check base Librewolf path for accuracy
FIREFOX_LIBRE_BASE = os.path.expanduser("~/.librewolf/")


# TODO THUNDERBIRD PATHS

# FIXME this will not log entries on the first run of the app because LOG_DIR hasn't been created yet.
def init_paths():
    paths = [APP_CACHE, DOWNLOAD_DIR, LOG_DIR]
    for each in paths:
        try:
            os.mkdir(path=each)
            log.info(f"{each} directory created.")
        except FileExistsError as err:
            log.info(f"{each} already exists. Skipped.")
        except FileNotFoundError as err:
            log.error("Couldn't find parent dir when initializing dirs ::", err)
            return

    log.info("All paths initialized.")
