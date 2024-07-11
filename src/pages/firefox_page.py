# firefox_page.py
# TODO once this is working properly turn this class into a generic parent class and spin off Firefox and Thunderbird Pages into their own subclasses
# TODO make firefox_path and profile_path class properties that can be edited easily

import logging, json, os.path, shutil
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from .firefox_prefs import FIREFOX_OPTIONS
from ..utils.profiles import find_profiles
from ..utils import install
from ..utils import paths
from ..utils import online

log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/addwater-page.ui")
class FirefoxPage(Adw.Bin):
    """Firefox ViewStackPage. Must be converted into a generalized class for both Firefox and Thunderbird"""
    __gtype_name__ = "AddwaterPage"

    # Firefox Attributes

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()
    profile_list = Gtk.Template.Child()



    def __init__(self, firefox_path):
    # GUI and Backend
        super().__init__()
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
        self.settings.delay()
        if firefox_path is None:
            print("FIREFOX_PATH not found")
            pass
            # TODO Show a status page that asks user to set the firefox-path manually and to check Firefox flatpak permissions..
        self.init_prefs(FIREFOX_OPTIONS)

        # Change Confirmation bar
        # TODO Should parameter be None? What does the parameter refer to?
        # TODO Should these be Gio.SimpleAction or install_action?
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

    # Find Firefox Attributes
        self.installed_version = self.settings.get_int("installed-version")
        self.firefox_path = firefox_path
        self.profiles = find_profiles(moz_path=self.firefox_path)
        for each in self.profiles:
            self.profile_list.append(each["name"])

    # Look for updates
        self.update_version = online.check_for_updates(app="firefox")
        if self.update_version > self.installed_version:
            msg = f"Theme updated (v{self.update_version})"
            # TODO set has unapplied to True and ask to install if theme is installed, or automatically install
        else:
            msg = "No update available"

        self.toast_overlay.add_toast(
            Adw.Toast(
                title=msg,
                timeout=2
            )
        )


    def init_prefs(self, OPTIONS_LIST):
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
            group = Adw.PreferencesGroup(title=each["group_name"])

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
        self.settings.set_int("installed-version", self.update_version)
        self.settings.apply()
        selected_profile_name = self.profile_switcher.get_selected_item().get_string()
        for each in self.profiles:
            if each["name"] == selected_profile_name:
                profile_id = each["id"]
                break

        # TODO Turn the install and uninstall into bespoke methods separate from each other
        if self.settings.get_boolean("theme-enabled") is True:
            msg = self.install_theme(profile_id=profile_id)
        else:
            msg = self.uninstall_theme(profile_id=profile_id)

        toast = Adw.Toast(
            title=msg,
            timeout=5,
            priority=Adw.ToastPriority.HIGH
        )
        self.toast_overlay.add_toast(toast)



    def discard_changes(self, one, action, three):
        self.settings.revert()

        # FIXME Toasts don't disappear unless another window is in focus. Why?
        toast = Adw.Toast(
            title="Changes reverted",
            timeout=3,
            priority=Adw.ToastPriority.NORMAL
        )
        self.toast_overlay.add_toast(toast)

    def install_theme(self, profile_id):
        selected_profile_name = self.profile_switcher.get_selected_item().get_string()
        for each in self.profiles:
            if each["name"] == selected_profile_name:
                profile_id = each["id"]
                break

        user_js = os.path.join(self.firefox_path, profile_id, "user.js")
        # Run install script
        install.install_firefox(
            firefox_path=self.firefox_path,
            profile=profile_id,
            version=self.update_version
        )

        # Set all user.js options according to gsettings
        with open(file=user_js, mode="r") as file:
            lines = file.readlines()

        with open(file=user_js, mode="w") as file:
            for group in FIREFOX_OPTIONS:
                for option in group["options"]:
                    js_key = option["js_key"]
                    value = str(self.settings.get_boolean(option["key"])).lower()
                    pref_name = f"gnomeTheme.{js_key}"
                    full_line = f"""user_pref("{pref_name}", {value});\n"""

                    found = False
                    for i in range(len(lines)):
                        if pref_name in lines[i]:
                            lines[i] = full_line
                            found = True
                            break
                    if found == False:
                        lines.append(full_line)

            file.writelines(lines)

        log.info("Theme installed successfully.")
        return "Firefox theme installed. Restart Firefox to see changes."

    def uninstall_theme(self, profile_id):
        # Delete Chrome folder
        chrome_path = os.path.join(self.firefox_path, profile_id, "chrome")
        shutil.rmtree(chrome_path)

        # Set all user_prefs to false
        user_js = os.path.join(self.firefox_path, profile_id, "user.js")
        try:
            with open(file=user_js, mode="r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            pass

        with open(file=user_js, mode="w") as file:
            # TODO Cleaner way to do this? A basic for each doesn't let you replace the item in the list
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")
        return "Firefox theme uninstalled. Restart Firefox to see changes."

