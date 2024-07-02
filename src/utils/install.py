# theme_actions.py
# TODO make sure these commands work regardless of shell user has

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

    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith("rafaelmardojai-firefox-gnome-theme"):
                p = each.name
    script_path = os.path.join(extract_dir, p, "scripts", "install.sh")

    # Preview of the final command
    try:
        print(script_path, profile_arg, profile, "-f", firefox_path)
        subprocess.run([script_path, profile_arg, profile, "-f", firefox_path],
                        capture_output=True,
                        check=True)
    except CalledProcessError as err:
        print("Install Firefox Failed")
        log.critical(f"Install CMD failed ;; Return={err.returncode} ;; Full command: {err.args}")
        return False

    log.info(f"Installed Firefox successfully.")
    print(f"Installed Firefox successfully.")
    return True

def uninstall_firefox_theme(firefox_path, profile):
    pass
    # TODO delete chrome folder
    # TODO remove all prefs in user.js with " gnomeTheme" or set all false


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
