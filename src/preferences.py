#preferences.py
# TODO make pref window close on Ctrl+W and allow close app with Ctrl+Q
# TODO add option to show experimental unstable features
# FIXME [Widget of type “AddWaterPreferences” already has an accessible role of type “GTK_ACCESSIBLE_ROLE_GENERIC”]



from gi.repository import Adw, Gtk, Gio, GLib

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"

    custom_firefox_path = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        print("preferences is alive!")
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")

        firefox_path = self.settings.get_string("firefox-path")
        self.custom_firefox_path.set_subtitle(firefox_path)

        # TODO Make set_custom_firefox_path handler
