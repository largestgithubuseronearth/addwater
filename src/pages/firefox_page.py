# firefox_page.py

from gi.repository import Gtk, Adw, Gio, GLib

from ..utils.profiles import find_profiles


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"

    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    profile_list = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()

    def __init__(self):
        print("firefox")
        # TODO read gsettings and set all preferences accordingly. Store this info in a dict.
        self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

        self.profiles = find_profiles(moz_path=(GLib.get_user_data_dir() + "/temp/"))
        for each in self.profiles:
            self.profile_list.append(each["name"])


    def add_change(self, change):
        pass

    def remove_change(self, change):
        pass

    def apply_changes(self):
        pass
