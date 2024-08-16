

import logging, json, os.path, shutil, requests
from typing import Optional
from gi.repository import Gio, GLib, GObject
from configparser import ConfigParser
from .utils import install, paths
from .utils import exceptions as err
from .theme_options import FIREFOX_COLORS

import logging

log = logging.getLogger(__name__)

class AddWaterBackend(object):

    def __init__(self, app_path, app_options, theme_url):
        print("Backend is alive!")

        # TODO make this compatible for both apps later
        self.settings = Gio.Settings(schema_id='dev.qwery.AddWater.Firefox')
        self.app_path = app_path
        self.app_options = app_options
        self.theme_url = theme_url


    # TODO make this private, rename it, and make a separate "get_profiles" method to give the profile list to the frontend
    def get_profiles(self):
        """BACK: Reads the app configuration files and returns a list of profiles. The user's preferred profiles are first in the list.

        Args:
        app_path : The full path to where the app stores its profiles and the profiles.ini files

        Returns:
        A list of dicts with all profiles. Each dict includes the full ID path of the profile ["id"], and a display name to present in the UI ["name"].
        """
        app_path = self.app_path

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
        """Check theme github for new releases"""
        print("updates!")
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
        print(update_version)

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
            print("No update available.")
            return update_version


    # TODO how to make download asynchronous? Is that even worthwhile?
    # TODO Move this to outside the class?
    # TODO move extraction step here
    # TODO delete old versions and make them all the same name
    def download_release(self, tarball_url: str, version: int):
        log.info(f"Update available (v{version}). Downloading now...")

        DL_CACHE = paths.DOWNLOAD_DIR
        try:
            response = requests.get(tarball_url) # ASYNC use stream flag
        except requests.RequestException as e:
            log.error(f"Github download failed [{e}]")
            raise err.NetworkException('Download failed.')

        # TODO delete previous downloads

        # TODO make this compat w both apps
        p = os.path.join(DL_CACHE, f"Firefox-{version}.tar.gz")
        with open(file=p, mode="wb") as file:
            file.write(response.content)

        log.info("Github download SUCCESS!")



    # TODO type these args
    def install_theme(self, profile_path: str, options, version: int, colors: str):
        """BACK: Setup install method and set userjs preferences"""
        if not os.path.exists(profile_path):
            raise err.FatalPageException('Install failed. Profile doesn\'t exist.')

        self.settings.set_int("installed-version", version)
        self.settings.apply()

        # Run install script
        try:
            install.install_firefox_theme(
                version=version,
                profile_path=profile_path,
                theme=colors
            )
        except err.InstallException as e:
            print(e)

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




    def uninstall_theme(self, profile_path):
        self.settings.apply()

        # Delete Chrome folder
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
            return

        with open(file=user_js, mode="w") as file:
            # This is easier than a foreach
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")

