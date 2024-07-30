# theme_actions.py
# TODO move 'extract tarball' step into 'download theme release' step

import os, shutil
import os.path
import tarfile

from gi.repository import Gio
from . import paths
from .logs import logging

log = logging.getLogger(__name__)

DL_CACHE = paths.DOWNLOAD_DIR

def install_firefox_theme(theme_path, profile_path, theme):
    # TODO ensure complete functional parity with install script
    """Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """

    # Check paths to ensure they exist
    if os.path.exists(profile_path) is False:
        log.error("profile_path not found. Install canceled.")
        return
    if os.path.exists(theme_path) is False:
        log.error("theme_path not found. Install canceled.")
        return

    # Make chrome folder if it doesn't already exist
    chrome_path = os.path.join(profile_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileExistsError:
        log.info("Chrome exists.")
        pass
    except FileNotFoundError:
        log.critical("Install path does not exist. Install canceled.")
        return False


    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path,
        dst=os.path.join(chrome_path, "firefox-gnome-theme"),
        dirs_exist_ok=True
    )

    # Add import lines to CSS files, and creates them if necessary.
    css_files = [
        "userChrome.css",
        "userContent.css"
    ]

    for each in css_files:
        p = os.path.join(chrome_path, each)
        try:
            with open(file=p, mode="r") as file:
                lines = file.readlines()
                log.info(f"Found {each}.")
        except FileNotFoundError:
                lines = []
                log.info(f"Creating {each}.")

        with open(file=p, mode="w") as file:
            # Remove old import lines
            remove_list = []
            for line in lines:
                if "firefox-gnome-theme" in line:
                    lines.remove(line)
            log.info("Removed prior import lines")

            # Add new import lines
            import_line = f'@import "firefox-gnome-theme/{each}";'
            if theme != "adwaita":
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/light-{theme}.css";')
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/dark-{theme}.css";')
                log.info(f"Installing the {theme} theme")
            lines.insert(0, import_line)

            file.writelines(lines)
            log.info(f"{each} finished")


    # Backup user.js and replace with provided version that includes the prerequisite prefs
    # TODO do i want to automatically import the user's user.js preferences? Must avoid rewriting prefs on subsequent reinstalls
    user_js = os.path.join(profile_path, "user.js")
    user_js_backup = os.path.join(profile_path, "user.js.bak")
    if os.path.exists(user_js) is True and os.path.exists(user_js_backup) is False:
        os.rename(user_js, user_js_backup)

    template = os.path.join(chrome_path, "firefox-gnome-theme", "configuration", "user.js")
    shutil.copy(template, profile_path)

    log.info("Install successful")


def extract_release(app, version):
    # TODO refactor to be cleaner
    name = f"{app}-{version}"
    zipfile = os.path.join(DL_CACHE, f"{name}.tar.gz")
    extract_dir = os.path.join(DL_CACHE, f"{name}-extracted/")

    if os.path.exists(extract_dir):
        log.info(f"{name} already extracted. Skipping.")
        return os.path.join(extract_dir, "firefox-gnome-theme")

    if not os.path.exists(zipfile):
        log.error(f"Release zip doesn't exist: {zipfile}")
        return None

    with tarfile.open(zipfile) as tar:
        tar.extractall(path=extract_dir,
                        filter="data")

    # Must rename the inner folder to "firefox-gnome-theme" for the provided script to work. Otherwise the theme won't show properly
    with os.scandir(path=extract_dir) as scan:
        for each in scan:
            if each.name.startswith("rafaelmardojai-firefox-gnome-theme"):
                old = os.path.join(extract_dir, each.name)
                new = os.path.join(extract_dir, "firefox-gnome-theme")
                os.rename(old, new)
    print("new: ", new)
    log.info(f"{name} tarball extracted successfully.")
    return new


