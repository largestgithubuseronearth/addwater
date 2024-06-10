# theme_actions.py
# TODO make sure these commands work regardless of shell user has
# TODO use fnmatch or glob module to find the inner folder of the theme which is randomized
#   ALTERNATIVE: Find way to list what dirs are in the release folder and just automatically pick the first and only one.

import subprocess
import os
import os.path
import tarfile

from . import paths
from .logs import logging

log = logging.getLogger(__name__)

DL_CACHE = paths.DOWNLOAD_DIR

def install_firefox(firefox_path, profile, version):
    extract_dir = extract_release(app="firefox", version=version)
    if extract_dir is None:
        log.error("Extraction failed. Installation cancelled")
        return False

    profile_arg = "-p"
    if profile is None:
        profile_arg = ""
        profile = ""
    # TODO This is all temporary toying
    p = os.scandir(path=extract_dir)
    print("WEEEEEEEEEED:   ", p)
    script_path = DL_CACHE + extract_dir + p + "scripts/" + "install.sh"
    # Preview of the final command
    print("." + script_path, profile_arg, profile, "-f", firefox_path)

    # TODO MAKE SURE THIS COMMAND IS 100% SAFE BEFORE RUNNING
    # r = subprocess.run(["." + script_path, profile_arg, profile, "-f", firefox_path],
                         # capture_output=True)


def uninstall_firefox_theme(firefox_path):
    pass
    # TODO delete chrome folder
    # TODO remove all prefs in user.js with " gnomeTheme" or set all false


def extract_release(app, version):
    name = f"{app}-{version}"
    zipfile = DL_CACHE + f"{name}.tar.gz"
    extract_dir = DL_CACHE + f"{name}-extracted/"

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
