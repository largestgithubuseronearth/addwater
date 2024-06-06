# firefox_page.py

from gi.repository import Gtk, Adw, Gio, GLib


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"

    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    def __init__(self):
        print("firefox")
        # TODO read gsettings and set all preferences accordingly and store that state
        # TODO Read profiles ini and list all profiles

    def add_change(self, change):
        pass

    def remove_change(self, change):
        pass

    def apply_changes(self):
        pass
