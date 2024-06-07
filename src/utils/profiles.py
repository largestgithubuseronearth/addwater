# profiles.py
# Returns a list of profile names for the app path specified.
# TODO Find where snaps and flatpak store the profiles ini
# TODO Make this work for both firefox and thunderbird
# TODO is this correct to read the default profile from install.ini` or should I read it from profiles.ini?


from configparser import ConfigParser
from gi.repository import GLib


# Note: First profile in returned list MUST ALWAYS be the user's default/preferred profile
def find_profiles(moz_path):
    cfg = ConfigParser()
    install_file = moz_path + "installs.ini"
    profiles_file = moz_path + "profiles.ini"
    profiles = []

    try:
        # Preferred
        cfg.read(install_file)
        default_profile = cfg[cfg.sections()[0]]["Default"]
        profiles.append({"id" : default_profile,
                        "name" : default_profile.partition(".")[2] + " (Preferred)"})

        # All
        cfg.read(profiles_file)
        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s != default_profile:
                    profiles.append({"id" : s,
                                    "name" : s.partition(".")[2]})
            except KeyError:
                pass
    except:
        print("Reading profiles ini failed :(")
        return

    return profiles
