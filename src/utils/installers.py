import os
import logging
import shutil
from os.path import join, exists

log = logging.getLogger(__name__)

def firefox_installer(profile_path: str, theme_path: str, theme_color: str="adwaita") -> None:
    """FIREFOX ONLY
    Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """
    # Check paths to ensure they exist
    try:
        if not exists(profile_path):
            raise FileNotFoundError('Install failed. Profile path not found.')

        if not exists(theme_path):
            raise FileNotFoundError('Install failed. Cannot find theme files.')
    except (TypeError, FileNotFoundError) as e:
        log.critical(e)
        raise err.InstallException("Install failed")

    # Make chrome folder if it doesn't already exist
    chrome_path = join(profile_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileNotFoundError:
        log.critical("Install path does not exist. Install canceled.")
        raise err.InstallException('Profile doesn\'t exist.')
    except FileExistsError:
        pass

    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path,
        dst=join(chrome_path, "firefox-gnome-theme"),
        dirs_exist_ok=True
    )

    # Add import lines to CSS files, and creates them if necessary.
    css_files = ["userChrome.css", "userContent.css"]

    for each in css_files:
        p = join(chrome_path, each)
        try:
            with open(file=p, mode="r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        with open(file=p, mode="w", encoding='utf-8') as file:
            # Remove old import lines
            remove_list = []
            for line in lines:
                if "firefox-gnome-theme" in line:
                    lines.remove(line)

            # Add new import lines
            # FIXME inserting like this puts all three imports onto the same line. Doesn't seem to cause issues though.
            if theme_color != "adwaita":
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/light-{theme_color}.css";')
                lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/dark-{theme_color}.css";')
                log.debug('Installing the %s theme', theme_color)
            import_line = f'@import "firefox-gnome-theme/{each}";'
            lines.insert(0, import_line)

            file.writelines(lines)
        log.debug("%s finished", each)

