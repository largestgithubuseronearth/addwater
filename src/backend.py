

import logging, json, os, os.path, shutil, requests, tarfile
from typing import Optional
from gi.repository import Gio, GLib, GObject
from configparser import ConfigParser
from .utils.paths import DOWNLOAD_DIR
from .utils import unzip
from .utils import exceptions as err
from .theme_options import FIREFOX_COLORS
import logging

log = logging.getLogger(__name__)

class AddWaterBackend(object):
    def __init__(self, app_name: str, app_path: str, app_options, theme_url: str,):
        print("Backend is alive!")

        # TODO make this compatible for both apps later
        self.settings = Gio.Settings(schema_id=f'dev.qwery.AddWater.{app_name}')
        self.app_path = app_path
        self.app_options = app_options
        self.theme_url = theme_url

        try:
            self.profile_list = self._find_profiles(self.app_path)
        except FileNotFoundError as e:
            log.critical(e)
            raise err.FatalPageException(e)

    def get_profiles(self):
        return self.profile_list


    def _find_profiles(self, app_path: str):
        """BACK: Reads the app configuration files and returns a list of profiles. The user's preferred profiles are first in the list.

        Args:
        app_path : The full path to where the app stores its profiles and the profiles.ini files

        Returns:
        A list of dicts with all profiles. Each dict includes the full ID path of the profile ["id"], and a display name to present in the UI ["name"].
        """
        cfg = ConfigParser()
        defaults = []
        profiles = []

        install_file = os.path.join(app_path, "installs.ini")
        profiles_file = os.path.join(app_path, "profiles.ini")

        # Find preferred profile first so it's always at top of list
        if len(cfg.read(install_file)) == 0:
            raise FileNotFoundError('Reading installs.ini failed. File doesn\'t exist.')
        for each in cfg.sections():
            default_profile = cfg[each]["Default"]
            defaults.append(default_profile)
            profiles.append({"id" : default_profile,
                            "name" : default_profile.partition(".")[2] + " (Preferred)"})
            log.debug(f"User's default profile is {default_profile}")

        # Find all others
        if len(cfg.read(profiles_file)) == 0:
            raise FileNotFoundError('Reading profiles.ini failed. File doesn\'t exist.')
        for each in cfg.sections():
            try:
                s = cfg[each]["path"]
                if s not in defaults:
                    profiles.append({"id" : s,
                                    "name" : s.partition(".")[2]})
            except KeyError:
                pass

        return profiles


    def get_updates(self, URL: str, installed_version: int) -> Optional[int]:
        # TODO is there a way to check the Firefox version first? If so, check that first and if newer only then check Github once every day
        # TODO Set API limit more strict before flathub release
        # TODO consider making this consider special cases like rollbacks or partial updates
        """Check theme github for new releases"""
        try:
            # TODO make sure this request is complaint with github's specification
            response = requests.get((URL))
        except requests.RequestException as e:
            log.error(f"Update request failed: {e}")
            raise err.NetworkException('Unable to check for an update due to a network issue')

        api_calls_left = int(response.headers["x-ratelimit-remaining"])
        log.debug(f'Remaining Github API calls for the next hour: {api_calls_left}')
        print("Github calls left:", api_calls_left)
        if api_calls_left < 10:
            log.error("Limiting polling in order to not overstep Github API rate limits")
            print("Limiting polling so to not overstep Github API rate limits")
            raise err.NetworkException('Unable to check for updates. Please try again later.')

        latest_release = response.json()[0]

        update_version = int(latest_release["tag_name"].lstrip("v"))

        if update_version > installed_version:
            try:
                self.download_release(
                    tarball_url=latest_release["tarball_url"],
                    version=update_version
                )
            except err.NetworkException as e:
                raise err.NetworkException(e)

            return update_version
        else:
            log.info("No update available.")
            return update_version


    # TODO how to make download asynchronous? Is that even worthwhile?
    # TODO Move this to outside the class?
    # TODO move extraction step here
    # TODO delete old versions and make them all the same name
    def download_release(self, tarball_url: str, version: int):
        log.info(f"Update available (v{version}). Downloading now...")

        try:
            response = requests.get(tarball_url) # TODO use stream flag
        except requests.RequestException as e:
            log.error(f"Github download failed [{e}]")
            raise err.NetworkException('Download failed.')

        # TODO delete previous downloads

        # TODO make this compat w both apps
        p = os.path.join(DOWNLOAD_DIR, f"firefox-{version}.tar.gz")
        with open(file=p, mode="wb") as file:
            file.write(response.content)

        log.info("Github download SUCCESS!")


    # TODO type these args
    # TODO break this into two install paths: full (install + prefs) and quick/background (install)
    def full_install(self, profile_path: str, options, version: int, colors: str):
        """BACK: Setup install method and set userjs preferences"""
        if not os.path.exists(profile_path):
            raise err.FatalPageException('Install failed. Profile doesn\'t exist.')

        self.settings.set_int("installed-version", version)

        # Run install script
        try:
            self._install_theme_files(
                version=version,
                profile_path=profile_path,
                theme=colors
            )
            self._set_theme_prefs(profile_path, options)
        except err.InstallException as e:
            print(e)


    def _set_theme_prefs(self, profile_path: str, options) -> None:
        # Set all user.js options according to gsettings
        user_js = os.path.join(profile_path, "user.js")
        with open(file=user_js, mode="r") as file:
            lines = file.readlines()

        with open(file=user_js, mode="w") as file:
            for group in options:
                for option in group["options"]:
                    js_key = option["js_key"]
                    value = str(self.settings.get_boolean(option["key"])).lower()
                    pref_name = f"gnomeTheme.{js_key}"
                    full_line = f"""user_pref("{pref_name}", {value});\n"""

                    found = False
                    for i in range(len(lines)):
                        # This is easier than a for-each
                        if pref_name in lines[i]:
                            lines[i] = full_line
                            found = True
                            break
                    if found == False:
                        lines.append(full_line)

            file.writelines(lines)

        log.info("Theme installed successfully.")




    def _install_theme_files(self, version: int, profile_path: str, theme: str="adwaita") -> None:
        # FIREFOX ONLY
        # TODO ensure complete functional parity with install script
        """Replaces the included theme installer

        Arguments:
            theme_path = path to the extracted theme folder. Likely inside `[app_path]/cache/add-water/downloads/`
            profile_path = path to the profile folder in which the theme will be installed.
            theme = user selected color theme
        """
        # Check paths to ensure they exist
        try:
            if not os.path.exists(profile_path):
                raise FileNotFoundError('Install failed. Profile path not found.')

            # TODO move 'extract tarball' step into 'download theme release' step
            theme_path = unzip.extract_theme_release(appname="Firefox", version=version)
            if not os.path.exists(theme_path):
                raise FileNotFoundError('Install failed. Cannot find theme files.')
        except (TypeError, FileNotFoundError) as e:
            log.critical(e)
            # FIXME error here occurs when handling the error. Passing e to raise is illegal?
            raise err.InstallException("Install failed")

        # Make chrome folder if it doesn't already exist
        chrome_path = os.path.join(profile_path, "chrome")
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
            dst=os.path.join(chrome_path, "firefox-gnome-theme"),
            dirs_exist_ok=True
        )

        # Add import lines to CSS files, and creates them if necessary.
        css_files = ["userChrome.css", "userContent.css"]

        for each in css_files:
            p = os.path.join(chrome_path, each)
            try:
                with open(file=p, mode="r") as file:
                    lines = file.readlines()
            except FileNotFoundError:
                    lines = []

            with open(file=p, mode="w") as file:
                # Remove old import lines
                remove_list = []
                for line in lines:
                    if "firefox-gnome-theme" in line:
                        lines.remove(line)

                # Add new import lines
                # FIXME inserting like this puts all three imports onto the same line. Doesn't seem to cause issues though.
                if theme != "adwaita":
                    lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/light-{theme}.css";')
                    lines.insert(0, f'@import "firefox-gnome-theme/theme/colors/dark-{theme}.css";')
                    log.debug(f"Installing the {theme} theme")
                import_line = f'@import "firefox-gnome-theme/{each}";'
                lines.insert(0, import_line)

                file.writelines(lines)
            log.debug(f"{each} finished")

        # Backup user.js and replace with provided version that includes the prerequisite prefs
        user_js = os.path.join(profile_path, "user.js")
        user_js_backup = os.path.join(profile_path, "user.js.bak")
        if os.path.exists(user_js) is True and os.path.exists(user_js_backup) is False:
            os.rename(user_js, user_js_backup)

        template = os.path.join(chrome_path, "firefox-gnome-theme", "configuration", "user.js")
        shutil.copy(template, profile_path)

        log.info("Install successful")


    def uninstall_theme(self, profile_path):
        # Delete theme folder
        try:
            chrome_path = os.path.join(profile_path, "chrome", "firefox-gnome-theme")
            shutil.rmtree(chrome_path)
        except FileNotFoundError:
            pass

        # TODO remove css import lines

        # Set all user_prefs to false
        user_js = os.path.join(profile_path, "user.js")
        try:
            with open(file=user_js, mode="r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            log.info("Theme uninstalled successfully.")
            return

        with open(file=user_js, mode="w") as file:
            # This is easier than a foreach
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")


    def full_uninstall(self):
        # TODO is there a cleaner way to implement this with signals/actions?
        print(f"Removing theme from all profiles in path [{self.app_path}]")
        log.info(f"Removing theme from all profiles in path [{self.app_path}]")
        for each in self.profile_list:
            profile_path = os.path.join(self.app_path, each["id"])
            self.uninstall_theme(profile_path=profile_path)
