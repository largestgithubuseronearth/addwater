# paths.py

import os.path
from gi.repository import GLib

# PATHS AVAILABLE
# TODO How do XDG dirs work when installed locally (not flatpak)?
XDG_CACHE_DIR = GLib.get_user_cache_dir()
XDG_DATA_DIR = GLib.get_user_data_dir()
XDG_CONFIG_DIR = GLib.get_user_config_dir()


CACHE_DOWNLOADS = XDG_CACHE_DIR + "/downloads/"

def init_paths():
    try:
        os.mkdir(path=CACHE_DOWNLOADS)
        print("LOG: CACHE_DOWNLOADS directory made.")
    except FileExistsError as err:
        print("LOG: CACHE_DOWNLOADS already exists. Skipped.")
    except FileNotFoundError as err:
        print("CRITICAL: Couldn't find parent dir when initializing dirs")
        print(err)
