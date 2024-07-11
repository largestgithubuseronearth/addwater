# DO NOT RUN UNTIL TESTED
import os, shutil


def install_firefox_theme(theme_path, install_path, theme):
    """Replaces the included theme installer
    ARGS
    theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
    install_path = path to the profile folder in which the theme will be installed.
    theme = user selected color theme
    """

    # Go into firefox_path/profile_path
        # Check that this path actually exists

    # Make chrome folder if it doesn't already exist
    chrome_path = os.path.join(install_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileExistsError:
        pass
    except FileNotFoundError:
        LOG ERROR
        return False


    # Copy theme repo into chrome folder
    shutil.copytree(theme_path, install_path)

    # Create userChrome.css file inside install_path if non-existant or empty

        # Remove older theme imports
        # Add single line "@import firefox-gnome-theme/userChrome.css"
        line = """@import "firefox-gnome-theme/userChrome.css";"""



