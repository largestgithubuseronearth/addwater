# firefox_page.py

from gi.repository import Gtk, Adw, Gio


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"

    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    def __init__(self):
        print("firefox")
        # TODO read gsettings and set all preferences accordingly and store that state
        # self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")

    def add_change(self, change):
        pass

    def remove_change(self, change):
        pass

    def apply_changes(self):
        pass
