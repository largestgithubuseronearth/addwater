# TODO add logs

# TODO add theme install
# @import "firefox-gnome-theme/theme/colors/light-maia.css";
# @import "firefox-gnome-theme/theme/colors/dark-maia.css";
import os, shutil


def install_firefox_theme(theme_path, profile_path, theme):
    """Replaces the included theme installer

    Arguments:
        theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
        profile_path = path to the profile folder in which the theme will be installed.
        theme = user selected color theme
    """

    # Check paths to ensure they exist
    if os.path.exists(profile_path) is False:
        print("profile_path not found. Install canceled.")
        return
    if os.path.exists(theme_path) is False:
        print("theme_path not found. Install canceled.")
        return

    # Make chrome folder if it doesn't already exist
    chrome_path = os.path.join(profile_path, "chrome")
    try:
        os.mkdir(chrome_path)
    except FileExistsError:
        print("Chrome exists.")
        pass
    except FileNotFoundError:
        print("Install path does not exist. Install canceled.")
        return False


    # Copy theme repo into chrome folder
    shutil.copytree(
        src=theme_path,
        dst=os.path.join(chrome_path, "firefox-gnome-theme"),
        dirs_exist_ok=True
    )

    # Create userChrome.css file inside profile_path if non-existant or empty
    css_files = [
        "userChrome.css",
        "userContent.css"
    ]
    for each in css_files:
        p = os.path.join(chrome_path, each)
        try:
            with open(file=p, mode="r") as file:
                lines = file.readlines()
                print(f"Found {each}.")
        except FileNotFoundError:
                lines = []
                print(f"Creating {each}.")
        finally:
            with open(file=p, mode="w") as file:
                print("lines: ", lines)
                for i in range(len(lines)):
                    if "firefox-gnome-theme" in lines[i]:
                        del lines[i]
                        print("found line deleted")

                import_line = f"""@import "firefox-gnome-theme/{each};"""
                lines.insert(0, import_line)
                file.writelines(lines)
            print(f"{each} finished")

    print("install finished :)")
