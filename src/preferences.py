#preferences.py



from gi.repository import Adw, Gtk, Gio, GLib

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"

    custom_firefox_path = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")

        firefox_path = self.settings.get_string("firefox-path")

        # TODO Make set_custom_firefox_path handler

