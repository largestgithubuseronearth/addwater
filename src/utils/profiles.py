# profiles.py
# Returns a list of profile names for the app path specified.
# TODO This must work for Thunderbird AND Firefox
# TODO is this correct to read the default profile from install.ini` or should I read it from profiles.ini? Likely latter


from configparser import ConfigParser
from gi.repository import GLib, Gio
import logging
import os.path
log = logging.getLogger(__name__)

# TODO find_installs()
def find_installs():
    pass


# Note: First profile in returned list MUST ALWAYS be the user's default/preferred profile
# TODO Make sure this works in the Flatpak!! Was it just incorrectly formatted as a path???
def find_profiles(moz_path):
    install_file = os.path.join(moz_path, "installs.ini")
    profiles_file = os.path.join(moz_path, "profiles.ini")

    cfg = ConfigParser()
    profiles = []

    try:
        # Preferred
        if len(cfg.read(install_file)) == 0:
            raise FileNotFoundError(install_file)

        default_profile = cfg[cfg.sections()[0]]["Default"]
        profiles.append({"id" : default_profile,
                        "name" : default_profile.partition(".")[2] + " (Preferred)"})
        log.debug(f"User's default profile is {default_profile}")

        # All
        if len(cfg.read(profiles_file)) == 0:
            raise FileNotFoundError(profiles_file)

        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s != default_profile:
                    profiles.append({"id" : s,
                                    "name" : s.partition(".")[2]})
            except KeyError:
                pass
    except FileNotFoundError as err:
        log.error(f"Reading INI failed: {err}")
        return

    return profiles
