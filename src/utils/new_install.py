# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# DO NOT RUN UNTIL TESTED
# TODO add logs

# TODO add theme install
# @import "firefox-gnome-theme/theme/colors/light-maia.css";
# @import "firefox-gnome-theme/theme/colors/dark-maia.css";
import os, shutil


def install_firefox_theme(theme_path, install_path, theme):
    """Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        install_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """

    # Check paths to ensure they exist
        if !os.path.exists(install_path):
            print("install_path not found. Install canceled.")
            return
        if !os.path.exists(theme_path):
            print("theme_path not found. Install canceled.")
            return

    # Make chrome folder if it doesn't already exist
    chrome_path = os.path.join(install_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileExistsError:
        print("Chrome exists.")
        pass
    except FileNotFoundError:
        print("Install path does not exist. Install canceled.")
        return False


    # Copy theme repo into chrome folder
    shutil.copytree(theme_path, install_path)

    # Create userChrome.css file inside install_path if non-existant or empty
    files = [
        "userChrome.css",
        "userContent.css"
    ]
    for file in files:
        p = os.path.join(chrome_path, file)
        try:
            with open(file=p, mode="r") as file:
                lines = file.readlines()
                print(f"Found {file}.")
        except FileNotFoundError:
                lines = []
                print(f"Creating {file}.")
        finally:
            import_line = f"""@import "firefox-gnome-theme/{file};"""
            with open(file=p, mode="w") as file:
                for line in lines:
                    if "firefox-gnome-theme" in line:
                        lines.del(line)
                        print("found line deleted")

                lines.insert(0, import_line)
                file.writelines(lines)

        print("install finished :)")
