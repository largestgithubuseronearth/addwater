# theme_actions.py
# TODO make sure these commands work regardless of shell user has

import subprocess
import os
import os.path
import tarfile

from . import paths
from .logs import logging

log = logging.getLogger(__name__)

DL_CACHE = paths.APP_CACHE

def install_firefox(firefox_path, profile, version):
    if not extract_release(app="firefox", version=version):
        log.error("Installation cancelled")
        return False

    profile_arg = "-p"
    if profile is None:
        profile_arg = ""
        profile = ""

    # TODO MAKE SURE THIS COMMAND IS 100% SAFE BEFORE RUNNING
    # script_path = DL_CACHE + "extracted/" + "scripts/" + "install.sh"
    # print("weed: ", script_path)
    # print(f"./{script_path} {profile_arg} {profile} -f {firefox_path}")
    # r = subprocess.run(["." + script_path, profile_arg, profile, -f, firefox_path],
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
        return True

    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        return False

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir,
                        filter="data")

    log.info(f"{name} tarball extracted successfully.")
    return True
