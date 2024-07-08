# theme_actions.py
# TODO make sure these commands work regardless of shell user has

import subprocess
import os
import os.path
import tarfile

from gi.repository import Gio
from . import paths
from .logs import logging

log = logging.getLogger(__name__)

DL_CACHE = paths.DOWNLOAD_DIR

def install_firefox(firefox_path, profile, version):
    """Installs Firefox theme from a downloaded release

    Args

    firefox_path: String, Full OS path to folder that stores all user profiles. e.g. /var/home/myname/.mozilla/firefox/\n
    profile: String, Full profile id which includes the random string prefix.\n
    version: int, Theme version to install. May be allowed to be changed in the future.\n
    """
    extract_dir = extract_release(app="firefox", version=version)
    if extract_dir is None:
        log.error("Extraction failed. Installation cancelled")
        return False

    profile_arg = "-p"
    if profile is None:
        profile_arg = ""
        profile = ""

    # Must rename the inner folder to "firefox-gnome-theme" for the provided script to work. Otherwise the theme won't show properly
    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith("rafaelmardojai-firefox-gnome-theme"):
                old = os.path.join(extract_dir, each.name)
                new = os.path.join(extract_dir, "firefox-gnome-theme")
                os.rename(old, new)

    script_path = os.path.join(extract_dir, "firefox-gnome-theme", "scripts", "install.sh")

    # TODO Make my own installation script to replace the theme dev's provided bash script. Should be simple to extract the files and add lines to the user.js and css files.
    try:
        log.info(f"Command run to install:  \n", script_path, profile_arg, profile, "-f", firefox_path)
        subprocess.run([script_path, profile_arg, profile, "-f", firefox_path],
                        capture_output=True,
                        check=True)
    except CalledProcessError as err:
        print("Install Firefox Failed")
        log.critical(f"Install CMD failed ;; Return={err.returncode} ;; Full command: {err.args}")
        return False

    log.info(f"Installed Firefox successfully.")
    print(f"Installed Firefox successfully.")
    Gio.Settings(schema_id="dev.qwery.AddWater.Firefox").set_int("installed-version", version)


def extract_release(app, version):
    name = f"{app}-{version}"
    zipfile = os.path.join(DL_CACHE, f"{name}.tar.gz")
    extract_dir = os.path.join(DL_CACHE, f"{name}-extracted/")

    if os.path.exists(extract_dir):
        log.info(f"{name} already extracted. Skipping.")
        return extract_dir

    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        return None

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir,
                        filter="data")

    log.info(f"{name} tarball extracted successfully.")
    return extract_dir
