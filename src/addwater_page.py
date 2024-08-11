# addwater_page.py
#
# Copyright 2024 Qwery
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

# TODO make app_path a class property that can be edited easily
# FIXME If the app updates but the user doesn't install it, then the theme update is downloaded in full repeatedly until user manually installs it


import logging, json, os.path, shutil, requests
from configparser import ConfigParser
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from .utils import install, paths
from .theme_options import FIREFOX_COLORS

log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    __gtype_name__ = "AddWaterPage"

    # Class Attributes
    # Version of theme installed and what will be updated
    installed_version = None
    update_version = None

    app_name = None     # Proper, capitalized name of the app, 'Firefox' or 'Thunderbird'
    app_options = None      # Theme features that user can enable in GUI
    app_path = None     # Path to where app stores its profile folders and profiles.ini file
    theme_url = None        # URL to GitHub theme to download and poll for updates

    colors = None       # User's chosen color theme
    selected_profile = None        # User's chosen profile to install theme to


    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()
    profile_list = Gtk.Template.Child()
    colors_list = Gtk.Template.Child()
    colors_switcher = Gtk.Template.Child()



    def __init__(self, app_path, app_options, app_name, theme_url):
        super().__init__()
        self.app_path = app_path
        self.app_options = app_options
        self.app_name = app_name
        self.theme_url = theme_url

        self.settings = Gio.Settings(schema_id=f"dev.qwery.AddWater.{self.app_name}")
        self.settings.delay()
        self.installed_version = self.settings.get_int("installed-version")

        # Profiles and Colors lists
        self.selected_profile = self.settings.get_string("last-profile")
        self.find_profiles(profile_path=self.app_path)
        self.colors = self.settings.get_string("color-theme")

        self._init_gui(app_options)

        self.profile_switcher.notify("selected-item")
        self.profile_switcher.connect("notify::selected-item", self._set_profile)
        self.colors_switcher.notify("selected-item")
        self.colors_switcher.connect("notify::selected-item", self._set_colors)

        # Change Confirmation bar
        # TODO try using an action group instead
        self.install_action(
            "water.apply-changes",
            None,
            self.apply_changes
        )
        self.install_action(
            "water.discard-changes",
            None,
            self.discard_changes
        )

        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE
        )

        # Check for updates and install if new available and theme is already enabled
        msg = self.check_for_updates()
        if (self.update_version is not None and self.update_version > self.installed_version):
            # FIXME this bypasses applying changes to gsettings
            if self.settings.get_boolean("theme-enabled") == True:
                self.install_theme(
                    profile_id=self.selected_profile,
                    options=self.app_options,
                    version=self.update_version
                )

            msg = f"Updated to v{self.update_version}"

        if msg is not None:
            self.send_toast(msg)


    def _init_gui(self, OPTIONS_LIST):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            OPTIONS_LIST: a json-style list of dictionaries which include all option groups
                and options that the theme supports. Included in theme_options.py
        """
        # TODO consider adding option to move the "New Tab" button for Hide Single Tab
        # App options
        self.settings.bind(
            "theme-enabled",
            self.enable_button,
            "active",
            Gio.SettingsBindFlags.DEFAULT
        )

        # Theme options
        for each in OPTIONS_LIST:
            group = Adw.PreferencesGroup(
                title=each["group_name"],
                margin_start=30,
                margin_end=30
            )

            for option in each["options"]:
                button = Adw.SwitchRow(
                    title=option["summary"],
                    subtitle=option["description"]
                )
                self.settings.bind(
                    option["key"],
                    button,
                    "active",
                    Gio.SettingsBindFlags.DEFAULT
                )
                # Disables theme-specific options if theme isn't enabled.
                self.enable_button.bind_property(
                    "active",
                    button,
                    "sensitive",
                    GObject.BindingFlags.SYNC_CREATE
                )

                group.add(button)
            self.preferences_page.add(group)

        # Colors list
        for each in FIREFOX_COLORS:
            self.colors_list.append(each)
        selected = self.colors.title()
        self.colors_switcher.set_selected(FIREFOX_COLORS.index(selected))

        # Profile list
        last_profile = self.settings.get_string("last-profile")
        for each in self.profiles:
            if each["id"] == last_profile:
                self.profile_switcher.set_selected(self.profiles.index(each))
                break


    def apply_changes(self, _, action, __):
        # TODO Refactor how I use update_version and installed_version so that there's never a disconnect between them that causes unexpected issues
        """Apply changes to GSettings and call the proper install or uninstall method"""

        if self.update_version is None:
            version = self.installed_version
        else:
            version = self.update_version


        profile_id = self.selected_profile
        if self.settings.get_boolean("theme-enabled") is True:
            msg = self.install_theme(
                profile_id=profile_id,
                options=self.app_options,
                version=version
            )
        else:
            msg = self.uninstall_theme(profile_id=profile_id)

        self.send_toast(msg, 3, 1)


    def discard_changes(self, _, action, __):
        """Revert changes made to GSettings and notify user"""
        self.settings.revert()
        self.send_toast("Changes reverted")


        # Reset combo boxes to the original state
        selected = self.settings.get_string("color-theme").title()
        for each in FIREFOX_COLORS:
            if each == selected:
                self.colors_switcher.set_selected(FIREFOX_COLORS.index(each))
                break

        last_profile = self.settings.get_string("last-profile")
        for each in self.profiles:
            if each["id"] == last_profile:
                self.profile_switcher.set_selected(self.profiles.index(each))
                break


    def install_theme(self, profile_id, options, version):
        self.settings.set_int("installed-version", version)
        self.settings.apply()

        profile_path = os.path.join(self.app_path, profile_id)

        # Run install script
        install.install_firefox_theme(
            version=version,
            profile_path=profile_path,
            theme=self.colors
        )

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
        return "Installed Theme. Restart Firefox to see changes."


    def uninstall_theme(self, profile_id):
        log.info(f"Removing theme from {profile_id}...")
        print(f"Removing theme from {profile_id}...")
        # Delete Chrome folder
        try:
            chrome_path = os.path.join(self.app_path, profile_id, "chrome", "firefox-gnome-theme")
            shutil.rmtree(chrome_path)
        except FileNotFoundError:
            pass

        # TODO remove css import lines

        # Set all user_prefs to false
        user_js = os.path.join(self.app_path, profile_id, "user.js")
        try:
            with open(file=user_js, mode="r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return "Removed Theme. Restart Firefox to see changes."

        with open(file=user_js, mode="w") as file:
            # This is easier than a foreach
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")
        return "Removed Theme. Restart Firefox to see changes."


    def check_for_updates(self):
        # TODO is there a way to check the Firefox version first? If so, check that first and if newer only then check Github once every day
        """Check theme github for new releases


        Returns:
            None = No new release to update to
            Int = Next release version to update to
        """

        DL_CACHE = paths.DOWNLOAD_DIR
        check_url = self.theme_url
        try:
            r = requests.get((check_url))
            log.debug(f'Remaining Github API calls for the next hour: {r.headers["x-ratelimit-remaining"]}')
            # TODO set this to be more strict when releasing for Flathub
            if int(r.headers["x-ratelimit-remaining"]) < 10:
                raise ResourceWarning
            latest_release = r.json()[0]

        except requests.RequestException as err:
            log.error(f"Update request failed: {err}")
            msg = "Update failed. Please try again later."
            self.update_version = None
            return msg
        except ResourceWarning as err:
            # Deliberately limiting below the actual limit. There's no reason to poll Github so often.
            log.error(f"Limiting polling in order to not overstep Github API rate limits")
            print(f"Limiting polling in order to not overstep Github API rate limits")
            self.update_version = None
            msg = "To avoid rate limits, please try again later"
            return msg

        self.update_version = int(latest_release["tag_name"].lstrip("v"))

        if self.update_version > self.installed_version:
            self.download_release(
                tarball_url=latest_release["tarball_url"],
                version=self.update_version
            )
        else:
            log.info("No update available.")


    # TODO how to make download asynchronous? Is that even worthwhile?
    def download_release(self, tarball_url, version):
        DL_CACHE = paths.DOWNLOAD_DIR
        log.info(f"Update available ({self.installed_version} → {self.update_version}). Downloading now...")
        response = requests.get(tarball_url) # ASYNC use stream flag
        if response.status_code != 200:
            log.error(f"Github download request gave bad response [{response.status_code}]")

        p = os.path.join(DL_CACHE, f"{self.app_name}-{version}.tar.gz")
        with open(file=p, mode="wb") as file:
            file.write(response.content)

        log.info("Github download SUCCESS!")


    def find_profiles(self, profile_path):
        """Reads the app configuration files and returns a list of profiles. The user's preferred profiles are first in the list.

        Args:
        profile_path : The path to where the app stores its profiles and the profiles.ini files

        Returns:
        A list of dicts with all profiles. Each dict includes the full ID of the profile, and a display name to present in the UI without the randomized prefix string.
        The first in the list is always the user's selected default profile.

        """
        install_file = os.path.join(profile_path, "installs.ini")
        profiles_file = os.path.join(profile_path, "profiles.ini")

        cfg = ConfigParser()
        defaults = []
        profiles = []

        try:
            # Find Preferred profile
            if len(cfg.read(install_file)) == 0:
                raise FileNotFoundError(install_file)

            for each in cfg.sections():
                default_profile = cfg[each]["Default"]
                defaults.append(default_profile)
                profiles.append({"id" : default_profile,
                                "name" : default_profile.partition(".")[2] + " (Preferred)"})
                log.debug(f"User's default profile is {default_profile}")

            # Find all others
            if len(cfg.read(profiles_file)) == 0:
                raise FileNotFoundError(profiles_file)

            for each in cfg.sections():
                try:
                    s = cfg[each]["path"]
                    if s not in defaults:
                        profiles.append({"id" : s,
                                        "name" : s.partition(".")[2]})
                except KeyError:
                    pass
        except FileNotFoundError as err:
            log.error(f"Reading INI failed: {err}")
            return

        # NOTE: The user's preferred profile must always be the first option in the list
        self.profiles = profiles
        for each in self.profiles:
            self.profile_list.append(each["name"])


    def _set_profile(self, row, _=None):
        profile_display_name = row.get_selected_item().get_string()
        for each in self.profiles:
            if each["name"] == profile_display_name:
                self.selected_profile = each["id"]
                log.debug(f'set profile to {each["id"]}')
                break

        # This compare check avoids triggering "has-unapplied" at app launch
        if self.selected_profile != self.settings.get_string("last-profile"):
            self.settings.set_string("last-profile", self.selected_profile)


    def _set_colors(self, row, _):
        self.colors = row.get_selected_item().get_string().lower()

        # This compare check avoids triggering "has-unapplied" at app launch
        if self.colors != self.settings.get_string("color-theme"):
            self.settings.set_string("color-theme", self.colors)


    def send_toast(self, msg, time=2, priority=0):
        # Workaround for libadwaita bug which cause toasts not to disappear automatically
        self.toast_overlay.add_toast(
            Adw.Toast(
                title=msg,
                timeout=time,
                priority=priority
            )
        )
        self.enable_button.grab_focus()


    def full_uninstall(self, *args):
        # TODO is there a cleaner way to implement this with signals/actions?
        print(f"Removing theme from all profiles in path [{self.app_path}]")
        log.info(f"Removing theme from all profiles in path [{self.app_path}]")
        for each in self.profiles:
            self.uninstall_theme(profile_id=each["id"])

