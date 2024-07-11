# profiles.py
# Returns a list of profile names for the app path specified.
# TODO This must work for Thunderbird AND Firefox
# TODO is this correct to read the default profile from install.ini` or should I read it from profiles.ini? Likely latter
# TODO test this entire module again


import os.path
import logging
from configparser import ConfigParser
from gi.repository import GLib, Gio
from . import paths

log = logging.getLogger(__name__)

def find_firefox_path():
    """Iterates over all common Firefox config directories and returns which one exists.

    SUPPORTS: Only Firefox
    """
    path_list = [
        paths.FIREFOX_BASE,
        paths.FIREFOX_FLATPAK,
        paths.FIREFOX_FLATPAK_WRONG,
        paths.FIREFOX_SNAP
    ]
    for each in path_list:
        if os.path.exists(each):
            return each

    return None


# Note: First profile in returned list MUST ALWAYS be the user's default/preferred profile
def find_profiles(moz_path):
    """Reads the app configuration files to adds all of them in a list.
    SUPPORTS: Firefox, Thunderbird

    ARGS:
    moz_path : The path to where the app stores its profiles and the profiles.ini files

    RETURN:
    A list of dicts with all profiles. Each dict includes the full ID of the profile, and a display name to present in the UI without the randomized prefix string.
    The first in the list is always the user's selected default profile.

    """
    install_file = os.path.join(moz_path, "installs.ini")
    profiles_file = os.path.join(moz_path, "profiles.ini")

    cfg = ConfigParser()
    defaults = []
    profiles = []

    try:
        # Preferred
        if len(cfg.read(install_file)) == 0:
            raise FileNotFoundError(install_file)

        # TODO Test that this works with multiple default profiles
        for each in cfg.sections():
            default_profile = cfg[each]["Default"]
            defaults.append(default_profile)
            profiles.append({"id" : default_profile,
                            "name" : default_profile.partition(".")[2] + " (Preferred)"})
            log.debug(f"User's default profile is {default_profile}")

        # All
        if len(cfg.read(profiles_file)) == 0:
            raise FileNotFoundError(profiles_file)

        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s not in defaults:
                    profiles.append({"id" : s,
                                    "name" : s.partition(".")[2]})
            except KeyError:
                pass
    except FileNotFoundError as err:
        log.error(f"Reading INI failed: {err}")
        return

    return profiles
