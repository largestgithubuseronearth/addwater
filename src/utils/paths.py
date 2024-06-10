# paths.py

import os.path
from .logs import logging
from gi.repository import GLib

logger = logging.getLogger(__name__)

# PATHS AVAILABLE TO MY APP
XDG_CACHE_DIR = GLib.get_user_cache_dir()
XDG_DATA_DIR = GLib.get_user_data_dir()
XDG_CONFIG_DIR = GLib.get_user_config_dir()

APP_CACHE = XDG_CACHE_DIR + "/add-water/"
APP_CONFIG = XDG_CONFIG_DIR + "/add-water/"
APP_DATA = XDG_DATA_DIR + "/add-water/"

# FIREFOX PATHS
FIREFOX_BASE = "~/.mozilla/firefox"
FIREFOX_FLATPAK = "~/.var/app/org.mozilla.Firefox/.mozilla/firefox/"
# TODO is this snap dir still correct?
FIREFOX_SNAP = "~/snap/firefox/common/.mozilla/firefox/"

def init_paths():
    paths = [APP_CACHE]

    for each in paths:
        try:
            os.mkdir(path=each)
            logger.info(f"{each} directory created.")
        except FileExistsError as err:
            logger.info(f"{each} already exists. Skipped.")
        except FileNotFoundError as err:
            logger.error("Couldn't find parent dir when initializing dirs ::", err)
            return

    logger.info("All paths initialized.")
