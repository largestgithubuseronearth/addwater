# addwater_page.py
# TODO once this is working properly turn this class into a generic parent class and spin off Firefox and Thunderbird Pages into their own subclasses
# TODO make app_path and profile_path class properties that can be edited easily
# TODO make selected profile a class property that methods can use immediately
# TODO refactor entire app to work even without internet

import logging, json, os.path, shutil, requests
from configparser import ConfigParser
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from .utils import install, paths

log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    """ ViewStackPage"""
    __gtype_name__ = "AddWaterPage"

    update_version = None

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()
    profile_list = Gtk.Template.Child()



    def __init__(self, app_path, app_options, app_name, theme_url):
        self.app_path = app_path
        self.app_options = app_options
        self.app_name = app_name
        self.theme_url = theme_url
        self.profile = None

    # GUI and Backend
        super().__init__()
        self.settings = Gio.Settings(schema_id=f"dev.qwery.AddWater.{self.app_name}")
        self.settings.delay()
        self._init_prefs(app_options)

        # Change Confirmation bar
        # TODO make sure this doesn't cause issues. If it does, then add an ActionGroup to this class or just workaround actions altogether and connect the signal directly
        self.install_action(
            "water.apply-changes",
            # TODO is this legal?
            self.update_version,
            self.apply_changes
        )
        self.install_action(
            "water.discard-changes",
            None,
            self.discard_changes
        )
        self.install_action(
            "water.reset",
            None,
            self.reset_app
        )

        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE
        )
        self.profile_switcher.connect(
            # FIXME what is the correct signal name?
            "activate",
            self.set_profile
        )

    # Find Firefox Attributes
        self.installed_version = self.settings.get_int("installed-version")
        self.find_profiles(profile_path=self.app_path)

    # Look for updates
        msg = self.check_for_updates()
        if self.update_version is not None and self.update_version > self.installed_version:
            if self.settings.get_bool("theme-enabled") == True:
                selected_profile_name = self.profile_switcher.get_selected_item().get_string()
                for each in self.profiles:
                    if each["name"] == selected_profile_name:
                        profile_id = each["id"]
                        break

                self.install_theme(
                    profile_id=profile_id,
                    OPTIONS=self.app_options
                )

            msg = f"Updated to v{self.update_version}"

        self.toast_overlay.add_toast(
            Adw.Toast(
                title=msg,
                timeout=2
            )
        )


    def _init_prefs(self, OPTIONS_LIST):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            OPTIONS_LIST: a json-style list of dictionaries which include all option groups
                and options that the theme supports.
        """
        # TODO When a button is switched from its previous position, add a dot next to the switch to show it's been changed. Set all to hidden when settings are applied.
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
                    tooltip_text=option["description"]
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



    def apply_changes(self, one, action, three):
        if self.update_version is None:
            version = self.installed_version
        else:
            version = self.update_version
        self.settings.set_int("installed-version", version)
        self.settings.apply()
        selected_profile_name = self.profile_switcher.get_selected_item().get_string()
        for each in self.profiles:
            if each["name"] == selected_profile_name:
                profile_id = each["id"]
                break

        # TODO Turn the install and uninstall into bespoke methods separate from each other
        if self.settings.get_boolean("theme-enabled") is True:
            msg = self.install_theme(
                profile_id=profile_id,
                options=self.app_options,
                version=version
            )
        else:
            msg = self.uninstall_theme(profile_id=profile_id)

        toast = Adw.Toast(
            title=msg,
            timeout=5,
            priority=Adw.ToastPriority.HIGH
        )
        self.toast_overlay.add_toast(toast)



    def discard_changes(self, one, action, three):
        """Revert changes made to GSettings and notify user"""
        self.settings.revert()

        # FIXME Toasts don't disappear unless another window is in focus. Why?
        toast = Adw.Toast(
            title="Changes reverted",
            timeout=3,
            priority=Adw.ToastPriority.NORMAL
        )
        self.toast_overlay.add_toast(toast)


    def install_theme(self, profile_id, options, version):
        profile_path = os.path.join(self.app_path, profile_id)

        theme_path = install.extract_release(
            app=self.app_name,
            version=version
        )
        # Run install script
        install.install_firefox_theme(
            theme_path=theme_path,
            profile_path=profile_path,
            theme="adwaita"
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
                    # TODO Cleaner way to do this? A basic for each doesn't let you replace the item in the list
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
        # Delete Chrome folder
        try:
            chrome_path = os.path.join(self.app_path, profile_id, "chrome")
            shutil.rmtree(chrome_path)
        except FileNotFoundError:
            pass

        # Set all user_prefs to false
        user_js = os.path.join(self.app_path, profile_id, "user.js")
        try:
            with open(file=user_js, mode="r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return "Removed Theme. Restart Firefox to see changes."

        with open(file=user_js, mode="w") as file:
            # TODO Cleaner way to do this? A basic for each doesn't let you replace the item in the list
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")
        return "Removed Theme. Restart Firefox to see changes."


    def check_for_updates(self):
        """Check theme github for new releases


        Returns:
            None = No new release to update to
            Int = Next release version to update to
        """

        DL_CACHE = paths.DOWNLOAD_DIR
        check_url = self.theme_url
        try:
            latest_release = requests.get((check_url)).json()[0]
        except requests.RequestException as err:
            log.error(f"Update request failed: {err}")
            msg = "Update failed. Please try again later."
            self.update_version = None
            return msg
        except KeyError as err:
        # TODO make this more robust and reliable
            log.error(f"Likely exceeded Github rate limit: {err}")
            self.update_version = None
            msg = "Update failed. Please try again later."
            return msg
            # TODO add checks to ensure this doesn't exceed GitHub API limit and add error logs



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
        """Reads the app configuration files to adds all of them in a list.

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
            # Preferred
            if len(cfg.read(install_file)) == 0:
                raise FileNotFoundError(install_file)

            for each in cfg.sections():
                default_profile = cfg[each]["Default"]
                defaults.append(default_profile)
                profiles.append({"id" : default_profile,
                                "name" : default_profile.partition(".")[2] + " (Preferred)"})
                log.debug(f"User's default profile is {default_profile}")

            # All
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


    def reset_app(self):
    # TODO Uninstall theme from all profiles and move the backup file back to user.js.
        print("reset action activated")

    # TODO reset all GSettings values

    # TODO delete everything in APP_CACHE
        pass

    def set_profile(self, arg):
        print(arg)
        print(type(arg))
        print("set profile activated")
        self.profile = self.profile_switcher.get_selected_item().get_string()
        print(self.profile)

